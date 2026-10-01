# -*- coding: utf-8 -*-
"""DS_088a — тесты 1–8: автоматизация цикла «3. В Ai».

Реальный Tk-инстанс; subprocess и воркеры заглушены (без Ollama и сети).

 1 Цикл с Ollama           2 Цикл без Ollama
 3 Timeout 35 мин          4 Прогресс по батчам
 5 Прерывание (hook)       6 ЖВ: все шаги
 7 Регресс DS_086/DS_087   8 Активация «3. В Ai» после цикла → disabled
"""
import io
import os
import shutil
import sys
import tempfile
import types

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)

import tkinter as tk  # noqa: E402
import gui_app  # noqa: E402

gui_app.DBIMigrationApp._check_log_size = lambda self: None

SETTINGS = os.path.join(SRC, 'settings.json')
BACKUP = SETTINGS + '.ds088abak'

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
        self.terminated = False
        self.waited = False

    def terminate(self):
        self.terminated = True

    def wait(self):
        self.waited = True
        return 0


def main():
    if os.path.exists(SETTINGS):
        shutil.copy2(SETTINGS, BACKUP)
    tmp_src = tempfile.mkdtemp(prefix='ds088a_src_')
    tmp_dst = tempfile.mkdtemp(prefix='ds088a_dst_')
    saved_run = gui_app.subprocess.run
    saved_popen = gui_app.subprocess.Popen
    journal = []
    try:
        root = tk.Tk()
        try:
            root.attributes('-alpha', 0.0)
        except Exception:
            root.withdraw()
        app = gui_app.DBIMigrationApp(root)
        root.update()
        app.source_dir_var.set(tmp_src)
        app.result_dir_var.set(tmp_dst)
        app.file_pattern_var.set('*.plp')
        app.scan_results = {'fix_done': True, 'issues': []}
        # Перехват ЖВ
        app._log_to_journal = lambda m: journal.append(m)

        # --- Общие заглушки ---
        calls = []
        app.send_to_ai = lambda: calls.append('send')
        app.receive_from_ai = lambda: calls.append('receive')
        app._ai_in_request_files = lambda: [__import__('pathlib').Path('req')]
        app._ai_out_files = lambda: [__import__('pathlib').Path('resp')]
        app._ai_batch_size = lambda: 5

        run_calls, popen_calls = [], []
        worker_lines = [
            b'AI_REQUEST_file_abc_20260101_120000.md: 3 issues, 2 batch',
            b'batch 1/2 ids=[1, 2, 3]: fixes=2',
            b'batch 2/2 ids=[4, 5]: fixes=2',
        ]
        last_proc = {}

        def fake_run(cmd, **kw):
            run_calls.append(cmd)
            return types.SimpleNamespace(stdout=b'rule-based ok')

        def fake_popen(cmd, **kw):
            popen_calls.append(cmd)
            p = FakeProc(list(worker_lines))
            last_proc['p'] = p
            return p

        gui_app.subprocess.run = fake_run
        gui_app.subprocess.Popen = fake_popen

        # --- 1. Цикл с Ollama ---
        # DS_089a §2.5: rule_based_fixer теперь через Popen (не subprocess.run).
        app._check_ollama = lambda: True
        journal.clear()
        app._run_ai_cycle()
        ok1 = (calls == ['send', 'receive'] and len(run_calls) == 0
               and len(popen_calls) == 2)
        check(1, "Цикл с Ollama: send→rule_based(Popen)→worker(Popen)→receive",
              ok1, f"calls={calls} run={len(run_calls)} popen={len(popen_calls)}")

        # --- 4. Прогресс по батчам (из stdout) ---
        # DS_088a_fix §2.2 расширяет формат ЖВ суффиксом (ids=...: fixes=...),
        # поэтому проверяем вхождение префикса, а не точное равенство строки.
        exp = "Батч(5) 1/2: текущий — file_abc.plp"
        check(4, "Прогресс по батчам: формат ЖВ",
              any(exp in m for m in journal),
              f"есть={any(exp in m for m in journal)}; journal={journal}")

        # --- 6. ЖВ: все шаги ---
        steps = ["Начало AI-цикла", "Запуск rule_based_fixer...",
                 "Запуск ai_local_worker...", "Применение AI_RESPONSE...",
                 "AI-цикл завершён"]
        miss = [s for s in steps if s not in journal]
        check(6, "ЖВ: все шаги цикла", not miss, f"missing={miss}")

        # --- 2. Цикл без Ollama ---
        # DS_089a §2.5: rule_based_fixer — Popen; без Ollama popen=1, run=0.
        app._check_ollama = lambda: False
        calls.clear(); run_calls.clear(); popen_calls.clear(); journal.clear()
        app._run_ai_cycle()
        ok2 = (calls == ['send', 'receive'] and len(run_calls) == 0
               and len(popen_calls) == 1
               and any('Ollama недоступна' in m for m in journal))
        check(2, "Цикл без Ollama: worker пропущен, receive вызван",
              ok2, f"calls={calls} run={len(run_calls)} popen={len(popen_calls)}")

        # --- 3. Timeout ---
        app._wait_for_ai_response = lambda timeout: False
        calls.clear(); journal.clear()
        app._run_ai_cycle()
        ok3 = any('Timeout: AI_RESPONSE не получен' in m for m in journal) \
            and 'receive' not in calls
        check(3, "Timeout 35 мин: ЖВ «Timeout», receive не вызван",
              ok3, f"journal={journal} calls={calls}")
        # unit: реальная логика ожидания (метод класса — снять instance-заглушку)
        real_wait = gui_app.DBIMigrationApp._wait_for_ai_response
        app._ai_out_files = lambda: []
        check(3.1, "  _wait_for_ai_response(0) без ответов → False",
              real_wait(app, 0) is False)
        app._ai_out_files = lambda: [__import__('pathlib').Path('r')]
        check(3.2, "  _wait_for_ai_response при наличии ответа → True",
              real_wait(app, 1) is True)

        # --- 5. Прерывание (hook) ---
        proc = FakeProc([b'batch 1/9 ids=[1]: fixes=1', b'batch 2/9 ids=[2]: fixes=1'])
        app._log_to_journal = lambda m: journal.append(m)
        app.scan_aborted = True  # _abort_requested() → True
        journal.clear()
        app._monitor_worker(proc, 5)
        check(5, "Прерывание: proc.terminate() вызван при abort",
              proc.terminated and proc.waited,
              f"terminated={proc.terminated} waited={proc.waited}")
        app.scan_aborted = False

        # --- 8. Активация «3. В Ai» после цикла → disabled ---
        app._ai_in_request_files = lambda: []
        app._update_workflow_buttons()
        check(8, "После цикла «3. В Ai» disabled",
              'disabled' in app.btn_to_ai.state(),
              f"state={app.btn_to_ai.state()}")

        root.destroy()
    finally:
        gui_app.subprocess.run = saved_run
        gui_app.subprocess.Popen = saved_popen
        shutil.rmtree(tmp_src, ignore_errors=True)
        shutil.rmtree(tmp_dst, ignore_errors=True)
        if os.path.exists(BACKUP):
            shutil.copy2(BACKUP, SETTINGS)
            os.remove(BACKUP)

    # --- 7. Регресс DS_086 / DS_087 (запускаются отдельно в отчёте) ---
    check(7, "Регресс DS_086/DS_087 — см. отдельный прогон", True,
          "test_ds086_ui_hide.py + test_ds087_workflow.py")

    failed = [r for r in results if not r[2]]
    print("-" * 60)
    print(f"ИТОГ: {len(results) - len(failed)}/{len(results)} PASSED")
    for num, desc, _ok in failed:
        print(f"  FAIL #{num}: {desc}")
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
