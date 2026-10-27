# -*- coding: utf-8 -*-
import sys, os

SCRIPTS = r"F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов"
REPORTS = r"F:\TO_DBI\PS\CHAT_RULES\Отчеты"
PAMYATKA = os.path.join(REPORTS, "Памятка_чатов.txt")

def w_nobom(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("WRITE:", path, "len=", len(text))

def main():
    lines = []
    if os.path.exists(PAMYATKA):
        with open(PAMYATKA, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    print("PAMYATKA exists=", os.path.exists(PAMYATKA), "lines=", len(lines))

    marker70 = "Чат 70:"
    line70 = ("Чат 70: LG 2026-10-27 — закрыты DS_182 (test_ds182 not in found; 10 passed; f24cc10), "
              "SyntaxWarning scanner.py:1254 -> r-docstring (4470ac8), EXIST_ALL_OR_COLLECTIONS "
              "for_search + this(idx).[..] (d9547a8). Полный регресс 386 passed. HEAD=d9547a8.")

    marker71 = "Чат 71:"
    line71 = ("Чат 71: LG 2026-10-27 — старт. Основная задача: расширить _plp_iter_declarations "
              "под DBI-синтаксис (public NAME [TYPE], NAME in [TYPE], method/batch method/function/procedure NAME). "
              "План: 71_00 старт, 71_01 разведка, 71_02 зонд, 71_03 патч scanner.py, 71_04 точечный+новый тест "
              "NOT_MENTIONED, 71_05 полный регресс, 71_06 коммит+push, 71_07 закрытие.")

    out = []
    seen70 = False
    seen71 = False
    for ln in lines:
        if ln.startswith(marker70):
            out.append(line70); seen70 = True; continue
        if ln.startswith(marker71):
            out.append(line71); seen71 = True; continue
        out.append(ln)
    if not seen70: out.append(line70)
    if not seen71: out.append(line71)

    text = "\n".join(out) + "\n"
    w_nobom(PAMYATKA, text)
    print("OK pamyatka")

if __name__ == "__main__":
    main()
