# -*- coding: utf-8 -*-
"""DS_086 (pytest-версия) — тесты скрытия элементов GUI (меню «Вид»).

Скрытые по умолчанию элементы реестра (workflow «1. Сканировать →
2. Исправить код → 3. В AI»):
  btn_show_sql, btn_send_koda, changelog_frame, btn_receive_koda, btn_result_history.
  (btn_from_ai видим по DS_134 — вне реестра скрытия.)

НЕ ТРОГАТЬ: journal_frame («Журнал выполнения») — проверка #4.

Метод скрытия — pack_forget()/pack(), НЕ destroy: обработчики и порядок
виджетов сохраняются (#6, #11).

Мигрировано с legacy test_ds086_ui_hide.py (15 проверок).
"""
import json

import pytest

import gui_app


# ---------- константы (перенос из legacy) ----------
HIDE_KEYS = [k for k, _ in gui_app.UI_HIDEABLE_ELEMENTS]


# ---------- хелперы (перенос из legacy) ----------
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


def clear_settings_key(settings_path):
    """Убрать ui_hidden_elements — тест проверяет состояние ПЕРВОГО запуска."""
    if not settings_path.exists():
        return
    try:
        with open(settings_path, encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return
    if 'ui_hidden_elements' in data:
        del data['ui_hidden_elements']
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


@pytest.fixture
def clean_app(settings_backup, app):
    """app + очистка ui_hidden_elements в settings.json ПЕРЕД созданием app.

    Порядок важен: app создаётся с уже очищенным settings.json,
    чтобы имитировать «первый запуск» (как в legacy main()).
    """
    return app


# ---------- тесты ----------
def test_01_gui_started(clean_app):
    """GUI запущен, окно существует."""
    assert clean_app.root.winfo_exists()


def test_02_workflow_buttons_visible(clean_app):
    """Видны «Сканировать», «Исправить код», «В AI»."""
    a = clean_app
    assert all(is_shown(a, k) for k in ('btn_scan', 'btn_fix', 'btn_to_ai'))


def test_03_registry_elements_hidden(clean_app):
    """Скрыты 5 элементов реестра."""
    a = clean_app
    managers = {k: getattr(a, k).winfo_manager() for k in HIDE_KEYS}
    assert all(is_hidden(a, k) for k in HIDE_KEYS), str(managers)


def test_04_journal_frame_visible(clean_app):
    """journal_frame «Журнал выполнения» виден и вне реестра."""
    a = clean_app
    jf = journal_frame(a)
    assert jf.winfo_manager() == 'pack'
    assert str(jf.cget('text')) == 'Журнал выполнения'
    assert 'journal_frame' not in HIDE_KEYS


def test_05_window_height_reduced(clean_app):
    """Высота окна уменьшена (h_after < h_before)."""
    a = clean_app
    h_base = a._ui_base_geometry[1]
    h_now = a._window_size()[1]
    assert h_now < h_base, f"before={h_base}, after={h_now}"


def test_06_widgets_and_commands_alive(clean_app):
    """winfo_exists() + command сохранены у всех скрытых."""
    a = clean_app
    det = []
    for key, _label in gui_app.UI_HIDEABLE_ELEMENTS:
        w = getattr(a, key, None)
        if w is None or not w.winfo_exists():
            det.append(f"{key}: widget мёртв")
        elif key != 'changelog_frame' and not str(w.cget('command')):
            det.append(f"{key}: command пуст")
    assert not det, "; ".join(det)


def test_07_view_menu_counts(clean_app):
    """Меню «Вид»: 5 checkbutton + 2 команды."""
    a = clean_app
    vm = getattr(a, 'view_menu', None)
    n_check = n_cmd = 0
    if vm is not None:
        for i in range((vm.index('end') or 0) + 1):
            t = vm.type(i)
            n_check += t == 'checkbutton'
            n_cmd += t == 'command'
    assert vm is not None and n_check == 5 and n_cmd == 2, \
        f"checkbutton={n_check} command={n_cmd}"


def test_08_show_all(clean_app):
    """«Показать все элементы» → все видны, высота = базовая."""
    a = clean_app
    h_base = a._ui_base_geometry[1]
    a.set_all_ui_elements(True)
    a.root.update_idletasks()
    h_show = a._window_size()[1]
    assert all(is_shown(a, k) for k in HIDE_KEYS) and h_show == h_base, \
        f"h={h_show} base={h_base}"


def test_09_hide_all(clean_app):
    """«Скрыть все элементы» → все скрыты, высота < базовой."""
    a = clean_app
    h_base = a._ui_base_geometry[1]
    a.set_all_ui_elements(False)
    a.root.update_idletasks()
    h_hide = a._window_size()[1]
    assert all(is_hidden(a, k) for k in HIDE_KEYS) and h_hide < h_base, \
        f"h={h_hide}"


def test_10_toggle_one_element(clean_app):
    """toggle btn_show_sql → он виден, changelog_frame скрыт."""
    a = clean_app
    a.set_all_ui_elements(False)
    a.root.update_idletasks()
    a.ui_visible_vars['btn_show_sql'].set(True)
    a.toggle_ui_element('btn_show_sql')
    a.root.update_idletasks()
    assert is_shown(a, 'btn_show_sql') and is_hidden(a, 'changelog_frame'), \
        f"show_sql={a.btn_show_sql.winfo_manager()!r} " \
        f"changelog={a.changelog_frame.winfo_manager()!r}"


def test_11_button_order_preserved(clean_app):
    """Порядок кнопок восстановлен (От AI < Рубикатор, SQL < Koda)."""
    a = clean_app
    for visible in (True, False, True):
        a.set_all_ui_elements(visible)
    a.root.update_idletasks()
    names = [w.winfo_name() for w in a.control_frame.winfo_children()]

    def idx(k):
        return names.index(getattr(a, k).winfo_name())

    assert idx('btn_from_ai') < idx('btn_rubricator')
    assert idx('btn_show_sql') < idx('btn_send_koda')


def test_12_height_stable(clean_app):
    """Высота стабильна после 3 переключений (нет накопления)."""
    a = clean_app
    h_base = a._ui_base_geometry[1]
    for visible in (True, False, True):
        a.set_all_ui_elements(visible)
    a.root.update_idletasks()
    # После нечётного числа переключений (True, False, True) — все видны,
    # высота = базовая.
    assert a._window_size()[1] == h_base, f"h={a._window_size()[1]} base={h_base}"


def test_13_settings_written(clean_app, settings_backup):
    """settings.json → ui_hidden_elements содержит 5 ключей."""
    a = clean_app
    a.set_all_ui_elements(False)
    a.root.update_idletasks()
    with open(settings_backup, encoding='utf-8') as f:
        saved = json.load(f).get('ui_hidden_elements')
    assert isinstance(saved, list) and sorted(saved) == sorted(HIDE_KEYS), str(saved)


def test_14_restore_ui_visibility_empty(clean_app):
    """_restore_ui_visibility([]) → все элементы видны."""
    a = clean_app
    a.set_all_ui_elements(False)
    a.root.update_idletasks()
    a._restore_ui_visibility([])
    a.root.update_idletasks()
    assert all(is_shown(a, k) for k in HIDE_KEYS)


def test_15_log_text_alive(clean_app):
    """log_text цел, journal_frame не в реестре скрытия."""
    a = clean_app
    assert a.log_text.winfo_exists()
    assert 'journal_frame' not in HIDE_KEYS