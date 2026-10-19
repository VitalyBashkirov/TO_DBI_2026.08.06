# -*- coding: utf-8 -*-
"""DS_147c: AST-тесты замены PRIORITY_RULES на rule.priority из v5.json."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GUI = PROJECT_ROOT / "SRC" / "gui_app.py"

sys.path.insert(0, str(PROJECT_ROOT))


def _gui_tree():
    return ast.parse(GUI.read_text(encoding="utf-8"))


def _find_method(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _method_uses_name(method, name):
    for node in ast.walk(method):
        if isinstance(node, ast.Name) and node.id == name:
            return True
    return False


def _method_imports_module(method, module_name):
    for node in ast.walk(method):
        if isinstance(node, ast.ImportFrom) and node.module == module_name:
            return True
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == module_name:
                    return True
    return False


def test_ds147c_gui_exists():
    assert GUI.exists(), f"нет файла: {GUI}"


def test_ds147c_gui_bom_false():
    b = GUI.read_bytes()
    assert not b.startswith(b"\xef\xbb\xbf"), "BOM недопустим"


def test_ds147c_gui_ast_parse():
    _gui_tree()


def test_ds147c_run_scan_no_priority_rules():
    tree = _gui_tree()
    m = _find_method(tree, "_run_scan")
    assert m is not None, "_run_scan не найден"
    assert not _method_uses_name(m, "PRIORITY_RULES"), "PRIORITY_RULES в _run_scan"
    assert not _method_imports_module(m, "rubricator_priority_mapping"), "import в _run_scan"


def test_ds147c_run_fix_no_priority_rules():
    tree = _gui_tree()
    m = _find_method(tree, "_run_fix")
    assert m is not None, "_run_fix не найден"
    assert not _method_uses_name(m, "PRIORITY_RULES"), "PRIORITY_RULES в _run_fix"
    assert not _method_imports_module(m, "rubricator_priority_mapping"), "import в _run_fix"


def test_ds147c_no_method_uses_priority_rules():
    """Ни один метод не использует PRIORITY_RULES как имя в AST (кроме комментов)."""
    tree = _gui_tree()
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _method_uses_name(node, "PRIORITY_RULES"):
                bad.append(node.name)
    assert not bad, f"PRIORITY_RULES в методах: {bad}"


def test_ds147c_no_module_import_anywhere():
    tree = _gui_tree()
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "rubricator_priority_mapping":
            found.append(node.lineno)
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == "rubricator_priority_mapping":
                    found.append(node.lineno)
    assert not found, f"импорт остался: {found}"


def test_ds147c_uses_rule_priority():
    """В _run_scan/_run_fix фильтр читает priority."""
    src = GUI.read_text(encoding="utf-8")
    assert "selected_priorities" in src
    assert chr(39) + "priority" + chr(39) in src
