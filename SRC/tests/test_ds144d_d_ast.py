# -*- coding: utf-8 -*-
"""DS_144d-d: замена 6 legacy-комментариев PRIORITY_RULES в gui_app.py.

Проверяет:
- в AST gui_app.py нет ast.Name(id='PRIORITY_RULES');
- в комментариях gui_app.py нет 'PRIORITY_RULES' без пометки legacy/DS_144d-d/удалён;
- (D2) нет строки '# Формируем ...' без отступа.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUI = ROOT / 'SRC' / 'gui_app.py'


def _read():
    return GUI.read_text(encoding='utf-8')


def test_ds144d_d_no_priority_rules_as_name_in_ast():
    """PRIORITY_RULES не используется как ast.Name (только в комментариях)."""
    tree = ast.parse(_read())
    bad = [node.lineno for node in ast.walk(tree)
           if isinstance(node, ast.Name) and node.id == 'PRIORITY_RULES']
    assert not bad, f"PRIORITY_RULES как ast.Name на строках: {bad}"


def test_ds144d_d_comments_replaced():
    """В комментариях gui_app.py нет 'PRIORITY_RULES' без пометки legacy/DS_144d-d/удалён."""
    offenders = []
    for i, line in enumerate(_read().splitlines(), 1):
        stripped = line.lstrip()
        if not stripped.startswith('#'):
            continue
        if 'PRIORITY_RULES' not in line:
            continue
        if 'legacy' in line.lower() or 'DS_144d-d' in line or 'удалён' in line or 'удален' in line:
            continue
        offenders.append((i, line.strip()))
    assert not offenders, f"комментарии с PRIORITY_RULES без пометки: {offenders}"


def test_ds144d_d_comment_indent_fixed():
    """D2: строка '# Формируем ...' имеет отступ (не в начале строки)."""
    bad = []
    for i, line in enumerate(_read().splitlines(), 1):
        if '# Формируем отсортированный список правил' in line:
            if not line.startswith(' '):
                bad.append((i, line))
    assert not bad, f"строка без отступа: {bad}"