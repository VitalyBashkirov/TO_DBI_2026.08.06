# -*- coding: utf-8 -*-
"""
DS_146: тесты — DeepScanner удалён из GUI.

Проверки через AST (не через текст): не зависит от упоминаний
`start_deep_scan` в docstring, только от структуры кода.

Всего проверок: 12.
"""
import ast
from pathlib import Path

import pytest

GUI_PATH = Path(__file__).parent.parent / "gui_app.py"
DEEP_PATH = Path(__file__).parent.parent / "analyzer" / "deep_scanner.py"
STD_PATH = Path(__file__).parent.parent.parent / "EXCHANGE" / "DS_STANDARD.md"


# ---------- Фикстуры ----------

@pytest.fixture(scope="module")
def gui_tree():
    src = GUI_PATH.read_text(encoding="utf-8")
    return ast.parse(src)


@pytest.fixture(scope="module")
def deep_tree():
    src = DEEP_PATH.read_text(encoding="utf-8")
    return ast.parse(src)


@pytest.fixture(scope="module")
def gui_src():
    return GUI_PATH.read_text(encoding="utf-8")


# ---------- 1-4: в gui_app.py НЕТ кода start_deep_scan ----------

def test_no_functiondef_start_deep_scan(gui_tree):
    """AST: нет определения def start_deep_scan."""
    names = [n.name for n in ast.walk(gui_tree) if isinstance(n, ast.FunctionDef)]
    assert "start_deep_scan" not in names, f"start_deep_scan всё ещё определён: {names}"


def test_no_attribute_start_deep_scan(gui_tree):
    """AST: нет обращений self.start_deep_scan."""
    attrs = [n.attr for n in ast.walk(gui_tree) if isinstance(n, ast.Attribute)]
    assert "start_deep_scan" not in attrs, "self.start_deep_scan всё ещё вызывается"


def test_no_control_f5_binding(gui_tree):
    """AST: нет строкового литерала '<Control-F5>'."""
    strings = [n.value for n in ast.walk(gui_tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    matches = [s for s in strings if "<Control-F5>" in s]
    assert not matches, f"bind Control-F5 всё ещё есть: {matches}"


def test_no_algoritm_deep_menu(gui_tree):
    """AST: нет строкового литерала с 'Алгоритм Deep'."""
    strings = [n.value for n in ast.walk(gui_tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    matches = [s for s in strings if "Алгоритм Deep" in s]
    assert not matches, f"пункт меню 'Алгоритм Deep' всё ещё есть: {matches}"


# ---------- 5-7: ключевые методы на месте ----------

def _function_names(tree):
    return [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]


def test_has_start_scan(gui_tree):
    """AST: def start_scan присутствует (1 раз)."""
    names = _function_names(gui_tree)
    assert names.count("start_scan") == 1


def test_has_run_scan(gui_tree):
    """AST: def _run_scan присутствует (1 раз)."""
    names = _function_names(gui_tree)
    assert names.count("_run_scan") == 1


def test_has_start_fix(gui_tree):
    """AST: def start_fix присутствует (1 раз)."""
    names = _function_names(gui_tree)
    assert names.count("start_fix") == 1


# ---------- 8: deep_mode сохранён ----------

def test_run_scan_has_deep_mode_param(gui_tree):
    """AST: _run_scan сохраняет параметр deep_mode (default=False)."""
    for node in ast.walk(gui_tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_run_scan":
            args = [a.arg for a in node.args.args]
            assert "deep_mode" in args, f"deep_mode отсутствует: {args}"
            # проверяем default=False
            defaults = node.args.defaults
            if defaults:
                last = defaults[-1]
                assert isinstance(last, ast.Constant) and last.value is False
            return
    pytest.fail("_run_scan не найден")


# ---------- 9-10: deep_scanner.py (CLI-путь) ----------

def test_deep_scanner_importable():
    """DeepScanner импортируется, метод run существует."""
    import importlib
    mod = importlib.import_module("analyzer.deep_scanner")
    assert hasattr(mod, "DeepScanner")
    assert hasattr(mod.DeepScanner, "run")


def test_deep_scanner_uses_plplus(deep_tree):
    """AST: DeepScanner.run использует PLPlusScanner (через ImportFrom)."""
    imported = []
    for node in ast.walk(deep_tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for a in node.names:
                imported.append((mod, a.name))
    assert any("scanner" in mod and name == "PLPlusScanner" for mod, name in imported), \
        f"PLPlusScanner не импортируется: {imported}"


# ---------- 11: DS_STANDARD.md содержит §6.6.26 и §6.6.27 ----------

def test_ds_standard_has_sections():
    """DS_STANDARD.md содержит §6.6.26 и §6.6.27."""
    src = STD_PATH.read_text(encoding="utf-8")
    assert "§6.6.26" in src, "§6.6.26 отсутствует в DS_STANDARD.md"
    assert "§6.6.27" in src, "§6.6.27 отсутствует в DS_STANDARD.md"


# ---------- 12: smoke DeepScanner.run() на пустом каталоге ----------

def test_deep_scanner_smoke_empty_dir(tmp_path):
    """Smoke: DeepScanner.run() на пустом каталоге с одним правилом — не падает."""
    from analyzer.deep_scanner import DeepScanner

    scanner = DeepScanner(
        source_dir=str(tmp_path),
        selected_rules=["plpcheck.BAD_PREFIX"],
        log_callback=lambda m, l="info": None,
        progress_callback=lambda p: None,
        status_callback=lambda m: None,
    )
    result = scanner.run()
    assert isinstance(result, tuple) and len(result) == 2, \
        f"run() вернул не (stats, path): {type(result)}"
    stats, report_path = result
    assert isinstance(stats, dict)
    assert "total_issues" in stats
    assert stats["files_scanned"] == 0
    assert stats["total_issues"] == 0
