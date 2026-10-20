# -*- coding: utf-8 -*-
"""DS_154 (OQ-1): _is_rule_selected narrows plpcheck.* by full rule code.

Tests:
  #7 functional: selected=['plpcheck.BAD_PREFIX'] -> no other plpcheck.*
  #8 AST: multiline _check_plp_* calls are guarded by _is_rule_selected.
"""
import ast
import subprocess
import sys
from pathlib import Path

import pytest

from analyzer.scanner import PLPlusScanner
from rubricator_prompts import RubricatorPrompts

ROOT = Path(__file__).resolve().parent.parent.parent
RUBRICATOR = ROOT / "DATA" / "Рубрикатор v5"
GEN = ROOT / "tools" / "gen_test_plp.py"
SCANNER_PY = ROOT / "SRC" / "analyzer" / "scanner.py"

RULES_CSV = (
    "plpcheck.BAD_PREFIX,plpcheck.CODE_IN_COMMENT,"
    "plpcheck.NOT_MENTIONED,plpcheck.WRONG_METHOD_SYNTAX"
)


@pytest.fixture(scope="module")
def rubricator():
    rp = RubricatorPrompts(RUBRICATOR)
    assert rp.load()
    return rp


@pytest.fixture
def plp(tmp_path):
    r = subprocess.run(
        [sys.executable, str(GEN), "-s", "PlpCheck",
         "-o", str(tmp_path), "--rules", RULES_CSV],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), timeout=60,
    )
    files = list(tmp_path.glob("*.plp"))
    assert files, f"gen failed:\n{r.stdout}\n{r.stderr}"
    return files[0]


def _scan(plp, selected_rules, rubricator, tmp_path):
    config = {
        "paths": {"source_dir": str(tmp_path), "results_dir": str(tmp_path)},
        "scan": {"file_pattern": "**/*.plp", "exclude_patterns": []},
    }
    scanner = PLPlusScanner(config, selected_rules, rubricator)
    scanner.scan_file(plp)
    return scanner


# ---------- 7: selected=['plpcheck.BAD_PREFIX'] narrows multiline set ----------
def test_selected_bad_prefix_only(plp, rubricator, tmp_path):
    sc = _scan(plp, ["plpcheck.BAD_PREFIX"], rubricator, tmp_path)
    types = {i.issue_type for i in sc.issues}
    for forbidden in (
        "plpcheck.CODE_IN_COMMENT",
        "plpcheck.NOT_MENTIONED",
        "plpcheck.WRONG_METHOD_SYNTAX",
    ):
        assert forbidden not in types, (
            f"DS 154: selected=['plpcheck.BAD_PREFIX'] must not include "
            f"{forbidden}; got {types}"
        )


# ---------- 8 (AST): each _check_plp_* call is guarded by _is_rule_selected ----------
PLP_GUARD_MAP = {
    "_check_plp_bad_prefix": "plpcheck.BAD_PREFIX",
    "_check_plp_not_mentioned": "plpcheck.NOT_MENTIONED",
    "_check_plp_prefix_type_in_var_name": "plpcheck.PREFIX_TYPE_IN_VAR_NAME",
    "_check_plp_wrong_method_syntax": "plpcheck.WRONG_METHOD_SYNTAX",
    "_check_plp_code_in_comment": "plpcheck.CODE_IN_COMMENT",
}


def test_multiline_calls_guarded_by_is_rule_selected():
    tree = ast.parse(SCANNER_PY.read_text(encoding="utf-8"))

    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        cond = node.test
        if not (isinstance(cond, ast.Call) and isinstance(cond.func, ast.Attribute)):
            continue
        if cond.func.attr != "_is_rule_selected":
            continue
        if not cond.args or not isinstance(cond.args[0], ast.Constant):
            continue
        rule = cond.args[0].value
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                if sub.func.attr in PLP_GUARD_MAP:
                    found[sub.func.attr] = rule

    missing = [fn for fn in PLP_GUARD_MAP if fn not in found]
    assert not missing, f"unguarded _check_plp_* calls: {missing}"

    for fn, expected_rule in PLP_GUARD_MAP.items():
        assert found[fn] == expected_rule, (
            f"{fn} guarded by {found[fn]}, expected {expected_rule}"
        )