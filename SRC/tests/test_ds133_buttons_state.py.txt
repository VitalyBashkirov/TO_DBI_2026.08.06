# -*- coding: utf-8 -*-
"""DS_133 — тесты активации main-кнопок 1/2/3/4.

Проверяет логику `_update_main_buttons`:
  К1 = source_ok AND pattern_ok AND rule_ok
  К2 = source_has_plp AND result_ok  (DS_136)
  К3 = result_ok AND has_plp AND ai_in_empty
  К4 = ai_out_has (управляется `_update_ai_button_state`)

Единственный источник правды — артефакты на диске (не scan_results).
Жирный шрифт (`WorkflowActive.TButton`) = кнопка доступна;
тонкий (`WorkflowNormal.TButton`) = недоступна.
"""
import io
import os
import shutil
import sys
import tempfile

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)

import tkinter as tk  # noqa: E402
import gui_app  # noqa: E402

# Без модалок.
gui_app.DBIMigrationApp._check_log_size = lambda self: None
for _fn in ('askyesno', 'showinfo', 'showwarning', 'showerror'):
    setattr(gui_app.messagebox, _fn, lambda *a, **k: False)

ROOT = os.path.dirname(SRC)
AI_IN = os.path.join(ROOT, 'EXCHANGE', 'AI_IN')
AI_OUT = os.path.join(ROOT, 'EXCHANGE', 'AI_OUT')

results = []


def check(num, desc, ok, detail=""):
    results.append((num, desc, bool(ok)))
    print(f"[{'OK  ' if ok else 'FAIL'}] #{num:>2} {desc}" + (f"  :: {detail}" if detail else ""))


def btn_state(app, name):
    return 'disabled' not in getattr(app, name).state()


def btn_style(app, name):
    return str(getattr(app, name).cget('style'))


