# -*- coding: utf-8 -*-
"""DS_144c: K1=скан+зеркало; K2 без повторного скана.

Тесты:
1. K1: _copy_files_to_result вызывается с only_edited=False, edited_files=None
2. K1: при _copy_res['aborted'] -> прогресс 100 + return
3. K1: при scan_aborted=True -> копирование НЕ вызывается
4. K2: без self.scan_results -> fail-fast (диалог + return)
5. K2: без self.scan_results['scanner'] -> fail-fast
6. K2: scanner.scan_directory НЕ вызывается повторно
7. K2: _copy_files_to_result НЕ вызывается
8. K2: final_results_dir == result_dir (без _v<ts>)
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PROJ = Path(__file__).resolve().parent.parent.parent
if str(PROJ) not in sys.path:
    sys.path.insert(0, str(PROJ))


# ---------- helpers ----------

def _patch_root_after_sync(app):
    """root.after(0, fn) -> fn() немедленно; возвращает фиктивный id."""
    def _after(delay, fn=None, *a, **kw):
        if fn is not None:
            try:
                fn(*a, **kw)
            except Exception:
                pass
        return "after-id"
    app.root.after = _after


def _patch_progress(app, sink):
    """Собирает все _progress_update(pct) в sink."""
    orig = app._progress_update
    def _pu(pct, force=False):
        sink.append(pct)
        try:
            orig(pct, force=force)
        except Exception:
            pass
    app._progress_update = _pu


def _setup_app(app, monkeypatch, tmp_path):
    """Общая подготовка app для тестов DS_144c."""
    _patch_root_after_sync(app)

    src_dir = tmp_path / "src"
    res_dir = tmp_path / "res"
    src_dir.mkdir(exist_ok=True)
    res_dir.mkdir(exist_ok=True)
    app.source_dir_var.set(str(src_dir))
    app.result_dir_var.set(str(res_dir))

    monkeypatch.setattr(app, "_play_result_sound", lambda *a, **kw: None)
    monkeypatch.setattr(app, "_finish_abortable_operation", lambda: None)
    monkeypatch.setattr(app, "_bot_log", lambda *a, **kw: None)
    monkeypatch.setattr(app, "_current_header_flags", lambda: {})
    monkeypatch.setattr("fixer.code_fixer.save_scan_only_log",
                        lambda *a, **kw: None)

    return src_dir, res_dir


def _fake_scanner_class(scan_calls=None):
    """Фабрика фейкового класса PLPlusScanner."""
    if scan_calls is None:
        scan_calls = []
    class _FakeScanner:
        def __init__(self, *a, **kw):
            self.issues = []
            self.issues_before_dedup = []
            self.abort_percent = None
        def scan_directory(self, log_callback=None):
            scan_calls.append(1)
            return {'files_scanned': 0, 'total_issues': 0, 'by_type': {}}
        def get_issues_by_file(self):
            return {}
    return _FakeScanner


def _fake_fixer_class(captured=None):
    """Фабрика фейкового класса PLPlusFixer."""
    if captured is None:
        captured = {}
    class _FakeFixer:
        def __init__(self, *a, **kw):
            self.flags = {}
        def fix_directory(self, scanner, final_dir, **kw):
            captured['final_dir'] = final_dir
            return []
        def save_log(self, *a, **kw):
            pass
        def save_scan_log(self, *a, **kw):
            return None
    return _FakeFixer


# ---------- 1. K1 вызывает _copy_files_to_result(only_edited=False) ----------

def test_ds144c_k1_calls_copy_with_full_mirror(app, monkeypatch, tmp_path):
    _setup_app(app, monkeypatch, tmp_path)

    calls = []
    def _fake_copy(**kw):
        calls.append(kw)
        return {'copied': 0, 'skipped': 0, 'errors': 0, 'aborted': None}
    monkeypatch.setattr(app, "_copy_files_to_result", _fake_copy)
    monkeypatch.setattr("analyzer.scanner.PLPlusScanner", _fake_scanner_class())
    monkeypatch.setattr(app, "_show_scan_result_dialog", lambda **kw: None)

    app.scan_aborted = False

    try:
        app._run_scan()
    except Exception:
        pass

    assert len(calls) >= 1, "K1 должен вызвать _copy_files_to_result"
    assert calls[0]['only_edited'] is False, "K1: only_edited должен быть False"
    assert calls[0]['edited_files'] is None, "K1: edited_files должен быть None"


# ---------- 2. K1 при aborted -> прогресс 100 + return ----------

def test_ds144c_k1_aborted_progress_100(app, monkeypatch, tmp_path):
    _setup_app(app, monkeypatch, tmp_path)

    progress = []
    _patch_progress(app, progress)

    monkeypatch.setattr(app, "_copy_files_to_result",
                        lambda **kw: {'copied': 0, 'skipped': 0, 'errors': 0,
                                      'aborted': 'Не указаны шаблоны файлов'})
    monkeypatch.setattr("analyzer.scanner.PLPlusScanner", _fake_scanner_class())
    monkeypatch.setattr(app, "_show_scan_result_dialog", lambda **kw: None)

    app.scan_aborted = False

    try:
        app._run_scan()
    except Exception:
        pass

    assert 100 in progress, f"K1: ожидался прогресс 100 при aborted, есть {progress}"


# ---------- 3. K1 при scan_aborted -> копирование НЕ вызывается ----------

def test_ds144c_k1_scan_aborted_no_copy(app, monkeypatch, tmp_path):
    _setup_app(app, monkeypatch, tmp_path)

    calls = []
    def _fake_copy(**kw):
        calls.append(kw)
        return {'copied': 0, 'skipped': 0, 'errors': 0, 'aborted': None}
    monkeypatch.setattr(app, "_copy_files_to_result", _fake_copy)
    monkeypatch.setattr("analyzer.scanner.PLPlusScanner", _fake_scanner_class())
    monkeypatch.setattr(app, "_show_scan_result_dialog", lambda **kw: None)

    app.scan_aborted = True

    try:
        app._run_scan()
    except Exception:
        pass

    assert len(calls) == 0, "K1 при scan_aborted не должен копировать"

# ---------- 4. K2 без scan_results -> fail-fast ----------

def test_ds144c_k2_no_scan_results_failfast(app, monkeypatch, tmp_path):
    _setup_app(app, monkeypatch, tmp_path)

    dialogs = []
    monkeypatch.setattr(app, "_show_copyable_dialog",
                        lambda *a, **kw: dialogs.append((a, kw)) or None)

    app.scan_results = None

    def _fail(*a, **kw):
        pytest.fail("PLPlusScanner/PLPlusFixer не должны создаваться в K2")
    monkeypatch.setattr("analyzer.scanner.PLPlusScanner", _fail)
    monkeypatch.setattr("fixer.code_fixer.PLPlusFixer", _fail)

    try:
        app._run_fix()
    except Exception:
        pass

    assert len(dialogs) >= 1, "K2 без scan_results должен показать диалог"


# ---------- 5. K2 без scan_results['scanner'] -> fail-fast ----------

def test_ds144c_k2_no_scanner_failfast(app, monkeypatch, tmp_path):
    _setup_app(app, monkeypatch, tmp_path)

    dialogs = []
    monkeypatch.setattr(app, "_show_copyable_dialog",
                        lambda *a, **kw: dialogs.append((a, kw)) or None)

    app.scan_results = {'scanner': None, 'stats': {}}

    def _fail(*a, **kw):
        pytest.fail("PLPlusScanner/PLPlusFixer не должны создаваться в K2")
    monkeypatch.setattr("analyzer.scanner.PLPlusScanner", _fail)
    monkeypatch.setattr("fixer.code_fixer.PLPlusFixer", _fail)

    try:
        app._run_fix()
    except Exception:
        pass

    assert len(dialogs) >= 1, "K2 без scanner должен показать диалог"


# ---------- 6. K2 не вызывает scan_directory ----------

def test_ds144c_k2_no_rescan(app, monkeypatch, tmp_path):
    _setup_app(app, monkeypatch, tmp_path)

    scan_calls = []
    fake_scanner = _fake_scanner_class(scan_calls)()
    app.scan_results = {'scanner': fake_scanner,
                        'stats': {'files_scanned': 1, 'total_issues': 5}}

    monkeypatch.setattr("fixer.code_fixer.PLPlusFixer", _fake_fixer_class())

    app.scan_aborted = False

    try:
        app._run_fix()
    except Exception:
        pass

    assert len(scan_calls) == 0, "K2 не должен вызывать scan_directory"

# ---------- 7. K2 не вызывает _copy_files_to_result ----------

def test_ds144c_k2_no_copy(app, monkeypatch, tmp_path):
    _setup_app(app, monkeypatch, tmp_path)

    copy_calls = []
    def _fake_copy(**kw):
        copy_calls.append(kw)
        return {'copied': 0, 'skipped': 0, 'errors': 0, 'aborted': None}
    monkeypatch.setattr(app, "_copy_files_to_result", _fake_copy)

    fake_scanner = _fake_scanner_class()()
    app.scan_results = {'scanner': fake_scanner,
                        'stats': {'files_scanned': 1, 'total_issues': 5}}

    monkeypatch.setattr("fixer.code_fixer.PLPlusFixer", _fake_fixer_class())

    app.scan_aborted = False

    try:
        app._run_fix()
    except Exception:
        pass

    assert len(copy_calls) == 0, "K2 не должен вызывать _copy_files_to_result"


# ---------- 8. K2 final_results_dir == result_dir ----------

def test_ds144c_k2_final_dir_is_result_dir(app, monkeypatch, tmp_path):
    src_dir, res_dir = _setup_app(app, monkeypatch, tmp_path)

    captured = {}
    fake_scanner = _fake_scanner_class()()
    app.scan_results = {'scanner': fake_scanner,
                        'stats': {'files_scanned': 1, 'total_issues': 5}}

    monkeypatch.setattr("fixer.code_fixer.PLPlusFixer",
                        _fake_fixer_class(captured))

    app.scan_aborted = False

    try:
        app._run_fix()
    except Exception:
        pass

    assert 'final_dir' in captured, "fix_directory должен быть вызван"
    assert str(captured['final_dir']) == str(res_dir), \
        f"final_results_dir должен быть {res_dir}, получено {captured['final_dir']}"

# ---------- 9. K1 при aborted -> флаг _k1_copy_aborted=True ----------

def test_ds144c2_k1_aborted_flag_set(app, monkeypatch, tmp_path):
    """DS_144c2: при _copy_res['aborted'] флаг _k1_copy_aborted=True,
    звук завершения — 'ошибка' (False)."""
    _setup_app(app, monkeypatch, tmp_path)

    monkeypatch.setattr(app, "_copy_files_to_result",
                        lambda **kw: {'copied': 0, 'skipped': 0, 'errors': 0,
                                      'aborted': 'Не указаны шаблоны файлов'})
    monkeypatch.setattr("analyzer.scanner.PLPlusScanner", _fake_scanner_class())
    monkeypatch.setattr(app, "_show_scan_result_dialog", lambda **kw: None)

    sounds = []
    monkeypatch.setattr(app, "_play_result_sound",
                        lambda ok, dur: sounds.append(ok))

    app.scan_aborted = False
    app._k1_copy_aborted = False

    try:
        app._run_scan()
    except Exception:
        pass

    assert getattr(app, '_k1_copy_aborted', False) is True, \
        "при aborted флаг _k1_copy_aborted должен быть True"
    assert sounds and sounds[-1] is False, \
        f"звук должен быть 'ошибка' (False), получено {sounds}"