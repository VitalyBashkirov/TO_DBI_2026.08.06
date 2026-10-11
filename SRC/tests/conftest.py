# -*- coding: utf-8 -*-
"""Pytest conftest для DS_140 — миграция legacy-тестов на pytest.

v4 (DS_140 Шаг 3.2): добавлена фикстура settings_backup (DS_086).

Фикстуры:
- app (scope=function): Tk + DBIMigrationApp, гарантированный destroy.
- isolated_ai: изоляция EXCHANGE\\AI_IN и AI_OUT через tmp_path.
- settings_backup: backup/restore SRC/settings.json через .ds140bak.
- patched_messagebox (autouse, session): блокировка диалогов messagebox.

Monkeypatch'и:
- DBIMigrationApp.log — не пишем в logs_Deep.
- DBIMigrationApp._check_log_size — вызывается в __init__, не нужен в тестах.
- DBIMigrationApp._poll_ai_out — 5-секундный таймер, не нужен в тестах.

Фикс TclError:
- _cancel_all_after(root) — отмена pending after перед destroy.
- monkeypatch _poll_ai_out — страховка (таймер не перезапустится).
"""
import shutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest
import tkinter as tk

import gui_app


def _cancel_all_after(root):
    """Отменить все pending after-команды Tk перед destroy.

    Иначе Tcl пытается вызвать уничтоженные команды
    (например, _poll_ai_out) и падает с TclError.
    """
    try:
        pending = root.tk.call('after', 'info')
        if pending:
            for after_id in pending:
                try:
                    root.after_cancel(after_id)
                except Exception:
                    pass
    except Exception:
        pass


@pytest.fixture(scope='session', autouse=True)
def patched_messagebox():
    """Заменяем диалоги messagebox на возврат False (как в legacy)."""
    original = {}
    for fn in ('askyesno', 'showinfo', 'showwarning', 'showerror', 'askokcancel'):
        if hasattr(gui_app.messagebox, fn):
            original[fn] = getattr(gui_app.messagebox, fn)
            setattr(gui_app.messagebox, fn, lambda *a, **k: False)
    yield
    for fn, fn_orig in original.items():
        setattr(gui_app.messagebox, fn, fn_orig)


@pytest.fixture
def isolated_ai(monkeypatch, tmp_path):
    """Изоляция _ai_in_request_files / _ai_out_files через tmp_path."""
    ai_in = tmp_path / 'AI_IN'
    ai_out = tmp_path / 'AI_OUT'
    ai_in.mkdir()
    ai_out.mkdir()

    def _fake_ai_in(self):
        try:
            if not ai_in.exists():
                return []
            return sorted(ai_in.glob('AI_REQUEST_*.md'))
        except Exception:
            return []

    def _fake_ai_out(self):
        try:
            if not ai_out.exists():
                return []
            return sorted(list(ai_out.glob('AI_RESPONSE_*.md')) +
                          list(ai_out.glob('AI_RESPONSE_*.json')))
        except Exception:
            return []

    monkeypatch.setattr(gui_app.DBIMigrationApp, '_ai_in_request_files', _fake_ai_in)
    monkeypatch.setattr(gui_app.DBIMigrationApp, '_ai_out_files', _fake_ai_out)

    yield {'ai_in': ai_in, 'ai_out': ai_out}


@pytest.fixture
def settings_backup():
    """Backup/restore SRC/settings.json через .ds140bak.

    Используется в DS_086: тесты работают с реальным settings.json,
    но восстанавливают его в teardown.
    """
    settings = SRC / 'settings.json'
    backup = settings.with_suffix('.json.ds140bak')
    if settings.exists():
        shutil.copy2(settings, backup)
    try:
        yield settings
    finally:
        if backup.exists():
            shutil.copy2(backup, settings)
            backup.unlink()


@pytest.fixture
def app(monkeypatch):
    """Tk + DBIMigrationApp с гарантированным destroy в teardown."""
    monkeypatch.setattr(gui_app.DBIMigrationApp, 'log', lambda self, *a, **k: None)
    monkeypatch.setattr(gui_app.DBIMigrationApp, '_check_log_size', lambda self: None)
    # DS_140: _poll_ai_out — 5-секундный самоперезапускающийся таймер.
    # В тестах не нужен, а после destroy Tk даёт TclError.
    monkeypatch.setattr(gui_app.DBIMigrationApp, '_poll_ai_out', lambda self: None)

    root = tk.Tk()
    try:
        root.attributes('-alpha', 0.0)
    except Exception:
        root.withdraw()

    a = gui_app.DBIMigrationApp(root)
    root.update()

    try:
        yield a
    finally:
        # DS_140: отменяем все pending after ДО destroy.
        _cancel_all_after(root)
        try:
            root.destroy()
        except Exception:
            pass