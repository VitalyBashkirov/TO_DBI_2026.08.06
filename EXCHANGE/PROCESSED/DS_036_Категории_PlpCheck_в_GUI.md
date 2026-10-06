DS_036 — Добавление флагов категорий PlpCheck в GUI
Метаданные задачи
Параметр	Значение
Код задачи	DS_036
Проект	АРМ «Адаптация под DBI» (Народный банк)
Предыдущие задачи	DS_032, DS_033, DS_035
Приоритет	HIGH
Статус	К выполнению
Исполнитель	KODA (VS Code)
Репозиторий	F:\TO_DBI\
Файл GUI	F:\TO_DBI\gui_app.py
Файл сканера	F:\TO_DBI\scanner.py
Источник категорий	2.RUBRICATOR_CATEGORIES v5.md
Источник CHECK-значений	scan_report_patch_REPS_EXP_115_1_20260912_203341.md
Контекст задачи
Текущее состояние
На форме GUI есть один чекбокс для правил PlpCheck:

☐ «2. Рубрикатор PlpCheck»

Он включает все правила PlpCheck скопом. Пользователь не может отключить часть правил или выбрать только нужные категории.

Целевое состояние
Заменить один чекбокс на группу:

Один чекбокс-родитель — «2. Рубрикатор PlpCheck».

Восемь дочерних чекбоксов — 7 категорий из 2.RUBRICATOR_CATEGORIES v5.md + OTHER (прочие).

Чекбокс «Выбрать все PlpCheck-категории».

Соответствие категорий и CHECK-значений
В отчёте scan_report_patch_REPS_EXP_115_1_20260912_203341.md (26 проблем) присутствуют 5 CHECK-значений:

CHECK	Кол-во в отчёте	Пример ERROR
bad_prefix	9	Не корректный префикс, пожалуйста переименуйте в "v_iDp"
not_mentioned	5	Переменная fmt24 более нигде не упоминается.
prefix_type_in_var_name	5	Наименование переменной не содержит префикс типа, пожалуйста переименуйте в "rP_PARAM"
wrong_method_syntax	1	Обращение к методу должно быть в формате ::[RUNTIME].[STR]
code_in_comment	4	Удалите закомментированный код
Итого: 26 проблем.

Таблица: категория → CHECK-значения
N	Код категории	Описание	CHECK-значения (из отчёта)
31	PLSQL.OPTIMIZATION	Оптимизация (2L/перевызов БД)	— (в отчёте нет)
32	JAVA.OPTIMIZATION	Оптимизация (СП/Java)	— (в отчёте нет)
33	DBI.ADAPTATION	Адаптация под PostgreSQL	— (в отчёте нет)
34	SQL.CHECKS	Проверки чистого SQL	— (в отчёте нет)
35	WEB.ADAPTATION	Адаптация под Веб-Навигатор	— (в отчёте нет)
36	STYLE.PREFIXES	Префиксы и оформление	bad_prefix, not_mentioned, wrong_method_syntax, code_in_comment
37	STYLE.PREFIX_COMBINATION	Комбинированные префиксы	prefix_type_in_var_name
—	OTHER	Прочие PlpCheck-правила	— (в отчёте нет)
ВАЖНО: Соответствие условное, основано на семантике названий CHECK-правил. Требуется уточнение через ЗАДАЧУ 4 (сбор реальных category/subcategory из 4.RUBRICATOR_PROMPT v5.json).

Поведение (уточнено пользователем)
Ситуация	Поведение
Рубрикатор PlpCheck НЕ выбран	Все 8 категорий — отключены и недоступны (disabled)
Рубрикатор PlpCheck выбран, все категории сняты	При нажатии кнопок «Сканировать», «Исправлять код», «Генерация тестовых .plp» — предупреждение
Рубрикатор PlpCheck выбран, хотя бы одна категория включена	Работает штатно: применяются только правила выбранных категорий
Все категории включены	Работает как раньше: все правила PlpCheck применяются
По умолчанию: рубрикатор PlpCheck выключен; все 8 категорий включены, но disabled.

