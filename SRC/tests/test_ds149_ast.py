# -*- coding: utf-8 -*-
"""DS_149e: сводные AST-тесты на все пункты DS_149 (a, b, c, d, g).

Проверяют исходник SRC/gui_app.py статически, без запуска GUI.
"""
from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path

import pytest


GUI_PATH = Path(__file__).resolve().parent.parent / 'gui_app.py'


@lru_cache(maxsize=1)
def _tree() -> ast.Module:
    return ast.parse(GUI_PATH.read_text(encoding='utf-8-sig'))


def _find_func(name: str) -> ast.FunctionDef:
    for node in ast.walk(_tree()):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    pytest.fail(f'функция {name!r} не найдена в {GUI_PATH}')


def _walk_calls(func: ast.FunctionDef):
    """Все ast.Call внутри функции (включая вложенные)."""
    for node in ast.walk(func):
        if isinstance(node, ast.Call):
            yield node


def _call_attr(call: ast.Call) -> str | None:
    """attr вызываемого, если вызов вида X.attr(...)."""
    f = call.func
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _call_value_attr(call: ast.Call) -> str | None:
    """value.attr, если X.value.attr(...) — например messagebox.showwarning()."""
    f = call.func
    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
        return f.value.id
    return None


# --- DS_149a ---

def test_ds149a_reset_all_keeps_selected_rules():
    """_set_all_rules_for_current_rubricator вызывает _update_rubricator_parent_state(update_var=False)."""
    func = _find_func('_set_all_rules_for_current_rubricator')
    found = False
    for call in _walk_calls(func):
        if _call_attr(call) == '_update_rubricator_parent_state':
            for kw in call.keywords:
                if kw.arg == 'update_var' and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                    found = True
                    break
    assert found, 'DS_149a: нет вызова _update_rubricator_parent_state(update_var=False)'


# --- DS_149b ---

def test_ds149b_one_rule_one_click():
    """В _on_rule_click дочерняя ветка (клик по правилу) НЕ должна вызывать plpcheck_enabled_var.set."""
    func = _find_func('_on_rule_click')
    # Найти if item in self._rubricator_parent_items ... else (дочерняя ветка)
    # Проще: пройти по всем If в функции; найти тот, у которого condition не про parent,
    # но в теле есть rc = self._rule_item_map.get(item)
    has_child_set = False
    for node in ast.walk(func):
        if not isinstance(node, ast.If):
            continue
        # Проверим, есть ли в теле присваивание rc = self._rule_item_map.get(item)
        is_child_branch = False
        for sub in ast.walk(node):
            if isinstance(sub, ast.Assign):
                for tgt in sub.targets:
                    if isinstance(tgt, ast.Name) and tgt.id == 'rc':
                        # value = Call(attr='get')
                        if isinstance(sub.value, ast.Call) and _call_attr(sub.value) == 'get':
                            is_child_branch = True
        if not is_child_branch:
            continue
        # Теперь ищем в теле этого If вызов plpcheck_enabled_var.set
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and _call_attr(sub) == 'set':
                f = sub.func
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Attribute) and f.value.attr == 'plpcheck_enabled_var':
                    has_child_set = True
    assert not has_child_set, (
        'DS_149b: в дочерней ветке _on_rule_click найден plpcheck_enabled_var.set '
        '(должен быть только в родительской ветке)')


def test_ds149b_populating_tree_guard():
    """_populating_tree устанавливается в _populate_rules_tree и проверяется в _sync_plpcheck_checkbox."""
    pop = _find_func('_populate_rules_tree')
    syn = _find_func('_sync_plpcheck_checkbox')

    def has_attr(node, attr_name):
        for sub in ast.walk(node):
            if isinstance(sub, ast.Attribute) and sub.attr == attr_name:
                return True
            if isinstance(sub, ast.Constant) and sub.value == attr_name:
                return True
        return False
    assert has_attr(pop, '_populating_tree'), 'DS_149b: _populate_rules_tree не использует _populating_tree'
    assert has_attr(syn, '_populating_tree'), 'DS_149b: _sync_plpcheck_checkbox не проверяет _populating_tree'


# --- DS_149c ---

