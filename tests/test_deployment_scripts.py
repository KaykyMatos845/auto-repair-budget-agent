import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SwarmScriptTests(unittest.TestCase):
    def run_node(self, arguments, role='manager', manager='10.0.0.10:2377', state='active', stdin=''):
        with tempfile.TemporaryDirectory() as directory:
            docker = Path(directory) / 'docker'
            docker.write_text('#!/bin/sh\ncase "$*" in\n'
                              f'*LocalNodeState*) echo {state} ;;\n'
                              f'*ControlAvailable*) echo {"true" if role == "manager" else "false"} ;;\n'
                              f'*NodeAddr*) echo {"10.0.0.10" if role == "manager" else "10.0.0.11"} ;;\n'
                              f'*RemoteManagers*) echo {manager} ;;\n'
                              '*) echo unexpected-mutation >&2; exit 99 ;;\nesac\n')
            docker.chmod(0o755)
            return subprocess.run(['bash', str(ROOT/'scripts/swarm-node.sh'), *arguments],
                                  env={**os.environ, 'PATH': directory + os.pathsep + os.environ['PATH']},
                                  input=stdin, text=True, capture_output=True)

    def test_existing_manager_is_reused(self):
        result = self.run_node(['manager', '10.0.0.10'])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_existing_worker_requires_the_expected_manager(self):
        result = self.run_node(['worker', '10.0.0.11', '10.0.0.10'], role='worker')
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_node(['worker', '10.0.0.11', '10.0.0.10'], role='worker', manager='10.0.0.20:2377')
        self.assertEqual(result.returncode, 1)
        self.assertIn('outro manager', result.stderr)

    def test_empty_token_does_not_attempt_to_join(self):
        result = self.run_node(['worker', '10.0.0.11', '10.0.0.10'], role='worker', state='inactive')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Worker token required', result.stderr)
        self.assertNotIn('unexpected-mutation', result.stderr)

    def test_publish_rejects_local_registries_and_missing_tags(self):
        for image in ['localhost/backend:v4', 'localhost:5000/backend:v4', '127.0.0.1:5000/backend:v4',
                      'registry.example:5000/backend', 'ghcr.io/example/backend:latest']:
            result = subprocess.run(['bash', str(ROOT/'scripts/build-images.sh'), '--push'], cwd=ROOT,
                                    env={**os.environ, 'BACKEND_IMAGE': image,
                                         'FRONTEND_IMAGE': 'ghcr.io/example/frontend:v4', 'MONITOR_IMAGE': 'ghcr.io/example/monitor:v4'}, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2, image)

    def test_rolled_back_update_is_not_reported_as_success(self):
        with tempfile.TemporaryDirectory() as directory:
            docker = Path(directory) / 'docker'
            docker.write_text('#!/bin/sh\ncase "$*" in\n'
                              '*ControlAvailable*) echo true ;;\n'
                              '"node ls"*) printf "Ready Active\\nReady Active\\n" ;;\n'
                              '"stack config"*|"stack deploy"*) exit 0 ;;\n'
                              '"stack services"*) printf "autobudget_backend 2/2\\nautobudget_frontend 2/2\\n" ;;\n'
                              '"service inspect"*) printf "rollback_completed\\ncompleted\\n" ;;\n'
                              '"stack ps"*) echo fixture ;;\n'
                              '*) exit 99 ;;\nesac\n')
            docker.chmod(0o755)
            result = subprocess.run(['bash', str(ROOT/'scripts/deploy-swarm.sh')], cwd=ROOT,
                                    env={**os.environ, 'PATH': directory + os.pathsep + os.environ['PATH'],
                                         'BACKEND_IMAGE': 'ghcr.io/example/backend:v4',
                                         'FRONTEND_IMAGE': 'ghcr.io/example/frontend:v4', 'MONITOR_IMAGE': 'ghcr.io/example/monitor:v4'}, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('rollback', result.stderr)

    def test_three_replicas_are_rejected_for_the_two_node_demo(self):
        result = subprocess.run(['bash', str(ROOT/'scripts/deploy-swarm.sh')], cwd=ROOT,
                                env={**os.environ, 'APP_REPLICAS': '3',
                                     'BACKEND_IMAGE': 'ghcr.io/example/backend:v5',
                                     'FRONTEND_IMAGE': 'ghcr.io/example/frontend:v5'}, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('1 ou 2', result.stderr)

    def test_readiness_requires_both_ready_and_active_without_status_filter(self):
        cases = [('Ready Active\nReady Active\n', 17),
                 ('Ready Active\nDown Active\n', 1),
                 ('Ready Active\nReady Drain\n', 1),
                 ('Ready Active\nReady Pause\n', 1)]
        for states, expected in cases:
            with self.subTest(states=states), tempfile.TemporaryDirectory() as directory:
                docker = Path(directory) / 'docker'
                docker.write_text('#!/bin/sh\ncase "$*" in\n'
                                  '*"--filter status=ready"*) echo "invalid filter status" >&2; exit 99 ;;\n'
                                  '*ControlAvailable*) echo true ;;\n'
                                  '"node ls --format {{.Status}} {{.Availability}}") printf "%s" "$TEST_NODE_STATES" ;;\n'
                                  '"stack config"*) exit 0 ;;\n'
                                  '"stack deploy"*) echo DEPLOY_REACHED; exit 17 ;;\n'
                                  '*) echo unexpected-command >&2; exit 98 ;;\nesac\n')
                docker.chmod(0o755)
                result = subprocess.run(['bash', str(ROOT/'scripts/deploy-swarm.sh')], cwd=ROOT,
                                        env={**os.environ, 'PATH': directory + os.pathsep + os.environ['PATH'],
                                             'TEST_NODE_STATES': states, 'WITH_VISUALIZER': '0',
                                             'BACKEND_IMAGE': 'ghcr.io/example/backend:v5',
                                             'FRONTEND_IMAGE': 'ghcr.io/example/frontend:v5'},
                                        text=True, capture_output=True)
                self.assertEqual(result.returncode, expected, result.stderr)
                if expected == 17:
                    self.assertIn('DEPLOY_REACHED', result.stdout)
                else:
                    self.assertNotIn('DEPLOY_REACHED', result.stdout)