Задачи KODA
ЗАДАЧА 1 — Изучить текущую структуру GUI
Файл: F:\TO_DBI\gui_app.py

Действие: Найти фрагмент, где создаётся чекбокс «2. Рубрикатор PlpCheck» (или аналог).

Скопировать:

Строку инициализации переменной (например, self.var_add_plpcheck = tk.BooleanVar()).

Строку создания Checkbutton.

Место, где переменная читается и передаётся в scanner.py.

Место, где переменная сохраняется в конфиг.

Список кнопок «Сканировать», «Исправлять код», «Генерация тестовых .plp» — их команды и методы-обработчики.

Прислать: полный текст фрагментов (с номерами строк).

ЗАДАЧА 2 — Изучить структуру selected_rules
Действие: Найти метод, формирующий selected_rules.

Прислать: полный текст метода.

ЗАДАЧА 3 — Изучить фильтрацию правил PlpCheck в scanner.py
Файл: F:\TO_DBI\scanner.py

Действие: Найти в _load_patterns_from_rubricator() блок фильтрации по selected_rules.

Прислать: фрагмент.

ЗАДАЧА 4 — Собрать уникальные category/subcategory правил PlpCheck
Действие: Создать временный скрипт temp\collect_plpcheck_categories.py:

python
import json
from pathlib import Path

RUBRICATOR = Path(r"F:\TO_DBI\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json")

with open(RUBRICATOR, 'r', encoding='utf-8') as f:
    data = json.load(f)

rules = data.get('rules', {})
plpcheck_rules = {k: v for k, v in rules.items() if k.startswith('plpcheck.')}
print(f"Всего правил PlpCheck: {len(plpcheck_rules)}")

categories = {}
for key, rule in plpcheck_rules.items():
    cat = rule.get('category', 'N/A')
    subcat = rule.get('subcategory', 'N/A')
    categories.setdefault((cat, subcat), []).append(key)

print("\n=== Уникальные (category, subcategory) ===")
for (cat, subcat), keys in sorted(categories.items()):
    print(f"{cat:15} | {subcat:30} | {len(keys):3} правил")
    for k in keys:
        print(f"    - {k}")
Действие: Запустить скрипт. Прислать полный вывод.

ЗАДАЧА 5 — Построить маппинг rule_key → category_code
Действие: На основе ЗАДАЧИ 4 создать в scanner.py таблицу маппинга:

python
# DS 036: Маппинг правил PlpCheck на 7 категорий + OTHER
PLPCHECK_RULE_TO_CATEGORY: Dict[str, str] = {
    # STYLE.PREFIXES
    'plpcheck.BAD_PREFIX': 'STYLE.PREFIXES',
    'plpcheck.NOT_MENTIONED': 'STYLE.PREFIXES',
    'plpcheck.CODE_IN_COMMENT': 'STYLE.PREFIXES',
    'plpcheck.WRONG_METHOD_SYNTAX': 'STYLE.PREFIXES',
    'plpcheck.WRONG_LOCAL_PREFIX': 'STYLE.PREFIXES',
    'plpcheck.RESERVED_PREFIX': 'STYLE.PREFIXES',
    # STYLE.PREFIX_COMBINATION
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'STYLE.PREFIX_COMBINATION',
    # DBI.ADAPTATION
    'plpcheck.OUTER_JOIN': 'DBI.ADAPTATION',
    'plpcheck.CONNECTBY2WITH': 'DBI.ADAPTATION',
    'plpcheck.JSON_TYPES': 'DBI.ADAPTATION',
    'plpcheck.ROWNUM': 'DBI.ADAPTATION',
    # SQL.CHECKS
    'plpcheck.PURE_SQL_DBLINK': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_OUTER_JOIN': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_MINUS_NOT_DBI': 'SQL.CHECKS',
    # WEB.ADAPTATION
    'plpcheck.VBS_LINKING_ERROR': 'WEB.ADAPTATION',
    'plpcheck.WEB_NOT_IMPLEMENTED': 'WEB.ADAPTATION',
    # OTHER (прочие)
    'plpcheck.SYNTAX_ERROR': 'OTHER',
    'plpcheck.VARIABLE_SAME_NAME': 'OTHER',
    # ... дополнить по выводу ЗАДАЧИ 4
}
ЗАДАЧА 6 — Добавить константы в gui_app.py
Файл: F:\TO_DBI\gui_app.py

