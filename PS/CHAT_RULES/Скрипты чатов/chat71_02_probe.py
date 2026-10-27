# -*- coding: utf-8 -*-
import re, os, sys

FIXTURES = [
    r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\DEPN\PSH_ED_PRC_SCHM.plp",
    r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\PL_US\PSH_PS_DEL.plp",
    r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\RKO\PSH_VK_UNK_INP.plp",
]
ACFIN = [
    r"F:\TO_DBI\DATA\CFT Platform IDE Documentation\ide_dbi_project\20260922\src\ENTITY\AC_FIN\PSH_ACC_TURN_LS.plp",
    r"F:\TO_DBI\DATA\CFT Platform IDE Documentation\ide_dbi_project\20260922\src\ENTITY\AC_FIN\PSH_AFTER_AC_FAM.plp",
    r"F:\TO_DBI\DATA\CFT Platform IDE Documentation\ide_dbi_project\20260922\src\ENTITY\AC_FIN\PSH_LIB.plp",
]

# текущий decl_re из scanner.py:941-948 (копия)
CUR_DECL = re.compile(
    r"^\s*(\w+)\s+("
    r"integer|number|string|varchar2|date|boolean|timestamp|rowtype"
    r"|(?:ref\s*)?\[[\w\d_]+\]"
    r"|&[\w.]+"
    r")\s*(\(\s*\d+\s*\))?\s*(?::=|;)",
    re.IGNORECASE
)

# новый decl_re: + NAME in [TYPE]
NEW_DECL = re.compile(
    r"^\s*(\w+)\s+("
    r"integer|number|string|varchar2|date|boolean|timestamp|rowtype"
    r"|(?:ref\s*)?\[[\w\d_]+\]"
    r"|in\s+\[[\w\d_]+\]"
    r"|&[\w.]+"
    r")\s*(\(\s*\d+\s*\))?\s*(?::=|;)",
    re.IGNORECASE
)

PUB_FUNC = re.compile(r"^\s*public\s+function\s+(\w+)\s*\(", re.I)
PUB_PROC = re.compile(r"^\s*public\s+procedure\s+(\w+)\s*\(", re.I)
METHOD   = re.compile(r"^\s*method\s+(\w+)\s+is\b", re.I)
BMETHOD  = re.compile(r"^\s*batch\s+method\s+(\w+)\s+is\b", re.I)
GPROC    = re.compile(r"^\s*procedure\s+(\w+)\s*\(", re.I)
GFUNC    = re.compile(r"^\s*function\s+(\w+)\s*\(", re.I)

SKIP = ("class", "method", "execute", "begin", "pragma", "function", "end", "if", "return")

def iter_cur(lines):
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("--") or s.startswith("@") or s.lower().startswith(SKIP):
            continue
        m = CUR_DECL.match(line)
        if m:
            yield i, m.group(1), m.group(2)

def iter_new(lines):
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("--") or s.startswith("@") or s.lower().startswith(SKIP):
            continue
        m = NEW_DECL.match(line)
        if m:
            yield i, m.group(1), m.group(2)

def scan_new_kinds(lines):
    out = []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        for pat, kind in ((PUB_FUNC,"func"), (PUB_PROC,"proc"), (METHOD,"method"), (BMETHOD,"batch_method"), (GPROC,"proc"), (GFUNC,"func")):
            m = pat.match(line)
            if m:
                out.append((i, m.group(1), kind, s))
                break
    return out

def run_file(fp):
    print("=" * 60)
    print("FILE:", fp)
    if not os.path.exists(fp):
        print("  NOT FOUND"); return
    with open(fp, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    print("  lines=", len(lines))
    cur = list(iter_cur(lines))
    new = list(iter_new(lines))
    kinds = scan_new_kinds(lines)
    print("  CUR decl count:", len(cur))
    for n in cur: print("    CUR:", n)
    print("  NEW decl count:", len(new))
    for n in new: print("    NEW:", n)
    print("  NEW kinds count:", len(kinds))
    for k in kinds: print("    KIND:", k)

def main():
    print("=== patch_suboptimal_test_3 fixtures ===")
    for fp in FIXTURES: run_file(fp)
    print()
    print("=== AC_FIN sample (3 files) ===")
    for fp in ACFIN: run_file(fp)
    print("DONE")

if __name__ == "__main__":
    main()
