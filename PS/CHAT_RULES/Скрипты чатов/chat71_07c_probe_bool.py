# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, r"F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов")
import chat72_00_maker as m

rep = []
rep.append("# Отчёт чата 71 (2026-10-27, LG)")
rep.append("")
rep.append("## Главное")
rep.append("- Долг 1 ...")
rep.append("- scanner.py: ...")
rep.append("- Тест test_ds71 ...")
rep.append("- Полный регресс: ...")
rep.append("- Коммит b3100ad ...")
rep.append("")
rep.append("## Что сделано")
rep.append("- 71_00: ...")
rep.append("- 71_01..71_01c: ...")
rep.append("- 71_02..71_02b: ...")
rep.append("- 71_03..71_03h: ...")
for i, x in enumerate(rep):
    print(i, type(x).__name__, repr(x)[:80])

print("---- direct scan of m.py source: rep.append items ----")
p = r"F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов\chat72_00_maker.py"
txt = open(p, "r", encoding="utf-8").read()
n = 0
for line in txt.splitlines():
    if "rep.append" in line:
        n += 1
print(n)
