# -*- coding: utf-8 -*-
"""
DS_086 — тесты скрытия элементов GUI (меню «Вид»).

Скрытые по умолчанию элементы реестра (workflow «1. Сканировать →
2. Исправить код → 3. В AI»):
  btn_show_sql, btn_send_koda, btn_from_ai, changelog_frame («Журнал изменений»).

НЕ ТРОГАТЬ: journal_frame («Журнал выполнения») — проверка #4.

Метод скрытия — pack_forget()/pack(), НЕ destroy: обработчики и порядок
виджетов сохраняются (#6, #11).

Запуск:  python SRC\\tests\\test_ds086_ui_hide.py
"""
import io
import json
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, SRC_DIR)

import tkinter as tk  # noqa: E402
import gui_app  # noqa: E402

# _check_log_size показывает messagebox при превышении лимита логов — в тесте
# это модальная блокировка. Заглушка: ничего не спрашиваем, ничего не удаляем.
gui_app.messagebox.askyesno = lambda *a, **k: False
gui_app.messagebox.showinfo = lambda *a, **k: None
gui_app.messagebox.showwarning = lambda *a, **k: None
gui_app.messagebox.showerror = lambda *a, **k: None

SETTINGS = os.path.join(SRC_DIR, 'settings.json')
BACKUP = SETTINGS + '.ds086bak'
HIDE_KEYS = [k for k, _ in gui_app.UI_HIDEABLE_ELEMENTS]

results = []


def check(num, desc, ok, detail=""):
    results.append((num, desc, bool(ok)))
    mark = "OK  " if ok else "FAIL"
    print(f"[{mark}] #{num:>2} {desc}" + (f"  :: {detail}" if detail else ""))


def is_hidden(app, key):
    """pack_forget применён — виджет не управляется ни одним менеджером."""
    w = getattr(app, key, None)
    return w is not None and w.winfo_manager() == ''


def is_shown(app, key):
    w = getattr(app, key, None)
    return w is not None and w.winfo_manager() == 'pack'


def journal_frame(app):
    """«Журнал выполнения»: log_text -> внутренний Frame -> LabelFrame."""
    return app.log_text.master.master


