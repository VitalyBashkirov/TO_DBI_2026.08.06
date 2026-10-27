import io, os, sys

RULES   = sys.argv[1]
RU      = sys.argv[2]
MARKER  = "## 63_1."
SEP     = "## "

with io.open(RU, "r", encoding="utf-8", newline="") as f:
    ru = f.read()
if not ru.endswith("\n"):
    ru = ru + "\r\n"
with io.open(RULES, "r", encoding="utf-8", newline="") as f:
    src = f.read()

idx = src.find(MARKER)
if idx < 0:
    print("[INFO] marker not found, appending at EOF")
    if not src.endswith("\n"):
        src = src + "\r\n"
    out = src + "\r\n" + ru
else:
    tail_pos = src.find(SEP, idx + len(MARKER))
    if tail_pos < 0:
        out = src[:idx] + ru
    else:
        out = src[:idx] + ru + src[tail_pos:]

with io.open(RULES, "w", encoding="utf-8", newline="") as f:
    f.write(out)

print("[OK] replaced block 63_1, rules len =", len(out))