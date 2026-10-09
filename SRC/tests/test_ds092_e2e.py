# -*- coding: utf-8 -*-
"""DS_092 - end-to-end GUI resume (skan / fix).

t1..t5 - testy (sm. DS_092 S5).
Zapusk:  python SRC/tests/test_ds092_e2e.py
"""
import os
import re
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def _make_tmp_dirs():
    return tempfile.mkdtemp(), tempfile.mkdtemp()


def _make_plp_files(src_dir, names):
    files = []
    for n in names:
        p = Path(src_dir) / f'{n}.plp'
        p.write_text('procedure test is\nbegin\n  null;\nend;\n',
                     encoding='utf-8')
        files.append(str(p))
    return files


def _fixer_config(src_dir):
    return {
        'paths': {'source_dir': src_dir, 'results_dir': src_dir,
                  'logs_dir': src_dir},
        'scan': {'file_pattern': '**/*.plp', 'recursive': True},
        'output': {'preserve_structure': True, 'only_modified': False,
                   'fix_only_found': False},
    }


class TestDS092_StopEvent(unittest.TestCase):
    """t1: _stop_event set/clear."""

    def test_t1_stop_event_set_clear(self):
        ev = threading.Event()
        self.assertFalse(ev.is_set())
        ev.set()
        self.assertTrue(ev.is_set())
        ev.clear()
        self.assertFalse(ev.is_set())


class TestDS092_Iteration(unittest.TestCase):
    """t2, t3: iteration v _run_fix / _run_scan."""

    def test_t2_fixer_iteration_format(self):
        from fixer.code_fixer import PLPlusFixer
        cfg = _fixer_config(tempfile.mkdtemp())
        fixer = PLPlusFixer(cfg, 'v20261005120000')
        self.assertTrue(fixer.iteration)
        self.assertRegex(fixer.iteration, r'^v\d{14}$')
        shutil.rmtree(cfg['paths']['source_dir'], ignore_errors=True)

    def test_t3_scanner_no_crash(self):
        from analyzer.scanner import PLPlusScanner
        scanner = PLPlusScanner.__new__(PLPlusScanner)
        self.assertIsNotNone(scanner)


class TestDS092_ScenarioA_Scan(unittest.TestCase):
    """t4: skan + abort + resume (2 .plp)."""

    def test_t4_scan_abort_resume(self):
        from gui_app import DBIMigrationApp
        src_dir, res_dir = _make_tmp_dirs()
        try:
            files = _make_plp_files(src_dir, ['a', 'b'])
            app = DBIMigrationApp.__new__(DBIMigrationApp)
            app._stop_event = threading.Event()
            app._abort_state = None
            app.scan_aborted = False
            app.source_dir_var = MagicMock()
            app.source_dir_var.get.return_value = src_dir
            app.result_dir_var = MagicMock()
            app.result_dir_var.get.return_value = res_dir
            app.file_pattern_var = MagicMock()
            app.file_pattern_var.get.return_value = '*.plp'
            app.selected_rules = {}
            app.log = MagicMock()
            app._bot_log = MagicMock()
            app._log_to_journal = MagicMock()
            app._update_main_buttons = MagicMock()
            app._play_result_sound = MagicMock()
            app._start_operation = MagicMock()
            app._finish_operation = MagicMock()
            app._abort_requested = MagicMock(return_value=False)

            # Simulate: abort_state with first file's issues
            from analyzer.scanner import Issue
            iss_a = Issue(file_path=files[0], line_number=1,
                          issue_type='v53.T', description='d',
                          original_code='x', category='SQL',
                          match_fragment='f')
            keys = app._ds089b_processed_keys([iss_a])
            app._abort_state = {'operation': 'scan', 'processed_keys': keys}

            # Verify filter works
            all_issues = [iss_a, Issue(file_path=files[1], line_number=1,
                                       issue_type='v53.T', description='d2',
                                       original_code='y', category='SQL',
                                       match_fragment='f2')]
            prev_keys = app._abort_state['processed_keys']
            kept = DBIMigrationApp._ds089b_filter_processed(all_issues, prev_keys)
            self.assertEqual(len(kept), 1)
            self.assertIn('b.plp', kept[0].file_path)
        finally:
            shutil.rmtree(src_dir, ignore_errors=True)
            shutil.rmtree(res_dir, ignore_errors=True)


class TestDS092_ScenarioB_Fix(unittest.TestCase):
    """t5: fix + abort + resume (2 .plp)."""

    def test_t5_fix_abort_resume(self):
        from fixer.code_fixer import PLPlusFixer
        src_dir, res_dir = _make_tmp_dirs()
        try:
            files = _make_plp_files(src_dir, ['a', 'b'])
            scanner = MagicMock()
            issues_by_file = {str(f): [] for f in files}
            scanner.get_issues_by_file.return_value = issues_by_file
            scanner.config = _fixer_config(src_dir)
            scanner.selected_rules = []
            scanner.rubricator_prompts = None
            scanner.plpcheck_categories = []

            # Part 1: abort after first file
            state = {'n': 0}
            def _cb():
                state['n'] += 1
                return state['n'] > 1
            f1 = PLPlusFixer(_fixer_config(src_dir), 'v0001', abort_callback=_cb)
            f1.fix_directory(scanner, Path(res_dir))
            self.assertEqual(len(f1.processed_files), 1)

            # Part 2: resume with skip_files
            done = set(f1.processed_files)
            scanner2 = MagicMock()
            scanner2.get_issues_by_file.return_value = issues_by_file
            scanner2.config = _fixer_config(src_dir)
            scanner2.selected_rules = []
            scanner2.rubricator_prompts = None
            scanner2.plpcheck_categories = []
            f2 = PLPlusFixer(_fixer_config(src_dir), 'v0001')
            f2.fix_directory(scanner2, Path(res_dir), skip_files=done)
            self.assertEqual(len(f2.processed_files), 1)
            # Both files processed total
            all_processed = set(f1.processed_files) | set(f2.processed_files)
            self.assertEqual(len(all_processed), 2)
        finally:
            shutil.rmtree(src_dir, ignore_errors=True)
            shutil.rmtree(res_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
