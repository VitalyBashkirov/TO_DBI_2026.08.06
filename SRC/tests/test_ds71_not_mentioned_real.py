# -*- coding: utf-8 -*-
"""DS_71: NOT_MENTIONED на реальных неиспользуемых объявлениях.

Проверяет расширение _plp_iter_declarations (форма NAME in [TYPE]) и
_check_plp_not_mentioned (public function/procedure, procedure, method,
batch method) на собственной фикстуре tests/fixtures/ds71_in_type.plp.
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

from analyzer.scanner import PLPlusScanner  # noqa: E402
from rubricator_prompts import RubricatorPrompts  # noqa: E402

RUB = Path(r"F:\TO_DBI\DATA\Рубрикатор v5")
FIX = Path(__file__).resolve().parent / "fixtures" / "ds71_in_type.plp"


def _cfg():
    return {
        "paths": {"source_dir": r"F:\TO_DBI\PATCH_IN",
                  "results_dir": r"F:\TO_DBI\PATCH_CALC"},
        "scan": {"file_pattern": "**/*.plp", "exclude_patterns": []},
    }


def _make():
    rp = RubricatorPrompts(RUB)
    assert rp.load(), "рубрикатор не загрузился"
    return PLPlusScanner(_cfg(), {"plpcheck.NOT_MENTIONED"}, rp)


def _name_from_issue(it):
    _, msg, _ = it
    m = re.search(r"(?:Функция|Процедура|Метод|Батч-метод|Переменная)\s+(\w+)", msg)
    assert m, f"не удалось извлечь имя из сообщения: {msg!r}"
    return m.group(1)


def test_iter_declarations_in_type():
    """Форма NAME in [TYPE] теперь распознаётся итератором."""
    sc = _make()
    lines = FIX.read_text(encoding="utf-8").splitlines()
    decls = list(sc._plp_iter_declarations(lines))
    names = {d[1] for d in decls}
    assert "v_unused_in" in names, f"in [TYPE] не распознан; декларации: {decls}"
    assert "r_ref" in names
    for d in decls:
        if d[1] in ("v_unused_in", "r_ref"):
            assert d[2] == "in", f"{d[1]}: type_str={d[2]!r}"
    # базовые типы не должны превращаться в in
    for d in decls:
        if d[1] in ("v_local", "v_m", "v_b", "v_used"):
            assert d[2] != "in", f"{d[1]}: type_str={d[2]!r} — integer превратился в in"


def test_not_mentioned_real_issues():
    sc = _make()
    lines = FIX.read_text(encoding="utf-8").splitlines()
    issues = sc._check_plp_not_mentioned(lines)
    names = [_name_from_issue(it) for it in issues]
    name_set = set(names)

    expected = {
        "v_tmp", "v_m", "v_b", "r_ref", "v_unused_in",
        "unused_pub_func", "unused_pub_proc",
        "unused_method", "unused_batch_method",
    }
    assert name_set == expected, (
        f"ожидалось ровно {sorted(expected)}; получено {sorted(name_set)}"
    )
    assert len(issues) == 9

    # used-контроль
    assert "v_local" not in name_set
    assert "v_used" not in name_set
    # Default_Mes — не объявление
    assert "Default_Mes" not in name_set

    # вид сообщения по kind: func/proc/method/batch_method — свои префиксы
    expected_prefix = {
        "unused_pub_func":     "Функция ",
        "unused_pub_proc":     "Процедура ",
        "unused_method":       "Метод ",
        "unused_batch_method": "Батч-метод ",
    }
    default_prefix = "Переменная "
    for it in issues:
        name = _name_from_issue(it)
        msg = it[1]
        pref = expected_prefix.get(name, default_prefix)
        assert msg.startswith(pref), f"{name}: {msg!r} не начинается с {pref!r}"


def test_not_mentioned_does_not_fire_on_fixture_without_unused():
    """На пустом/используемом коде issues не появляются."""
    sc = _make()
    lines = [
        "class X"
        "  execute"
        "    v_a integer;"
        "    v_a := 1;"
        "  end;"
    ]
    issues = sc._check_plp_not_mentioned(lines)
    assert issues == []
