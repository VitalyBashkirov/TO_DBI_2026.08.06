# -*- coding: utf-8 -*-
from pathlib import Path
import sys, re

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
ML_RULES = {
    "plpcheck.BAD_PREFIX",
    "plpcheck.NOT_MENTIONED",
    "plpcheck.PREFIX_TYPE_IN_VAR_NAME",
    "plpcheck.WRONG_METHOD_SYNTAX",
    "plpcheck.CODE_IN_COMMENT",
    "plpcheck.SUBOPTIMAL_QUERY_WROWNUM",
}

cfg = {
    "paths": {"source_dir": r"F:\TO_DBI\PATCH_IN", "results_dir": r"F:\TO_DBI\PATCH_CALC"},
    "scan": {"file_pattern": "**/*.plp", "exclude_patterns": []},
}

def make():
    rp = RubricatorPrompts(RUB)
    assert rp.load(), "рубрикатор не загрузился"
    return PLPlusScanner(cfg, ["plpcheck."], rp)

# Правильные регэкспы (одинарные бэкслеши в raw-строках)
RE_FUNC_OLD = re.compile(r"^\s*function\s+(\w+)\s*\(", re.IGNORECASE)
RE_METHOD   = re.compile(r"^\s*method\s+(\w+)\s+is\b", re.IGNORECASE)
RE_PUBLIC   = re.compile(r"^\s*public\s+(\w+)\s*\[", re.IGNORECASE)
RE_PARAM_IN = re.compile(r"^\s*(\w+)\s+in\s*\[", re.IGNORECASE)
RE_VAR_DECL = re.compile(r"^\s*(\w+)\s+(number|ref|const|string|boolean|date)\b", re.IGNORECASE)

def classify(lines, name, decl_line):
    pat = re.compile(r"\b" + re.escape(name) + r"\b")
    hits = []
    for i, line in enumerate(lines, 1):
        if i == decl_line:
            continue
        if pat.search(line):
            hits.append((i, line.strip()))
    return hits

for f in FILES:
    print("=" * 78)
    print(f"FILE: {f}")
    if not f.exists():
        print("  MISSING")
        continue
    lines = f.read_text(encoding="utf-8").splitlines()
    print(f"  lines={len(lines)}")

    print("--- 1. первые 80 строк ---")
    for i, ln in enumerate(lines[:80], 1):
        print(f"{i:5}: {ln}")

    sc = make()
    sc.lines = lines

    print("--- 2. _plp_iter_declarations (как в scanner.py) ---")
    decls = list(sc._plp_iter_declarations(lines))
    print(f"  declarations count = {len(decls)}")
    for d in decls:
        print(f"    {d!r}")

    print("--- 3. old function regex ^\\s*function\\s+(\\w+)\\s*\\( ---")
    old_funcs = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("--"):
            continue
        m = RE_FUNC_OLD.match(line)
        if m:
            old_funcs.append((i, m.group(1)))
    print(f"  old funcs = {old_funcs}")

    print("--- 4. Расширенные кандидаты объявлений ---")
    ext = []  # (line, kind, name)
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("--") or s.startswith("/*") or s.startswith("*") or s.startswith("*/"):
            continue
        m = RE_METHOD.match(line)
        if m:
            ext.append((i, "method", m.group(1))); continue
        m = RE_PUBLIC.match(line)
        if m:
            ext.append((i, "public", m.group(1))); continue
        m = RE_PARAM_IN.match(line)
        if m:
            ext.append((i, "param_in", m.group(1))); continue
        m = RE_VAR_DECL.match(line)
        if m and not s.startswith("--"):
            ext.append((i, "var_decl", m.group(1))); continue
    for (i, kind, name) in ext:
        print(f"    {kind:9} line={i:4} name={name!r}")

    print("--- 5. used? по расширенному набору ---")
    for (i, kind, name) in ext:
        hits = classify(lines, name, i)
        used = bool(hits)
        print(f"    {kind:9} {name!r} decl_line={i} used={used} hits={len(hits)}")
        for (hi, hs) in hits[:3]:
            print(f"        hit {hi:4}: {hs[:110]}")

    print("--- 6. _check_plp_not_mentioned напрямую ---")
    nm = sc._check_plp_not_mentioned(lines)
    print(f"  issues = {len(nm)}")
    for it in nm[:20]:
        print(f"    {it!r}")

# --- сводный _scan_all по всем трём файлам ---
print("=" * 78)
print("SUMMARY _scan_all([plpcheck.]) по трём файлам")
sc = make()
def rule(it):
    if isinstance(it, dict):
        return it.get("rule") or it.get("issue_type") or it.get("rule_id") or it.get("code")
    for a in ("rule", "issue_type", "rule_id", "code"):
        v = getattr(it, a, None)
        if v:
            return v
    return None
all_issues = []
for f in FILES:
    if not f.exists():
        continue
    sc.scan_file(f)
    all_issues.extend(sc.issues)
    sc.issues.clear()
found = sorted({rule(it) for it in all_issues if rule(it)})
print(f"  total issues = {len(all_issues)}")
for r in found:
    print(f"    {r}")
print(f"  ML_RULES found = {sorted(set(found) & ML_RULES)}")
