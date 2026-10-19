# -*- coding: utf-8 -*-
"""DS_144d-b: диагностика дыр в PLPCHECK_RULE_TO_CATEGORY (8 DEV.* subcategory).

Скрипт лежит в SRC/tests/, поэтому ROOT = parents[2].
"""
import importlib.util
import json
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
SCANNER = ROOT / 'SRC' / 'analyzer' / 'scanner.py'
V5 = ROOT / 'DATA' / 'Рубрикатор v5' / '4.RUBRICATOR_PROMPT v5.json'

sys.path.insert(0, str(ROOT / 'SRC'))
spec = importlib.util.spec_from_file_location('_scanner_diag', SCANNER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mapping = dict(mod.PLPCHECK_RULE_TO_CATEGORY)
sys.path.pop(0)

rules = json.loads(V5.read_text(encoding='utf-8'))['rules']
plp = {c: r for c, r in rules.items() if r.get('source') == 'plpcheck'}

by_sub = {}
for code, r in plp.items():
    sub = r.get('subcategory')
    if sub:
        by_sub.setdefault(sub, []).append(code)

holes = []
for sub, codes in sorted(by_sub.items()):
    aggs = {mapping.get(c, 'OTHER') for c in codes}
    if aggs == {'OTHER'}:
        holes.append((sub, codes))

print("=== holes: DEV.* subcategory, all rules in OTHER ===")
for sub, codes in holes:
    print(f"\n[{sub}] rules={len(codes)}")
    for c in sorted(codes):
        print(f"  {c}  -> {mapping.get(c, '<not in mapping>')}")
        print(f"      short_description: {plp[c].get('short_description', '')}")

print("\n=== distribution: aggregate -> count (all plpcheck) ===")
cnt = Counter(mapping.get(c, 'OTHER') for c in plp)
for agg, n in sorted(cnt.items()):
    print(f"  {agg} = {n}")