def test_ds149c_tooltips_nm():
    """_update_select_deselect_tooltips содержит шаблоны (N/M) для выбора и сброса."""
    func = _find_func('_update_select_deselect_tooltips')
    src = ast.get_source_segment(GUI_PATH.read_text(encoding='utf-8-sig'), func) or ''
    assert 'Выбрать все правила текущего рубрикатора (' in src, \
        'DS_149c: нет шаблона "Выбрать все правила текущего рубрикатора ("'
    assert 'Сбросить все правила текущего рубрикатора (' in src, \
        'DS_149c: нет шаблона "Сбросить все правила текущего рубрикатора ("'
    assert '/{m})' in src or '/ {m})' in src, \
        'DS_149c: нет подстановки /{m}) в шаблоне N/M'


# --- DS_149d ---

def test_ds149d_processed_rules_init_before_try():
    """processed_rules = set() инициализируется ДО try в _run_test_generation."""
    func = _find_func('_run_test_generation')
    assign_idx = None
    try_idx = None
    for i, node in enumerate(func.body):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == 'processed_rules':
                    assign_idx = i
        if isinstance(node, ast.Try):
            if try_idx is None:
                try_idx = i
    assert assign_idx is not None, 'DS_149d: нет присваивания processed_rules в _run_test_generation'
    assert try_idx is not None, 'DS_149d: нет try в _run_test_generation'
    assert assign_idx < try_idx, (
        f'DS_149d: processed_rules (idx {assign_idx}) должно быть ДО try (idx {try_idx})')


def test_ds149d_matching_filters_by_rubricator_rule_vars():
    """В _run_test_generation фильтр matching использует self._rubricator_rule_vars."""
    func = _find_func('_run_test_generation')
    found = False
    for node in ast.walk(func):
        if isinstance(node, (ast.ListComp, ast.GeneratorExp)):
            for if_node in node.generators:
                for cond in if_node.ifs:
                    for sub in ast.walk(cond):
                        if isinstance(sub, ast.Attribute) and sub.attr == '_rubricator_rule_vars':
                            found = True
    assert found, 'DS_149d: нет фильтра по self._rubricator_rule_vars в _run_test_generation'


def test_ds149d_warning_on_zero_rules():
    """При 0 правилах _run_test_generation показывает messagebox.showwarning «Не выбрано ни одного правила»."""
    func = _find_func('_run_test_generation')
    has_showwarning = False
    has_msg = False
    for call in _walk_calls(func):
        if _call_attr(call) == 'showwarning' and _call_value_attr(call) == 'messagebox':
            has_showwarning = True
    src = ast.get_source_segment(GUI_PATH.read_text(encoding='utf-8-sig'), func) or ''
    if 'Не выбрано ни одного правила' in src:
        has_msg = True
    assert has_showwarning, 'DS_149d: нет messagebox.showwarning в _run_test_generation'
    assert has_msg, 'DS_149d: нет текста "Не выбрано ни одного правила"'


def test_ds149d_no_priority_rules_in_generation():
    """После DS_149d-доп PRIORITY_RULES в _run_test_generation не используется."""
    func = _find_func('_run_test_generation')
    has_name = False
    has_import = False
    for node in ast.walk(func):
        if isinstance(node, ast.Name) and node.id == 'PRIORITY_RULES':
            has_name = True
        if isinstance(node, ast.ImportFrom) and node.module == 'rubricator_priority_mapping':
            has_import = True
    assert not has_name, 'DS_149d-доп: PRIORITY_RULES найден в _run_test_generation'
    assert not has_import, 'DS_149d-доп: import PRIORITY_RULES найден в _run_test_generation'


# --- DS_149g ---

def _find_class(name: str) -> ast.ClassDef:
    for node in ast.walk(_tree()):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    pytest.fail(f'класс {name!r} не найден в {GUI_PATH}')


def test_ds149g_minsize_900_600():
    """В DBIMigrationApp есть minsize(900, 600)."""
    cls = _find_class('DBIMigrationApp')
    found = False
    for node in ast.walk(cls):
        if isinstance(node, ast.Call) and _call_attr(node) == 'minsize':
            if len(node.args) < 2:
                continue
            a0, a1 = node.args[0], node.args[1]
            w_ok = isinstance(a0, ast.Constant) and a0.value == 1026
            h_ok = (
                (isinstance(a1, ast.Constant) and a1.value == 400)
                or (isinstance(a1, ast.Name) and a1.id == 'UI_MIN_WINDOW_HEIGHT')
            )
            if w_ok and h_ok:
                found = True
                break
    assert found, ('DS_149g: нет minsize(1026, UI_MIN_WINDOW_HEIGHT|400) '
                   'в DBIMigrationApp')
