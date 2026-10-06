# DS_CNT_013. Уточнение к DS_CNT_012: спорные моменты индексации

## Контекст
DS_CNT_012 выполнен. Определён оптимальный список для индексации:
~30 файлов (корень *.md, EXCHANGE\*.md, DATA\Рубрикатор v5\*.md,
.continue/rules/agents-short.md, PROJECT_STATUS\, PROMPTS\).
Исключено: SRC\, tools\, EXCHANGE-подкаталоги, PATCH_IN\, PATCH_OUT\,
logs\, .kilo\, reports\, temp\, JSON/SQL > 50 KB.

## Вопросы (8)

### Критичные

1. **`tools\` — исключать полностью или частично?**
   - `tools\_template_nightly.cmd` — шаблон ночной задачи;
   - `tools\run_cnt_*.cmd` — скрипты регламента;
   - `tools\indexer\cli.py` — CLI индексатора;
   - `tools\indexer\config.py` — конфиг (rate limit, чанк).
   Индексировать ли их? Если да — точечно или полностью?
   Если нет — как CNT найдёт «как запустить ночную задачу»,
   «какой rate limit»?

2. **Корневые `*.md` — все 10 актуальны?**
   - `AGENTS.md`, `README.md`, `DOCUMENTATION_ARM.md`,
     `ALGORITHM_FLOWCHART*.md`, `CHANGELOG.md`, `FIX_INSTRUCTIONS.md`,
     `RULES_SUMMARY.md`, `README_GIT.md`, `INSTRUCTIONS_ARH_RUN.md`.
   Какие **точно** актуальны? Какие устаревшие/разовые?

3. **Фильтр JSON/SQL > 50 KB — где реализовать?**
   - В `reader.py`?
   - В `.continueignore`?
   Есть ли в `DATA\` важные JSON < 50 KB? Важные JSON > 50 KB?

### Важные

4. **`PROJECT_STATUS\` и `PROMPTS\` — актуальны?**
   - `PROJECT_STATUS\PROJECT_STATUS.md` — как часто обновляется?
   - `PROMPTS\DS_PROJECT_CONTEXT.md` — актуален?

5. **`EXCHANGE\CNT_config_example.yaml` — актуален?**
   Не дублирует ли `agents-short.md` или регламент?

6. **`DATA\` — другие подкаталоги с документами?**
   Только `Рубрикатор v5` и `OUTERS`? Или есть ещё?

### Проверочные

7. **Overlap 64 vs 32 — почему 64?**
   Для 30 файлов это критично?

8. **`tools\indexer\*.py` — индексировать?**
   CNT может спрашивать «как работает индексатор»?

## Формат ответа
По `EXCHANGE\DS_089b_report.md`:
- Ответы на 8 вопросов;
- Итоговые списки (индексировать / исключить);
- Корректировки к DS_CNT_012;
- Следующие шаги.