def clear_settings_key():
    """Убрать ui_hidden_elements — тест проверяет состояние ПЕРВОГО запуска."""
    if not os.path.exists(SETTINGS):
        return
    try:
        with open(SETTINGS, encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return
    if 'ui_hidden_elements' in data:
        del data['ui_hidden_elements']
        with open(SETTINGS, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    if os.path.exists(SETTINGS):
        shutil.copy2(SETTINGS, BACKUP)
    clear_settings_key()

    root = tk.Tk()
    try:
        app = gui_app.DBIMigrationApp(root)
        root.update_idletasks()

        # --- 1: GUI открывается ---
        check(1, "GUI запустился, окно существует", root.winfo_exists())

        # --- 2: workflow-элементы видны ---
        check(2, "видны «Сканировать», «Исправить код», «В AI»",
              all(is_shown(app, k) for k in ('btn_scan', 'btn_fix', 'btn_to_ai')))

        # --- 3: элементы реестра скрыты по умолчанию ---
        managers = {k: getattr(app, k).winfo_manager() for k in HIDE_KEYS}
        check(3, "скрыты btn_show_sql / btn_send_koda / btn_from_ai / changelog_frame",
              all(is_hidden(app, k) for k in HIDE_KEYS), str(managers))

        # --- 4: «Журнал выполнения» НЕ ТРОНУТ ---
        jf = journal_frame(app)
        check(4, "journal_frame «Журнал выполнения» виден и вне реестра",
              jf.winfo_manager() == 'pack'
              and str(jf.cget('text')) == 'Журнал выполнения'
              and 'journal_frame' not in HIDE_KEYS,
              f"manager={jf.winfo_manager()} text={jf.cget('text')}")

        # --- 5: высота уменьшена ---
        h_base = app._ui_base_geometry[1]
        h_now = app._window_size()[1]
        check(5, "высота окна уменьшена (h_after < h_before)", h_now < h_base,
              f"before={h_base}, after={h_now}")

        # --- 6: обработчики сохранены (widget жив, command на месте) ---
        det6 = []
        for key, _label in gui_app.UI_HIDEABLE_ELEMENTS:
            w = getattr(app, key, None)
            if w is None or not w.winfo_exists():
                det6.append(f"{key}: widget мёртв")
            elif key != 'changelog_frame' and not str(w.cget('command')):
                det6.append(f"{key}: command пуст")
        check(6, "winfo_exists() + command сохранены у всех скрытых", not det6,
              "; ".join(det6) or "all ok")

        # --- 7: меню «Вид» — 4 чекбокса + 2 команды ---
        vm = getattr(app, 'view_menu', None)
        n_check = n_cmd = 0
        if vm is not None:
            # index('end') — номер последнего пункта, поэтому +1 (скан с 0).
            for i in range((vm.index('end') or 0) + 1):
                t = vm.type(i)
                n_check += t == 'checkbutton'
                n_cmd += t == 'command'
        check(7, "меню «Вид»: 4 checkbutton + 2 команды",
              vm is not None and n_check == 4 and n_cmd == 2,
              f"checkbutton={n_check} command={n_cmd}")

        # --- 8: «Показать все» — все видны, высота восстановлена ---
        app.set_all_ui_elements(True)
        root.update_idletasks()
        h_show = app._window_size()[1]
        check(8, "«Показать все элементы» → все видны, высота = базовая",
              all(is_shown(app, k) for k in HIDE_KEYS) and h_show == h_base,
              f"h={h_show} base={h_base}")

        # --- 9: «Скрыть все» — все скрыты, высота меньше базовой ---
        app.set_all_ui_elements(False)
        root.update_idletasks()
        h_hide = app._window_size()[1]
        check(9, "«Скрыть все элементы» → все скрыты, высота < базовой",
              all(is_hidden(app, k) for k in HIDE_KEYS) and h_hide < h_base,
              f"h={h_hide}")

        # --- 10: индивидуальное переключение одного элемента ---
        app.ui_visible_vars['changelog_frame'].set(True)
        app.toggle_ui_element('changelog_frame')
        root.update_idletasks()
        check(10, "toggle changelog_frame → он виден, кнопки скрыты",
              is_shown(app, 'changelog_frame') and is_hidden(app, 'btn_from_ai'),
              f"changelog={app.changelog_frame.winfo_manager()!r} "
              f"from_ai={app.btn_from_ai.winfo_manager()!r}")

        # --- 11: порядок кнопок в панели сохранён после show/hide циклов ---
        for visible in (True, False, True):
            app.set_all_ui_elements(visible)
        root.update_idletasks()
        names = [w.winfo_name() for w in app.control_frame.winfo_children()]

        def idx(k):
            return names.index(getattr(app, k).winfo_name())

        check(11, "порядок кнопок восстановлен (От AI < Рубрикатор, SQL < Koda)",
              idx('btn_from_ai') < idx('btn_rubricator')
              and idx('btn_show_sql') < idx('btn_send_koda'),
              f"ai={idx('btn_from_ai')} rub={idx('btn_rubricator')} "
              f"sql={idx('btn_show_sql')} koda={idx('btn_send_koda')}")

        # --- 12: нет дрейфа высоты после нескольких переключений ---
        check(12, "высота стабильна после 3 переключений (нет накопления)",
              app._window_size()[1] == h_base, f"h={app._window_size()[1]}")

        # --- 13: состояние записано в settings.json ---
        app.set_all_ui_elements(False)
        root.update_idletasks()
        with open(SETTINGS, encoding='utf-8') as f:
            saved = json.load(f).get('ui_hidden_elements')
        check(13, "settings.json → ui_hidden_elements содержит 4 ключа",
              isinstance(saved, list) and sorted(saved) == sorted(HIDE_KEYS), str(saved))

        # --- 14: восстановление из settings.json (пустой список = всё видно) ---
        app._restore_ui_visibility([])
        root.update_idletasks()
        check(14, "_restore_ui_visibility([]) → все элементы видны",
              all(is_shown(app, k) for k in HIDE_KEYS))

        # --- 15: «Журнал выполнения» жив после всех переключений ---
        check(15, "log_text цел, journal_frame не в реестре скрытия",
              app.log_text.winfo_exists() and 'journal_frame' not in HIDE_KEYS)
    finally:
        try:
            root.destroy()
        except Exception:
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
