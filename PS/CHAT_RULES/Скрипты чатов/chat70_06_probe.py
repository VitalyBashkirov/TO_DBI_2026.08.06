# -*- coding: utf-8 -*-
from pathlib import Path
import sys, re

SRC = Path(r"F:\TO_DBI\SRC")
sys.path.insert(0, str(SRC))

from analyzer.scanner import PLPlusScanner
from rubricator_prompts import RubricatorPrompts

PLP = Path(r"F:\TO_DBI\PATCH_IN\patch_suboptimal_test_3\ENTITY\DEPN\PSH_ED_PRC_SCHM.plp")
RUB = Path(r"F:\TO_DBI\DATA\Рубрикатор v5")

lines = PLP.read_text(encoding="utf-8").splitlines()
print(f"[probe] file={PLP.name} lines={len(lines)}")

print("--- 1. Первые 80 строк файла ---")
for i, ln in enumerate(lines[:80], 1):
    print(f"{i:5}: {ln}")

cfg = {
    "paths": {"source_dir": r"F:\\TO_DBI\\PATCH_IN", "results_dir": r"F:\\TO_DBI\\PATCH_CALC"},
    "scan": {"file_pattern": "**/*.plp", "exclude_patterns": []},
}
rp = RubricatorPrompts(RUB)
assert rp.load(), "рубрикатор не загрузился"
sc = PLPlusScanner(cfg, ["plpcheck."], rp)
sc.lines = lines

print("--- 2. _plp_iter_declarations ---")
decls = list(sc._plp_iter_declarations(lines))
print(f"[probe] declarations count = {len(decls)}")
for d in decls:
    print(f"  decl={d!r}")

print("--- 3. функции по regex ^\\s*function\\s+(\\w+)\\s*\\( ---")
func_re = re.compile(r"^\\s*function\\s+(\\w+)\\s*\\(", re.IGNORECASE)
funcs = []
for i, line in enumerate(lines, 1):
    s = line.strip()
    if s.startswith("--"):
        continue
    m = func_re.match(line)
    if m:
        funcs.append((i, m.group(1), s))
print(f"[probe] functions count = {len(funcs)}")
for f in funcs:
    print(f"  func={f!r}")

print("--- 4. Почему used=True: упоминания каждого объявления ---")
declared = {}
for line_num, var_name, type_str, is_exec in decls:
    declared[var_name] = (line_num, "var")
for i, line in enumerate(lines, 1):
    s = line.strip()
    if s.startswith("--"):
        continue
    m = func_re.match(line)
    if m:
        declared[m.group(1)] = (i, "func")
print(f"[probe] total declared (var+func) = {len(declared)}")
for name, (dl, kind) in declared.items():
    pat = re.compile(rf"\\b{re.escape(name)}\\b")
    hits = []
    for i, line in enumerate(lines, 1):
        if i == dl:
            continue
        if pat.search(line):
            hits.append((i, line.strip()))
    used = bool(hits)
    print(f"  {kind} {name!r} decl_line={dl} used={used} hits={len(hits)}")
    for (i, s) in hits[:3]:
        print(f"      hit line {i}: {s[:120]}")

print("--- 5. _check_plp_not_mentioned напрямую ---")
nm = sc._check_plp_not_mentioned(lines)
print(f"[probe] not_mentioned issues = {len(nm)}")
for it in nm[:20]:
    print(f"  {it!r}")
