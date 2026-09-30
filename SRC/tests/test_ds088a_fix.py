# -*- coding: utf-8 -*-
"""DS_088a_fix — тесты 1–16: формат ЖВ + пороги confidence + layout."""
import inspect
import io
import json
import os
import shutil
import sys
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)

import tkinter as tk  # noqa: E402
import gui_app  # noqa: E402
import ai_exchange  # noqa: E402

gui_app.DBIMigrationApp._check_log_size = lambda self: None
for _fn in ('askyesno', 'showinfo', 'showwarning', 'showerror'):
    setattr(gui_app.messagebox, _fn, lambda *a, **k: None)

SETTINGS = os.path.join(SRC, 'settings.json')
BACKUP = SETTINGS + '.ds088afixbak'

results = []


def check(num, desc, ok, detail=""):
    results.append((num, desc, bool(ok)))
    print(f"[{'OK  ' if ok else 'FAIL'}] #{num:>2} {desc}" + (f"  :: {detail}" if detail else ""))


class FakeStdout:
    def __init__(self, lines):
        self._it = iter(lines)

    def readline(self):
        try:
            return next(self._it)
        except StopIteration:
            return b''


class FakeProc:
    def __init__(self, lines):
        self.stdout = FakeStdout(lines)

    def terminate(self):
        pass

    def wait(self):
        return 0