Действие: В начало модуля добавить:

python
# DS 036: Категории PlpCheck из 2.RUBRICATOR_CATEGORIES v5.md
# Для каждой категории указаны CHECK-значения (из scan_report_patch_REPS_EXP_115_1_20260912_203341.md)
PLPCHECK_CATEGORIES = [
    ('PLSQL.OPTIMIZATION',       'Оптимизация (2L/перевызов БД)',   ''),
    ('JAVA.OPTIMIZATION',        'Оптимизация (СП/Java)',           ''),
    ('DBI.ADAPTATION',           'Адаптация под PostgreSQL',        ''),
    ('SQL.CHECKS',               'Проверки чистого SQL',            ''),
    ('WEB.ADAPTATION',           'Адаптация под Веб-Навигатор',     ''),
    ('STYLE.PREFIXES',           'Префиксы и оформление',
        'bad_prefix, not_mentioned, wrong_method_syntax, code_in_comment'),
    ('STYLE.PREFIX_COMBINATION', 'Комбинированные префиксы',
        'prefix_type_in_var_name'),
    ('OTHER',                    'Прочие PlpCheck-правила',          ''),
]
Структура: (код_категории, описание, check_значения_через_запятую).

ЗАДАЧА 7 — Реализовать UI группы флагов
Файл: F:\TO_DBI\gui_app.py

Действие: Найти секцию с чекбоксом «2. Рубрикатор PlpCheck». Заменить на:

python
# DS 036: Чекбокс-родитель "2. Рубрикатор PlpCheck"
self.var_add_plpcheck = tk.BooleanVar(value=False)
self.chk_add_plpcheck = tk.Checkbutton(
    parent_frame,
    text="2. Рубрикатор PlpCheck",
    variable=self.var_add_plpcheck,
    command=self._on_plpcheck_toggle
)
self.chk_add_plpcheck.pack(anchor='w')

# DS 036: Контейнер для дочерних категорий
self.frame_plpcheck_categories = tk.Frame(parent_frame)
self.frame_plpcheck_categories.pack(anchor='w', padx=(20, 0))

# DS 036: Чекбокс "Выбрать все PlpCheck-категории"
self.var_plpcheck_all = tk.BooleanVar(value=True)
self.chk_plpcheck_all = tk.Checkbutton(
    self.frame_plpcheck_categories,
    text="☑ Выбрать все PlpCheck-категории",
    variable=self.var_plpcheck_all,
    command=self._toggle_all_plpcheck_categories,
    state='disabled'
)
self.chk_plpcheck_all.pack(anchor='w')

# DS 036: 8 чекбоксов категорий (7 + OTHER) с CHECK-значениями
self.var_plpcheck_categories = {}
self.chk_plpcheck_categories = {}
for code, descr, checks in PLPCHECK_CATEGORIES:
    var = tk.BooleanVar(value=True)
    self.var_plpcheck_categories[code] = var
    
    # DS 036: формируем текст с CHECK-значениями
    if checks:
        text = f"    PlpCheck: {code} — {descr}  [CHECK: {checks}]"
    else:
        text = f"    PlpCheck: {code} — {descr}"
    
    chk = tk.Checkbutton(
        self.frame_plpcheck_categories,
        text=text,
        variable=var,
        command=self._update_plpcheck_all_checkbox,
        state='disabled',
        anchor='w',
        justify='left'
    )
    chk.pack(anchor='w', fill='x')
    self.chk_plpcheck_categories[code] = chk
