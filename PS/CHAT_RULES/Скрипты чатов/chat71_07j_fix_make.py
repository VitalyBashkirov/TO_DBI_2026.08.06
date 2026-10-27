# -*- coding: utf-8 -*-
import os, py_compile

FIXMAKE = r"F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов\chat71_07f_make.py"

def apply_once(text, old, new, tag):
    n = text.count(old)
    print("TAG %s count=%d" % (tag, n))
    if n != 1:
        raise SystemExit("ANCHOR %s count=%d" % (tag, n))
    return text.replace(old, new, 1)

def main():
    src = open(FIXMAKE, "r", encoding="utf-8").read()
    print("SRC len=", len(src))
    bs = chr(92)
    # old: A("    st.append(r'F:\\TO_DBI\\PS\\CHAT_RULES\\')")  -> c двумя \\ в конце
    old = 'A("    st.append(r''F:' + bs + bs + 'TO_DBI' + bs + bs + 'PS' + bs + bs + 'CHAT_RULES' + bs + bs + '')")'
    # new: A("    st.append(r'F:\\TO_DBI\\PS\\CHAT_RULES')")  -> без trailing \\
    new = 'A("    st.append(r''F:' + bs + bs + 'TO_DBI' + bs + bs + 'PS' + bs + bs + 'CHAT_RULES'')")'
    t = apply_once(src, old, new, "st-chat_rules")
    print("NEW len=", len(t), "delta=", len(t) - len(src))
    tmp = FIXMAKE + ".ds71_07jtmp"
    open(tmp, "w", encoding="utf-8").write(t)
    try:
        py_compile.compile(tmp, doraise=True)
        print("py_compile tmp OK")
    except Exception as e:
        print("py_compile tmp FAIL:", e)
        os.remove(tmp)
        raise SystemExit(1)
    os.remove(tmp)
    open(FIXMAKE, "w", encoding="utf-8").write(t)
    print("WROTE size=", os.path.getsize(FIXMAKE))

if __name__ == "__main__":
    main()
