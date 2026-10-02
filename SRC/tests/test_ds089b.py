"""Tests for DS_089b — resume по ключу (скан / фикс).

Тесты 1–11 из DS_089b §3; тест 12 (регресс) запускается отдельно
(unittest discover по каталогу tests).
"""
import inspect
import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def _mk_issue(file_path, line, itype='v53.SQL.OUTERJOIN.п.1.1',
              desc='Замена (+) на LEFT JOIN', frag='(+)'):
    from analyzer.scanner import Issue
    return Issue(file_path=file_path, line_number=line, issue_type=itype,
                 description=desc, original_code='select ... from t1, t2',
                 category='SQL', match_fragment=frag)


class TestDS089b_SaveState(unittest.TestCase):
    """Тесты 1–3: сохранение состояния при прерывании."""

    def test_t1_abort_state_saved_on_scan(self):
        """Т1: _abort_state заполняется структурой operation/processed_keys."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app._abort_state = None
        issues = [_mk_issue('F:/x/a.plp', 10), _mk_issue('F:/x/a.plp', 20)]
        # Симуляция блока сохранения из _run_scan (тот же код-конструктор):
        keys = app._ds089b_processed_keys(issues)
        app._abort_state = {'operation': 'scan', 'processed_keys': keys}
        self.assertIsNotNone(app._abort_state)
        self.assertEqual(app._abort_state['operation'], 'scan')
        self.assertEqual(len(app._abort_state['processed_keys']), 2)

    def test_t2_processed_keys_match_dedup_format(self):
        """Т2: ключ = (file_path, line_number, issue_type, description,
        match_fragment) — формат дедупа scanner.py."""
        from gui_app import DBIMigrationApp
        i = _mk_issue('F:/x/a.plp', 12, itype='v53.T', desc='D', frag='frag')
        key = DBIMigrationApp._ds089b_issue_key(i)
        self.assertEqual(key, ('F:/x/a.plp', 12, 'v53.T', 'D', 'frag'))

    def test_t2b_scan_source_saves_state(self):
        """Т2b: _run_scan содержит сохранение _abort_state при abort."""
        from gui_app import DBIMigrationApp
        src = inspect.getsource(DBIMigrationApp._run_scan)
        self.assertIn("'operation': 'scan'", src)
        self.assertIn("'processed_keys'", src)
        self.assertIn('self.scan_aborted', src)

    def test_t3_processed_files_saved_on_fix(self):
        """Т3: fix_directory ведёт processed_files (файлы до прерывания)."""
        from fixer.code_fixer import PLPlusFixer
        src_dir, res_dir = _make_tmp_dirs()
        try:
            files = _make_plp_files(src_dir, ['a', 'b', 'c'])
            scanner = _mock_scanner(files, src_dir)
            # abort после первого файла: счётчик вызовов callback
            state = {'n': 0}

            def _cb():
                state['n'] += 1
                return state['n'] > 1  # пропустить 1-й, остановить на 2-м
            fixer = PLPlusFixer(_fixer_config(src_dir), 'v0001',
                                abort_callback=_cb)
            fixer.fix_directory(scanner, Path(res_dir))
            self.assertEqual(len(fixer.processed_files), 1)
            self.assertIn(Path(files[0]).name, fixer.processed_files[0])
        finally:
            shutil.rmtree(src_dir, ignore_errors=True)
            shutil.rmtree(res_dir, ignore_errors=True)


class TestDS089b_ResumeScan(unittest.TestCase):
    """Тесты 4–6: resume scanner — пересканировать + фильтр по ключам."""

    def test_t4_filter_removes_prev_keys(self):
        """Т4: issues с сохранёнными ключами исключаются (фильтр)."""
        from gui_app import DBIMigrationApp
        prev = [_mk_issue('F:/x/a.plp', 10), _mk_issue('F:/x/a.plp', 20)]
        prev_keys = {DBIMigrationApp._ds089b_issue_key(i) for i in prev}
        # Перескан вернул те же два + один новый
        new_issues = prev + [_mk_issue('F:/x/b.plp', 5)]
        kept = DBIMigrationApp._ds089b_filter_processed(new_issues, prev_keys)
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0].file_path, 'F:/x/b.plp')

    def test_t5_no_duplicates_after_filter(self):
        """Т5: пропуск обработанных — в результате нет дублей prev-ключей."""
        from gui_app import DBIMigrationApp
        prev = [_mk_issue('F:/x/a.plp', 10)]
        prev_keys = {DBIMigrationApp._ds089b_issue_key(i) for i in prev}
        dup = _mk_issue('F:/x/a.plp', 10)  # идентичный дубль
        kept = DBIMigrationApp._ds089b_filter_processed([dup], prev_keys)
        self.assertEqual(kept, [])

    def test_t6_new_issues_added(self):
        """Т6: новые issues (отличающийся любой компонент ключа) остаются."""
        from gui_app import DBIMigrationApp
        prev = [_mk_issue('F:/x/a.plp', 10, frag='(+)')]
        prev_keys = {DBIMigrationApp._ds089b_issue_key(i) for i in prev}
        variants = [
            _mk_issue('F:/x/a.plp', 11, frag='(+)'),      # др. строка
            _mk_issue('F:/x/a.plp', 10, frag='t2.id(+)'),  # др. фрагмент
            _mk_issue('F:/x/a.plp', 10, itype='v53.OTHER'),  # др. тип
        ]
        kept = DBIMigrationApp._ds089b_filter_processed(variants, prev_keys)
        self.assertEqual(len(kept), 3)


class TestDS089b_ResumeFix(unittest.TestCase):
    """Тесты 7–8: resume code_fixer — пропуск обработанных файлов."""

    def test_t7_skip_files_skipped(self):
        """Т7: файлы из skip_files не обрабатываются (resume fix)."""
        from fixer.code_fixer import PLPlusFixer
        src_dir, res_dir = _make_tmp_dirs()
        try:
            files = _make_plp_files(src_dir, ['a', 'b', 'c'])
            scanner = _mock_scanner(files, src_dir)
            fixer = PLPlusFixer(_fixer_config(src_dir), 'v0001')
            fixer.fix_directory(scanner, Path(res_dir),
                                skip_files={str(files[0])})
            self.assertNotIn(Path(files[0]).name,
                             ' '.join(fixer.processed_files))
            self.assertEqual(len(fixer.processed_files), 2)
        finally:
            shutil.rmtree(src_dir, ignore_errors=True)
            shutil.rmtree(res_dir, ignore_errors=True)

    def test_t8_idempotent_parts_equals_full(self):
        """Т8: фикс по частям (abort + resume) = фикс всех файлов."""
        from fixer.code_fixer import PLPlusFixer
        src_dir, res_parts, res_full = None, None, None
        try:
            src_dir = tempfile.mkdtemp()
            res_parts = tempfile.mkdtemp()
            res_full = tempfile.mkdtemp()
            files = _make_plp_files(src_dir, ['a', 'b', 'c'])
            scanner = _mock_scanner(files, src_dir)
            # Прогон «по частям»: часть 1 — только a; часть 2 — b, c (skip a)
            st = {'n': 0}

            def _cb():
                st['n'] += 1
                return st['n'] > 1
            f1 = PLPlusFixer(_fixer_config(src_dir), 'v0001',
                             abort_callback=_cb)
            f1.fix_directory(scanner, Path(res_parts))
            done = set(f1.processed_files)
            f2 = PLPlusFixer(_fixer_config(src_dir), 'v0001')
            f2.fix_directory(scanner, Path(res_parts), skip_files=done)
            # Полный прогон для сравнения
            scanner2 = _mock_scanner(files, src_dir)
            f3 = PLPlusFixer(_fixer_config(src_dir), 'v0001')
            f3.fix_directory(scanner2, Path(res_full))
            # Итог: во всех трёх файлах результаты созданы в обоих режимах
            for f in files:
                name = Path(f).name
                parts_hits = list(Path(res_parts).rglob(name))
                full_hits = list(Path(res_full).rglob(name))
                self.assertTrue(parts_hits, f'нет {name} в частичном')
                self.assertTrue(full_hits, f'нет {name} в полном')
                # Содержимое идентично (результат = копия оригинала,
                # issue не детерминированный → was_modified=False)
                self.assertEqual(parts_hits[0].read_bytes(),
                                 full_hits[0].read_bytes())
        finally:
            for d in (src_dir, res_parts, res_full):
                if d:
                    shutil.rmtree(d, ignore_errors=True)


class TestDS089b_AICycle(unittest.TestCase):
    """Тест 9: AI-цикл не возобновляется (пометка в ЖВ)."""

    def test_t9_ai_cycle_not_resumed(self):
        from gui_app import DBIMigrationApp
        src = inspect.getsource(DBIMigrationApp._run_ai_cycle)
        self.assertIn('AI-цикл не возобновляется', src)

    def test_t9b_ai_cycle_sets_no_abort_state(self):
        """_run_ai_cycle не заполняет _abort_state (resume — не для AI)."""
        from gui_app import DBIMigrationApp
        src = inspect.getsource(DBIMigrationApp._run_ai_cycle)
        self.assertNotIn('_abort_state', src)


class TestDS089b_Logging(unittest.TestCase):
    """Тесты 10–11: логирование resume в ЖВ + bot.log."""

    def test_t10_resume_log_label(self):
        """Т10: «Возобновление с N issues (пропущено M)» в _run_scan + bot.log."""
        from gui_app import DBIMigrationApp
        src = inspect.getsource(DBIMigrationApp._run_scan)
        self.assertIn('Возобновление с', src)
        self.assertIn('пропущено', src)
        self.assertIn('self._bot_log', src)

    def test_t11_resume_completed_label(self):
        """Т11: «Операция возобновлена и завершена» в скане и фиксе."""
        from gui_app import DBIMigrationApp
        for fn in (DBIMigrationApp._run_scan, DBIMigrationApp._run_fix):
            src = inspect.getsource(fn)
            self.assertIn('Операция возобновлена и завершена', src)

    def test_t11b_state_saved_label(self):
        """Т11b: «Состояние сохранено: N issues, M файлов» при abort."""
        from gui_app import DBIMigrationApp
        src_scan = inspect.getsource(DBIMigrationApp._run_scan)
        src_fix = inspect.getsource(DBIMigrationApp._run_fix)
        self.assertIn('Состояние сохранено', src_scan)
        self.assertIn('Состояние сохранено', src_fix)


class TestDS089b_FixerSkipSource(unittest.TestCase):
    """Доп: fix_directory принимает skip_files и ведёт processed_files."""

    def test_skip_files_param_in_signature(self):
        import inspect as _inspect
        from fixer.code_fixer import PLPlusFixer
        sig = _inspect.signature(PLPlusFixer.fix_directory)
        self.assertIn('skip_files', sig.parameters)


# ---------------------------------------------------------------------------
# Хелперы интеграционных тестов
# ---------------------------------------------------------------------------
def _make_tmp_dirs():
    return tempfile.mkdtemp(), tempfile.mkdtemp()


def _make_plp_files(src_dir, names):
    """Создать простые .plp файлы (без детерминированно-исправимых конструкций)."""
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


def _mock_scanner(files, src_dir):
    """MagicMock-сканер: get_issues_by_file -> {путь: [один недет. issue]}."""
    scanner = MagicMock()
    issues_by_file = {}
    for f in files:
        issues_by_file[str(f)] = [_mk_issue(str(f), 2)]
    scanner.get_issues_by_file.return_value = issues_by_file
    # Реальные атрибуты для verification-сканера (создаётся в try/except)
    scanner.config = _fixer_config(src_dir)
    scanner.selected_rules = []
    scanner.rubricator_prompts = None
    scanner.plpcheck_categories = []
    return scanner


if __name__ == '__main__':
    unittest.main()
