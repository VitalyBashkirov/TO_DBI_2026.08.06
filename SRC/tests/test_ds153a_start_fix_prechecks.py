# -*- coding: utf-8 -*-
"""DS_153a: AST-тесты pre-checks K2 («Исправить код»).

Покрывает чек-лист чата 44:
  п.1  — _run_fix: нет scan_results -> "Сначала выполните сканирование (K1)."
  п.1b — _run_fix: total_issues == 0 -> "Проблем не найдено."
  п.2  — start_fix: нет selected_rules -> "Выберите хотя бы один файл..."
  п.2b — start_fix: нет source_dir -> "Укажите исходный каталог!"
  п.0  — start_fix: проверки идут ДО threading.Thread(target=self._run_fix)
"""
import ast
from pathlib import Path

GUI_PATH = Path(__file__).resolve().parent.parent / "gui_app.py"


def _load_tree():
    src = GUI_PATH.read_text(encoding="utf-8")
    return ast.parse(src)


def _find_func(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"функция {name} не найдена в gui_app.py")


def _strings_in(node):
    return [n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _calls_named(node, func_name):
    """Все Call-узлы, где вызывается имя func_name (Name или Attribute)."""
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


def _has_none_compare(node):
    for n in ast.walk(node):
        if isinstance(n, ast.Compare) and any(isinstance(op, ast.Is) for op in n.ops):
            for c in n.comparators:
                if isinstance(c, ast.Constant) and c.value is None:
                    return True
    return False


# ---------- п.2: start_fix — нет selected_rules ----------
def test_start_fix_no_selected_rules_message():
    tree = _load_tree()
    fn = _find_func(tree, "start_fix")
    strings = _strings_in(fn)
    assert "Выберите хотя бы один файл в рубрикаторе!" in strings, \
        "start_fix должен содержать сообщение о пустом selected_rules"
    assert any(n.id == "any_rule_selected"
               for n in ast.walk(fn) if isinstance(n, ast.Name)), \
        "start_fix должен вычислять any_rule_selected"


# ---------- п.2b: start_fix — нет source_dir ----------
def test_start_fix_no_source_dir_message():
    tree = _load_tree()
    fn = _find_func(tree, "start_fix")
    strings = _strings_in(fn)
    assert "Укажите исходный каталог!" in strings, \
        "start_fix должен содержать сообщение о пустом source_dir"


# ---------- п.1: _run_fix — нет scan_results / scanner ----------
def test_run_fix_no_scan_results_dialog():
    tree = _load_tree()
    fn = _find_func(tree, "_run_fix")
    strings = _strings_in(fn)
    assert "Сначала выполните сканирование (K1)." in strings, \
        "_run_fix должен содержать сообщение о необходимости K1"
    assert _calls_named(fn, "_show_copyable_dialog"), \
        "_run_fix должен вызывать _show_copyable_dialog при отсутствии scanner"
    assert _has_none_compare(fn), \
        "_run_fix должен содержать проверку `scanner is None`"


# ---------- п.1b: _run_fix — total_issues == 0 ----------
def test_run_fix_zero_issues_message():
    tree = _load_tree()
    fn = _find_func(tree, "_run_fix")
    strings = _strings_in(fn)
    assert any("Проблем не найдено" in s for s in strings), \
        "_run_fix должен содержать сообщение о нуле проблем"
    assert any("total_issues" in s for s in strings), \
        "_run_fix должен обращаться к total_issues"


# ---------- п.0: порядок проверок ДО threading.Thread ----------
def test_start_fix_checks_before_thread():
    tree = _load_tree()
    fn = _find_func(tree, "start_fix")
    msg_src_dir_ln = None
    msg_rules_ln = None
    thread_ln = None
    for n in ast.walk(fn):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            if n.value == "Укажите исходный каталог!":
                msg_src_dir_ln = n.lineno
            elif n.value == "Выберите хотя бы один файл в рубрикаторе!":
                msg_rules_ln = n.lineno
        if isinstance(n, ast.Call):
            f = n.func
            is_thread = (
                (isinstance(f, ast.Attribute) and f.attr == "Thread")
                or (isinstance(f, ast.Name) and f.id == "Thread")
            )
            if is_thread:
                thread_ln = n.lineno
    assert msg_src_dir_ln is not None
    assert msg_rules_ln is not None
    assert thread_ln is not None, "threading.Thread(...) не найден в start_fix"
    assert msg_src_dir_ln < thread_ln, \
        "проверка source_dir должна быть ДО запуска потока"
    assert msg_rules_ln < thread_ln, \
        "проверка selected_rules должна быть ДО запуска потока"

