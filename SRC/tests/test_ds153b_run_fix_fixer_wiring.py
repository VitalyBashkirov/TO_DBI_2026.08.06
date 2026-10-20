# -*- coding: utf-8 -*-
"""DS_153b: AST-тесты связки _run_fix -> PLPlusFixer (K2).

Покрывает чек-лист чата 44:
  п.3  — _run_fix: selected_rules через _get_rules_for_selected_files
  п.3b — _run_fix: fixer.flags = _current_header_flags(); передача scanner в fix_directory
  п.3c — _current_fix_flags: defaults regex/hybrid/ai_fallback/ignore/backup/other
  п.9  — Только Ai НЕ влияет на К2: ai_only_var отсутствует в _run_fix,
         присутствует в send_to_ai (K3)
"""
import ast
from pathlib import Path

GUI_PATH = Path(__file__).resolve().parent.parent / "gui_app.py"


def _load_tree():
    return ast.parse(GUI_PATH.read_text(encoding="utf-8"))


def _find_func(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"функция {name} не найдена в gui_app.py")


def _calls_named(node, func_name):
    out = []
    for n in ast.walk(node):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Name) and f.id == func_name:
            out.append(n)
        elif isinstance(f, ast.Attribute) and f.attr == func_name:
            out.append(n)
    return out


def _has_attr_named(node, attr):
    return any(isinstance(n, ast.Attribute) and n.attr == attr
               for n in ast.walk(node))


# ---------- п.3: _run_fix -> _get_rules_for_selected_files ----------
def test_run_fix_uses_get_rules_for_selected_files():
    tree = _load_tree()
    fn = _find_func(tree, "_run_fix")
    calls = _calls_named(fn, "_get_rules_for_selected_files")
    assert calls, "_run_fix должен вызывать _get_rules_for_selected_files"
    src = ast.dump(calls[0])
    assert "selected_files" in src, \
        "_run_fix должен передавать selected_files в _get_rules_for_selected_files"


# ---------- п.3b: _run_fix -> fixer.fix_directory(scanner, ...) ----------
def test_run_fix_calls_fix_directory_with_scanner():
    tree = _load_tree()
    fn = _find_func(tree, "_run_fix")
    calls = _calls_named(fn, "fix_directory")
    assert calls, "_run_fix должен вызывать fixer.fix_directory"
    src = ast.dump(calls[0])
    assert "scanner" in src, \
        "fix_directory должен получать scanner (а не scan_results)"
    assert "fix_only_found" in src, \
        "fix_directory должен получать fix_only_found"


# ---------- п.3b: _run_fix -> fixer.flags = _current_header_flags() ----------
def test_run_fix_assigns_fixer_flags():
    tree = _load_tree()
    fn = _find_func(tree, "_run_fix")
    calls = _calls_named(fn, "_current_header_flags")
    assert calls, "_run_fix должен вызывать _current_header_flags()"
    ok = False
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if (isinstance(t, ast.Attribute) and t.attr == "flags"
                        and isinstance(t.value, ast.Name)
                        and t.value.id == "fixer"):
                    ok = True
    assert ok, "_run_fix должен присваивать fixer.flags = ..."


# ---------- п.3c: _current_fix_flags -> defaults ----------
def test_current_fix_flags_defaults():
    tree = _load_tree()
    fn = _find_func(tree, "_current_fix_flags")
    expected = {"regex", "hybrid", "ai_fallback", "ignore", "backup", "other"}
    found = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Dict):
            keys = {k.value for k in n.keys
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            if expected.issubset(keys):
                found = keys
                break
    assert expected.issubset(found), \
        f"_current_fix_flags: defaults должны содержать {sorted(expected)}"


# ---------- п.9: ai_only_var НЕ в _run_fix, ЕСТЬ в send_to_ai ----------
def test_ai_only_not_in_run_fix_but_in_send_to_ai():
    tree = _load_tree()
    run_fix = _find_func(tree, "_run_fix")
    send_to_ai = _find_func(tree, "send_to_ai")
    assert not _has_attr_named(run_fix, "ai_only_var"), \
        "_run_fix (K2) НЕ должен читать ai_only_var"
    assert not any(isinstance(n, ast.Name) and n.id == "ai_only_var"
                   for n in ast.walk(run_fix)), \
        "_run_fix (K2) НЕ должен ссылаться на ai_only_var"
    assert _has_attr_named(send_to_ai, "ai_only_var"), \
        "send_to_ai (K3) должен читать ai_only_var (фильтр «Только Ai»)"

