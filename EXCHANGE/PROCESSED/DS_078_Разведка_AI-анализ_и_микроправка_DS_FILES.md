# DS_078 — Разведка AI-анализа + микроправка DS_FILES.md

Дата: 26.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: разведка + микроправка | Приоритет: высокий
Зависит от: DS_077 | Блокирует: DS_079
См.: DS_STANDARD.md (§2, §4), DS_CONTEXT.md (§9, §9.5), AGENTS.md («Логирование»),
     OUTBOX\DS_054_report.md, DS_067_report.md, DS_068_report.md

---

## §0. Микроправка DS_FILES.md (единственный правимый файл)

1. Шапка: версия `2.1 от 25.09.2026` → `2.2 от 26.09.2026 (после DS_075, DS_076, DS_077)`.
2. §4 (тесты): добавить `test_ds077.py` — «Регресс метрик отчётов (DS_077)».
3. §9: добавить запись DS_077 — `scanner.py` / `code_fixer.py` (две строки проблем при дублях); `SRC\tests\test_ds077.py`.
4. §9 заголовок: `## 9. Изменения 21.09.2026` → `## 9. История изменений`.

SRC, DATA, рубрикаторы — не трогать.

---

## 1. Цель

Read-only разведка AI-анализа (кроме §0):
1. Что реализовано: AI_IN/AI_OUT, кнопки «В AI»/«От AI», ai_exchange.py.
2. Что не реализовано: сам AI-анализ, заглушка `[AI]`, needs_ai_fix.
3. Что доработать для полноценного AI-анализа.

---

## 2. Точки разведки

| Объект | Файл / место |
|--------|--------------|
| Каталоги AI_IN / AI_OUT | EXCHANGE\AI_IN, EXCHANGE\AI_OUT |
| Формат запроса | ai_exchange.py — build_request_text |
| Формат ответа | ai_exchange.py — parse_response |
| send_to_ai | gui_app.py |
| receive_from_ai | gui_app.py |
| Кнопки btn_to_ai / btn_from_ai | gui_app.py:651–656 |
| _update_ai_button_state (управляет только btn_from_ai) | gui_app.py:860–877 |
| _poll_ai_out (таймер 5 c) | gui_app.py:879–… |
| needs_ai_fix | code_fixer.py:_verify_file (~1291) |
| Заглушка [AI] | code_fixer.py:save_scan_only_log (DS_067) |
| Правила AI | koda_prompts.py (маркер &debug) |

Что собрать (10 пунктов):
1. Схема AI_IN → файл → AI_OUT.
2. Формат файлов (примеры).
3. Шаги send_to_ai + зависимости.
4. Шаги receive_from_ai (парсинг, применение).
5. API ai_exchange.py (классы/функции).
6. Полный цикл needs_ai_fix (остаток issue + ai_fallback).
7. Условие и формат заглушки [AI].
8. Что не реализовано.
9. Почему btn_to_ai всегда active.
10. Открытые вопросы: API AI, формат ответа, применение результата.

**Тестовый прогон (для п.7 «что попадает в AI_IN»):**
`F:\TO_DBI\PATCH_IN\patch_WORK\src\ENTITY\DEPN` — использовать этот каталог как вход АРМ.
Полный patch_WORK не гонять; ограничиться DEPN.

---

## 3. Ограничения

- SRC\, DATA\, рубрикаторы — НЕ МЕНЯТЬ (кроме §0 — только DS_FILES.md).
- Полный patch_WORK не запускать.
- Логи: только EXCHANGE\bot.log. SRC\bot.log, SRC\*.log, EXCHANGE\LOG\* — запрещены.
- temp\ — писать можно.
- Расхождение с DS_CONTEXT.md §9.5 — доложить автору DS.

---

## 4. Зафиксировать

- Факты: пути, строки, имена функций.
- Схема AI_IN → AI → AI_OUT (диаграмма текстом).
- MD5: ai_exchange.py, gui_app.py, code_fixer.py, koda_prompts.py.
- Артефакты: temp\ds078_extract.json, temp\ds078_schema.md.

---

## 5. Отчёт (OUTBOX\DS_078_report.md)

Стандарт (DS_STANDARD.md §3) + разделы:

5.0. §0 — что стало: версия 2.2; §4 +test_ds077.py; §9 +DS_077.

5.1. Схема AI-обмена (уточнить по коду):
    [АРМ] send_to_ai → AI_IN/<запрос>
      ↓
    [внешний AI] (вручную?)
      ↓
    [АРМ] receive_from_ai ← AI_OUT/<ответ>

5.2. Что реализовано — таблица: Компонент | Файл | Функция | Что делает
     (AI_IN, AI_OUT, send_to_ai, receive_from_ai, ai_exchange.py, needs_ai_fix, заглушка [AI]).

5.3. Что НЕ реализовано — таблица: # | Что | Где должно быть.

5.4. Баг/недоделка btn_to_ai:
     — создаётся gui_app.py:651, не переводится в disabled;
     — _update_ai_button_state управляет только btn_from_ai;
     — Варианты: (A) disabled при отсутствии issues для AI; (B) всегда active — задокументировать.

5.5. Рекомендация для DS_079 — один абзац: с чего начать реализацию AI-анализа.

5.6. Результат прогона на DEPN:
     — сколько файлов обработано;
     — сколько попало в AI_IN (имена файлов);
     — что именно в них (по формату build_request_text);
     — есть ли ответы в AI_OUT (ожидаемо — нет).

---

## 6. Артефакты

- EXCHANGE\OUTBOX\DS_078_report.md
- temp\ds078_extract.json
- temp\ds078_schema.md
- EXCHANGE\DS_FILES.md (v2.2, только §0)