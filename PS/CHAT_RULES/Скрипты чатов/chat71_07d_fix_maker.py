# -*- coding: utf-8 -*-
import os, shutil, py_compile

GEN = r"F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов\chat72_00_maker.py"
BAK = GEN + ".ds71_07dbak"

def apply_once(text, old, new, tag):
    n = text.count(old)
    if n != 1:
        raise SystemExit("ANCHOR %s count=%d" % (tag, n))
    return text.replace(old, new, 1)

def main():
    src = open(GEN, "r", encoding="utf-8").read()
    print("SRC len=", len(src))
    shutil.copyfile(GEN, BAK)
    print("BAK size=", os.path.getsize(BAK))
    q = chr(39)
    dq = chr(34)
    # 1) фикс elif == 'in' -> == "in"
    old1 = "elif == " + q + q + "in" + q + q + " (integer"
    new1 = "elif == " + dq + "in" + dq + " (integer"
    # 2) фикс до ''in'' -> до "in"
    old2 = "до " + q + q + "in" + q + q + ". Намеренно"
    new2 = "до " + dq + "in" + dq + ". Намеренно"
    new = src
    new = apply_once(new, old1, new1, "elif-in")
    new = apply_once(new, old2, new2, "do-in")
    print("NEW len=", len(new), "delta=", len(new) - len(src))
    tmp = GEN + ".ds71_07dtmp"
    open(tmp, "w", encoding="utf-8").write(new)
    try:
        py_compile.compile(tmp, doraise=True)
        print("py_compile tmp OK")
    except Exception as e:
        print("py_compile tmp FAIL:", e)
        os.remove(tmp)
        raise SystemExit(1)
    os.remove(tmp)
    open(GEN, "w", encoding="utf-8").write(new)
    print("WROTE size=", os.path.getsize(GEN))

if __name__ == "__main__":
    main()
