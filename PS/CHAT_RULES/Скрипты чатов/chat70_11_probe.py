# -*- coding: utf-8 -*-
from pathlib import Path
import sys, re, json

SRC = Path(r"F:\TO_DBI\SRC")
sys.path.insert(0, str(SRC))

from analyzer.scanner import PLPlusScanner
from rubricator_prompts import RubricatorPrompts

Q = chr(34)
RUB_DIR  = Path(r"F:\TO_DBI\DATA\Рубрикатор v5")
RUB_JSON = RUB_DIR / "4.RUBRICATOR_PROMPT v5.json"
FILES = [
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\DEPN\PSH_ED_PRC_SCHM.plp"),
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\PL_US\PSH_PS_DEL.plp"),
    Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\RKO\PSH_VK_UNK_INP.plp"),
]

data = json.loads(RUB_JSON.read_text(encoding="utf-8"))
rule = data["rules"]["plpcheck.EXIST_ALL_OR_COLLECTIONS"]
fs_pat = rule["regex_patterns"]["for_search"][0]["pattern"]
fi_pat = rule["regex_patterns"]["for_ignore"][0]["pattern"]
print("[rule] for_search  = " + fs_pat)
print("[rule] for_ignore  = " + fi_pat)

# --- 1. Где в PSH_ED_PRC_SCHM срабатывает EXIST_ALL_OR_COLLECTIONS:
# ищем по тексту оригинальный for_search, чтобы понять «эталонную» строку. ---
print("=" * 78)
print("1. for_search (original) hit lines across three files")
fs_re = re.compile(fs_pat, re.IGNORECASE | re.MULTILINE)
fi_re = re.compile(fi_pat, re.IGNORECASE | re.MULTILINE)
for f in FILES:
    if not f.exists():
        print("  MISSING " + str(f))
        continue
    text = f.read_text(encoding="utf-8")
    lines = text.splitlines()
    print("--- " + f.name)
    any_hit = False
    for i, ln in enumerate(lines, 1):
        for m in fs_re.finditer(ln):
            any_hit = True
            frag = ln[max(0, m.start()-10):m.end()+10]
            print("  L" + str(i) + " match=" + repr(m.group(0)) + "  frag=" + repr(frag))
    if not any_hit:
        print("  (no for_search hits)")

# --- 2. Как scanner.py применяет for_ignore: проверим текст рядом с def _check_plp_exist...
# (отдельного метода нет, но посмотрим, есть ли общий regex-движок, где вызываются for_search/for_ignore).
print("=" * 78)
print("2. grep for_search / for_ignore / regex_patterns in scanner.py")
sc = Path(r"F:\TO_DBI\SRC\analyzer\scanner.py")
slines = sc.read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(slines, 1):
    s = ln
    if ("for_search" in s) or ("for_ignore" in s) or ("regex_patterns" in s):
        print(str(i).rjust(5) + ": " + s)

# --- 3. Гипотеза: расширить for_search, чтобы ловить in this(idx).[B_PS] и in this.[...].
# Пробуем несколько вариантов. ---
print("=" * 78)
print("3. extended for_search candidates vs three files")
candidates = {
    "A_orig": r"in\s+::\[\w+\]\s*(?!all|collection)",
    "B_plus_this_dotdot": r"in\s+(?:::\[\w+\]|this(?:\(\w+\))?\.\[\w+\])\s*(?!all|collection)",
    "C_plus_this_dotdot_bracket": r"in\s+(?:::\[\w+\]|this(?:\(\w+\))?\.\[\w+\]|\[\w+\])\s*(?!all|collection)",
    "D_loose_in_collection": r"in\s+[^;\n]*\[[A-Za-z_#][\w#]*\]",
}
for name, pat in candidates.items():
    try:
        cre = re.compile(pat, re.IGNORECASE | re.MULTILINE)
    except Exception as e:
        print("  " + name + " : REGEX ERROR " + str(e))
        continue
    print("  -- " + name + " : " + pat)
    for f in FILES:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        hits = []
        for i, ln in enumerate(lines, 1):
            for m in cre.finditer(ln):
                hits.append((i, m.group(0)))
        if hits:
            print("     " + f.name + " : " + str(len(hits)) + " hits")
            for (i, g) in hits[:6]:
                print("       L" + str(i) + " : " + repr(g[:120]))
        else:
            print("     " + f.name + " : 0")

# --- 4. Поведение for_ignore (all|collection) при расширении:
#     в строке 18 нет all/collection, но for_ignore обычно применяется к найденному фрагменту,
#     а не к строке. Покажем, есть ли совпадения fi_re в найденном фрагменте. ---
print("=" * 78)
print("4. for_ignore (all|collection) presence in matched fragments (candidate B)")
cre = re.compile(candidates["B_plus_this_dotdot"], re.IGNORECASE | re.MULTILINE)
for f in FILES:
    if not f.exists():
        continue
    text = f.read_text(encoding="utf-8")
    for m in cre.finditer(text):
        frag = m.group(0)
        ign = bool(fi_re.search(frag))
        print("  " + f.name + " match=" + repr(frag[:80]) + "  for_ignore_in_frag=" + str(ign))
