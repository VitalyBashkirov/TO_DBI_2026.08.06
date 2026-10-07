#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АРМ "Адаптация под DBI"
Графический интерфейс для миграции PLPlus кода на DBI
Версия: вычисляется автоматически при запуске
"""
import sys
import io
# Принудительное переключение на UTF-8 для корректного вывода в консоли
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from typing import List, Tuple, Optional
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, Menu
from pathlib import Path
import json
import os
from datetime import datetime
import threading
import shutil
import zipfile
# DS_088a: автоматизация AI-цикла («3. В Ai») — запуск воркеров и ожидание.
import subprocess
import time
import re
import urllib.request
import urllib.error

# Импорт модуля рубрикатора
from rubricator_prompts import RubricatorPrompts

# Вычисляемые константы версии на основе текущей даты
_now = datetime.now()
_year_short = str(_now.year)[-2:]
_quarter = (_now.month - 1) // 3 + 1
_quarter_start = datetime(_now.year, (_quarter - 1) * 3 + 1, 1)
_release = (_now - _quarter_start).days + 1

APP_VERSION = f"v{_year_short}.{_quarter}.{_release:03d}"
APP_TITLE = f"АРМ 'Адаптация под DBI' {APP_VERSION}"
APP_QUARTER = ["1-й квартал (янв-мар)", "2-й квартал (апр-июн)", "3-й квартал (июл-сен)", "4-й квартал (окт-дек)"][_quarter - 1]
APP_RELEASE = f"{_release:03d}"

# Константы для логов
MAX_LOG_SIZE_MB = 2  # Максимальный размер логов в МБ (по умолчанию)

# DS 036 (ревизия 2): Категории PlpCheck из 2.RUBRICATOR_CATEGORIES v5.md (№31-37) + OTHER
# DS 037: константа перенесена в scanner.py (Вариант A) — доступна и сканеру, и GUI
from analyzer.scanner import PLPCHECK_CATEGORIES

# DS_058+DS_057: тултипы для кнопок и чекбоксов GUI
RUBRICATOR_TOOLTIPS = {
    'v53': "Правила рубрикатора v5.3.0 (332 правила + 75 правил парсера).",
    'тдс20240828': "Правила из тдс20240828.Требования для совместимости кода с DBI.",
    'тклоик20240828': "Правила из тклоик20240828.Требования к локальным объектам и к коду.",
    'PlpCheck': "Правила из rule-description.html (PlpCheck 2.5.2).",
}

# DS_058+DS_057: маппинг код файла рубрикатора -> префикс rule_code
RUBRICATOR_PREFIXES = {
    'v53': 'v53.',
    'тдс20240828': 'тдс20240828.',
    'тклоик20240828': 'тклоик20240828.',
    'PlpCheck': 'plpcheck.',
}

# DS_086: элементы GUI, не участвующие в workflow «Сканировать → Исправить код →
# В AI». Скрываются через pack_forget (обратимо, НЕ destroy) по одному или все
# сразу — меню «Вид». journal_frame («Журнал выполнения») в реестр НЕ входит.
UI_HIDEABLE_ELEMENTS = (
    ('btn_show_sql', 'Показать SQL для ручного исправления'),
    ('btn_send_koda', 'Отправить в Koda'),
    ('btn_from_ai', 'От AI'),
    ('changelog_frame', 'Журнал изменений'),
    # DS_087 §2.4: скрыть по умолчанию кнопки вне workflow 1→2→3.
    # В ТЗ имена btn_get_answer / btn_history_rk — фактические переменные
    # в коде: btn_receive_koda («Получить ответ»), btn_result_history
    # («История РК»). Идентификация по уникальному тексту, см. отчёт §5.9.
    ('btn_receive_koda', 'Получить ответ'),
    ('btn_result_history', 'История РК'),
)
# DS_086 §2.2: по умолчанию все элементы реестра скрыты (требование задачи).
UI_HIDE_DEFAULT = tuple(key for key, _label in UI_HIDEABLE_ELEMENTS)
# DS_087: состав UI_HIDE_DEFAULT до расширения реестра (для миграции
# сохранённого состояния: если в settings.json лежит ровно старый дефолт —
# пользователь меню «Вид» не трогал → мигрируем на новый дефолт, новые
# кнопки тоже скрыты).
UI_HIDE_DEFAULT_V1 = ('btn_show_sql', 'btn_send_koda', 'btn_from_ai', 'changelog_frame')
# DS_086 §2.3: нижняя граница высоты окна при скрытии «Журнала изменений».
UI_MIN_WINDOW_HEIGHT = 400


class Tooltip:
    """DS_058+DS_057: простой тултип для Tkinter-виджетов."""

    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._id = None
        self._tip = None
        widget.bind('<Enter>', self._schedule)
        widget.bind('<Leave>', self._hide)
        widget.bind('<ButtonPress>', self._hide)

    def _schedule(self, _event=None):
        self._cancel()
        self._id = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self._id is not None:
            try:
                self.widget.after_cancel(self._id)
            except Exception:
                pass
            self._id = None

    def _show(self):
        if self._tip is not None or not self.text:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self._tip = tk.Toplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f'+{x}+{y}')
        label = tk.Label(self._tip, text=self.text, background='#FFFFE0',
                         relief=tk.SOLID, borderwidth=1, justify=tk.LEFT,
                         font=('Segoe UI', 9), wraplength=480)
        label.pack()

    def _hide(self, _event=None):
        self._cancel()
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


def filter_ai_issues(issues, remaining_by_rule, eng=None):
    """DS_080 §2.2/§2.3: отбор issues для AI-запроса при галке «Только Ai».

    Возвращает (отобранные_issues, режим_фильтра):
      'needs_ai_fix' — (а) правило transform_type=="ignore" И (б) строка issue
                       осталась в remaining_by_rule (не закрыта детерминированным
                       конвейером);
      'ignore_set'   — remaining_by_rule пуст (не было «Исправить код»),
                       отбор только по ignore_set (поведение DS_079);
      'без фильтра'  — нет ни remaining_by_rule, ни движка правил.
    """
    remaining = remaining_by_rule or {}
    if remaining:
        kept = []
        for it in issues:
            code = getattr(it, 'issue_type', '')
            if getattr(it, 'line_number', None) not in (remaining.get(code) or []):
                continue
            if eng is not None and not eng.rule_needs_ai(code):
                continue
            kept.append(it)
        return kept, 'needs_ai_fix'
    if eng is None:
        return list(issues), 'без фильтра'
    return ([it for it in issues if eng.rule_needs_ai(getattr(it, 'issue_type', ''))],
            'ignore_set')


def inject_only_ai_flag(report_path, flags: dict) -> bool:
    """DS_080 §0: дописать строку only_ai в блок «Флаги замены» .md-лога.

    Шаблон заголовка scan_report_* формирует analyzer/scanner.py (§4 DS_080 —
    не менять), поэтому строка вставляется post-factum в уже записанный файл.
    Идемпотентно: при знакомом only_ai файл не трогается. Возвращает True,
    если файл изменён.
    """
    from fixer.code_fixer import append_only_ai_flag
    p = Path(report_path)
    if not p.exists():
        return False
    raw = p.read_text(encoding='utf-8', errors='replace')
    src = raw.splitlines()
    out = append_only_ai_flag(list(src), flags)
    if out == src:
        return False
    nl = '\r\n' if '\r\n' in raw else '\n'
    p.write_text(nl.join(out) + nl, encoding='utf-8')
    return True


class DBIMigrationApp:
    """Основное приложение"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        # DS_087 §2.5: размер окна 1600×900; если экран меньше — во весь экран;
        # центрирование. _ui_base_geometry (DS_086) синхронизируется с фактическим
        # размером — от него считается высота при скрытии элементов реестра.
        W, H = 1600, 900
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        if sw < W or sh < H:
            W, H = sw, sh  # во весь экран
        x = (sw - W) // 2
        y = (sh - H) // 2
        self.root.geometry(f"{W}x{H}+{x}+{y}")
        # DS_086 §2.3: базовый размер окна. Высота при скрытии элементов
        # считается от него — см. _adjust_window_height().
        self._ui_base_geometry = (W, H)
        # DS_087 §2.5: minsize согласован с UI_MIN_WINDOW_HEIGHT = 400 (DS_086).
        self.root.minsize(1200, 600)
        
        # Переменные
        self.source_dir_var = tk.StringVar()
        self.result_dir_var = tk.StringVar()
        self.file_pattern_var = tk.StringVar(value="**/*.plp")
        self.log_level_var = tk.StringVar(value="Минимальный")
        # DS_075: минимальный размер выборки для top-файлов (порог «достаточности»)
        self.report_stats_min_files_var = tk.StringVar(value="10")
        self.only_modified_var = tk.BooleanVar(value=True)
        self.preserve_structure_var = tk.BooleanVar(value=True)
        self.scan_recursive_var = tk.BooleanVar(value=True)
        
# Состояние рубрикатора
        self.rubricator_loaded = False
        # DS_058+DS_057: состояние отдельных правил (rule_code -> BooleanVar)
        self._rubricator_rule_vars = {}
        # item_id родителя -> код файла рубрикатора
        self._rubricator_parent_items = {}
        # item_id дочернего -> rule_code
        self._rule_item_map = {}
        # код файла -> список rule_code (порядок из рубрикатора)
        self._rubricator_rules_by_file = {}
        # Тултипы дерева правил (item_id -> Tooltip-like текст)
        self._tree_tooltips = {}
        self.rubricator_dir = Path(__file__).parent.parent / 'DATA' / 'Рубрикатор v5'
        self.rubricator_files = {}  # Код файла: Полное имя из 1.RUBRICATOR_FILES v5.md
        
        # Новый рубрикатор 4.RUBRICATOR_PROMPT v5.json
        self.rubricator_prompts: Optional[RubricatorPrompts] = None
        
        # Флаг PlpCheck - включение/выключение правил стиля кода
        self.plpcheck_enabled_var = tk.BooleanVar(value=False)
        
        # Флаг чистого вывода (без маркеров изменений)
        self.clean_output_var = tk.BooleanVar(value=False)
        
        # Выбранные правила
        self.selected_rules = {}
        self.rule_checkboxes = {}  # Для доступа к виджетов
        
        # Сохранённые правила из предыдущего запуска
        self._saved_rules = []
        
        # DS 018: выбранные приоритеты HIGH/MEDIUM/LOW (заполняется из чекбоксов бокса 3)
        self._selected_priorities = []
        
        # Результаты сканирования (для кнопки "Показать SQL для ручного исправления")
        self.scan_results = None  # Результаты последнего сканирования
        
        # Ссылки на поля ввода для привязки событий
        self.source_entry = None
        self.result_entry = None
        
        # Путь для дублирования логов
        self.logs_deep_dir = Path(__file__).parent.parent / 'logs_Deep'
        self.logs_deep_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = None
    
        # Флаг изменения выбора правил
        self.rules_changed = False
        
        # Ссылка на кнопки для управления доступностью
        self.btn_scan = None
        self.btn_fix = None
        # DS 054: кнопки файлового обмена с AI
        self.btn_to_ai = None
        self.btn_from_ai = None
        
        # DS 038 (Проблема A): флаги управления прерыванием
        self.scan_running = False       # True, пока идёт сканирование/исправление/генерация
        self.scan_aborted = False       # True, если пользователь нажал «Прервать»
        self.btn_abort = None           # Кнопка «Прервать» (создаётся в _create_widgets)
        # DS 041: заморозка индикатора при прерывании + процент прерывания
        self._progress_frozen = False   # True — обычные обновления value игнорируются
        self.abort_percent = None       # None — не прервано; иначе float (0.0–100.0)

        # DS_089b §2.2: состояние прерванной операции для resume
        # {'operation': 'scan'|'fix', 'processed_keys': [...], 'processed_files': [...]}
        self._abort_state = None

        # DS_089b: механизм graceful stop через threading.Event
        self._stop_event = threading.Event()
        
        # Создаём главное меню
        self._create_menu()
        
        # Создаём интерфейс
        self._create_widgets()
        
        # Загрузка настроек (ПЕРЕД применением правил в рубрикаторе)
        self.load_settings()
        
        # Проверка размера логов
        self._check_log_size()
        
        # Заполняем рубрикатор и применяем сохранённые правила
        self._populate_rules_tree()
        
        # Состояние чекбоксов уже установлено из 1.RUBRICATOR_FILES v5.md (признак +/−)
        # Никаких дополнительных правил из settings.json не загружаем
        
        # DS 029: вывод информации о загруженных рубрикаторах в Журнал выполнения
        self._log_rubricator_status()
        
        # Привязка событий для поля ввода
        self._bind_entry_events()

        # DS_088b §2.3: контекстное меню (ПКМ) для всех Entry/Text формы.
        self._attach_all_context_menus()
    
    def _log_rubricator_status(self):
        """Вывод информации о загруженных рубрикаторах в Журнал выполнения (DS 029)"""
        self.log("=" * 60, 'info')
        self.log("ЗАГРУЖЕНЫ РУБРИКАТОРЫ:", 'highlight')
        self.log("=" * 60, 'info')
        
        total_rules = 0
        for code, var in self.selected_rules.items():
            status = "включён" if var.get() else "отключён"
            name = self.rubricator_files.get(code, code)
            self.log(f"  [{'+' if var.get() else '-'}] {code} ({status})", 'info')
            # Подсчёт правил для каждого файла
            if self.rubricator_prompts and self.rubricator_prompts.loaded:
                rules = [r for r in self.rubricator_prompts.get_all_rules() if r['code'].lower().startswith(code.lower())]
                if rules:
                    total_rules += len(rules)
                    self.log(f"      Правил: {len(rules)}", 'debug')
        
        self.log("=" * 60, 'info')
        if self.rubricator_prompts and self.rubricator_prompts.loaded:
            self.log(f"Всего правил: {total_rules}", 'info')
        self.log("=" * 60, 'info')
        
        # DS 030: информация о фильтрах по приоритету
        selected_priorities = []
        if getattr(self, 'priority_high_var', None) and self.priority_high_var.get():
            selected_priorities.append('HIGH')
        if getattr(self, 'priority_medium_var', None) and self.priority_medium_var.get():
            selected_priorities.append('MEDIUM')
        if getattr(self, 'priority_low_var', None) and self.priority_low_var.get():
            selected_priorities.append('LOW')
        
        if selected_priorities:
            self.log("=" * 60, 'info')
            self.log("ФИЛЬТРЫ ПО ПРИОРИТЕТУ:", 'highlight')
            self.log("=" * 60, 'info')
            for prio in selected_priorities:
                self.log(f"  ★ {prio}", 'highlight')
            
            # Показываем количество правил по каждому приоритету
            try:
                from rubricator_priority_mapping import PRIORITY_RULES
                # DS 030: в PRIORITY_RULES ключи - 'Приоритет 1/2/3', а не 'HIGH/MEDIUM/LOW'
                prio_key_map = {'HIGH': 'Приоритет 1', 'MEDIUM': 'Приоритет 2', 'LOW': 'Приоритет 3'}
                for prio in selected_priorities:
                    prio_key = prio_key_map.get(prio, prio)
                    if prio_key in PRIORITY_RULES:
                        count = len(PRIORITY_RULES[prio_key])
                        self.log(f"     Правил в {prio}: {count}", 'info')
            except ImportError:
                pass
            
            self.log("=" * 60, 'info')
        else:
            self.log("=" * 60, 'info')
            self.log("ФИЛЬТРЫ ПО ПРИОРИТЕТУ: не выбраны (используются все правила)", 'info')
            self.log("=" * 60, 'info')
    
    def display_log_line(self, line: str):
        """Вывод строки PlpCheck-отчёта с цветовой подсветкой (DS 030, DS 032).
        
        Формат ЦФТ-PlpCheck (таб-разделяемый):
        №	CLASS_ID	SHORT_NAME	SECTION	LINE	CHECK	LEVEL	TYPE	ERROR	PLAN
        Подсветка: локация (синий), номер строки (зелёный), тип (оранжевый),
        описание (чёрный), ПЛАН (красный жирный).
        """
        import re
        match = re.match(
            r'^(\d+)	([\w.]+)	([\w.]+)	(\w+)	(\d+)	([\w.]+)	(\w+)	(\w+)	([^	]*?)(?:	(.*))?$',
            line
        )
        if not match:
            self.log(line, 'info')
            return
        
        num, class_id, short_name, section, line_number, check, level, itype, error, plan = match.groups()
        self.log_with_tags([
            (f"{num} ", 'line_number'),
            (f"{class_id}.{short_name}.{section}:", 'class_method'),
            (f"{line_number} ", 'line_number'),
            (f"{check} ", 'issue_type'),
            (f"[{level}/{itype}] ", 'description'),
            (f"{error}", 'description'),
            (f" | ПЛАН: {plan}" if plan else "", 'plan'),
        ])
    
    def _create_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Каталоги"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Каталоги", menu=file_menu)
        file_menu.add_command(label="Корневой каталог...", command=self.browse_source, accelerator="Ctrl+O")
        file_menu.add_command(label="Каталог результатов...", command=self.browse_result, accelerator="Ctrl+R")
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить настройки", command=self.save_settings, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_close, accelerator="Alt+F4")
        
        # Меню "Проект"
        project_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Проект", menu=project_menu)
        project_menu.add_command(label="Структура проекта", command=self.show_project_structure)
        project_menu.add_command(label="Рубрикатор", command=self.open_rubricator)
        
        # Меню "Действия"
        actions_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Действия", menu=actions_menu)
        actions_menu.add_command(label="Сканировать", command=self.start_scan, accelerator="F5")
        actions_menu.add_command(label="Сканировать. Алгоритм Deep", command=self.start_deep_scan, accelerator="Ctrl+F5")
        actions_menu.add_separator()
        actions_menu.add_command(label="Исправить код", command=self.start_fix, accelerator="F6")
        
        # DS_086: меню "Вид" — скрытие/показ элементов GUI по одному и всех сразу
        self._create_view_menu(menubar)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Документация", command=self.show_documentation)
        help_menu.add_separator()
        help_menu.add_command(label="О программе", command=self.show_about)
        
        # Горячие клавиши
        self.root.bind('<Control-o>', lambda e: self.browse_source())
        self.root.bind('<Control-r>', lambda e: self.browse_result())
        self.root.bind('<Control-s>', lambda e: self.save_settings())
        self.root.bind('<F5>', lambda e: self.start_scan())
        self.root.bind('<Control-F5>', lambda e: self.start_deep_scan())
        self.root.bind('<F6>', lambda e: self.start_fix())
    
    # ------------------------------------------------------------------
    # DS_086: скрытие элементов GUI (workflow «Сканировать → Исправить код → В AI»)
    # Метод — pack_forget()/pack(), НЕ destroy: виджеты и их обработчики
    # сохраняются, действие обратимо. journal_frame («Журнал выполнения») в
    # реестр не входит (ТЗ §1a).
    # ------------------------------------------------------------------
    def _create_view_menu(self, menubar):
        """Меню «Вид»: скрыть/показать элементы реестра по одному и все сразу."""
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        self.view_menu = view_menu
        self.ui_visible_vars = {}
        for key, label in UI_HIDEABLE_ELEMENTS:
            var = tk.BooleanVar(value=key not in UI_HIDE_DEFAULT)
            self.ui_visible_vars[key] = var
            view_menu.add_checkbutton(label=label, variable=var,
                                      command=lambda k=key: self.toggle_ui_element(k))
        view_menu.add_separator()
        view_menu.add_command(label="Скрыть все элементы",
                              command=lambda: self.set_all_ui_elements(False))
        view_menu.add_command(label="Показать все элементы",
                              command=lambda: self.set_all_ui_elements(True))
    
    def _register_ui_hideables(self):
        """Зафиксировать параметры pack элементов реестра и применить состояние.

        Вызывается в конце _create_widgets, когда все виджеты уже созданы.
        _ui_height_delta[key] — вклад элемента в высоту окна: учитываются
        только блоки, упакованные по вертикали (side=top/bottom). Кнопки
        реестра лежат в btn_bar_canvas (side=left) и высоту не меняют.
        """
        if not hasattr(self, 'ui_visible_vars'):
            self.ui_visible_vars = {}
        self._ui_pack_opts = {}
        self._ui_height_delta = {}
        self.root.update_idletasks()
        for key, _label in UI_HIDEABLE_ELEMENTS:
            widget = getattr(self, key, None)
            if widget is None:
                continue
            try:
                opts = widget.pack_info()
            except Exception:
                opts = {}
            self._ui_pack_opts[key] = opts
            if str(opts.get('side', 'top')) in ('top', 'bottom'):
                try:
                    pady = int(opts.get('pady') or 0)
                except (TypeError, ValueError):
                    pady = 0
                self._ui_height_delta[key] = widget.winfo_reqheight() + 2 * pady
            else:
                self._ui_height_delta[key] = 0
        self._apply_ui_visibility(persist=False)
    
    def _window_size(self):
        """Текущие размеры окна (ширина, высота) из geometry()."""
        try:
            width, height = self.root.geometry().split('+')[0].split('x')
            return int(width), int(height)
        except Exception:
            return 0, self.root.winfo_reqheight()
    
    def _apply_ui_visibility(self, persist=True):
        """Применить видимость всех элементов реестра и пересчитать высоту окна."""
        if not getattr(self, '_ui_pack_opts', None):
            return
        h_before = self._window_size()[1]
        for key, opts in self._ui_pack_opts.items():
            var = self.ui_visible_vars.get(key)
            visible = True if var is None else bool(var.get())
            widget = getattr(self, key, None)
            if widget is None:
                continue
            try:
                if visible:
                    widget.pack(**opts)
                else:
                    widget.pack_forget()
            except Exception as exc:
                self.log(f"DS_086: {key} — не удалось изменить видимость: {exc}", 'warning')
        h_after = self._adjust_window_height()
        if persist:
            self._autosave_ui_visibility()
        self._bot_log(f"DS_086 GUI height: before={h_before}, after={h_after}")
    
    def _adjust_window_height(self):
        """DS_086 §2.3: высота окна = базовая минус высота скрытых блоков.

        Считается от базового размера (_ui_base_geometry), а не от текущего,
        поэтому многократные переключения не «уводят» окно (нет дрейфа).
        Кнопки реестра лежат в горизонтально-прокручиваемой панели
        (btn_bar_canvas, side=left) и на высоту не влияют — уменьшает её
        только «Журнал изменений» (changelog_frame, side=top).
        """
        w_base, h_base = getattr(self, '_ui_base_geometry', (1090, 650))
        w_now, _h_now = self._window_size()
        width = w_now if w_now > 1 else w_base
        hidden = sum(self._ui_height_delta.get(key, 0)
                     for key, var in self.ui_visible_vars.items() if not var.get())
        target = max(UI_MIN_WINDOW_HEIGHT, h_base - hidden)
        try:
            self.root.geometry(f"{width}x{target}")
            self.root.update_idletasks()
        except Exception as exc:
            self.log(f"DS_086: не удалось изменить высоту окна: {exc}", 'warning')
            return self._window_size()[1]
        return target
    
    def toggle_ui_element(self, key):
        """Смена видимости одного элемента реестра (пункт меню «Вид»)."""
        var = self.ui_visible_vars.get(key)
        if var is None:
            return
        self._apply_ui_visibility()
        label = dict(UI_HIDEABLE_ELEMENTS).get(key, key)
        self.log(f"DS_086: «{label}» — {'виден' if var.get() else 'скрыт'}", 'info')
    
    def set_all_ui_elements(self, visible):
        """Скрыть/показать все элементы реестра сразу (пункт меню «Вид»)."""
        for var in self.ui_visible_vars.values():
            var.set(visible)
        self._apply_ui_visibility()
        self.log(f"DS_086: элементы реестра — "
                 f"{'все видны' if visible else 'все скрыты'}", 'info')
    
    def _hidden_ui_keys(self):
        """Ключи скрытых элементов реестра (для settings.json)."""
        return sorted(key for key, var in getattr(self, 'ui_visible_vars', {}).items()
                      if not var.get())
    
    def _restore_ui_visibility(self, saved_keys):
        """DS_086: применить состояние из settings.json.

        saved_keys — список ключей, которые нужно СКРЫТЬ. None — ключа нет
        (первый запуск): остаётся UI_HIDE_DEFAULT, ничего не меняем.
        """
        if saved_keys is None or not getattr(self, 'ui_visible_vars', None):
            return
        # DS_087: миграция старого дефолта (4 ключа DS_086) на новый (6 ключей) —
        # иначе новые скрытые по умолчанию кнопки остались бы видимыми.
        if tuple(sorted(saved_keys)) == tuple(sorted(UI_HIDE_DEFAULT_V1)):
            saved_keys = list(UI_HIDE_DEFAULT)
        hidden = {k for k in saved_keys if k in self.ui_visible_vars}
        for key, var in self.ui_visible_vars.items():
            var.set(key not in hidden)
        self._apply_ui_visibility(persist=False)
    
    def _autosave_ui_visibility(self):
        """Автосохранение видимости в settings.json (read-modify-write одного ключа).

        По образцу _autosave_fix_flags: не писать во время загрузки настроек.
        """
        if getattr(self, '_loading_settings', False):
            return
        if not getattr(self, 'ui_visible_vars', None):
            return
        try:
            settings_path = Path(__file__).parent / 'settings.json'
            settings = {}
            if settings_path.exists():
                try:
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                except Exception:
                    settings = {}
            settings['ui_hidden_elements'] = self._hidden_ui_keys()
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(f"Не удалось автосохранить видимость GUI: {exc}")
    
    def _create_widgets(self):
        """Создание виджетов"""
        # Подвал (статус-бар) — pack ПЕРВЫМ, чтобы он был внизу
        self.status_label = tk.Label(self.root, text="Готово", relief=tk.FLAT, anchor=tk.W,
                                     padx=10, pady=2, bg='#e8e8e8', font=('Segoe UI', 9),
                                     borderwidth=1, highlightthickness=0)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
        # Основной контейнер с прокруткой
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        # DS_087 §2.6: scrollable_frame растягивается по ширине канваса —
        # иначе LabelFrame'ы сжимаются по содержимому и элементы «липнут»
        # к правому краю (напр. группа «Топ-файлов» в боксе 3).
        _canvas_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_main_canvas_configure(event):
            try:
                main_canvas.itemconfigure(_canvas_window, width=event.width)
            except Exception:
                pass

        main_canvas.bind("<Configure>", _on_main_canvas_configure)
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Секция 1 - Пути и настройки сканирования
        paths_frame = ttk.LabelFrame(scrollable_frame, text="1. Пути и настройки сканирования", padding="5")
        paths_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Строка 0: Исходный каталог
        # DS_087 §2.6.1: поля ИК/КР сужены 50→40 — кнопки [...] гарантированно
        # влезают даже при minsize=1200 (40 симв. + метка + кнопка в колонке).
        ttk.Label(paths_frame, text="Исходный каталог:").grid(row=0, column=0, sticky=tk.W, padx=(0,1))
        self.source_entry = ttk.Entry(paths_frame, textvariable=self.source_dir_var, width=40, style='Valid.TEntry')
        self.source_entry.grid(row=0, column=1, padx=0, sticky=tk.EW)
        self.btn_browse_source = ttk.Button(paths_frame, text="...", command=self.browse_source, width=3)
        self.btn_browse_source.grid(row=0, column=2, padx=(0,2))
        Tooltip(self.btn_browse_source, "Выбрать исходный каталог с PLPlus-файлами.")

        # Строка 0: Каталог результатов
        ttk.Label(paths_frame, text="Каталог результатов:").grid(row=0, column=3, sticky=tk.W, padx=(2,1))
        self.result_entry = ttk.Entry(paths_frame, textvariable=self.result_dir_var, width=40, style='Valid.TEntry')
        self.result_entry.grid(row=0, column=4, padx=0, sticky=tk.EW)
        self.btn_browse_result = ttk.Button(paths_frame, text="...", command=self.browse_result, width=3)
        self.btn_browse_result.grid(row=0, column=5, padx=(0,0))
        Tooltip(self.btn_browse_result, "Выбрать каталог для сохранения результатов.")
        
        # Стили цветовой индикации полей ИК/РК (DS 008)
        entry_style = ttk.Style()
        entry_style.configure('Valid.TEntry', fieldbackground='#d4edda')    # зелёный — доступен
        entry_style.configure('Warning.TEntry', fieldbackground='#fff3cd')  # жёлтый — будет создан
        entry_style.configure('Invalid.TEntry', fieldbackground='#f8d7da')  # красный — ошибка
        
        # Строка 1: Шаблон + Сканировать подкаталоги
        ttk.Label(paths_frame, text="Шаблон:").grid(row=1, column=0, sticky=tk.W, padx=(0,1), pady=2)
        ttk.Entry(paths_frame, textvariable=self.file_pattern_var, width=50).grid(row=1, column=1, padx=0, sticky=tk.W)
        ttk.Checkbutton(paths_frame, text="Рекурсивно", variable=self.scan_recursive_var).grid(row=1, column=2, padx=(2,0), sticky=tk.W)
        
        # Строка 2: Метки статуса каталогов (DS 009)
        self.source_status_label = ttk.Label(paths_frame, text="", font=("Segoe UI", 9))
        self.source_status_label.grid(row=2, column=1, sticky=tk.W)
        
        self.result_status_label = ttk.Label(paths_frame, text="", font=("Segoe UI", 9))
        self.result_status_label.grid(row=2, column=4, sticky=tk.W)
        
        paths_frame.grid_columnconfigure(1, weight=1)
        paths_frame.grid_columnconfigure(4, weight=1)
        
        # Секция 2 - Рубрикатор
        rules_frame = ttk.LabelFrame(scrollable_frame, text="2. Рубрикатор. Выбор корректировок", padding="5")
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        
        # Загрузка файлов рубрикатора
        self._load_rubricator_files()
        
        # Treeview с прокруткой (высота -50%, ширина -30%)
        # DS_087 §2.6.2: скроллбары сохранены в self — видны и проверяемы.
        tree_scroll_y = self.tree_scroll_y = ttk.Scrollbar(rules_frame, orient=tk.VERTICAL)
        tree_scroll_x = self.tree_scroll_x = ttk.Scrollbar(rules_frame, orient=tk.HORIZONTAL)
        
        self.rules_tree = ttk.Treeview(rules_frame,
                                       yscrollcommand=tree_scroll_y.set,
                                       xscrollcommand=tree_scroll_x.set,
                                       show='tree headings',
                                       height=4)

        tree_scroll_y.config(command=self.rules_tree.yview)
        tree_scroll_x.config(command=self.rules_tree.xview)

        # Настройка колонок: Рубрикатор/правило | Выбрано | Код | Название
        # DS_058+DS_057: колонка #0 (tree) — родительские чекбоксы рубрикаторов
        self.rules_tree.column('#0', width=180, minwidth=140, stretch=False)
        self.rules_tree['columns'] = ('selected', 'code', 'name')
        self.rules_tree.column('selected', width=60, minwidth=60, anchor=tk.CENTER)
        self.rules_tree.column('code', width=110, minwidth=110, anchor=tk.W)
        # DS_087 §2.6.2: stretch=False — длинное имя НЕ сдвигает скроллбары;
        # горизонтальная прокрутка показывает остаток.
        self.rules_tree.column('name', width=750, minwidth=400, anchor=tk.W, stretch=False)

        # Заголовки
        self.rules_tree.heading('#0', text='Рубрикатор', anchor=tk.W)
        self.rules_tree.heading('selected', text='Выбрано', anchor=tk.CENTER)
        self.rules_tree.heading('code', text='Код файла', anchor=tk.W)
        self.rules_tree.heading('name', text='Полное имя файла', anchor=tk.W)
        
        # Размещаем Treeview и скроллы
        # DS_087 §2.6.2: таблица растягивается по ширине бокса 2, скроллбары
        # (верт./гориз.) остаются в зоне видимости и не уходят за край.
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.rules_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # DS 018: панель приоритетов удалена из бокса 2 (перенесена в бокс 3 как HIGH/MEDIUM/LOW)
        
        # Заполняем Treeview (позже, после создания кнопок)
        # self._populate_rules_tree() будет вызван после инициализации кнопок
        
        # Секция 3 - Опции сканирования и исправления. Логирование
        # DS_087 §2.6.3: options_frame сохранён в self (для layout-тестов).
        options_frame = self.options_frame = ttk.LabelFrame(scrollable_frame, text="3. Опции сканирования и исправления. Логирование", padding="5")
        options_frame.pack(fill=tk.X, padx=5, pady=3)
        # DS_087 §2.6.3: колонка-распорка 6 поглощает свободное место —
        # группа «Топ-файлов» (col 4-5) не прижимается к правому краю.
        options_frame.grid_columnconfigure(6, weight=1)
        
        # Опции вывода
        ttk.Checkbutton(options_frame, text="Только модифицированные файлы", 
                       variable=self.only_modified_var).grid(row=0, column=0, sticky=tk.W, padx=3)
        ttk.Checkbutton(options_frame, text="Сохранить структуру каталогов", 
                       variable=self.preserve_structure_var).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # Уровень логирования
        ttk.Label(options_frame, text="Уровень логирования:").grid(row=0, column=2, sticky=tk.W, padx=(15,3))
        ttk.Combobox(options_frame, textvariable=self.log_level_var, 
                    values=["Минимальный", "Подробный"], 
                    state="readonly", width=15).grid(row=0, column=3, sticky=tk.W)
        # DS_075 §3.2: порог вывода топ-файлов (при «Подробный»).
        # DS_087 §2.6.3: метка «Топ-файлов» сохранена (для layout-теста).
        self.report_stats_label = ttk.Label(options_frame, text="Топ-файлов, мин. файлов:")
        self.report_stats_label.grid(row=0, column=4, sticky=tk.W, padx=(15,3))
        self.report_stats_entry = ttk.Entry(options_frame, textvariable=self.report_stats_min_files_var, width=5)
        self.report_stats_entry.grid(row=0, column=5, sticky=tk.W)
        
