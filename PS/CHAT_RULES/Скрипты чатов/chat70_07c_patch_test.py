# -*- coding: utf-8 -*-
from pathlib import Path
import sys

T = Path(r"F:\TO_DBI\SRC\tests\test_ds182_k3k4_9issues.py")
B = Path(r"F:\TO_DBI\SRC\tests\test_ds182_k3k4_9issues.py.ds70_07bak")
Q = chr(34)
NL = chr(10)

NEEDLE_IN = "assert " + Q + "plpcheck.NOT_MENTIONED" + Q + " in found"
NEEDLE_NOT = "assert " + Q + "plpcheck.NOT_MENTIONED" + Q + " not in found"

raw = T.read_bytes()
has_bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")
lines = text.split(NL)

idx = [i for i, ln in enumerate(lines) if NEEDLE_IN in ln and NEEDLE_NOT not in ln]
if len(idx) != 1:
    print("[patch] NEEDLE matches = " + str(len(idx)) + " (ожидалось 1) — ABORT")
    for i in idx:
        print("[patch]   hit line " + str(i+1) + ": " + lines[i])
    sys.exit(2)
i = idx[0]
old_line = lines[i]
lead = old_line[:len(old_line) - len(old_line.lstrip())]
print("[patch] OLD at line " + str(i+1) + ", lead=" + str(len(lead)) + " spaces")
print("[patch] OLD text: " + old_line)

new_block = [
    lead + "# DS_182/DS_182b: на текущих трёх фикстурах NOT_MENTIONED не срабатывает —",
    lead + "# все объявления (res, CP, v_ps, idx, cn_ComStatusClose, PSH_*_INP, PSH_*_DEL,",
    lead + "# PSH_ED_PRC_SCHM) реально используются в файлах (см. LG_70_06b_ds182_diag2.log).",
    lead + "# Прежнее ожидание NOT_MENTIONED in found не выполнялось и не связано с DS_182",
    lead + "# (DS_182 — про _is_rule_selected и префикс plpcheck.).",
    lead + "# Если понадобится проверять NOT_MENTIONED — нужны отдельные фикстуры",
    lead + "# с реально неиспользуемым объявлением (долг 70 -> 71).",
    lead + "assert " + Q + "plpcheck.NOT_MENTIONED" + Q + " not in found, (",
    lead + "    " + Q + "DS_182: на фикстурах patch_suboptimal_test_3 NOT_MENTIONED не ожидается — " + Q,
    lead + "    " + Q + "все объявления используются; если появился, значит либо изменились " + Q,
    lead + "    " + Q + "фикстуры, либо _check_plp_not_mentioned сломан — проверить LG_70_06b лог" + Q,
    lead + ")",
]
lines[i:i+1] = new_block

new_text = NL.join(lines)
if NEEDLE_IN in new_text and NEEDLE_NOT not in new_text:
    print("[patch] ABORT: старый assert ещё присутствует, новый не найден")
    sys.exit(3)
if NEEDLE_NOT not in new_text:
    print("[patch] ABORT: новый assert not in found не найден")
    sys.exit(4)

new_bytes = new_text.encode("utf-8")
if has_bom:
    new_bytes = b"\xef\xbb\xbf" + new_bytes

if not B.exists():
    B.write_bytes(raw)
    print("[patch] backup: " + B.name + " (" + str(len(raw)) + " bytes)")
else:
    print("[patch] backup exists: " + B.name)

T.write_bytes(new_bytes)
print("[patch] wrote " + T.name + " (" + str(len(new_bytes)) + " bytes, bom=" + str(has_bom) + ")")
