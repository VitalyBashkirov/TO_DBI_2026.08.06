# DS_141 — Кириллица U+FFFD в ЖВ (Урок EE)

## Контекст

Чат 30. При ручном smoke К3 в чате 29 в Журнале выполнения (Tkinter Text)
русский текст от ai_local_worker.py выводился как U+FFFD (�):
  [16:11:47] resume: 96 id ������������
  [16:11:47] AI_REQUEST_..._.md: issues ��� ...

Причина: дочерний процесс (ai_local_worker.py) пишет stdout в системной
кодировке Windows (cp1251), GUI читает его через raw.decode('utf-8')
(строка ~5859 gui_app.py).

## Действие (вариант C — belt and suspenders)

1. tools/ai_local_worker.py: принудительный sys.stdout/stderr → UTF-8
   (TextIOWrapper, errors='replace') после блока импортов.
2. SRC/gui_app.py: 2 точки Popen (rule_based_fixer, ai_local_worker) —
   env=dict(os.environ, PYTHONIOENCODING='utf-8').

rule_based_fixer.py НЕ трогаем — он уже принудительно ставит UTF-8
внутри main() (см. строки 333-336).

## Ожидание

- ai_local_worker.py: 1018 → 1027 строк (+9), BOM=False.
- gui_app.py: 6059 → 6063 строк (+4), BOM=False.
- ast.parse OK для обоих.
- ai_local_worker.py --check → OK.
- pytest 77 passed; DS_133 18/18; DS_086 15/15.

## Артефакты

- Отчёт: EXCHANGE\OUTBOX\DS_141_utf8_ai_worker_report.md
- Логи: PS\ds141_preview.log, ds141_preview_rulebased.log,
  ds141_fix_worker.log, ds141_fix_gui.log (FAIL .like),
  ds141_fix_gui_v2.log, ds141_regress.log, ds141_git.log
- Бэкапы: ai_local_worker.py.bak_ds141, gui_app.py.bak_ds141,
  gui_app.py.bak_ds141v2

## Замечание

Файл EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md — modified (не мы,
вероятно ночной pipeline CNT). В коммит DS_141 НЕ включается.