# -*- coding: utf-8 -*-
from pathlib import Path
PAM = Path(r"F:\TO_DBI\PS\CHAT_RULES\Отчеты\Памятка_чатов.txt")
STA = Path(r"F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\70.Старт.txt")
NL = chr(10)
def write_no_bom(p, text):
    p.write_text(text, encoding="utf-8")
    b = p.read_bytes()
    bom = b.startswith(b"\xef\xbb\xbf")
    print(p.name, "bytes=", len(b), "bom=", bom)
    if bom: raise SystemExit("BOM not allowed: " + str(p))

# Памятка: строка о чате 69 (закрыт) + раздел чата 70
old = PAM.read_text(encoding="utf-8") if PAM.exists() else ""
blk = [
  "",
  "## Чат 69 (2026-10-27) — ЗАКРЫТ",
  "- DS_187 закрыт: блок ВЫБОР ПОЛЬЗОВАТЕЛЯ в отчётах (md/html/VVVxVV). Коммит 8623af2.",
  "- Снят UTF-8 BOM с gui_app.py. Тесты: 7/60/385 passed, 1 failed (DS_182 baseline).",
  "",
  "## Чат 70 (2026-10-27) — В РАБОТЕ",
  "- Хост: LG (старт).",
  "- Шаг 70_00: старт чата, Памятка, чтение 69.Отчёт.txt.",
  "- Долг 2 (план, первый): SyntaxWarning invalid escape sequence в scanner.py:1257 -> r-строка.",
  "- Долг 1 (план): DS_182 plpcheck.NOT_MENTIONED в test_ds182 — разбор _check_plp_not_mentioned.",
  "- Долг 3 (план): PSH_PS_DEL.plp for v_ps in this(idx).[B_PS] — отдельное правило.",
  "- Долг 4: грязные фоновые не коммитить.",
  "",
]
block = NL.join(blk)
if "## Чат 70 (2026-10-27) — В РАБОТЕ" in old:
    print("[pam] раздел 70 уже есть — пропуск")
else:
    write_no_bom(PAM, old.rstrip() + NL + block + NL)

# Старт чата 70
sta = [
  "============================================",
  "  70.СТАРТ (сгенерировано 2026-10-27 из чата 69)",
  "  Хост: LGGRAMA8V7Q8U (hostTag=LG) / MATEBOOKE (hostTag=MBE)",
  "============================================",
  "",
  "## Где искать правила (ОБЯЗАТЕЛЬНО в новом чате)",
  "F:\\TO_DBI\\PS\\CHAT_RULES\\",
  "  00_INDEX.md",
  "  Отчеты\\ — +69",
  "  Скрипты чатов\\ — +chat70_*",
  "  Старт новых чатов\\ — +70",
  "  Старт новых чатов\\01_08 Правила,регламенты,сокращения и т.п\\",
  "      00_INDEX.md, 01_Правила_PS.md (вкл. 67_1), 02_Сокращения_GUI.md, 03_Матрица_флагов.md,",
  "      04_Регламент_логов.md, 05_Регламент_тестов.md, 06_Регламент_коммитов.md, 07_Шаблон_PS.md, 08_Окружение.md",
  "",
  "## Статус на 2026-10-27 (после чата 69)",
  "- HEAD = 8623af2. origin/feature/dockerization = 8623af2.",
  "- DS_187 закрыт: блок ВЫБОР ПОЛЬЗОВАТЕЛЯ в отчётах (md/html/VVVxVV), scanner.py не менялся.",
  "- Снят UTF-8 BOM с gui_app.py; полный регресс 385 passed, 1 failed (DS_182, предсуществующий).",
  "- Тест test_ds187_rubricator_user_in_reports.py — 7 passed.",
  "",
  "## Долги 69 -> 70",
  "1. DS_182: plpcheck.NOT_MENTIONED не находится в test_ds182 — отдельная задача (baseline 1 failed).",
  "2. SyntaxWarning: invalid escape sequence в scanner.py:1257 — заменить на raw-строку.",
  "3. PSH_PS_DEL.plp: for v_ps in this(idx).[B_PS] — отдельное правило, не suboptimal_query_wrownum.",
  "4. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1) — не коммитить.",
  "",
  "## Первые шаги чата 70",
  "1. Прочитать CHAT_RULES\\Старт новых чатов\\01_08 ...\\00_INDEX.md -> 01..08.",
  "2. Прочитать Отчеты\\69.Отчёт.txt.",
  "3. Взять долг №2 (SyntaxWarning в scanner.py:1257) или новую задачу.",
  "4. Действовать по регламентам: 04, 05, 06, 07, 61_1, 64_2, 64_3, 64_4, 65_1, 65_2, 66_1, 66_2, 67_1.",
  "",
  "## Правила PS (краткая выжимка)",
  "1-13, 60_1..60_9, 61_1..61_7, 62_1, 63_1, 64_1..64_4, 64_10, 65_1, 65_2, 66_1, 66_2, 67_1.",
  "",
]
write_no_bom(STA, NL.join(sta) + NL)
print("DONE")
