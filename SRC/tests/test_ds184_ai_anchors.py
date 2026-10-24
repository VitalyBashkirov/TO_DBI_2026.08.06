# -*- coding: utf-8 -*-
"""DS_184: AI-якоря (МПК) в ai_exchange.apply_fixes / process_response.

Проверяем:
  t1. mark_in_code=False -> якорей нет.
  t2. mark_in_code=True, log_level='Обычный' -> якорь "-- YYYY.MM.DD HH:MI|<rule>|<Ai>|Строка NN".
  t3. clean_output=True (ВТИК) отменяет mark_in_code -> якорей нет.
  t4. log_level='Минимальный' -> один сводный "-- МПК: N правок, правила: ...".
  t5. log_level='Подробный', диапазон 3-5 -> "Строки 3-5" + под-якоря "Строка 4", "Строка 5".
  t6. user='Vitaly' -> в якоре есть " Vitaly|".
  t7. stats['anchors'] == число вставленных якорей.
  t8. Идемпотентность: повторный apply_fixes без правок (before mismatch) -> anchors=0.
"""
import io
import os
import re
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import ai_exchange


ANCHOR_RE = re.compile(
    r"^\s*-- \d{4}\.\d{2}\.\d{2} \d{2}:\d{2}( [^|]+)?\|[^|]+\|<Ai>\|Строк[аи] \d+(-\d+)?$"
)


def _mk_file(lines, newline="\n"):
    fd, path = tempfile.mkstemp(suffix=".plp", text=False)
    os.close(fd)
    content = newline.join(lines)
    if not content.endswith(newline):
        content += newline
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    return Path(path)


def _read(path):
    with io.open(path, "r", encoding="utf-8-sig", newline="") as f:
        return f.read()


def _make_fix(line, after, rule="DS_001", conf=0.9, before=None):
    return {"line": line, "after": after, "confidence": conf,
            "rule": rule, "before": before}


def test_t1_no_anchors_when_off():
    p = _mk_file(["  a", "  b", "  c"])
    try:
        fixes = [_make_fix(2, "  B", before="  b")]
        st = ai_exchange.apply_fixes(p, fixes, mark_in_code=False)
        txt = _read(p)
        assert st["anchors"] == 0, st
        assert not any(l.lstrip().startswith("-- ") for l in txt.splitlines()), txt
        assert "  B" in txt, txt
    finally:
        try: p.unlink()
        except Exception: pass


def test_t2_anchor_when_on():
    p = _mk_file(["  a", "  b", "  c"])
    try:
        fixes = [_make_fix(2, "  B", rule="DS_001", before="  b")]
        st = ai_exchange.apply_fixes(p, fixes, mark_in_code=True,
                                     log_level="Обычный")
        txt = _read(p)
        assert st["anchors"] >= 1, st
        lines = txt.splitlines()
        anchor_idx = [i for i, l in enumerate(lines) if l.lstrip().startswith("-- ")]
        assert anchor_idx, txt
        anchor = lines[anchor_idx[0]].lstrip()
        assert "DS_001" in anchor, anchor
        assert "<Ai>" in anchor, anchor
        assert "Строка 2" in anchor, anchor
        assert ANCHOR_RE.match(anchor), anchor
        assert "  B" in lines[anchor_idx[0] + 1], lines
    finally:
        try: p.unlink()
        except Exception: pass


def test_t3_vtik_cancels():
    p = _mk_file(["  a", "  b", "  c"])
    try:
        fixes = [_make_fix(2, "  B", before="  b")]
        st = ai_exchange.apply_fixes(p, fixes, mark_in_code=True,
                                     clean_output=True)
        txt = _read(p)
        assert st["anchors"] == 0, st
        assert not any(l.lstrip().startswith("-- ") for l in txt.splitlines()), txt
        assert "  B" in txt, txt
    finally:
        try: p.unlink()
        except Exception: pass


def test_t4_minimal():
    p = _mk_file(["  a", "  b", "  c", "  d"])
    try:
        fixes = [
            _make_fix(2, "  B", rule="DS_001", before="  b"),
            _make_fix(4, "  D", rule="DS_001", before="  d"),
        ]
        st = ai_exchange.apply_fixes(p, fixes, mark_in_code=True,
                                     log_level="Минимальный")
        txt = _read(p)
        assert st["anchors"] == 1, st
        anchors = [l for l in txt.splitlines() if l.lstrip().startswith("-- МПК:")]
        assert len(anchors) == 1, txt
        assert "2 правок" in anchors[0], anchors[0]
        assert "DS_001" in anchors[0], anchors[0]
    finally:
        try: p.unlink()
        except Exception: pass


def test_t5_detailed_range():
    p = _mk_file(["  l1", "  l2", "  l3", "  l4", "  l5", "  l6"])
    try:
        fixes = [
            _make_fix(3, "  L3", rule="DS_010", before="  l3"),
            _make_fix(4, "  L4", rule="DS_010", before="  l4"),
            _make_fix(5, "  L5", rule="DS_010", before="  l5"),
        ]
        st = ai_exchange.apply_fixes(p, fixes, mark_in_code=True,
                                     log_level="Подробный")
        txt = _read(p)
        lines = txt.splitlines()
        assert any("Строки 3-5" in l for l in lines if l.lstrip().startswith("-- ")), txt
        assert any("Строка 4" in l for l in lines if l.lstrip().startswith("-- ")), txt
        assert any("Строка 5" in l for l in lines if l.lstrip().startswith("-- ")), txt
        assert st["anchors"] == 3, st
    finally:
        try: p.unlink()
        except Exception: pass


def test_t6_user_tag():
    p = _mk_file(["  a", "  b"])
    try:
        fixes = [_make_fix(2, "  B", before="  b")]
        st = ai_exchange.apply_fixes(p, fixes, mark_in_code=True,
                                     log_level="Обычный", user="Vitaly")
        txt = _read(p)
        anchors = [l for l in txt.splitlines() if l.lstrip().startswith("-- ")]
        assert anchors, txt
        assert " Vitaly|" in anchors[0], anchors[0]
    finally:
        try: p.unlink()
        except Exception: pass


def test_t7_stats_anchors_count():
    p = _mk_file(["  a", "  b", "  c", "  d"])
    try:
        fixes = [
            _make_fix(1, "  A", rule="DS_001", before="  a"),
            _make_fix(3, "  C", rule="DS_002", before="  c"),
        ]
        st = ai_exchange.apply_fixes(p, fixes, mark_in_code=True,
                                     log_level="Обычный")
        assert st["anchors"] == 2, st
    finally:
        try: p.unlink()
        except Exception: pass


def test_t8_idempotent_noop():
    p = _mk_file(["  a", "  b"])
    try:
        fixes = [_make_fix(2, "  B", before="  b")]
        ai_exchange.apply_fixes(p, fixes, mark_in_code=True, log_level="Обычный")
        st = ai_exchange.apply_fixes(p, fixes, mark_in_code=True, log_level="Обычный")
        assert st["anchors"] == 0, st
        assert st["skipped"] >= 1, st
    finally:
        try: p.unlink()
        except Exception: pass
