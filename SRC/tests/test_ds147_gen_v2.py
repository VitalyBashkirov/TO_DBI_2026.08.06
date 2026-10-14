# -*- coding: utf-8 -*-
# DS_147: pytest-тесты для TestGeneratorV2.
#
# Покрытие:
#   1. импорт;
#   2. конструктор (defaults);
#   3. загрузка правил (332);
#   4. select_rules без фильтров;
#   5. фильтр sources;
#   6. фильтр priorities;
#   7. комбо sources + priorities;
#   8. select_rules по явным кодам;
#   9. safe_name (транслит);
#   10. generate single;
#   11. generate per-rule;
#   12. single: PUBLIC PROCEDURE;
#   13. single: нет дубля -- Правило:;
#   14. procedure: нет begin внутри [+];
#   15. meta: -- Теги: есть;
#   16. BOM=False для выходных файлов.
import os
import re
import sys
from pathlib import Path

import pytest

# sys.path: SRC в PYTHONPATH
_HERE = Path(__file__).resolve()
_SRC = _HERE.parent.parent  # SRC/
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from analyzer.test_generator_v2 import TestGeneratorV2, safe_name


# --- Фикстуры ---

@pytest.fixture(scope='module')
def gen():
    return TestGeneratorV2()


@pytest.fixture(scope='module')
def gen_plpcheck():
    return TestGeneratorV2(sources=['plpcheck'])


@pytest.fixture(scope='module')
def gen_high():
    return TestGeneratorV2(priorities=['HIGH'])


@pytest.fixture(scope='module')
def gen_plpcheck_high():
    return TestGeneratorV2(sources=['plpcheck'], priorities=['HIGH'])


@pytest.fixture
def sample_codes(gen):
    codes = gen.select_rules()
    assert codes, 'нет правил'
    return codes[:3]

# --- 1-3: импорт, конструктор, загрузка ---

def test_01_import():
    from analyzer.test_generator_v2 import TestGeneratorV2 as TG
    assert TG is not None


def test_02_init_defaults():
    g = TestGeneratorV2()
    assert g.rubricator_dir.name == 'Рубрикатор v5'
    assert g.sources is None
    assert g.priorities is None
    assert g.categories is None


def test_03_load_rules(gen):
    # гибко: >= 300
    assert len(gen.rules) >= 300


# --- 4-8: select_rules ---

def test_04_select_all(gen):
    codes = gen.select_rules()
    assert len(codes) == len(gen.rules)
    assert codes == sorted(codes)


def test_05_filter_sources(gen_plpcheck):
    codes = gen_plpcheck.select_rules()
    assert len(codes) >= 100  # гибко: было 152
    assert all(c.startswith('plpcheck.') for c in codes)


def test_06_filter_priorities(gen_high):
    codes = gen_high.select_rules()
    assert len(codes) >= 100  # гибко: было 189
    # все правила HIGH
    for c in codes:
        assert gen_high.rules[c].priority.upper() == 'HIGH'


def test_07_filter_combo(gen_plpcheck, gen_plpcheck_high):
    pc = set(gen_plpcheck.select_rules())
    pc_high = set(gen_plpcheck_high.select_rules())
    # combo — подмножество обоих
    assert pc_high.issubset(pc)
    assert len(pc_high) >= 50  # гибко: было 108


def test_08_select_by_codes(gen):
    codes = gen.select_rules(['plpcheck.ACCESS_STATIC'])
    assert codes == ['plpcheck.ACCESS_STATIC']


# --- 9: safe_name ---

def test_09_safe_name():
    assert safe_name('v50.SQL.OUTERJOIN.п.1.1') == 'v50_SQL_OUTERJOIN_p_1_1'
    assert safe_name('plpcheck.ACCESS_STATIC') == 'plpcheck_ACCESS_STATIC'
    # кириллица транслитерируется
    r = safe_name('тклоик20240828.SUBMIT_JOB.стр.8')
    assert 'стр' not in r
    assert 'str' in r

# --- 10-11: генерация ---

def test_10_generate_single(gen, sample_codes, tmp_path):
    p = gen.generate(rule_codes=sample_codes, mode='single', out_dir=tmp_path)
    assert p is not None
    assert p.exists()
    assert p.suffix == '.plp'
    # имя: test_<src>_<prio>_<cat>_<sel|all>_single_<ts>.plp
    assert re.match(r'^test_.+_(sel|all)_single_\d{8}_\d{6}\.plp$', p.name)


def test_11_generate_per_rule(gen, sample_codes, tmp_path):
    paths = gen.generate(rule_codes=sample_codes, mode='per-rule', out_dir=tmp_path)
    assert isinstance(paths, list)
    assert len(paths) == len(sample_codes)
    for p in paths:
        assert p.exists()
        assert p.suffix == '.plp'
        # имя: test_<safe_name>_<ts>.plp
        assert re.match(r'^test_.+_\d{8}_\d{6}\.plp$', p.name)


# --- 12-15: содержимое ---

def test_12_single_contains_procedure(gen, sample_codes, tmp_path):
    p = gen.generate(rule_codes=sample_codes, mode='single', out_dir=tmp_path)
    txt = p.read_text(encoding='utf-8')
    assert 'PUBLIC PROCEDURE' in txt
    assert txt.count('PUBLIC PROCEDURE') == len(sample_codes)


def test_13_single_no_duplicate_meta(gen, sample_codes, tmp_path):
    p = gen.generate(rule_codes=sample_codes, mode='single', out_dir=tmp_path)
    txt = p.read_text(encoding='utf-8')
    # -- Правило: ровно N раз (без дубля)
    assert txt.count('-- Правило:') == len(sample_codes)


def test_14_no_begin_in_good(gen, tmp_path):
    # берём конкретное правило с declare/begin/end
    code = 'plpcheck.ACCESS_STATIC'
    if code not in gen.rules:
        pytest.skip('нет правила ' + code)
    p = gen.generate(rule_codes=[code], mode='per-rule', out_dir=tmp_path)
    txt = p[0].read_text(encoding='utf-8')
    lines = txt.splitlines()
    in_good = False
    has_begin = False
    for ln in lines:
        if '-- [+] ПРАВИЛЬНО' in ln:
            in_good = True
            continue
        if in_good and '-- end pl/sql' in ln:
            in_good = False
        if in_good and ln.strip().lower().startswith('begin'):
            has_begin = True
    assert not has_begin, 'begin внутри [+]'


def test_15_meta_has_tags(gen, tmp_path):
    code = 'plpcheck.ACCESS_STATIC'
    if code not in gen.rules:
        pytest.skip('нет правила ' + code)
    p = gen.generate(rule_codes=[code], mode='per-rule', out_dir=tmp_path)
    txt = p[0].read_text(encoding='utf-8')
    assert '-- Теги:' in txt


# --- 16: BOM=False ---

def test_16_no_bom(gen, sample_codes, tmp_path):
    p = gen.generate(rule_codes=sample_codes, mode='single', out_dir=tmp_path)
    b = p.read_bytes()
    assert b[:3] != bytes([0xef, 0xbb, 0xbf]), 'BOM в single'
    paths = gen.generate(rule_codes=sample_codes, mode='per-rule', out_dir=tmp_path)
    for pp in paths:
        bb = pp.read_bytes()
        assert bb[:3] != bytes([0xef, 0xbb, 0xbf]), 'BOM в ' + pp.name


# --- main ---

if __name__ == '__main__':
    import pytest as _pt
    _pt.main([__file__, '-v'])