Примечание: если строка с [CHECK: ...] получается слишком длинной — можно вынести CHECK-значения в tooltip (всплывающую подсказку) или отдельную метку под чекбоксом серым цветом. Пример с отдельной меткой:

python
for code, descr, checks in PLPCHECK_CATEGORIES:
    var = tk.BooleanVar(value=True)
    self.var_plpcheck_categories[code] = var
    
    chk = tk.Checkbutton(
        self.frame_plpcheck_categories,
        text=f"    PlpCheck: {code} — {descr}",
        variable=var,
        command=self._update_plpcheck_all_checkbox,
        state='disabled',
        anchor='w'
    )
    chk.pack(anchor='w')
    self.chk_plpcheck_categories[code] = chk
    
    # DS 036: CHECK-значения серым текстом под чекбоксом
    if checks:
        lbl = tk.Label(
            self.frame_plpcheck_categories,
            text=f"        CHECK: {checks}",
            font=('Segoe UI', 8),
            fg='#666666',
            anchor='w'
        )
        lbl.pack(anchor='w', padx=(20, 0))
Действие: Реализовать методы:

python
def _on_plpcheck_toggle(self):
    """DS 036: Включить/отключить доступность дочерних чекбоксов PlpCheck."""
    enabled = self.var_add_plpcheck.get()
    state = 'normal' if enabled else 'disabled'
    
    self.chk_plpcheck_all.config(state=state)
    for chk in self.chk_plpcheck_categories.values():
        chk.config(state=state)

def _toggle_all_plpcheck_categories(self):
    """DS 036: Установить/снять все флаги PlpCheck-категорий."""
    if not self.var_add_plpcheck.get():
        return
    value = self.var_plpcheck_all.get()
    for var in self.var_plpcheck_categories.values():
        var.set(value)

def _update_plpcheck_all_checkbox(self):
    """DS 036: Синхронизировать флаг 'Выбрать все' с состоянием категорий."""
    if not self.var_add_plpcheck.get():
        return
    all_selected = all(var.get() for var in self.var_plpcheck_categories.values())
    self.var_plpcheck_all.set(all_selected)

def _has_selected_plpcheck_categories(self) -> bool:
    """DS 036: Есть ли хотя бы одна выбранная категория PlpCheck."""
    if not self.var_add_plpcheck.get():
        return True
    return any(var.get() for var in self.var_plpcheck_categories.values())

def _check_plpcheck_categories_before_action(self) -> bool:
    """
    DS 036: Проверка перед действиями (Сканировать, Исправлять, Генерация).
    Возвращает True, если можно продолжать; False — если пользователь отменил.
    """
    if not self.var_add_plpcheck.get():
        return True
    
    if self._has_selected_plpcheck_categories():
        return True
    
    result = messagebox.askyesno(
        "PlpCheck: категории не выбраны",
        "Рубрикатор PlpCheck выбран, но ни одна категория не отмечена.\n\n"
        "PlpCheck-правила не будут применены.\n\n"
        "Продолжить без PlpCheck-правил?",
        icon='warning'
    )
    return result
ЗАДАЧА 8 — Обновить формирование selected_rules
Действие: Найти метод get_selected_rules(). Изменить:

python
def get_selected_rules(self):
    """DS 036: Формирование selected_rules с учётом категорий PlpCheck."""
    rules = []
    
    if self.var_add_v53.get():
        rules.append('v53')
    if self.var_add_tds.get():
        rules.append('тдс20240828')
    if self.var_add_tkloik.get():
        rules.append('тклоик20240828')
    
    if self.var_add_plpcheck.get():
        rules.append('PlpCheck')
        self.plpcheck_categories_filter = [
            code for code, var in self.var_plpcheck_categories.items()
            if var.get()
        ]
    else:
        self.plpcheck_categories_filter = []
    
    return rules
ЗАДАЧА 9 — Передать фильтр категорий в сканер
Файл: F:\TO_DBI\scanner.py

