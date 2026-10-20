# -*- coding: utf-8 -*-
"""DS_153d: тесты PLPlusScanner — фактическое поведение фильтрации (п.4).

Фиксирует ТЕКУЩЕЕ поведение сканера:
  - selected_rules=[] -> fallback «все правила» (issue есть);
  - selected_rules=[<правило>] -> скан работает (issue есть);
  - multiline-правила (BAD_PREFIX, NOT_MENTIONED, WRONG_METHOD_SYNTAX,
    CODE_IN_COMMENT) выполняются ВСЕГДА для .plp;
  - известное ограничение (баг) _is_rule_selected: selected_rules=
    [<plpcheck.X>] НЕ сужает набор plpcheck-правил (сравнение по префиксу
    "plpcheck", а не по полному коду);
  - get_issues_by_file() -> dict по файлам.

.plp генерируется через tools/gen_test_plp.py (DS_147a) в tmp_path.
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
RULES_CSV = "plpcheck.BAD_PREFIX,plpcheck.CODE_IN_COMMENT"


@pytest.fixture(scope="module")
def rubricator():
    rp = RubricatorPrompts(RUBRICATOR)
    assert rp.load(), "рубрикатор не загружен"
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
    assert files, f"gen_test_plp не создал .plp:\n{r.stdout}\n{r.stderr}"
    return files[0]


def _scan(plp, selected_rules, rubricator, tmp_path):
    config = {
        "paths": {"source_dir": str(tmp_path), "results_dir": str(tmp_path)},
        "scan": {"file_pattern": "**/*.plp", "exclude_patterns": []},
    }
    scanner = PLPlusScanner(config, selected_rules, rubricator)
    scanner.scan_file(plp)
    return scanner


# ---------- 1: selected_rules=[] -> issue есть (fallback) ----------
def test_scanner_returns_issues_when_empty(plp, rubricator, tmp_path):
    sc = _scan(plp, [], rubricator, tmp_path)
    assert len(sc.issues) > 0, \
        "selected_rules=[] должен вернуть все правила (fallback)"


# ---------- 2: selected_rules=[<rule>] -> скан работает ----------
def test_scanner_returns_issues_with_selected_rule(plp, rubricator, tmp_path):
    sc = _scan(plp, ["plpcheck.BAD_PREFIX"], rubricator, tmp_path)
    assert len(sc.issues) > 0, \
        "сканер должен вернуть issue и при выбранном правиле"


# ---------- 3: multiline-правила НЕ фильтруются по selected_rules ----------
def test_multiline_not_filtered_by_selected_rules(plp, rubricator, tmp_path):
    sc = _scan(plp, ["plpcheck.CODE_IN_COMMENT"], rubricator, tmp_path)
    types = {i.issue_type for i in sc.issues}
    assert "plpcheck.CODE_IN_COMMENT" in types, \
        "CODE_IN_COMMENT должен быть найден (multiline, .plp)"
    others = types - {"plpcheck.CODE_IN_COMMENT"}
    assert others, \
        "multiline-правила не фильтруются: должны быть и другие issue"


# ---------- 4: get_issues_by_file -> dict по файлам ----------
def test_get_issues_by_file_returns_dict(plp, rubricator, tmp_path):
    sc = _scan(plp, [], rubricator, tmp_path)
    by_file = sc.get_issues_by_file()
    assert len(by_file) == 1, "должен быть ровно 1 файл"
    issues = list(by_file.values())[0]
    assert issues, "get_issues_by_file должен вернуть непустой список"
    assert all(i.issue_type for i in issues), "у каждой issue есть rule_code"


# ---------- 5 (AST): _is_rule_selected вызывается в scan_file ----------
def test_is_rule_selected_called_in_scan_file():
    tree = ast.parse(SCANNER_PY.read_text(encoding="utf-8"))
    callers = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Attribute) and sub.attr == "_is_rule_selected":
                callers.add(node.name)
    assert "scan_file" in callers, \
        "_is_rule_selected должен вызываться в scan_file (пост-фильтрация)"


# ---------- 6: известное ограничение — plpcheck.* не сужаются ----------
def test_selected_rule_does_not_narrow_plpcheck(plp, rubricator, tmp_path):
    sc = _scan(plp, ["plpcheck.BAD_PREFIX"], rubricator, tmp_path)
    types = {i.issue_type for i in sc.issues}
    assert "plpcheck.CODE_IN_COMMENT" in types, \
        "известное ограничение: plpcheck.* не сужаются по selected_rules"

