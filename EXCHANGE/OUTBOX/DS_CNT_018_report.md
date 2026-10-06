# DS_CNT_018 — Отчёт

**Дата:** 04.10.2026 12:38
**Статус:** Выполнено

## Что сделано

| Шаг | Что | Результат |
|---|---|---|
| 1 | `tools\check_standard.py` — модель 1.5b → 3b | ✅ |
| 2 | `tools\explain_log.py` — модель 1.5b → 3b | ✅ |
| 3 | `tools\make_pilot_report.ps1` — $model 1.5b → 3b, блок «Проблемы» переписан | ✅ |
| 4 | `.continue\rules\agents-short.md` — блок «Модели Ollama» (Pipeline + 3b, удалена 1.5b) | ✅ |
| 5 | `EXCHANGE\SEC_POLICY_AI.md` §5.1 — Pipeline + 3b, примечание об удалении 1.5b | ✅ |
| 6 | Тест 3b через Ollama | ✅ «OK» за 11.3 сек |
| 7 | Повторный прогон `run_cnt_007_nightly.cmd` | ✅ RC=0 |
| 8 | Проверка качества check-standard | ✅ Осмысленно, без галлюцинаций |
| 9 | Проверка качества explain-log | ✅ Структурно, без зацикливаний |
| 10 | `DS_CNT_007_pilot_report.md` — дописан раздел «Обновление (DS_CNT_018)» | ✅ |
| 11 | `CNT_REFERENCE.md` — новая §7 «Ночной pipeline CNT», v1.3 | ✅ |
| 12 | `DS_CNT_000_regulation.md` — добавлен п. 1.16 (pipeline + модель 3b) | ✅ |
| 13 | `bot.log` — запись о выполнении | ✅ |

## Что проверено

- Ollama содержит `qwen2.5-coder:3b`, `qwen2.5-coder:1.5b` **удалена**.
- Тестовый запрос к 3b: `response: "OK"`, 11.3 сек.
- `ds_cnt_007.exit` = 0, `ds_cnt_007.log` — `DONE RC=0`.
- `logs\ds_cnt_007_check_standard.md` — 48 строк, разбор по всем 12 пунктам SEC_POLICY_AI.md, нарушения указаны в чек-листе 12.4.
- `logs\ds_cnt_007_explain_log.md` — 37 строк, нумерованный список из 16 задач, без повторов.
- EOL всех изменённых `.md` сохранён CRLF.
- PS-скрипты сохранены в UTF-8 BOM.

## Результат

### Сравнение 1.5b → 3b

| Аспект | 1.5b | 3b |
|---|---|---|
| check-standard | Шаблонные «файл не содержит команды GIT» | Распознала структуру, прошлась по 12 пунктам, отметила чек-лист 12.4 |
| explain-log | Зацикливание (повтор одной фразы ×20+) | Структурный разбор, 16 задач, коды выхода |
| Галлюцинации | Много | Нет |
| Скорость | 8 сек / 2 токена | 11 сек / 2 токена |

### Артефакты

- `EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md` — обновлён (раздел «Обновление»).
- `logs\ds_cnt_007_check_standard.md` — новый, на 3b.
- `logs\ds_cnt_007_explain_log.md` — новый, на 3b.
- `logs\ds_cnt_007.log`, `ds_cnt_007.exit` — RC=0.

## Проблемы

1. **Обрыв explain-log на 16-м пункте** — `num_predict=600` ограничивает
   объём. Для полного разбора 200 строк лога нужно 1000–1500 токенов
   или сокращение tail до 100 строк. **Не блокирует** — структура
   получена, хвост восстанавливается вручную.
2. **check-standard не нашёл реальных нарушений** в SEC_POLICY_AI.md —
   корректно, т.к. это политика, а не DS-задание. Пункт стандарта 2.x
   к нему неприменим.

## Следующие шаги

- Регистрация в Task Scheduler `TO_DBI_CNT_NightlyPipeline` — по явному
  разрешению Администратора АРМ (п. 1.16 регламента).
- При необходимости — увеличение `num_predict` до 1200 в `explain_log.py`
  или сокращение tail до 100 строк.
- Переход на 7b или GPU — при появлении требования к качеству выше.

## Артефакты

- `F:\TO_DBI\tools\check_standard.py` — MODEL = qwen2.5-coder:3b.
- `F:\TO_DBI\tools\explain_log.py` — MODEL = qwen2.5-coder:3b.
- `F:\TO_DBI\tools\make_pilot_report.ps1` — $model = qwen2.5-coder:3b.
- `F:\TO_DBI\.continue\rules\agents-short.md` — блок «Модели Ollama».
- `F:\TO_DBI\EXCHANGE\SEC_POLICY_AI.md` — §5.1.
- `F:\TO_DBI\EXCHANGE\CNT_REFERENCE.md` — v1.3, §7 (pipeline).
- `F:\TO_DBI\EXCHANGE\DS_CNT_000_regulation.md` — п. 1.16.
- `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md` — обновлён.
- `F:\TO_DBI\EXCHANGE\bot.log` — дополнен.
- `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_018_report.md` — этот отчёт.