# Чекбокс для режима вывода при исправлении
        self.fix_only_found_var = tk.BooleanVar(value=False)
        # Стиль для зелёного текста чекбокса
        style = ttk.Style()
        style.configure('Green.TCheckbutton', foreground='green')
        ttk.Checkbutton(options_frame, text='"Исправить код" — только пометить найденные теги "--NEW YYYY-MM-DD"', 
                        variable=self.fix_only_found_var, style='Green.TCheckbutton').grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5,0))
        
        # Чекбокс PlpCheck — включение/выключение правил стиля кода
        # DS 038 (Проблема E): переименовано из "Добавлять PlpCheck-правила (стиль кода)"
        # DS_088a_fix §2.7: без columnspan — подфлаги (2 колонки) идут правее.
        ttk.Checkbutton(options_frame, text="2. Рубрикатор PlpCheck", 
                        variable=self.plpcheck_enabled_var).grid(row=2, column=0, sticky=tk.W, pady=(5,0))
        # Синхронизация флага PlpCheck с чекбоксом в дереве правил
        self.plpcheck_enabled_var.trace_add('write', lambda *args: self._sync_plpcheck_checkbox())
        
        # DS 036: группа флагов категорий PlpCheck (8 категорий + OTHER)
        # DS_088a_fix §2.7: подфлаги перевёрстаны в ДВЕ колонки (grid) —
        # освобождает вертикальное место, «Фильтр по приоритету» и «Флаги
        # DS_053» поднимаются выше автоматически.
        self.frame_plpcheck_categories = ttk.Frame(options_frame)
        self.frame_plpcheck_categories.grid(row=2, column=1, columnspan=5, sticky=tk.W, padx=(30, 0), pady=(5, 0))
        self.frame_plpcheck_categories.grid_columnconfigure(0, weight=0)
        self.frame_plpcheck_categories.grid_columnconfigure(1, weight=0)
        
        # DS 036: чекбокс "Выбрать все PlpCheck-категории" (на всю ширину)
        self.var_plpcheck_all = tk.BooleanVar(value=True)
        self.chk_plpcheck_all = ttk.Checkbutton(
            self.frame_plpcheck_categories,
            text="Выбрать все PlpCheck-категории",
            variable=self.var_plpcheck_all,
            command=self._toggle_all_plpcheck_categories,
            state='disabled'  # DS 036: disabled пока PlpCheck не выбран
        )
        self.chk_plpcheck_all.grid(row=0, column=0, columnspan=2, sticky='w')
        
        # DS 036: 8 чекбоксов категорий (7 + OTHER) с CHECK-значениями.
        # DS_088a_fix §2.7: раскладка в 2 колонки — каждая категория в своей
        # ячейке (подкадре): чекбокс + опциональная строка «CHECK: ...».
        self.var_plpcheck_categories = {}
        self.chk_plpcheck_categories = {}
        for _idx, (code, descr, checks) in enumerate(PLPCHECK_CATEGORIES):
            var = tk.BooleanVar(value=True)
            self.var_plpcheck_categories[code] = var
            cell = ttk.Frame(self.frame_plpcheck_categories)
            cell.grid(row=1 + _idx // 2, column=_idx % 2,
                      sticky='nw', padx=(0, 24), pady=1)
            chk = ttk.Checkbutton(
                cell,
                text=f"PlpCheck: {code} — {descr}",
                variable=var,
                command=self._update_plpcheck_all_checkbox,
                state='disabled'  # DS 036: disabled пока PlpCheck не выбран
            )
            chk.pack(anchor='w')
            self.chk_plpcheck_categories[code] = chk
            
            # DS 036 (ревизия 2): CHECK-значения серым текстом под чекбоксом
            if checks:
                lbl = ttk.Label(
                    cell,
                    text=f"CHECK: {checks}",
                    font=('Segoe UI', 8),
                    foreground='#666666',
                    anchor='w'
                )
                lbl.pack(anchor='w', padx=(20, 0))
        
        # DS 036: синхронизация доступности категорий при переключении флага PlpCheck
        self.plpcheck_enabled_var.trace_add('write', lambda *args: self._on_plpcheck_toggle())
        
        # DS 018: чекбоксы приоритетов HIGH/MEDIUM/LOW (фильтр правил)
        priority_frame = ttk.Frame(options_frame)
        priority_frame.grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=(5,0))
        
        ttk.Label(priority_frame, text="Фильтр по приоритету:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0,10))
        
        self.priority_high_var = tk.BooleanVar(value=False)
        self.priority_medium_var = tk.BooleanVar(value=False)
        self.priority_low_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(priority_frame, text="HIGH", variable=self.priority_high_var,
                        command=self._on_priority_filter_change).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(priority_frame, text="MEDIUM", variable=self.priority_medium_var,
                        command=self._on_priority_filter_change).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(priority_frame, text="LOW", variable=self.priority_low_var,
                        command=self._on_priority_filter_change).pack(side=tk.LEFT, padx=5)
        
        # Метка для отображения выбранных приоритетов
        self.priority_status_label = ttk.Label(priority_frame, text="Все приоритеты", font=('Segoe UI', 9, 'italic'), foreground='gray')
        self.priority_status_label.pack(side=tk.LEFT, padx=(10,0))
        
        # Чекбокс чистого вывода (без маркеров изменений)
        ttk.Checkbutton(options_frame, 
                       text="Верни только исправленный код без пояснений и маркеров изменений.\nВсе пояснения, изменения, удаления журналируй", 
                       variable=self.clean_output_var).grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(5,0))
        
        # Чекбокс архивирования
        self.archive_result_var = tk.BooleanVar(value=True)
        self.archive_result_check = ttk.Checkbutton(options_frame, text="Архивировать результат", 
                                                    variable=self.archive_result_var)
        self.archive_result_check.grid(row=1, column=4, sticky=tk.W, padx=(20,0))
        # Изначально доступен только если включена сохранность структуры
        self._update_archive_state()
        
        # Привязка изменения preserve_structure к доступности archive
        self.preserve_structure_var.trace_add('write', lambda *args: self._update_archive_state())

        # DS 053: флаги детерминированного фикса (6 чекбоксов).
        # Порядок и подписи соответствуют rule_engine.FLAG_ORDER.
        flags_frame = ttk.LabelFrame(options_frame, text="Флаги детерминированного фикса (DS_053)", padding="5")
        flags_frame.grid(row=5, column=0, columnspan=5, sticky=tk.W, pady=(6, 0))
        # DS_053_Уточнение_3 (задача C): подпись из трёх строк (точный текст).
        _cap = ttk.Frame(flags_frame)
        _cap.grid(row=0, column=0, columnspan=6, sticky=tk.W)
        for _i, _line in enumerate([
            "Имя дополнительного лога: scan_VVxVVx (V — флаг выбран, x — нет)",
            "Формируется при сканировании и исправлении.",
            "При отсутствии флагов — пустой, с пометкой «флаги не выбраны».",
        ]):
            ttk.Label(_cap, text=_line,
                      font=('Segoe UI', 8, 'italic'), foreground='#666666').grid(
                row=_i, column=0, sticky=tk.W)
        self.var_fix_flags = {}
        _flag_defs = [
            ('regex', 'regex (чистые regex-правила)', True),
            ('hybrid', 'hybrid (полудетерм. с algorithmic_hint)', True),
            ('ai_fallback', 'ai_fallback (помечать needs_ai_fix)', False),
            ('ignore', 'ignore (не автофиксить, только лог)', False),
            ('backup', 'backup (резервные regex-правила)', False),
            ('other', 'other (hybrid без algorithmic_hint)', False),
        ]
        for _i, (_name, _text, _default) in enumerate(_flag_defs):
            _var = tk.BooleanVar(value=_default)
            self.var_fix_flags[_name] = _var
            # DS_053_Уточнение_2 (задача C): автосохранение при изменении флага.
            _var.trace_add('write', lambda *a: self._autosave_fix_flags())
            ttk.Checkbutton(flags_frame, text=_text, variable=_var).grid(
                row=1 + _i // 3, column=_i % 3, sticky=tk.W, padx=6, pady=1)
        
        # Панель управления (DS_054_Уточнение, задача B): оборачиваем в
        # горизонтально-прокручиваемый канвас — если кнопки не влезают в ширину
        # окна, все они достижимы горизонтальным скроллом. Приложение на Tkinter
        # (не PyQt/PySide), QScrollArea неприменим, а нативного wrap/flow-менеджера
        # в Tkinter нет — выбран Вариант A (скролл; Tkinter-аналог QScrollArea).
        self.btn_bar_canvas = tk.Canvas(scrollable_frame, height=44, highlightthickness=0)
        _btn_bar_scrollx = ttk.Scrollbar(scrollable_frame, orient=tk.HORIZONTAL,
                                         command=self.btn_bar_canvas.xview)
        self.btn_bar_canvas.configure(xscrollcommand=_btn_bar_scrollx.set)
        control_frame = ttk.Frame(self.btn_bar_canvas, padding="5")
        self.control_frame = control_frame
        self.btn_bar_canvas.create_window((0, 0), window=control_frame, anchor="nw")

        def _sync_btn_bar(*_a):
            # scrollregion по содержимому + авто-высота канваса под строку кнопок.
            try:
                self.btn_bar_canvas.configure(scrollregion=self.btn_bar_canvas.bbox("all"))
                h = control_frame.winfo_reqheight()
                if h:
                    self.btn_bar_canvas.configure(height=h)
            except Exception:
                pass

        control_frame.bind("<Configure>", _sync_btn_bar)

        # Колесо мыши (со Shift) над панелью — горизонтальная прокрутка.
        def _btn_wheel(event):
            step = -1 if getattr(event, 'delta', 0) > 0 else 1
            self.btn_bar_canvas.xview_scroll(step, "units")
            return "break"
        self.btn_bar_canvas.bind("<Shift-MouseWheel>", _btn_wheel)

        _btn_bar_scrollx.pack(side=tk.BOTTOM, fill=tk.X)
        self.btn_bar_canvas.pack(fill=tk.X)
        
        self.btn_scan = ttk.Button(control_frame, text="1. Сканировать", command=self.start_scan, width=20)
        self.btn_scan.pack(side=tk.LEFT, padx=3)
        
        # DS_087 §2.3: стили для логики активации 1→2→3 — активная кнопка
        # жирная, остальные обычные. ('Fix.TButton' оставлен для совместимости
        # тестов, но шрифт btn_fix управляется workflow-стилями.)
        style = ttk.Style()
        style.configure('Fix.TButton', font=('Segoe UI', 9, 'bold'))
        style.configure('WorkflowActive.TButton', font=('Segoe UI', 9, 'bold'))
        style.configure('WorkflowNormal.TButton', font=('Segoe UI', 9))
        
        # DS_087 §2.2: «2. Исправить код» — нумерованное имя workflow.
        self.btn_fix = ttk.Button(control_frame, text="2. Исправить код", command=self.start_fix, width=20)
        self.btn_fix.pack(side=tk.LEFT, padx=3)
        
        # DS 054 / DS_054_Уточнение (задача A): «В AI» / «От AI» — сразу после
        # «Исправить код» (обработка needs_ai_fix / needs_manual). Обработчики и
        # логика активации из DS_054 сохранены.
        # DS_087 §2.2: переименована в «3. В Ai» + tooltip.
        # DS_088a §1/§2.2: нажатие запускает полный AI-цикл (запрос → воркеры →
        # ожидание AI_RESPONSE → приём). Логика send_to_ai() не изменена.
        self.btn_to_ai = ttk.Button(control_frame, text="3. В Ai", command=self.start_ai_cycle, width=10)
        self.btn_to_ai.pack(side=tk.LEFT, padx=3)
        self.btn_to_ai.state(['disabled'])
        # DS_087 §2.2: tooltip «3. В Ai» (инстанс сохранён — для тестов).
        self._tooltip_to_ai = Tooltip(
            self.btn_to_ai,
            "Использовать LLM для корректировки ошибок, требующих Ai-анализа.")
        
        self.btn_from_ai = ttk.Button(control_frame, text="От AI", command=self.receive_from_ai, width=10)
        self.btn_from_ai.pack(side=tk.LEFT, padx=3)
        # DS_054_Уточнение_C: «От AI» активна только при наличии файлов-ответов
        # в EXCHANGE\AI_OUT (обновление — _update_ai_button_state, таймер 5 сек).
        self.btn_from_ai.state(['disabled'])
        
        # DS_079: галка «Только Ai» — фильтр отбора issues, требующих AI
        # (правило transform_type == "ignore"). По умолчанию ВКЛЮЧЕНА
        # (отправляем только AI). При выключенной — все issues (отладка,
        # обратная совместимость с DS_054). Рядом с группой AI-кнопок,
        # после «От AI» (сохраняет смежность «В AI»→«От AI» из DS_054_Уточнение).
        self.ai_only_var = tk.BooleanVar(value=True)
        self.chk_ai_only = ttk.Checkbutton(control_frame, text="Только Ai",
                                           variable=self.ai_only_var)
        self.chk_ai_only.pack(side=tk.LEFT, padx=3)

        # DS_088a_fix §2.5: пороги confidence — рядом с «Только Ai».
        # Часть C §2.6: поля добавляются ДО кнопок «Открыть рубикатор» /
        # «Генерация тестовых .plp» — те сдвигаются правее автоматически.
        self.conf_label = ttk.Label(control_frame, text="Пороги confidence:")
        self.conf_label.pack(side=tk.LEFT, padx=(10, 3))
        self.conf_low_var = tk.StringVar(value="0.5")
        self.conf_high_var = tk.StringVar(value="0.8")
        self.conf_low_entry = ttk.Entry(control_frame,
                                        textvariable=self.conf_low_var, width=5)
        self.conf_low_entry.pack(side=tk.LEFT)
        ttk.Label(control_frame, text="–").pack(side=tk.LEFT, padx=2)
        self.conf_high_entry = ttk.Entry(control_frame,
                                         textvariable=self.conf_high_var, width=5)
        self.conf_high_entry.pack(side=tk.LEFT)
        # DS_088b §2.5: один tooltip на метку «Пороги confidence:» (не на поля).
        self._tooltip_conf = Tooltip(
            self.conf_label,
            "Пороги confidence для AI-фиксов:\n"
            "— ниже нижнего порога: needs_manual (ручная проверка);\n"
            "— между порогами: средняя уверенность;\n"
            "— выше верхнего порога: авто-применение.\n"
            "Диапазон ввода: 0.0–1.0. Рекомендуемые значения: 0.5–0.8.")
        self._conf_low_prev = 0.5
        self._conf_high_prev = 0.8
        for _w in (self.conf_low_entry, self.conf_high_entry):
            _w.bind('<FocusOut>', lambda e: self._on_confidence_change())
            _w.bind('<Return>', lambda e: self._on_confidence_change())
        
        self.btn_rubricator = ttk.Button(control_frame, text="Открыть рубрикатор", command=self.open_rubricator, width=25)
        self.btn_rubricator.pack(side=tk.LEFT, padx=3)
        
        self.btn_test_gen = ttk.Button(control_frame, text="Генерация тестовых .plp", command=self.start_test_generation, width=30)
        self.btn_test_gen.pack(side=tk.LEFT, padx=3)
        
        self.btn_show_sql = ttk.Button(control_frame, text="Показать SQL для ручного исправления", command=self.show_sql_for_manual_fix, width=35)
        self.btn_show_sql.pack(side=tk.LEFT, padx=3)
        self.btn_show_sql.state(['disabled'])
        
        self.btn_send_koda = ttk.Button(control_frame, text="Отправить в Koda", command=self.send_to_koda, width=20)
        self.btn_send_koda.pack(side=tk.LEFT, padx=3)
        self.btn_send_koda.state(['disabled'])
        
        self.btn_receive_koda = ttk.Button(control_frame, text="Получить ответ", command=self.receive_from_koda, width=20)
        self.btn_receive_koda.pack(side=tk.LEFT, padx=3)
        self.btn_receive_koda.state(['disabled'])
        
        # DS 010: кнопка просмотра истории изменений РК
        self.btn_result_history = ttk.Button(control_frame, text="История РК", command=self.show_result_dir_history, width=15)
        self.btn_result_history.pack(side=tk.LEFT, padx=3)
        
        # Журнал выполнения — уменьшенный размер
        # DS_087 §2.6.4: journal_frame и его скроллбары сохранены в self
        # (проверяемость: верт. скроллбар должен быть видим).
        journal_frame = self.journal_frame = ttk.LabelFrame(scrollable_frame, text="Журнал выполнения", padding="5")
        journal_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=3)
        
        # Журнал с прокруткой (вертикальная + горизонтальная)
        log_scroll_y = self.log_scroll_y = ttk.Scrollbar(journal_frame, orient=tk.VERTICAL)
        log_scroll_x = self.log_scroll_x = ttk.Scrollbar(journal_frame, orient=tk.HORIZONTAL)
        
        self.log_text = scrolledtext.ScrolledText(journal_frame, 
                                                  wrap=tk.NONE,
                                                  font=('Consolas', 9),
                                                  yscrollcommand=log_scroll_y.set,
                                                  xscrollcommand=log_scroll_x.set,
                                                  height=8, width=58)
        
        log_scroll_y.config(command=self.log_text.yview)
        log_scroll_x.config(command=self.log_text.xview)
        
        # Кнопки журнала — ПОД полем (pack раньше, чтобы были внизу секции)
        journal_buttons = ttk.Frame(journal_frame)
        journal_buttons.pack(side=tk.BOTTOM, fill=tk.X, pady=(3, 0))
        
        # DS_087 §2.6.4: journal_frame занимает grid-строку 1 у parent
        # (scrollable_frame через create_window — pack для соседей). Явный
        # rowconfigure не нужен; проверяем, что Text + верт. скроллбар
        # влезают: width=58 символов Consolas 9 ≈ 510 px + скроллбар 17 px
        # + padding ≈ 560 px < 1200 (minsize) и < 1600 (базовый размер).
        self.btn_clear_log = ttk.Button(journal_buttons, text="Очистить журнал", command=self.clear_log)
        self.btn_clear_log.pack(side=tk.LEFT, padx=3)
        self.btn_copy_log = ttk.Button(journal_buttons, text="Копировать в буфер", command=self.copy_log)
        self.btn_copy_log.pack(side=tk.LEFT, padx=3)
        
        # DS 039: кнопка "Прервать" — полностью стандартный вид (без красного фона)
        self.btn_abort = tk.Button(
            journal_buttons,
            text="⏹ Прервать",
            command=self.on_abort_click,
            state='disabled',
            font=('Segoe UI', 9, 'bold'),
            padx=10, pady=2,
            relief=tk.RAISED
        )
        self.btn_abort.pack(side=tk.LEFT, padx=3)
        
        # Скроллы и журнал
        log_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        log_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Индикатор выполнения — процент в той же строке (под журналом)
        progress_frame = ttk.Frame(scrollable_frame, padding="5")
        progress_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # DS 040: стиль для жёлтого индикатора при прерывании
        style = ttk.Style()
        style.configure(
            "Yellow.Horizontal.TProgressbar",
            background='#FFA500',
            troughcolor='#e0e0e0',
            lightcolor='#FFA500',
            darkcolor='#FFA500'
        )
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_label = ttk.Label(progress_frame, text="0%", width=10)
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        # Цвета для логов
        self.log_text.tag_configure('info', foreground='black')
        self.log_text.tag_configure('warning', foreground='orange')
        self.log_text.tag_configure('error', foreground='red')
        self.log_text.tag_configure('success', foreground='green')
        self.log_text.tag_configure('debug', foreground='gray')
        self.log_text.tag_configure('highlight', foreground='green', font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure('pending', foreground='orange', font=('Consolas', 9, 'bold'))
        # DS 030: теги цветовой подсветки строк PlpCheck-отчёта
        self.log_text.tag_configure('class_method', foreground='#0066cc')
        self.log_text.tag_configure('line_number', foreground='#008000', font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure('issue_type', foreground='#cc6600')
        self.log_text.tag_configure('description', foreground='#000000')
        self.log_text.tag_configure('plan', foreground='#cc0000', font=('Consolas', 9, 'bold'))
        
        # DS 030: кликабельные ссылки на сохранённые отчёты (Отчёт/Методичка/DeepScan)
        self.log_text.tag_configure('report_link', foreground='#0066cc', underline=True,
                                    font=('Consolas', 9, 'bold'))
        self.log_text.tag_bind('report_link', '<Button-1>', self._open_report_link)
        self.log_text.tag_bind('report_link', '<Enter>',
                               lambda e: self.log_text.configure(cursor='hand2'))
        self.log_text.tag_bind('report_link', '<Leave>',
                               lambda e: self.log_text.configure(cursor=''))
        
        # Вкладка журнала изменений
        self.changelog_frame = ttk.LabelFrame(scrollable_frame, text="Журнал изменений", padding="5")
        self.changelog_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        
        self.changelog_text = scrolledtext.ScrolledText(self.changelog_frame,
                                                        wrap=tk.WORD,
                                                        font=('Consolas', 9),
                                                        height=10,
                                                        state='disabled')
        self.changelog_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки журнала изменений
        changelog_buttons = ttk.Frame(self.changelog_frame)
        changelog_buttons.pack(fill=tk.X, pady=(5, 0))
        
        self.btn_clear_changelog = ttk.Button(changelog_buttons, text="Очистить журнал", command=self.clear_changelog)
        self.btn_clear_changelog.pack(side=tk.LEFT, padx=3)
        self.btn_save_changelog = ttk.Button(changelog_buttons, text="Сохранить журнал в файл", command=self.save_changelog_to_file)
        self.btn_save_changelog.pack(side=tk.LEFT, padx=3)

        # DS_058+DS_057: тултипы для кнопок GUI
        self._apply_button_tooltips()

        # DS_054_Уточнение_C: таймер проверки AI_OUT (5 сек) — кнопка «От AI».
        self.root.after(5000, self._poll_ai_out)

        # Логируем загруженные файлы рубрикатора (после создания log_text)
        if self.rubricator_files:
            for code, name in self.rubricator_files.items():
                self.log(f"Загружен файл рубрикатора: {code} -> {name[:50]}...", 'debug')
    
        # Путь для дублирования логов
        self.logs_deep_dir = Path(__file__).parent.parent / 'logs_Deep'
        self.logs_deep_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = None
        
        # DS_053_Уточнение_2 (задача A): реестр скрываемых элементов GUI.
        # Вызывается ПОСЛЕДНИМ — все виджеты к этому моменту уже созданы.
        self._register_ui_hideables()
    
    def _apply_button_tooltips(self):
        """DS_058+DS_057: тултипы для всех кнопок GUI (1–2 предложения)."""
        tooltips = [
            (self.btn_scan, "Запустить сканирование исходных PLPlus-файлов "
                            "по выбранным рубрикаторам."),
            (self.btn_fix, "Автоматически исправить найденные проблемы "
                           "(детерминированный фикс + AI-fallback)."),
        (self.btn_to_ai, "Сформировать файл-запрос для AI "
                         "(проблемы, требующие AI-анализа)."),
        (getattr(self, 'chk_ai_only', None),
         "Отправлять только issues, требующие AI "
         "(transform_type=ignore + needs_ai_fix>0)."),
            (self.btn_rubricator, "Показать перечень файлов рубрикатора и "
                                  "текущий выбор правил."),
            (self.btn_test_gen, "Сгенерировать тестовые .plp-файлы "
                                "для выбранных правил."),
            (self.btn_show_sql, "Показать SQL-команды для ручного исправления "
                                "найденных проблем."),
            (self.btn_send_koda, "Сформировать задание для Koda "
                                 "(файловый обмен через EXCHANGE)."),
            (self.btn_receive_koda, "Загрузить результат выполнения задания "
                                    "от Koda."),
            (self.btn_result_history, "Просмотр истории изменений "
                                      "каталога результатов (РК)."),
            (self.btn_abort, "Прервать текущую операцию "
                             "(сканирование/исправление/генерацию)."),
            (getattr(self, 'btn_clear_log', None), "Очистить журнал выполнения."),
            (getattr(self, 'btn_copy_log', None), "Копировать содержимое журнала "
                                                  "в буфер обмена."),
            (getattr(self, 'btn_clear_changelog', None), "Очистить журнал изменений."),
            (getattr(self, 'btn_save_changelog', None), "Сохранить журнал изменений "
                                                        "в файл."),
        ]
        for widget, text in tooltips:
            if widget is not None:
                Tooltip(widget, text)
        # DS_054_Уточнение_C: тултип «От AI» — динамический (сохраняем ссылку,
        # текст обновляется в _update_ai_button_state по наличию файлов в AI_OUT).
        self._tooltip_from_ai = Tooltip(
            self.btn_from_ai,
            "Загрузить и применить ответы AI из каталога AI_OUT.")
        self._update_ai_button_state()

    # ------------------------------------------------------------------
    # DS_054_Уточнение_C: состояние кнопки «От AI» по содержимому AI_OUT
    # ------------------------------------------------------------------
    def _ai_out_files(self) -> list:
        """Файлы-ответы AI (AI_RESPONSE_*.md/json) в EXCHANGE\AI_OUT."""
        try:
            out_dir = Path(__file__).parent.parent / 'EXCHANGE' / 'AI_OUT'
            if not out_dir.exists():
                return []
            return sorted(list(out_dir.glob('AI_RESPONSE_*.md')) +
                          list(out_dir.glob('AI_RESPONSE_*.json')))
        except Exception:
            return []

    def _update_ai_button_state(self):
        """«От AI» disabled при пустом AI_OUT, normal — при наличии ответов.

        Тултип: «В AI_OUT нет файлов» / «Забрать ответы из AI_OUT (N файлов)».
        """
        btn = getattr(self, 'btn_from_ai', None)
        if btn is None:
            return
        files = self._ai_out_files()
        if files:
            btn.state(['!disabled'])
            tip = f"Забрать ответы из AI_OUT ({len(files)} файл(ов))."
        else:
            btn.state(['disabled'])
            tip = "В AI_OUT нет файлов"
        tooltip = getattr(self, '_tooltip_from_ai', None)
        if tooltip is not None:
            tooltip.text = tip

    # ── DS_087 §2.3: workflow «Скан → Фикс → Ai» ──────────────────────────
    def _result_dir_has_pattern_files(self) -> bool:
        """Есть ли файлы по Шаблону в каталоге результатов (включая подкаталоги)."""
        result = self.result_dir_var.get().strip()
        pattern = self.file_pattern_var.get().strip()
        if not result or not pattern:
            return False
        try:
            p = Path(result)
            if not p.exists() or not p.is_dir():
                return False
            if '**' in pattern:
                gen = p.glob(pattern)
            elif self.scan_recursive_var.get():
                gen = p.rglob(pattern)
            else:
                gen = p.glob(pattern)
            return any(True for _ in gen)
        except Exception:
            return False

    def _ai_in_request_files(self) -> list:
        """Файлы-запросы AI_REQUEST_*.md в EXCHANGE\AI_IN (маска из DS_087 §2.3)."""
        try:
            in_dir = Path(__file__).parent.parent / 'EXCHANGE' / 'AI_IN'
            if not in_dir.exists():
                return []
            return sorted(in_dir.glob('AI_REQUEST_*.md'))
        except Exception:
            return []

    def _update_workflow_buttons(self):
        """DS_087 §2.3: активация workflow 1→2→3 (условия, жирный шрифт).

        Ровно одна кнопка активна (state NORMAL + жирный), остальные
        disabled + обычный шрифт. Во время операции (scan_running) — не
        пересчитывать: их отключает/включает сам процесс operations.
        """
        if getattr(self, 'scan_running', False):
            return
        source = self.source_dir_var.get().strip()
        result = self.result_dir_var.get().strip()
        pattern = self.file_pattern_var.get().strip()
        any_rule = any(var.get() for var in self.selected_rules.values())
        scan_done = self.scan_results is not None
        fix_done = bool(scan_done and self.scan_results.get('fix_done'))
        cond_ai = fix_done and bool(self._ai_in_request_files())
        cond_fix = scan_done and self._result_dir_has_pattern_files()
        cond_scan = bool(source) and bool(result) and bool(pattern) and any_rule
        # Приоритет у позднего шага: workflow идёт 1→2→3.
        active = 'ai' if cond_ai else ('fix' if cond_fix else ('scan' if cond_scan else None))
        self._workflow_active = active
        for btn, key in ((getattr(self, 'btn_scan', None), 'scan'),
                         (getattr(self, 'btn_fix', None), 'fix'),
                         (getattr(self, 'btn_to_ai', None), 'ai')):
            if btn is None:
                continue
            if key == active:
                btn.state(['!disabled'])
                btn.configure(style='WorkflowActive.TButton')
            else:
                btn.state(['disabled'])
                btn.configure(style='WorkflowNormal.TButton')

    def _poll_ai_out(self):
        """Таймер (5 сек): периодическая проверка AI_OUT (DS_054_Уточнение_C)."""
        try:
            if not self.root.winfo_exists():
                return
            self._update_ai_button_state()
        except Exception:
            return
        try:
            self.root.after(5000, self._poll_ai_out)
        except Exception:
            pass

    def _check_log_size(self):
        """Проверка размера каталогов с логами и предложение очистки при превышении лимита"""
        log_dirs = [
            Path(__file__).parent.parent / 'logs',
            self.logs_deep_dir
        ]
        
        total_size = 0
        log_files = []
        
        # Собираем информацию о лог-файлах
        for log_dir in log_dirs:
            if log_dir.exists():
                for log_file in log_dir.glob('*.log'):
                    file_size = log_file.stat().st_size
                    total_size += file_size
                    log_files.append((log_file, file_size))
                for md_file in log_dir.glob('*.md'):
                    file_size = md_file.stat().st_size
                    total_size += file_size
                    log_files.append((md_file, file_size))
        
        # Проверяем превышение лимита
        max_size_bytes = MAX_LOG_SIZE_MB * 1024 * 1024
        if total_size > max_size_bytes:
            size_mb = total_size / (1024 * 1024)
            # Каталоги логов (только существующие)
            log_dirs_str = '\n'.join(
                f'  - {d}' for d in log_dirs if d.exists()
            )
            # Путь к файлу настроек (единый источник — метод класса)
            settings_path = self._settings_path()
            result = messagebox.askyesno(
                "Лимит логов превышен",
                f"Размер файлов логов: {size_mb:.2f} МБ\n"
                f"Максимальный размер: {MAX_LOG_SIZE_MB} МБ\n\n"
                f"Настройка: {settings_path} (max_log_size_mb)\n"
                f"Каталоги для очистки:\n{log_dirs_str}\n\n"
                f"Удалить все файлы логов (.log, .md) из этих каталогов?"
            )
            
            if result:
                # Удаляем все файлы логов
                deleted_count = 0
                for log_dir in log_dirs:
                    if log_dir.exists():
                        for file_path in log_dir.glob('*'):
                            if file_path.suffix.lower() in ['.log', '.md']:
                                try:
                                    file_path.unlink()
                                    deleted_count += 1
                                except Exception:
                                    pass
                
                self.log(f"Удалено файлов логов: {deleted_count}", 'info')
                messagebox.showinfo("Очистка завершена", f"Удалено файлов логов: {deleted_count}")
            else:
                self.log(f"Предупреждение о размере логов проигнорировано ({size_mb:.2f} МБ)", 'warning')
    
    def _load_rubricator_files(self):
        """Загрузка информации о файлах рубрикатора"""
        try:
            file_path = self.rubricator_dir / '1.RUBRICATOR_FILES v5.md'
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        # Пропускаем заголовки и разделители
                        if line.startswith('#') or line.startswith('|---') or not line.strip():
                            continue
                        if '|' in line:
                            parts = [p.strip() for p in line.split('|')]
                            # Формат без закрывающего |: | N | Признак | Код файла | Полное имя файла
                            # parts: ['', '1', '+', 'v50', 'F:\TO_DBI\...']
                            if len(parts) >= 5:
                                code = parts[3].strip()
                                name = parts[4].strip()
                                sign = parts[2].strip()  # '+' или '-'
                                if code and not code.lower() in ['n', '№', 'код файла', '']:
                                    self.rubricator_files[code] = name
                                    # Сохраняем признак обработки (+/-)
                                    if not hasattr(self, '_rubricator_file_signs'):
                                        self._rubricator_file_signs = {}
                                    self._rubricator_file_signs[code] = (sign == '+')
        except Exception as e:
            print(f"Ошибка загрузки рубрикатора: {e}")
    
    def _populate_rules_tree(self):
        """Заполнение Treeview правилами (DS_058+DS_057: 4 родительских
        чекбокса рубрикаторов + дочерние чекбоксы конкретных правил)"""
        # Очищаем дерево
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        self._rubricator_rule_vars = {}
        self._rubricator_parent_items = {}
        self._rule_item_map = {}
        self._rubricator_rules_by_file = {}
        self._tree_tooltips = {}

        # Загружаем расширенный рубрикатор (нужен для списка rule_code)
        self._load_rubricator_prompts()

        # Список всех правил (rule_code + описание)
        all_rules = []
        if self.rubricator_prompts and self.rubricator_prompts.loaded:
            all_rules = self.rubricator_prompts.get_all_rules()

        # DS_058+DS_057: инициализация состояния правил из settings.json
        # (при отсутствии ключа — из 1.RUBRICATOR_FILES v5.md, вариант C)
        rule_states = self._init_rubricator_rule_states([r['code'] for r in all_rules])

        # Группировка правил по рубрикаторам (по префиксу rule_code)
        for r in all_rules:
            for file_code, prefix in RUBRICATOR_PREFIXES.items():
                if r['code'].startswith(prefix):
                    self._rubricator_rules_by_file.setdefault(file_code, []).append(r['code'])
                    break

        # Строим дерево: родитель — рубрикатор, дети — конкретные правила
        for code, name in self.rubricator_files.items():
            rule_codes = self._rubricator_rules_by_file.get(code, [])
            # Состояние файла: включён, если включено хотя бы одно его правило
            enabled = any(rule_states.get(rc, False) for rc in rule_codes)
            var = tk.BooleanVar(value=enabled)
            self.selected_rules[code] = var

            # Родительский элемент (рубрикатор)
            parent_id = self.rules_tree.insert(
                '', tk.END, text=code, open=False,
                values=('✓' if enabled else '✗', code, name))
            self.rule_checkboxes[code] = (parent_id, var)
            self._rubricator_parent_items[parent_id] = code
            self._tree_tooltips[parent_id] = RUBRICATOR_TOOLTIPS.get(
                code, f"Рубрикатор {code}")

            # Дочерние элементы (конкретные правила)
            for rc in rule_codes:
                rule = self.rubricator_prompts.get_rule(rc) or {}
                desc = rule.get('short_description', rc)
                rule_enabled = bool(rule_states.get(rc, False))
                rule_var = tk.BooleanVar(value=rule_enabled)
                self._rubricator_rule_vars[rc] = rule_var
                child_id = self.rules_tree.insert(
                    parent_id, tk.END, text='•',
                    values=('✓' if rule_enabled else '✗', rc, desc))
                self._rule_item_map[child_id] = rc
                self._tree_tooltips[child_id] = f"{rc}\n{desc}"

            # Синхронизация флага PlpCheck с признаком из рубрикатора
            if code == 'PlpCheck':
                self.plpcheck_enabled_var.set(enabled)

        # Обработчик клика для переключения чекбокса
        self.rules_tree.bind('<Button-1>', self._on_rule_click)
        # DS_058+DS_057: тултипы при наведении на строки дерева
        self.rules_tree.bind('<Motion>', self._on_tree_motion)
        self.rules_tree.bind('<Leave>', lambda e: self._hide_tree_tooltip())
        self._update_buttons_state()

    def _on_tree_motion(self, event):
        """DS_058+DS_057: тултип для строки дерева правил (код + описание)."""
        item = self.rules_tree.identify_row(event.y)
        if not item or item not in self._tree_tooltips:
            self._hide_tree_tooltip()
            return
        text = self._tree_tooltips[item]
        if self._tree_tooltip_text == text:
            return
        self._hide_tree_tooltip()
        x = self.rules_tree.winfo_rootx() + event.x + 12
        y = self.rules_tree.winfo_rooty() + event.y + 14
        tip = tk.Toplevel(self.rules_tree)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f'+{x}+{y}')
        tk.Label(tip, text=text, background='#FFFFE0', relief=tk.SOLID,
                 borderwidth=1, justify=tk.LEFT, font=('Segoe UI', 9),
                 wraplength=480).pack()
        self._tree_tooltip = tip
        self._tree_tooltip_text = text

    def _hide_tree_tooltip(self):
        tip = getattr(self, '_tree_tooltip', None)
        if tip is not None:
            try:
                tip.destroy()
            except Exception:
                pass
            self._tree_tooltip = None
        self._tree_tooltip_text = None

    def _settings_path(self) -> Path:
        return Path(__file__).parent / 'settings.json'

    def _read_settings_json(self) -> dict:
        try:
            p = self._settings_path()
            if p.exists():
                with open(p, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _write_settings_json(self, settings: dict):
        with open(self._settings_path(), 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    def _init_rubricator_rule_states(self, all_rule_codes) -> dict:
        """DS_058+DS_057 (вариант C + дополнение): состояние правил.

        - Ключа rubricator_selected_rules нет — инициализация из
          1.RUBRICATOR_FILES v5.md (+ -> true, прочее -> false) и сохранение
          в settings.json.
        - Ключ есть — использовать только его; отсутствующие правила
          (новые) добавить со значением false и сохранить (если были
          добавления). 1.RUBRICATOR_FILES v5.md только читается.
        """
        settings = self._read_settings_json()
        saved = settings.get('rubricator_selected_rules')

        if saved is None:
            # Первый запуск: признаки из 1.RUBRICATOR_FILES v5.md
            signs = getattr(self, '_rubricator_file_signs', {})
            states = {}
            for rc in all_rule_codes:
                prefix = None
                for file_code, p in RUBRICATOR_PREFIXES.items():
                    if rc.startswith(p):
                        prefix = file_code
                        break
                states[rc] = bool(signs.get(prefix, False)) if prefix else False
            settings['rubricator_selected_rules'] = states
            try:
                self._write_settings_json(settings)
            except Exception as e:
                print(f"Не удалось сохранить rubricator_selected_rules: {e}")
            return states

        # Ключ есть: дополнить новыми правилами (false), существующие не трогать
        states = {k: bool(v) for k, v in saved.items()}
        added = False
        for rc in all_rule_codes:
            if rc not in states:
                states[rc] = False
                added = True
        if added:
            settings['rubricator_selected_rules'] = states
            try:
                self._write_settings_json(settings)
            except Exception as e:
                print(f"Не удалось дополнить rubricator_selected_rules: {e}")
        return states

    def _update_rubricator_parent_state(self, file_code):
        """Пересчёт состояния родительского чекбокса по дочерним правилам."""
        if file_code not in self.rule_checkboxes:
            return
        parent_id, var = self.rule_checkboxes[file_code]
        rule_codes = self._rubricator_rules_by_file.get(file_code, [])
        enabled = any(self._rubricator_rule_vars[rc].get()
                      for rc in rule_codes if rc in self._rubricator_rule_vars)
        if var.get() != enabled:
            var.set(enabled)
        all_on = all(self._rubricator_rule_vars[rc].get()
                     for rc in rule_codes if rc in self._rubricator_rule_vars)
        sign = '✓' if all_on else ('◐' if enabled else '✗')
        self.rules_tree.set(parent_id, 'selected', sign)
    
    def _load_rubricator_prompts(self):
        """Загрузка расширенного рубрикатора 4.RUBRICATOR_PROMPT v5.json"""
        try:
            self.rubricator_prompts = RubricatorPrompts(self.rubricator_dir)
            if self.rubricator_prompts.load():
                self.log(f"Загружен расширенный рубрикатор: 4.RUBRICATOR_PROMPT v5.json", 'debug')
                # Вывод доступных правил
                rules = self.rubricator_prompts.get_all_rules()
                for rule in rules:
                    self.log(f"  Правило: {rule['code']} ({rule.get('category', 'N/A')})", 'debug')
            else:
                self.log("Расширенный рубрикатор не найден или не загружен", 'warning')
        except Exception as e:
            self.log(f"Ошибка загрузки расширенного рубрикатора: {e}", 'error')
    
    def _on_rule_click(self, event):
        """Обработка клика по правилу (DS_058+DS_057: родитель — групповое
        включение/выключение рубрикатора, дочерний — отдельное правило)"""
        item = self.rules_tree.identify_row(event.y)
        column = self.rules_tree.identify_column(event.x)

        # Колонка "Выбрано" (индекс 1)
        if column != '#1':
            return

        # Клик по родительскому чекбоксу рубрикатора
        if item in self._rubricator_parent_items:
            file_code = self._rubricator_parent_items[item]
            rule_codes = self._rubricator_rules_by_file.get(file_code, [])
            existing = [rc for rc in rule_codes if rc in self._rubricator_rule_vars]
            if not existing:
                return
            # Все включены -> выключить все; иначе -> включить все
            new_state = not all(self._rubricator_rule_vars[rc].get() for rc in existing)
            for rc in existing:
                self._rubricator_rule_vars[rc].set(new_state)
                for child_id, mapped_rc in self._rule_item_map.items():
                    if mapped_rc == rc:
                        self.rules_tree.set(child_id, 'selected',
                                            '✓' if new_state else '✗')
            self._update_rubricator_parent_state(file_code)
            self.rules_changed = True
            self._reset_progress()
            self.log(f"Рубрикатор {file_code}: "
                     f"{'все правила включены' if new_state else 'все правила выключены'}",
                     'debug')
            if file_code == 'PlpCheck':
                self.plpcheck_enabled_var.set(new_state)
            self._update_buttons_state()
            return

        # Клик по дочернему чекбоксу конкретного правила
        rc = self._rule_item_map.get(item)
        if rc is None:
            return
        var = self._rubricator_rule_vars[rc]
        var.set(not var.get())
        self.rules_tree.set(item, 'selected', '✓' if var.get() else '✗')
        self.rules_changed = True
        self._reset_progress()
        self.log(f"Правило {rc}: {'включено' if var.get() else 'выключено'}", 'debug')
        # Обновляем родительский чекбокс (файл включён, если хоть одно правило вкл.)
        for file_code, prefix in RUBRICATOR_PREFIXES.items():
            if rc.startswith(prefix):
                self._update_rubricator_parent_state(file_code)
                if file_code == 'PlpCheck':
                    self.plpcheck_enabled_var.set(
                        self.rule_checkboxes['PlpCheck'][1].get())
                break
        # Обновляем доступность кнопок
        self._update_buttons_state()

    def _sync_plpcheck_checkbox(self):
        """Синхронизация флага PlpCheck с чекбоксами правил plpcheck.* в дереве"""
        rule_codes = self._rubricator_rules_by_file.get('PlpCheck', [])
        new_state = self.plpcheck_enabled_var.get()
        for rc in rule_codes:
            if rc in self._rubricator_rule_vars:
                self._rubricator_rule_vars[rc].set(new_state)
        for child_id, mapped_rc in self._rule_item_map.items():
            if mapped_rc.startswith('plpcheck.'):
                self.rules_tree.set(child_id, 'selected',
                                    '✓' if new_state else '✗')
        self._update_rubricator_parent_state('PlpCheck')
        self.rules_changed = True
        self._reset_progress()
    
    def on_abort_click(self):
        """DS 038 + DS_089a §2.2: toggle «Прервать»/«Продолжить».
        Первый клик — scan_aborted=True, текст → «▶ Продолжить»;
        второй — scan_aborted=False, текст → «⏹ Прервать»."""
        if not self.scan_running:
            return

        # --- ПРОДОЛЖИТЬ (второй клик) ---
        if self.scan_aborted:
            self.scan_aborted = False
            self._stop_event.clear()  # DS_089b: сброс сигнала остановки
            self._progress_frozen = False
            # DS_089b §2.6: если есть сохранённое состояние — подсказка о resume.
            # Состояние НЕ потребляется: resume применяется при следующем
            # запуске «Сканировать»/«Исправить» (поток уже завершился бы).
            if getattr(self, '_abort_state', None):
                self.log("[DS_089b] Есть сохранённое состояние прерванной "
                         "операции: следующий запуск пропустит обработанное.",
                         'info')
            try:
                if hasattr(self, 'progress'):
                    self.progress.configure(style="Horizontal.TProgressbar")
                    self.progress.update_idletasks()
            except Exception as e:
                print(f"[DS_089a] Ошибка сброса стиля: {e}")
            self.btn_abort.config(text="⏹ Прервать")
            _ts = time.strftime("%H:%M:%S")
            self.log(f"[{_ts}] Операция продолжена", 'info')
            return

        # --- ПРЕРВАТЬ (первый клик) ---
        try:
            if hasattr(self, 'progress'):
                self.progress.configure(style="Yellow.Horizontal.TProgressbar")
                self.progress.update_idletasks()
        except Exception as e:
            print(f"[DS 041] Ошибка перекраски индикатора: {e}")
        self._progress_frozen = True

        self.scan_aborted = True
        self._stop_event.set()  # DS_089b: потокобезопасный сигнал остановки
        # DS_089b §2.2: _abort_state сохраняется в конце _run_scan/_run_fix,
        # когда поток завершился и обработанные ключи/файлы точно известны.
        self.btn_abort.config(text="▶ Продолжить")
        _ts = time.strftime("%H:%M:%S")
        self.log(f"[{_ts}] Мягкое прерывание запрошено.", 'warning')
        self.log(f"[{_ts}] Текущий файл будет дочитан, затем операция остановится.", 'warning')
        # DS_089a §2.7: прогноз времени до фактического останова.
        try:
            _done = getattr(self, '_op_files_done', 0) or 0
            _total = getattr(self, '_op_total_files', 0) or 0
            _start = getattr(self, '_op_start_time', None)
            if _start and _total and _done and _done < _total:
                _elapsed = time.time() - _start
                _eta = int(round(_elapsed / _done * (_total - _done)))
                self.log(
                    f"[{_ts}] Прогноз: остановка через ~{_eta} сек "
                    f"(осталось {_total - _done} из {_total} файлов).",
                    'warning')
            elif _total and _done and _done >= _total:
                self.log(
                    f"[{_ts}] Прогноз: сканирование почти завершено "
                    f"(~1 сек).",
                    'warning')
            else:
                self.log(
                    f"[{_ts}] Прогноз: AI-цикл — ~30 сек (без данных о файлах).",
                    'warning')
        except Exception:
            pass
    
    def _abort_requested(self) -> bool:
        """DS 038: callback для сканера — проверка флага прерывания (потокобезопасно)."""
        return self.scan_aborted
    
    # ------------------------------------------------------------------
    # DS_089b §2.2/§2.3: ключ и фильтр resume-состояния (тестируемые методы).
    # Формат ключа — тот же, что дедупликация в scanner.py:1636–1637.
    # ------------------------------------------------------------------
    @staticmethod
    def _ds089b_issue_key(issue) -> tuple:
        """DS_089b: ключ issue = (file_path, line_number, issue_type,
        description, match_fragment)."""
        return (issue.file_path, issue.line_number, issue.issue_type,
                issue.description, issue.match_fragment)

    @classmethod
    def _ds089b_processed_keys(cls, issues) -> list:
        """DS_089b §2.2: список ключей обработанных issues для _abort_state."""
        return [cls._ds089b_issue_key(i) for i in issues]

    @classmethod
    def _ds089b_filter_processed(cls, issues, prev_keys) -> list:
        """DS_089b §2.3: исключить issues с ранее обработанными ключами."""
        return [i for i in issues if cls._ds089b_issue_key(i) not in prev_keys]
    
    def _set_status_running(self):
        """DS 043: установить статус 'Выполняется...' при старте длительной операции."""
        try:
            self.status_label.config(text="Выполняется...")
        except Exception as e:
            print(f"[DS 043] Ошибка установки статуса: {e}")

    def _start_abortable_operation(self):
        """DS 038: активировать кнопку «Прервать» перед запуском операции."""
        # DS 043: статус-бар → "Выполняется..." сразу при старте любой из
        # трёх длительных операций (скан/фикс/тест-генерация)
        self._set_status_running()
        self.scan_running = True
        self.scan_aborted = False
        # DS 041: разморозить индикатор для новой операции
        self._progress_frozen = False
        # DS 040: сброс стиля индикатора (стандартный цвет) при старте новой операции
        if hasattr(self, 'progress'):
            self.progress.configure(style="Horizontal.TProgressbar")
        if self.btn_abort:
            self.btn_abort.config(state='normal')
            # DS_089a §2.2: сброс toggle-текста при старте операции
            try:
                self.btn_abort.config(text="⏹ Прервать")
            except Exception:
                pass
    
    def _finish_abortable_operation(self):
        """DS 038: сбросить флаги и деактивировать кнопку «Прервать» (в finally).

        DS_108a: дополнительно сбросить статус-бар, прогресс-бар и
        _progress_frozen, чтобы UI не оставался в состоянии «Выполняется...».
        """
        self.scan_running = False
        self.scan_aborted = False
        # DS 042: гарантированный сброс кнопки «Прервать» с проверкой существования
        try:
            if self.btn_abort and self.btn_abort.winfo_exists():
                self.btn_abort.config(state='disabled')
                # DS_089a §2.2: сброс toggle-текста при завершении операции
                self.btn_abort.config(text="⏹ Прервать")
                self.btn_abort.update_idletasks()
        except Exception as e:
            print(f"[DS 042] Ошибка сброса btn_abort: {e}")
        # DS_108a: сброс статуса и прогресса после завершения операции
        self._progress_frozen = False
        try:
            self.set_status("Готово")
        except Exception as e:
            print(f"[DS_108a] Ошибка сброса status: {e}")
        try:
            self._reset_progress()
        except Exception as e:
            print(f"[DS_108a] Ошибка сброса progress: {e}")
    
    def _play_result_sound(self, success: bool, duration: float):
        """DS_088b §2.2: звук завершения операции (Windows-only).

        duration — время операции в секундах. Если duration меньше
        sound_min_duration (settings.json, по умолчанию 30) — звук не играет.
        Победные: 1000→1200→1500; печальные: 1500→1200→1000.
        При RuntimeError (нет доступа к динамику) — fallback MessageBeep.
        """
        try:
            min_dur = float(self._read_settings_json().get(
                'sound_min_duration', 30))
        except Exception:
            min_dur = 30
        if duration < min_dur:
            return
        try:
            import winsound
            if success:
                winsound.Beep(1000, 300)
                winsound.Beep(1200, 300)
                winsound.Beep(1500, 500)
            else:
                winsound.Beep(1500, 300)
                winsound.Beep(1200, 300)
                winsound.Beep(1000, 500)
        except (ImportError, RuntimeError):
            try:
                import winsound
                if success:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                else:
                    winsound.MessageBeep(winsound.MB_ICONHAND)
            except Exception:
                pass
        except Exception:
            pass

    def _progress_update(self, pct, force=False):
        """DS 041: установить индикатор выполнения.
        При заморозке (прерывание) обычные обновления игнорируются —
        индикатор остаётся на проценте прерывания (одинаковая длина).
        force=True — явная установка процента прерывания (разрешена)."""
        if self._progress_frozen and not force:
            return
        self.root.after(0, lambda p=pct: self.progress.config(value=p))
        self.root.after(0, lambda p=pct: self.progress_label.config(text=f"{p:.2f}%" if isinstance(p, float) else f"{p}%"))
    
    def _on_plpcheck_toggle(self):
        """DS 036: Включить/отключить доступность дочерних чекбоксов PlpCheck."""
        enabled = self.plpcheck_enabled_var.get()
        state = 'normal' if enabled else 'disabled'
        
        # Чекбокс "Выбрать все"
        if hasattr(self, 'chk_plpcheck_all'):
            self.chk_plpcheck_all.config(state=state)
        
        # 8 чекбоксов категорий
        if hasattr(self, 'chk_plpcheck_categories'):
            for chk in self.chk_plpcheck_categories.values():
                chk.config(state=state)
    
    def _toggle_all_plpcheck_categories(self):
        """DS 036: Установить/снять все флаги PlpCheck-категорий."""
        if not self.plpcheck_enabled_var.get():
            return
        value = self.var_plpcheck_all.get()
        for var in self.var_plpcheck_categories.values():
            var.set(value)
    
    def _update_plpcheck_all_checkbox(self):
        """DS 036: Синхронизировать флаг 'Выбрать все' с состоянием категорий.
        DS 038 (Проблема D): синхронизация работает в ОБОИХ направлениях и
        не зависит от флага PlpCheck (ранее при выключенном PlpCheck
        синхронизация прерывалась и «Выбрать все» застревал в неверном состоянии).
        """
        if not hasattr(self, 'var_plpcheck_categories') or not self.var_plpcheck_categories:
            return
        all_selected = all(var.get() for var in self.var_plpcheck_categories.values())
        if self.var_plpcheck_all.get() != all_selected:
            self.var_plpcheck_all.set(all_selected)
    
    def _has_selected_plpcheck_categories(self) -> bool:
        """DS 036: Есть ли хотя бы одна выбранная категория PlpCheck."""
        if not self.plpcheck_enabled_var.get():
            return True  # PlpCheck не выбран — не мешаем
        return any(var.get() for var in self.var_plpcheck_categories.values())
    
    def _check_plpcheck_categories_before_action(self) -> bool:
        """
        DS 036: Проверка перед действиями (Сканировать, Исправлять, Генерация).
        Возвращает True, если можно продолжать; False — если пользователь отменил.
        """
        if not self.plpcheck_enabled_var.get():
            return True  # PlpCheck не выбран — не мешаем
        
        if self._has_selected_plpcheck_categories():
            return True  # Хотя бы одна категория выбрана — OK
        
        # Ни одна категория не выбрана — предупреждаем
        result = messagebox.askyesno(
            "PlpCheck: категории не выбраны",
            "Рубрикатор PlpCheck выбран, но ни одна категория не отмечена.\n\n"
            "PlpCheck-правила не будут применены.\n\n"
            "Продолжить без PlpCheck-правил?",
            icon='warning'
        )
        return result
    
    def _on_priority_filter_change(self):
        """Обработка изменения чекбоксов HIGH/MEDIUM/LOW (DS 018)"""
        selected = []
        if self.priority_high_var.get():
            selected.append('HIGH')
        if self.priority_medium_var.get():
            selected.append('MEDIUM')
        if self.priority_low_var.get():
            selected.append('LOW')
        
        # Обновляем статус
        if selected:
            self.priority_status_label.config(text=f"Активны: {', '.join(selected)}", foreground='green')
        else:
            self.priority_status_label.config(text="Все приоритеты", foreground='gray')
        
        # Сохраняем для использования в сканировании
        self._selected_priorities = selected
        
        # Логируем
        self.log(f"Фильтр по приоритетам: {', '.join(selected) if selected else 'все'}", 'info')
        
        self._update_buttons_state()
    
    def get_selected_priorities(self):
        """Возвращает выбранные приоритеты HIGH/MEDIUM/LOW (DS 018)"""
        return list(self._selected_priorities)
    
    def _update_archive_state(self):
        """Обновление доступности чекбокса архивирования"""
        if self.preserve_structure_var.get():
            self.archive_result_check.state(['!disabled'])
        else:
            self.archive_result_check.state(['disabled'])
            self.archive_result_var.set(False)
    
    def _refresh_rubricator_tree(self):
        """
        Обновляет список рубрикаторов в Treeview — показывает все строки.
        Вызывается при отключении всех приоритетов.
        """
        for code, (item_id, var) in self.rule_checkboxes.items():
            self.rules_tree.item(item_id, values=self.rules_tree.item(item_id)['values'])
            self.rules_tree.item(item_id, open=True)
        self.log("  Список рубрикаторов обновлён (показаны все файлы)", 'info')
    
    def _bind_entry_events(self):
        """Привязка событий для поля ввода - логирование только при потере фокуса"""
        # Привязываем события потери фокуса для полей ввода
        if self.source_entry:
            self.source_entry.bind('<FocusOut>', self._on_source_focus_out)
            # Также привязываем событие изменения для автоматического обновления результата
            self.source_dir_var.trace_add('write', lambda *args: self._on_source_dir_changed())
            # DS 008/009: обновление цветовой индикации и меток статуса при изменении ИК
            self.source_dir_var.trace_add('write', lambda *args: self._update_dir_indicators())
        if self.result_entry:
            self.result_entry.bind('<FocusOut>', self._on_result_focus_out)
            # DS 008/009: обновление цветовой индикации и меток статуса при изменении РК
            self.result_dir_var.trace_add('write', lambda *args: self._update_dir_indicators())
        
        # DS 008/009: первичное обновление индикации каталогов
        self._update_dir_indicators()
    
        # Привязка события изменения чекбоксов и комбобоксов
        self.only_modified_var.trace_add('write', lambda *args: (self._reset_progress(), self._update_buttons_state()))
        self.preserve_structure_var.trace_add('write', lambda *args: (self._reset_progress(), self._update_buttons_state()))
        self.log_level_var.trace_add('write', lambda *args: self._reset_progress())
        self.scan_recursive_var.trace_add('write', lambda *args: self._reset_progress())
        self.file_pattern_var.trace_add('write', lambda *args: self._update_buttons_state())
        # DS 54 §2: полный набор триггеров пересчёта активации кнопок —
        # любые изменения в боксах 1-3 должны переключать «Сканировать»/«В Ai».
        self.file_pattern_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.scan_recursive_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.log_level_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.report_stats_min_files_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.only_modified_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.preserve_structure_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.plpcheck_enabled_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.priority_high_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.priority_medium_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.priority_low_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.clean_output_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.fix_only_found_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        self.archive_result_var.trace_add('write', lambda *args: self._update_workflow_buttons())
        
        # Привязка события изменения выбора в рубрикаторе
        self.root.after(100, self._update_buttons_state)

    def _attach_context_menu(self, widget, is_text=False):
        """DS_088b §2.3: контекстное меню (ПКМ) для Entry/Text.

        Выделить всё / Копировать / Вставить; для Text — ещё «Очистить».
        """
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(
            label="Выделить всё",
            command=lambda: widget.event_generate('<<SelectAll>>'))
        menu.add_command(
            label="Копировать",
            command=lambda: widget.event_generate('<<Copy>>'))
        menu.add_command(
            label="Вставить",
            command=lambda: widget.event_generate('<<Paste>>'))
        if is_text:
            menu.add_separator()
            menu.add_command(
                label="Очистить",
                command=lambda: widget.delete('1.0', 'end'))
        widget.bind('<Button-3>',
                    lambda e: menu.tk_popup(e.x_root, e.y_root))
        widget._context_menu = menu
        return menu

    def _attach_all_context_menus(self, parent=None):
        """DS_088b §2.3: рекурсивно навесить контекстное меню на все Entry/Text.

        Исключения: Treeview (рубрикатор), Combobox (уровень лога), Checkbutton,
        Label — они не Entry/Text и не затрагиваются.
        """
        if parent is None:
            parent = self.root
        count = 0
        for child in parent.winfo_children():
            try:
                cls = child.winfo_class()
            except Exception:
                cls = ''
            if cls in ('Entry', 'TEntry'):
                self._attach_context_menu(child, is_text=False)
                count += 1
            elif cls == 'Text':
                self._attach_context_menu(child, is_text=True)
                count += 1
            count += self._attach_all_context_menus(child)
        return count

    def _on_source_dir_changed(self):
        """Обработка изменения исходного каталога - автоматическое обновление результата (DS 013: с детальным логированием)"""
        # === ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ ВЫЧИСЛЕНИЯ РК ===
        self.log("=" * 60)
        self.log("🔍 ВЫЧИСЛЕНИЕ РК")
        self.log("=" * 60)
        
        # 1. Получаем значение ИК
        source_dir = self.source_dir_var.get().strip()
        self.log(f"📁 ИК (исходный): '{source_dir}'")
        self.log(f"📏 Длина ИК: {len(source_dir)}")
        
        if not source_dir:
            self.log("⚠️ ИК пуст, РК не изменяется")
            self.log("=" * 60)
            self.log("🔍 КОНЕЦ ВЫЧИСЛЕНИЯ РК")
            self.log("=" * 60)
            return
        
        # 2. Проверяем наличие PATCH_IN
        has_patch_in = 'PATCH_IN' in source_dir
        self.log(f"🔎 Найдено 'PATCH_IN': {has_patch_in}")
        
        if has_patch_in:
            # 3. Находим позицию PATCH_IN
            patch_index = source_dir.find('PATCH_IN')
            self.log(f"📍 Позиция 'PATCH_IN': {patch_index}")
            
            # 4. Показываем части пути
            before = source_dir[:patch_index]
            after = source_dir[patch_index + len('PATCH_IN'):]
            self.log(f"📂 До 'PATCH_IN': '{before}'")
            self.log(f"📂 После 'PATCH_IN': '{after}'")
            
            # 5. Выполняем замену (DS 011/012: полная замена всех вхождений)
            result_dir = source_dir.replace('PATCH_IN', 'PATCH_OUT')
            self.log(f"🔄 Результат replace(): '{result_dir}'")
            
            # 6. Альтернативный способ (для проверки)
            alt_result = before + 'PATCH_OUT' + after
            self.log(f"🔄 Альтернативный результат: '{alt_result}'")
        else:
            result_dir = None
            self.log("ℹ️ В ИК отсутствует 'PATCH_IN'. РК не изменён.")
        
        # 7. Автоподстановка через _auto_fill_result_dir (сохраняет trailing slash)
        result_path = self._auto_fill_result_dir(source_dir) if result_dir else None
        
        # 8. Фиксируем итоговое значение РК
        actual_result = self.result_dir_var.get()
        self.log(f"🔍 Фактическое значение РК: '{actual_result}'")
        
        if result_path is not None:
            # DS 010: логирование автоматического обновления РК в историю
            self.log_result_dir_change(source_dir, str(result_path), action="auto_update")
            self.log(f"🔄 Автоматически обновлён РК: {result_path}")
            # 9. Сравниваем ожидание и реальность
            if result_dir and result_dir.rstrip(chr(92)) == actual_result.rstrip(chr(92)):
                self.log("✅ РК установлен корректно")
            else:
                self.log(f"❌ РАСХОЖДЕНИЕ! Ожидалось: '{result_dir}', Получено: '{actual_result}'")
            # 10. Вывод вычисленного РК в Журнал
            self.log(f"📝 ВЫЧИСЛЕННЫЙ РК: {result_path}")
        
        # Обновить состояние кнопок
        self._update_buttons_state()
        
        self.log("=" * 60)
        self.log("🔍 КОНЕЦ ВЫЧИСЛЕНИЯ РК")
        self.log("=" * 60)
    
    def update_result_dir_from_source(self, source_dir):
        """Резервный метод обновления РК (DS 012).
        Возвращает РК с заменой PATCH_IN -> PATCH_OUT (сохраняется весь хвост пути).
        """
        if source_dir and 'PATCH_IN' in source_dir:
            return source_dir.replace('PATCH_IN', 'PATCH_OUT')
        return source_dir
    
    def _auto_fill_result_dir(self, source_dir: Path):
        """Автоматическое формирование каталога результатов из исходного (DS 011).
        PATCH_IN + подкаталоги -> PATCH_OUT + те же подкаталоги (структура сохраняется)
        PATCH_OUT + подкаталоги -> PATCH_IN + те же подкаталоги
        """
        BS = chr(92)  # обратный слэш
        source_str = str(source_dir).replace('/', BS)
        
        # Сохраняем завершающий слэш (если был), работаем с путём без него
        trailing = BS if source_str.endswith(BS) else ''
        core = source_str.rstrip(BS).rstrip('/')
        
        if 'PATCH_IN' in core:
            # PATCH_IN\xxx -> PATCH_OUT\xxx (заменяем все вхождения PATCH_IN)
            result_str = core.replace('PATCH_IN', 'PATCH_OUT') + trailing
        elif 'PATCH_OUT' in core:
            # PATCH_OUT\xxx -> PATCH_IN\xxx (заменяем все вхождения PATCH_OUT)
            result_str = core.replace('PATCH_OUT', 'PATCH_IN') + trailing
        else:
            return None
        
        result_path = Path(result_str.rstrip(BS))
        
        # ============================================================
        # ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ РК (DS 017: условие блокировки убрано)
        # РК обновляется всегда при изменении ИК, без проверки текущего значения
        # ============================================================
        self.result_dir_var.set(result_str)
        
        # DS 014: проверка, что значение не было перезаписано другим кодом
        actual = self.result_dir_var.get()
        if actual != result_str:
            self.log(f"❌ ЗНАЧЕНИЕ БЫЛО ПЕРЕЗАПИСАНО! Ожидалось: '{result_str}', Получено: '{actual}'")
            self.log("📌 Ищите другой код, который меняет result_dir_var")
            # Принудительная установка через Entry (запасной механизм)
            if self.result_entry is not None:
                try:
                    self.result_entry.delete(0, tk.END)
                    self.result_entry.insert(0, result_str)
                    self.result_dir_var.set(result_str)
                    self.log(f"🔧 РК установлен принудительно через Entry: '{self.result_dir_var.get()}'")
                except Exception as e:
                    self.log(f"Ошибка принудительной установки РК: {e}", 'error')
        
        return result_path
    
    def _ensure_result_path(self, source_dir: Path, result_dir: Path) -> Path:
        """
        Возвращает result_dir без изменений.
        (Логика добавления подкаталога перенесена в _auto_fill_result_dir)
        """
        return result_dir
    
    def _check_full_structure(self, source_dir: Path, result_dir: Path) -> bool:
        """Проверка наличия полного набора файлов в каталоге результатов"""
        if not source_dir.exists() or not result_dir.exists():
            return False
        
        # Собираем все файлы из исходного каталога (кроме .plp)
        source_files = set()
        for file_path in source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() != '.plp':
                rel_path = file_path.relative_to(source_dir)
                source_files.add(rel_path)
        
        # Проверяем наличие каждого файла в каталоге результатов
        for rel_path in source_files:
            result_file = result_dir / rel_path
            if not result_file.exists():
                return False
        
        return len(source_files) > 0
    
    def _copy_directory_structure(self, source_dir: Path, result_dir: Path) -> int:
        """
        Копирование недостающих подкаталогов и всех файлов (кроме .plp) из source_dir в result_dir.
        Возвращает количество скопированных файлов.
        Создаёт недостающие подкаталоги и копирует недостающие файлы.
        """
        files_copied = 0
        dirs_created = 0
        
        # Создаем все подкаталоги из исходного каталога (если их нет в результате)
        for dir_path in source_dir.rglob('*'):
            if dir_path.is_dir():
                target_dir = result_dir / dir_path.relative_to(source_dir)
                if not target_dir.exists():
                    target_dir.mkdir(parents=True, exist_ok=True)
                    dirs_created += 1
                    self.root.after(0, lambda d=target_dir.name: self.log(f"  Создан подкаталог: {d}", 'info'))
                else:
                    self.root.after(0, lambda d=target_dir.name: self.log(f"  Подкаталог существует: {d}", 'debug'))
        
        # Копируем все файлы (кроме .plp), если их нет в результате
        for file_path in source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() != '.plp':
                target_file = result_dir / file_path.relative_to(source_dir)
                if not target_file.exists():
                    try:
                        # Гарантируем, что родительский каталог существует
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, target_file)
                        files_copied += 1
                        self.root.after(0, lambda f=file_path.name: self.log(f"  Скопирован файл: {f}", 'info'))
                    except Exception as e:
                        self.root.after(0, lambda f=file_path.name, err=e: self.log(f"  Ошибка копирования {f}: {err}", 'error'))
                else:
                    self.root.after(0, lambda f=file_path.name: self.log(f"  Файл существует, пропущен: {f}", 'debug'))
        
        self.root.after(0, lambda: self.log(f"  Создано подкаталогов: {dirs_created}, скопировано файлов: {files_copied}", 'info'))
        return files_copied
    
    def _update_buttons_state(self):
        """Обновление доступности кнопок в зависимости от параметров"""
        source_dir = self.source_dir_var.get()
        result_dir = self.result_dir_var.get()
        file_pattern = self.file_pattern_var.get()
        
        # Проверка: выбран ли хотя бы один файл в рубрикаторе
        any_rule_selected = any(var.get() for var in self.selected_rules.values())
        
        # Кнопки доступны только если:
        # 1. Указан исходный каталог
        # 2. Указан каталог результатов (для исправления)
        # 3. Выбран хотя бы один файл в рубрикаторе
        
        # DS_087 §2.3: кнопки 1/2/3 («Сканировать»/«Исправить код»/«В Ai»)
        # управляются единой логикой активации workflow — ровно одна активна
        # и жирная. Старшие условия (источник/результат/рубрикатор) входят в
        # cond_scan; см. _update_workflow_buttons().
        self._update_workflow_buttons()
    
        # Кнопка "Показать SQL для ручного исправления" - активна после сканирования
        show_sql_enabled = self.scan_results is not None
        self.btn_show_sql.state(['!disabled' if show_sql_enabled else 'disabled'])

        # Кнопки Koda - активны после сканирования
        self.btn_send_koda.state(['!disabled' if show_sql_enabled else 'disabled'])
        self.btn_receive_koda.state(['!disabled' if show_sql_enabled else 'disabled'])

        # DS 054: «В AI» активна после сканирования (есть проблемы для запроса).
        # DS_054_Уточнение_C: «От AI» — по наличию файлов-ответов в AI_OUT
        # (не включаем безусловно; обновление — _update_ai_button_state).
        # DS_087 §2.3: state btn_to_ai («3. В Ai») больше НЕ ставится здесь —
        # им управляет _update_workflow_buttons (ровно одна активна из 1/2/3).
        self._update_ai_button_state()
    
# Кнопка "Архивировать" - активируется при установленном флаге "Сохранить структуру"
        archive_enabled = False
        if (bool(result_dir) and
            self.preserve_structure_var.get()):
            # Проверяем полный набор файлов
            if source_dir and result_dir:
                source_path = Path(source_dir)
                result_path = Path(result_dir)
                if self._check_full_structure(source_path, result_path):
                    archive_enabled = True
        
        self._update_archive_state()
    
    def _on_source_focus_out(self, event):
        """Обработка потери фокуса поля исходного каталога"""
        value = self.source_dir_var.get()
        if value:
            self.log(f"Исходный каталог: {value}", 'info')
        else:
            self.log("Исходный каталог очищен", 'info')
    
    def _on_result_focus_out(self, event):
        """Обработка потери фокуса поля каталога результатов"""
        value = self.result_dir_var.get()
        if value:
            self.log(f"Каталог результатов: {value}", 'info')
        else:
            self.log("Каталог результатов очищен", 'info')
    
    def validate_directories(self):
        """Проверка существования и доступности ИК и РК"""
        source_dir = self.source_dir_var.get().strip()
        result_dir = self.result_dir_var.get().strip()
        
        errors = []
        warnings = []
        
        # Проверка ИК
        if not source_dir:
            errors.append("Исходный каталог не указан")
        elif not os.path.exists(source_dir):
            errors.append(f"Исходный каталог не существует: {source_dir}")
        elif not os.access(source_dir, os.R_OK):
            errors.append(f"Нет доступа на чтение к ИК: {source_dir}")
        
        # Проверка РК
        if result_dir:
            if not os.path.exists(result_dir):
                warnings.append(f"РК не существует, будет создан: {result_dir}")
            elif not os.access(result_dir, os.W_OK):
                errors.append(f"Нет доступа на запись в РК: {result_dir}")
        else:
            warnings.append("РК не указан, будет использован ИК")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def update_field_colors(self):
        """Обновление цвета полей ввода на основе валидации
        
        Поля - ttk.Entry, поэтому цвет задаётся через ttk.Style (fieldbackground).
        """
        try:
            validation = self.validate_directories()
            errors = validation["errors"]
            
            # ИК
            source_dir = self.source_dir_var.get().strip()
            if source_dir and os.path.exists(source_dir) and os.access(source_dir, os.R_OK):
                self.source_entry.configure(style='Valid.TEntry')      # зелёный
            elif any('Исходный' in e for e in errors):
                self.source_entry.configure(style='Invalid.TEntry')    # красный
            else:
                self.source_entry.configure(style='Warning.TEntry')    # жёлтый
            
            # РК
            result_dir = self.result_dir_var.get().strip()
            if result_dir and os.path.exists(result_dir):
                if os.access(result_dir, os.W_OK):
                    self.result_entry.configure(style='Valid.TEntry')    # зелёный
                else:
                    self.result_entry.configure(style='Invalid.TEntry')  # красный (нет доступа)
            elif result_dir:
                self.result_entry.configure(style='Warning.TEntry')      # жёлтый (будет создан)
            else:
                self.result_entry.configure(style='Invalid.TEntry')      # красный (не указан)
        except Exception:
            pass  # Индикация не должна ломать работу АРМа
    
    def update_status_indicators(self):
        """Обновление индикаторов статуса каталогов (DS 009)"""
        def get_status_text(path, is_source=True):
            if not path:
                return "⚠️ не указан", "#b8860b"  # жёлтый (тёмный для читаемости на светлом фоне)
            
            if is_source:
                if not os.path.exists(path):
                    return "❌ не существует", "#dc3545"  # красный
                elif not os.access(path, os.R_OK):
                    return "🔒 нет доступа", "#dc3545"  # красный
                else:
                    return "✅ доступен", "#28a745"  # зелёный
            else:
                if not os.path.exists(path):
                    return "📁 будет создан", "#b8860b"  # жёлтый
                elif not os.access(path, os.W_OK):
                    return "🔒 нет доступа", "#dc3545"  # красный
                else:
                    return "✅ доступен", "#28a745"  # зелёный
        
        try:
            # Обновление ИК
            source_dir = self.source_dir_var.get().strip()
            text, color = get_status_text(source_dir, True)
            self.source_status_label.config(text=text, foreground=color)
            
            # Обновление РК
            result_dir = self.result_dir_var.get().strip()
            if not result_dir:
                result_dir = source_dir  # если РК не указан, используем ИК
            text, color = get_status_text(result_dir, False)
            self.result_status_label.config(text=text, foreground=color)
        except Exception:
            pass  # Индикация не должна ломать работу АРМа
    
    def log_result_dir_change(self, source_dir, result_dir, action="auto_update"):
        """Логирование изменения РК в result_dir_history.json (DS 010)"""
        history_file = Path(__file__).parent.parent / 'EXCHANGE' / 'result_dir_history.json'
        
        try:
            # Загрузка существующей истории
            history = {"history": []}
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Добавление записи
            history["history"].append({
                "timestamp": datetime.now().isoformat(timespec='seconds'),
                "source_dir": source_dir,
                "result_dir": result_dir,
                "action": action,
                "user": os.getenv("USERNAME", "unknown")
            })
            
            # Ограничение истории (последние 100 записей)
            if len(history["history"]) > 100:
                history["history"] = history["history"][-100:]
            
            # Сохранение
            history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            self.log(f"📝 Изменение РК зафиксировано: {result_dir}")
        except Exception as e:
            self.log(f"Ошибка записи истории РК: {e}", 'error')
    
    def show_result_dir_history(self):
        """Показать историю изменений РК (DS 010)"""
        history_file = Path(__file__).parent.parent / 'EXCHANGE' / 'result_dir_history.json'
        
        if not history_file.exists():
            self.log("📭 История РК пуста")
            return
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception as e:
            self.log(f"Ошибка чтения истории РК: {e}", 'error')
            return
        
        if not history.get("history"):
            self.log("📭 История РК пуста")
            return
        
        self.log("=" * 60)
        self.log("📋 ИСТОРИЯ ИЗМЕНЕНИЙ РК")
        self.log("=" * 60)
        
        for i, entry in enumerate(history["history"][-10:], 1):
            self.log(f"{i}. [{entry['timestamp']}]")
            self.log(f"   ИК: {entry['source_dir']}")
            self.log(f"   РК: {entry['result_dir']}")
            self.log(f"   Действие: {entry['action']}")
            self.log(f"   Пользователь: {entry['user']}")
    
    def _update_dir_indicators(self):
        """Единая точка обновления визуальной индикации каталогов (цвет полей + метки статуса)"""
        self.update_field_colors()
        if hasattr(self, 'update_status_indicators'):
            self.update_status_indicators()
        # DS 54 §2: статусы кнопок пересчитываются и при смене индикации
        self._update_workflow_buttons()
    
    def _load_rules(self) -> dict:
        """Загрузка списка правил из рубрикатора"""
        rules = {}
        try:
            rubricator_path = self.rubricator_dir / '3.RUBRICATOR_FIXES v5.md'
            if rubricator_path.exists():
                with open(rubricator_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if '|' in line and not line.startswith('|---') and not line.startswith('|N'):
                            parts = [p.strip() for p in line.split('|')]
                            # Формат v5: |N |++|Код |Пункт |Priority |Теги |Описание
                            # parts: ['', '1', '++', 'v50.SQL.OUTERJOIN.п.1.1', 'п.1.1', 'HIGH', 'tags', 'desc']
                            if len(parts) >= 8:
                                code = parts[3]
                                desc = parts[7]
                                if code and (code.startswith('v') or code.startswith('PlpCheck') or code.startswith('тдс') or code.startswith('тклоик')):
                                    rules[code] = desc
                            elif len(parts) >= 2:
                                code = parts[1]
                                desc = parts[4] if len(parts) > 4 else ''
                                if code and code.startswith('v'):
                                    rules[code] = desc
        except Exception as e:
            print(f"Ошибка загрузки правил: {e}")
        
        if not rules:
            rules = {
                'v50': 'Рекомендации по адаптации кода на PLPlus для DBI',
                'тдс20240828': 'Правила для проекта ТДС',
                'тклоик20240828': 'Правила для проекта ТЦ ЛОИК',
                'PlpCheck': 'Правила PlpCheck (стиль кода)'
            }
        
        return rules
    
    def _get_rules_for_selected_files(self, selected_files=None):
        """Получить список правил для выбранных файлов рубрикатора (DS 019/DS 020).
        
        Маппинг код файла -> префиксы правил:
        - v53/v50 -> v53.* или v50.*
        - PlpCheck -> plpcheck.*
        - тдс20240828 -> тдс20240828.*
        - тклоик20240828 -> тклоик20240828.*
        
        Args:
            selected_files: список кодов файлов. Если None - берётся из selected_rules.
        """
        if selected_files is None:
            selected_files = [code for code, var in self.selected_rules.items() if var.get()]
        
        if not self.rubricator_prompts or not self.rubricator_prompts.loaded:
            return selected_files  # fallback: возвращаем коды файлов
        
        all_rules = self.rubricator_prompts.get_all_rules()
        matched_rules = []
        
        # Префикс(ы) правил для каждого кода файла рубрикатора (DS 019)
        file_prefixes = {
            'v53': ('v53.', 'v50.'),   # актуальный код файла рубрикатора
            'v50': ('v53.', 'v50.'),   # старый код (совместимость)
            'PlpCheck': ('plpcheck.',),
            'тдс20240828': ('тдс20240828.',),
            'тклоик20240828': ('тклоик20240828.',),
        }
        
        for file_code in selected_files:
            prefixes = file_prefixes.get(file_code)
            if prefixes:
                for rule in all_rules:
                    if rule['code'].startswith(prefixes):
                        matched_rules.append(rule['code'])
            else:
                # fallback: ищем правила, содержащие код файла
                for rule in all_rules:
                    if file_code in rule['code']:
                        matched_rules.append(rule['code'])
        
        return sorted(set(matched_rules))
    
    def browse_source(self):
        """Выбор исходного каталога"""
        directory = filedialog.askdirectory()
        if directory:
            # Нормализуем путь к Windows-формату
            directory = directory.replace('/', '\\')
            self.source_dir_var.set(directory)
            # Сброс индикатора
            self._reset_progress()
            # Логирование только при потере фокуса, здесь - мгновенно
            self.log(f"Исходный каталог: {directory}", 'info')
            # Автоматическое формирование каталога результатов
            self._auto_fill_result_dir(directory)
            # Обновляем доступность кнопок
            self._update_buttons_state()
    
    def browse_result(self):
        """Выбор каталога результатов"""
        directory = filedialog.askdirectory()
        if directory:
            # Нормализуем путь к Windows-формату
            directory = directory.replace('/', '\\')
            old_result = self.result_dir_var.get()
            self.result_dir_var.set(directory)
            # Сброс индикатора
            self._reset_progress()
            # Логирование только при потере фокуса, здесь - мгновенно
            self.log(f"Каталог результатов: {directory}", 'info')
            # DS 010: логирование ручного изменения РК
            if directory != old_result:
                self.log_result_dir_change(self.source_dir_var.get(), directory, action="manual")
            # Обновляем доступность кнопок
            self._update_buttons_state()
    
    def log(self, message: str, level: str = 'info'):
        """Добавление сообщения в журнал и дублирование в logs_Deep"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Вывод в GUI
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", level)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # Дублирование в файл logs_Deep
        if not self.current_log_file:
            log_filename = f"gui_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            self.current_log_file = self.logs_deep_dir / log_filename
        
        try:
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(formatted_message)
        except Exception:
            pass  # Игнорируем ошибки записи в файл
    
    def _reset_progress(self):
        """Сброс индикатора выполнения"""
        self.progress.config(value=0)
        self.progress_label.config(text="0%")
        self.root.update_idletasks()
        
    def log_with_tags(self, parts: List[Tuple[str, str]]):
        """Добавление сообщения с разными тегами для разных частей
        
        parts: список кортежей (текст, тег)
        Например: [("Исправление в Строке 17 <<< ", "highlight"), ("DateTimeEnd date_time;", "info")]
        """
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] "
        self.log_text.insert(tk.END, timestamp, 'info')
        for text, tag in parts:
            self.log_text.insert(tk.END, text, tag)
        self.log_text.insert(tk.END, "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def _log_report_saved(self, report_path, fmt: str):
        """DS 030: сообщение о сохранении отчёта + отдельная кликабельная ссылка
        с полным путём к файлу. Клик открывает файл (HTML в браузере и т.д.).
        
        Используется для всех отчётов: Отчёт (HTML/MD), Методичка, DeepScan.
        """
        self.log(f"Отчёт сохранён ({fmt}):", 'success')
        self.log_with_tags([
            (str(report_path), 'report_link'),
            ("  (клик — открыть)", 'debug'),
        ])
    
    def _open_report_link(self, event=None):
        """DS 030: клик по ссылке отчёта в журнале — открыть файл под курсором."""
        try:
            idx = self.log_text.index(tk.CURRENT)
        except Exception:
            return
        self._open_link_at(idx)
    
    def _open_link_at(self, idx) -> bool:
        """DS 030: извлечь полный путь ссылки тега report_link по индексу журнала
        и открыть файл. Возвращает True, если файл открыт."""
        if 'report_link' not in self.log_text.tag_names(idx):
            return False
        # Расширяем диапазон тега report_link, содержащий индекс:
        # nextrange от idx даёт конец диапазона (если idx внутри — начало == idx),
        # prevrange от конца даёт начало диапазона, оканчивающегося не позже конца.
        nextrange = self.log_text.tag_nextrange('report_link', idx)
        if not nextrange:
            return False
        end_idx = nextrange[1]
        prevrange = self.log_text.tag_prevrange('report_link', end_idx)
        if not prevrange:
            return False
        path = self.log_text.get(prevrange[0], end_idx).strip()
        if not path:
            return False
        try:
            if not os.path.isfile(path):
                self.log(f"Файл отчёта не найден: {path}", 'error')
                return False
            os.startfile(path)  # Windows: открытие ассоциированным приложением
            return True
        except Exception as e:
            self.log(f"Не удалось открыть отчёт: {e}", 'error')
            return False
        
    def _log_separator(self, title: str = None):
        """Вывод разделителя в журнал"""
        separator = "=" * 80
        if title:
            self.log(separator, 'info')
            self.log(title, 'info')
            self.log(separator, 'info')
        else:
            self.log(separator, 'info')
        
    def clear_log(self):
        """Очистка журнала"""
        # Сброс индикатора
        self.progress.config(value=0)
        self.progress_label.config(text="0%")
        self.root.update_idletasks()
        
        self.log_text.delete('1.0', tk.END)
        self.log("Журнал очищен", 'info')
    
    def copy_log(self):
        """Копирование журнала в буфер"""
        # Сброс индикатора
        self.progress.config(value=0)
        self.progress_label.config(text="0%")
        self.root.update_idletasks()
        
        log_content = self.log_text.get('1.0', tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        self.log("Журнал скопирован в буфер обмена", 'info')
        messagebox.showinfo("Копирование", "Журнал скопирован в буфер обмена")
    
    def _current_fix_flags(self) -> dict:
        """DS_053_Уточнение_2: текущее состояние 6 флагов детерминированного
        фикса в каноническом порядке. Используется для передачи в сканер
        (заголовок отчётов) и фиксер. Если чекбоксы ещё не созданы — дефолт."""
        defaults = {'regex': True, 'hybrid': True, 'ai_fallback': False,
                    'ignore': False, 'backup': False, 'other': False}
        vars_ = getattr(self, 'var_fix_flags', None)
        if not vars_:
            return defaults
        return {name: bool(var.get()) for name, var in vars_.items()}

    def _current_header_flags(self) -> dict:
        """DS_080 §0: 6 флагов замены + only_ai — для заголовков логов.

        only_ai вне FLAG_ORDER: не участвует в подписи VVxVVx имени файла и в
        корзинах правил, поэтому добавляется только сюда (settings.json и
        AI_REQUEST остаются без изменений).
        """
        flags = dict(self._current_fix_flags())
        try:
            flags['only_ai'] = bool(self.ai_only_var.get())
        except Exception:
            flags['only_ai'] = True
        return flags

    def _append_only_ai_flag_line(self, report_path) -> None:
        """DS_080 §0: строка only_ai в блоке «Флаги замены» уже записанного .md.

        Шаблон блока формируется в analyzer/scanner.py (§4 DS_080 — не менять),
        поэтому строка дописывается post-factum к файлу. Идемпотентно: при
        знакомом only_ai файл не трогается.
        """
        try:
            inject_only_ai_flag(report_path, self._current_header_flags())
        except Exception as e:
            self.log(f"  [!] only_ai не добавлен в заголовок: {e}", 'warning')

    def _autosave_fix_flags(self):
        """DS_053_Уточнение_2 (задача C): автосохранение состояния 6 флагов в
        settings.json (read-modify-write только ключа 'fix_flags'). Не писать
        во время загрузки настроек и до инициализации чекбоксов."""
        if getattr(self, '_loading_settings', False):
            return
        if not getattr(self, 'var_fix_flags', None):
            return
        try:
            settings_path = Path(__file__).parent / 'settings.json'
            settings = {}
            if settings_path.exists():
                try:
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                except Exception:
                    settings = {}
            settings['fix_flags'] = self._current_fix_flags()
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Не удалось автосохранить флаги DS_053: {e}")

    # ── DS_088a_fix §2.4/§2.5: пороги confidence ─────────────────────────
    def _confidence_thresholds(self) -> tuple:
        """Пороги confidence (low, high): из полей формы, иначе из settings.json.

        DS_088a_fix §2.4: используется в receive_from_ai для проброса в
        ai_exchange.process_all_responses(conf_low=..., conf_high=...).
        """
        low, high = 0.5, 0.8
        try:
            s = self._read_settings_json()
            low = float(s.get('conf_low', low))
            high = float(s.get('conf_high', high))
        except Exception:
            pass
        try:
            if getattr(self, 'conf_low_var', None):
                low = float(self.conf_low_var.get().replace(',', '.'))
            if getattr(self, 'conf_high_var', None):
                high = float(self.conf_high_var.get().replace(',', '.'))
        except Exception:
            pass
        return low, high

    def _autosave_confidence(self):
        """DS_088a_fix §2.5: сохранение conf_low/conf_high в settings.json
        (read-modify-write, как UI-флаги DS_086)."""
        try:
            settings = self._read_settings_json()
            settings['conf_low'] = self._conf_low_prev
            settings['conf_high'] = self._conf_high_prev
            self._write_settings_json(settings)
        except Exception as e:
            print(f"Не удалось автосохранить пороги confidence: {e}")

    def _on_confidence_change(self):
        """DS_088a_fix §2.5: контроль диапазона 0.0..1.0 + запись в ЖВ.

        При неверном вводе — сообщение в ЖВ и возврат к предыдущему значению.
        """
        if getattr(self, '_loading_settings', False):
            return
        if not getattr(self, 'conf_low_var', None):
            return
        try:
            low = float(self.conf_low_var.get().replace(',', '.'))
            high = float(self.conf_high_var.get().replace(',', '.'))
        except (ValueError, TypeError):
            self.log("Пороги confidence: введите число (0.0–1.0) — откат", 'warning')
            self.conf_low_var.set(str(self._conf_low_prev))
            self.conf_high_var.set(str(self._conf_high_prev))
            return
        if not (0.0 <= low <= 1.0) or not (0.0 <= high <= 1.0):
            self.log("Пороги confidence вне диапазона 0.0–1.0 — откат", 'warning')
            self.conf_low_var.set(str(self._conf_low_prev))
            self.conf_high_var.set(str(self._conf_high_prev))
            return
        if low == self._conf_low_prev and high == self._conf_high_prev:
            return
        self._conf_low_prev = low
        self._conf_high_prev = high
        self.log(f"Пороги confidence изменены: low={low}, high={high}", 'info')
        self._autosave_confidence()

    def load_settings(self):
        """Загрузка настроек из файла"""
        # DS_053_Уточнение_2 (задача C): блокируем автосохранение на время
        # восстановления флагов (var.set() вызвал бы trace_add → запись).
        self._loading_settings = True
        settings_path = Path(__file__).parent / 'settings.json'
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.source_dir_var.set(settings.get('source_dir', ''))
                    self.result_dir_var.set(settings.get('result_dir', ''))
                    self.file_pattern_var.set(settings.get('file_pattern', '**/*.plp'))
                    self.log_level_var.set(settings.get('log_level', 'Минимальный'))
                    # DS_075 §3.2: порог вывода топ-файлов.
                    self.report_stats_min_files_var.set(str(settings.get('report_stats_min_files', 10)))
                    self.scan_recursive_var.set(settings.get('recursive', True))
                    self.only_modified_var.set(settings.get('only_modified', True))
                    self.preserve_structure_var.set(settings.get('preserve_structure', True))
                    self.clean_output_var.set(settings.get('clean_output', False))
                    # DS_088a_fix §2.5: пороги confidence из settings.json.
                    if getattr(self, 'conf_low_var', None):
                        _cl = float(settings.get('conf_low', 0.5))
                        _ch = float(settings.get('conf_high', 0.8))
                        self._conf_low_prev = _cl
                        self._conf_high_prev = _ch
                        self.conf_low_var.set(str(_cl))
                        self.conf_high_var.set(str(_ch))
                    
                    # DS_058+DS_057: состояние чекбоксов рубрикатора хранится в
                    # settings.json -> rubricator_selected_rules (инициализируется
                    # в _populate_rules_tree / _init_rubricator_rule_states)
                    self._saved_rules = []
                        
                    # Загрузка настройки максимального размера логов
                    global MAX_LOG_SIZE_MB
                    max_log_size = settings.get('max_log_size_mb', 2)
                    if max_log_size:
                        MAX_LOG_SIZE_MB = max_log_size
                    
                    # Загрузка сохранённых приоритетов (DS 018: HIGH/MEDIUM/LOW)
                    saved_priorities = settings.get('selected_priorities', [])
                    self._selected_priorities = [p for p in saved_priorities if p in ('HIGH', 'MEDIUM', 'LOW')]
                    if hasattr(self, 'priority_high_var'):
                        self.priority_high_var.set('HIGH' in self._selected_priorities)
                        self.priority_medium_var.set('MEDIUM' in self._selected_priorities)
                        self.priority_low_var.set('LOW' in self._selected_priorities)
                        self._on_priority_filter_change()
                    if self._selected_priorities:
                        self.log(f"Восстановлены приоритеты: {', '.join(self._selected_priorities)}", 'info')
                    
                    # DS 036: восстановление состояния категорий PlpCheck
                    if hasattr(self, 'var_plpcheck_categories'):
                        saved_categories = settings.get('plpcheck_categories', None)
                        if saved_categories is None:
                            # Первый запуск — все категории включены
                            saved_categories = [code for code, _, _ in PLPCHECK_CATEGORIES]
                        for code, var in self.var_plpcheck_categories.items():
                            var.set(code in saved_categories)
                        # Синхронизация UI
                        self.var_plpcheck_all.set(all(var.get() for var in self.var_plpcheck_categories.values()))
                        self._on_plpcheck_toggle()
                        self.log(f"Восстановлены категории PlpCheck: {', '.join(saved_categories)}", 'info')

                    # DS_053_Уточнение_2 (задача C): восстановление 6 флагов
                    # детерминированного фикса. Если ключа нет — первый
                    # запуск: остаются дефолты чекбоксов (regex+hybrid).
                    if getattr(self, 'var_fix_flags', None):
                        saved_flags = settings.get('fix_flags', None)
                        if saved_flags is not None:
                            for name, var in self.var_fix_flags.items():
                                var.set(bool(saved_flags.get(name, var.get())))
                            self.log(
                                "Восстановлены флаги DS_053: " +
                                ', '.join(f"{n}={'V' if v.get() else 'x'}"
                                          for n, v in self.var_fix_flags.items()), 'info')
                    
                    # DS_086: восстановление скрытых элементов GUI (меню «Вид»).
                    # Ключа нет — первый запуск: действует UI_HIDE_DEFAULT.
                    if getattr(self, 'ui_visible_vars', None):
                        self._restore_ui_visibility(
                            settings.get('ui_hidden_elements', None))
                        
                self.log("Настройки загружены", 'info')
                
                # Автоматическое формирование каталога результатов из исходного (без логирования)
                if self.source_dir_var.get():
                    source_path = Path(self.source_dir_var.get())
                    self._auto_fill_result_dir(source_path)
                
                # Обновить состояние кнопок после загрузки настроек
                self._update_buttons_state()
            except Exception as e:
                self.log(f"Ошибка загрузки настроек: {e}", 'error')
        else:
            self.log("Настройки не найдены. Используются значения по умолчанию", 'info')
            self._saved_rules = []
            # Обновить состояние кнопок
            self._update_buttons_state()
        # DS_053_Уточнение_2 (задача C): разблокировать автосохранение флагов.
        self._loading_settings = False
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        settings_path = Path(__file__).parent / 'settings.json'
        
        settings = {
            'source_dir': self.source_dir_var.get(),
            'result_dir': self.result_dir_var.get(),
            'file_pattern': self.file_pattern_var.get(),
            'log_level': self.log_level_var.get(),
            'report_stats_min_files': int(self.report_stats_min_files_var.get() or 10),
            'recursive': self.scan_recursive_var.get(),
            'only_modified': self.only_modified_var.get(),
            'preserve_structure': self.preserve_structure_var.get(),
            'clean_output': self.clean_output_var.get(),
            'max_log_size_mb': MAX_LOG_SIZE_MB,
            'selected_priorities': list(getattr(self, '_selected_priorities', []))
        }
        # DS_088a_fix §2.5: пороги confidence (иначе save_settings стёр бы ключи,
        # записанные _autosave_confidence).
        try:
            settings['conf_low'] = float(getattr(self, '_conf_low_prev', 0.5))
            settings['conf_high'] = float(getattr(self, '_conf_high_prev', 0.8))
        except Exception:
            settings['conf_low'] = 0.5
            settings['conf_high'] = 0.8
        # DS_058+DS_057: состояние чекбоксов рубрикатора — в settings.json
        if self._rubricator_rule_vars:
            settings['rubricator_selected_rules'] = {
                rc: bool(var.get()) for rc, var in self._rubricator_rule_vars.items()
            }
        # DS 036: сохранение выбранных категорий PlpCheck
        if hasattr(self, 'var_plpcheck_categories'):
            settings['plpcheck_categories'] = [
                code for code, var in self.var_plpcheck_categories.items() if var.get()
            ]
        # DS_053_Уточнение_2 (задача C): сохранение 6 флагов детерминированного фикса
        if getattr(self, 'var_fix_flags', None):
            settings['fix_flags'] = self._current_fix_flags()
        # DS_086: сохранение скрытых элементов GUI (меню «Вид»). Ключ нужен и
        # здесь: save_settings пишет файл целиком и иначе стёр бы запись,
        # сделанную _autosave_ui_visibility.
        settings['ui_hidden_elements'] = self._hidden_ui_keys()
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.log("Настройки сохранены", 'success')
        except Exception as e:
            self.log(f"Ошибка сохранения настроек: {e}", 'error')
        
        # DS_058+DS_057: сохраняем состояние чекбоксов рубрикатора
        # в settings.json (1.RUBRICATOR_FILES v5.md больше не изменяется)
        self._save_rubricator_state()
    
    def _save_rubricator_state(self):
        """DS_058+DS_057: сохранение состояния чекбоксов рубрикатора в
        settings.json -> rubricator_selected_rules (read-modify-write).
        Файл 1.RUBRICATOR_FILES v5.md не изменяется."""
        try:
            settings = self._read_settings_json()
            # Идемпотентно: актуальное состояние всех правил из GUI
            states = {rc: bool(var.get())
                      for rc, var in self._rubricator_rule_vars.items()}
            settings['rubricator_selected_rules'] = states
            self._write_settings_json(settings)
            self.log("Состояние рубрикатора сохранено в settings.json "
                     "(rubricator_selected_rules)", 'success')
        except Exception as e:
            self.log(f"Ошибка сохранения состояния рубрикатора: {e}", 'error')
    
    def show_project_structure(self):
        """Показ структуры проекта"""
        self._log_separator("СТРУКТУРА ПРОЕКТА")
        
        project_root = Path(__file__).parent.parent
        for item in project_root.rglob('*'):
            if not item.name.startswith('.') and item.is_file():
                rel_path = item.relative_to(project_root)
                self.log(f"  [ФАЙЛ] {rel_path}", 'info')
    
    def show_documentation(self):
        """Показ документации - открывает файл в Word"""
        self._log_separator("ДОКУМЕНТАЦИЯ")
        
        # Путь к основной документации
        docs_path = Path(__file__).parent / 'AI_DOCS'
        
        # Основная документация (по умолчанию — старая версия 26.2.005)
        doc_file_2005 = docs_path / 'АРМ Адаптация под DBI v26.2.005.docx'
        doc_file_2006 = docs_path / 'АРМ Адаптация под DBI v26.2.006.docx'
        
        # Ищем файл: сначала старую версию, потом новую
        doc_to_open = None
        if doc_file_2005.exists():
            doc_to_open = doc_file_2005
        elif doc_file_2006.exists():
            doc_to_open = doc_file_2006
        
        if doc_to_open:
            self.log(f"[ДОКУМЕНТ] {doc_to_open.name}", 'info')
            self.log(f"     Полный путь: {doc_to_open}", 'info')
            self.log(f"     Каталог хранения: {docs_path}", 'info')
            self.log("     Для ручного поиска: F:\\TO_DBI\\SRC\\AI_DOCS\\", 'info')
            
            # Открываем документ в Word через OLE
            try:
                import subprocess
                import os
                
                # Пробуем открыть через ShellExecute (Windows)
                import ctypes
                ctypes.windll.shell32.ShellExecuteW(
                    None, 'open', str(doc_to_open), None, None, 1
                )
                self.log(f"     [SUCCESS] Документ открыт в Microsoft Word", 'success')
            except Exception as e:
                self.log(f"     [!] Не удалось открыть в Word: {e}", 'warning')
                self.log(f"     [INFO] Откройте файл вручную: {doc_to_open}", 'info')
        else:
            self.log("  [!] Документация не найдена", 'warning')
            self.log(f"     Каталог: {docs_path}", 'debug')
    
    def set_status(self, message: str):
        """Установка сообщения в подвале"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def show_about(self):
        """Показ информации о программе"""
        # Обновляем версию только если были изменения (новая дата)
        _now = datetime.now()
        _year_short = str(_now.year)[-2:]
        _quarter = (_now.month - 1) // 3 + 1
        _quarter_start = datetime(_now.year, (_quarter - 1) * 3 + 1, 1)
        _release = (_now - _quarter_start).days + 1
        
        current_version = f"v{_year_short}.{_quarter}.{_release:03d}"
        current_quarter = ["1-й квартал (янв-мар)", "2-й квартал (апр-июн)", "3-й квартал (июл-сен)", "4-й квартал (окт-дек)"][_quarter - 1]
        current_release = f"{_release:03d}"
        
        if current_version != APP_VERSION:
            self.log(f"Версия АРМ обновлена: {current_version}", 'info')
        
        messagebox.showinfo(
            "О программе",
            f"АРМ 'Адаптация под DBI' {current_version}\n\n"
            "Автоматизированное рабочее место для миграции\n"
            "PLPlus-кода с Oracle на PostgreSQL (2MCA DBI).\n\n"
            "Разработчик: NLP-Core-Team\n"
            f"Дата: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"Версия: {current_quarter}, версия {current_release}"
        )
        self.log("Открыто окно 'О программе'", 'info')
    
    def load_rubricator_on_start(self):
        """Загрузка рубрикатора при запуске"""
        self.set_status("Загрузка рубрикатора...")
        self.log("Загрузка рубрикатора...", 'info')
        
        if not self.rubricator_dir.exists():
            self.log(f"[!] Каталог рубрикатора не найден: {self.rubricator_dir}", 'error')
            self.set_status("Готово")
            return
        
        try:
            # Вывод 1.RUBRICATOR_FILES v5.md
            file_path = self.rubricator_dir / '1.RUBRICATOR_FILES v5.md'
            if file_path.exists():
                self.log(f"# {file_path}", 'info')
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    for line in lines[:30]:
                        self.log(line, 'info')
                self.log("", 'info')
            
            # Вывод 2.RUBRICATOR_CATEGORIES.md
            file_path = self.rubricator_dir / '2.RUBRICATOR_CATEGORIES.md'
            if file_path.exists():
                self.log(f"# {file_path}", 'info')
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    for line in lines[:30]:
                        self.log(line, 'info')
                self.log("", 'info')
                    
            # Вывод 3.RUBRICATOR_FIXES v5.md
            file_path = self.rubricator_dir / '3.RUBRICATOR_FIXES v5.md'
            if file_path.exists():
                self.log(f"# {file_path}", 'info')
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    for line in lines[:50]:
                        self.log(line, 'info')
                self.log("", 'info')
                    
            self.rubricator_loaded = True
            self.log("Рубрикатор загружен успешно", 'success')
                
        except Exception as e:
            self.log(f"[!] Ошибка загрузки рубрикатора: {e}", 'error')
        
        self.set_status("Готово")
    
    def start_scan(self):
        """Запуск сканирования"""
        # Проверка заполнения путей
        if not self.source_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите исходный каталог")
            return
        if not self.result_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите каталог результатов")
            return
        
        # Проверка существования исходного каталога
        source_dir = Path(self.source_dir_var.get())
        if not source_dir.exists():
            messagebox.showerror("Ошибка", f"Исходный каталог не найден:\n{source_dir}")
            return
        
        # Отключение кнопок на время сканирования
        self.btn_scan.state(['disabled'])
        self.btn_fix.state(['disabled'])
        self.btn_test_gen.state(['disabled'])
        
        # Сброс флага и запуск в отдельном потоке
        self.scanning = True
        self._stop_event.clear()
        thread = threading.Thread(target=self._run_scan, args=(False,), daemon=True)
        thread.start()
    
    def _run_scan(self, deep_mode=False):
        """Рабочая функция сканирования (вызывается в отдельном потоке)
        
        Args:
            deep_mode: Если True - использовать углублённое сканирование
        """
        # DS_088b §2.2: замер длительности для звука завершения.
        _op_start = time.time()
        # DS_089a §2.7: сохранение начала операции для прогноза времени.
        self._op_start_time = _op_start
        self._op_files_done = 0
        self._op_total_files = 0
        try:
            # Сброс индикатора (DS 041: через _progress_update — уважает заморозку)
            self._progress_update(0)
            # DS 040: сброс процента прерывания (новое сканирование)
            # DS 041: переустановка стиля убрана из потока — выполнялась через
            # root.after и могла ПЕРЕКРЫТЬ жёлтый стиль, установленный в
            # on_abort_click (гонка). Синхронный сброс стиля уже есть в
            # _start_abortable_operation (главный поток, до запуска потока).
            self.abort_percent = None
            
            # Если были изменения в правилах и рубрикатор не открывался
            if self.rules_changed:
                self.root.after(0, lambda: self.log_text.delete('1.0', tk.END))
                self.root.after(0, self.open_rubricator)
                self.rules_changed = False
            
            self.root.after(0, lambda: self.set_status("Сканирование..."))
            self.root.after(0, lambda: self._log_separator("НАЧАЛО СКАНИРОВАНИЯ"))
            
            # Логирование использования нового рубрикатора
            if self.rubricator_prompts and self.rubricator_prompts.loaded:
                self.root.after(0, lambda: self.log("\n[ИСПОЛЬЗУЕТСЯ] Расширенный рубрикатор 4.RUBRICATOR_PROMPT v5.json", 'highlight'))
                self.root.after(0, lambda: self.log(f"  Версия: {self.rubricator_prompts.data.get('version', 'N/A')}", 'debug'))
            else:
                self.root.after(0, lambda: self.log("\n[ИСПОЛЬЗУЕТСЯ] Старый рубрикатор 3.RUBRICATOR_FIXES v5.md", 'warning'))
            
            # Подготовка конфигурации
            config = {
                'paths': {
                    'source_dir': self.source_dir_var.get(),
                    'results_dir': self.result_dir_var.get(),
                    'logs_dir': str(Path(__file__).parent.parent / 'logs')
                },
                'scan': {
                    'recursive': self.scan_recursive_var.get(),
                    'file_pattern': self.file_pattern_var.get(),
                    'exclude_patterns': ['.bak', '.tmp']
                },
                'logging': {
                    'level': self.log_level_var.get()
                }
            }
            
            # Определение выбранных правил (DS 019/DS 020: только правила из выбранных файлов рубрикатора)
            selected_files = [code for code, var in self.selected_rules.items() if var.get()]
            
            # DS 020: фильтр PlpCheck применяется к ФАЙЛАМ до сбора правил
            if not self.plpcheck_enabled_var.get():
                selected_files = [r for r in selected_files if r != 'PlpCheck']
                self.root.after(0, lambda: self.log("\n[PlpCheck] Флаг выключен — правила стиля кода не применяются", 'info'))
            else:
                self.root.after(0, lambda: self.log("\n[PlpCheck] Флаг включён — применяются правила стиля кода", 'info'))
            
            # DS 036: фильтр категорий PlpCheck
            self.plpcheck_categories_filter = [
                code for code, var in self.var_plpcheck_categories.items() if var.get()
            ]
            self.root.after(0, lambda: self.log(
                f"[PlpCheck] Категории: {', '.join(self.plpcheck_categories_filter) or 'нет'}",
                'info'))
            
            selected_rules = self._get_rules_for_selected_files(selected_files)
            
            # DS 023: отладочный вывод в лог АРМ
            self.log(f"[DEBUG] selected_files: {selected_files}", 'info')
            self.log(f"[DEBUG] selected_rules (передано в сканер): {selected_rules[:20]}{' ...' if len(selected_rules) > 20 else ''} (всего {len(selected_rules)})", 'info')
            
            self.root.after(0, lambda: self.log("\nВЫБРАННЫЕ ФАЙЛЫ РУБРИКАТОРА:", 'highlight'))
            for f in selected_files:
                self.root.after(0, lambda ff=f: self.log(f"  [+] {ff}", 'highlight'))
            
            # Если выбраны приоритеты — используем правила из выбранных приоритетов (DS 018: HIGH/MEDIUM/LOW)
            # DS 024: защита от пустого результата — если после фильтра не осталось ни одного правила,
            # selected_rules НЕ обнуляется (иначе сканер загрузит ВСЕ правила)
            from rubricator_priority_mapping import PRIORITY_RULES
            priority_mapping = {'HIGH': 'Приоритет 1', 'MEDIUM': 'Приоритет 2', 'LOW': 'Приоритет 3'}
            selected_priorities = [priority_mapping.get(p, p) for p in getattr(self, '_selected_priorities', [])]
            
            if selected_priorities:
                # Собираем правила из выбранных приоритетов (DS 024)
                priority_rules = set()
                for prio in selected_priorities:
                    if prio in PRIORITY_RULES:
                        priority_rules.update(PRIORITY_RULES[prio])
                
                if priority_rules:
                    # DS 024: регистронезависимое сопоставление кодов
                    # PRIORITY_RULES использует 'PlpCheck.DBI.*.п.1', рубрикатор - 'plpcheck.ACCESS_STATIC'
                    pr_lower = {r.lower(): r for r in priority_rules}
                    filtered_rules = []
                    for r in selected_rules:
                        r_lower = r.lower()
                        # 1) точное совпадение (регистронезависимо)
                        if r_lower in pr_lower:
                            filtered_rules.append(r)
                            continue
                        # 2) частичное совпадение: код приоритета начинается с кода правила
                        #    (PlpCheck.DBI.OUTER_JOIN.п.1 vs plpcheck.DBI.OUTER_JOIN)
                        if any(pr.lower().startswith(r_lower) or r_lower.startswith(pr.lower()) for pr in priority_rules):
                            filtered_rules.append(r)
                    
                    if filtered_rules:
                        selected_rules = filtered_rules
                        self.root.after(0, lambda: self.log(f"\n[ПРИОРИТЕТ] Фильтрация по приоритетам: {', '.join(getattr(self, '_selected_priorities', []))}", 'highlight'))
                        self.root.after(0, lambda: self.log(f"  Всего правил из приоритетов: {len(priority_rules)}", 'info'))
                        self.root.after(0, lambda: self.log(f"  Используемых правил: {len(selected_rules)}", 'info'))
                    else:
                        # DS 024: НЕ обнуляем selected_rules — используем все правила выбранных файлов
                        self.root.after(0, lambda: self.log(f"\n⚠ Для выбранных файлов нет правил с приоритетами {', '.join(getattr(self, '_selected_priorities', []))}. Используются все правила выбранных файлов ({len(selected_rules)}).", 'warning'))
                else:
                    # DS 024: в PRIORITY_RULES нет правил — не трогаем selected_rules
                    self.root.after(0, lambda: self.log("\n⚠ Нет правил в PRIORITY_RULES. Используются все правила выбранных файлов.", 'warning'))
            
            self.root.after(0, lambda: self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА ({len(selected_rules)}):", 'info'))
            for rule in selected_rules[:30]:
                self.root.after(0, lambda r=rule: self.log(f"  [+] {r}", 'info'))
            if len(selected_rules) > 30:
                self.root.after(0, lambda: self.log(f"  ... и ещё {len(selected_rules) - 30} правил", 'info'))
            
            # Логирование использования промптов из нового рубрикатора
            if self.rubricator_prompts and self.rubricator_prompts.loaded:
                self.root.after(0, lambda: self.log("\nПРОМПТЫ ИЗ 4.RUBRICATOR_PROMPT v5.json:", 'highlight'))
                for rule in selected_rules:
                    new_rule = self.rubricator_prompts.get_rule(rule)
                    if new_rule:
                        search_prompt = new_rule.get('search_prompt', '')
                        fix_prompt = new_rule.get('fix_prompt', '')
                        self.root.after(0, lambda r=rule, sp=search_prompt[:100], fp=fix_prompt[:100]: self.log(
                            f"  Правило {r}:\n"
                            f"    search_prompt: {sp}...\n"
                            f"    fix_prompt: {fp}...", 'debug'
                        ))
                    else:
                        self.root.after(0, lambda r=rule: self.log(f"  Правило {r}: промпты недоступны (старый алгоритм)", 'warning'))
            
            # Загрузка рубрикатора если ещё не загружен
            if not self.rubricator_loaded:
                self.root.after(0, self.load_rubricator_on_start)
            
            # Сброс прогресса
            self._progress_update(0)
            
            # Создание сканера
            from analyzer.scanner import PLPlusScanner
            scanner = PLPlusScanner(config, selected_rules, self.rubricator_prompts,
                                    plpcheck_categories=getattr(self, 'plpcheck_categories_filter', []),
                                    abort_callback=self._abort_requested,  # DS 038
                                    stop_event=self._stop_event,            # DS_089b
                                    fix_flags=self._current_header_flags())  # DS_053_Уточнение_2 (задача A), DS_080 §0
            
            # Логирование вызова Парсера SQL
            self.root.after(0, lambda: self.log("\n[ПАРСЕР SQL] Начало сканирования и анализа...", 'highlight'))
            self.root.after(0, lambda: self.log(f"  Источник: {config['paths']['source_dir']}", 'debug'))
            self.root.after(0, lambda: self.log(f"  Правила: {len(selected_rules)}", 'debug'))
            
            self._progress_update(10)
            
            # Callback для вывода в журнал (вызывается в главном потоке)
            def scan_log(message, level='info'):
                self.root.after(0, lambda m=message, l=level: self.log(m, l))
                # DS 040: обновление индикатора из сообщений «Прогресс» сканера
                import re as _re
                m = _re.search(r'Прогресс: (\d+)/(\d+) \((\d+)%\)', message)
                if m:
                    pct = int(m.group(3))
                    self._progress_update(pct)
                    # DS_089a §2.7: сохранение прогресса для прогноза
                    self._op_files_done = int(m.group(1))
                    self._op_total_files = int(m.group(2))
            
            # Callback для вывода с разными тегами
            def scan_log_with_tags(parts):
                self.root.after(0, lambda p=parts: self.log_with_tags(p))
            
            # Сканирование
            scan_results = scanner.scan_directory(log_callback=scan_log)
            
            # DS_089b §2.3: resume скана — если есть состояние прерванного
            # скана, исключить из результатов issues с ранее обработанными
            # ключами (file_path, line_number, issue_type, description,
            # match_fragment) — тот же ключ, что дедуп в scanner.py.
            _ab = getattr(self, '_abort_state', None)
            _resumed_scan = False
            if _ab and _ab.get('operation') == 'scan':
                _prev_keys = {tuple(k) for k in _ab.get('processed_keys', [])}
                self._abort_state = None
                if _prev_keys:
                    _resumed_scan = True
                    _before = len(scanner.issues)
                    scanner.issues = self._ds089b_filter_processed(
                        scanner.issues, _prev_keys)
                    _removed = _before - len(scanner.issues)
                    _ts = time.strftime("%H:%M:%S")
                    _msg = (f"[{_ts}] Возобновление с {len(scanner.issues)} "
                            f"issues (пропущено {_removed})")
                    self.root.after(0, lambda m=_msg: self.log(m, 'info'))
                    self._bot_log(f"DS 089: {_msg}")
            
            # DS_089b §2.2: скан прерван — сохранить ключи обработанных
            # issues; следующий запуск («Сканировать») исключит их (resume).
            if self.scan_aborted:
                _keys = self._ds089b_processed_keys(scanner.issues)
                self._abort_state = {'operation': 'scan',
                                     'processed_keys': _keys}
                _ts = time.strftime("%H:%M:%S")
                _msg = (f"[{_ts}] Состояние сохранено: {len(_keys)} issues, "
                        f"0 файлов. Следующий скан исключит их (resume).")
                self.root.after(0, lambda m=_msg: self.log(m, 'warning'))
                self._bot_log(f"DS 089: {_msg}")
            
            # DS_089b §2.6: resume завершён успешно (не прерван повторно).
            if _resumed_scan and not self.scan_aborted:
                _ts = time.strftime("%H:%M:%S")
                _msg = f"[{_ts}] Операция возобновлена и завершена"
                self.root.after(0, lambda m=_msg: self.log(m, 'success'))
                self._bot_log(f"DS 089: {_msg}")
            
            # DS 040: сохранить процент прерывания из сканера (None если не прервано)
            self.abort_percent = getattr(scanner, 'abort_percent', None)
            
            # DS 040: при прерывании индикатор остаётся на проценте прерывания
            # (жёлтый стиль уже применён в on_abort_click), не перескакиваем на 50%
            # DS 041: force=True — явная установка авторитетного процента прерывания
            if self.abort_percent is not None:
                self._progress_update(self.abort_percent, force=True)
            else:
                self._progress_update(50)
            
            # Завершение работы Парсера SQL
            self.root.after(0, lambda: self.log(f"\n[ПАРСЕР SQL] Завершено:", 'highlight'))
            self.root.after(0, lambda: self.log(f"  Найдено файлов: {scan_results.get('files_scanned', 0)}", 'info'))
            self.root.after(0, lambda: self.log(f"  Найдено проблем: {scan_results.get('total_issues', 0)}", 'info'))
            
            # Генерация отчёта
            source_name = Path(self.source_dir_var.get()).name
            # DS_075 §3.2: порог вывода топ-файлов + уровень логирования.
            _log_level = self.log_level_var.get()
            try:
                _min_files = int(self.report_stats_min_files_var.get() or 10)
            except (ValueError, TypeError):
                _min_files = 10
            output_path = Path(config['paths']['logs_dir']) / f'scan_report_{source_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            scanner.generate_report(output_path, mode='scan', fixed_count=0,
                                    log_level=_log_level, report_stats_min_files=_min_files)
            # DS_080 §0: строка only_ai в «Флаги замены» заголовка scan_report_*.md.
            self._append_only_ai_flag_line(output_path)
            
            # DS 025: дополнительно HTML-отчёт в формате дистрибутивного PlpCheck
            html_report_path = Path(config['paths']['logs_dir']) / f'plpcheck_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            scanner.generate_report(html_report_path)
            
            # DS_053_Уточнение_4 (задача A): дополнительный лог scan_VVxVVx_*
            # при «Сканировать» — ПРОГНОЗ исправлений (симуляция конвейера
            # без записи: пары «> было / <КР> станет» по Схеме A). Без флагов —
            # пустой лог с пометкой «флаги не выбраны» (имя scan_xxxxxx_*).
            from fixer.code_fixer import save_scan_only_log
            _flags = self._current_header_flags()  # DS_080 §0
            _scan_log_path = save_scan_only_log(
                Path(config['paths']['logs_dir']), source_name, _flags,
                scanner, config, log_level=_log_level, report_stats_min_files=_min_files)
            
            self.root.after(0, lambda: self.log(f"\n[2/3] Результаты сканирования:", 'info'))
            self.root.after(0, lambda: self.log(f"  Найдено *.plp файлов: {scan_results.get('files_scanned', 0)}", 'info'))
            self.root.after(0, lambda: self.log(f"  Проблемных конструкций: {scan_results.get('total_issues', 0)}", 'info'))
            
            self.root.after(0, lambda: self.log(f"\n[3/3] Проблемы по типам:", 'info'))
            for issue_type, count in scan_results.get('by_type', {}).items():
                self.root.after(0, lambda t=issue_type, c=count: self.log(f"  {t}: {c}", 'info'))
            
            self.root.after(0, lambda: self.log(f"\nОтчёт сохранён: {output_path}", 'info'))
            # DS_053_Уточнение_3 (задача A): уведомление о доп. логе.
            if _scan_log_path:
                self.root.after(0, lambda p=_scan_log_path: self.log(f"Дополнительный лог сохранён: {p}", 'info'))
            
            # DS 042: различаем завершённое и прерванное сканирование.
            # ВАЖНО: scan_aborted ещё не сброшен (сброс — в finally через
            # _finish_abortable_operation), поэтому условие корректно.
            if self.scan_aborted:
                abort_pct = self.abort_percent or 0.0
                self.root.after(0, lambda p=abort_pct: self._log_separator(f"СКАНИРОВАНИЕ ПРЕРВАНО НА {p:.2f} %"))
            else:
                self.root.after(0, lambda: self._log_separator("СКАНИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО"))
            # DS 042: статус-бар различает завершение и прерывание
            # (scan_aborted ещё не сброшен — сброс в finally)
            if self.scan_aborted:
                self.root.after(0, lambda: self.set_status("Прервано"))
            else:
                self.root.after(0, lambda: self.set_status("Готово"))
            
# DS 040: при прерывании индикатор остаётся на проценте прерывания (не 100%)
            # DS 041: через _progress_update — force=True для авторитетного процента
            # DS 042: если прервано, но abort_percent не установился (клик после
            # последнего файла) — всё равно НЕ прорисовываем 100%
            if self.abort_percent is not None:
                self._progress_update(self.abort_percent, force=True)
            elif self.scan_aborted:
                pass  # оставляем текущее значение (заморожено в on_abort_click)
            else:
                self._progress_update(100)
            
            # Показываем результаты
            self.root.after(0, lambda: self.btn_scan.state(['!disabled']))
            self.root.after(0, lambda: self.btn_fix.state(['!disabled']))
            self.root.after(0, lambda: self.btn_show_sql.state(['!disabled']))
            
            # Сохраняем результаты сканирования для кнопки "Показать SQL для ручного исправления"
            # DS_080 §2.3: при «Сканировать» верификации фиксера нет — ключ
            # обнуляется явно, чтобы не/filter не использовал остаток прошлого
            # прогона «Исправить код» (send_to_ai уходит на fallback ignore_set).
            self.scan_results = {
                'scanner': scanner,
                'issues': scanner.issues,
                'issues_before_dedup': scanner.issues_before_dedup,
                'stats': scan_results,
                'remaining_by_rule': {},
                # DS_087 §2.3: чистый скан — фикса ещё не было.
                'fix_done': False,
            }
            
            # DS 040: окно результата — обычное или «прервано на xxx.xx %»
            # DS_053_Уточнение_5 (задача C): показываются все три лога.
            self.root.after(0, 
                lambda: self._show_scan_result_dialog(
                    files_count=scan_results.get('files_scanned', 0),
                    issues_count=scan_results.get('total_issues', 0),
                    report_path=output_path,
                    forecast_path=_scan_log_path,
                    html_report_path=html_report_path)
            )
            
        except Exception as e:
            self.log(f"[!] Ошибка сканирования: {e}", 'error')
            messagebox.showerror("Ошибка", f"Сканирование завершилось с ошибкой:\n{e}")
        finally:
            # DS 039: ВСЕГДА разблокируем «Сканировать»/«Исправить»
            # (успех / ошибка / прерывание) — раньше только в ветке успеха
            self.root.after(0, lambda: self.btn_scan.state(['!disabled']))
            self.root.after(0, lambda: self.btn_fix.state(['!disabled']))
            # DS_088b §2.2: звук завершения (scan_aborted ещё не сброшен).
            _sound_ok = not self.scan_aborted
            _sound_dur = time.time() - _op_start
            self.root.after(0, lambda s=_sound_ok, d=_sound_dur:
                            self._play_result_sound(s, d))
            # DS 038: сброс флагов прерывания и деактивация кнопки
            self.root.after(0, self._finish_abortable_operation)
    
    def _show_scan_result_dialog(self, files_count, issues_count, report_path,
                                 forecast_path=None, html_report_path=None):
        """DS 040: окно результата сканирования (обычное или прерванное).
        Нативный messagebox не поддерживает смену фона — используется tk.Toplevel.

        DS_053_Уточнение_5 (задача C): показываются все три лога —
        Основной (scan_report_*), Прогноз (scan_VVxVVx_*), PlpCheck
        (plpcheck_report_*.html). Если лог не сформирован — пометка
        «не сформирован»."""
        is_aborted = self.abort_percent is not None

        # DS 040: расчёт процента прерывания
        abort_percent = self.abort_percent or 0.0

        if is_aborted:
            title = f"Сканирование прервано на {abort_percent:.2f} %"
            bg_color = '#FFF4CC'      # светло-жёлтый
            fg_color = '#8B6914'      # тёмно-жёлтый для текста
            icon_symbol = '⚠'
        else:
            title = "Сканирование завершено"
            bg_color = '#FFFFFF'
            fg_color = '#333333'
            icon_symbol = 'ℹ'

        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg=bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Заголовок
        header = tk.Label(
            dialog,
            text=f"{icon_symbol}  {title}",
            font=('Segoe UI', 11, 'bold'),
            bg=bg_color,
            fg=fg_color
        )
        header.pack(padx=20, pady=(15, 10))

        # Тело
        body_text = (
            f"Найдено *.plp файлов: {files_count}\n"
            f"Проблемных конструкций: {issues_count}\n"
            "\n"
            "Отчёты:\n"
            f"  Основной:  {report_path}\n"
            f"  Прогноз:   {forecast_path if forecast_path else 'не сформирован'}\n"
            f"  PlpCheck:  {html_report_path if html_report_path else 'не сформирован'}"
        )
        if is_aborted:
            body_text += f"\n\n⚠ Прервано пользователем на {abort_percent:.2f} %"

        body = tk.Label(
            dialog,
            text=body_text,
            justify='left',
            bg=bg_color,
            fg=fg_color,
            font=('Segoe UI', 9)
        )
        body.pack(padx=20, pady=(0, 15))

        # Кнопка OK
        ok_btn = tk.Button(
            dialog,
            text="OK",
            command=dialog.destroy,
            width=10,
            bg='#FFA500' if is_aborted else 'SystemButtonFace',
            fg='white' if is_aborted else 'SystemButtonText'
        )
        ok_btn.pack(pady=(0, 15))

        # Центрирование
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        self.root.wait_window(dialog)
    
    def start_deep_scan(self):
        """Запуск глубокого сканирования в отдельном потоке"""
        if not self.source_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите исходный каталог!")
            return
        
        # Проверка: выбран ли хотя бы один файл в рубрикаторе
        any_rule_selected = any(var.get() for var in self.selected_rules.values())
        if not any_rule_selected:
            messagebox.showerror("Ошибка", "Выберите хотя бы один файл в рубрикаторе!")
            return
        
        # Отключаем кнопку на время сканирования
        self.btn_scan.state(['disabled'])
        self.btn_fix.state(['disabled'])
        
        # Логирование начала глубокого сканирования
        self.log("\n" + "="*80, 'highlight')
        self.log("НАЧАЛО ГЛУБОКОГО СКАНИРОВАНИЯ (Deep Scan)", 'highlight')
        self.log("="*80, 'highlight')
        
        # Запускаем сканирование в отдельном потоке с флагом deep_mode
        thread = threading.Thread(target=self._run_scan, args=(True,), daemon=True)
        thread.start()
    
    def start_fix(self):
        """Запуск исправления кода"""
        # DS 036: проверка выбранных категорий PlpCheck
        if not self._check_plpcheck_categories_before_action():
            return  # Пользователь отменил
        
        if not self.source_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите исходный каталог!")
            return
        
        # Автоматическое формирование каталога результатов из исходного
        # PATCH_IN/xxx -> PATCH_OUT (без подкаталога)
        # PATCH_OUT/xxx -> PATCH_IN (без подкаталога)
        source_path = Path(self.source_dir_var.get())
        auto_result = self._auto_fill_result_dir(source_path)
        if auto_result:
            self.result_dir_var.set(str(auto_result))
            self.log(f"Каталог результатов обновлён: {auto_result}", 'info')
        
        # Проверяем наличие каталога результатов
        if not self.result_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите каталог результатов!")
            return
        
        result_path = Path(self.result_dir_var.get())
        
        # Автоматическое формирование полного пути к каталогу результатов
        # Если исходный PATCH_IN/xxx, а результат PATCH_OUT - добавляем подкаталог xxx
        result_path = self._ensure_result_path(source_path, result_path)
        
        # Создаем каталог результатов если не существует
        if not result_path.exists():
            self.log(f"Создание каталога результатов: {result_path}", 'info')
            result_path.mkdir(parents=True, exist_ok=True)
            self.result_dir_var.set(str(result_path))
            self.log(f"Каталог создан успешно", 'success')
        
        # Проверка: выбран ли хотя бы один файл в рубрикаторе
        any_rule_selected = any(var.get() for var in self.selected_rules.values())
        if not any_rule_selected:
            messagebox.showerror("Ошибка", "Выберите хотя бы один файл в рубрикаторе!")
            return
        
        # Отключаем кнопки на время работы
        self.btn_scan.state(['disabled'])
        self.btn_fix.state(['disabled'])
        
        # DS 038: активировать кнопку «Прервать»
        self._start_abortable_operation()
        
        # Сброс индикатора
        self.progress.config(value=0)
        self.progress_label.config(text="0%")
        self.root.update_idletasks()
        
        # Если были изменения в правилах и рубрикатор не открывался
        if self.rules_changed:
            self.log_text.delete('1.0', tk.END)
            self.open_rubricator()
            self.rules_changed = False
        
        # Запускаем исправление в отдельном потоке
        self._stop_event.clear()
        thread = threading.Thread(target=self._run_fix, daemon=True)
        thread.start()
    
    def _run_fix(self):
        """Рабочая функция исправления (вызывается в отдельном потоке)"""
        # DS_089: флаг отмены для _run_fix.
        self._fix_abort = False
        # DS_088b §2.2: замер длительности для звука завершения.
        _op_start = time.time()
        # DS_089a §2.7: сохранение начала операции для прогноза времени.
        self._op_start_time = _op_start
        try:
            source_dir = Path(self.source_dir_var.get())
            result_dir = Path(self.result_dir_var.get())
            
            # Создание каталога результатов если отсутствует
            if not result_dir.exists():
                self.root.after(0, lambda: self.log(f"Создание каталога результатов: {result_dir}", 'info'))
                result_dir.mkdir(parents=True, exist_ok=True)
                self.root.after(0, lambda: self.log(f"Каталог создан успешно", 'success'))
            
            self.root.after(0, lambda: self.set_status("Исправление кода..."))
            self.root.after(0, lambda: self._log_separator("НАЧАЛО ИСПРАВЛЕНИЯ КОДА"))
            
            # Проверка условий для предварительного копирования структуры
            file_pattern = self.file_pattern_var.get()
            should_copy_structure = (
                self.preserve_structure_var.get()
            )
            
            if should_copy_structure:
                # Копируем структуру каталогов и все файлы (кроме .plp) из исходного в результат
                self.root.after(0, lambda: self.log("\n[0/5] Копирование структуры каталогов и файлов...", 'info'))
                files_copied = self._copy_directory_structure(source_dir, result_dir)
                self.root.after(0, lambda: self.log(f"  Скопировано файлов: {files_copied}", 'info'))
                self._progress_update(5)
            
            # Подготовка конфигурации
            config = {
                'paths': {
                    'source_dir': str(source_dir),
                    'results_dir': str(result_dir),
                    'logs_dir': str(Path(__file__).parent.parent / 'logs')
                },
                'scan': {
                    'recursive': self.scan_recursive_var.get(),
                    'file_pattern': self.file_pattern_var.get() if self.file_pattern_var.get() else '**/*.plp',
                    'exclude_patterns': ['.bak', '.tmp']
                },
'output': {
                    'only_modified': self.only_modified_var.get(),
                    'preserve_structure': self.preserve_structure_var.get(),
                    'fix_only_found': self.fix_only_found_var.get()
                },
                'rules': {
                    'max_comment_length': 60,
                    'mark_before_changed_line': True,
                    'comment_old_code': True,
                    'inline_comment': True
                },
                'logging': {
                    'level': self.log_level_var.get()
                }
            }
            
# Определение выбранных правил (DS 019/DS 020: только правила из выбранных файлов рубрикатора)
            selected_files = [code for code, var in self.selected_rules.items() if var.get()]
            
            # DS 020: фильтр PlpCheck применяется к ФАЙЛАМ до сбора правил
            if not self.plpcheck_enabled_var.get():
                selected_files = [r for r in selected_files if r != 'PlpCheck']
                self.root.after(0, lambda: self.log("\n[PlpCheck] Флаг выключен — правила стиля кода не применяются", 'info'))
            else:
                self.root.after(0, lambda: self.log("\n[PlpCheck] Флаг включён — применяются правила стиля кода", 'info'))
            
            # DS 036: фильтр категорий PlpCheck
            self.plpcheck_categories_filter = [
                code for code, var in self.var_plpcheck_categories.items() if var.get()
            ]
            self.root.after(0, lambda: self.log(
                f"[PlpCheck] Категории: {', '.join(self.plpcheck_categories_filter) or 'нет'}",
                'info'))
            
            selected_rules = self._get_rules_for_selected_files(selected_files)
            
            # DS 023: отладочный вывод в лог АРМ
            self.log(f"[DEBUG] selected_files: {selected_files}", 'info')
            self.log(f"[DEBUG] selected_rules (передано в сканер): {selected_rules[:20]}{' ...' if len(selected_rules) > 20 else ''} (всего {len(selected_rules)})", 'info')
            
            self.root.after(0, lambda: self.log("\nВЫБРАННЫЕ ФАЙЛЫ РУБРИКАТОРА:", 'highlight'))
            for f in selected_files:
                self.root.after(0, lambda ff=f: self.log(f"  [+] {ff}", 'highlight'))
            
            # Если выбраны приоритеты — используем правила из выбранных приоритетов (DS 018: HIGH/MEDIUM/LOW)
            # DS 024: защита от пустого результата — если после фильтра не осталось ни одного правила,
            # selected_rules НЕ обнуляется (иначе сканер загрузит ВСЕ правила)
            from rubricator_priority_mapping import PRIORITY_RULES
            priority_mapping = {'HIGH': 'Приоритет 1', 'MEDIUM': 'Приоритет 2', 'LOW': 'Приоритет 3'}
            selected_priorities = [priority_mapping.get(p, p) for p in getattr(self, '_selected_priorities', [])]
            
            if selected_priorities:
                # Собираем правила из выбранных приоритетов (DS 024)
                priority_rules = set()
                for prio in selected_priorities:
                    if prio in PRIORITY_RULES:
                        priority_rules.update(PRIORITY_RULES[prio])
                
                if priority_rules:
                    # DS 024: регистронезависимое сопоставление кодов
                    # PRIORITY_RULES использует 'PlpCheck.DBI.*.п.1', рубрикатор - 'plpcheck.ACCESS_STATIC'
                    pr_lower = {r.lower(): r for r in priority_rules}
                    filtered_rules = []
                    for r in selected_rules:
                        r_lower = r.lower()
                        # 1) точное совпадение (регистронезависимо)
                        if r_lower in pr_lower:
                            filtered_rules.append(r)
                            continue
                        # 2) частичное совпадение: код приоритета начинается с кода правила
                        #    (PlpCheck.DBI.OUTER_JOIN.п.1 vs plpcheck.DBI.OUTER_JOIN)
                        if any(pr.lower().startswith(r_lower) or r_lower.startswith(pr.lower()) for pr in priority_rules):
                            filtered_rules.append(r)
                    
                    if filtered_rules:
                        selected_rules = filtered_rules
                        self.root.after(0, lambda: self.log(f"\n[ПРИОРИТЕТ] Фильтрация по приоритетам: {', '.join(getattr(self, '_selected_priorities', []))}", 'highlight'))
                        self.root.after(0, lambda: self.log(f"  Всего правил из приоритетов: {len(priority_rules)}", 'info'))
                        self.root.after(0, lambda: self.log(f"  Используемых правил: {len(selected_rules)}", 'info'))
                    else:
                        # DS 024: НЕ обнуляем selected_rules — используем все правила выбранных файлов
                        self.root.after(0, lambda: self.log(f"\n⚠ Для выбранных файлов нет правил с приоритетами {', '.join(getattr(self, '_selected_priorities', []))}. Используются все правила выбранных файлов ({len(selected_rules)}).", 'warning'))
                else:
                    # DS 024: в PRIORITY_RULES нет правил — не трогаем selected_rules
                    self.root.after(0, lambda: self.log("\n⚠ Нет правил в PRIORITY_RULES. Используются все правила выбранных файлов.", 'warning'))
            
            self.root.after(0, lambda: self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА ({len(selected_rules)}):", 'info'))
            for rule in selected_rules[:30]:
                self.root.after(0, lambda r=rule: self.log(f"  [+] {r}", 'info'))
            if len(selected_rules) > 30:
                self.root.after(0, lambda: self.log(f"  ... и ещё {len(selected_rules) - 30} правил", 'info'))
            
            # Загрузка рубрикатора если ещё не загружен
            if not self.rubricator_loaded:
                self.root.after(0, self.load_rubricator_on_start)
            
            # Сброс прогресса
            self._progress_update(0)
            
            # Логирование вызова Парсера SQL (ПЕРЕД созданием сканера)
            self.log("\n[ПАРСЕР SQL] Начало сканирования и анализа...", 'highlight')
            self.log(f"  Источник: {source_dir}", 'debug')
            self.log(f"  Правила: {len(selected_rules)}", 'debug')
            self.root.update_idletasks()  # Принудительное обновление GUI
            
            # Создание сканера
            from analyzer.scanner import PLPlusScanner
            scanner = PLPlusScanner(config, selected_rules, self.rubricator_prompts,
                                    plpcheck_categories=getattr(self, 'plpcheck_categories_filter', []),
                                    abort_callback=self._abort_requested,  # DS 038
                                    stop_event=self._stop_event,            # DS_089b
                                    fix_flags=self._current_header_flags())  # DS_053_Уточнение_2 (задача A), DS_080 §0
            
            # Callback для вывода в журнал
            def scan_log(message, level='info'):
                self.root.after(0, lambda m=message, l=level: self.log(m, l))
            
            # Сканирование
            scan_results = scanner.scan_directory(log_callback=scan_log)
            
            self._progress_update(40)
            
            # Завершение работы Парсера SQL
            self.log(f"\n[ПАРСЕР SQL] Завершено:", 'highlight')
            self.log(f"  Найдено файлов: {scan_results.get('files_scanned', 0)}", 'info')
            self.log(f"  Найдено проблем: {scan_results.get('total_issues', 0)}", 'info')
            self.root.update_idletasks()  # Принудительное обновление GUI
            
            self.root.after(0, lambda: self.log(f"\n[1/5] Сканирование завершено...", 'info'))
            self.root.after(0, lambda: self.log(f"  Найдено *.plp файлов: {scan_results.get('files_scanned', 0)}", 'info'))
            self.root.after(0, lambda: self.log(f"  Проблемных конструкций: {scan_results.get('total_issues', 0)}", 'info'))
            
            if scan_results.get('total_issues', 0) == 0:
                self.root.after(0, lambda: self.log("\n[!] Проблем не найдено. Исправление не требуется.", 'warning'))
                self._progress_update(0)
                self.root.after(0, lambda: self.set_status("Готово"))
                self.root.after(0, lambda: self._log_separator("ИСПРАВЛЕНИЕ КОДА ЗАВЕРШЕНО (проблем не найдено)"))
                self.root.after(0, lambda: self.btn_scan.state(['!disabled']))
                self.root.after(0, lambda: self.btn_fix.state(['!disabled']))
                return
            
             # Создание фиксера
            from fixer.code_fixer import PLPlusFixer
            iteration = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = source_dir.name
            fixer = PLPlusFixer(config, iteration, clean_output=self.clean_output_var.get(),
                                abort_callback=self._abort_requested,  # DS 038
                                stop_event=self._stop_event)           # DS_089b
            
            # DS 053: передача флагов детерминированного фикса в фиксер.
            # DS_080 §0: только_ai в общем блоке «Флаги замены» — только_ai не
            # детерминированный, _run_fix() читает только известные ключи.
            try:
                fixer.flags = self._current_header_flags()
            except Exception as e:
                self.root.after(0, lambda e=e: self.log(f"  [!] Не удалось применить флаги DS_053: {e}", 'warning'))

            
            self._progress_update(50)
            
            # Определение каталога результатов
            if config['output']['preserve_structure']:
                # Сохраняем структуру каталогов
                final_results_dir = result_dir
            else:
                # Создаём подкаталог с меткой версии
                final_results_dir = result_dir / f"{source_name}_v{iteration}"
                final_results_dir.mkdir(parents=True, exist_ok=True)
            
            self.root.after(0, lambda: self.log(f"\n[2/5] Применение исправлений...", 'info'))
            self.root.after(0, lambda: self.log(f"  Каталог результатов: {final_results_dir}", 'info'))
            self.root.after(0, lambda: self.log(f"  Сохранять структуру: {config['output']['preserve_structure']}", 'info'))
            self.root.after(0, lambda: self.log(f"  Только модифицированные: {config['output']['only_modified']}", 'info'))
            
            # DS_089b §2.4: resume fix — передаём фиксеру уже обработанные
            # файлы из сохранённого состояния прерванного фикса (skip).
            _skip_files = None
            _resumed_fix = False
            _ab = getattr(self, '_abort_state', None)
            if _ab and _ab.get('operation') == 'fix':
                _skip_files = set(_ab.get('processed_files', []))
                self._abort_state = None
                if _skip_files:
                    _resumed_fix = True
                    _ts = time.strftime("%H:%M:%S")
                    _msg = (f"[{_ts}] Возобновление фикса "
                            f"(пропущено {len(_skip_files)} файлов)")
                    self.root.after(0, lambda m=_msg: self.log(m, 'info'))
                    self._bot_log(f"DS 089: {_msg}")

            # Передаём callback для вывода в журнал
            files_modified = fixer.fix_directory(scanner, final_results_dir, 
                                                  log_callback=scan_log, 
                                                  log_level=self.log_level_var.get(),
                                                  fix_only_found=self.fix_only_found_var.get(),
                                                  skip_files=_skip_files)

            # DS_089b §2.2: фикс прерван — сохранить обработанные файлы
            # для resume при следующем запуске «Исправить».
            if self.scan_aborted:
                _proc = list(getattr(fixer, 'processed_files', []))
                self._abort_state = {'operation': 'fix',
                                     'processed_files': _proc}
                _ts = time.strftime("%H:%M:%S")
                _msg = (f"[{_ts}] Состояние сохранено: 0 issues, "
                        f"{len(_proc)} файлов. Следующий фикс пропустит их "
                        f"(resume).")
                self.root.after(0, lambda m=_msg: self.log(m, 'warning'))
                self._bot_log(f"DS 089: {_msg}")

            # DS_089b §2.6: resume завершён успешно (не прерван повторно).
            if _resumed_fix and not self.scan_aborted:
                _ts = time.strftime("%H:%M:%S")
                _msg = f"[{_ts}] Операция возобновлена и завершена"
                self.root.after(0, lambda m=_msg: self.log(m, 'success'))
                self._bot_log(f"DS 089: {_msg}")
            
            self._progress_update(75)
            
            # Сохранение лога
            self.root.after(0, lambda: self.log("\n[3/5] Сохранение лога...", 'info'))
            log_path = Path(config['paths']['logs_dir']) / f'fix_log_{source_name}_{iteration}.md'
            fixer.save_log(log_path)

            # DS 053: лог сканирования/фиксации scan_VVxVVx_<source>_<ts>.md.
            try:
                scan_log_path = fixer.save_scan_log(Path(config['paths']['logs_dir']), source_name)
                if scan_log_path:
                    _slp = str(scan_log_path)
                    if len(_slp) >= 2 and _slp[1] == ':':
                        _slp = _slp[0].upper() + _slp[1:]
                    self.root.after(0, lambda p=_slp: self.log(f"  Лог флагов (scan_VVxVVx): {p}", 'info'))
            except Exception as e:
                self.root.after(0, lambda e=e: self.log(f"  [!] Ошибка лога scan_*: {e}", 'warning'))

            
            self._progress_update(90)
            
            # Вывод результатов
            self.root.after(0, lambda: self.log("\n[4/5] Финализация...", 'info'))
            self.root.after(0, lambda: self.log(f"\nРЕЗУЛЬТАТЫ:", 'info'))
            self.root.after(0, lambda: self.log(f"  Обработано *.plp файлов: {scan_results.get('files_scanned', 0)}", 'info'))
            self.root.after(0, lambda: self.log(f"  Исправлено конструкций: {scan_results.get('total_issues', 0)}", 'info'))
            self.root.after(0, lambda: self.log(f"  Создано файлов: {files_modified}", 'info'))
            self.root.after(0, lambda: self.log(f"  Результаты: {final_results_dir}", 'info'))
            # Нормализация пути к логу: буква диска в верхнем регистре
            log_path_str = str(log_path)
            if len(log_path_str) >= 2 and log_path_str[1] == ':':
                log_path_str = log_path_str[0].upper() + log_path_str[1:]
            self.root.after(0, lambda: self.log(f"  Лог: {log_path_str}", 'info'))
            
            # Итоги по файлам и категориям (минимальный режим)
            if scan_results.get('by_file'):
                self.root.after(0, lambda: self.log("\nИТОГИ ПО ФАЙЛАМ:", 'info'))
                for file_path, issues in scan_results['by_file'].items():
                    self.root.after(0, lambda f=file_path, i=issues: self.log(f"  {f}: {i} правок", 'info'))
            
            if scan_results.get('by_type'):
                self.root.after(0, lambda: self.log("\nИТОГИ ПО КАТЕГОРИЯМ:", 'info'))
                for issue_type, count in scan_results['by_type'].items():
                    self.root.after(0, lambda t=issue_type, c=count: self.log(f"  {t}: {c}", 'info'))
            
            self._progress_update(100)
            
            self.root.after(0, lambda: self._log_separator("ИСПРАВЛЕНИЕ КОДА ЗАВЕРШЕНО УСПЕШНО"))
            self.root.after(0, lambda: self.set_status("Готово"))
            self.root.after(0, lambda: self.btn_scan.state(['!disabled']))
            self.root.after(0, lambda: self.btn_fix.state(['!disabled']))
            self.root.after(0, lambda: self.btn_show_sql.state(['!disabled']))
            
            # Сохраняем результаты сканирования для кнопки "Показать SQL для ручного исправления"
            # DS_080 §2.1: остаток верификации фиксера (rule_code -> [строки]) —
            # источник фильтра «Только Ai» в send_to_ai.
            self.scan_results = {
                'scanner': scanner,
                'issues': scanner.issues,
                'issues_before_dedup': scanner.issues_before_dedup,
                'stats': scan_results,
                'remaining_by_rule': dict(
                    (getattr(fixer, 'verify_stats', None) or {}).get('remaining_by_rule', {})),
                # DS_087 §2.3: «фикс завершён, есть что проверить через Ai» —
                # состояние кнопки «От Ai» (btn_to_ai) до активации чекбокса.
                'fix_done': bool(scanner.issues),
            }
            
            # Обновить состояние кнопок после исправления
            self.root.after(0, self._update_buttons_state)
            
            # Проверка условий для архивации
            should_archive = (
                self.preserve_structure_var.get() and 
                self.archive_result_var.get()
            )
            
            if should_archive:
                # Запуск архивации в отдельном потоке
                thread = threading.Thread(target=self._run_archive, args=(final_results_dir, source_dir), daemon=True)
                thread.start()
            else:
                self.root.after(0, lambda: self.log("Архивация пропущена (отключена)", 'info'))
            
            # Показываем результаты с нормализацией буквы диска
            log_path_str = str(log_path)
            if len(log_path_str) >= 2 and log_path_str[1] == ':':
                log_path_str = log_path_str[0].upper() + log_path_str[1:]
            final_results_str = str(final_results_dir)
            if len(final_results_str) >= 2 and final_results_str[1] == ':':
                final_results_str = final_results_str[0].upper() + final_results_str[1:]
            
            self.root.after(0, 
                lambda: messagebox.showinfo("Исправление завершено", 
                          f"Обработано файлов: {scan_results.get('files_scanned', 0)}\n"
                          f"Исправлено конструкций: {scan_results.get('total_issues', 0)}\n"
                          f"Создано файлов: {files_modified}\n\n"
                          f"Результаты: {final_results_str}\n"
                          f"Лог: {log_path_str}"))
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.log(f"[!] Ошибка исправления: {error_msg}", 'error'))
            self.root.after(0, lambda: self.btn_scan.state(['!disabled']))
            self.root.after(0, lambda: self.btn_fix.state(['!disabled']))
            self.root.after(0, lambda: self.set_status("Готово"))
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Исправление завершилось с ошибкой:\n{error_msg}"))
        finally:
            # DS 043: финальный статус-бар (до сброса флагов)
            self.root.after(0, lambda: self.set_status("Прервано" if self.scan_aborted else "Готово"))
            # DS_088b §2.2: звук завершения (scan_aborted ещё не сброшен).
            _sound_ok = not self.scan_aborted
            _sound_dur = time.time() - _op_start
            self.root.after(0, lambda s=_sound_ok, d=_sound_dur:
                            self._play_result_sound(s, d))
            # DS 038: сброс флагов прерывания и деактивация кнопки
            self.root.after(0, self._finish_abortable_operation)
    
    def _run_archive(self, results_dir: Path, source_dir: Path):
        """Рабочая функция архивации (вызывается в отдельном потоке)"""
        try:
            self.root.after(0, lambda: self.log("\n[5/5] Архивация результатов...", 'info'))
            self._progress_update(95)
            
            # Архив создаётся в родительском каталоге результатов
            archive_path = results_dir.parent / f"{results_dir.name}.zip"
            
            # Создаём архив
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(results_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(results_dir.parent)
                        zipf.write(file_path, arcname)
                        self.root.after(0, lambda f=file: self.log(f"  Добавлен: {f}", 'debug'))
            
            # Копируем .pck файл: из source_dir.parent/{source_dir.name}.pck в results_dir/{results_dir.name}.pck
            source_pck = source_dir.parent / f"{source_dir.name}.pck"
            if source_pck.exists():
                result_pck_path = results_dir / f"{results_dir.name}.pck"
                if not result_pck_path.exists():
                    shutil.copy2(source_pck, result_pck_path)
                    self.root.after(0, lambda: self.log(f"  Копирован .pck файл в: {result_pck_path}", 'info'))
                else:
                    self.root.after(0, lambda: self.log(f"  .pck файл уже существует: {result_pck_path.name}", 'info'))
            else:
                self.root.after(0, lambda: self.log(f"  .pck файл не найден в источнике: {source_pck}", 'warning'))
            
            self._progress_update(100)
            
            archive_str = str(archive_path)
            if len(archive_str) >= 2 and archive_str[1] == ':':
                archive_str = archive_str[0].upper() + archive_str[1:]
            
            self.root.after(0, lambda: self.log(f"\nАрхив создан: {archive_str}", 'success'))
            self.root.after(0, 
                lambda: messagebox.showinfo("Архивация завершена", 
                          f"Архив создан:\n{archive_str}"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.log(f"[!] Ошибка архивации: {error_msg}", 'error'))
    
    def start_archive(self):
        """Запуск архивации вручную"""
        if not self.result_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите каталог результатов!")
            return
        
        results_dir = Path(self.result_dir_var.get())
        if not results_dir.exists():
            messagebox.showerror("Ошибка", f"Каталог результатов не найден: {results_dir}")
            return
        
        source_dir = Path(self.source_dir_var.get()) if self.source_dir_var.get() else None
        
        # Запускаем архивацию в отдельном потоке
        thread = threading.Thread(target=lambda: self._run_archive(results_dir, source_dir), daemon=True)
        thread.start()
    
    def start_test_generation(self):
        """Запуск генерации тестовых .plp-файлов"""
        # DS 036: проверка выбранных категорий PlpCheck
        if not self._check_plpcheck_categories_before_action():
            return  # Пользователь отменил
        
        # Проверка: выбран ли хотя бы один файл в рубрикаторе
        any_rule_selected = any(var.get() for var in self.selected_rules.values())
        if not any_rule_selected:
            messagebox.showerror("Ошибка", "Выберите хотя бы один файл в рубрикаторе!")
            return
        
        # DS 038: активировать кнопку «Прервать»
        self._start_abortable_operation()
        
        # Запускаем генерацию в отдельном потоке
        thread = threading.Thread(target=self._run_test_generation, daemon=True)
        thread.start()
    
    def _run_test_generation(self):
        """Рабочая функция генерации тестов (вызывается в отдельном потоке)"""
        # DS_088b §2.2: замер длительности для звука завершения.
        _op_start = time.time()
        # DS_089a §2.7: сохранение начала операции для прогноза времени.
        self._op_start_time = _op_start
        try:
            # Очистить журнал перед генерацией
            self.root.after(0, lambda: self.clear_log())
            
            self.root.after(0, lambda: self._log_separator("ГЕНЕРАЦИЯ ТЕСТОВЫХ .plp"))
            self.root.after(0, lambda: self.set_status("Генерация тестовых файлов..."))
            
            # Определяем каталог для тестовых файлов
            project_root = Path(__file__).parent.parent
            test_dir = project_root / 'DATA' / 'Тестовые файлы'
            
            # Создаем каталог если не существует
            if not test_dir.exists():
                self.root.after(0, lambda: self.log(f"Создание каталога: {test_dir}", 'info'))
                test_dir.mkdir(parents=True, exist_ok=True)
            
            # Используем новый TestGenerator
            try:
                from analyzer.test_generator import TestGenerator
                import json
                
                self.root.after(0, lambda: self.log("Использование нового генератора тестов...", 'info'))
                generator = TestGenerator(self.rubricator_dir)
                
                # Маппинг кодов файлов к правилам v5.0.0
                # selected_rules содержит коды файлов из 1.RUBRICATOR_FILES v5.md:
                #   v50 → все правила, начинающиеся с v50.
                #   тдс20240828, тклоик20240828 → правила, содержащие код в названии
                selected_file_codes = [code for code, var in self.selected_rules.items() if var.get()]
                
                if not selected_file_codes:
                    self.root.after(0, lambda: self.log("Нет выбранных файлов в рубрикаторе", 'warning'))
                    self.root.after(0, lambda: self.set_status("Готово"))
                    return
                
                # Собираем все доступные правила v5.0.0
                all_rules = generator.rubricator_v3.rules
                
                # Маппинг: код файла → список кодов правил
                matched_rules = []
                for file_code in selected_file_codes:
                    self.root.after(0, lambda fc=file_code: self.log(f"Поиск правил для файла: {fc}", 'info'))
                    if file_code == 'README':
                        self.root.after(0, lambda fc=file_code: self.log(f"  ⚠️ README — документация, правил нет", 'warning'))
                        continue
                    
                    # Ищем правила: для v50 — все начинающиеся с v50., для остальных — содержащих код
                    matching = [code for code in all_rules if code.startswith(file_code + '.') or file_code in code]
                    if matching:
                        matched_rules.extend(matching)
                        self.root.after(0, lambda fc=file_code, m=len(matching): self.log(f"  Найдено правил: {m}", 'info'))
                    else:
                        self.root.after(0, lambda fc=file_code: self.log(f"  ⚠️ Правил не найдено для файла: {fc}", 'warning'))
                
                if not matched_rules:
                    self.root.after(0, lambda: self.log("Нет подходящих правил для генерации", 'warning'))
                    self.root.after(0, lambda: self.set_status("Готово"))
                    return
                
                # Загружаем JSON для доступа к examples
                json_path = self.rubricator_dir / '4.RUBRICATOR_PROMPT v5.json'
                json_data = {}
                if json_path.exists():
                    with open(json_path, 'r', encoding='utf-8-sig') as f:
                        json_data = json.load(f)
                
                # Получаем выбранные приоритеты для фильтрации правил (DS 018: HIGH/MEDIUM/LOW)
                from rubricator_priority_mapping import PRIORITY_RULES
                priority_mapping = {'HIGH': 'Приоритет 1', 'MEDIUM': 'Приоритет 2', 'LOW': 'Приоритет 3'}
                selected_priorities = [priority_mapping.get(p, p) for p in getattr(self, '_selected_priorities', [])]
                
                # Если приоритеты выбраны — используем только правила из выбранных приоритетов
                if selected_priorities:
                    matched_rules = set()
                    for prio in selected_priorities:
                        if prio in PRIORITY_RULES:
                            matched_rules.update(PRIORITY_RULES[prio])
                    matched_rules = sorted(matched_rules)
                    self.root.after(0, lambda: self.log(f"Фильтрация по приоритетам: {', '.join(selected_priorities)}", 'info'))
                    self.root.after(0, lambda: self.log(f"  Найдено правил по приоритетам: {len(matched_rules)}", 'info'))
                else:
                    # Приоритеты не выбраны — используем все правила из выбранных файлов рубрикатора
                    matched_rules = []
                    for file_code in selected_file_codes:
                        self.root.after(0, lambda fc=file_code: self.log(f"Поиск правил для файла: {fc}", 'info'))
                        if file_code == 'README':
                            self.root.after(0, lambda fc=file_code: self.log(f"  ⚠️ README — документация, правил нет", 'warning'))
                            continue
                        
                        # Ищем правила: для v50 — все начинающиеся с v50., для остальных — содержащих код
                        matching = [code for code in all_rules if code.startswith(file_code + '.') or file_code in code]
                        if matching:
                            matched_rules.extend(matching)
                            self.root.after(0, lambda fc=file_code, m=len(matching): self.log(f"  Найдено правил: {m}", 'info'))
                        else:
                            self.root.after(0, lambda fc=file_code: self.log(f"  ⚠️ Правил не найдено для файла: {fc}", 'warning'))
                    matched_rules = sorted(set(matched_rules))
                
# Формируем отсортированный список правил
                # DS 038 (доработка): фильтруем правила, отсутствующие в
                # generator.rubricator_v3.rules (например, коды PRIORITY_RULES
                # вида 'PlpCheck.DBI.*.п.1') — иначе all_rules[rule_code] даёт KeyError
                missing = [r for r in matched_rules if r not in all_rules]
                sorted_rules = [r for r in matched_rules if r in all_rules]
                if missing:
                    self.root.after(0, lambda m=len(missing): self.log(
                        f"  Пропущено правил (нет в генераторе v5.0.0): {m}", 'warning'))
                total = len(sorted_rules)
                if not sorted_rules:
                    self.root.after(0, lambda: self.log("Нет правил для генерации после фильтрации", 'warning'))
                    self.root.after(0, lambda: self.set_status("Готово"))
                    return
                self.root.after(0, lambda t=total: self.log(f"Сводный файл: {t} правил v5.0.0", 'info'))
                
                # Генерируем один сводный файл
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_name = f"test_all_{timestamp}.plp"
                file_path = test_dir / file_name
                
                self.root.after(0, lambda: self.log(f"Создание сводного файла: {file_name}", 'info'))
                
                lines = []
                
                # Заголовок со списком всех правил
                lines.append('-- ============================================================================')
                lines.append(f'-- СВОДНЫЙ ТЕСТОВЫЙ ФАЙЛ: ВСЕ ПРАВИЛА v5.0.0 ({total} правил)')
                lines.append(f'-- Дата генерации: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                lines.append(f'-- Описание: Тестовые файлы для всех правил PLPlus адаптации')
                
                # Добавляем информацию о выбранных приоритетах (DS 018: HIGH/MEDIUM/LOW)
                selected_priorities = list(getattr(self, '_selected_priorities', []))
                if selected_priorities:
                    lines.append(f'-- Приоритеты: {", ".join(selected_priorities)}')
                
                lines.append('-- ============================================================================')
                lines.append('-- Список всех правил (HIGH, ' + str(total) + ' шт.):')
                lines.append('-- ============================================================================')
                
                for i, rule_code in enumerate(sorted_rules, 1):
                    rule = all_rules[rule_code]
                    short_desc = rule.short_description[:50] if rule.short_description else '...'
                    desc_padded = short_desc.ljust(55)
                    lines.append(f'-- {i:2d}.  {rule_code:45s} - {desc_padded}')
                
                lines.append('-- ============================================================================')
                lines.append('')
                
                # Секции для каждого правила
                aborted = False
                processed_rules = 0
                for i, rule_code in enumerate(sorted_rules, 1):
                    # DS 038 (доработка): проверка прерывания в цикле генерации —
                    # кнопка «Прервать» останавливает генерацию между правилами
                    if self.scan_aborted:
                        aborted = True
                        self.root.after(0, lambda n=processed_rules, t=total: self.log(
                            f"[ПРЕРВАНО] Генерация тестовых .plp остановлена пользователем. "
                            f"Обработано правил: {n} из {t}", 'warning'))
                        self.root.after(0, lambda: self.set_status("Прервано"))
                        break
                    
                    processed_rules = i
                    rule = all_rules[rule_code]
                    short_desc = rule.short_description[:60] if rule.short_description else '...'
                    
                    lines.append('-- ============================================================================')
                    lines.append(f'-- {i:2d}: {rule_code} - {short_desc}')
                    lines.append('-- ============================================================================')
                    
                    # Метаданные
                    lines.append('-- 3.RUBRICATOR_FIXES v5.md:')
                    lines.append(f'--   Короткое описание: {rule.short_description}')
                    lines.append(f'--   Подробное описание: {rule.documentation_text}')
                    
                    bad_main = rule.code_example_bad[0] if rule.code_example_bad else ''
                    extra_bads = rule.code_example_bad[1:] if rule.code_example_bad else []
                    
                    if bad_main:
                        lines.append(f'--   Пример кода (плохой): {bad_main}')
                    for idx, bad in enumerate(extra_bads, 2):
                        lines.append(f'--   Пример кода {idx} (плохой): {bad}')
                    
                    # Хорошие примеры из JSON
                    json_rule = json_data.get('rules', {}).get(rule_code, {})
                    examples = json_rule.get('examples', {})
                    good = ''
                    if examples:
                        good = examples.get('simple', {}).get('good', '')
                        if not good:
                            good = examples.get('simple_case', {}).get('good', '')
                        if not good:
                            for ex_name, ex_data in examples.items():
                                if ex_data.get('good'):
                                    good = ex_data['good']
                                    break
                    
                    if good:
                        lines.append(f'--   Пример кода (исправленный): {good}')
                    
                    parts = rule_code.split('.')
                    tags = ', '.join(parts) if len(parts) >= 2 else rule.priority
                    lines.append(f'--   Теги: {tags}')
                    
                    # JSON metadata
                    lines.append('-- 4.RUBRICATOR_PROMPT v5.json (расширенный):')
                    lines.append(f'--   documentation_text: {rule.documentation_text}')
                    lines.append(f'--   plplus_materials_note: {rule.plplus_materials_note}')
                    lines.append(f'--   search_prompt: {rule.search_prompt}')
                    
                    patterns_str = []
                    for p in rule.regex_patterns_search:
                        desc = p.get('description', p.get('pattern', ''))
                        patterns_str.append(f'({len(patterns_str)+1}) {desc}')
                    if patterns_str:
                        lines.append(f'--   regex_patterns.for_search: {"; ".join(patterns_str)}')
                    
                    if bad_main:
                        lines.append(f'--   code_example_bad: {bad_main}')
                    for idx, bad in enumerate(extra_bads, 2):
                        lines.append(f'--   code_example_bad{idx}: {bad}')
                    
                    if rule.fix_instruction:
                        lines.append(f'--   fix_instruction: {rule.fix_instruction}')
                    
                    lines.append(f'--   test_generation_prompt: Сгенерировать тестовый PLPlus файл для проверки правила \'{rule_code}\' с проблемными конструкциями.')
                    lines.append(f'--   examples.simple.bad: {bad_main if bad_main else "(нет примера)"}')
                    lines.append(f'--   examples.simple.good: {good if good else "(нет примера)"}')
                    
                    # Дополнительные примеры из JSON
                    if examples:
                        for ex_name in ['simple_case', 'parametrized_collection', 'parametrized_ref', 'with_order', 'between']:
                            if ex_name in examples:
                                ex = examples[ex_name]
                                ex_bad = ex.get('bad', ex.get('bad2', ''))
                                ex_good = ex.get('good', '')
                                lines.append(f'--   examples.{ex_name}.bad: {ex_bad}')
                                lines.append(f'--   examples.{ex_name}.good: {ex_good}')
                    
                    lines.append(f'--   priority: {rule.priority}')
                    lines.append(f'--   category: {rule.category}')
                    lines.append(f'--   subcategory: {rule.subcategory}')
                    lines.append(f'--   source_files: v50.docx')
                    lines.append(f'--   source_sections: {rule_code.split(".")[-1] if len(rule_code.split(".")) > 2 else "N/A"}')
                    lines.append('-- ============================================================================')
                    
# Блок кода PROCEDURE
                    proc_name = rule_code.replace('.', '_').replace('(', '').replace(')', '').replace(',', '')
                    # Транслитерация кириллицы в латиницу для имени процедуры
                    _CYR_TO_LAT = {
                        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
                        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
                        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
                        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
                        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
                        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
                        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
                        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
                    }
                    proc_name = ''.join(_CYR_TO_LAT.get(ch, ch) for ch in proc_name)
                    lines.append(f'PROCEDURE {proc_name} IS')
                    
                    if bad_main:
                        lines.append('	-- Объявления переменных из примеров')
                    
                    lines.append('BEGIN')
                    
                    # [-] Неправильный код
                    lines.append('	-- [-] Неправильный код')
                    if bad_main:
                        lines.append('	-- begin pl/sql')
                        for line in bad_main.strip().split('\n'):
                            lines.append(f'		{line.strip()}')
                        if extra_bads:
                            for extra in extra_bads:
                                lines.append(f'		-- Дополнительный пример:')
                                for line in extra.strip().split('\n'):
                                    lines.append(f'		{line.strip()}')
                        lines.append('	-- end pl/sql')
                    else:
                        lines.append('		-- (нет примера плохого кода)')
                    
                    lines.append('')
                    
                    # [+] Исправленный код
                    lines.append('	-- [+] Исправленный код')
                    if good:
                        lines.append('	-- begin pl/sql')
                        for line in good.strip().split('\n'):
                            lines.append(f'		{line.strip()}')
                        lines.append('	-- end pl/sql')
                    elif rule.fix_instruction:
                        lines.append('	-- begin pl/sql')
                        lines.append(f'		-- Исправление: {rule.fix_instruction}')
                        lines.append('	-- end pl/sql')
                    else:
                        lines.append('		-- (нет примера исправленного кода)')
                    
                    lines.append('END;')
                    lines.append('')
                    lines.append('')
                
                # Футер
                lines.append('-- ============================================================================')
                lines.append(f'-- КОНЕЦ ФАЙЛА: {total} правил v5.0.0')
                lines.append(f'-- Дата генерации: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                lines.append('-- ============================================================================')
                
                # DS 038 (доработка): при прерывании файл НЕ сохраняется
                if aborted:
                    self.root.after(0, lambda n=processed_rules: self.log(
                        f"[ПРЕРВАНО] Сводный файл не создан (обработано правил: {n}). "
                        f"Повторите генерацию без прерывания для полного файла.", 'warning'))
                else:
                    # Записываем файл
                    content = '\n'.join(lines)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.root.after(0, lambda fp=file_path: self.log(f"  ✅ Создан: {fp.name}", 'success'))
                    self.root.after(0, lambda t=total: self.log(f"\nСоздано сводных файлов: 1 ({t} правил)", 'info'))
                    
                    self.root.after(0, lambda: self._log_separator("ГЕНЕРАЦИЯ ЗАВЕРШЕНА"))
                    self.root.after(0, lambda: self.set_status("Готово"))
                    
                    self.root.after(0, 
                        lambda: messagebox.showinfo("Генерация завершена", 
                                  f"Создан сводный файл: {file_path.name}\n\n"
                                  f"Правил: {total}\n\n"
                                  f"Каталог: {test_dir}"))
                
            except ImportError as e:
                self.root.after(0, lambda: self.log(f"[!] Ошибка импорта TestGenerator: {e}", 'error'))
                self.root.after(0, lambda: self.set_status("Готово"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.log(f"[!] Ошибка генерации: {error_msg}", 'error'))
            self.root.after(0, lambda: self.set_status("Готово"))
        finally:
            # DS 039: ВСЕГДА разблокируем «Сканировать»/«Исправить» после генерации
            self.root.after(0, lambda: self.btn_scan.state(['!disabled']))
            self.root.after(0, lambda: self.btn_fix.state(['!disabled']))
            # DS 043: финальный статус-бар (до сброса флагов)
            self.root.after(0, lambda: self.set_status("Прервано" if self.scan_aborted else "Готово"))
            # DS 038: сброс флагов прерывания и деактивация кнопки
            self.root.after(0, self._finish_abortable_operation)

    def _run_test_generation_legacy(self, test_dir: Path):
        """Генерация тестовых файлов по старому алгоритму (из 3.RUBRICATOR_FIXES v5.md)"""
        try:
            # Загружаем данные из 3.RUBRICATOR_FIXES v5.md
            fixes_data = self._load_fixes_from_rubricator()
            
            # Группируем по кодам файлов
            fixes_by_file = {}
            for fix in fixes_data:
                file_code = fix.get('file_code', '')
                if file_code and fix.get('should_generate', False):
                    if file_code not in fixes_by_file:
                        fixes_by_file[file_code] = []
                    fixes_by_file[file_code].append(fix)
            
            # Генерируем файлы для каждого выбранного кода файла
            files_created = 0
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for file_code, fixes in fixes_by_file.items():
                if file_code in self.selected_rules and self.selected_rules[file_code].get():
                    # Формируем имя файла
                    safe_file_code = file_code.replace('.', '_').replace(' ', '_')
                    file_name = f"{safe_file_code}_{timestamp}.plp"
                    file_path = test_dir / file_name
                    
                    # Генерируем содержимое файла
                    content = self._generate_test_file_content(file_code, fixes)
                    
                    # Записываем файл
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    files_created += 1
                    self.root.after(0, lambda f=file_path: self.log(f"  Создан: {f.name}", 'success'))
            
            self.root.after(0, lambda: self.log(f"\nСоздано тестовых файлов (старый алгоритм): {files_created}", 'info'))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.log(f"[!] Ошибка генерации (legacy): {error_msg}", 'error'))
    
    def _load_fixes_from_rubricator(self) -> List[dict]:
        """Загрузка данных об исправлениях из 3.RUBRICATOR_FIXES v5.md"""
        fixes = []
        try:
            file_path = self.rubricator_dir / '3.RUBRICATOR_FIXES v5.md'
            if not file_path.exists():
                return fixes
            
            from utils.encoding_utils import read_file_with_encoding
            content, used_encoding = read_file_with_encoding(file_path)
            lines = content.split('\n')
            
            current_fix = {}
            for line in lines:
                if not line.strip() or line.startswith('#'):
                    continue
                
                if line.startswith('|') and not '|---' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 8:
                        # Формат: | N | ++ | Коды Файла... | Категория | Короткое описание | Подробное описание | Пример кода | Пример исправленного |
                        # Индексы: [0,  1,   2,             3,          4,                  5,                   6,            7]
                        try:
                            # Извлекаем теги из колонки "++" (формат: +|теги|Описание или +теги|)
                            plus_plus = parts[2].strip() if len(parts) > 2 else ''
                            tags = ''
                            if plus_plus and plus_plus[0] == '+':
                                # Проверяем формат "+|теги|Описание"
                                remaining = plus_plus[1:]  # Убираем первый '+'
                                if remaining.startswith('|'):
                                    # Формат "+|теги|Описание"
                                    parts_after_plus = remaining.split('|')
                                    if len(parts_after_plus) >= 2:
                                        tags = parts_after_plus[1].strip()
                            
                            current_fix = {
                                'n': parts[1].strip() if len(parts) > 1 else '',
                                'plus_plus': plus_plus,
                                'tags': tags,
                                'file_codes': parts[3].strip() if len(parts) > 3 else '',
                                'category': parts[4].strip() if len(parts) > 4 else '',
                                'short_desc': parts[5].strip() if len(parts) > 5 else '',
                                'full_desc': parts[6].strip() if len(parts) > 6 else '',
                                'example_code': parts[7].strip() if len(parts) > 7 else '',
                                'example_fixed': parts[8].strip() if len(parts) > 8 else '',
                            }
                            # Проверяем колонку "++" - если 1-й символ '+', генерируем
                            current_fix['should_generate'] = plus_plus.startswith('+')
                            # Извлекаем код файла (первый код из списка)
                            if current_fix['file_codes']:
                                file_code = current_fix['file_codes'].split('.')[0].strip()
                                current_fix['file_code'] = file_code
                            fixes.append(current_fix)
                            current_fix = {}
                        except Exception:
                            continue
        except Exception as e:
            self.log(f"[!] Ошибка загрузки данных рубрикатора: {e}", 'error')
        
        return fixes
    
    def _generate_test_file_content(self, file_code: str, fixes: List[dict]) -> str:
        """Генерация содержимого тестового .plp файла"""
        lines = []
        
        # Заголовок файла
        lines.append(f"-- Тестовый файл для проверки правил: {file_code}")
        lines.append(f"-- Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        for fix in fixes:
            n = fix.get('n', '')
            file_codes = fix.get('file_codes', '')
            category = fix.get('category', '')
            tags = fix.get('tags', '')
            short_desc = fix.get('short_desc', '')
            full_desc = fix.get('full_desc', '')
            example_code = fix.get('example_code', '')
            example_fixed = fix.get('example_fixed', '')
            
            # Заголовок теста в формате: --[№] КодФайла.Категории.Исправления.Пункты/Строки|Теги|Короткое описание
            lines.append(f"--[{n}] {file_code}.{category}|Теги:{tags}|{short_desc}")
            
            # Генерируем тестовый код на основе документации
            test_code = self._generate_test_code(example_code, example_fixed, full_desc)
            
            if test_code:
                lines.append("")
                lines.append(test_code)
            else:
                # Если не удалось сгенерировать - TODO
                lines.append("")
                lines.append("--TODO: Не удалось сгенерировать тестовый код на основе документации")
                lines.append("--TODO: " + full_desc)
            
            lines.append("")
            lines.append("--" + "="*60)
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_test_code(self, example_code: str, example_fixed: str, full_desc: str) -> str:
        """Генерация тестового кода на основе примера или описания"""
        # Используем пример кода если есть
        code_source = example_code if example_code else example_fixed
        
        if code_source:
            # Дополняем код согласно синтаксису PL/Plus
            return self._complete_code_plplus(code_source)
        else:
            # Если нет примера - возвращаем None (будет TODO)
            return None
    
    def _complete_code_plplus(self, code: str) -> str:
        """
        Дополнение незавершенного кода PL/Plus согласно синтаксису.
        Добавляет begin/end; loop; exit; и комментарии <добавлено при генерации теста>
        """
        lines = []
        code_lines = code.strip().split('\n')
        
        # Проверяем, есть ли begin в коде
        has_begin = any('begin' in line.lower() for line in code_lines)
        has_end = any('end' in line.lower() for line in code_lines)
        has_loop = any('loop' in line.lower() for line in code_lines)
        has_for = any('for' in line.lower() for line in code_lines)
        
        # Если код не содержит begin - добавляем
        if not has_begin:
            lines.append("begin --<добавлено при генерации теста>")
        else:
            lines.append("begin")
        
        for line in code_lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Если строка содержит for-loop, оборачиваем правильно
            if has_for and has_loop:
                if 'loop' in stripped.lower():
                    lines.append(f"  {stripped} --<добавлено при генерации теста>")
                else:
                    lines.append(f"  {stripped}")
            else:
                lines.append(f"  {stripped}")
        
        # Если есть loop, добавляем end loop
        if has_loop:
            lines.append("end loop; --<добавлено при генерации теста>")
        else:
            # Если нет loop, добавляем exit для завершения
            lines.append("  exit; --<добавлено при генерации теста>")
        
        # Добавляем end
        if not has_end:
            lines.append("end; --<добавлено при генерации теста>")
        else:
            lines.append("end;")
        
        return '\n'.join(lines)
    
    def show_sql_for_manual_fix(self):
        """Показать файл со всеми найденными SQL конструкциями для ручного исправления"""
        if not self.scan_results:
            messagebox.showwarning("Предупреждение", 
                                  "Сначала выполните сканирование!\n\n"
                                  "Нажмите кнопку «Сканировать» (F5)")
            return
        
        try:
            self._log_separator("ГЕНЕРАЦИЯ ФАЙЛА SQL ДЛЯ РУЧНОГО ИСПРАВЛЕНИЯ")
            self.log("Генерация файла со всеми найденными SQL конструкциями...", 'info')
            
            # Получаем результаты сканирования
            issues = self.scan_results.get('issues', [])
            
            if not issues:
                messagebox.showinfo("Нет проблем", "Проблемных конструкций не найдено")
                return
            
            # Создаём временный файл
            project_root = Path(__file__).parent.parent
            temp_dir = project_root / 'temp'
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            sql_file = temp_dir / f'sql_for_manual_fix_{timestamp}.sql'
            
            # Группируем проблемы по файлам
            by_file = {}
            for issue in issues:
                if issue.file_path not in by_file:
                    by_file[issue.file_path] = []
                by_file[issue.file_path].append(issue)
            
            # Генерируем содержимое SQL-файла
            lines = []
            lines.append("-- ФАЙЛ: SQL конструкции для ручного исправления")
            lines.append(f"-- Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            # DS_064_Уточнение_A (B1): «до дедупа» — из поля сканера, «уникальных» —
            # по дедуплицированному списку issues.
            before = self.scan_results.get('issues_before_dedup')
            if before is not None and before != len(issues):
                lines.append(f"-- Всего issues (с дублями): {before}")
            lines.append(f"-- Всего проблем (после дедупа): {len(issues)}")
            # Дефект 5 (DS_066 §3.5): счётчик «Уникальных (file,line,check)» удалён
            lines.append(f"-- Файлов: {len(by_file)}")
            lines.append("")
            lines.append("-- ВАЖНО: Этот файл содержит список всех найденных проблемных конструкций.")
            lines.append("-- Используйте его для ручного исправления или анализа.")
            lines.append("")
            lines.append("=" * 80)
            lines.append("")
            
            for file_path, file_issues in sorted(by_file.items()):
                lines.append(f"--{'='*78}")
                lines.append(f"-- ФАЙЛ: {file_path}")
                lines.append(f"-- Проблем: {len(file_issues)}")
                lines.append(f"--{'='*78}")
                lines.append("")
                
                # Группируем проблемы по строкам
                by_line = {}
                for issue in file_issues:
                    if issue.line_number not in by_line:
                        by_line[issue.line_number] = []
                    by_line[issue.line_number].append(issue)
                
                for line_num in sorted(by_line.keys()):
                    line_issues = by_line[line_num]
                    lines.append(f"-- Строка {line_num}: {len(line_issues)} проблем(ы)")
                    
                    # Получаем исходный код с учётом кодировки
                    try:
                        from utils.encoding_utils import read_file_with_encoding
                        content, used_encoding = read_file_with_encoding(file_path)
                        file_lines = content.splitlines()
                        if line_num <= len(file_lines):
                            original_code = file_lines[line_num - 1].rstrip()
                            lines.append(f"-- >>> {original_code}")
                    except Exception:
                        lines.append(f"-- >>> Код недоступен")
                    
                    # Выводим информацию о каждой проблеме
                    for idx, issue in enumerate(line_issues, 1):
                        lines.append(f"--   Проблема {idx}: {issue.issue_type}")
                        lines.append(f"--   Описание: {issue.description}")
                        if issue.rubricator_example_fixed:
                            lines.append(f"--   Пример исправления: {issue.rubricator_example_fixed}")
                    
                    lines.append("")
                    lines.append("")
            
            # Записываем файл
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            # Нормализация пути
            sql_file_str = str(sql_file)
            if len(sql_file_str) >= 2 and sql_file_str[1] == ':':
                sql_file_str = sql_file_str[0].upper() + sql_file_str[1:]
            
            self.log(f"Файл создан: {sql_file_str}", 'success')
            # DS_064_Уточнение_A (B1): «до дедупа» — из поля сканера, «уникальных» —
            # по дедуплицированному списку issues.
            before = self.scan_results.get('issues_before_dedup')
            if before is not None and before != len(issues):
                self.log(f"Всего issues (с дублями): {before}", 'info')
            self.log(f"Всего проблем (после дедупа): {len(issues)}", 'info')
            # Дефект 5 (DS_066 §3.5): счётчик «Уникальных (file,line,check)» удалён
            self.log(f"Всего файлов: {len(by_file)}", 'info')
            
            # Открываем файл в системе
            import os
            os.startfile(sql_file)
            
            self.log("Файл открыт в системе", 'info')
            
        except Exception as e:
            error_msg = str(e)
            self.log(f"[!] Ошибка генерации SQL-файла: {error_msg}", 'error')
            messagebox.showerror("Ошибка", f"Ошибка генерации файла:\n{error_msg}")
    
    def open_rubricator(self):
        """Открытие рубрикатора"""
        # Сохраняем текущий выбор перед очисткой
        saved_selection = {code: var.get() for code, var in self.selected_rules.items()}
        
        # Очистить журнал перед открытием
        self.clear_log()
        
        self.set_status("Открытие рубрикатора...")
        self._log_separator("-= ОТКРЫТИЕ РУБРИКАТОРА =-")
        
        # Если были изменения в выборе файлов, сбрасываем флаг загрузки
        if self.rules_changed:
            self.rubricator_loaded = False
            self.log("Обнаружены изменения в выборе файлов. Перезагрузка рубрикатора...", 'info')
            self.rules_changed = False
        
        try:
            # Восстанавливаем сохранённый выбор
            for code, selected in saved_selection.items():
                if code in self.selected_rules:
                    self.selected_rules[code].set(selected)
            # Всегда учитываем текущий выбор правил
            selected_codes = {code for code, var in self.selected_rules.items() if var.get()}
            
            # Вывод 1.RUBRICATOR_FILES v5.md с актуальными значениями "+/-"
            file_path = self.rubricator_dir / '1.RUBRICATOR_FILES v5.md'
            if file_path.exists():
                self.log(f"# {file_path}", 'info')
                self.log("# Рубрикатор: перечень файлов (с учетом текущего выбора)", 'info')
                try:
                    from utils.encoding_utils import read_file_with_encoding
                    content, used_encoding = read_file_with_encoding(file_path)
                    self.log(f"  (кодировка: {used_encoding})", 'debug')
                except Exception as enc_err:
                    self.log(f"  [!] Ошибка чтения файла: {enc_err}", 'error')
                    content = ""
                
                lines = content.strip().split('\n') if content else []
                
                for line in lines:
                    # Пропускаем заголовки и пустые строки
                    if line.startswith('#') or not line.strip():
                        continue
                    
                    # Пропускаем строки-разделители
                    if line.startswith('|---') or line.startswith('+-'):
                        continue
                    
                    # Обрабатываем строки с данными
                    if line.startswith('|'):
                        parts = [p.strip() for p in line.split('|')]
                        # Формат после split('|'): ['', 'N', '+/-', 'код', 'имя', '']
                        # Индексы:          [0,  1,   2,    3,   4,   5]
                        if len(parts) >= 5:
                            n = parts[1].strip()
                            original_sign = parts[2].strip()  # Старый знак из файла (не используем)
                            code = parts[3].strip()
                            name = parts[4].strip()
                            
                            # Пропускаем заголовки
                            if code.lower() in ['код файла', 'n', '№', '']:
                                continue
                            
                            # Определяем актуальный признак на основе выбранного состояния
                            if code in self.selected_rules:
                                current_sign = '+' if self.selected_rules[code].get() else '-'
                            else:
                                current_sign = original_sign  # Если код не найден, используем исходный
                            
                            # Формируем строку с фиксированной шириной колонок: 2, 2, 14, без ограничений
                            updated_line = f"|{n[:2]:<2}|{current_sign:<2}|{code[:14]:<14}|{name:<60}"
                            self.log(updated_line, 'info')
                
                self.log("+--+--+--------------+------------------------------------------------------------------------", 'info')
                
            
            # Вывод 2.RUBRICATOR_CATEGORIES.md
            file_path = self.rubricator_dir / '2.RUBRICATOR_CATEGORIES.md'
            if file_path.exists():
                self.log(f"# {file_path}", 'info')
                self.log("# Рубрикатор: категории исправлений (с учетом выбранных файлов)", 'info')
                try:
                    from utils.encoding_utils import read_file_with_encoding
                    content, used_encoding = read_file_with_encoding(file_path)
                    self.log(f"  (кодировка: {used_encoding})", 'debug')
                except Exception as enc_err:
                    self.log(f"  [!] Ошибка чтения файла: {enc_err}", 'error')
                    content = ""
                
                lines = content.strip().split('\n') if content else []
                for line in lines:
                    # Пропускаем заголовки и пустые строки
                    if line.startswith('#') or not line.strip():
                        continue
                    
                    # Выводим строки заголовка и разделителя
                    if line.startswith('|---') or 'Категория' in line:
                        self.log(line, 'info')
                        continue
                    
                    # Для строк с данными проверяем, есть ли выбранные коды файлов
                    if line.startswith('|'):
                        parts = [p.strip() for p in line.split('|')]
                        # Формат: ['', 'N', 'Категория', 'Код(ы) файлов', 'Описание', '']
                        # Индексы: [0,  1,   2,          3,                4]
                        if len(parts) >= 4:
                            codes_str = parts[3].strip()
                            # Разделяем коды файлов по запятой
                            file_codes = [c.strip() for c in codes_str.split(',')]
                            # Проверяем, есть ли хотя бы один выбранный код
                            if any(code in selected_codes for code in file_codes):
                                self.log(line, 'info')
                        else:
                            self.log(line, 'info')
                    
            # Вывод 3.RUBRICATOR_FIXES v5.md
            file_path = self.rubricator_dir / '3.RUBRICATOR_FIXES v5.md'
            if file_path.exists():
                self.log(f"# {file_path}", 'info')
                self.log("# Рубрикатор: перечень исправлений (с учетом выбранных правил)", 'info')
                try:
                    from utils.encoding_utils import read_file_with_encoding
                    content, used_encoding = read_file_with_encoding(file_path)
                    self.log(f"  (кодировка: {used_encoding})", 'debug')
                except Exception as enc_err:
                    self.log(f"  [!] Ошибка чтения файла: {enc_err}", 'error')
                    content = ""
                
                lines = content.strip().split('\n') if content else []
                
                # Вывод заголовков из файла (строки начинающиеся с #)
                for line in lines[:2]:
                    if line.startswith('#'):
                        self.log(line, 'info')
                
                # Вывод заголовка таблицы
                self.log("|---|--|----------------------------------------------|----------|--------------------------|----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|-------------------------------------------------------------", 'info')
                
                for line in lines[2:]:  # Пропускаем заголовки файла
                    if not line.strip():
                        continue
                    
                    # Пропускаем строки-разделители из файла (они уже выведены выше)
                    if '|---' in line:
                        continue
                    
                    # Для строк с данными проверяем колонку "++"
                    if line.startswith('|'):
                        parts = [p.strip() for p in line.split('|')]
                        # Формат: ['', 'N', '++', 'Коды Файла...', ...]
                        # Индексы: [0,  1,  2,   3,                ...]
                        if len(parts) >= 3:
                            plus_plus = parts[2].strip()
                            # 1-й символ колонки "++": '+' или ' ' (пробел) - выполнять, '-' - не выполнять
                            if plus_plus and plus_plus[0] == '-':
                                # Пропускаем строки с отключенным кодом исправления
                                continue
                            
                            # Проверяем, есть ли выбранные коды файлов
                            include_line = False
                            for code in selected_codes:
                                if code in line:
                                    include_line = True
                                    break
                            
                            if include_line:
                                self.log(line, 'info')
                    
            self.log("ВЫБРАННЫЕ ПРАВИЛА:", 'info')
            selected_count = 0
            for code, var in self.selected_rules.items():
                if var.get():
                    selected_count += 1
                    self.log(f"  [+] {code}: ВКЛ", 'info')
            
            self.log(f"\nВсего выбрано правил: {selected_count}", 'info')
            
            # Информация о выбранных приоритетах (DS 018: HIGH/MEDIUM/LOW)
            selected_priorities = list(getattr(self, '_selected_priorities', []))
            if selected_priorities:
                self.log("ВЫБРАННЫЕ ПРИОРИТЕТЫ:", 'highlight')
                for prio in selected_priorities:
                    self.log(f"  ★ {prio}", 'highlight')
            else:
                self.log("Приоритеты не выбраны (используются все правила из выбранных файлов)", 'info')
            
            # Устанавливаем флаг загрузки
            self.rubricator_loaded = True
                
        except Exception as e:
            self.log(f"[!] Ошибка открытия рубрикатора: {str(e)}", 'error')
    
        self.set_status("Готово")
    
    def on_close(self):
        """Закрытие приложения"""
        self.save_settings()
        self.log("Настройки сохранены. Приложение закрывается...", 'info')
        self.root.destroy()
    
    def clear_changelog(self):
        """Очистка журнала изменений"""
        self.changelog_text.configure(state='normal')
        self.changelog_text.delete('1.0', tk.END)
        self.changelog_text.configure(state='disabled')
    
    def show_changelog(self, changelog_text):
        """Отображение журнала в поле"""
        self.changelog_text.configure(state='normal')
        self.changelog_text.delete('1.0', tk.END)
        self.changelog_text.insert('1.0', changelog_text)
        self.changelog_text.configure(state='disabled')
        self.log("Журнал изменений обновлен", 'info')
    
    def save_changelog_to_file(self):
        """Сохранение журнала в файл"""
        changelog_content = self.changelog_text.get('1.0', tk.END)
        if not changelog_content.strip():
            messagebox.showwarning("Предупреждение", "Журнал пуст")
            return
        
        filename = f"CHANGELOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile=filename
        )
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(changelog_content)
            messagebox.showinfo("Успех", f"Журнал сохранен в:\n{filepath}")
            self.log(f"Журнал сохранен: {filepath}", 'success')
    
    def process_koda_response(self, response: str, clean_mode: bool = False):
        """
        Обработка ответа от KODA
        
        Args:
            response: ответ от KODA
            clean_mode: если True, возвращает только чистый код без маркеров
        """
        from fixer.code_fixer import parse_koda_response
        
        result = parse_koda_response(response, clean_mode)
        
        # Вставляем код в редактор (если есть)
        if hasattr(self, 'code_editor'):
            self.code_editor.delete('1.0', tk.END)
            self.code_editor.insert('1.0', result['code'])
        
        # Показываем журнал
        if result['changelog'] and clean_mode:
            self.show_changelog(result['changelog'])
            # Сохраняем журнал в файл
            self._save_changelog_to_disk(result['changelog'])
        elif not clean_mode:
            self.clear_changelog()
        
        self.log("Ответ от KODA обработан", 'info')
    
    def send_to_koda(self):
        """Отправка результатов сканирования в Koda через файл"""
        if not self.scan_results:
            messagebox.showwarning("Предупреждение", "Сначала выполните сканирование!")
            return
        
        try:
            exchange_dir = Path(__file__).parent.parent / 'EXCHANGE' / 'INBOX'
            exchange_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            task_file = exchange_dir / f"koda_task_{timestamp}.md"
            
            issues = self.scan_results.get('issues', [])
            stats = self.scan_results.get('stats', {})
            
            lines = []
            lines.append("# Задание для Koda: Исправление PLPlus кода")
            lines.append("")
            lines.append(f"## Статистика")
            lines.append(f"- Найдено файлов: {stats.get('files_scanned', 0)}")
            lines.append(f"- Найдено проблем: {stats.get('total_issues', 0)}")
            lines.append("")
            lines.append(f"## Проблемы ({len(issues)} шт.)")
            lines.append("")
            
            for i, issue in enumerate(issues, 1):
                lines.append(f"### {i}. {issue.issue_type}")
                lines.append(f"- Строка: {issue.line_number}")
                lines.append(f"- Описание: {issue.description}")
                lines.append(f"- Файл: {issue.file_path}")
                lines.append(f"- Было: {issue.original_code or 'N/A'}")
                if issue.rubricator_example_fixed:
                    lines.append(f"- Пример исправления: {issue.rubricator_example_fixed}")
                lines.append("")
            
            content = '\n'.join(lines)
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log(f"Задание отправлено в Koda: {task_file.name}", 'success')
            self.log(f"Файл: {task_file}", 'info')
            messagebox.showinfo("Успех", f"Задание отправлено в Koda!\n\nФайл: {task_file.name}")
            
            # Активируем кнопку получения ответа
            self.btn_receive_koda.state(['!disabled'])
            
        except Exception as e:
            self.log(f"Ошибка отправки в Koda: {e}", 'error')
            messagebox.showerror("Ошибка", f"Не удалось отправить задание:\n{e}")
    
    def receive_from_koda(self):
        """Получение ответа от Koda из OUTBOX"""
        try:
            exchange_dir = Path(__file__).parent.parent / 'EXCHANGE' / 'OUTBOX'
            if not exchange_dir.exists():
                messagebox.showwarning("Предупреждение", "Папка OUTBOX не найдена")
                return
            
            files = sorted(exchange_dir.glob('*.md')) + sorted(exchange_dir.glob('*.json'))
            if not files:
                messagebox.showinfo("Информация", "Нет ответов в OUTBOX")
                return
            
            # Берём последний файл
            last_file = files[-1]
            
            with open(last_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Вставляем в журнал изменений
            self.changelog_text.configure(state='normal')
            self.changelog_text.delete('1.0', tk.END)
            self.changelog_text.insert('1.0', content)
            self.changelog_text.configure(state='disabled')
            
            self.log(f"Ответ получен из: {last_file.name}", 'success')
            self.log(f"Размещено в Журнале изменений", 'info')
            
            # Перемещаем файл в PROCESSED
            processed_dir = Path(__file__).parent.parent / 'EXCHANGE' / 'PROCESSED'
            processed_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(last_file), str(processed_dir / last_file.name))
            
            self.log(f"Файл перемещен в PROCESSED: {last_file.name}", 'info')
            messagebox.showinfo("Успех", f"Ответ получен из:\n{last_file.name}\n\nРазмещён в Журнале изменений")
            
        except Exception as e:
            self.log(f"Ошибка получения ответа: {e}", 'error')
            messagebox.showerror("Ошибка", f"Не удалось получить ответ:\n{e}")
    
    # ------------------------------------------------------------------
    # DS 054: файловый обмен с AI (AI-fallback)
    # ------------------------------------------------------------------
    def _ai_rubricators(self) -> List[str]:
        """Список активных рубрикаторов для шапки AI-запроса."""
        names = []
        try:
            for code, var in self.selected_rules.items():
                try:
                    if var.get():
                        names.append(code)
                except Exception:
                    pass
        except Exception:
            pass
        return names

    def _ai_severity(self, issue_type: str) -> str:
        """Уровень WARNING/ERROR по коду правила (через сканер из scan_results)."""
        scanner = None
        if self.scan_results:
            scanner = self.scan_results.get('scanner')
        if scanner is not None and hasattr(scanner, '_get_severity_level'):
            try:
                return scanner._get_severity_level(issue_type)
            except Exception:
                return 'WARNING'
        return 'WARNING'

    def _bot_log(self, message: str):
        """DS_079: запись в EXCHANGE\bot.log (формат DS_050: [ДД.ММ.ГГГГ ЧЧ:ММ:СС]).

        Только EXCHANGE\bot.log — иные пути логов запрещены (AGENTS.md).
        Ошибки записи молча игнорируются (не должны ронять GUI-операцию).
        """
        try:
            log_path = Path(__file__).parent.parent / 'EXCHANGE' / 'bot.log'
            log_path.parent.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{ts}] {message}\r\n")
        except Exception:
            pass

    def send_to_ai(self):
        """DS 054: сформировать файл-запрос для AI в EXCHANGE\AI_IN.

        DS_080 §2.2: при галке «Только Ai» (по умолчанию включена) отбираются
        issues, реально требующие AI: (а) правило transform_type == "ignore"
        (5.RUBRICATOR_PARSER_SQL v5.json, plpcheck.<NAME> -> RuleEngine
        _resolve_code) И (б) issue остался в scan_results['remaining_by_rule']
        — не закрыт детерминированным конвейером (данные верификации фиксера).
        Если remaining_by_rule нет (не было «Исправить код») — fallback на
        ignore_set (DS_079) с записью в bot.log. При выключенной галке — все
        issues (обратная совместимость, отладка).
        """
        if not self.scan_results:
            messagebox.showwarning("Предупреждение", "Сначала выполните сканирование!")
            return
        issues = self.scan_results.get('issues', [])
        if not issues:
            messagebox.showinfo("Нет проблем", "Проблемных конструкций не найдено")
            return
        try:
            import ai_exchange
            ai_exchange.ensure_dirs()
            flags = self._current_fix_flags()
            rubs = self._ai_rubricators()
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')

            total = len(issues)
            # DS_079 §2.1: галка «Только Ai» (по умолчанию ВКЛ).
            ai_only = bool(getattr(self, 'ai_only_var', None)
                           and self.ai_only_var.get())
            # DS_080 §2.2: критерий отбора — (а) правило transform_type=="ignore"
            # И (б) issue остался в remaining_by_rule (не исправлен
            # детерминированным конвейером). Если remaining_by_rule нет (не было
            # «Исправить код») — fallback на ignore_set как в DS_079.
            filter_mode = ''
            if ai_only:
                eng = None
                try:
                    from rule_engine import get_rule_engine
                    eng = get_rule_engine()
                except Exception:
                    eng = None
                remaining = self.scan_results.get('remaining_by_rule') or {}
                issues, filter_mode = filter_ai_issues(issues, remaining, eng)
                if filter_mode == 'needs_ai_fix':
                    self.log(f"  Фильтр «только Ai»: needs_ai_fix (остаток после "
                             f"конвейера), правил в остатке: {len(remaining)}.", 'info')
                elif filter_mode == 'без фильтра':
                    self._bot_log("Движок правил недоступен — отправлены все issues.")
                    self.log("  [!] Движок правил недоступен — отправлены все issues.", 'warning')
                else:
                    self._bot_log("needs_ai_fix недоступен, фильтр по ignore_set.")
                    self.log("  Фильтр «только Ai»: needs_ai_fix недоступен, "
                             "отбор по ignore_set.", 'info')
                if not issues:
                    self._bot_log("Нет issues, требующих AI (фильтр «только Ai»).")
                    messagebox.showinfo(
                        "Нет issues, требующих AI",
                        "После фильтра «только Ai» не осталось проблем.\n"
                        "Снимите галку «Только Ai» для отправки всех issues.")
                    return

            # Группируем проблемы по файлам-источникам.
            by_file = {}
            for issue in issues:
                by_file.setdefault(issue.file_path, []).append(issue)

            self._log_separator("ФОРМИРОВАНИЕ AI-ЗАПРОСОВ (DS 054)")
            written = []
            for file_path, file_issues in sorted(by_file.items()):
                if not file_path or not Path(file_path).exists():
                    self.log(f"  [!] Пропуск (файл не найден): {file_path}", 'warning')
                    continue
                req = ai_exchange.write_request(
                    Path(file_path), file_issues, flags, rubs,
                    severity_fn=self._ai_severity, timestamp=ts)
                written.append(req)
                self.log(f"  AI-запрос: {req.name} ({len(file_issues)} проблем)", 'success')

            # DS_079 §2.2 п.5 / DS_080 §2.2 п.4: «Отправлено N issues из M
            # (фильтр: needs_ai_fix)». filter_mode = ignore_set — fallback без
            # верификации фиксера (не было «Исправить код»).
            if ai_only:
                self.log(f"Отправлено {len(issues)} issues из {total} "
                         f"(фильтр: {filter_mode})", 'highlight')
                self._bot_log(
                    f"Отправлено {len(issues)} issues из {total} "
                    f"(фильтр: {filter_mode}). AI-запросов: {len(written)}.")
            self.log(f"Сформировано AI-запросов: {len(written)} → EXCHANGE\AI_IN", 'highlight')
            self.log("Отправьте файл(ы) в AI, затем положите ответ "
                     "AI_RESPONSE_<source>_<ts>.md в EXCHANGE\AI_OUT и нажмите «От AI».", 'info')
            # DS_054_Уточнение_C: «От AI» включается только при наличии
            # файлов-ответов в AI_OUT (перепроверка после отправки).
            self._update_ai_button_state()
            ai_in = Path(__file__).parent.parent / 'EXCHANGE' / 'AI_IN'
            messagebox.showinfo(
                "AI-запрос сформирован",
                f"Файлов-запросов: {len(written)}\n\nКаталог: {ai_in}\n\n"
                "Отправьте их в AI и верните ответы в EXCHANGE\AI_OUT.")
        except Exception as e:
            self.log(f"Ошибка формирования AI-запроса: {e}", 'error')
            messagebox.showerror("Ошибка", f"Не удалось сформировать AI-запрос:\n{e}")

    def _rescan_ai_files(self, results) -> dict:
        """DS_081 §2.1: повторный скан только файлов, затронутых AI-ответами.

        Полный каталог НЕ пересканируется: берём source из results процесса
        «От AI», у которых что-то применено (applied_auto + applied_medium > 0).
        «было» — по pre-AI копии (_preai, создаётся process_response при
        backup=True), «стало» — по файлу после применения. Скан тем же
        механизмом, что верификация в «Исправить код» (отдельный
        PLPlusScanner с теми же правилами).

        Возвращает {'files': K, 'before': N, 'after': M}; пишет bot.log на
        файл и итоговую сводку. Ошибки не должны ронять обработку AI-ответов.
        """
        stats = {'files': 0, 'before': 0, 'after': 0}
        # DS_108b: суффиксы бэкапов — в rescan не берём
        _backup_suffix_re = re.compile(
            r'(_preai|_\d{8}_\d{6})\.plp$', re.IGNORECASE)
        touched = []
        for r in results or []:
            if not isinstance(r, dict) or r.get('status') != 'ok':
                continue
            try:
                applied = (int(r.get('applied_auto', 0) or 0) +
                           int(r.get('applied_medium', 0) or 0))
            except (TypeError, ValueError):
                applied = 0
            src = r.get('source')
            if applied > 0 and src and Path(src).exists():
                s = str(src)
                # DS_108b: отсеиваем бэкапы
                if _backup_suffix_re.search(s):
                    continue
                touched.append((s, r.get('backup_path')))
        # DS_108b: дедупликация по src (один файл мог быть в нескольких
        # AI-ответах — считать его дважды нельзя)
        if touched:
            seen = set()
            unique = []
            for s, bp in touched:
                key = str(Path(s).resolve()).lower()
                if key in seen:
                    continue
                seen.add(key)
                unique.append((s, bp))
            touched = unique
        if not touched:
            return stats

        base_sc = (getattr(self, 'scan_results', None) or {}).get('scanner')
        if base_sc is None:
            self.log("  Rescan: нет данных сканирования (scanner) — пропущен.", 'warning')
            return stats
        try:
            from analyzer.scanner import PLPlusScanner
            ver = PLPlusScanner(base_sc.config, base_sc.selected_rules,
                                base_sc.rubricator_prompts,
                                base_sc.plpcheck_categories)
        except Exception as e:
            self.log(f"  [!] Rescan: не создан verification-сканер: {e}", 'warning')
            return stats

        # _verify_file (верификация «как при Исправить код») живёт в фиксере —
        # берём лёгкий экземпляр без рубрикатора, он ничего не пишет.
        fx = None
        try:
            from fixer.code_fixer import PLPlusFixer
            fx = PLPlusFixer(base_sc.config, 'ai_rescan', use_rubricator=False)
            fx._verify_scanner = ver
            try:
                fx.flags = self._current_header_flags()
            except Exception:
                pass
        except Exception as e:
            self.log(f"  [!] Rescan: _verify_file недоступен, счёт по скану: {e}",
                     'warning')
            fx = None

        for src, backup_path in touched:
            try:
                before_issues = []
                if backup_path and Path(backup_path).exists():
                    before_issues = ver.scan_file(Path(backup_path)) or []
                n_before = len(before_issues)
                n_after = None
                if fx is not None:
                    try:
                        v = fx._verify_file(Path(src), before_issues) or {}
                        n_after = sum((v.get('remaining_count_by_rule') or {}).values())
                    except Exception:
                        n_after = None
                if n_after is None:
                    n_after = len(ver.scan_file(Path(src)) or [])
                stats['files'] += 1
                stats['before'] += n_before
                stats['after'] += n_after
                line = (f"Rescan {Path(src).name}: было {n_before}, "
                        f"стало {n_after}")
                self._bot_log(line)
                self.log("  " + line, 'info')
            except Exception as e:
                self.log(f"  [!] Rescan {Path(src).name}: ошибка {e}", 'warning')

        summary = (f"Rescan: {stats['files']} файлов; было {stats['before']}, "
                   f"стало {stats['after']}")
        self.log(summary, 'highlight')
        self._bot_log(summary)
        return stats

    def receive_from_ai(self):
        """DS 054: обработать файлы-ответы из EXCHANGE\AI_OUT."""
        try:
            import ai_exchange
            dirs = ai_exchange.ensure_dirs()
            out_dir = dirs['AI_OUT']
            files = sorted(list(out_dir.glob(ai_exchange.RESPONSE_PREFIX + '*.md')) +
                           list(out_dir.glob(ai_exchange.RESPONSE_PREFIX + '*.json')))
            if not files:
                messagebox.showinfo("Нет ответов",
                                    f"В каталоге нет файлов-ответов:\n{out_dir}")
                return

            self._log_separator("ОБРАБОТКА AI-ОТВЕТОВ (DS 054)")
            self.log(f"Найдено ответов: {len(files)}", 'info')
            # DS_088a_fix §2.4: пороги confidence из settings.json/полей формы.
            _conf_low, _conf_high = self._confidence_thresholds()
            self.log(f"Пороги confidence: low={_conf_low}, high={_conf_high}", 'info')
            results = ai_exchange.process_all_responses(
                backup=True, conf_low=_conf_low, conf_high=_conf_high)
            # DS_081 §2.2: структурированная сводка — строки в журнал +
            # корзины by_confidence для артефакта needs_manual.
            summary = ai_exchange.summarize(results, structured=True)
            for line in summary['lines']:
                self.log(line, 'info')

            # DS_081 §2.1: повторный скан только AI-затронутых файлов
            # (полный каталог не пересканируется), строки в bot.log.
            try:
                self._rescan_ai_files(results)
            except Exception as e:
                self.log(f"  [!] Ошибка повторного скана после AI: {e}", 'warning')

            # DS_081 §2.3/§2.4: needs_manual_* в EXCHANGE\OUTBOX (пусто —
            # файл не создаётся, только bot.log).
            try:
                nm_path = ai_exchange.save_needs_manual(summary)
                nm_count = len((summary.get('by_confidence') or {}).get('manual') or [])
                if nm_path:
                    self.log(f"  needs_manual: {nm_count} → {nm_path}", 'success')
                    self._bot_log(f"needs_manual: {nm_count} → {nm_path.name}")
                else:
                    self.log("  needs_manual: 0", 'info')
                    self._bot_log("needs_manual: 0")
            except Exception as e:
                self.log(f"  [!] Ошибка артефакта needs_manual: {e}", 'warning')

            # Дублируем сводку в Журнал изменений (КР).
            try:
                summary_text = "\n".join(summary['lines'])
                self.changelog_text.configure(state='normal')
                self.changelog_text.insert(tk.END,
                    f"\n\n=== AI-ответы ({datetime.now():%Y-%m-%d %H:%M:%S}) ===\n"
                    f"{summary_text}\n")
                self.changelog_text.configure(state='disabled')
            except Exception:
                pass

            total_ok = sum(1 for r in results if r.get('status') == 'ok')
            messagebox.showinfo(
                "AI-ответы обработаны",
                f"Обработано файлов: {total_ok} из {len(results)}\n\n"
                "См. Журнал выполнения и Журнал изменений.")
        except Exception as e:
            self.log(f"Ошибка обработки AI-ответов: {e}", 'error')
            messagebox.showerror("Ошибка", f"Не удалось обработать AI-ответы:\n{e}")
        finally:
            # DS_054_Уточнение_C: после обработки перепроверяем AI_OUT —
            # если файлы обработаны (архивированы), кнопка выключается.
            try:
                self._update_ai_button_state()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # DS_088a: автоматизация цикла «3. В Ai»
    #   send_to_ai → rule_based_fixer → ai_local_worker (Ollama) →
    #   ожидание AI_RESPONSE (timeout 35 мин) → receive_from_ai.
    # Логика send_to_ai()/receive_from_ai() не меняется (§1).
    # ------------------------------------------------------------------
    def _log_to_journal(self, message: str):
        """DS_088a §2.1: запись в ЖВ (log_text) с учётом потока.

        Из главного потока — напрямую; из воркера — через root.after,
        чтобы обращения к Tk шли только из главного потока.
        """
        try:
            if threading.current_thread() is threading.main_thread():
                self.log(message)
            else:
                self.root.after(0, lambda m=message: self.log(m))
        except Exception:
            pass

    def _call_in_main(self, func, timeout=None):
        """DS_088a: выполнить func в главном потоке Tk и дождаться результата.

        Нужно, чтобы send_to_ai()/receive_from_ai() (работа с Tk-виджетами
        и messagebox) исполнялись в главном потоке, даже когда цикл запущен
        в фоновом потоке. Если мы уже в главном потоке — вызов прямой.
        """
        if threading.current_thread() is threading.main_thread():
            return func()
        done = threading.Event()
        box = {}

        def _wrap():
            try:
                box['result'] = func()
            except Exception as exc:  # noqa: BLE001 - пробрасываем наружу
                box['error'] = exc
            finally:
                done.set()

        self.root.after(0, _wrap)
        done.wait(timeout)
        if 'error' in box:
            raise box['error']
        return box.get('result')

    def _ai_batch_size(self) -> int:
        """DS_088a §2.1: размер батча из tools/ai_local_worker_config.json."""
        try:
            cfg_path = (Path(__file__).parent.parent / 'tools'
                        / 'ai_local_worker_config.json')
            cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
            return int(cfg.get('batch_size', 10))
        except Exception:
            return 10

    def _check_ollama(self) -> bool:
        """DS_088a §2.6: доступность Ollama (GET /api/tags, timeout 5с).

        Реализовано на stdlib urllib (без зависимости requests).
        """
        try:
            url = 'http://localhost:11434/api/tags'
            with urllib.request.urlopen(url, timeout=5) as resp:
                return getattr(resp, 'status', resp.getcode()) == 200
        except Exception:
            return False

    @staticmethod
    def _pretty_source(request_name: str) -> str:
        """DS_088a §2.3: AI_REQUEST_<stem>_<ts>.md → <stem>.plp для ЖВ."""
        name = str(request_name)
        if name.startswith('AI_REQUEST_'):
            name = name[len('AI_REQUEST_'):]
        name = re.sub(r'_\d{8}_\d{6}\.(md|json)$', '', name)
        name = re.sub(r'\.(md|json)$', '', name)
        return f"{name}.plp"

    def _source_from_request_name(self, request_name: str) -> str:
        """DS_088a_fix §2.3: имя source-файла из AI_REQUEST_*.md («- Источник:»).

        Запрос одно-файловый, поэтому источник однозначен. Если файл/строка
        недоступны — fallback на _pretty_source (имя из самого AI_REQUEST).
        """
        try:
            in_dir = Path(__file__).parent.parent / 'EXCHANGE' / 'AI_IN'
            p = in_dir / request_name
            if p.exists():
                text = p.read_text(encoding='utf-8', errors='replace')
                m = re.search(r'^-\s*Источник:\s*(.+)$', text, re.MULTILINE)
                if m:
                    return Path(m.group(1).strip()).name
        except Exception:
            pass
        return self._pretty_source(request_name)

    def _monitor_worker(self, proc, batch_size: int):
        """DS_088a §2.5/§2.3 + DS_088a_fix §2.2: читать stdout воркера в ЖВ.

        Строки «batch X/Y <остаток>» выводятся в формате:
        «Батч(nn) X/Y: текущий — file.plp (<остаток>)», где nn — batch_size
        из конфига, file.plp — источник из AI_REQUEST («- Источник:»),
        остаток — из stdout как есть (ids=...: fixes=... время=... conf=...).
        Fallback (`fallback: split A -> B (по S)`) дополняется «(fallback B×S)».
        Прочие строки — как есть.
        """
        cur_file = ''
        fallback_size = 5
        batch_re = re.compile(r'batch\s+(\d+)\s*/\s*(\d+)')
        fb_split_re = re.compile(
            r'fallback:\s*split\s+\d+\s*->\s*(\d+)(?:\s*\(по\s*(\d+)\))?')
        try:
            for raw in iter(proc.stdout.readline, b''):
                text = raw.decode('utf-8', errors='replace').strip()
                if not text:
                    continue
                m = re.match(r'^(AI_REQUEST_[^:]+?):\s*\d+\s+issues', text)
                if m:
                    cur_file = self._source_from_request_name(m.group(1))
                fm = fb_split_re.search(text)
                if fm:
                    n_sub = fm.group(1)
                    size = fm.group(2) or str(fallback_size)
                    self._log_to_journal(f"{text} (fallback {n_sub}×{size})")
                else:
                    bm = batch_re.search(text)
                    if bm:
                        rest = text[bm.end():].strip()
                        suffix = f" ({rest})" if rest else ''
                        self._log_to_journal(
                            f"Батч({batch_size}) {bm.group(1)}/{bm.group(2)}: "
                            f"текущий — {cur_file}{suffix}")
                    else:
                        self._log_to_journal(text)
                if self._abort_requested():
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                    break
        finally:
            try:
                proc.wait()
            except Exception:
                pass

    def _wait_for_ai_response(self, timeout: int) -> bool:
        """DS_088a §2.4: ждать AI_RESPONSE_*.md/json в AI_OUT (шаг 10с).

        Возвращает True, если ответ появился; False — timeout или abort.
        """
        start = time.time()
        while time.time() - start < timeout:
            if self._abort_requested():
                return False
            if self._ai_out_files():
                return True
            time.sleep(10)
        return False

    def start_ai_cycle(self):
        """DS_088a: обработчик кнопки «3. В Ai» — запуск AI-цикла в фоне."""
        if getattr(self, '_ai_cycle_running', False):
            self.log("AI-цикл уже выполняется", 'warning')
            return
        if not self.scan_results:
            messagebox.showwarning("Предупреждение",
                                   "Сначала выполните сканирование!")
            return
        self._ai_cycle_running = True
        # DS_038: активировать «Прервать» и статус «Выполняется...» на время цикла.
        self._start_abortable_operation()
        thread = threading.Thread(target=self._run_ai_cycle, daemon=True)
        thread.start()

    def _run_ai_cycle(self):
        """DS_088a §2.2: полный AI-цикл (фоновый поток).

        Шаги: send_to_ai → rule_based_fixer → ai_local_worker (если Ollama) →
        ожидание AI_RESPONSE (35 мин) → receive_from_ai. Все шаги — в ЖВ.
        messagebox на время цикла подавляются (автономный режим), методы
        send_to_ai()/receive_from_ai() не изменяются.
        """
        root = Path(__file__).parent.parent
        tools = root / 'tools'
        ai_in = root / 'EXCHANGE' / 'AI_IN'
        ai_out = root / 'EXCHANGE' / 'AI_OUT'
        # DS_088b §2.2: замер длительности и признак успеха для звука.
        _op_start = time.time()
        _ai_ok = False
        # Подавляем модальные диалоги, пока идёт автономный цикл.
        import tkinter.messagebox as _mb
        saved = {}
        for name in ('showinfo', 'showwarning', 'showerror',
                     'askyesno', 'askokcancel'):
            saved[name] = getattr(_mb, name)
            setattr(_mb, name, lambda *a, **k: None)
        try:
            self._log_to_journal("Начало AI-цикла")
            # 1. Формирование AI_REQUEST_*.md в AI_IN.
            self._call_in_main(self.send_to_ai)
            if not self._ai_in_request_files():
                self._log_to_journal(
                    "AI-цикл прерван: AI_REQUEST не сформирован")
                return
            # 2a. rule_based_fixer (детерминированные правила) — DS_089a §2.5: Popen + мониторинг.
            self._log_to_journal("Запуск rule_based_fixer...")
            try:
                proc = subprocess.Popen(
                    [sys.executable, str(tools / 'rule_based_fixer.py'),
                     '--in-dir', str(ai_in), '--out-dir', str(ai_out)],
                    cwd=str(root), stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
                self._monitor_worker(proc, batch_size=0)
            except Exception as exc:
                self._log_to_journal(f"rule_based_fixer: ошибка {exc}")
            # 2b. ai_local_worker (локальная LLM) — если Ollama доступна.
            if self._check_ollama():
                self._log_to_journal("Запуск ai_local_worker...")
                bs = self._ai_batch_size()
                try:
                    proc = subprocess.Popen(
                        [sys.executable, str(tools / 'ai_local_worker.py'),
                         '--in-dir', str(ai_in), '--out-dir', str(ai_out),
                         '--resume'],
                        cwd=str(root), stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
                    self._monitor_worker(proc, bs)
                except Exception as exc:
                    self._log_to_journal(f"ai_local_worker: ошибка {exc}")
            else:
                self._log_to_journal("Ollama недоступна, AI-воркер пропущен")
            if self._abort_requested():
                self._log_to_journal("AI-цикл прерван пользователем")
                # DS_089a §2.8: AI-цикл не возобновляется (resume — DS_089b).
                self._log_to_journal(
                    "AI-цикл не возобновляется. "
                    "Новый цикл — по кнопке «3. В Ai».")
                return
            # 3. Ожидание AI_RESPONSE (timeout 35 мин).
            if not self._wait_for_ai_response(timeout=35 * 60):
                if self._abort_requested():
                    self._log_to_journal("AI-цикл прерван пользователем")
                    # DS_089a §2.8: AI-цикл не возобновляется (resume — DS_089b).
                    self._log_to_journal(
                        "AI-цикл не возобновляется. "
                        "Новый цикл — по кнопке «3. В Ai».")
                else:
                    self._log_to_journal("Timeout: AI_RESPONSE не получен")
                return
            # 4. Автоматический приём ответов.
            self._log_to_journal("Применение AI_RESPONSE...")
            self._call_in_main(self.receive_from_ai)
            self._log_to_journal("AI-цикл завершён")
            _ai_ok = True
        except Exception as exc:
            self._log_to_journal(f"AI-цикл: ошибка {exc}")
        finally:
            for name, fn in saved.items():
                setattr(_mb, name, fn)
            self._ai_cycle_running = False
            # DS_088b §2.2: звук завершения AI-цикла (до сброса scan_aborted).
            _sound_ok = _ai_ok and not self.scan_aborted
            _sound_dur = time.time() - _op_start
            try:
                self._call_in_main(
                    lambda s=_sound_ok, d=_sound_dur:
                    self._play_result_sound(s, d))
            except Exception:
                pass
            try:
                self._call_in_main(self._finish_abortable_operation)
            except Exception:
                pass
            # DS_088a тест 8: после цикла пересчитать активацию workflow
            # (AI_REQUEST заархивированы → «3. В Ai» снова disabled).
            try:
                self._call_in_main(self._update_workflow_buttons)
            except Exception:
                pass

    def _save_changelog_to_disk(self, changelog_text: str, source_file: str = ''):
        """Сохранение журнала на диск"""
        import os
        
        filename = os.path.basename(source_file) if source_file else 'unknown'
        name_without_ext = os.path.splitext(filename)[0]
        date_str = datetime.now().strftime('%Y%m%d')
        changelog_filename = f"CHANGELOG_{name_without_ext}_{date_str}.md"
        
        # Путь для сохранения - рядом с результатами
        results_dir = self.result_dir_var.get()
        if results_dir:
            changelog_path = os.path.join(results_dir, changelog_filename)
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(changelog_text)
            self.log(f"Журнал сохранен: {changelog_path}", 'success')


def main():
    """Точка входа приложения"""
    print(f"Запуск {APP_TITLE}...")
    root = tk.Tk()
    
    app = DBIMigrationApp(root)
    
    # Обработка закрытия
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    
    root.mainloop()
    print("Приложение закрыто")


if __name__ == '__main__':
    main()
