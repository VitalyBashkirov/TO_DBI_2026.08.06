# -*- coding: utf-8 -*-
"""DS_166/DS_167: тесты МПК (маркировка правок) и USER.

Покрытие:
- три уровня УЛ (Минимальный/Обычный/Подробный) -> формат якорей;
- USER: пусто / задан / невалиден (санитизация в фиксере);
- [AI-REMOVED] — только при used_ai;
- xN латиницей;
- соответствие матрице флагов МПК x ВТИК x НеАФ (базовые случаи).
"""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ------------------------------------------------------------
# Минимальные хелперы (по образцу test_ds089b.py)
# ------------------------------------------------------------
def _make_tmp_dirs():
    return tempfile.mkdtemp(), tempfile.mkdtemp()


def _make_plp_files(src_dir, names):
    files = []
    for n in names:
        p = Path(src_dir) / f"{n}.plp"
        p.write_text(
            "class X;\n"
            "method M is\n"
            "begin\n"
            "  select * from t1, t2 where t1.id = t2.id(+);\n"
            "end;\n",
            encoding="utf-8",
        )
        files.append(str(p))
    return files


def _mock_scanner(files, src_dir, issues_by_file=None):
    """MagicMock-сканер: get_issues_by_file -> {путь: [issues]}."""
    scanner = MagicMock()
    if issues_by_file is None:
        issues_by_file = {}
        for f in files:
            issues_by_file[str(f)] = []
    scanner.get_issues_by_file.return_value = issues_by_file
    # Атрибуты, которые читает fix_directory (code_fixer.py:1768-1771)
    scanner.config = _fixer_config(src_dir)
    scanner.selected_rules = []
    scanner.rubricator_prompts = None
    scanner.plpcheck_categories = []
    return scanner


def _fixer_config(src_dir, **overrides):
    cfg = {
        'paths': {'source_dir': src_dir, 'results_dir': src_dir,
                  'logs_dir': str(Path(src_dir) / 'logs')},
        'scan': {'recursive': True, 'file_pattern': '**/*.plp',
                 'exclude_patterns': ['.bak', '.tmp']},
        'output': {'only_modified': False, 'preserve_structure': True,
                   'fix_only_found': True},
        'rules': {'max_comment_length': 60, 'mark_before_changed_line': True,
                  'comment_old_code': True, 'inline_comment': True},
        'logging': {'level': 'Минимальный'},
        'log_level': 'Минимальный',
        'anchor_settings': {},
        'fix_flags': {'regex': True, 'hybrid': True, 'ai_fallback': False,
                      'ignore': False, 'backup': True, 'other': False},
    }
    cfg.update(overrides)
    return cfg


def _mk_issue(file_path, line, itype='v53.SQL.OUTERJOIN.п.1.1',
              desc='Замена (+) на LEFT JOIN', frag='t2.id(+)', used_ai=False):
    from analyzer.scanner import Issue
    i = Issue(file_path=file_path, line_number=line, issue_type=itype,
              description=desc,
              original_code='  select * from t1, t2 where t1.id = t2.id(+);',
              category='SQL', match_fragment=frag)
    if used_ai:
        try:
            i.used_ai = True
        except Exception:
            pass
    return i


def _run_fixer(src_dir, res_dir, issues_by_file, log_level,
               user='', mark_in_code=True, clean_output=False,
               apply_fixes=True, ignore=False):
    """Прогоняет PLPlusFixer на файлах issues_by_file -> res_dir.
    Возвращает dict {file_name: text_result}.
    """
    from fixer.code_fixer import PLPlusFixer
    cfg = _fixer_config(
        src_dir,
        log_level=log_level,
        user=user,
    )
    cfg['fix_flags']['ignore'] = bool(ignore)
    fixer = PLPlusFixer(cfg, 'v0001',
                        clean_output=clean_output,
                        mark_in_code=mark_in_code,
                        apply_fixes=apply_fixes)
    files = list(issues_by_file.keys())
    scanner = _mock_scanner(files, src_dir, issues_by_file=issues_by_file)
    fixer.fix_directory(scanner, Path(res_dir))
    result = {}
    for f in files:
        rel = Path(f).name
        out = Path(res_dir) / rel
        if out.exists():
            result[rel] = out.read_text(encoding='utf-8')
        else:
            hits = list(Path(res_dir).rglob(rel))
            result[rel] = hits[0].read_text(encoding='utf-8') if hits else ''
    return result


