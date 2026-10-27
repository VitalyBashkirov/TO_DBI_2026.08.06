# -*- coding: utf-8 -*-
from pathlib import Path
import py_compile
REPO = Path(r"F:\TO_DBI\SRC")
GUI  = REPO / "gui_app.py"
FIX  = REPO / "fixer" / "code_fixer.py"
Q  = chr(34)
NL = chr(10)
SP = chr(32)
AP = chr(39)
def bak(p):
    b = p.with_suffix(p.suffix + ".ds187bak")
    if not b.exists(): b.write_bytes(p.read_bytes())
    print("backup:", b)
def patch_fixer():
    src = FIX.read_text(encoding="utf-8")
    if "_generate_user_selection_lines" in src:
        print("[fixer] already patched"); return
    lines = src.splitlines(keepends=True)
    pref = "    lines.append(f" + Q + "**"
    idx = None
    for i, L in enumerate(lines):
        if L.startswith(pref):
            idx = i; break
    if idx is None: raise SystemExit("[fixer] anchor line not found")
    print("[fixer] anchor at line", idx + 1)
    ins = []
    ins.append(SP*4 + "# DS_187: user selection block" + NL)
    ins.append(SP*4 + "try:" + NL)
    ins.append(SP*8 + "lines.extend(scanner._generate_user_selection_lines())" + NL)
    ins.append(SP*4 + "except Exception as e:" + NL)
    ins.append(SP*8 + "logger.warning(f" + Q + "[FIXER] user_selection block unavailable: {e}" + Q + ")" + NL)
    ins.append(NL)
    lines[idx:idx] = ins
    FIX.write_text("".join(lines), encoding="utf-8")
    print("[fixer] patched at", idx + 1)
def make_block_fn(name, html_mode):
    b = []
    b.append("def " + name + "(report_path, user_selection: dict) -> bool:" + NL)
    b.append(SP*4 + "p = Path(report_path)" + NL)
    b.append(SP*4 + "if not p.exists(): return False" + NL)
    b.append(SP*4 + "us = user_selection or {}" + NL)
    b.append(SP*4 + "if not us: return False" + NL)
    b.append(SP*4 + "raw = p.read_text(encoding=" + Q + "utf-8" + Q + ", errors=" + Q + "replace" + Q + ")" + NL)
    b.append(SP*4 + "if " + Q + "ВЫБОР ПОЛЬЗОВАТЕЛЯ В РУБРИКАТОРЕ:" + Q + " in raw: return False" + NL)
    b.append(SP*4 + "nl = " + Q + chr(92)+"r"+chr(92)+"n" + Q + " if " + Q + chr(92)+"r"+chr(92)+"n" + Q + " in raw else " + Q + chr(92)+"n" + Q + NL)
    b.append(SP*4 + "lines = [" + Q + "ВЫБОР ПОЛЬЗОВАТЕЛЯ В РУБРИКАТОРЕ:" + Q + "]" + NL)
    b.append(SP*4 + "lines.append(f" + Q + "  Режим: {us.get(" + AP + "mode" + AP + ", " + AP + AP + ")}" + Q + ")" + NL)
    b.append(SP*4 + "f = us.get(" + AP + "files" + AP + ", []) or []" + NL)
    b.append(SP*4 + "r = us.get(" + AP + "rules" + AP + ", []) or []" + NL)
    b.append(SP*4 + "lines.append(f" + Q + "  Выбрано файлов рубрикатора: {len(f)}" + Q + ")" + NL)
    b.append(SP*4 + "lines.append(f" + Q + "  Выбрано правил: {len(r)}" + Q + ")" + NL)
    b.append(SP*4 + "for x in r[:30]: lines.append(f" + Q + "    [+] {x}" + Q + ")" + NL)
    b.append(SP*4 + "if len(r) > 30: lines.append(f" + Q + "    ... и ещё {len(r)-30} правил" + Q + ")" + NL)
    if html_mode:
        b.append(SP*4 + "import html as h" + NL)
        b.append(SP*4 + "div = " + Q + "<div class=" + Q + Q + "active-rubricators" + Q + Q + ">" + Q + " + h.escape(chr(10).join(lines)) + " + Q + "</div>" + Q + NL)
        b.append(SP*4 + "m = " + Q + "<div class=" + Q + Q + "active-rubricators" + Q + Q + ">" + Q + NL)
        b.append(SP*4 + "i = raw.find(m)" + NL)
        b.append(SP*4 + "if i >= 0:" + NL)
        b.append(SP*8 + "e = raw.find(" + Q + "</div>" + Q + ", i)" + NL)
        b.append(SP*8 + "if e >= 0: new = raw[:e+6] + chr(10) + div + raw[e+6:]" + NL)
        b.append(SP*8 + "else: new = raw + chr(10) + div" + NL)
        b.append(SP*4 + "else: new = raw + chr(10) + div" + NL)
    else:
        b.append(SP*4 + "block = nl.join(lines) + nl" + NL)
        b.append(SP*4 + "m = " + Q + "Активные рубрикаторы и флаги:" + Q + NL)
        b.append(SP*4 + "if m in raw:" + NL)
        b.append(SP*8 + "pos = raw.index(m); end = raw.find(nl+nl, pos)" + NL)
        b.append(SP*8 + "if end >= 0: new = raw[:end+len(nl)] + block + raw[end+len(nl):]" + NL)
        b.append(SP*8 + "else: new = raw + nl + block" + NL)
        b.append(SP*4 + "else: new = raw + nl + block" + NL)
    b.append(SP*4 + "p.write_text(new, encoding=" + Q + "utf-8" + Q + "); return True" + NL)
    b.append(NL)
    return "".join(b)
