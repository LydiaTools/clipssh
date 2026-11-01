#!/usr/bin/env python3
"""Exercise the upload path using an isolated local shell in place of SSH."""
import base64
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'clipssh'
PNG_A = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
PNG_B = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADUlEQVR42mP8z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC')


class SyntheticUpload(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='clipssh-check-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.remote = self.root / "remote spaces ' $HOME ;"
        self.remote.mkdir()
        self.stub('pngpaste', 'cp "$TEST_INPUT" "$1"')
        self.stub('pbcopy', 'cat > "$TEST_OUTPUT"')
        self.stub('xclip', '''case " $* " in
  *" -o "*) cat "$TEST_INPUT" ;;
  *) cat > "$TEST_OUTPUT" ;;
esac''')
        self.stub('ssh', '''if [ "$1" = "-V" ]; then echo OpenSSH_9.0 >&2; exit 0; fi
for arg do last=$arg; done
case " $* " in *" synthetic@host "*) ;; *) exit 97 ;; esac
if [ "${TEST_SSH_MODE:-}" = fail ]; then exit 255; fi
if [ "${TEST_SSH_MODE:-}" = banner ]; then printf 'unexpected banner\\n'; fi
TEST_REMOTE=1 /bin/sh -c "$last"''')
        self.stub('cat', '''if [ "${TEST_REMOTE:-}" = 1 ] && [ "${TEST_CAT_FAIL:-}" = 1 ]; then exit 1; fi
exec /bin/cat "$@"''')
        self.a = self.root / 'a.png'
        self.b = self.root / 'b.png'
        self.a.write_bytes(PNG_A)
        self.b.write_bytes(PNG_B)

    def stub(self, name, body):
        path = self.bin / name
        path.write_text('#!/bin/sh\n' + body + '\n')
        path.chmod(0o700)

    def start(self, source, label, force_linux=False, **overrides):
        env = os.environ.copy()
        env.pop('WAYLAND_DISPLAY', None)
        env.update({'PATH': str(self.bin) + os.pathsep + env['PATH'], 'CLIPSSH_REMOTE_DIR': str(self.remote), 'TEST_INPUT': str(source), 'TEST_OUTPUT': str(self.root / label)})
        env.update(overrides)
        command = ['bash', '-c', 'OSTYPE=linux-gnu; source "$1" synthetic@host', '_', str(SCRIPT)] if force_linux else ['bash', str(SCRIPT), 'synthetic@host']
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

    def test_parallel_uploads_preserve_both_images_and_permissions(self):
        first = self.start(self.a, 'out-a')
        second = self.start(self.b, 'out-b')
        out_a, err_a = first.communicate(timeout=10)
        out_b, err_b = second.communicate(timeout=10)
        self.assertEqual(first.returncode, 0, err_a)
        self.assertEqual(second.returncode, 0, err_b)
        path_a = Path((self.root / 'out-a').read_text())
        path_b = Path((self.root / 'out-b').read_text())
        self.assertNotEqual(path_a, path_b)
        self.assertEqual(path_a.read_bytes(), PNG_A)
        self.assertEqual(path_b.read_bytes(), PNG_B)
        for path in (path_a, path_b):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            self.assertEqual(path.parent.parent, self.remote)

    def test_failure_does_not_return_a_path_or_delete_existing_data(self):
        existing = self.remote / 'keep.txt'
        existing.write_text('keep')
        proc = self.start(self.a, 'out-fail', TEST_CAT_FAIL='1')
        _, stderr = proc.communicate(timeout=10)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('outcome may be unknown', stderr)
        self.assertEqual(existing.read_text(), 'keep')
        self.assertFalse((self.root / 'out-fail').exists())
        self.assertEqual(list(self.remote.iterdir()), [existing])

    def test_unexpected_ssh_output_is_not_copied_as_a_path(self):
        proc = self.start(self.a, 'out-banner', TEST_SSH_MODE='banner')
        _, stderr = proc.communicate(timeout=10)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('outcome is unknown', stderr)
        self.assertFalse((self.root / 'out-banner').exists())
        self.assertEqual(len(list(self.remote.glob('clipboard-*/image.png'))), 1)

    def test_transport_failure_keeps_existing_files_and_does_not_claim_success(self):
        existing = self.remote / 'keep.txt'
        existing.write_text('keep')
        proc = self.start(self.a, 'out-transport', TEST_SSH_MODE='fail')
        stdout, stderr = proc.communicate(timeout=10)
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn('Uploaded:', stdout)
        self.assertIn('outcome may be unknown', stderr)
        self.assertFalse((self.root / 'out-transport').exists())
        self.assertEqual(existing.read_text(), 'keep')

    def test_linux_clipboard_branch_uses_stubbed_xclip(self):
        proc = self.start(self.a, 'out-linux', force_linux=True)
        _, stderr = proc.communicate(timeout=10)
        self.assertEqual(proc.returncode, 0, stderr)
        self.assertEqual(Path((self.root / 'out-linux').read_text()).read_bytes(), PNG_A)


if __name__ == '__main__':
    unittest.main()