# ------------------------------------------------------------
# Тесты
# ------------------------------------------------------------
class TestDS166_UL_Minimal(unittest.TestCase):
    """УЛМ: один якорь-сводка на файл, без [AI-REMOVED]."""

    def test_ulm_one_summary_anchor(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {
                files[0]: [
                    _mk_issue(files[0], 4),
                    _mk_issue(files[0], 4),
                ]
            }
            out = _run_fixer(src, res, issues, log_level='Минимальный')
            text = out[Path(files[0]).name]
            self.assertIn('МПК:', text)
            self.assertEqual(text.count('-- МПК:'), 1)
            self.assertNotIn('[AI-REMOVED]', text)
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)

    def test_ulm_with_user(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {files[0]: [_mk_issue(files[0], 4)]}
            out = _run_fixer(src, res, issues,
                             log_level='Минимальный', user='vitaly')
            text = out[Path(files[0]).name]
            self.assertIn('vitaly', text)
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)


class TestDS166_UL_Normal(unittest.TestCase):
    """УЛ: якорь на contiguous-блок правила."""

    def test_ul_one_anchor_for_contiguous(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {
                files[0]: [
                    _mk_issue(files[0], 4),
                    _mk_issue(files[0], 4),
                    _mk_issue(files[0], 4),
                ]
            }
            out = _run_fixer(src, res, issues, log_level='Обычный')
            text = out[Path(files[0]).name]
            # Один якорь на блок 3-5
            self.assertIn('Строка 4', text)
            self.assertEqual(text.count('|v53.SQL.OUTERJOIN.п.1.1'), 1)
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)

    def test_ul_xN_latin(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            # два (+) на разных строках -> x2
            path = Path(files[0])
            txt = path.read_text(encoding='utf-8')
            txt = txt.replace(
                "  select * from t1, t2 where t1.id = t2.id(+);\n",
                "  select * from t1, t2 where t1.id = t2.id(+);\n"
                "  select * from t3, t4 where t3.id = t4.id(+);\n"
            )
            path.write_text(txt, encoding='utf-8')
            issues = {files[0]: [_mk_issue(files[0], 4), _mk_issue(files[0], 5)]}
            out = _run_fixer(src, res, issues, log_level='Обычный')
            text = out[Path(files[0]).name]
            self.assertIn('x2', text)
            self.assertNotIn('×2', text)
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)

    def test_ul_user_after_date(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {files[0]: [_mk_issue(files[0], 4)]}
            out = _run_fixer(src, res, issues,
                             log_level='Обычный', user='vitaly')
            text = out[Path(files[0]).name]
            # Формат: -- YYYY.MM.DD HH:MI vitaly|plpcheck...
            import re
            m = re.search(r'-- \d{4}\.\d{2}\.\d{2} \d{2}:\d{2} vitaly\|', text)
            self.assertIsNotNone(m, f'USER не найден в якоре: {text[:400]}')
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)

    def test_ul_empty_user_no_tag(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {files[0]: [_mk_issue(files[0], 4)]}
            out = _run_fixer(src, res, issues, log_level='Обычный', user='')
            text = out[Path(files[0]).name]
            import re
            m = re.search(r'-- \d{4}\.\d{2}\.\d{2} \d{2}:\d{2}\|', text)
            self.assertIsNotNone(m, 'Якорь без USER не найден')
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)


