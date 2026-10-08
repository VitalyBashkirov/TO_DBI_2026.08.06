# DS_125 — .gitattributes + уроки чата 21

## Контекст

Чат 21 выявил практические грабли PowerShell и пробелы в процессе.
Фиксируем в DS_STANDARD.md и AGENTS.md. Плюс .gitattributes не покрывал *.log.

## Файлы

1. F:\TO_DBI\.gitattributes
2. F:\TO_DBI\AGENTS.md
3. F:\TO_DBI\EXCHANGE\DS_STANDARD.md

## Правка 1 — .gitattributes

Добавлено: *.log text eol=lf (в раздел Data / config / scripts).

## Правка 2 — AGENTS.md (после L608, перед "### Что не делать")

Добавлены два подраздела:
- ### Простые DS — без KODA (DS_125)
- ### INBOX-гигиена при ручном выполнении DS (DS_125)

## Правка 3 — DS_STANDARD.md §6.2.1

Добавлен подраздел "6.2.1. Практические грабли PowerShell (DS_125)":
- -SimpleMatch не понимает |
- Select-String находит docstring и сигнатуры
- ReadAllBytes/WriteAllText — только абсолютные пути

## Правка 4 — DS_STANDARD.md §3.2

Добавлен абзац "Плоский формат для INBOX-заданий (DS_125)":
- вложенные блоки кода ломают разметку при Text Copy Download
- решение: отступы (4 пробела) вместо блоков кода

## Ограничения

- Сохранить UTF-8 без BOM.
- Не менять существующий текст (только вставки).

## Проверка (§5)

1. .gitattributes: *.log — L15.
2. AGENTS.md: Простые DS — L610; INBOX-гигиена — L624.
3. DS_STANDARD.md: §6.2.1 — L326; Плоский формат — L116.
4. BOM: все три файла False.
5. git diff --stat: 3 files changed, 50 insertions(+), 1 deletion(-).

## Ожидаемый результат

- .gitattributes покрывает *.log (warning LF->CRLF исчезнет).
- AGENTS.md содержит правила Простые DS и INBOX-гигиена.
- DS_STANDARD.md содержит §6.2.1 и правило плоского формата.