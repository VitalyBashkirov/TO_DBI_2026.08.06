# -*- coding: utf-8 -*-
"""DS_143 — тесты: only_ai в шапках, поведение галки.

Покрывает:
- flags_line (ai_exchange): only_ai в строке флагов (A2).
- write_request (ai_exchange): строка Флаги: с only_ai.
- chk_ai_only (gui_app): state по k3_normal (как K3).
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / 'SRC'
sys.path.insert(0, str(SRC))


# ----------------------------------------------------------------------
# 1-3. flags_line (ai_exchange)
# ----------------------------------------------------------------------

def test_flags_line_without_only_ai():
    import ai_exchange as ae
    flags = {'regex': True, 'hybrid': True, 'ai_fallback': True,
             'ignore': False, 'backup': True, 'other': True}
    line = ae.flags_line(flags)
    assert 'only_ai' not in line
    assert line == 'regex=V, hybrid=V, ai_fallback=V, ignore=x, backup=V, other=V'


def test_flags_line_with_only_ai_true():
    import ai_exchange as ae
    flags = {'regex': True, 'hybrid': True, 'ai_fallback': True,
             'ignore': False, 'backup': True, 'other': True,
             'only_ai': True}
    line = ae.flags_line(flags)
    assert line.endswith('only_ai=V')


def test_flags_line_with_only_ai_false():
    import ai_exchange as ae
    flags = {'regex': True, 'hybrid': True, 'ai_fallback': True,
             'ignore': False, 'backup': True, 'other': True,
             'only_ai': False}
    line = ae.flags_line(flags)
    assert line.endswith('only_ai=x')


# ----------------------------------------------------------------------
# 4. write_request — строка Флаги: содержит only_ai
# ----------------------------------------------------------------------

def test_write_request_has_only_ai(tmp_path, monkeypatch):
    import ai_exchange as ae

    # изолировать каталоги обмена в tmp_path
    monkeypatch.setattr(ae, 'base_dir', lambda: tmp_path)

    src = tmp_path / 'X.plp'
    src.write_text('begin\n  null;\nend;\n', encoding='utf-8')

    # issues — минимальный набор, чтобы запрос сформировался
    class _Issue:
        def __init__(self, line_number, issue_type, description, original_code):
            self.line_number = line_number
            self.issue_type = issue_type
            self.description = description
            self.original_code = original_code

    issues = [_Issue(2, 'TEST', 'test desc', 'null;')]
    flags = {'regex': True, 'hybrid': True, 'ai_fallback': True,
             'ignore': False, 'backup': True, 'other': True,
             'only_ai': True}

    req = ae.write_request(src, issues, flags)
    text = Path(req).read_text(encoding='utf-8')
    assert 'only_ai=V' in text


def test_write_request_only_ai_x(tmp_path, monkeypatch):
    import ai_exchange as ae
    monkeypatch.setattr(ae, 'base_dir', lambda: tmp_path)

    src = tmp_path / 'Y.plp'
    src.write_text('begin\n  null;\nend;\n', encoding='utf-8')

    class _Issue:
        def __init__(self, line_number, issue_type, description, original_code):
            self.line_number = line_number
            self.issue_type = issue_type
            self.description = description
            self.original_code = original_code

    issues = [_Issue(2, 'TEST', 'test desc', 'null;')]
    flags = {'regex': True, 'hybrid': True, 'ai_fallback': True,
             'ignore': False, 'backup': True, 'other': True,
             'only_ai': False}

    req = ae.write_request(src, issues, flags)
    text = Path(req).read_text(encoding='utf-8')
    assert 'only_ai=x' in text


# ----------------------------------------------------------------------
# 5-6. chk_ai_only: state по k3_normal (как K3)
# ----------------------------------------------------------------------

def test_chk_ai_only_exists(app):
    """Галка chk_ai_only существует в GUI."""
    assert hasattr(app, 'chk_ai_only')
    assert hasattr(app, 'ai_only_var')


def test_chk_ai_only_state_matches_k3_normal(app, monkeypatch):
    """Состояние галки совпадает с состоянием btn_to_ai (K3)."""
    # Принудительно пересчитать main-buttons
    app._update_main_buttons()

    # Считываем состояние chk_ai_only
    chk_state = app.chk_ai_only.state()
    btn_state = app.btn_to_ai.state()

    # chk_ai_only disabled <=> btn_to_ai disabled
    chk_disabled = 'disabled' in chk_state
    btn_disabled = 'disabled' in btn_state
    assert chk_disabled == btn_disabled


def test_ai_only_flag_helper(app):
    """_only_ai_flag возвращает {'only_ai': bool}."""
    flag = app._only_ai_flag()
    assert isinstance(flag, dict)
    assert 'only_ai' in flag
    assert isinstance(flag['only_ai'], bool)