def patch_gui():
    t = GUI.read_text(encoding="utf-8")
    if "def inject_user_selection_block" in t:
        print("[gui] functions already exist")
    else:
        anchor = "class DBIMigrationApp:"
        if anchor not in t: raise SystemExit("[gui] class anchor not found")
        fn = NL + make_block_fn("inject_user_selection_block", False) + make_block_fn("inject_user_selection_html", True)
        t = t.replace(anchor, fn + NL + anchor, 1)
        GUI.write_text(t, encoding="utf-8")
        print("[gui] functions injected")
def patch_calls():
    t = GUI.read_text(encoding="utf-8")
    changed = False
    if "inject_user_selection_block(output_path" not in t:
        a = SP*12 + "scanner.generate_report(output_path, mode=" + AP + "scan" + AP + ", fixed_count=0,"
        i = t.find(a)
        if i < 0: raise SystemExit("[gui] call md anchor not found")
        j = t.find(NL+NL, i)
        if j < 0: raise SystemExit("[gui] call md end not found")
        ins = NL + SP*12 + "try:" + NL + SP*16 + "inject_user_selection_block(output_path, self._collect_user_selection())" + NL + SP*12 + "except Exception as _e:" + NL + SP*16 + "self.log(f" + Q + "  [!] user_selection .md: {_e}" + Q + ", " + AP + "warning" + AP + ")" + NL
        t = t[:j] + ins + t[j:]
        changed = True
    if "inject_user_selection_html(html_report_path" not in t:
        a = SP*12 + "scanner.generate_report(html_report_path)"
        i = t.find(a)
        if i < 0: raise SystemExit("[gui] call html anchor not found")
        j = t.find(NL+NL, i)
        if j < 0: j = i + len(a)
        ins = NL + SP*12 + "try:" + NL + SP*16 + "inject_user_selection_html(html_report_path, self._collect_user_selection())" + NL + SP*12 + "except Exception as _e:" + NL + SP*16 + "self.log(f" + Q + "  [!] user_selection .html: {_e}" + Q + ", " + AP + "warning" + AP + ")" + NL
        t = t[:j] + ins + t[j:]
        changed = True
    if changed:
        GUI.write_text(t, encoding="utf-8")
        print("[gui] calls injected")
    else:
        print("[gui] calls already present")
if __name__ == "__main__":
    bak(GUI); bak(FIX)
    patch_fixer()
    patch_gui()
    patch_calls()
    py_compile.compile(str(GUI), doraise=True)
    py_compile.compile(str(FIX), doraise=True)
    print("PATCH OK")
