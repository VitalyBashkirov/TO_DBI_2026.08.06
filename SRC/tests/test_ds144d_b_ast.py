# -*- coding: utf-8 -*-
"""DS_144d-b: полнота маппинга 34 plpcheck-subcategory <-> 7 агрегатов.

Проверяет:
- все 7 агрегатов PLPCHECK_RULE_TO_CATEGORY непусты;
- все значения маппинга принадлежат {7 агрегатов} u {"OTHER"};
- в v5.json ровно 34 уникальных plpcheck-subcategory (слепок);
- B2c: каждый plpcheck-код явно присутствует в PLPCHECK_RULE_TO_CATEGORY
  (fallback "OTHER" в TestGeneratorV2._passes_filters для plpcheck не используется).
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCANNER = ROOT / 'SRC' / 'analyzer' / 'scanner.py'
V5 = ROOT / 'DATA' / 'Рубрикатор v5' / '4.RUBRICATOR_PROMPT v5.json'

SEVEN_AGGREGATES = {
    'STYLE.PREFIXES',
    'STYLE.PREFIX_COMBINATION',
    'STYLE.SYNTAX',
    'SQL.CHECKS',
    'WEB.ADAPTATION',
    'DBI.ADAPTATION',
    'OTHER',
}

EXPECTED_PLPCHECK_SUBCATEGORIES = 34


def _load_mapping():
    sys.path.insert(0, str(ROOT / 'SRC'))
    try:
        spec = importlib.util.spec_from_file_location('_scanner_ds144d_b', SCANNER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return dict(mod.PLPCHECK_RULE_TO_CATEGORY)
    finally:
        sys.path.pop(0)


def _load_v5_rules():
    raw = V5.read_text(encoding='utf-8')
    return json.loads(raw)['rules']


def _plpcheck_rules(rules):
    return {code: r for code, r in rules.items() if r.get('source') == 'plpcheck'}


def test_ds144d_b_seven_aggregates_nonempty():
    """Каждый из 7 агрегатов встречается хотя бы у одного правила в маппинге."""
    mapping = _load_mapping()
    used = set(mapping.values())
    missing = SEVEN_AGGREGATES - used
    assert not missing, f"пустые агрегаты (нет ни одного правила): {sorted(missing)}"


def test_ds144d_b_plpcheck_values_in_known_aggregates():
    """Все значения PLPCHECK_RULE_TO_CATEGORY принадлежат 7 агрегатам u {OTHER}."""
    mapping = _load_mapping()
    bad = {code: agg for code, agg in mapping.items() if agg not in SEVEN_AGGREGATES}
    assert not bad, f"значения вне известных агрегатов: {bad}"


def test_ds144d_b_34_plpcheck_subcategories_present():
    """В v5.json ровно 34 уникальных plpcheck-subcategory (слепок)."""
    rules = _load_v5_rules()
    plp = _plpcheck_rules(rules)
    subs = sorted({r.get('subcategory') for r in plp.values() if r.get('subcategory')})
    assert len(subs) == EXPECTED_PLPCHECK_SUBCATEGORIES, (
        f"ожидалось {EXPECTED_PLPCHECK_SUBCATEGORIES} plpcheck-subcategory, "
        f"получено {len(subs)}: {subs}"
    )


def test_ds144d_b_each_plpcheck_code_explicitly_mapped():
    """B2c: каждый plpcheck-код явно присутствует в PLPCHECK_RULE_TO_CATEGORY.

    Fallback "OTHER" в TestGeneratorV2._passes_filters для plpcheck не используется.
    """
    mapping = _load_mapping()
    rules = _load_v5_rules()
    plp = _plpcheck_rules(rules)

    missing = sorted(c for c in plp if c not in mapping)
    assert not missing, (
        f"plpcheck-коды без явного маппинга ({len(missing)} шт.): {missing}"
    )