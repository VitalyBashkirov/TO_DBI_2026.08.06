# -*- coding: utf-8 -*-
"""DS_144d-c: удаление legacy rubricator_priority_mapping.py (PRIORITY_RULES).

Проверяет:
- файл SRC/rubricator_priority_mapping.py отсутствует;
- ни один .py в SRC/ (кроме SRC/tests/) не импортирует rubricator_priority_mapping;
- в документации упоминания помечены как "удалён" / "DS_144d-c".
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'SRC'
DOCS = [
    ROOT / 'AGENTS.md',
    ROOT / 'DOCUMENTATION_ARM.md',
    ROOT / 'PROMPTS' / 'DS_PROJECT_CONTEXT.md',
]


def test_ds144d_c_file_removed():
    """SRC/rubricator_priority_mapping.py удалён."""
    target = SRC / 'rubricator_priority_mapping.py'
    assert not target.exists(), f"файл не удалён: {target}"


def test_ds144d_c_no_imports_in_src():
    """Ни один .py в SRC/ (кроме SRC/tests/) не импортирует rubricator_priority_mapping."""
    offenders = []
    for py in SRC.rglob('*.py'):
        # пропускаем tests/ — там проверяют отсутствие
        rel = py.relative_to(SRC)
        if rel.parts and rel.parts[0] == 'tests':
            continue
        try:
            tree = ast.parse(py.read_text(encoding='utf-8'))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name == 'rubricator_priority_mapping':
                        offenders.append((str(rel), node.lineno))
            elif isinstance(node, ast.ImportFrom) and node.module == 'rubricator_priority_mapping':
                offenders.append((str(rel), node.lineno))
    assert not offenders, f"импорты rubricator_priority_mapping: {offenders}"


def test_ds144d_c_docs_updated():
    """В документации упоминания rubricator_priority_mapping помечены как удалённые."""
    missing = []
    for doc in DOCS:
        if not doc.exists():
            continue
        text = doc.read_text(encoding='utf-8')
        if 'rubricator_priority_mapping' not in text:
            continue
        # если упоминание есть — рядом должно быть "удалён" или "DS_144d-c"
        ok = False
        for line in text.splitlines():
            if 'rubricator_priority_mapping' in line:
                if 'удалён' in line or 'удален' in line or 'DS_144d-c' in line:
                    ok = True
                    break
        if not ok:
            missing.append(str(doc.relative_to(ROOT)))
    assert not missing, (
        f"в этих файлах упоминание без пометки 'удалён'/'DS_144d-c': {missing}"
    )