# DS_149 — Кнопки «Выделить все» / «Сбросить все» в дереве рубрикатора

**Дата:** 2026-10-14
**Ветка:** feature/dockerization
**Статус:** закрыт

---

## 1. Цель

Добавить в GUI возможность быстро включать/снимать все правила текущего рубрикатора одним кликом.

---

## 2. Что сделано

### 2.1. Кнопки над деревом

В gui_app.py над rules_tree добавлен rules_toolbar с двумя ttk.Button:
- «Выделить все» -> _select_all_current_rubricator;
- «Сбросить все» -> _deselect_all_current_rubricator.

Порядок pack: toolbar (TOP) -> scroll_y (RIGHT) -> scroll_x (BOTTOM) -> rules_tree (LEFT).

### 2.2. Методы

| Метод | Что |
|-------|-----|
| _get_current_rubricator_file_code() | file_code выделенного узла |
| _set_all_rules_for_current_rubricator(value) | установить все правила |
| _select_all_current_rubricator() | обёртка True |
| _deselect_all_current_rubricator() | обёртка False |

### 2.3. Тултипы

Через существующий class Tooltip:
- «Выделить все правила рубрикатора»;
- «Сбросить все правила рубрикатора».

### 2.4. Лог с полным путём

[OK] Создан: F:\TO_DBI\DATA\Тестовые файлы	est_*.plp

---

## 3. Артефакты

| Файл | Размер | BOM |
|------|--------|-----|
| SRC/gui_app.py | ~353435 B | False |
| EXCHANGE/DS_STANDARD.md | +§6.6.32 (69405 B) | False |
| EXCHANGE/OUTBOX/DS_149_report.md | новый | False |

---

## 4. Открытые вопросы

1. Клик по родителю — toggle детей? (Не сделано. Только кнопки.)
2. Тесты — AST-тесты не создавались.
3. Двойной клик по родителю — не сделано.

---

## 5. Рекомендации

1. DS_149a — toggle детей при клике на родителя (двойной клик).
2. DS_149b — тесты AST.

---

## 6. Коммиты

(заполняется при git commit)

