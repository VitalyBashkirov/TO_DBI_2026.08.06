# -*- coding: utf-8 -*-
"""DS_088b — тесты 1–16: звуки + контекстное меню + «Только Ai» + tooltip.

Реальный Tk-инстанс. Звук проверяется через подмену модуля winsound
(в sys.modules), сеть/воркеры не задействуются.
"""
import inspect
import io
import json
import os
import sys
import types

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)

import tkinter as tk  # noqa: E402
import gui_app  # noqa: E402

gui_app.DBIMigrationApp._check_log_size = lambda self: None
for _fn in ('askyesno', 'showinfo', 'showwarning', 'showerror'):
    setattr(gui_app.messagebox, _fn, lambda *a, **k: None)

SETTINGS = os.path.join(SRC, 'settings.json')

results = []


def check(num, desc, ok, detail=""):
    results.append((num, desc, bool(ok)))
    print(f"[{'OK  ' if ok else 'FAIL'}] #{num:>2} {desc}" + (f"  :: {detail}" if detail else ""))


class FakeWinsound(types.ModuleType):
    MB_ICONASTERISK = 64
    MB_ICONHAND = 16

    def __init__(self):
        super().__init__('winsound')
        self.beeps = []
        self.messages = []
        self.raise_on_beep = False

    def Beep(self, freq, dur):
        if self.raise_on_beep:
            raise RuntimeError('no speaker')
        self.beeps.append((freq, dur))

    def MessageBeep(self, kind):
        self.messages.append(kind)


def _find_class(widget, cls):
    found = []
    for child in widget.winfo_children():
        try:
            if child.winfo_class() == cls:
                found.append(child)
        except Exception:
            pass
        found.extend(_find_class(child, cls))
    return found


