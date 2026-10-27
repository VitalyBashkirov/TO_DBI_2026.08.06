# -*- coding: utf-8 -*-
import re, os

FIX = r"F:\TO_DBI\SRC\tests\fixtures\ds71_in_type.plp"

CUR_DECL = re.compile(
    r"^\s*(\w+)\s+("
    r"integer|number|string|varchar2|date|boolean|timestamp|rowtype"
    r"|(?:ref\s*)?\[[\w\d_]+\]"
    r"|&[\w.]+"
    r")\s*(\(\s*\d+\s*\))?\s*(?::=|;)",
    re.IGNORECASE
)

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

def iter_decl(lines, rx):
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("--") or s.startswith("@") or s.lower().startswith(SKIP):
            continue
        m = rx.match(line)
        if m:
            yield i, m.group(1), m.group(2)

def kinds(lines):
    out = []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        for pat, kind in ((PUB_FUNC,"func"),(PUB_PROC,"proc"),(METHOD,"method"),(BMETHOD,"batch_method"),(GPROC,"proc"),(GFUNC,"func")):
            m = pat.match(line)
            if m:
                out.append((i, m.group(1), kind, s)); break
    return out

def main():
    if not os.path.exists(FIX):
        print("FIX NOT FOUND:", FIX); return
    with open(FIX, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    print("FIX lines=", len(lines))
    cur = list(iter_decl(lines, CUR_DECL))
    new = list(iter_decl(lines, NEW_DECL))
    kd  = kinds(lines)
    print("--- CUR decl (%d) ---" % len(cur))
    for t in cur: print("  CUR:", t)
    print("--- NEW decl (%d) ---" % len(new))
    for t in new: print("  NEW:", t)
    print("--- NEW kinds (%d) ---" % len(kd))
    for t in kd: print("  KIND:", t)
    # контроль: чего НЕ должно быть
    bad = [t for t in new if t[1] in ("Default_Mes",)]
    print("BAD (Default_Mes caught):", bad)

if __name__ == "__main__":
    main()