def main():
    # Сохраняем содержимое AI_IN/AI_OUT, чтобы восстановить после теста.
    ai_in_backup = tempfile.mkdtemp(prefix='ds133_ai_in_bak_')
    ai_out_backup = tempfile.mkdtemp(prefix='ds133_ai_out_bak_')
    created_in = []
    created_out = []
    try:
        if os.path.isdir(AI_IN):
            for f in os.listdir(AI_IN):
                src_f = os.path.join(AI_IN, f)
                if os.path.isfile(src_f):
                    shutil.copy2(src_f, ai_in_backup)
                    created_in.append(f)
        if os.path.isdir(AI_OUT):
            for f in os.listdir(AI_OUT):
                src_f = os.path.join(AI_OUT, f)
                if os.path.isfile(src_f):
                    shutil.copy2(src_f, ai_out_backup)
                    created_out.append(f)

        # Чистим AI_IN/AI_OUT для изоляции.
        if os.path.isdir(AI_IN):
            for f in os.listdir(AI_IN):
                p = os.path.join(AI_IN, f)
                if os.path.isfile(p):
                    os.remove(p)
        if os.path.isdir(AI_OUT):
            for f in os.listdir(AI_OUT):
                p = os.path.join(AI_OUT, f)
                if os.path.isfile(p):
                    os.remove(p)

        tmp_src = tempfile.mkdtemp(prefix='ds133_src_')
        tmp_dst = tempfile.mkdtemp(prefix='ds133_dst_')

        root = tk.Tk()
        try:
            root.attributes('-alpha', 0.0)
        except Exception:
            root.withdraw()
        app = gui_app.DBIMigrationApp(root)
        root.update()

        # ─── К1 ─────────────────────────────────────────────
        # 1. source пустой
        app.source_dir_var.set('')
        app.result_dir_var.set(tmp_dst)
        app.file_pattern_var.set('*.plp')
        first_rule = next(iter(app.selected_rules.values()))
        first_rule.set(True)
        app._update_main_buttons()
        check(1, "К1 disabled при пустом source",
              not btn_state(app, 'btn_scan'), f"state={app.btn_scan.state()}")

        # 2. source не существует
        app.source_dir_var.set(os.path.join(tmp_src, 'несуществующий'))
        app._update_main_buttons()
        check(2, "К1 disabled, если source не существует",
              not btn_state(app, 'btn_scan'), f"state={app.btn_scan.state()}")

        # 3. pattern пустой
        app.source_dir_var.set(tmp_src)
        app.file_pattern_var.set('')
        app._update_main_buttons()
        check(3, "К1 disabled при пустом pattern",
              not btn_state(app, 'btn_scan'), f"state={app.btn_scan.state()}")

        # 4. нет выбранных правил
        app.file_pattern_var.set('*.plp')
        for v in app.selected_rules.values():
            v.set(False)
        app._update_main_buttons()
        check(4, "К1 disabled без выбранных правил",
              not btn_state(app, 'btn_scan'), f"state={app.btn_scan.state()}")

        # 5. все условия — К1 normal
        first_rule.set(True)
        app._update_main_buttons()
        check(5, "К1 normal при source+pattern+rule",
              btn_state(app, 'btn_scan'), f"state={app.btn_scan.state()}")

        # ─── К2 ─────────────────────────────────────────────
        # 6. result не существует
        app.result_dir_var.set(os.path.join(tmp_dst, 'несуществующий'))
        app._update_main_buttons()
        check(6, "К2 disabled, если result не существует",
              not btn_state(app, 'btn_fix'), f"state={app.btn_fix.state()}")

        # 7. result есть, но без *.plp
        empty_dst = tempfile.mkdtemp(prefix='ds133_empty_')
        app.result_dir_var.set(empty_dst)
        app._update_main_buttons()
        check(7, "К2 disabled без *.plp в result",
              not btn_state(app, 'btn_fix'), f"state={app.btn_fix.state()}")

        # 8. result с *.plp + source с *.plp — К2 normal (DS_136)
        with open(os.path.join(empty_dst, 'test.plp'), 'w') as f:
            f.write('x')
        src_plp = os.path.join(tmp_src, 'src_test.plp')
        with open(src_plp, 'w') as f:
            f.write('x')
        app._update_main_buttons()
        check(8, "К2 normal при *.plp в result и source",
              btn_state(app, 'btn_fix'), f"state={app.btn_fix.state()}")

        # 8b. DS_136: result с *.plp, но source без *.plp — К2 disabled
        os.remove(src_plp) if os.path.exists(src_plp) else None
        app._update_main_buttons()
        check(8, "К2 disabled, если source без *.plp (DS_136)",
              not btn_state(app, 'btn_fix'), f"state={app.btn_fix.state()}")

        # 8c. DS_136: тултип К2 при source без *.plp
        tt_k2 = getattr(app, '_tooltip_fix', None)
        check(8, "Тултип К2: нет *.plp в source (DS_136)",
              tt_k2 is not None and 'нет файлов по шаблону' in (tt_k2.text or '').lower(),
              f"tip={tt_k2.text if tt_k2 else None!r}")

        # Восстанавливаем source с *.plp для К3
        with open(src_plp, 'w') as f:
            f.write('x')
        app._update_main_buttons()

        # ─── К3 ─────────────────────────────────────────────
        # 9. К3 disabled, если в AI_IN есть AI_REQUEST_*.md
        if not os.path.isdir(AI_IN):
            os.makedirs(AI_IN)
        req = os.path.join(AI_IN, 'AI_REQUEST_ds133_test.md')
        with open(req, 'w') as f:
            f.write('тест')
        app._update_main_buttons()
        check(9, "К3 disabled при AI_REQUEST в AI_IN",
              not btn_state(app, 'btn_to_ai'), f"state={app.btn_to_ai.state()}")

        # 10. К3 normal, если AI_IN пуст
        os.remove(req)
        app._update_main_buttons()
        check(10, "К3 normal при *.plp + пустом AI_IN",
              btn_state(app, 'btn_to_ai'), f"state={app.btn_to_ai.state()}")

        # ─── К4 ─────────────────────────────────────────────
        # 11. AI_OUT пуст — К4 disabled
        app._update_ai_button_state()
        check(11, "К4 disabled при пустом AI_OUT",
              not btn_state(app, 'btn_from_ai'), f"state={app.btn_from_ai.state()}")

        # 12. AI_RESPONSE_*.md — К4 normal
        if not os.path.isdir(AI_OUT):
            os.makedirs(AI_OUT)
        resp = os.path.join(AI_OUT, 'AI_RESPONSE_ds133_test.md')
        with open(resp, 'w') as f:
            f.write('ответ')
        app._update_ai_button_state()
        check(12, "К4 normal при AI_RESPONSE в AI_OUT",
              btn_state(app, 'btn_from_ai'), f"state={app.btn_from_ai.state()}")

        # ─── Стили ──────────────────────────────────────────
        # 13. normal → WorkflowActive
        first_rule.set(True)
        app.source_dir_var.set(tmp_src)
        app.file_pattern_var.set('*.plp')
        app.result_dir_var.set(empty_dst)
        os.remove(req) if os.path.exists(req) else None
        app._update_main_buttons()
        check(13, "Стиль normal → WorkflowActive.TButton",
              'WorkflowActive' in btn_style(app, 'btn_scan'),
              f"style={btn_style(app, 'btn_scan')!r}")

        # 14. disabled → WorkflowNormal
        app.source_dir_var.set('')
        app._update_main_buttons()
        check(14, "Стиль disabled → WorkflowNormal.TButton",
              'WorkflowNormal' in btn_style(app, 'btn_scan'),
              f"style={btn_style(app, 'btn_scan')!r}")

        # ─── Тултипы ────────────────────────────────────────
        # 15. Тултип К1 отражает причину (source пуст)
        tt = getattr(app, '_tooltip_scan', None)
        check(15, "Тултип К1 отражает причину disabled",
              tt is not None and 'исходный каталог' in (tt.text or '').lower(),
              f"tip={tt.text if tt else None!r}")

        # ─── scan_running ───────────────────────────────────
        # 16. Во время scan_running — не пересчитываем
        app.source_dir_var.set(tmp_src)
        app.file_pattern_var.set('*.plp')
        first_rule.set(True)
        app._update_main_buttons()
        state_before = app.btn_scan.state()
        app.scan_running = True
        app.source_dir_var.set('')  # не должно повлиять
        app._update_main_buttons()
        state_after = app.btn_scan.state()
        app.scan_running = False
        check(16, "scan_running=True → не пересчитываем",
              state_before == state_after,
              f"before={state_before} after={state_after}")

        root.destroy()
        shutil.rmtree(tmp_src, ignore_errors=True)
        shutil.rmtree(tmp_dst, ignore_errors=True)
        shutil.rmtree(empty_dst, ignore_errors=True)
    finally:
        # Восстанавливаем AI_IN/AI_OUT.
        if os.path.isdir(AI_IN):
            for f in os.listdir(AI_IN):
                p = os.path.join(AI_IN, f)
                if os.path.isfile(p):
                    os.remove(p)
        for f in created_in:
            shutil.copy2(os.path.join(ai_in_backup, f), AI_IN)
        if os.path.isdir(AI_OUT):
            for f in os.listdir(AI_OUT):
                p = os.path.join(AI_OUT, f)
                if os.path.isfile(p):
                    os.remove(p)
        for f in created_out:
            shutil.copy2(os.path.join(ai_out_backup, f), AI_OUT)
        shutil.rmtree(ai_in_backup, ignore_errors=True)
        shutil.rmtree(ai_out_backup, ignore_errors=True)

    failed = [r for r in results if not r[2]]
    print("-" * 60)
    print(f"ИТОГ: {len(results) - len(failed)}/{len(results)} PASSED")
    for num, desc, _ok in failed:
        print(f"  FAIL #{num}: {desc}")
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
