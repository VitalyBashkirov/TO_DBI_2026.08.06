# -*- coding: utf-8 -*-
"""DS_087 — тесты 1–18 (реальный Tk, без mainloop).

Покрытие по ТЗ §3:
 1 Переименование           2 Tooltip «3. В Ai»
 3 Активация старт          4 Активация после скана
 5 Активация после фикса    6 Изменение бокса 1
 7 Изменение бокса 2        8 Скрытие кнопок
 9 Размер 1600×900         10 Fallback (малый экран)
11 Центрирование           12 Кнопки [...] видны
13 Скроллбары бокса 2      14 Бокс 3: правая группа сдвинута
15 Верт. скроллбар журнала 16 Копирование Entry
17 Копирование Text-лог    18 Регресс DS_086 (реестр «Вид» = 6)
"""
import io
import os
import shutil
import sys
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)

import tkinter as tk  # noqa: E402
import gui_app  # noqa: E402

# Без модалок.
gui_app.DBIMigrationApp._check_log_size = lambda self: None
for _fn in ('askyesno', 'showinfo', 'showwarning', 'showerror'):
    setattr(gui_app.messagebox, _fn, lambda *a, **k: False)

SETTINGS = os.path.join(SRC, 'settings.json')
BACKUP = SETTINGS + '.ds087bak'

results = []


def check(num, desc, ok, detail=""):
    results.append((num, desc, bool(ok)))
    print(f"[{'OK  ' if ok else 'FAIL'}] #{num:>2} {desc}" + (f"  :: {detail}" if detail else ""))


def active_btns(app):
    return [n for n in ('btn_scan', 'btn_fix', 'btn_to_ai')
            if 'disabled' not in getattr(app, n).state()]


