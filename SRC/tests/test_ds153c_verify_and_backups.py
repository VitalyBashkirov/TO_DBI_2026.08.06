# -*- coding: utf-8 -*-
"""DS_153c: AST-тесты верификации (_verify_file), бэкапов (_rescan_ai_files),
логирования fixer (_run_fix).

Покрывает чек-лист чата 44:
  п.5 — _verify_file: remaining_by_rule / remaining_count_by_rule,
        fixed = max(0, before - after), ai_on -> needs_ai_fix/needs_manual
  п.6 — _rescan_ai_files: regex бэкапов (_preai|_YYYYMMDD_HHMMSS) отсеивается
  п.7 — _run_fix: save_log + _bot_log (сводка в bot.log)
"""
import ast
from pathlib import Path

GUI_PATH = Path(__file__).resolve().parent.parent / "gui_app.py"
FIXER_PATH = Path(__file__).resolve().parent.parent / "fixer" / "code_fixer.py"


def _load_tree(path):
    return ast.parse(path.read_text(encoding="utf-8"))


def _find_func(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"функция {name} не найдена")


def _strings_in(node):
    return [n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


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


# ---------- п.5: _verify_file — remaining_by_rule / remaining_count_by_rule ----------
def test_verify_file_has_remaining_keys():
    tree = _load_tree(FIXER_PATH)
    fn = _find_func(tree, "_verify_file")
    # result = {...} должен содержать оба ключа
    keys = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Dict):
            for k in n.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    keys.add(k.value)
    assert "remaining_by_rule" in keys, \
        "_verify_file: result должен содержать remaining_by_rule"
    assert "remaining_count_by_rule" in keys, \
        "_verify_file: result должен содержать remaining_count_by_rule"


# ---------- п.5: _verify_file — fixed = max(0, before - after) ----------
def test_verify_file_uses_max_zero():
    tree = _load_tree(FIXER_PATH)
    fn = _find_func(tree, "_verify_file")
    calls = _calls_named(fn, "max")
    assert calls, "_verify_file должен вызывать max(0, ...) для fixed"
    # в аргументах max должен быть Sub (before - after) и Constant 0
    ok = False
    for c in calls:
        has_zero = any(isinstance(a, ast.Constant) and a.value == 0
                       for a in c.args)
        has_sub = any(isinstance(a, ast.BinOp) and isinstance(a.op, ast.Sub)
                      for a in c.args)
        if has_zero and has_sub:
            ok = True
            break
    assert ok, "_verify_file: fixed = max(0, before - after) не найден"


# ---------- п.5: _verify_file — ai_on -> needs_ai_fix / needs_manual ----------
def test_verify_file_ai_on_branch():
    tree = _load_tree(FIXER_PATH)
    fn = _find_func(tree, "_verify_file")
    strings = _strings_in(fn)
    assert "needs_ai_fix" in strings, \
        "_verify_file: должен фигурировать needs_ai_fix"
    assert "needs_manual" in strings, \
        "_verify_file: должен фигурировать needs_manual"
    assert "ai_fallback" in strings, \
        "_verify_file: должен читать флаг ai_fallback"


# ---------- п.6: _rescan_ai_files — regex бэкапов ----------
def test_rescan_ai_files_backup_regex():
    tree = _load_tree(GUI_PATH)
    fn = _find_func(tree, "_rescan_ai_files")
    strings = _strings_in(fn)
    joined = "\n".join(strings)
    assert "_preai" in joined, \
        "_rescan_ai_files: regex должен содержать _preai"
    assert "\\d{8}" in joined, \
        "_rescan_ai_files: regex должен содержать \\d{8} (бэкап _YYYYMMDD)"
    assert ".plp$" in joined, \
        "_rescan_ai_files: regex должен якориться на .plp$"


# ---------- п.7: _run_fix — save_log + _bot_log ----------
def test_run_fix_save_log_and_bot_log():
    tree = _load_tree(GUI_PATH)
    fn = _find_func(tree, "_run_fix")
    assert _calls_named(fn, "save_log"), \
        "_run_fix должен вызывать fixer.save_log(...)"
    assert _calls_named(fn, "_bot_log"), \
        "_run_fix должен писать сводку в bot.log (_bot_log)"