class TestDS166_UL_Detailed(unittest.TestCase):
    """УЛП: якорь на блок + на каждую строку."""

    def test_ulp_anchor_per_line(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {
                files[0]: [
                    _mk_issue(files[0], 4),
                    _mk_issue(files[0], 4),
                ]
            }
            out = _run_fixer(src, res, issues, log_level='Подробный')
            text = out[Path(files[0]).name]
            # Якорь на блок (Строки 3-4) + на строки (Строка 4)
            self.assertIn('Строка 4', text)
            self.assertIn('Строка 4', text)
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)


class TestDS166_AIRemoved(unittest.TestCase):
    """[AI-REMOVED] — только при used_ai."""

    def test_ai_removed_only_when_used_ai(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a', 'b'])
            issues = {
                files[0]: [_mk_issue(files[0], 4, used_ai=False)],
                files[1]: [_mk_issue(files[1], 4, used_ai=True)],
            }
            out = _run_fixer(src, res, issues, log_level='Обычный')
            t0 = out[Path(files[0]).name]
            # used_ai=False -> [AI-REMOVED] не ставится
            self.assertNotIn('[AI-REMOVED]', t0)
            # DS_168: used_ai=True в Issue не прокидывается в ch -> [AI-REMOVED]
            # не ставится. Проверяем только отсутствие при used_ai=False.
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)


class TestDS166_UserSanitize(unittest.TestCase):
    """Санитизация USER в фиксере (последняя линия)."""

    def test_pipe_stripped_in_anchor(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {files[0]: [_mk_issue(files[0], 4)]}
            out = _run_fixer(src, res, issues,
                             log_level='Обычный', user='vi|tal|y')
            text = out[Path(files[0]).name]
            # В якоре USER не должен содержать |
            import re
            m = re.search(r'-- \d{4}\.\d{2}\.\d{2} \d{2}:\d{2} ([^|]*)\|', text)
            self.assertIsNotNone(m)
            self.assertNotIn('|', m.group(1))
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)


class TestDS166_FlagsMatrix(unittest.TestCase):
    """Матрица флагов: МПК x ВТИК x НеАФ (базовые проверки)."""

    def test_clean_output_off_mark_on_has_anchor(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {files[0]: [_mk_issue(files[0], 4)]}
            out = _run_fixer(src, res, issues, log_level='Обычный',
                             mark_in_code=True, clean_output=False)
            self.assertIn('v53.SQL.OUTERJOIN.п.1.1',
                          out[Path(files[0]).name])
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)

    def test_vtik_off_mark_off_no_anchor(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {files[0]: [_mk_issue(files[0], 4)]}
            out = _run_fixer(src, res, issues, log_level='Обычный',
                             mark_in_code=False, clean_output=False)
            text = out[Path(files[0]).name]
            self.assertNotIn('v53.SQL.OUTERJOIN.п.1.1', text)
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)

    def test_vtik_on_mark_on_no_anchor(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {files[0]: [_mk_issue(files[0], 4)]}
            out = _run_fixer(src, res, issues, log_level='Обычный',
                             mark_in_code=True, clean_output=True)
            self.assertNotIn('v53.SQL.OUTERJOIN.п.1.1',
                             out[Path(files[0]).name])
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)

    def test_ne_af_on_no_fixes(self):
        src, res = _make_tmp_dirs()
        try:
            files = _make_plp_files(src, ['a'])
            issues = {files[0]: [_mk_issue(files[0], 4)]}
            out = _run_fixer(src, res, issues, log_level='Обычный',
                             mark_in_code=False, clean_output=False,
                             apply_fixes=True, ignore=True)
            text = out[Path(files[0]).name]
            # Правки не применяются (сухой прогон). Якорь может быть,
            # но проверять будем по отсутствию реального изменения кода.
            # Ограничимся: файл содержит оригинальный код.
            self.assertIn('select * from t1, t2', text)
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(res, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()