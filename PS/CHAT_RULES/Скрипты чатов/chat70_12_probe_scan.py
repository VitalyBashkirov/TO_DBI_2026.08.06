# -*- coding: utf-8 -*-
from pathlib import Path
import sys

SRC = Path(r"F:\TO_DBI\SRC")
sys.path.insert(0, str(SRC))
from analyzer.scanner import PLPlusScanner
from rubricator_prompts import RubricatorPrompts

RUB = Path(r"F:\TO_DBI\DATA\Рубрикатор v5")
FILES = [
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\DEPN\PSH_ED_PRC_SCHM.plp"),
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\PL_US\PSH_PS_DEL.plp"),
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\RKO\PSH_VK_UNK_INP.plp"),
]
cfg = {
    "paths": {"source_dir": r"F:\TO_DBI\PATCH_IN", "results_dir": r"F:\TO_DBI\PATCH_CALC"},
    "scan": {"file_pattern": "**/*.plp", "exclude_patterns": []},
}
rp = RubricatorPrompts(RUB)
assert rp.load(), "рубрикатор не загрузился"
sc = PLPlusScanner(cfg, ["plpcheck."], rp)
def rule(it):
    if isinstance(it, dict):
        return it.get("rule") or it.get("issue_type") or it.get("rule_id") or it.get("code")
    for a in ("rule", "issue_type", "rule_id", "code"):
        v = getattr(it, a, None)
        if v:
            return v
    return None
for f in FILES:
    sc.scan_file(f)
    n = 0
    for it in sc.issues:
        if rule(it) == "plpcheck.EXIST_ALL_OR_COLLECTIONS":
            n += 1
    print(f.name + " : EXIST_ALL_OR_COLLECTIONS x" + str(n) + " / total issues=" + str(len(sc.issues)))
    sc.issues.clear()
