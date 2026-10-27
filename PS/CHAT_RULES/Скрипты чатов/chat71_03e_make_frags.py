# -*- coding: utf-8 -*-
import os, sys

SCANNER = r"F:\TO_DBI\SRC\analyzer\scanner.py"
FRAG    = r"F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов"

def w(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("W", os.path.basename(path), "len=", len(text))

def show(tag, s):
    print(tag, "repr=", repr(s))

def main():
    src = open(SCANNER, "r", encoding="utf-8").read()
    print("SCANNER len=", len(src))
    lines = src.split("\n")
    print("lines=", len(lines))

    # диагностика: что реально в старом old_A.txt
    p = os.path.join(FRAG, "chat71_03_frag_old_A.txt")
    if os.path.exists(p):
        t = open(p, "r", encoding="utf-8").read()
        print("OLD_A.txt len=", len(t))
        show("OLD_A first line:", t.split("\\n")[0])
        show("SCANNER[941]:", lines[940])

    # вырезаем фрагменты из scanner.py по номерам строк (1-based)
    oldA  = "\\n".join(lines[940:948])   # 941..948
    oldA2 = "\\n".join(lines[958:961])   # 959..961
    oldB  = "\\n".join(lines[1102:1111]) # 1103..1111


    newA2 = oldA2 + "\\n" + a2_add

    b_add_lines = [
        "",
        "        # DS71: public function/procedure, procedure, method, batch method",
        "        extra_kinds = (",
        "        )",
        "        for i, line in enumerate(lines, 1):",
        "            stripped = line.strip()",
        "                continue",
        "            for rx, kind in extra_kinds:",
        "                m = rx.match(line)",
        "                if m:",
        "                    declared[m.group(1)] = (i, kind, stripped)",
        "                    break",
    ]
    newB = oldB + "\\n" + "\\n".join(b_add_lines)

    frags = {
        "chat71_03_frag_old_A.txt":  oldA,
        "chat71_03_frag_new_A.txt":  newA,
        "chat71_03_frag_old_A2.txt": oldA2,
        "chat71_03_frag_new_A2.txt": newA2,
        "chat71_03_frag_old_B.txt":  oldB,
        "chat71_03_frag_new_B.txt":  newB,
    }

    for name, text in frags.items():
        p = os.path.join(FRAG, name)
        w(p, text)

    print("--- verify old in scanner ---")
    for name in ("chat71_03_frag_old_A.txt","chat71_03_frag_old_A2.txt","chat71_03_frag_old_B.txt"):
        p = os.path.join(FRAG, name)
        t = open(p, "r", encoding="utf-8").read()
        print(name, "count=", src.count(t))

    print("--- verify new NOT in scanner ---")
    for name in ("chat71_03_frag_new_A.txt","chat71_03_frag_new_A2.txt","chat71_03_frag_new_B.txt"):
        p = os.path.join(FRAG, name)
        t = open(p, "r", encoding="utf-8").read()
        print(name, "count=", src.count(t))

    print("DONE")

if __name__ == "__main__":
    main()
