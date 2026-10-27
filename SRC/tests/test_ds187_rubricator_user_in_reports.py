# -*- coding: utf-8 -*-
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gui_app import inject_user_selection_block, inject_user_selection_html

US = {
    "mode": "конкретные правила (2 из 332)",
    "files": ["PlpCheck"],
    "rules": ["plpcheck.SUBOPTIMAL_QUERY_WROWNUM", "plpcheck.STYLE_PREFIX"],
    "total_rules": 332,
}

MD_HEAD = "Активные рубрикаторы и флаги:" + chr(10) + "  PlpCheck : ВКЛ" + chr(10) + chr(10) + "Таблица:" + chr(10)
HTML_HEAD = "<html><body>" + chr(10) + "<div class=""active-rubricators"">Активные рубрикаторы и флаги:" + chr(10) + "</div>" + chr(10) + "<h2>tab</h2></body></html>"

def _tmp(suffix, text):
    d = tempfile.mkdtemp(prefix="ds187_")
    p = Path(d) / ("rep" + suffix)
    p.write_text(text, encoding="utf-8")
    return p

def test_md_block_added():
    p = _tmp(".md", MD_HEAD)
    assert inject_user_selection_block(p, US) is True
    t = p.read_text(encoding="utf-8")
    assert "ВЫБОР ПОЛЬЗОВАТЕЛЯ В РУБРИКАТОРЕ:" in t
    assert "Режим:" in t
    assert "Выбрано файлов рубрикатора: 1" in t
    assert "Выбрано правил: 2" in t

def test_md_idempotent():
    p = _tmp(".md", MD_HEAD)
    assert inject_user_selection_block(p, US) is True
    assert inject_user_selection_block(p, US) is False
    t = p.read_text(encoding="utf-8")
    assert t.count("ВЫБОР ПОЛЬЗОВАТЕЛЯ В РУБРИКАТОРЕ:") == 1

def test_md_empty_us():
    p = _tmp(".md", MD_HEAD)
    before = p.read_text(encoding="utf-8")
    assert inject_user_selection_block(p, {}) is False
    assert p.read_text(encoding="utf-8") == before

def test_html_block_added():
    p = _tmp(".html", HTML_HEAD)
    assert inject_user_selection_html(p, US) is True
    t = p.read_text(encoding="utf-8")
    assert "ВЫБОР ПОЛЬЗОВАТЕЛЯ В РУБРИКАТОРЕ:" in t
    assert "Режим:" in t

def test_html_idempotent():
    p = _tmp(".html", HTML_HEAD)
    assert inject_user_selection_html(p, US) is True
    assert inject_user_selection_html(p, US) is False
    t = p.read_text(encoding="utf-8")
    assert t.count("ВЫБОР ПОЛЬЗОВАТЕЛЯ В РУБРИКАТОРЕ:") == 1

def test_scan_vvvxvv_block(tmp_path):
    from analyzer.scanner import PLPlusScanner
    from fixer.code_fixer import save_scan_only_log
    cfg = {"paths": {"source_dir": str(tmp_path)}}
    sc = PLPlusScanner(cfg, [], None, user_selection=US)
    flags = {}
    p = save_scan_only_log(tmp_path, "src", flags, sc, cfg)
    assert p is not None and Path(p).exists()
    t = Path(p).read_text(encoding="utf-8")
    assert "ВЫБОР ПОЛЬЗОВАТЕЛЯ В РУБРИКАТОРЕ:" in t
    assert "Режим:" in t

def test_scanner_accepts_user_selection(tmp_path):
    from analyzer.scanner import PLPlusScanner
    cfg = {"paths": {"source_dir": str(tmp_path)}}
    sc = PLPlusScanner(cfg, [], None, user_selection=US)
    assert sc.user_selection == US