def main():
    if os.path.exists(SETTINGS):
        shutil.copy2(SETTINGS, BACKUP)
    ai_in = os.path.join(SRC, '..', 'EXCHANGE', 'AI_IN')
    ai_in = os.path.normpath(ai_in)
    tmp_req = os.path.join(ai_in, 'AI_REQUEST_zzfix_20260101_000000.md')
    tmp_out = tempfile.mkdtemp(prefix='ds088afix_out_')
    created_req = False
    try:
        root = tk.Tk()
        try:
            root.attributes('-alpha', 0.0)
        except Exception:
            root.withdraw()
        app = gui_app.DBIMigrationApp(root)
        root.update()
        journal = []
        app._log_to_journal = lambda m: journal.append(m)

        # ---- Тест 1: формат ЖВ ----
        proc = FakeProc([
            b'AI_REQUEST_file_abc_20260101_120000.md: 3 issues, 1 batch',
            b'batch 1/5 ids=[1]: fixes=1 \xd0\xb2\xd1\x80\xd0\xb5\xd0\xbc\xd1\x8f=53.6\xd1\x81 conf=[0.95]',
        ])
        journal.clear()
        app._monitor_worker(proc, 10)
        exp1 = "Батч(10) 1/5: текущий — file_abc.plp (ids=[1]: fixes=1 время=53.6с conf=[0.95])"
        check(1, "Формат ЖВ batch 1/5", exp1 in journal, f"journal={journal}")

        # ---- Тест 2: fallback ----
        proc = FakeProc([
            b'batch 2/5 ids=[1]: \xd0\xbd\xd0\xb5\xd0\xb2\xd0\xb0\xd0\xbb\xd0\xb8\xd0\xb4\xd0\xbd\xd1\x8b\xd0\xb9 JSON \xe2\x80\x94 fallback',
            b'  fallback: split 10 -> 2 (\xd0\xbf\xd0\xbe 5)',
        ])
        journal.clear()
        app._monitor_worker(proc, 10)
        check(2, "Fallback → (fallback 2×5)",
              any("(fallback 2×5)" in m for m in journal), f"journal={journal}")

        # ---- Тест 3: mapping id → source (из - Источник:) ----
        with open(tmp_req, 'w', encoding='utf-8') as f:
            f.write("# AI-запрос\n- Источник: F:\\TO_DBI\\SRC\\ENTITY\\MY_FILE_zz.plp\n")
        created_req = True
        src_name = app._source_from_request_name('AI_REQUEST_zzfix_20260101_000000.md')
        check(3, "Mapping id → source из «- Источник:»",
              src_name == 'MY_FILE_zz.plp', f"got={src_name!r}")

        # ---- Тест 4/5: сигнатуры ----
        p1 = inspect.signature(ai_exchange.process_all_responses).parameters
        check(4, "process_all_responses принимает conf_low/conf_high",
              'conf_low' in p1 and 'conf_high' in p1, f"params={list(p1)}")
        p2 = inspect.signature(ai_exchange.apply_fixes).parameters
        check(5, "apply_fixes принимает conf_low/conf_high",
              'conf_low' in p2 and 'conf_high' in p2, f"params={list(p2)}")

        # ---- Тест 7: обратная совместимость (дефолты) ----
        tmpf = os.path.join(tmp_out, 'compat.plp')
        with open(tmpf, 'w', encoding='utf-8') as f:
            f.write('line1\nline2\n')
        st = ai_exchange.apply_fixes(tmpf, [
            {'line': 2, 'before': 'line2', 'after': 'line2x', 'confidence': 0.9}])
        check(7, "Обратная совместимость: apply_fixes() без порогов",
              st.get('applied_auto') == 1, f"stats={st}")
        check(7.1, "  classify_fix() дефолт 0.8/0.5",
              ai_exchange.classify_fix({'confidence': 0.6, 'after': 'x'}) == 'medium'
              and ai_exchange.classify_fix({'confidence': 0.9, 'after': 'x'}) == 'auto',
              "ok")

        # ---- Тест 6: пороги из config (receive_from_ai передаёт) ----
        app.conf_low_var.set('0.6')
        app.conf_high_var.set('0.85')
        app._conf_low_prev, app._conf_high_prev = 0.6, 0.85
        captured = {}

        def fake_par(**kw):
            captured.update(kw)
            return []

        real_ensure = ai_exchange.ensure_dirs
        real_par = ai_exchange.process_all_responses
        from pathlib import Path as _P
        ai_exchange.ensure_dirs = lambda *a, **k: {
            'AI_IN': _P(tmp_out), 'AI_OUT': _P(tmp_out),
            'AI_IN_PROCESSED': _P(tmp_out), 'AI_OUT_PROCESSED': _P(tmp_out)}
        with open(os.path.join(tmp_out, 'AI_RESPONSE_x_20260101_000000.md'),
                  'w', encoding='utf-8') as f:
            f.write('```json\n[]\n```')
        ai_exchange.process_all_responses = fake_par
        app.receive_from_ai()
        ai_exchange.process_all_responses = real_par
        ai_exchange.ensure_dirs = real_ensure
        check(6, "receive_from_ai передаёт пороги из config",
              captured.get('conf_low') == 0.6 and captured.get('conf_high') == 0.85,
              f"captured={captured}")

        # ---- Тест 8: поля confidence на форме ----
        ok8 = (app.conf_low_entry.winfo_ismapped() and app.conf_high_entry.winfo_ismapped())
        check(8, "2 поля confidence на форме", bool(ok8),
              f"low={app.conf_low_entry.winfo_ismapped()} high={app.conf_high_entry.winfo_ismapped()}")

        # ---- Тест 9: tooltip ----
        # DS_088b §2.5 перенёс tooltip с поля conf_low на метку «Пороги
        # confidence:» и заменил текст — проверка обновлена под новое поведение.
        tip = getattr(app, '_tooltip_conf', None)
        check(9, "Tooltip метки «Пороги confidence:» (DS_088b)",
              tip is not None and 'Пороги confidence для AI-фиксов' in tip.text,
              tip.text if tip else 'None')

        # ---- Тест 10: контроль диапазона ----
        loglines = []
        real_log = app.log
        app.log = lambda msg, level='info': loglines.append(msg)
        app._conf_low_prev, app._conf_high_prev = 0.5, 0.8
        app.conf_low_var.set('1.5')
        app.conf_high_var.set('0.8')
        loglines.clear()
        app._on_confidence_change()
        ok10 = (app.conf_low_var.get() == '0.5'
                and any('вне диапазона' in m for m in loglines))
        check(10, "Контроль диапазона: 1.5 → сообщение + откат", ok10,
              f"low={app.conf_low_var.get()} log={loglines}")

        # ---- Тест 11: запись в ЖВ при изменении ----
        app._conf_low_prev, app._conf_high_prev = 0.5, 0.8
        app.conf_low_var.set('0.6')
        app.conf_high_var.set('0.85')
        loglines.clear()
        app._on_confidence_change()
        app.log = real_log
        check(11, "Запись в ЖВ при изменении порогов",
              any('Пороги confidence изменены: low=0.6, high=0.85' in m for m in loglines),
              f"log={loglines}")

        # ---- Тест 12: сохранение в settings.json ----
        saved = app._read_settings_json()
        check(12, "settings.json обновлён (conf_low/conf_high)",
              saved.get('conf_low') == 0.6 and saved.get('conf_high') == 0.85,
              f"conf_low={saved.get('conf_low')} conf_high={saved.get('conf_high')}")

        # ---- Тест 13: сдвиг кнопок правее ----
        root.update_idletasks()
        x_conf = app.conf_high_entry.winfo_x()
        x_rub = app.btn_rubricator.winfo_x()
        x_gen = app.btn_test_gen.winfo_x()
        check(13, "«Открыть рубикатор»/«Генерация .plp» правее полей confidence",
              x_rub > x_conf and x_gen > x_rub,
              f"conf_high={x_conf} rubricator={x_rub} test_gen={x_gen}")

        # ---- Тест 14: подфлаги в две колонки (10 чекбоксов) ----
        n_chk = 1 + len(app.chk_plpcheck_categories)  # «Выбрать все» + 9
        rows = set()
        cols = set()
        for child in app.frame_plpcheck_categories.winfo_children():
            gi = child.grid_info()
            if gi:
                rows.add(int(gi['row']))
                cols.add(int(gi['column']))
        check(14, "Подфлаги PlpCheck в 2 колонки (10 чекбоксов)",
              n_chk == 10 and cols == {0, 1} and max(rows) <= 5,
              f"n={n_chk} cols={sorted(cols)} max_row={max(rows)}")

        # ---- Тест 15: элементы подняты (plpcheck компактнее) ----
        # 2 колонки: 6 строк (0 + 5) вместо 10 (0 + 9) — вертикальное место
        # освобождено, «Фильтр по приоритету» и «Флаги DS_053» выше.
        ok15 = max(rows) <= 5 and app.priority_high_var is not None and app.var_fix_flags
        check(15, "Подъём: plpcheck компактен (≤6 строк), priority/flags на месте",
              bool(ok15), f"max_row={max(rows)}")

        root.destroy()
    finally:
        if created_req and os.path.exists(tmp_req):
            os.remove(tmp_req)
        shutil.rmtree(tmp_out, ignore_errors=True)
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
