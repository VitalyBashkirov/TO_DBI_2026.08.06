# -*- coding: utf-8 -*-
"""DS_133 (pytest-версия) — тесты активации main-кнопок 1/2/3/4.

Проверяет логику `_update_main_buttons`:
  К1 = source_ok AND pattern_ok AND rule_ok
  К2 = source_has_plp AND result_ok  (DS_136)
  К3 = result_ok AND has_plp AND ai_in_empty
  К4 = ai_out_has (управляется `_update_ai_button_state`)

Единственный источник правды — артефакты на диске (не scan_results).
Жирный шрифт (`WorkflowActive.TButton`) = кнопка доступна;
тонкий (`WorkflowNormal.TButton`) = недоступна.

Мигрировано с legacy test_ds133_buttons_state.py (18 проверок).
"""
import pytest


# ---------- хелперы (перенесены из legacy) ----------
def btn_state(app, name):
    """True, если кнопка активна."""
    return 'disabled' not in getattr(app, name).state()


def btn_style(app, name):
    """Строка стиля кнопки."""
    return str(getattr(app, name).cget('style'))


def first_rule(app):
    """Первое правило из selected_rules."""
    return next(iter(app.selected_rules.values()))


# ---------- К1: source + pattern + rule ----------
def test_01_k1_disabled_empty_source(app, isolated_ai, tmp_path):
    app.source_dir_var.set('')
    app.result_dir_var.set(str(tmp_path))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()
    assert not btn_state(app, 'btn_scan'), f"state={app.btn_scan.state()}"


def test_02_k1_disabled_nonexistent_source(app, isolated_ai, tmp_path):
    app.source_dir_var.set(str(tmp_path / 'несуществующий'))
    app.result_dir_var.set(str(tmp_path))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()
    assert not btn_state(app, 'btn_scan'), f"state={app.btn_scan.state()}"


