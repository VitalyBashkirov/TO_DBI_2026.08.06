# DS_109. Регламент имён отчётов KODA + финальный GP DS_106

**Дата:** 07.10.2026
**Автор:** DeepSeek (DS)
**Исполнитель:** KODA
**Приоритет:** средний
**Связано:** DS_103 (ручной GUI-прогон), DS_106 (GP), DS_108 (фиксы GUI), DS_104 (гигиена репо), DS_STANDARD.md §3.1, §6.1

---

## 0. Контекст (важно!)

**DS_106 (GP) уже выполнен** — коммит `4bd51b3` «DS_103 + DS_108: GUI-прогон (успех) + фиксы GUI», push в `origin/feature/dockerization` успешен (`3bf2b26..4bd51b3`).

Однако в рабочем дереве остались **незакоммиченными**:
- `M EXCHANGE/bot.log`
- `?? EXCHANGE/OUTBOX/DS_106_final_gp_report.md`
- `?? EXCHANGE/PROCESSED/DS_106_final_gp.md`

И **не переименован** отчёт DS_103: в `4bd51b3` вошёл как `EXCHANGE/OUTBOX/DS_103_report.md` (старое имя).

**DS_109 закрывает:**
1. Регламент имён отчётов KODA (новый §3.2 в DS_STANDARD.md + правки AGENTS.md).
2. Переименование `DS_103_report.md` → `DS_103_gui_manual_run_report.md` (`git mv`).
3. Финальный GP: дозакоммитить DS_106-файлы + `bot.log` + правки DS_109 + переименование DS_103.

---

## 1. Цель

1. Устранить противоречия в регламенте имён отчётов KODA:
   - `AGENTS.md:284` — `DS_XXX_отчет.md` (транслит, нет краткого описания);
   - `DS_STANDARD.md:32, 175, 262` — `DS_XXX_report.md` (нет краткого описания).
2. Привести в соответствие с DS_104 раздел «НЕ версионируются» в `AGENTS.md:393`.
3. Переименовать единственный существующий отчёт с неверным именем:
   `EXCHANGE/OUTBOX/DS_103_report.md` → `EXCHANGE/OUTBOX/DS_103_gui_manual_run_report.md`.
4. Зафиксировать финальный GP:
   - `EXCHANGE/bot.log` (записи DS_106/DS_108, уже M);
   - `EXCHANGE/OUTBOX/DS_106_final_gp_report.md` (untracked);
   - `EXCHANGE/PROCESSED/DS_106_final_gp.md` (untracked);
   - `EXCHANGE/OUTBOX/DS_103_gui_manual_run_report.md` (после `git mv`);
   - `EXCHANGE/DS_STANDARD.md` (новый §3.2 + замены);
   - `AGENTS.md` (правки строк 284, 393);
   - `EXCHANGE/PROCESSED/DS_109_report_naming_convention.md` (задание DS_109);
   - `EXCHANGE/OUTBOX/DS_109_report_naming_convention_report.md` (отчёт KODA по DS_109).

---

## 2. Задача 1 — новый §3.2 в `EXCHANGE\DS_STANDARD.md`

**Файл:** `EXCHANGE\DS_STANDARD.md`

**Действие 1:** вставить новый подраздел **сразу после §3.1 «Язык отчёта»** (перед следующим `###`).

**Текст для вставки:**

```markdown
### 3.2. Имена файлов отчётов KODA

Отчёты KODA размещаются в `EXCHANGE\OUTBOX\` и именуются по шаблону:

**`DS_XXX_краткое_описание_report.md`**

где:
- `XXX` — номер DS (например, `103`, `108`, `109`),
- `краткое_описание` — латиница, `snake_case`, без пробелов
  (например, `gui_manual_run`, `gui_fixes_rescan_ui`, `final_gp`),
- `_report` — обязательный суффикс отчёта.

**Примеры:**
- `DS_103_gui_manual_run_report.md`
- `DS_108_gui_fixes_rescan_ui_report.md`
- `DS_109_report_naming_convention_report.md`

**Задания DS (исполненные)** переносятся KODA в `EXCHANGE\PROCESSED\`
с тем же базовым именем, но **без** суффикса `_report`:
- `DS_103_gui_manual_run_report.md` (отчёт) → `DS_103_gui_manual_run.md` (задание).
- `DS_108_gui_fixes_rescan_ui_report.md` (отчёт) → `DS_108_gui_fixes_rescan_ui.md` (задание).

**ЗАПРЕЩЕНО:**
- Имена без краткого описания: `DS_XXX_report.md`.
- Транслит: `DS_XXX_отчет.md`, `DS_XXX_otchet.md`.
- Пробелы в имени файла.

**Область применения:** с DS_109 вперёд. Исторические отчёты
(`DS_100a_report.md`, `DS_101*`, `DS_102_report.md`, `DS_104_report.md`,
`DS_105_report.md`, `DS_107_report.md`) **не переименовываются** —
во избежание разрыва ссылок в `bot.log` и `PROCESSED`.