Действие: В PLPlusScanner.__init__() добавить параметр:

python
def __init__(
    self,
    config: dict,
    selected_rules: List[str] = None,
    rubricator_prompts=None,
    plpcheck_categories: List[str] = None   # DS 036
):
    self.config = config
    self.selected_rules = selected_rules or []
    self.plpcheck_categories = plpcheck_categories or []
    # ... остальное без изменений
Действие: В _load_patterns_from_rubricator() найти блок фильтрации PlpCheck и добавить:

python
# DS 036: фильтрация правил PlpCheck по категориям
if file_code.lower() == 'plpcheck':
    if not self.plpcheck_categories:
        print(f"[DS 036] Правило {rule_key} пропущено (ни одна категория не выбрана)")
        continue
    
    rule_category = PLPCHECK_RULE_TO_CATEGORY.get(rule_key, 'OTHER')
    
    if rule_category not in self.plpcheck_categories:
        print(f"[DS 036] Правило {rule_key} пропущено (категория {rule_category} не выбрана)")
        continue
Действие: В gui_app.py при создании PLPlusScanner передать plpcheck_categories:

python
scanner = PLPlusScanner(
    config=self.config,
    selected_rules=self.get_selected_rules(),
    rubricator_prompts=self.rubricator,
    plpcheck_categories=getattr(self, 'plpcheck_categories_filter', [])
)
ЗАДАЧА 10 — Предупреждение перед кнопками
Действие: Найти обработчики кнопок:

«Сканировать».

«Исправлять код».

«Генерация тестовых .plp».

В начало каждого обработчика добавить:

python
def on_scan_click(self):
    if not self._check_plpcheck_categories_before_action():
        return
    # ... остальной код
Импорт (если нет): from tkinter import messagebox.

ЗАДАЧА 11 — Сохранить/загрузить настройки
Действие: В save_config():

python
config['scan']['plpcheck_enabled'] = self.var_add_plpcheck.get()
config['scan']['plpcheck_categories'] = [
    code for code, var in self.var_plpcheck_categories.items()
    if var.get()
]
Действие: В load_config():

python
enabled = config.get('scan', {}).get('plpcheck_enabled', False)
self.var_add_plpcheck.set(enabled)

saved_categories = config.get('scan', {}).get('plpcheck_categories', None)
if saved_categories is None:
    saved_categories = [code for code, _, _ in PLPCHECK_CATEGORIES]

for code, var in self.var_plpcheck_categories.items():
    var.set(code in saved_categories)

self._on_plpcheck_toggle()
self._update_plpcheck_all_checkbox()
ЗАДАЧА 12 — Проверить работу
Действие: Запустить GUI, проверить сценарии:

№	Сценарий	Ожидаемое поведение
1	Первый запуск	PlpCheck выключен, 8 чекбоксов включены, но disabled
2	Клик на «2. Рубрикатор PlpCheck»	Чекбоксы становятся доступными
3	Клик на «Выбрать все PlpCheck-категории» (снятие)	Все 8 чекбоксов снимаются
4	Клик на «Сканировать» при снятых категориях	Предупреждение
5	Отмена в предупреждении	Сканирование не запускается
6	Согласие в предупреждении	Сканирование запускается без PlpCheck
7	Снятие галочки с PlpCheck	Все 8 чекбоксов становятся disabled
8	Снятие только STYLE.PREFIXES	В отчёте нет bad_prefix, not_mentioned, code_in_comment, wrong_method_syntax
9	Снятие только STYLE.PREFIX_COMBINATION	В отчёте нет prefix_type_in_var_name
10	Сохранение/загрузка конфига	Выбранные категории восстанавливаются
Прислать:

Скриншоты GUI (PlpCheck выключен, включён, категории сняты).

Скриншот предупреждения.

Отчёт scan_report_*.md с фильтрацией по категориям.

Содержимое config.json.

