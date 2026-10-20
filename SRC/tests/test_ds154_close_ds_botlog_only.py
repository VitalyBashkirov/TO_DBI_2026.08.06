# -*- coding: utf-8 -*-
"""DS_154 (OQ-2): close_ds.ps1 must not create empty commit when only bot.log staged."""
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
CLOSE_DS = ROOT / "tools" / "close_ds.ps1"


def test_close_ds_has_botlog_only_guard():
    txt = CLOSE_DS.read_text(encoding="utf-8-sig")
    # guard present
    assert "OQ-2" in txt, "close_ds.ps1: OQ-2 guard marker missing"
    assert "nonBotLog" in txt, "nonBotLog guard missing"
    # checks staged list
    assert "git diff --cached --name-only" in txt
    # returns early when only bot.log
    m = re.search(r"if \(\$nonBotLog\.Count -eq 0\)\s*\{(.+?)\n\}", txt, re.S)
    assert m, "nonBotLog.Count -eq 0 block not found"
    body = m.group(1)
    assert "return" in body, "guard must return (skip commit)"


def test_close_ds_guard_before_commit():
    txt = CLOSE_DS.read_text(encoding="utf-8-sig")
    i_guard = txt.find("if ($nonBotLog.Count -eq 0)")
    i_commit = txt.find("git commit -m")
    assert i_guard > 0 and i_commit > 0
    assert i_guard < i_commit, "guard must be before git commit"


def test_close_ds_syntax_ok():
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "$ErrorActionPreference='Stop'; $null = [ScriptBlock]::Create((Get-Content -Raw -LiteralPath '" + str(CLOSE_DS) + "')); 'OK'"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert "OK" in (r.stdout or ""), f"PS parse error:\n{r.stdout}\n{r.stderr}"