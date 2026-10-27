# -*- coding: utf-8 -*-
from pathlib import Path
REP = Path(r"F:\TO_DBI\PS\CHAT_RULES\Отчеты\69.Отчёт.txt")
NL = chr(10)
t = REP.read_text(encoding="utf-8")
line = "- 1. DS_182: plpcheck.NOT_MENTIONED не находится в test_ds182 — отдельная задача (baseline 1 failed)."
anchor = "- 2. SyntaxWarning: invalid escape sequence в scanner.py:1257 — заменить на raw-строку."
if line in t:
    print("[rep] пункт 1 уже есть — пропуск")
elif anchor not in t:
    print("[rep] якорь пункта 2 не найден — вставка в конец раздела")
    h = "## Долги 69 -> 70"
    i = t.find(h)
    if i < 0:
        t = t.rstrip() + NL + line + NL
    else:
        j = t.find(NL, i)
        t = t[:j+1] + line + NL + t[j+1:]
    REP.write_text(t, encoding="utf-8")
else:
    t = t.replace(anchor, line + NL + anchor, 1)
    REP.write_text(t, encoding="utf-8")
b = REP.read_bytes()
print("bytes=", len(b), "bom=", b.startswith(b"\xef\xbb\xbf"))
print("DONE")
