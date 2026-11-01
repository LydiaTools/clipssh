import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallTest(unittest.TestCase):
    def test_installs_preview_and_requires_checkout(self):
        with tempfile.TemporaryDirectory(prefix='clipssh-install-') as tmp:
            root = Path(tmp)
            binaries = root / 'bin'
            binaries.mkdir()
            stub = binaries / 'pngpaste'
            stub.write_text('#!/bin/sh\nexit 0\n')
            stub.chmod(0o700)
            env = os.environ.copy()
            env.update({'PATH': str(binaries) + os.pathsep + env['PATH'], 'INSTALL_DIR': str(root / 'installed')})
            result = subprocess.run(['bash', str(ROOT / 'install.sh')], cwd=ROOT, env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / 'installed' / 'clipssh').read_bytes(), (ROOT / 'clipssh').read_bytes())
            env['INSTALL_DIR'] = str(root / 'unexpected')
            result = subprocess.run(['bash', str(ROOT / 'install.sh')], cwd=root, env=env, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('preview fork checkout', result.stderr)
            self.assertFalse((root / 'unexpected').exists())


if __name__ == '__main__':
    unittest.main()