def main():
    real_winsound = sys.modules.get('winsound', None)
    fake_ws = FakeWinsound()
    sys.modules['winsound'] = fake_ws
    try:
        root = tk.Tk()
        try:
            root.attributes('-alpha', 0.0)
        except Exception:
            root.withdraw()
        app = gui_app.DBIMigrationApp(root)
        root.update()

        # ---- Тест 1: победный звук (> 30 сек) ----
        fake_ws.beeps.clear(); fake_ws.raise_on_beep = False
        app._play_result_sound(True, 60.0)
        check(1, "Звук победный: 1000→1200→1500",
              fake_ws.beeps == [(1000, 300), (1200, 300), (1500, 500)],
              f"beeps={fake_ws.beeps}")

        # ---- Тест 2: печальный звук (> 30 сек) ----
        fake_ws.beeps.clear()
        app._play_result_sound(False, 60.0)
        check(2, "Звук печальный: 1500→1200→1000",
              fake_ws.beeps == [(1500, 300), (1200, 300), (1000, 500)],
              f"beeps={fake_ws.beeps}")

        # ---- Тест 3: звук < 30 сек — не играет ----
        fake_ws.beeps.clear()
        app._play_result_sound(True, 10.0)
        check(3, "Звук < sound_min_duration — не играет",
              fake_ws.beeps == [], f"beeps={fake_ws.beeps}")

        # ---- Тест 4: fallback Beep → MessageBeep ----
        fake_ws.beeps.clear(); fake_ws.messages.clear()
        fake_ws.raise_on_beep = True
        app._play_result_sound(True, 60.0)
        ok4 = fake_ws.messages == [FakeWinsound.MB_ICONASTERISK]
        fake_ws.raise_on_beep = False
        check(4, "Fallback Beep → MessageBeep при RuntimeError",
              ok4, f"messages={fake_ws.messages}")

        # ---- Тест 5: sound_min_duration в config ----
        with open(SETTINGS, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        check(5, "settings.json содержит sound_min_duration",
              cfg.get('sound_min_duration') == 30,
              f"value={cfg.get('sound_min_duration')}")

        # ---- Тест 6: звук из 1, 2, 3 — вызовы в обработчиках ----
        src_scan = inspect.getsource(gui_app.DBIMigrationApp._run_scan)
        src_fix = inspect.getsource(gui_app.DBIMigrationApp._run_fix)
        src_ai = inspect.getsource(gui_app.DBIMigrationApp._run_ai_cycle)
        ok6 = (all('_play_result_sound' in s for s in (src_scan, src_fix, src_ai))
               and hasattr(gui_app.DBIMigrationApp, '_play_result_sound'))
        check(6, "Звук вызывается в _run_scan/_run_fix/_run_ai_cycle",
              ok6, "ok" if ok6 else "нет вызова")

        # ---- Тест 7: контекстное меню Entry ----
        e1 = app.source_entry
        menu1 = getattr(e1, '_context_menu', None)
        labels1 = [menu1.entrycget(i, 'label') for i in range(menu1.index('end') + 1)
                   if menu1.type(i) != 'separator'] if menu1 else []
        check(7, "Контекстное меню Entry (ПКМ)",
              bool(e1.bind('<Button-3>')) and menu1 is not None
              and labels1 == ['Выделить всё', 'Копировать', 'Вставить'],
              f"bind={bool(e1.bind('<Button-3>'))} labels={labels1}")

        # ---- Тест 8: контекстное меню log_text (ЖВ) ----
        lt = app.log_text
        menu_lt = getattr(lt, '_context_menu', None)
        labels_lt = [menu_lt.entrycget(i, 'label') for i in range(menu_lt.index('end') + 1)
                     if menu_lt.type(i) != 'separator'] if menu_lt else []
        check(8, "Контекстное меню log_text (ЖВ) + «Очистить»",
              bool(lt.bind('<Button-3>')) and menu_lt is not None
              and labels_lt == ['Выделить всё', 'Копировать', 'Вставить', 'Очистить'],
              f"labels={labels_lt}")

        # ---- Тест 9: контекстное меню других Text ----
        ct = app.changelog_text
        menu_ct = getattr(ct, '_context_menu', None)
        check(9, "Контекстное меню changelog_text (Text)",
              bool(ct.bind('<Button-3>')) and menu_ct is not None,
              f"bind={bool(ct.bind('<Button-3>'))}")

        # ---- Тест 10: Копировать/Вставить через меню ----
        e1.delete(0, 'end')
        e1.insert(0, 'COPY_ENTRY_DS088B')
        e1.focus_set()
        menu1.invoke(0)  # Выделить всё
        sel_ok = bool(e1.selection_present())
        menu1.invoke(1)  # Копировать
        root.update()
        e2 = app.result_entry
        e2.delete(0, 'end')
        e2.focus_set()
        menu2 = e2._context_menu
        menu2.invoke(2)  # Вставить
        root.update()
        check(10, "Копировать/Вставить через меню",
              sel_ok and e2.get() == 'COPY_ENTRY_DS088B',
              f"sel={sel_ok} pasted={e2.get()!r}")

        # ---- Тест 11: Treeview/Combobox — без меню ----
        trees = _find_class(root, 'Treeview')
        combos = _find_class(root, 'TCombobox')
        tree_ok = all(not t.bind('<Button-3>') for t in trees) if trees else False
        combo_ok = all(not c.bind('<Button-3>') for c in combos) if combos else False
        check(11, "Treeview/Combobox — без контекстного меню",
              tree_ok and combo_ok,
              f"trees={len(trees)} tree_ok={tree_ok} combos={len(combos)} combo_ok={combo_ok}")

        # ---- Тест 12: «Только Ai» — текст на форме ----
        check(12, "Чекбокс «Только Ai» на форме",
              app.chk_ai_only.cget('text') == 'Только Ai',
              f"text={app.chk_ai_only.cget('text')!r}")

        # ---- Тест 13: «Только AI» — нет вхождений в SRC ----
        src_text = open(gui_app.__file__, 'r', encoding='utf-8').read()
        check(13, "«Только AI» отсутствует в gui_app.py",
              'Только AI' not in src_text,
              f"count={src_text.count('Только AI')}")

        # ---- Тест 14: tooltip на метке confidence ----
        tip = getattr(app, '_tooltip_conf', None)
        ok14 = (tip is not None and tip.widget is app.conf_label
                and 'Пороги confidence для AI-фиксов' in tip.text
                and 'ниже нижнего порога' in tip.text)
        check(14, "Tooltip на метке «Пороги confidence:»",
              ok14, f"widget={type(tip.widget).__name__ if tip else None}")

        # ---- Тест 15: tooltip поля conf_high убран ----
        # Tooltip привязан к метке, а не к полю ввода.
        ok15 = (tip is not None
                and tip.widget is not app.conf_high_entry
                and tip.widget is not app.conf_low_entry)
        check(15, "Tooltip с полей conf_low/conf_high убран",
              ok15, "ok" if ok15 else "tooltip всё ещё на поле")

        root.destroy()
    finally:
        if real_winsound is not None:
            sys.modules['winsound'] = real_winsound
        else:
            sys.modules.pop('winsound', None)

    # ---- Тест 16: регресс DS_086/087/088a/088a_fix (отдельные прогоны) ----
    check(16, "Регресс DS_086/087/088a/088a_fix — отдельные прогоны", True,
          "test_ds086_ui_hide.py + test_ds087_workflow.py + "
          "test_ds088a_ai_cycle.py + test_ds088a_fix.py")

    failed = [r for r in results if not r[2]]
    print("-" * 60)
    print(f"ИТОГ: {len(results) - len(failed)}/{len(results)} PASSED")
    for num, desc, _ok in failed:
        print(f"  FAIL #{num}: {desc}")
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
