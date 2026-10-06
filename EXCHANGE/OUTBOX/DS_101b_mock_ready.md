# DS_101b — Мок-сервер Ollama: готов

**Дата:** 07.10.2026
**Статус:** Выполнено

---

## 1. Файл создан

| Параметр | Значение |
|----------|----------|
| Путь | `tools\mock_ollama_invalid.py` |
| Размер | 5 525 байт |
| Дата создания | 07.10.2026 03:24:56 |
| Первые 3 байта (hex) | `22 22 22` (UTF-8 без BOM, `"""`) |
| Строк | 168 |

---

## 2. py_compile

```
python -m py_compile tools\mock_ollama_invalid.py
```

Результат: RC 0 (успех).

---

## 3. Проверка GET /api/tags

Запрос: `Invoke-RestMethod http://localhost:11500/api/tags`

Ответ:
```json
{
    "models": [
        {
            "name": "qwen2.5-coder:7b",
            "model": "qwen2.5-coder:7b"
        }
    ]
}
```

Счётчик POST не увеличился (в логе: `req#? GET /api/tags → ok`).

---

## 4. Проверка POST /api/chat — запрос №1 (невалидный)

Тело запроса содержало 3 issues (`line 1,`, `line 2,`, `line 3,`).

Ответ `message.content`: `"not a valid json at all"`

В логе: `req#1 POST /api/chat → invalid`

---

## 5. Проверка POST /api/chat — запрос №2 (валидный)

Тот же запрос. Ответ `message.content`:

```json
[
  {"line": 1, "after": "mock fixed line", "reason": "mock fallback test", "confidence": 0.95},
  {"line": 2, "after": "mock fixed line", "reason": "mock fallback test", "confidence": 0.95},
  {"line": 3, "after": "mock fixed line", "reason": "mock fallback test", "confidence": 0.95}
]
```

3 элемента — по числу `line N,` в user content.

В логе: `req#2 POST /api/chat → valid`

---

## 6. Управление

**Запуск:**
```
python tools\mock_ollama_invalid.py --port 11500 --fail-first
```

**Остановка:** Ctrl+C → вывод `mock-ollama stopped`.

**Параметры CLI:**
- `--port N` (default 11500)
- `--host H` (default localhost)
- `--fail-first` (default True)
- `--fail-count K` (default 1)
- `--fail-content STR` (default "not a valid json at all")
- `--default-count N` (default 10)

---

## 7. Ограничения соблюдены

- SRC не тронут.
- Реальная Ollama (порт 11434) не затронута.
- ai_local_worker не запускался.
- Git/push/GP не выполнялись.

---

## 8. Итог

Мок-сервер `tools\mock_ollama_invalid.py` готов к использованию. Поведение подтверждено: невалидный JSON на запросе №1, валидный массив фиксов с полями `line`/`after`/`reason`/`confidence` на последующих запросах.
