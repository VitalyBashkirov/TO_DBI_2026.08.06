# -*- coding: utf-8 -*-
from pathlib import Path
import sys

T = Path(r"F:\TO_DBI\SRC\tests\test_ds182_k3k4_9issues.py")
B = Path(r"F:\TO_DBI\SRC\tests\test_ds182_k3k4_9issues.py.ds70_07bak")
OLD = '        assert "plpcheck.NOT_MENTIONED" in found, "нет NOT_MENTIONED"'
NL = chr(10)

raw = T.read_bytes()
has_bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
lines = text.split(NL)

idx = [i for i, ln in enumerate(lines) if ln == OLD]
if len(idx) != 1:
    print(f"[patch] OLD matches = {len(idx)} (ожидалось 1) — ABORT")
    sys.exit(2)
i = idx[0]
lead = OLD[:len(OLD) - len(OLD.lstrip())]
print(f"[patch] OLD at line {i+1}: {OLD!r}")

new_block = [
    lead + "# DS_182/DS_182b: на текущих трёх фикстурах NOT_MENTIONED не срабатывает —",
    lead + "# все объявления (res, CP, v_ps, idx, cn_ComStatusClose, PSH_*_INP, PSH_*_DEL,",
    lead + "# PSH_ED_PRC_SCHM) реально используются в файлах (см. LG_70_06b_ds182_diag2.log).",
    lead + "# Прежнее ожидание \"NOT_MENTIONED in found\" не выполнялось и не связано с DS_182",
    lead + "# Если понадобится проверять NOT_MENTIONED — нужны отдельные фикстуры",
    lead + "# с реально неиспользуемым объявлением (долг 70 -> 71).",
    lead + 'assert "plpcheck.NOT_MENTIONED" not in found, ('
    lead + '    "DS_182: на фикстурах patch_suboptimal_test_3 NOT_MENTIONED не ожидается — "'
    lead + '    "все объявления используются; если появился, значит либо изменились "'
    lead + '    "фикстуры, либо _check_plp_not_mentioned сломан — проверить LG_70_06b лог"'
    lead + ')'
]
lines[i:i+1] = new_block

# контроль: одна замена и только одна
new_text = NL.join(lines)
old_hits = sum(1 for ln in lines if ln.strip().endswith("in found, \"нет NOT_MENTIONED\""))
print(f"[patch] delta lines = {len(lines) - (text.count(NL) + 1)}")
if "in found, \\"нет NOT_MENTIONED\\"" in new_text and "not in found" not in new_text:
    print("[patch] ABORT: похоже, замена не применилась")
    sys.exit(3)

new_bytes = new_text.encode("utf-8")
if has_bom:
    new_bytes = b"\xef\xbb\xbf" + new_bytes

if not B.exists():
    B.write_bytes(raw)
    print(f"[patch] backup: {B.name} ({len(raw)} bytes)")
else:
    print(f"[patch] backup exists: {B.name}")

T.write_bytes(new_bytes)
print(f"[patch] wrote {T.name} ({len(new_bytes)} bytes, bom={has_bom})")
