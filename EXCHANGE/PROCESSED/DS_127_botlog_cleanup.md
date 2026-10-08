# DS_127. Чистка bot.log от DS_086 + удаление L547 в gui_app.py

## Контекст

АРМ «Адаптация под DBI». Ветка feature/dockerization.
Роли: Автор DS — DeepSeek. Пользователь — Vitaly.
KODA не запускается (правило F, DS_125). Всё — вручную PowerShell.

## Проблема

bot.log содержал 448 записей "DS_086 GUI height: before=N, after=N"
и 488 пустых строк — 63% файла. Источник: gui_app.py L547 —
_bot_log() в методе _apply_ui_visibility(), вызывается при каждом
переключении меню «Вид» и при старте GUI.

Аналог: DS_082b (закрыт DS_121) — тот же паттерн в ai_local_worker.

## Цель

1. Удалить L547 в SRC\gui_app.py — прекратить запись.
2. Очистить bot.log от 448 записей DS_086 и 488 пустых строк.
3. Проверить bot.log на другие шумы (аудит).
4. Зафиксировать результаты.

## Изменения

### 1. SRC\gui_app.py

Удалена строка L547:
  self._bot_log(f"DS_086 GUI height: before={h_before}, after={h_after}")

Ошибки (L543, L568) остаются — они ценны.

### 2. EXCHANGE\bot.log

Одноразовая чистка Python-скриптом (tools\_ds127_clean_botlog.py,
удалён после использования):
- удалены пустые строки (488),
- удалены строки с 'DS_086 GUI height' (448),
- сохранено 484 записи.

Резервная копия: EXCHANGE\bot.log.bak_ds127 (ignored, локально).

Формат: UTF-8 без BOM, EOL=LF (соответствует .gitattributes).

### 3. Аудит остатков bot.log

Топ ключей после чистки:
- DS 082b (131) — историческое, закрыто DS_121, не трогаем.
- DS 082a (43) — историческое, не трогаем.
- (no-timestamp) (35) — многострочные записи DS 082b, формат DS_050
  нарушен; кандидат в DS_128.
- needs_manual (16) — легитимное.
- DS_998/999/997_Тест_* (по 15) — историческое (протокол DS_049).
- Кракозябры (2) — [������ ���������] DS_NOEXIST_999.md;
  кандидат в DS_128.

## Проверка

1. gui_app.py: синтаксис Python — OK.
2. bot.log: 484 строки, 95086 B.
3. DS_086 в bot.log: 0.
4. Пустых строк: 0.
5. BOM bot.log: False.
6. bot.log.bak_ds127: 1420 строк, 448 DS_086 (ignored).
7. git status: gui_app.py + bot.log modified.

## Отчёт

EXCHANGE\OUTBOX\DS_127_botlog_cleanup_report.md