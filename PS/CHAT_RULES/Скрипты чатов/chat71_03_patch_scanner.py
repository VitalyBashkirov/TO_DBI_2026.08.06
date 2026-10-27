# -*- coding: utf-8 -*-
import sys, os, shutil, py_compile

SCANNER = r"F:\TO_DBI\SRC\analyzer\scanner.py"
BAK     = SCANNER + ".ds71_03bak"
FRAG    = r"F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов"

def read_frag(name):
    p = os.path.join(FRAG, name)
    return open(p, "r", encoding="utf-8").read()

def apply_once(text, old, new, tag):
    n = text.count(old)
    if n != 1:
        raise SystemExit("ANCHOR %s count=%d" % (tag, n))
    return text.replace(old, new, 1)

def main():
    if not os.path.exists(SCANNER):
        raise SystemExit("no scanner")
    src = open(SCANNER, "r", encoding="utf-8").read()
    print("SRC len=", len(src))
    shutil.copyfile(SCANNER, BAK)
    print("BAK:", BAK, "size=", os.path.getsize(BAK))
    new = src
    new = apply_once(new, read_frag("chat71_03_frag_old_A.txt"),  read_frag("chat71_03_frag_new_A.txt"),  "A")
    new = apply_once(new, read_frag("chat71_03_frag_old_A2.txt"), read_frag("chat71_03_frag_new_A2.txt"), "A2")
    new = apply_once(new, read_frag("chat71_03_frag_old_B.txt"),  read_frag("chat71_03_frag_new_B.txt"),  "B")
    print("NEW len=", len(new), "delta=", len(new) - len(src))
    tmp = SCANNER + ".ds71_03tmp"
    open(tmp, "w", encoding="utf-8").write(new)
    try:
        py_compile.compile(tmp, doraise=True)
        print("py_compile tmp OK")
    except Exception as e:
        print("py_compile tmp FAIL:", e)
        os.remove(tmp)
        raise SystemExit(1)
    os.remove(tmp)
    open(SCANNER, "w", encoding="utf-8").write(new)
    print("WROTE:", SCANNER, "size=", os.path.getsize(SCANNER))

if __name__ == "__main__":
    main()