def test_03_k1_disabled_empty_pattern(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    app.source_dir_var.set(str(src))
    app.result_dir_var.set(str(tmp_path))
    app.file_pattern_var.set('')
    first_rule(app).set(True)
    app._update_main_buttons()
    assert not btn_state(app, 'btn_scan'), f"state={app.btn_scan.state()}"


def test_04_k1_disabled_no_rules(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    app.source_dir_var.set(str(src))
    app.result_dir_var.set(str(tmp_path))
    app.file_pattern_var.set('*.plp')
    for v in app.selected_rules.values():
        v.set(False)
    app._update_main_buttons()
    assert not btn_state(app, 'btn_scan'), f"state={app.btn_scan.state()}"


def test_05_k1_normal_source_pattern_rule(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    app.source_dir_var.set(str(src))
    app.result_dir_var.set(str(tmp_path))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()
    assert btn_state(app, 'btn_scan'), f"state={app.btn_scan.state()}"


# ---------- К2: result + source *.plp (DS_136) ----------
def test_06_k2_disabled_nonexistent_result(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    app.source_dir_var.set(str(src))
    app.result_dir_var.set(str(tmp_path / 'несуществующий'))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()
    assert not btn_state(app, 'btn_fix'), f"state={app.btn_fix.state()}"


def test_07_k2_disabled_no_plp_in_result(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    empty_dst = tmp_path / 'empty_dst'
    empty_dst.mkdir()
    app.source_dir_var.set(str(src))
    app.result_dir_var.set(str(empty_dst))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()
    assert not btn_state(app, 'btn_fix'), f"state={app.btn_fix.state()}"


def test_08a_k2_normal_plp_in_result_and_source(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    empty_dst = tmp_path / 'empty_dst'
    empty_dst.mkdir()

    (empty_dst / 'test.plp').write_text('x')
    src_plp = src / 'src_test.plp'
    src_plp.write_text('x')

    app.source_dir_var.set(str(src))
    app.result_dir_var.set(str(empty_dst))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()
    assert btn_state(app, 'btn_fix'), f"state={app.btn_fix.state()}"


def test_08b_k2_disabled_source_no_plp(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    empty_dst = tmp_path / 'empty_dst'
    empty_dst.mkdir()
    (empty_dst / 'test.plp').write_text('x')
    # source без *.plp

    app.source_dir_var.set(str(src))
    app.result_dir_var.set(str(empty_dst))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()
    assert not btn_state(app, 'btn_fix'), f"state={app.btn_fix.state()}"


def test_08c_k2_tooltip_source_no_plp(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    empty_dst = tmp_path / 'empty_dst'
    empty_dst.mkdir()
    (empty_dst / 'test.plp').write_text('x')

    app.source_dir_var.set(str(src))
    app.result_dir_var.set(str(empty_dst))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()

    tt = getattr(app, '_tooltip_fix', None)
    assert tt is not None, "tooltip fix отсутствует"
    assert 'нет файлов по шаблону' in (tt.text or '').lower(), f"tip={tt.text!r}"


# ---------- К3: result + AI_IN пуст ----------
def test_09_k3_disabled_ai_request_in_ai_in(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    empty_dst = tmp_path / 'empty_dst'
    empty_dst.mkdir()
    (empty_dst / 'test.plp').write_text('x')
    (src / 'src_test.plp').write_text('x')

    # AI_REQUEST в изолированном AI_IN
    req = isolated_ai['ai_in'] / 'AI_REQUEST_ds140_test.md'
    req.write_text('тест')

    app.source_dir_var.set(str(src))
    app.result_dir_var.set(str(empty_dst))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()
    assert not btn_state(app, 'btn_to_ai'), f"state={app.btn_to_ai.state()}"


def test_10_k3_normal_plp_and_empty_ai_in(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    empty_dst = tmp_path / 'empty_dst'
    empty_dst.mkdir()
    (empty_dst / 'test.plp').write_text('x')
    (src / 'src_test.plp').write_text('x')
    # AI_IN пуст

    app.source_dir_var.set(str(src))
    app.result_dir_var.set(str(empty_dst))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()
    assert btn_state(app, 'btn_to_ai'), f"state={app.btn_to_ai.state()}"


# ---------- К4: AI_OUT ----------
def test_11_k4_disabled_empty_ai_out(app, isolated_ai, tmp_path):
    app._update_ai_button_state()
    assert not btn_state(app, 'btn_from_ai'), f"state={app.btn_from_ai.state()}"


def test_12_k4_normal_ai_response_in_ai_out(app, isolated_ai, tmp_path):
    resp = isolated_ai['ai_out'] / 'AI_RESPONSE_ds140_test.md'
    resp.write_text('ответ')
    app._update_ai_button_state()
    assert btn_state(app, 'btn_from_ai'), f"state={app.btn_from_ai.state()}"


# ---------- Стили ----------
def test_13_style_normal_workflow_active(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    empty_dst = tmp_path / 'empty_dst'
    empty_dst.mkdir()
    (empty_dst / 'test.plp').write_text('x')
    (src / 'src_test.plp').write_text('x')

    first_rule(app).set(True)
    app.source_dir_var.set(str(src))
    app.file_pattern_var.set('*.plp')
    app.result_dir_var.set(str(empty_dst))
    app._update_main_buttons()

    style = btn_style(app, 'btn_scan')
    assert 'WorkflowActive' in style, f"style={style!r}"


def test_14_style_disabled_workflow_normal(app, isolated_ai, tmp_path):
    app.source_dir_var.set('')
    app._update_main_buttons()
    style = btn_style(app, 'btn_scan')
    assert 'WorkflowNormal' in style, f"style={style!r}"


# ---------- Тултипы ----------
def test_15_tooltip_k1_reflects_reason(app, isolated_ai, tmp_path):
    app.source_dir_var.set('')
    app._update_main_buttons()
    tt = getattr(app, '_tooltip_scan', None)
    assert tt is not None, "tooltip scan отсутствует"
    assert 'исходный каталог' in (tt.text or '').lower(), f"tip={tt.text!r}"


# ---------- scan_running ----------
def test_16_scan_running_true_not_recalculated(app, isolated_ai, tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    (src / 'src_test.plp').write_text('x')

    app.source_dir_var.set(str(src))
    app.file_pattern_var.set('*.plp')
    first_rule(app).set(True)
    app._update_main_buttons()
    state_before = app.btn_scan.state()

    app.scan_running = True
    app.source_dir_var.set('')  # не должно повлиять
    app._update_main_buttons()
    state_after = app.btn_scan.state()
    app.scan_running = False

    assert state_before == state_after, f"before={state_before} after={state_after}"