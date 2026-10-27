# -*- coding: utf-8 -*-
from pathlib import Path
PAM = Path(r"F:\TO_DBI\PS\CHAT_RULES\Отчеты\Памятка_чатов.txt")
REP = Path(r"F:\TO_DBI\PS\CHAT_RULES\Отчеты\69.Отчёт.txt")
NL = chr(10)
def write_no_bom(p, text):
    p.write_text(text, encoding="utf-8")
    b = p.read_bytes()
    bom = b.startswith(b"\xef\xbb\xbf")
    print(p.name, "bytes=", len(b), "bom=", bom)
    if bom: raise SystemExit("BOM not allowed: " + str(p))

# Памятка: дописать блок "Чат 69 — ЗАВЕРШЁН"
old = PAM.read_text(encoding="utf-8") if PAM.exists() else ""
blk = [
  "",
  "## Чат 69 (2026-10-27) — ЗАВЕРШЁН",
  "- Долг 1 (DS_187) ЗАКРЫТ: блок ВЫБОР ПОЛЬЗОВАТЕЛЯ в отчётах (md/html/VVVxVV).",
  "  gui_app.py: inject_user_selection_block/_html; fixer/code_fixer.py: save_scan_only_log",
  "  дописывает _generate_user_selection_lines. scanner.py НЕ менялся.",
  "- Снят UTF-8 BOM с gui_app.py (требование test_ds147c/d).",
  "- Коммит 8623af2, push origin/feature/dockerization. 3 files, +148/-1.",
  "- Тесты: точечный 7 passed; полный 385 passed, 1 failed.",
  "- 1 failed = test_ds182 NOT_MENTIONED — ПРЕДСУЩЕСТВУЮЩИЙ (baseline current=1, baseline=1). Долг 69->70.",
  "- Долги 69->70: DS_182 NOT_MENTIONED; SyntaxWarning обратного слэша-s в scanner.py:1257; PSH_PS_DEL.plp",
  "  for v_ps in this(idx).[B_PS] (отдельное правило, не wrownum).",
  "",
]
block = NL.join(blk)
if "## Чат 69 (2026-10-27) — ЗАВЕРШЁН" in old:
    print("[pam] уже есть — пропуск")
else:
    write_no_bom(PAM, old.rstrip() + NL + block + NL)

# Отчёт чата 69
rep = [
  "# Отчёт чата 69 (2026-10-27, LG)",
  "",
  "## Главное",
  "- Долг 1 чата 68 (DS_187) ЗАКРЫТ: блок ВЫБОР ПОЛЬЗОВАТЕЛЯ в отчётах трёх форматов.",
  "- scanner.py не менялся (по регламенту чата 68).",
  "- Коммит 8623af2, push origin/feature/dockerization.",
  "",
  "## Что сделано",
  "- 69_01: Памятка чатов обновлена (67_1).",
  "- 69_02..69_07: разведка generate_report (scanner.py:2108), _generate_user_selection_lines (L1991),",
  "  _generate_html_report (L2368), save_scan_only_log (code_fixer.py:2637), вызовы PLPlusScanner (gui_app.py:4014).",
  "- Установлено: в бою блок отсутствует во ВСЕХ трёх форматах.",
  "  .md: generate_report не вызывал метод; .html: self.user_selection не доходил; VVVxVV: save_scan_only_log не вызывал метод.",
  "- 69_08b: патч (Python-патчер, без scanner.py):",
  "  * code_fixer.py: save_scan_only_log дописывает scanner._generate_user_selection_lines() в try/except;",
  "  * gui_app.py: inject_user_selection_block (md) + inject_user_selection_html (html), идемпотентно,",
  "    вызовы после generate_report (L~4322/L~4326).",
  "- 69_08e: снят UTF-8 BOM с gui_app.py — это была единственная причина 31 failed + 8 errors полного прогона.",
  "- 69_08d/69_08f: точечный 7 passed; BOM-тесты 60 passed; полный 385 passed, 1 failed.",
  "- 69_08g: baseline на .ds187bak: test_ds182 падает так же (current=1, baseline=1) —",
  "  падение предсуществующее, к DS_187 не относится.",
  "- 69_09: коммит 8623af2 (3 files, +148/-1), push OK, статус без ahead.",
  "",
  "## Долги 69 -> 70",
  "2. SyntaxWarning: invalid escape sequence в scanner.py:1257 — заменить на raw-строку.",
  "3. PSH_PS_DEL.plp: for v_ps in this(idx).[B_PS] — отдельное правило, не suboptimal_query_wrownum.",
  "4. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1) — не коммитить.",
  "",
  "## Артефакты",
  "- Коммит: 8623af2.",
  "- Файлы: SRC/gui_app.py (M), SRC/fixer/code_fixer.py (M), SRC/tests/test_ds187_rubricator_user_in_reports.py (A).",
  "- Логи: F:\\TO_DBI\\PS\\LG_69_*.log.",
  "- Бэкапы: *.ds187bak (до патча), gui_app.py.ds187bom.bak (до снятия BOM).",
  "- Патчер: CHAT_RULES\\Скрипты чатов\\chat69_08b_patch.py.",
  "",
]
write_no_bom(REP, NL.join(rep) + NL)
print("DONE")
