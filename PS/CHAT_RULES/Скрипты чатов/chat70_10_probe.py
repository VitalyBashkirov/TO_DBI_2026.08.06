# -*- coding: utf-8 -*-
from pathlib import Path
import sys, re, json

SRC = Path(r"F:\TO_DBI\SRC")
sys.path.insert(0, str(SRC))

from analyzer.scanner import PLPlusScanner
from rubricator_prompts import RubricatorPrompts

Q = chr(34)
RUB_DIR = Path(r"F:\TO_DBI\DATA\Рубрикатор v5")
RUB_JSON = RUB_DIR / "4.RUBRICATOR_PROMPT v5.json"
FILES = [
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\DEPN\PSH_ED_PRC_SCHM.plp"),
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\PL_US\PSH_PS_DEL.plp"),
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\RKO\PSH_VK_UNK_INP.plp"),
]

# --- 1. Полный текст PSH_PS_DEL.plp ---
psd = FILES[1]
print("=" * 78)
print("1. PSH_PS_DEL.plp FULL")
lines = psd.read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(lines, 1):
    print(str(i).rjust(4) + ": " + ln)

# --- 2. Правило EXIST_ALL_OR_COLLECTIONS в JSON рубрикатора ---
print("=" * 78)
print("2. EXIST_ALL_OR_COLLECTIONS in rubricator JSON")
data = json.loads(RUB_JSON.read_text(encoding="utf-8"))
print("top keys = " + str(list(data.keys()) if isinstance(data, dict) else type(data)))

def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, path + "/" + str(k))
    elif isinstance(obj, list):
        for j, v in enumerate(obj):
            walk(v, path + "[" + str(j) + "]")
    else:
        s = str(obj)
        if "EXIST_ALL_OR_COLLECTIONS" in s:
            print("  HIT at " + path + " = " + s[:300])
walk(data)

# --- 3. grep EXIST_ALL_OR_COLLECTIONS в scanner.py ---
print("=" * 78)
print("3. EXIST_ALL_OR_COLLECTIONS in scanner.py")
sc = Path(r"F:\TO_DBI\SRC\analyzer\scanner.py")
slines = sc.read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(slines, 1):
    if "EXIST_ALL_OR_COLLECTIONS" in ln or "exist_all" in ln.lower() or "check_plp_exist" in ln.lower():
        print(str(i).rjust(5) + ": " + ln)

print("=" * 78)
print("4. per-file issues by rule (selected=[plpcheck.])")
cfg = {
    "paths": {"source_dir": r"F:\TO_DBI\PATCH_IN", "results_dir": r"F:\TO_DBI\PATCH_CALC"},
    "scan": {"file_pattern": "**/*.plp", "exclude_patterns": []},
}
rp = RubricatorPrompts(RUB_DIR)
assert rp.load(), "рубрикатор не загрузился"
scanner = PLPlusScanner(cfg, ["plpcheck."], rp)

def rule(it):
    if isinstance(it, dict):
        return it.get("rule") or it.get("issue_type") or it.get("rule_id") or it.get("code")
    for a in ("rule", "issue_type", "rule_id", "code"):
        v = getattr(it, a, None)
        if v:
            return v
    return None

for f in FILES:
    if not f.exists():
        continue
    scanner.scan_file(f)
    per = {}
    for it in scanner.issues:
        r = rule(it)
        per[r] = per.get(r, 0) + 1
    print("--- " + f.name + " : issues=" + str(len(scanner.issues)))
    for r in sorted(per):
        print("    " + str(r) + " x" + str(per[r]))
    if "plpcheck.EXIST_ALL_OR_COLLECTIONS" in per:
        print("    !! EXIST_ALL_OR_COLLECTIONS FOUND on " + f.name)
    else:
        print("    -- EXIST_ALL_OR_COLLECTIONS NOT FOUND on " + f.name)
    scanner.issues.clear()

# --- 5. Если правило в JSON — прогнать его regex по PSH_PS_DEL.plp ---
print("=" * 78)
print("5. Try to locate rule pattern in JSON for PSH_PS_DEL.plp")
def find_rule(obj, code):
    if isinstance(obj, dict):
        if code in (obj.get("code"), obj.get("id"), obj.get("name"), obj.get("rule")):
            return obj
        for v in obj.values():
            r = find_rule(v, code)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_rule(v, code)
            if r:
                return r
    return None

rule_obj = find_rule(data, "plpcheck.EXIST_ALL_OR_COLLECTIONS")
if rule_obj is None:
    print("  rule object by exact name NOT found (maybe keyed differently)")
else:
    print("  rule keys = " + str(list(rule_obj.keys())))
    for k, v in rule_obj.items():
        s = str(v)
        if len(s) > 400:
            s = s[:400] + "..."
        print("    " + k + " = " + s)
    pat = rule_obj.get("pattern") or rule_obj.get("regex") or rule_obj.get("regexp")
    if pat:
        print("  --- compile+find on PSH_PS_DEL.plp ---")
        try:
            cre = re.compile(pat, re.IGNORECASE | re.MULTILINE)
            text = psd.read_text(encoding="utf-8")
            hits = list(cre.finditer(text))
            print("  hits = " + str(len(hits)))
            for m in hits[:5]:
                print("    match at " + str(m.start()) + " : " + repr(m.group(0)[:160]))
        except Exception as e:
            print("  regex error: " + str(e))
