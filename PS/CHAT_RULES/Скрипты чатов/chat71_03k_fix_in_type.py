# -*- coding: utf-8 -*-
import os, shutil, py_compile

SCANNER = r"F:\TO_DBI\SRC\analyzer\scanner.py"
BAK     = SCANNER + ".ds71_03k_prev"

def apply_once(text, old, new, tag):
    n = text.count(old)
    if n != 1:
        raise SystemExit("ANCHOR %s count=%d" % (tag, n))
    return text.replace(old, new, 1)

def main():
    src = open(SCANNER, "r", encoding="utf-8").read()
    print("SRC len=", len(src))
    shutil.copyfile(SCANNER, BAK)
    print("BAK size=", os.path.getsize(BAK))
    q = chr(39)
    old = "                elif type_str.lower().startswith(" + q + "in" + q + "):"
    new = "                elif type_str.lower() == " + q + "in" + q + ":"
    new_src = apply_once(src, old, new, "elif-in")
    print("delta=", len(new_src) - len(src))
    tmp = SCANNER + ".ds71_03k_tmp"
    open(tmp, "w", encoding="utf-8").write(new_src)
    try:
        py_compile.compile(tmp, doraise=True)
        print("py_compile tmp OK")
    except Exception as e:
        print("py_compile tmp FAIL:", e)
        os.remove(tmp)
        raise SystemExit(1)
    os.remove(tmp)
    open(SCANNER, "w", encoding="utf-8").write(new_src)
    print("WROTE size=", os.path.getsize(SCANNER))

if __name__ == "__main__":
    main()
