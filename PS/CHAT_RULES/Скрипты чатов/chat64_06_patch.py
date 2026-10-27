# -*- coding: utf-8 -*-
"""chat64_06_patch.py - t3/t4: garantirovannyj otkat settings.json (try/finally)."""
import io
import os
import re
import shutil
import sys

TARGET = r"F:\TO_DBI\SRC\tests\test_ds183_k4_model_setting.py"
BACKUP = TARGET + ".ds183bak"

def read(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return f.read()

def write(p, t):
    with io.open(p, "w", encoding="utf-8-sig", newline="") as f:
        f.write(t)

NEW_T3_FINALLY = (
    "\n"
    "    finally:\n"
    "        # garantirovannyj otkat: ne brosaem, tolko WARN\n"
    "        try:\n"
    "            if os.path.exists(BACKUP):\n"
    "                shutil.copy2(BACKUP, SETTINGS)\n"
    "            else:\n"
    "                print(\"  [WARN] t3 finally: BACKUP missing\")\n"
    "        except Exception as e:\n"
    "            print(f\"  [WARN] t3 restore: {e}\")\n"
    "        try:\n"
    "            if os.path.exists(BACKUP):\n"
    "                os.remove(BACKUP)\n"
    "        except Exception as e:\n"
    "            print(f\"  [WARN] t3 remove: {e}\")\n"
)

NEW_T4_FINALLY = (
    "\n"
    "    finally:\n"
    "        gui_app.messagebox.showwarning = _orig_warn\n"
    "        # garantirovannyj otkat: ne brosaem, tolko WARN\n"
    "        try:\n"
    "            if os.path.exists(BACKUP):\n"
    "                shutil.copy2(BACKUP, SETTINGS)\n"
    "            else:\n"
    "                print(\"  [WARN] t4 finally: BACKUP missing\")\n"
    "        except Exception as e:\n"
    "            print(f\"  [WARN] t4 restore: {e}\")\n"
    "        try:\n"
    "            if os.path.exists(BACKUP):\n"
    "                os.remove(BACKUP)\n"
    "        except Exception as e:\n"
    "            print(f\"  [WARN] t4 remove: {e}\")\n"
)

def replace_t3(src):
    i = src.find("    finally:\n        if not os.path.exists(BACKUP):\n            raise RuntimeError(\"DS_186: BACKUP missing in t3 finally\")")
    if i < 0: return None
    j = src.find("def test_t4_", i)
    if j < 0: return None
    return src[:i] + NEW_T3_FINALLY + "\n\n" + src[j:]

def replace_t4(src):
    i = src.find("    finally:\n        gui_app.messagebox.showwarning = _orig_warn\n        if not os.path.exists(BACKUP):\n            raise RuntimeError(\"DS_186: BACKUP missing in t4 finally\")")
    if i < 0: return None
    j = src.find("def test_t5_", i)
    if j < 0: return None
    return src[:i] + NEW_T4_FINALLY + "\n\n" + src[j:]

def main():
    if not os.path.exists(TARGET):
        print("[FATAL] no target: " + TARGET); return 2
    src = read(TARGET)
    if "garantirovannyj otkat" in src:
        print("[SKIP] already applied"); return 0
    if os.path.exists(BACKUP): os.remove(BACKUP)
    shutil.copy2(TARGET, BACKUP)
    print("[BK] " + BACKUP)
    t3 = replace_t3(src)
    if t3 is None:
        print("[WARN] t3 anchor not found")
    else:
        src = t3
        print("[OK] t3 replaced")
    t4 = replace_t4(src)
    if t4 is None:
        print("[WARN] t4 anchor not found")
    else:
        src = t4
        print("[OK] t4 replaced")
    write(TARGET, src)
    print("[OK] wrote " + TARGET)
    return 0

if __name__ == "__main__":
    sys.exit(main())
