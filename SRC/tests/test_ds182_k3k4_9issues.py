# -*- coding: utf-8 -*-
"""DS_182: префикс-фильтр ['plpcheck.'] включает многострочные DS_033-проверки.

Регрессионный тест: до DS_182 `_is_rule_selected('plpcheck.BAD_PREFIX')` при
selected_rules=['plpcheck.'] возвращал False, и многострочные проверки PlpCheck
отключались. После правки — True, а `scan_file` находит их issues.
"""
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

from analyzer.scanner import PLPlusScanner  # noqa: E402
from rubricator_prompts import RubricatorPrompts  # noqa: E402

RUB = Path(r"F:\TO_DBI\DATA\Рубрикатор v5")
FILES = [
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\DEPN\PSH_ED_PRC_SCHM.plp"),
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\PL_US\PSH_PS_DEL.plp"),
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\RKO\PSH_VK_UNK_INP.plp"),
]

ML_RULES = {
    "plpcheck.BAD_PREFIX",
    "plpcheck.NOT_MENTIONED",
    "plpcheck.PREFIX_TYPE_IN_VAR_NAME",
    "plpcheck.WRONG_METHOD_SYNTAX",
    "plpcheck.CODE_IN_COMMENT",
    "plpcheck.SUBOPTIMAL_QUERY_WROWNUM",
}


def _cfg():
    return {
        "paths": {"source_dir": r"F:\TO_DBI\PATCH_IN",
                  "results_dir": r"F:\TO_DBI\PATCH_CALC"},
        "scan": {"file_pattern": "**/*.plp", "exclude_patterns": []},
    }


def _make(selected_rules):
    rp = RubricatorPrompts(RUB)
    assert rp.load(), "рубрикатор не загрузился"
    return PLPlusScanner(_cfg(), selected_rules, rp)


def _scan_all(scanner):
    issues = []
    for f in FILES:
        assert f.exists(), f"нет входного файла: {f}"
        scanner.scan_file(f)
        issues.extend(scanner.issues)
        scanner.issues.clear()
    return issues


def _rule(it):
    if isinstance(it, dict):
        return it.get("rule") or it.get("issue_type") or it.get("rule_id") or it.get("code")
    for a in ("rule", "issue_type", "rule_id", "code"):
        v = getattr(it, a, None)
        if v:
            return v
    return None


# --- 1. Прямой юнит-тест на правку _is_rule_selected ---

@pytest.mark.parametrize("rule_id", sorted(ML_RULES))
def test_is_rule_selected_plpcheck_prefix_true(rule_id):
    sc = _make(["plpcheck."])
    assert sc._is_rule_selected(rule_id) is True, (
        f"DS_182 регресс: при selected_rules=['plpcheck.'] "
        f"_is_rule_selected({rule_id!r}) должно быть True"
    )


def test_is_rule_selected_empty_still_true():
    sc = _make([])
    for r in ML_RULES:
        assert sc._is_rule_selected(r) is True


def test_is_rule_selected_exact_other_false():
    # Точечный фильтр не должен расширяться: при выборе CODE_IN_COMMENT
    # остальные многострочные правила отключены.
    sc = _make(["plpcheck.CODE_IN_COMMENT"])
    assert sc._is_rule_selected("plpcheck.CODE_IN_COMMENT") is True
    for r in ML_RULES - {"plpcheck.CODE_IN_COMMENT"}:
        assert sc._is_rule_selected(r) is False, (
            f"DS_182 регресс: при точечном фильтре {r!r} не должно быть выбранным"
        )


# --- 2. Регрессионный тест на scan_file ---

def test_plpcheck_prefix_finds_multiline_issues():
    sc = _make(["plpcheck."])
    issues = _scan_all(sc)
    assert issues, "DS_182 регресс: при ['plpcheck.'] не найдено ни одного issue"
    found = {_rule(it) for it in issues}
    ml_found = found & ML_RULES
    assert ml_found, (
        f"DS_182 регресс: при ['plpcheck.'] не найдено ни одной "
        f"многострочной DS_033-проверки из {sorted(ML_RULES)}; "
        f"найдено правил: {sorted(found)[:20]}"
    )
    # ключевые правила из матрицы 49: CODE_IN_COMMENT и NOT_MENTIONED
    assert "plpcheck.CODE_IN_COMMENT" in found, "нет CODE_IN_COMMENT"
    assert "plpcheck.NOT_MENTIONED" in found, "нет NOT_MENTIONED"


def test_code_in_comment_only():
    sc = _make(["plpcheck.CODE_IN_COMMENT"])
    issues = _scan_all(sc)
    found = {_rule(it) for it in issues}
    assert found == {"plpcheck.CODE_IN_COMMENT"}, (
        f"DS_182 регресс: при ['plpcheck.CODE_IN_COMMENT'] "
        f"ожидалось только CODE_IN_COMMENT, найдено: {sorted(found)}"
    )
    assert issues, "нет ни одного CODE_IN_COMMENT"