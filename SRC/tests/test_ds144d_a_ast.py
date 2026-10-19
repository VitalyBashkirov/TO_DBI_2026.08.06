# -*- coding: utf-8 -*-
"""DS_144d-a: аудит фильтров АРМа по параметрам рубрикаторов (вариант B).

Фиксирует текущее поведение (слепок):
- что доходит до TestGeneratorV2 из gui_app._run_test_generation;
- как применяется по источникам plpcheck/v53/тдс20240828/тклоик20240828;
- дефект E2 (categories PlpCheck протекают на не-plpcheck источники),
  который будет исправлен в DS_144d-e.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUI = ROOT / 'SRC' / 'gui_app.py'
TG2 = ROOT / 'SRC' / 'analyzer' / 'test_generator_v2.py'
SCANNER = ROOT / 'SRC' / 'analyzer' / 'scanner.py'


def _read(p):
    return p.read_text(encoding='utf-8')


def test_ds144d_a_plpcheck_categories_filter_is_only_plpcheck():
    """Атрибут plpcheck_categories_filter не упоминается в контексте v53/тдс/тклоик."""
    src = _read(GUI)
    hits = [ln for ln in src.splitlines() if 'plpcheck_categories_filter' in ln]
    assert len(hits) >= 6, "ожидалось >=6 вхождений plpcheck_categories_filter"
    for h in hits:
        assert 'v53' not in h
        assert 'тдс' not in h
        assert 'тклоик' not in h


def test_ds144d_a_run_test_generation_passes_all_filters():
    """_run_test_generation передаёт sources/priorities/categories в TestGeneratorV2.

    Вызов многострочный — regex с .*? обрывается на первой ')',
    поэтому берём окно фиксированной длины после 'TestGeneratorV2('.
    """
    src = _read(GUI)
    idx = src.find('TestGeneratorV2(')
    assert idx >= 0, "вызов TestGeneratorV2(...) не найден в gui_app.py"
    block = src[idx: idx + 800]
    for key in ('sources=', 'priorities=', 'categories='):
        assert key in block, f"отсутствует {key} в TestGeneratorV2(...)"


def test_ds144d_a_passes_filters_three_branches():
    """_passes_filters учитывает self.sources, self.priorities, self.categories."""
    src = _read(TG2)
    tree = ast.parse(src)
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == '_passes_filters'), None)
    assert fn is not None
    body = ast.get_source_segment(src, fn) or ''
    for token in ('self.sources', 'self.priorities', 'self.categories'):
        assert token in body, f"отсутствует {token} в _passes_filters"


def test_ds144d_a_categories_is_hybrid_a_union_b():
    """categories в TestGeneratorV2 — гибрид A (PLPCHECK_RULE_TO_CATEGORY) ∪ B (subcategory)."""
    src = _read(TG2)
    assert 'PLPCHECK_RULE_TO_CATEGORY' in src
    assert re.search(r'PLPCHECK_RULE_TO_CATEGORY\.get\(', src)
    assert 'subcategory' in src


def test_ds144d_a_plpcheck_rule_to_category_defined_in_scanner():
    """PLPCHECK_RULE_TO_CATEGORY определён как Dict[str, str] в scanner.py."""
    src = _read(SCANNER)
    assert 'PLPCHECK_RULE_TO_CATEGORY' in src
    assert re.search(r'PLPCHECK_RULE_TO_CATEGORY\s*:\s*Dict\[str,\s*str\]', src)


def test_ds144d_a_e2_defect_fixed():
    """DS_144d-e: defect E2 fixed - categories gated by sources.

    Old: categories=list(getattr(self, PLPCHECK_CATS_FILTER, [])) or None,
    New: _cats = ...; if _cats: ... _srcs_norm != {PLPCHECK} -> _cats = None;
         categories=_cats,
    """
    src = _read(GUI)
    old_marker = "categories=list(getattr(self, " + chr(39) + "plpcheck_categories_filter" + chr(39)
    assert old_marker not in src
    new_marker = "_cats = list(getattr(self, " + chr(39) + "plpcheck_categories_filter" + chr(39)
    assert new_marker in src
    assert "if _srcs_norm != {" + chr(39) + "plpcheck" + chr(39) + "}:" in src
    assert "categories=_cats," in src
