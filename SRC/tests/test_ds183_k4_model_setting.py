# -*- coding: utf-8 -*-
"""DS_183 — тесты 1–5: K4 модель (3b/7b) в GUI + settings.json + argv воркера.

Без запуска GUI-цикла и без Ollama/сети.
"""
import inspect
import io
import json
import os
import shutil
import sys
import tempfile

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)

import gui_app  # noqa: E402

SETTINGS = os.path.join(SRC, "settings.json")
BACKUP = SETTINGS + ".ds183bak"

results = []


def check(num, desc, ok, detail=""):
    results.append((num, desc, bool(ok)))
    print(f"[{'OK  ' if ok else 'FAIL'}] #{num:>2} {desc}" + (f"  :: {detail}" if detail else ""))


def test_t1_settings_file_default():
    """В settings.json есть k4_model, допустимое значение по умолчанию (3b)."""
    with io.open(SETTINGS, "r", encoding="utf-8") as f:
        data = json.load(f)
    ok = "k4_model" in data and data["k4_model"] in ("qwen2.5-coder:3b", "qwen2.5-coder:7b")
    check(1, "settings.json: k4_model присутствует, значение 3b/7b", ok, data.get("k4_model"))
    assert ok, f"k4_model={data.get('k4_model')}"


def test_t2_default_3b():
    """Если k4_model нет в файле — load_settings ставит 3b (проверяем через исходник)."""
    src = inspect.getsource(gui_app.DBIMigrationApp.load_settings)
    ok = "k4_model" in src and "qwen2.5-coder:3b" in src
    check(2, "load_settings: default qwen2.5-coder:3b + валидация", ok)
    assert ok, "load_settings: default 3b/валидация не найдены"


def test_t3_save_settings_roundtrip():
    """save_settings пишет k4_model; load_settings читает его обратно."""
    if not os.path.exists(SETTINGS):
        check(3, "save/load roundtrip", False, "settings.json отсутствует")
        assert False, "settings.json отсутствует"
    try:
        shutil.copy2(SETTINGS, BACKUP)
    except Exception as e:
        check(3, "save/load roundtrip", False, f"backup failed: {e}")
        raise
    try:
        try:
            root.update_idletasks()  # проглотить .after до destroy
        except Exception:
            pass
        import tkinter as tk
        gui_app.DBIMigrationApp._check_log_size = lambda self: None
        _orig_warn = gui_app.messagebox.showwarning
        gui_app.messagebox.showwarning = lambda *a, **k: None
        root = tk.Tk()
        try:
            try:
                root.update_idletasks()  # проглотить .after до destroy
            except Exception:
                pass
            root.attributes("-alpha", 0.0)
        except Exception:
            root.withdraw()
        try:
            try:
                root.update_idletasks()  # проглотить .after до destroy
            except Exception:
                pass
            app = gui_app.DBIMigrationApp(root)
            root.update()
            app.k4_model_var.set("qwen2.5-coder:7b")
            app.save_settings()
            with io.open(SETTINGS, "r", encoding="utf-8") as f:
                data = json.load(f)
            ok_save = data.get("k4_model") == "qwen2.5-coder:7b"
            # load: сброс var и повторная загрузка
            app.k4_model_var.set("qwen2.5-coder:3b")
            app.load_settings()
            ok_load = app.k4_model_var.get() == "qwen2.5-coder:7b"
            check(3, "save_settings -> k4_model=7b; load_settings -> 7b",
                  ok_save and ok_load,
                  f"save={data.get('k4_model')} load={app.k4_model_var.get()}")
            try:
                try:
                    root.update_idletasks()  # проглотить .after до destroy
                except Exception:
                    pass
                try:
                    try:
                        root.update_idletasks()  # проглотить .after до destroy
                    except Exception:
                        pass
                    try:
                        app.on_close()
                    except Exception:
                        try:
                            root.destroy()
                        except Exception:
                            pass
                except Exception:
                    pass  # destroy in try: Tk .after may fire after widgets destroyed
            except Exception:
                pass
            assert ok_save and ok_load, f"save={data.get('k4_model')} load={app.k4_model_var.get()}"
        finally:
            gui_app.messagebox.showwarning = _orig_warn
    finally:
        if not os.path.exists(BACKUP):
            raise RuntimeError("DS_186: BACKUP missing in t3 finally")
        shutil.copy2(BACKUP, SETTINGS)
        try:
            try:
                root.update_idletasks()  # проглотить .after до destroy
            except Exception:
                pass
            os.remove(BACKUP)
        except Exception:
            pass