def main():
    if os.path.exists(SETTINGS):
        shutil.copy2(SETTINGS, BACKUP)
    tmp_src = tempfile.mkdtemp(prefix='ds087_src_')
    tmp_dst = tempfile.mkdtemp(prefix='ds087_dst_')
    ai_in = os.path.join(os.path.dirname(SRC), 'EXCHANGE', 'AI_IN')
    ai_req = os.path.join(ai_in, 'AI_REQUEST_ds087_test.md')
    created_req = False
    try:
        root = tk.Tk()
        # Прозрачное, но «реализованное» окно — layout считается, как на экране.
        try:
            root.attributes('-alpha', 0.0)
        except Exception:
            root.withdraw()
        app = gui_app.DBIMigrationApp(root)
        root.update()

        # 1. Переименование
        t = [app.btn_scan.cget('text'), app.btn_fix.cget('text'), app.btn_to_ai.cget('text')]
        check(1, "Переименование кнопок 1/2/3",
              t == ['1. Сканировать', '2. Исправить код', '3. В Ai'], str(t))

        # 2. Tooltip «3. В Ai»
        tip = getattr(app, '_tooltip_to_ai', None)
        check(2, "Tooltip «3. В Ai»",
              tip is not None and tip.text ==
              "Использовать LLM для корректировки ошибок, требующих Ai-анализа.",
              tip.text if tip else 'None')

        # 3. Активация на старте: ровно одна активна и жирная
        app.source_dir_var.set(tmp_src)
        app.result_dir_var.set(tmp_dst)
        app.file_pattern_var.set('*.plp')
        app._update_workflow_buttons()
        act = active_btns(app)
        bold = str(app.btn_scan.cget('style'))
        check(3, "Активация старт: только «1. Сканировать» (жирная)",
              act == ['btn_scan'] and 'WorkflowActive' in bold,
              f"active={act} style={bold!r}")

        # 4. После скана + файлы в КР → «2. Исправить код»
        open(os.path.join(tmp_dst, 'fixed.plp'), 'w').write('x')
        app.scan_results = {'fix_done': False}
        app._update_workflow_buttons()
        check(4, "Активация после скана: только «2. Исправить код»",
              active_btns(app) == ['btn_fix'] and
              'WorkflowActive' in str(app.btn_fix.cget('style')),
              str(active_btns(app)))

        # 5. После фикса + AI_IN запрос → «3. В Ai»
        if not os.path.isdir(ai_in):
            os.makedirs(ai_in)
        if not os.path.exists(ai_req):
            open(ai_req, 'w').write('тест')
            created_req = True
        app.scan_results = {'fix_done': True}
        app._update_workflow_buttons()
        check(5, "Активация после фикса: только «3. В Ai»",
              active_btns(app) == ['btn_to_ai'] and
              'WorkflowActive' in str(app.btn_to_ai.cget('style')),
              str(active_btns(app)))

        # 6. Изменение бокса 1 → пересчёт (сбрасываем состояние скана/фикса)
        app.scan_results = None
        app.source_dir_var.set('')
        a_empty = active_btns(app)
        app.source_dir_var.set(tmp_src)
        a_restored = active_btns(app)
        check(6, "Изменение бокса 1 → пересчёт активации",
              a_empty == [] and a_restored == ['btn_scan'],
              f"empty={a_empty} restored={a_restored}")

        # 7. Изменение бокса 2 (рубрикатор) → пересчёт
        app.scan_results = None
        app.source_dir_var.set(tmp_src)
        any_before = active_btns(app)
        for var in app.selected_rules.values():
            var.set(False)
        app._update_workflow_buttons()
        a_norules = active_btns(app)
        first = next(iter(app.selected_rules.values()))
        first.set(True)
        app._update_workflow_buttons()
        a_rules = active_btns(app)
        check(7, "Изменение бокса 2 → пересчёт активации",
              a_norules == [] and a_rules == ['btn_scan'],
              f"before={any_before} norules={a_norules} withrule={a_rules}")

        # 8. Скрытие btn_get_answer / btn_history_rk (факт. имена)
        m1 = app.btn_receive_koda.winfo_manager()
        m2 = app.btn_result_history.winfo_manager()
        check(8, "Скрытие «Получить ответ»/«История РК»",
              m1 == '' and m2 == '', f"managers: {m1!r}/{m2!r}")

        # 9/10/11. Размер, fallback, центрирование.
        # Базовая геометрия (_ui_base_geometry) = 1600×900 либо экран.
        # DS_086 уменьшает ФАКТИЧЕСКУЮ высоту на высоту скрытых блоков
        # (по умолчанию скрыт «Журнал изменений»), поэтому проверяем:
        #   width == base_width, height == base_height − скрытые блоки.
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        exp_w, exp_h = (1600, 900) if (sw >= 1600 and sh >= 900) else (sw, sh)
        base = getattr(app, '_ui_base_geometry', None)
        geo = root.geometry()
        rw, rh = root.winfo_width(), root.winfo_height()
        hidden = sum(app._ui_height_delta.get(k, 0)
                     for k, v in app.ui_visible_vars.items() if not v.get())
        exp_rh = max(400, exp_h - hidden)
        exp_x, exp_y = (sw - exp_w) // 2, (sh - exp_h) // 2
        check(9, f"Базовая геометрия {exp_w}×{exp_h}; ширина окна {exp_w}",
              base == (exp_w, exp_h) and rw == exp_w,
              f"base={base} winfo={rw}x{rh} geo={geo}")
        fallback = (sw < 1600 or sh < 900)
        check(10, "Fallback: малый экран → во весь экран (ширина)"
              if fallback else "Экран ≥1600×900 → базовая ширина",
              rw == exp_w, f"screen={sw}x{sh} winfo={rw}x{rh}")
        check(11, "Центрирование: winfo_x/y = (screen−W/H)/2",
              root.winfo_x() == exp_x and root.winfo_y() == exp_y,
              f"x={root.winfo_x()} y={root.winfo_y()} exp=({exp_x},{exp_y})")

        # 12. Кнопки [...] видны
        bs, br = app.btn_browse_source, app.btn_browse_result
        win_right = root.winfo_rootx() + rw
        ok12 = (bs.winfo_ismapped() and br.winfo_ismapped()
                and bs.winfo_rootx() + bs.winfo_width() <= win_right
                and br.winfo_rootx() + br.winfo_width() <= win_right)
        check(12, "Кнопки [...] видны и не за краем", bool(ok12),
              f"bs={bs.winfo_rootx()+bs.winfo_width()} br={br.winfo_rootx()+br.winfo_width()} right={win_right}")

        # 13. Скроллбары бокса 2 (таблица) видны
        ty, tx = app.tree_scroll_y, app.tree_scroll_x
        check(13, "Скроллбары бокса 2 (верт.+гориз.) видны",
              bool(ty.winfo_ismapped()) and bool(tx.winfo_ismapped())
              and app.rules_tree.column('name', 'stretch') in (0, '0', False),
              f"y={ty.winfo_ismapped()} x={tx.winfo_ismapped()} stretch={app.rules_tree.column('name','stretch')}")

        # 14. Бокс 3: правая группа сдвинута от правого края
        of = app.options_frame
        of.update_idletasks()
        e = app.report_stats_entry
        gap = of.winfo_width() - (e.winfo_x() + e.winfo_width())
        check(14, "Бокс 3: «Топ-файлов» не у правого края",
              gap > 40, f"frame_w={of.winfo_width()} entry_right={e.winfo_x()+e.winfo_width()} gap={gap}")

        # 15. Верт. скроллбар «Журнала выполнения» виден
        ly = app.log_scroll_y
        check(15, "Верт. скроллбар «Журнала выполнения» виден",
              bool(ly.winfo_ismapped()), f"mapped={ly.winfo_ismapped()}")

        # 16. Копирование Entry (Ctrl+C)
        ok16, det16 = False, ""
        try:
            root.clipboard_clear()
            root.clipboard_append('')
            e = app.source_entry
            e.delete(0, 'end')
            e.insert(0, 'COPY_ENTRY_DS087')
            e.select_range(0, 'end')
            e.focus_force()
            root.update()
            e.event_generate('<<Copy>>')
            root.update()
            val = root.clipboard_get()
            ok16 = 'COPY_ENTRY_DS087' in val
            det16 = repr(val[:40])
        except Exception as exc:
            det16 = f"exc: {exc}"
        check(16, "Копирование Entry (Ctrl+C) работает", ok16, det16)

        # 17. Копирование Text-лога (Ctrl+C)
        ok17, det17 = False, ""
        try:
            app.log_text.delete('1.0', 'end')
            app.log_text.insert('1.0', 'COPY_TEXT_DS087')
            root.clipboard_clear()
            root.clipboard_append('')
            app.log_text.tag_add('sel', '1.0', '1.end')
            app.log_text.focus_force()
            root.update()
            app.log_text.event_generate('<<Copy>>')
            root.update()
            val = root.clipboard_get()
            ok17 = 'COPY_TEXT_DS087' in val
            det17 = repr(val[:40])
        except Exception as exc:
            det17 = f"exc: {exc}"
        check(17, "Копирование Text-лога (Ctrl+C) работает", ok17, det17)

        # 18. Регресс DS_086: реестр «Вид» = 6 checkbutton
        vm = app.view_menu
        n_check = 0
        for i in range((vm.index('end') or 0) + 1):
            n_check += vm.type(i) == 'checkbutton'
        check(18, "Регресс DS_086: меню «Вид» = 6 checkbutton",
              n_check == 6, f"n={n_check}")

        root.destroy()
    finally:
        shutil.rmtree(tmp_src, ignore_errors=True)
        shutil.rmtree(tmp_dst, ignore_errors=True)
        if created_req:
            try:
                os.remove(ai_req)
            except OSError:
                pass
        if os.path.exists(BACKUP):
            shutil.copy2(BACKUP, SETTINGS)
            os.remove(BACKUP)

    failed = [r for r in results if not r[2]]
    print("-" * 60)
    print(f"ИТОГ: {len(results) - len(failed)}/{len(results)} PASSED")
    for num, desc, _ok in failed:
        print(f"  FAIL #{num}: {desc}")
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
