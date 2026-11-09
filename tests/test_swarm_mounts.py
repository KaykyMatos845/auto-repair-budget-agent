"""Opt-in native Swarm test. Never joins/leaves an existing cluster.

Build Dockerfile.frontend as auto-repair-frontend:test, then run on an empty,
inactive Docker daemon: RUN_SWARM_INTEGRATION=1 python3 tests/test_swarm_mounts.py
Uses the daemon host network (port 8080) to isolate mounts from VXLAN support.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get('RUN_SWARM_INTEGRATION') == '1', 'Opt-in test requires an empty Docker daemon')
class NativeSwarmMountTest(unittest.TestCase):
    def test_read_only_frontend_receives_writable_tmpfs(self):
        def docker(*arguments, env=None):
            try:
                return subprocess.check_output(['docker', *arguments], cwd=ROOT, env=env, text=True, stderr=subprocess.PIPE).strip()
            except subprocess.CalledProcessError as error:
                raise RuntimeError(error.stderr) from error

        self.assertEqual(docker('info', '--format', '{{.Swarm.LocalNodeState}}'), 'inactive', 'Refusing to alter an existing Swarm')
        self.assertEqual(docker('ps', '-q'), '', 'Use an empty test daemon')
        image = os.environ.get('SWARM_TEST_FRONTEND_IMAGE', 'auto-repair-frontend:test')
        docker('image', 'inspect', image)
        settings = {**os.environ, 'BACKEND_IMAGE': 'unused-backend:test', 'FRONTEND_IMAGE': image, 'APP_REPLICAS': '1'}
        config = json.loads(docker('compose', '-f', 'docker-compose.yml', 'config', '--format', 'json', env=settings))
        # Compose normalizes more than mounts (e.g. network names, numeric CPU).
        # Keep the actual filesystem settings and omit unrelated normalized fields.
        source = config['services']['frontend']
        frontend = {key: source[key] for key in ['image', 'read_only', 'cap_drop', 'healthcheck', 'volumes', 'tmpfs'] if key in source}
        for mount in frontend.get('volumes', []):
            if mount.get('type') == 'tmpfs':
                mount['tmpfs']['size'] = int(mount['tmpfs']['size'])
        frontend['deploy'] = {'replicas': 1}
        frontend['networks'] = ['test-host']
        stack = {'version': '3.8', 'services': {'frontend': frontend},
                 'networks': {'test-host': {'external': True, 'name': 'host'}}}
        created = False
        stack_name = 'auto-repair-tmpfs-check'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'stack.json'
            path.write_text(json.dumps(stack))
            try:
                docker('swarm', 'init', '--advertise-addr', '127.0.0.1')  # Capture join credentials; never print them.
                created = True
                docker('stack', 'deploy', '--resolve-image', 'never', '-c', str(path), stack_name)
                service = json.loads(docker('service', 'inspect', stack_name + '_frontend'))[0]
                mounts = service['Spec']['TaskTemplate']['ContainerSpec'].get('Mounts', [])
                temporary = [mount for mount in mounts if mount['Target'] == '/tmp']
                self.assertEqual(len(temporary), 1, mounts)
                self.assertEqual(temporary[0]['Type'], 'tmpfs')
                self.assertFalse(temporary[0].get('ReadOnly', False))
                self.assertEqual(temporary[0]['TmpfsOptions']['SizeBytes'], 32 * 1024 * 1024)
                deadline = time.monotonic() + 75
                while time.monotonic() < deadline:
                    ids = docker('ps', '-q', '--filter', 'label=com.docker.swarm.service.name=' + stack_name + '_frontend').splitlines()
                    if ids:
                        try:
                            self.assertEqual(docker('exec', ids[0], 'wget', '-Y', 'off', '-qO-', 'http://127.0.0.1:8080/healthz'), 'ok')
                            self.assertEqual(docker('exec', ids[0], 'stat', '-c', '%a', '/tmp'), '1777')
                            return
                        except RuntimeError:
                            pass
                    time.sleep(.5)
                self.fail('Nginx did not start: ' + docker('service', 'ps', '--no-trunc', stack_name + '_frontend'))
            finally:
                if created:
                    try:
                        docker('stack', 'rm', stack_name)
                    finally:
                        docker('swarm', 'leave', '--force')


if __name__ == '__main__':
    unittest.main(verbosity=2)
