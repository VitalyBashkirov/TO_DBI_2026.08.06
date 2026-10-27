# -*- coding: utf-8 -*-
from pathlib import Path
import sys

SC = Path(r"F:\TO_DBI\SRC\analyzer\scanner.py")
BK = Path(r"F:\TO_DBI\SRC\analyzer\scanner.py.ds70_01bak")

raw = SC.read_bytes()
has_bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
lines = text.split(chr(10))

def_idx = None
for i, ln in enumerate(lines):
    if "def _check_plp_suboptimal_wrownum" in ln:
        def_idx = i
        break
if def_idx is None:
    print("[patch] DEF NOT FOUND")
    sys.exit(2)
print(f"[patch] def at line {def_idx+1}")

doc_idx = None
for j in range(def_idx + 1, min(def_idx + 10, len(lines))):
    s = lines[j].lstrip()
    if s.startswith(chr(34)*3) and not s.startswith("r" + chr(34)*3) and not s.startswith("R" + chr(34)*3):
        doc_idx = j
        break
if doc_idx is None:
    print("[patch] DOCSTRING NOT FOUND")
    sys.exit(3)
orig = lines[doc_idx]
print(f"[patch] doc line {doc_idx+1}: {orig!r}")

lead = orig[:len(orig) - len(orig.lstrip())]
rest = orig[len(lead):]
if not rest.startswith(chr(34)*3):
    print("[patch] unexpected doc line")
    sys.exit(4)
new = lead + "r" + rest
lines[doc_idx] = new
print(f"[patch] new line {doc_idx+1}: {new!r}")

# проверка: ровно одна замена
changed = sum(1 for a, b in zip(text.split(chr(10)), lines) if a != b)
print(f"[patch] changed lines = {changed}")
if changed != 1:
    print("[patch] ABORT: expected exactly 1 change")
    sys.exit(5)

new_text = chr(10).join(lines)
new_bytes = new_text.encode("utf-8")
if has_bom:
    new_bytes = b"\xef\xbb\xbf" + new_bytes

if not BK.exists():
    BK.write_bytes(raw)
    print(f"[patch] backup: {BK.name} ({len(raw)} bytes)")
else:
    print(f"[patch] backup exists: {BK.name}")

SC.write_bytes(new_bytes)
print(f"[patch] wrote {SC.name} ({len(new_bytes)} bytes, bom={has_bom})")