Критерии приёмки DS_036
№	Критерий	Признак выполнения
1	Родительский чекбокс «2. Рубрикатор PlpCheck»	Работает
2	8 дочерних чекбоксов (7 + OTHER)	Отображаются
3	CHECK-значения видны в описании категорий	Скриншот
4	Чекбокс «Выбрать все»	Синхронизирован
5	PlpCheck выключен → дочерние disabled	Скриншот
6	PlpCheck включён → дочерние доступны	Скриншот
7	Все категории сняты + кнопки	Предупреждение
8	Снятие одной категории → правила не применяются	Отчёт
9	Сохранение/загрузка конфига	config.json
10	Маппинг PLPCHECK_RULE_TO_CATEGORY	Покрывает все правила PlpCheck
Приложение А — Категории и CHECK-значения
Из 2.RUBRICATOR_CATEGORIES v5.md (PlpCheck)
N	Код категории	Описание	CHECK-значения (из отчёта)
31	PLSQL.OPTIMIZATION	Оптимизация (2L/перевызов БД)	—
32	JAVA.OPTIMIZATION	Оптимизация (СП/Java)	—
33	DBI.ADAPTATION	Адаптация под PostgreSQL	—
34	SQL.CHECKS	Проверки чистого SQL	—
35	WEB.ADAPTATION	Адаптация под Веб-Навигатор	—
36	STYLE.PREFIXES	Префиксы и оформление	bad_prefix, not_mentioned, wrong_method_syntax, code_in_comment
37	STYLE.PREFIX_COMBINATION	Комбинированные префиксы	prefix_type_in_var_name
—	OTHER	Прочие PlpCheck-правила	—
Из scan_report_patch_REPS_EXP_115_1_20260912_203341.md (26 проблем)
CHECK	Кол-во	Категория
bad_prefix	9	STYLE.PREFIXES
not_mentioned	5	STYLE.PREFIXES
prefix_type_in_var_name	5	STYLE.PREFIX_COMBINATION
wrong_method_syntax	1	STYLE.PREFIXES
code_in_comment	4	STYLE.PREFIXES
Итого	26	—
Приложение Б — Вид GUI (пример)
text
☐ 1. Рубрикатор v53
☐ 1a. Рубрикатор тдс20240828
☐ 1b. Рубрикатор тклоик20240828
☑ 2. Рубрикатор PlpCheck                          ← родитель
    ☑ Выбрать все PlpCheck-категории
    ☑ PlpCheck: PLSQL.OPTIMIZATION — Оптимизация (2L/перевызов БД)
    ☑ PlpCheck: JAVA.OPTIMIZATION — Оптимизация (СП/Java)
    ☑ PlpCheck: DBI.ADAPTATION — Адаптация под PostgreSQL
    ☑ PlpCheck: SQL.CHECKS — Проверки чистого SQL
    ☑ PlpCheck: WEB.ADAPTATION — Адаптация под Веб-Навигатор
    ☑ PlpCheck: STYLE.PREFIXES — Префиксы и оформление
        CHECK: bad_prefix, not_mentioned, wrong_method_syntax, code_in_comment
    ☑ PlpCheck: STYLE.PREFIX_COMBINATION — Комбинированные префиксы
        CHECK: prefix_type_in_var_name
    ☑ PlpCheck: OTHER — Прочие PlpCheck-правила
Отчёт о выполнении
После выполнения задач прислать:

Скриншоты GUI (PlpCheck выключен, включён, категории сняты).

Скриншот предупреждения.

Фрагмент кода gui_app.py — секция с чекбоксами.

Фрагмент кода gui_app.py — методы _on_plpcheck_toggle(), _check_plpcheck_categories_before_action().

Фрагмент кода scanner.py — __init__(), фильтр в _load_patterns_from_rubricator().

Маппинг PLPCHECK_RULE_TO_CATEGORY (полный).

Содержимое config.json.

Отчёт scan_report_*.md с фильтрацией.

Вывод ЗАДАЧИ 4 (уникальные (category, subcategory)).

Конец задания DS_036.ЫЫ