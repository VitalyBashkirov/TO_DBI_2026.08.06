# -*- coding: utf-8 -*-
"""DS_186: _check_plp_suboptimal_wrownum должен ловить exit/return/raise/pragma error/message.error/app_error.

Проверка на трёх восстановленных .plp из PATCH_IN\\patch_suboptimal_test_3:
  PSH_ED_PRC_SCHM.plp  — 1 (exit, стр. 112)
  PSH_VK_UNK_INP.plp  — 2 (return стр. 15, pragma error стр. 48)
  PSH_PS_DEL.plp      — 0 (for v in collection, не select)
"""
import sys
from pathlib import Path
import pytest

SRC = Path(r"F:\\TO_DBI\\SRC")
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

RUB = Path(r"F:\\TO_DBI\\DATA\\Рубрикатор v5")
PATCH_IN = Path(r"F:\\TO_DBI\\PATCH_IN\\patch_suboptimal_test_3")
FILES = {
    "PSH_ED_PRC_SCHM.plp": PATCH_IN / "ENTITY" / "DEPN" / "PSH_ED_PRC_SCHM.plp",
    "PSH_VK_UNK_INP.plp": PATCH_IN / "ENTITY" / "RKO" / "PSH_VK_UNK_INP.plp",
    "PSH_PS_DEL.plp": PATCH_IN / "ENTITY" / "PL_US" / "PSH_PS_DEL.plp",
}


def _make_scanner():
    from analyzer.scanner import PLPlusScanner
    from rubricator_prompts import RubricatorPrompts
    rp = RubricatorPrompts(RUB)
    assert rp.load(), f"рубрикатор не загрузился: {RUB}"
    cfg = {
        "paths": {"source_dir": str(PATCH_IN)},
        "scan": {"exclude_patterns": []},
    }
    return PLPlusScanner(cfg, ["plpcheck.SUBOPTIMAL_QUERY_WROWNUM"], rp)


def test_ds186_wrownum_return_pragma():
    missing = [n for n, p in FILES.items() if not p.exists()]
    if missing:
        pytest.skip(f"PATCH_IN не восстановлен, нет: {missing}")

    scanner = _make_scanner()
    per = {}
    total = 0
    for name, path in FILES.items():
        issues = scanner.scan_file(path) or []
        only = [x for x in issues if "SUBOPTIMAL_QUERY_WROWNUM" in (getattr(x, "rubricator_code", "") or "").upper()]
        per[name] = len(only)
        total += len(only)

    assert per["PSH_ED_PRC_SCHM.plp"] == 1, f"SCHM: {per}"
    assert per["PSH_VK_UNK_INP.plp"] == 2, f"VK_UNK_INP: {per}"
    assert per["PSH_PS_DEL.plp"] == 0, f"PS_DEL: {per}"
    assert total == 3, f"итого {total}, per={per}"