def test_t4_load_7b_does_not_show_dialog():
    """load_settings с 7b: log(warning), но showwarning НЕ вызывается."""
    if not os.path.exists(SETTINGS):
        check(4, "load 7b без диалога", False, "settings.json отсутствует")
        assert False, "settings.json отсутствует"
    try:
        shutil.copy2(SETTINGS, BACKUP)
    except Exception as e:
        check(4, "load 7b", False, f"backup failed: {e}")
        raise
    calls = {"warn": 0}
    _orig_warn = gui_app.messagebox.showwarning
    gui_app.messagebox.showwarning = lambda *a, **k: calls.__setitem__("warn", calls["warn"] + 1) or False
    try:
        try:
            root.update_idletasks()  # проглотить .after до destroy
        except Exception:
            pass
        with io.open(SETTINGS, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["k4_model"] = "qwen2.5-coder:7b"
        with io.open(SETTINGS, "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
        import tkinter as tk
        gui_app.DBIMigrationApp._check_log_size = lambda self: None
        root = tk.Tk()
        try:
            try:
                root.update_idletasks()  # проглотить .after до destroy
            except Exception:
                pass
            root.attributes("-alpha", 0.0)
        except Exception:
            root.withdraw()
        try:
            try:
                root.update_idletasks()  # проглотить .after до destroy
            except Exception:
                pass
            app = gui_app.DBIMigrationApp(root)
            root.update()
            app.load_settings()
            ok = (app.k4_model_var.get() == "qwen2.5-coder:7b" and calls["warn"] == 0)
            check(4, "load_settings 7b: var=7b, showwarning НЕ вызван", ok,
                  f"var={app.k4_model_var.get()} warn={calls['warn']}")
            try:
                try:
                    root.update_idletasks()  # проглотить .after до destroy
                except Exception:
                    pass
                try:
                    try:
                        root.update_idletasks()  # проглотить .after до destroy
                    except Exception:
                        pass
                    try:
                        app.on_close()
                    except Exception:
                        try:
                            root.destroy()
                        except Exception:
                            pass
                except Exception:
                    pass  # destroy in try: Tk .after may fire after widgets destroyed
            except Exception:
                pass
            assert ok, f"var={app.k4_model_var.get()} warn={calls['warn']}"
        finally:
            pass
    finally:
        gui_app.messagebox.showwarning = _orig_warn
        if not os.path.exists(BACKUP):
            raise RuntimeError("DS_186: BACKUP missing in t4 finally")
        shutil.copy2(BACKUP, SETTINGS)
        try:
            try:
                root.update_idletasks()  # проглотить .after до destroy
            except Exception:
                pass
            os.remove(BACKUP)
        except Exception:
            pass


def test_t5_argv_has_model():
    """_run_ai_cycle / _run_fix / start_ai_cycle: argv содержит --model + k4_model_var.get()."""
    import inspect
    cands = []
    for name in ("_run_ai_cycle", "_run_fix", "start_ai_cycle"):
        fn = getattr(gui_app.DBIMigrationApp, name, None)
        if fn is None:
            continue
        try:
            try:
                root.update_idletasks()  # проглотить .after до destroy
            except Exception:
                pass
            cands.append((name, inspect.getsource(fn)))
        except Exception as e:
            print("  [warn] getsource({}): {}".format(name, e))
    ok = False
    detail = ""
    for name, s in cands:
        has_flag = ("'--model'" in s) or ('"--model"' in s)
        has_var  = "k4_model_var.get()" in s
        if has_flag and has_var:
            ok = True
            detail = "found in " + name
            break
    if not ok:
        names = [n for n, _ in cands]
        detail = "not found in " + ",".join(names) if names else "no candidates"
    check(5, "_run_ai_cycle/_run_fix/start_ai_cycle argv: --model + k4_model_var.get()", ok, detail)
    assert ok, detail


def test_t6_local_override():
    r"""DS_183b: local_settings.apply_local_k4_override читает %APPDATA%\TO_DBI\<HOST>.local.json."""
    import tempfile
    from pathlib import Path
    import local_settings as ls
    common = "qwen2.5-coder:3b"
    # 1) нет файла -> fallback на common
    with tempfile.TemporaryDirectory() as td:
        got = ls.apply_local_k4_override(common, computer_name="HOST_A", appdata=td)
        assert got == common, f"no-file: got={got}"
    # 2) файл с k4_model=7b -> 7b
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "TO_DBI"
        d.mkdir(parents=True, exist_ok=True)
        (d / "HOST_A.local.json").write_text('{"k4_model": "qwen2.5-coder:7b"}', encoding="utf-8")
        got = ls.apply_local_k4_override(common, computer_name="HOST_A", appdata=td)
        assert got == "qwen2.5-coder:7b", f"file-7b: got={got}"
    # 3) другой хост -> fallback (изоляция per-host)
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "TO_DBI"
        d.mkdir(parents=True, exist_ok=True)
        (d / "HOST_A.local.json").write_text('{"k4_model": "qwen2.5-coder:7b"}', encoding="utf-8")
        got = ls.apply_local_k4_override(common, computer_name="HOST_B", appdata=td)
        assert got == common, f"other-host: got={got}"
    # 4) битый JSON -> fallback
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "TO_DBI"
        d.mkdir(parents=True, exist_ok=True)
        (d / "HOST_A.local.json").write_text('{not json}', encoding="utf-8")
        got = ls.apply_local_k4_override(common, computer_name="HOST_A", appdata=td)
        assert got == common, f"broken-json: got={got}"
    # 5) пустой k4_model -> fallback
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "TO_DBI"
        d.mkdir(parents=True, exist_ok=True)
        (d / "HOST_A.local.json").write_text('{"k4_model": ""}', encoding="utf-8")
        got = ls.apply_local_k4_override(common, computer_name="HOST_A", appdata=td)
        assert got == common, f"empty-model: got={got}"
    check(6, "DS_183b: per-host override (5 сценариев)", True, "ok")


def _run(fn):
    """Standalone-раннер: ловит AssertionError, возвращает bool."""
    try:
        fn()
        return True
    except AssertionError as e:
        print("  [assert]", e)
        return False


def main():
    t1 = _run(test_t1_settings_file_default)
    t2 = _run(test_t2_default_3b)
    t3 = _run(test_t3_save_settings_roundtrip)
    t4 = _run(test_t4_load_7b_does_not_show_dialog)
    t5 = _run(test_t5_argv_has_model)
    t6 = _run(test_t6_local_override)
    ok_all = all([t1, t2, t3, t4, t5, t6])
    print("\nDS_183 SUMMARY:", "OK" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
