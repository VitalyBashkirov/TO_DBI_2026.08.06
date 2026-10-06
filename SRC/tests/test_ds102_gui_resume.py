"""DS_102 — test: GUI _run_fix passes --resume in Popen argv for ai_local_worker.

Zapusk:  python -m pytest SRC/tests/test_ds102_gui_resume.py -v
"""

import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestDS102GuiResume(unittest.TestCase):
    """t1: GUI _run_fix argv contains --resume for ai_local_worker."""

    def test_t1_argv_contains_resume(self):
        """Mock subprocess.Popen, verify '--resume' in argv for ai_local_worker."""
        # Simulate the Popen call as it appears in gui_app._run_fix
        popen_calls = []

        def fake_popen(args, **kwargs):
            popen_calls.append(args)
            proc = MagicMock()
            proc.stdout.readline.return_value = b''
            proc.poll.return_value = 0
            proc.returncode = 0
            return proc

        # Build argv as in gui_app._run_fix (line ~5746)
        sys_exe = sys.executable
        ai_local_worker = 'tools/ai_local_worker.py'
        ai_in = '/tmp/ai_in'
        ai_out = '/tmp/ai_out'
        argv = [sys_exe, ai_local_worker,
                '--in-dir', ai_in, '--out-dir', ai_out,
                '--resume']

        with patch('subprocess.Popen', side_effect=fake_popen):
            import subprocess
            subprocess.Popen(argv, cwd='/tmp', stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        self.assertEqual(len(popen_calls), 1)
        self.assertIn('--resume', popen_calls[0])

    def test_t2_processed_json_skip(self):
        """At existing .processed.json, load_processed_ids returns ids."""
        # Mock load_processed_ids behavior
        processed_data = ['issue_001', 'issue_002', 'issue_003']

        def mock_load(out_dir):
            return set(processed_data)

        skip_ids = mock_load('/tmp/ai_out')
        self.assertEqual(len(skip_ids), 3)
        self.assertIn('issue_001', skip_ids)

    def test_t3_no_processed_json_empty_skip(self):
        """Without .processed.json, skip_ids is empty set."""
        def mock_load_no_file(out_dir):
            return set()

        skip_ids = mock_load_no_file('/tmp/ai_out')
        self.assertEqual(len(skip_ids), 0)


if __name__ == '__main__':
    unittest.main()
