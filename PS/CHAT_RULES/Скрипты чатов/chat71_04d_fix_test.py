# -*- coding: utf-8 -*-
import os, shutil

TEST = r"F:\TO_DBI\SRC\tests\test_ds71_not_mentioned_real.py"

def main():
    src = open(TEST, "r", encoding="utf-8").read()
    print("SRC len=", len(src))
    bs = chr(92)
    old1 = bs + bs + "s+"
    new1 = bs + "s+"
    old2 = bs + bs + "w+"
    new2 = bs + "w+"
    n1 = src.count(old1)
    n2 = src.count(old2)
    print("count(\\\\\\\\s+)=", n1, " count(\\\\\\\\w+)=", n2)
    if n1 == 0 and n2 == 0:
        print("нечего менять — уже одинарные")
    new = src.replace(old1, new1).replace(old2, new2)
    open(TEST, "w", encoding="utf-8", newline="\n").write(new)
    print("WROTE len=", len(new), " delta=", len(new)-len(src))

if __name__ == "__main__":
    main()
