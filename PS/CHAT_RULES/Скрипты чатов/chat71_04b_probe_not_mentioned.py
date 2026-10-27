# -*- coding: utf-8 -*-
import sys
from pathlib import Path

SRC = Path(r"F:\TO_DBI\SRC")
sys.path.insert(0, str(SRC))

from analyzer.scanner import PLPlusScanner
from rubricator_prompts import RubricatorPrompts

FIX = Path(r"F:\TO_DBI\SRC\tests\fixtures\ds71_in_type.plp")
RUB = Path(r"F:\TO_DBI\DATA\Рубрикатор v5")

def cfg():
    return {
        "paths": {"source_dir": r"F:\TO_DBI\PATCH_IN",
                  "results_dir": r"F:\TO_DBI\PATCH_CALC"},
        "scan": {"file_pattern": "**/*.plp", "exclude_patterns": []},
    }

def main():
    if not FIX.exists():
        print("FIX missing:", FIX); return
    rp = RubricatorPrompts(RUB)
    ok = rp.load()
    print("rubricator load=", ok)
    sc = PLPlusScanner(cfg(), {"plpcheck.NOT_MENTIONED"}, rp)
    lines = FIX.read_text(encoding="utf-8").splitlines()
    print("FIX lines=", len(lines))
    print("--- iter_declarations ---")
    for t in sc._plp_iter_declarations(lines):
        print("  ITER:", t)
    print("--- not_mentioned issues ---")
    issues = sc._check_plp_not_mentioned(lines)
    print("count=", len(issues))
    for it in issues:
        print("  ISSUE:", it)

if __name__ == "__main__":
    main()
