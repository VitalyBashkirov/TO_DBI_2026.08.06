# -*- coding: utf-8 -*-
"""DS_147e: фикс фильтра sources в TestGeneratorV2 (нормализация префикса)."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TG = PROJECT_ROOT / "SRC" / "analyzer" / "test_generator_v2.py"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "SRC"))


def _tree():
    return ast.parse(TG.read_text(encoding="utf-8"))


def test_ds147e_bom_false():
    assert not TG.read_bytes().startswith(b"\xef\xbb\xbf")


def test_ds147e_ast_parse():
    _tree()


def test_ds147e_split_in_sources_filter():
    """_passes_filters нормализует sources через split по точке."""
    src = TG.read_text(encoding="utf-8")
    assert "s.split(" in src
    assert ".split(" in src


def test_ds147e_import_and_behavior(tmp_path):
    """Проверяем, что TestGeneratorV2 с sources=[PlpCheck] и [PlpCheck.X] эквивалентны."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tg_e", TG)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    gen1 = m.TestGeneratorV2(
        rubricator_dir=PROJECT_ROOT / "DATA" / "Рубрикатор v5",
        sources=["PlpCheck"],
    )
    r1 = gen1.select_rules(None)
    gen2 = m.TestGeneratorV2(
        rubricator_dir=PROJECT_ROOT / "DATA" / "Рубрикатор v5",
        sources=["PlpCheck.DBI.OUTER_JOIN"],
    )
    r2 = gen2.select_rules(None)
    gen3 = m.TestGeneratorV2(
        rubricator_dir=PROJECT_ROOT / "DATA" / "Рубрикатор v5",
        sources=["plpcheck"],
    )
    r3 = gen3.select_rules(None)
    assert len(r1) > 0
    assert r1 == r2 == r3, f"PlpCheck vs PlpCheck.X vs plpcheck: {len(r1)}/{len(r2)}/{len(r3)}"


def test_ds147e_tds_source(tmp_path):
    """sources=[тдс20240828] даёт только тдс20240828.*."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tg_e2", TG)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    gen = m.TestGeneratorV2(
        rubricator_dir=PROJECT_ROOT / "DATA" / "Рубрикатор v5",
        sources=["тдс20240828"],
    )
    rules = gen.select_rules(None)
    assert len(rules) > 0
    for c in rules:
        assert c.startswith("тдс20240828."), c


def test_ds147e_tkloik_source(tmp_path):
    """sources=[тклоик20240828] даёт только тклоик20240828.*."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tg_e3", TG)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    gen = m.TestGeneratorV2(
        rubricator_dir=PROJECT_ROOT / "DATA" / "Рубрикатор v5",
        sources=["тклоик20240828"],
    )
    rules = gen.select_rules(None)
    assert len(rules) > 0
    for c in rules:
        assert c.startswith("тклоик20240828."), c


def test_ds147e_plpcheck_uppercase(tmp_path):
    """sources=[PLPCHECK] (uppercase) работает."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tg_e4", TG)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    gen = m.TestGeneratorV2(
        rubricator_dir=PROJECT_ROOT / "DATA" / "Рубрикатор v5",
        sources=["PLPCHECK"],
    )
    rules = gen.select_rules(None)
    assert len(rules) > 0
    for c in rules:
        assert c.lower().startswith("plpcheck."), c


def test_ds147e_no_sources_returns_all():
    """sources=None -> все правила (без фильтра)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tg_e5", TG)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    gen = m.TestGeneratorV2(
        rubricator_dir=PROJECT_ROOT / "DATA" / "Рубрикатор v5",
    )
    rules = gen.select_rules(None)
    assert len(rules) > 200
