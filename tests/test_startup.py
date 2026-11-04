import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import start_local as startup


class StartupPathTests(unittest.TestCase):
    def test_server_launch_in_nested_download_folder_with_spaces_and_parentheses(self):
        # This fixture also runs on Windows; no shell, native libraries or model
        # are needed to verify which program, arguments and cwd reach the child.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'auto-repair-budget-agent-main (2)' / 'auto-repair-budget-agent-main'
            root.mkdir(parents=True)
            env_dir = root / '.venv'
            (root / 'server.py').write_text(
                'import json, os, sys\nfrom pathlib import Path\n'
                'Path("result.json").write_text(json.dumps({"argv": sys.argv, "cwd": os.getcwd(), '
                '"preload": os.environ.get("LOCAL_PRELOAD")}))\nsys.exit(7)\n', encoding='utf-8')
            with patch.object(startup, 'ROOT', root), \
                 patch.object(startup, 'ENV_DIR', env_dir), \
                 patch.object(startup, 'ENV_PYTHON', Path(sys.executable)), \
                 patch.object(startup.sys, 'prefix', str(env_dir)), \
                 patch.object(startup, 'probe_dependencies', return_value={'issues': []}), \
                 patch.object(startup, 'prepare_frontend') as frontend, \
                 patch('scripts.download_model.main'), \
                 patch.object(startup.os, 'chdir'), \
                 patch.object(startup.os, 'execv', side_effect=AssertionError('Do not use execv on Windows')), \
                 patch.dict(os.environ):
                self.assertEqual(startup.main(), 7)
            frontend.assert_called_once()
            result = json.loads((root / 'result.json').read_text())
            self.assertEqual(result['argv'], [str(root / 'server.py')])
            self.assertEqual(Path(result['cwd']), root)
            self.assertEqual(result['preload'], '1')


if __name__ == '__main__':
    unittest.main()
