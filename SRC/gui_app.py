#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АРМ "Адаптация под DBI" v26.2.005
Графический интерфейс для миграции PLPlus кода на DBI
Версия: 2026 2-й квартал (апрель-июнь), версия 005
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

# Импорт модуля рубрикатора
from rubricator_prompts import RubricatorPrompts

# Константы версии
APP_VERSION = "v26.2.005"
APP_TITLE = f"АРМ 'Адаптация под DBI' {APP_VERSION}"
APP_QUARTER = "2026 2-й квартал (апрель-июнь)"
APP_RELEASE = "005"

# Константы для логов
MAX_LOG_SIZE_MB = 2  # Максимальный размер логов в МБ (по умолчанию)


class DBIMigrationApp:
    """Основное приложение"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1060x600")
        
        # Переменные
        self.source_dir_var = tk.StringVar()
        self.result_dir_var = tk.StringVar()
        self.file_pattern_var = tk.StringVar(value="**/*.plp")
        self.log_level_var = tk.StringVar(value="Минимальный")
        self.only_modified_var = tk.BooleanVar(value=True)
        self.preserve_structure_var = tk.BooleanVar(value=True)
        self.scan_recursive_var = tk.BooleanVar(value=True)
        
        # Состояние рубрикатора
        self.rubricator_loaded = False
        self.rubricator_dir = Path(__file__).parent.parent / 'DATA' / 'Рубрикатор'
        self.rubricator_files = {}  # Код файла: Полное имя из 1.RUBRICATOR_FILES.md
        
        # Новый рубрикатор 4.RUBRICATOR_PROMPTS.json
        self.rubricator_prompts: Optional[RubricatorPrompts] = None
        
        # Выбранные правила
        self.selected_rules = {}
        self.rule_checkboxes = {}  # Для доступа к виджетов
        
        # Сохранённые правила из предыдущего запуска
        self._saved_rules = []
        
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
        
        # Применить сохранённые правила, если они есть
        if self._saved_rules:
            self.log(f"Восстановлены сохранённые правила: {', '.join(self._saved_rules)}", 'info')
            # Устанавливаем чекбоксы для сохранённых правил
            for code in self._saved_rules:
                if code in self.rule_checkboxes:
                    item_id, var = self.rule_checkboxes[code]
                    var.set(True)
                    self.rules_tree.set(item_id, 'selected', '✓')
            self._saved_rules = []  # Сброс после применения
        
        # Привязка событий для поля ввода
        self._bind_entry_events()
    
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
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Секция 1 - Пути и настройки сканирования
        paths_frame = ttk.LabelFrame(scrollable_frame, text="1. Пути и настройки сканирования", padding="5")
        paths_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Строка 0: Исходный каталог
        ttk.Label(paths_frame, text="Исходный каталог:").grid(row=0, column=0, sticky=tk.W, padx=(0,1))
        self.source_entry = ttk.Entry(paths_frame, textvariable=self.source_dir_var, width=50)
        self.source_entry.grid(row=0, column=1, padx=0, sticky=tk.EW)
        ttk.Button(paths_frame, text="...", command=self.browse_source, width=3).grid(row=0, column=2, padx=(0,2))
        
        # Строка 0: Каталог результатов
        ttk.Label(paths_frame, text="Каталог результатов:").grid(row=0, column=3, sticky=tk.W, padx=(2,1))
        self.result_entry = ttk.Entry(paths_frame, textvariable=self.result_dir_var, width=50)
        self.result_entry.grid(row=0, column=4, padx=0, sticky=tk.EW)
        ttk.Button(paths_frame, text="...", command=self.browse_result, width=3).grid(row=0, column=5, padx=(0,0))
        
        # Строка 1: Шаблон + Сканировать подкаталоги
        ttk.Label(paths_frame, text="Шаблон:").grid(row=1, column=0, sticky=tk.W, padx=(0,1), pady=2)
        ttk.Entry(paths_frame, textvariable=self.file_pattern_var, width=50).grid(row=1, column=1, padx=0, sticky=tk.W)
        ttk.Checkbutton(paths_frame, text="Рекурсивно", variable=self.scan_recursive_var).grid(row=1, column=2, padx=(2,0), sticky=tk.W)
        
        paths_frame.grid_columnconfigure(1, weight=1)
        paths_frame.grid_columnconfigure(4, weight=1)
        
        # Секция 2 - Рубрикатор
        rules_frame = ttk.LabelFrame(scrollable_frame, text="2. Рубрикатор. Выбор корректировок", padding="5")
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        
        # Загрузка файлов рубрикатора
        self._load_rubricator_files()
        
        # Treeview с прокруткой (высота -50%, ширина -30%)
        tree_scroll_y = ttk.Scrollbar(rules_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(rules_frame, orient=tk.HORIZONTAL)
        
        self.rules_tree = ttk.Treeview(rules_frame, 
                                       yscrollcommand=tree_scroll_y.set, 
                                       xscrollcommand=tree_scroll_x.set,
                                       show='headings',
                                       height=3)
        
        tree_scroll_y.config(command=self.rules_tree.yview)
        tree_scroll_x.config(command=self.rules_tree.xview)
        
        # Настройка колонок: Выбрано | Код файла | Полное имя файла
        self.rules_tree['columns'] = ('selected', 'code', 'name')
        self.rules_tree.column('selected', width=3, minwidth=3, anchor=tk.CENTER)
        self.rules_tree.column('code', width=5, minwidth=5, anchor=tk.W)
        self.rules_tree.column('name', width=552, minwidth=200, anchor=tk.W)
        
        # Заголовки
        self.rules_tree.heading('selected', text='Выбрано', anchor=tk.CENTER)
        self.rules_tree.heading('code', text='Код файла', anchor=tk.W)
        self.rules_tree.heading('name', text='Полное имя файла', anchor=tk.W)
        
        # Размещаем Treeview и скроллы
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.rules_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Заполняем Treeview (позже, после создания кнопок)
        # self._populate_rules_tree() будет вызван после инициализации кнопок
        
        # Секция 3 - Опции сканирования и исправления. Логирование
        options_frame = ttk.LabelFrame(scrollable_frame, text="3. Опции сканирования и исправления. Логирование", padding="5")
        options_frame.pack(fill=tk.X, padx=5, pady=3)
        
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
        
        # Панель управления
        control_frame = ttk.Frame(scrollable_frame, padding="5")
        control_frame.pack(fill=tk.X)
        
        self.btn_scan = ttk.Button(control_frame, text="🔍 Сканировать", command=self.start_scan, width=20)
        self.btn_scan.pack(side=tk.LEFT, padx=3)
        
        self.btn_fix = ttk.Button(control_frame, text="✏️ Исправить код", command=self.start_fix, width=20)
        self.btn_fix.pack(side=tk.LEFT, padx=3)
        
        self.btn_rubricator = ttk.Button(control_frame, text="📖 Открыть рубрикатор", command=self.open_rubricator, width=25)
        self.btn_rubricator.pack(side=tk.LEFT, padx=3)
        
        self.btn_archive = ttk.Button(control_frame, text="📦 Архивировать результат", command=self.start_archive, width=25)
        self.btn_archive.pack(side=tk.LEFT, padx=3)
        self.btn_archive.state(['disabled'])
        
        self.btn_test_gen = ttk.Button(control_frame, text="🧪 Генерация тестовых .plp", command=self.start_test_generation, width=30)
        self.btn_test_gen.pack(side=tk.LEFT, padx=3)
        
        self.btn_show_sql = ttk.Button(control_frame, text="📋 Показать SQL для ручного исправления", command=self.show_sql_for_manual_fix, width=35)
        self.btn_show_sql.pack(side=tk.LEFT, padx=3)
        self.btn_show_sql.state(['disabled'])
        
        # Журнал выполнения
        journal_frame = ttk.LabelFrame(scrollable_frame, text="Журнал выполнения", padding="5")
        journal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        
        # Журнал с прокруткой (ширина как у грида рубрикатора)
        log_scroll_y = ttk.Scrollbar(journal_frame, orient=tk.VERTICAL)
        
        self.log_text = scrolledtext.ScrolledText(journal_frame, 
                                                  wrap=tk.NONE,
                                                  font=('Consolas', 9),
                                                  yscrollcommand=log_scroll_y.set,
                                                  height=11, width=58)
        
        log_scroll_y.config(command=self.log_text.yview)
        
        # Кнопки журнала — ПОД полем (pack раньше, чтобы были внизу секции)
        journal_buttons = ttk.Frame(journal_frame)
        journal_buttons.pack(side=tk.BOTTOM, fill=tk.X, pady=(3, 0))
        
        ttk.Button(journal_buttons, text="🗑️ Очистить журнал", command=self.clear_log).pack(side=tk.LEFT, padx=3)
        ttk.Button(journal_buttons, text="📋 Копировать в буфер", command=self.copy_log).pack(side=tk.LEFT, padx=3)
        
        # Скроллы и журнал
        log_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Цвета для логов
        self.log_text.tag_configure('info', foreground='black')
        self.log_text.tag_configure('warning', foreground='orange')
        self.log_text.tag_configure('error', foreground='red')
        self.log_text.tag_configure('success', foreground='green')
        self.log_text.tag_configure('debug', foreground='gray')
        self.log_text.tag_configure('highlight', foreground='green', font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure('pending', foreground='orange', font=('Consolas', 9, 'bold'))
        
        # Логируем загруженные файлы рубрикатора (после создания log_text)
        if self.rubricator_files:
            for code, name in self.rubricator_files.items():
                self.log(f"Загружен файл рубрикатора: {code} -> {name[:50]}...", 'debug')
        
        # Индикатор выполнения — процент в той же строке
        progress_frame = ttk.Frame(scrollable_frame, padding="5")
        progress_frame.pack(fill=tk.X)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_label = ttk.Label(progress_frame, text="0%", width=10)
        self.progress_label.pack(side=tk.LEFT, padx=5)
    
        # Путь для дублирования логов
        self.logs_deep_dir = Path(__file__).parent.parent / 'logs_Deep'
        self.logs_deep_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = None
    
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
            result = messagebox.askyesno(
                "Лимит логов превышен",
                f"Размер файлов логов: {size_mb:.2f} МБ\n"
                f"Максимальный размер: {MAX_LOG_SIZE_MB} МБ\n\n"
                f"Удалить все файлы логов?"
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
            file_path = self.rubricator_dir / '1.RUBRICATOR_FILES.md'
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
                                if code and not code.lower() in ['n', '№', 'код файла', '']:
                                    self.rubricator_files[code] = name
        except Exception as e:
            print(f"Ошибка загрузки рубрикатора: {e}")
    
    def _populate_rules_tree(self):
        """Заполнение Treeview правилами"""
        # Очищаем дерево
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        
        # Загружаем коды файлов из 1.RUBRICATOR_FILES.md
        for code, name in self.rubricator_files.items():
            # По умолчанию включаем правило
            var = tk.BooleanVar(value=True)
            self.selected_rules[code] = var
            
            # Вставляем в дерево (без иконки)
            item_id = self.rules_tree.insert('', tk.END, 
                                            values=('✓', code, name))
            self.rule_checkboxes[code] = (item_id, var)
        
        # Загрузка нового рубрикатора 4.RUBRICATOR_PROMPTS.json
        self._load_rubricator_prompts()
        
        # Обработчик клика для переключения чекбокса
        self.rules_tree.bind('<Button-1>', self._on_rule_click)
        self._update_buttons_state()
    
    def _load_rubricator_prompts(self):
        """Загрузка расширенного рубрикатора 4.RUBRICATOR_PROMPTS.json"""
        try:
            self.rubricator_prompts = RubricatorPrompts(self.rubricator_dir)
            if self.rubricator_prompts.load():
                self.log(f"Загружен расширенный рубрикатор: 4.RUBRICATOR_PROMPTS.json", 'debug')
                # Вывод доступных правил
                rules = self.rubricator_prompts.get_all_rules()
                for rule in rules:
                    self.log(f"  Правило: {rule['code']} ({rule.get('category', 'N/A')})", 'debug')
            else:
                self.log("Расширенный рубрикатор не найден или не загружен", 'warning')
        except Exception as e:
            self.log(f"Ошибка загрузки расширенного рубрикатора: {e}", 'error')
    
    def _on_rule_click(self, event):
        """Обработка клика по правилу"""
        item = self.rules_tree.identify_row(event.y)
        column = self.rules_tree.identify_column(event.x)
        
        # Колонка "Выбрано" (индекс 1)
        if column == '#1':
            for code, (item_id, var) in self.rule_checkboxes.items():
                if item_id == item:
                    var.set(not var.get())
                    self.rules_tree.set(item, 'selected', '✓' if var.get() else '✗')
                    self.rules_changed = True  # Флаг изменения выбора
                    # Сброс индикатора
                    self._reset_progress()
                    self.log(f"Правило {code}: {'включено' if var.get() else 'выключено'}", 'debug')
                    # Обновляем доступность кнопок
                    self._update_buttons_state()
                    break
    
    def _bind_entry_events(self):
        """Привязка событий для поля ввода - логирование только при потере фокуса"""
        # Привязываем события потери фокуса для полей ввода
        if self.source_entry:
            self.source_entry.bind('<FocusOut>', self._on_source_focus_out)
            # Также привязываем событие изменения для автоматического обновления результата
            self.source_dir_var.trace_add('write', lambda *args: self._on_source_dir_changed())
        if self.result_entry:
            self.result_entry.bind('<FocusOut>', self._on_result_focus_out)
    
        # Привязка события изменения чекбоксов и комбобоксов
        self.only_modified_var.trace_add('write', lambda *args: (self._reset_progress(), self._update_buttons_state()))
        self.preserve_structure_var.trace_add('write', lambda *args: (self._reset_progress(), self._update_buttons_state()))
        self.log_level_var.trace_add('write', lambda *args: self._reset_progress())
        self.scan_recursive_var.trace_add('write', lambda *args: self._reset_progress())
        self.file_pattern_var.trace_add('write', lambda *args: self._update_buttons_state())
        
        # Привязка события изменения выбора в рубрикаторе
        self.root.after(100, self._update_buttons_state)
    
    def _on_source_dir_changed(self):
        """Обработка изменения исходного каталога - автоматическое обновление результата"""
        source_dir = self.source_dir_var.get()
        if source_dir:
            source_path = Path(source_dir)
            self._auto_fill_result_dir(source_path)
            # Обновить состояние кнопок
            self._update_buttons_state()
    
    def _auto_fill_result_dir(self, source_dir: Path):
        """Автоматическое формирование каталога результатов из исходного"""
        source_str = str(source_dir).replace('/', '\\')
        source_name = source_dir.name
        
        if 'PATCH_IN' in source_str:
            # PATCH_IN/xxx -> PATCH_OUT/xxx
            result_base = source_str.replace('PATCH_IN', 'PATCH_OUT', 1)
            result_path = Path(result_base) / source_name
        elif 'PATCH_OUT' in source_str:
            # PATCH_OUT/xxx -> PATCH_IN/xxx
            result_base = source_str.replace('PATCH_OUT', 'PATCH_IN', 1)
            result_path = Path(result_base) / source_name
        else:
            return None
    
        # Нормализуем путь - убираем дублирование имени подкаталога
        result_str = str(result_path).replace('/', '\\')
        # Проверяем, не дублируется ли имя подкаталога в конце
        if result_str.endswith(f'\\{source_name}\\{source_name}'):
            result_str = result_str[:-len(source_name)-1]  # Убираем дубликат
            result_path = Path(result_str)
        
        # Проверяем текущее значение каталога результатов
        current_result = self.result_dir_var.get()
        if current_result:
            current_result = current_result.replace('/', '\\')
        
        # Обновляем только если каталог не указан или совпадает с базой без подкаталога
        if not current_result:
            self.result_dir_var.set(result_str)
            return result_path
        elif Path(current_result).parent == Path(result_base):
            # Текущий каталог - это базовая папка PATCH_OUT или PATCH_IN без подкаталога
            self.result_dir_var.set(result_str)
            return result_path
        
        return None
    
    def _ensure_result_path(self, source_dir: Path, result_dir: Path) -> Path:
        """
        Обеспечение корректного пути к каталогу результатов.
        Если исходный PATCH_IN/xxx, а результат PATCH_OUT - добавляем подкаталог xxx.
        """
        source_str = str(source_dir)
        result_str = str(result_dir)
        
        # Если исходный содержит PATCH_IN
        if 'PATCH_IN' in source_str:
            source_name = source_dir.name
            # Проверяем, содержит ли результат PATCH_OUT
            if 'PATCH_OUT' in result_str:
                # Проверяем, есть ли подкаталог с именем source_name
                expected_result = result_dir / source_name
                # Если текущий результат не содержит подкаталог, добавляем его
                if not result_str.endswith(source_name):
                    return expected_result
        
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
        
        # Кнопка "Сканировать" - только источник и рубрикатор
        scan_enabled = bool(source_dir) and any_rule_selected
        self.btn_scan.state(['!disabled' if scan_enabled else 'disabled'])
        
        # Кнопка "Исправить" - источник + результат + рубрикатор
        fix_enabled = bool(source_dir) and bool(result_dir) and any_rule_selected
        self.btn_fix.state(['!disabled' if fix_enabled else 'disabled'])
    
        # Кнопка "Показать SQL для ручного исправления" - активна после сканирования
        show_sql_enabled = self.scan_results is not None
        self.btn_show_sql.state(['!disabled' if show_sql_enabled else 'disabled'])
    
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
        
        self.btn_archive.state(['!disabled' if archive_enabled else 'disabled'])
    
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
    
    def _load_rules(self) -> dict:
        """Загрузка списка правил из рубрикатора"""
        rules = {}
        try:
            rubricator_path = self.rubricator_dir / '3.RUBRICATOR_FIXES.md'
            if rubricator_path.exists():
                with open(rubricator_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if '|' in line and not line.startswith('|---'):
                            parts = [p.strip() for p in line.split('|')]
                            if len(parts) >= 2:
                                code = parts[1] if len(parts) > 1 else ''
                                desc = parts[4] if len(parts) > 4 else ''
                                if code and code.startswith('v'):
                                    rules[code] = desc
        except Exception as e:
            print(f"Ошибка загрузки правил: {e}")
        
        if not rules:
            rules = {
                'v50': 'Рекомендации по адаптации кода на PLPlus для DBI',
                'тдс20240828': 'Правила для проекта ТДС',
                'тклоик20240828': 'Правила для проекта ТЦ ЛОИК'
            }
        
        return rules
    
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
            self._auto_fill_result_dir(Path(directory))
            # Обновляем доступность кнопок
            self._update_buttons_state()
    
    def browse_result(self):
        """Выбор каталога результатов"""
        directory = filedialog.askdirectory()
        if directory:
            # Нормализуем путь к Windows-формату
            directory = directory.replace('/', '\\')
            self.result_dir_var.set(directory)
            # Сброс индикатора
            self._reset_progress()
            # Логирование только при потере фокуса, здесь - мгновенно
            self.log(f"Каталог результатов: {directory}", 'info')
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
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        settings_path = Path(__file__).parent / 'settings.json'
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.source_dir_var.set(settings.get('source_dir', ''))
                    self.result_dir_var.set(settings.get('result_dir', ''))
                    self.file_pattern_var.set(settings.get('file_pattern', '**/*.plp'))
                    self.log_level_var.set(settings.get('log_level', 'Минимальный'))
                    self.scan_recursive_var.set(settings.get('recursive', True))
                    self.only_modified_var.set(settings.get('only_modified', True))
                    self.preserve_structure_var.set(settings.get('preserve_structure', True))
                    
                    # Загрузка сохранённых правил рубрикатора
                    saved_rules = settings.get('selected_rules', [])
                    if saved_rules:
                        self._saved_rules = saved_rules
                    else:
                        self._saved_rules = []
                        
                    # Загрузка настройки максимального размера логов
                    global MAX_LOG_SIZE_MB
                    max_log_size = settings.get('max_log_size_mb', 2)
                    if max_log_size:
                        MAX_LOG_SIZE_MB = max_log_size
                        
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
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        settings_path = Path(__file__).parent / 'settings.json'
        
        # Сохраняем выбранные правила рубрикатора
        selected_rules = [code for code, var in self.selected_rules.items() if var.get()]
        
        settings = {
            'source_dir': self.source_dir_var.get(),
            'result_dir': self.result_dir_var.get(),
            'file_pattern': self.file_pattern_var.get(),
            'log_level': self.log_level_var.get(),
            'recursive': self.scan_recursive_var.get(),
            'only_modified': self.only_modified_var.get(),
            'preserve_structure': self.preserve_structure_var.get(),
            'selected_rules': selected_rules,
            'max_log_size_mb': MAX_LOG_SIZE_MB
        }
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.log("Настройки сохранены", 'success')
        except Exception as e:
            self.log(f"Ошибка сохранения настроек: {e}", 'error')
    
    def show_project_structure(self):
        """Показ структуры проекта"""
        self._log_separator("СТРУКТУРА ПРОЕКТА")
        
        project_root = Path(__file__).parent.parent
        for item in project_root.rglob('*'):
            if not item.name.startswith('.') and item.is_file():
                rel_path = item.relative_to(project_root)
                self.log(f"  [ФАЙЛ] {rel_path}", 'info')
    
    def show_documentation(self):
        """Показ документации"""
        self._log_separator("ДОКУМЕНТАЦИЯ")
        
        docs_path = Path(__file__).parent / 'AI_DOCS'
        if docs_path.exists():
            for doc_file in docs_path.glob('*.txt'):
                self.log(f"  [ДОКУМЕНТ] {doc_file.name}", 'info')
                self.log(f"     Полный путь: {doc_file}", 'debug')
        else:
            self.log("  [!] Документация не найдена", 'warning')
    
    def set_status(self, message: str):
        """Установка сообщения в подвале"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def show_about(self):
        """Показ информации о программе"""
        messagebox.showinfo(
            "О программе",
            f"АРМ 'Адаптация под DBI' {APP_VERSION}\n\n"
            "Автоматизированное рабочее место для миграции\n"
            "PLPlus-кода с Oracle на PostgreSQL (2MCA DBI).\n\n"
            "Разработчик: NLP-Core-Team\n"
            f"Дата: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"Версия: {APP_QUARTER}, версия {APP_RELEASE}"
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
            # Вывод 1.RUBRICATOR_FILES.md
            file_path = self.rubricator_dir / '1.RUBRICATOR_FILES.md'
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
                    
            # Вывод 3.RUBRICATOR_FIXES.md
            file_path = self.rubricator_dir / '3.RUBRICATOR_FIXES.md'
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
        """Запуск сканирования в отдельном потоке"""
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
        
        # Запускаем сканирование в отдельном потоке с deep_mode=False
        thread = threading.Thread(target=self._run_scan, args=(False,), daemon=True)
        thread.start()
    
    def _run_scan(self, deep_mode=False):
        """Рабочая функция сканирования (вызывается в отдельном потоке)
        
        Args:
            deep_mode: Если True - использовать углублённое сканирование
        """
        try:
            # Сброс индикатора
            self.root.after(0, lambda: self.progress.config(value=0))
            self.root.after(0, lambda: self.progress_label.config(text="0%"))
            
            # Если были изменения в правилах и рубрикатор не открывался
            if self.rules_changed:
                self.root.after(0, lambda: self.log_text.delete('1.0', tk.END))
                self.root.after(0, self.open_rubricator)
                self.rules_changed = False
            
            self.root.after(0, lambda: self.set_status("Сканирование..."))
            self.root.after(0, lambda: self._log_separator("НАЧАЛО СКАНИРОВАНИЯ"))
            
            # Логирование использования нового рубрикатора
            if self.rubricator_prompts and self.rubricator_prompts.loaded:
                self.root.after(0, lambda: self.log("\n[ИСПОЛЬЗУЕТСЯ] Расширенный рубрикатор 4.RUBRICATOR_PROMPTS.json", 'highlight'))
                self.root.after(0, lambda: self.log(f"  Версия: {self.rubricator_prompts.data.get('version', 'N/A')}", 'debug'))
            else:
                self.root.after(0, lambda: self.log("\n[ИСПОЛЬЗУЕТСЯ] Старый рубрикатор 3.RUBRICATOR_FIXES.md", 'warning'))
            
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
                    'exclude_patterns': ['.v????', '.bak', '.tmp']
                },
                'logging': {
                    'level': self.log_level_var.get()
                }
            }
            
            # Определение выбранных правил
            selected_rules = [code for code, var in self.selected_rules.items() if var.get()]
            self.root.after(0, lambda: self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА ({len(selected_rules)}):", 'info'))
            for rule in selected_rules:
                self.root.after(0, lambda r=rule: self.log(f"  [+] {r}", 'info'))
            
            # Логирование использования промптов из нового рубрикатора
            if self.rubricator_prompts and self.rubricator_prompts.loaded:
                self.root.after(0, lambda: self.log("\nПРОМПТЫ ИЗ 4.RUBRICATOR_PROMPTS.json:", 'highlight'))
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
            self.root.after(0, lambda: self.progress.config(value=0))
            self.root.after(0, lambda: self.progress_label.config(text="0%"))
            
            # Создание сканера
            from analyzer.scanner import PLPlusScanner
            scanner = PLPlusScanner(config, selected_rules)
            
            # Логирование вызова Парсера SQL
            self.root.after(0, lambda: self.log("\n[ПАРСЕР SQL] Начало сканирования и анализа...", 'highlight'))
            self.root.after(0, lambda: self.log(f"  Источник: {config['paths']['source_dir']}", 'debug'))
            self.root.after(0, lambda: self.log(f"  Правила: {len(selected_rules)}", 'debug'))
            
            self.root.after(0, lambda: self.progress.config(value=10))
            self.root.after(0, lambda: self.progress_label.config(text="10%"))
            
            # Callback для вывода в журнал (вызывается в главном потоке)
            def scan_log(message, level='info'):
                self.root.after(0, lambda m=message, l=level: self.log(m, l))
            
            # Callback для вывода с разными тегами
            def scan_log_with_tags(parts):
                self.root.after(0, lambda p=parts: self.log_with_tags(p))
            
            # Сканирование
            scan_results = scanner.scan_directory(log_callback=scan_log)
            
            self.root.after(0, lambda: self.progress.config(value=50))
            self.root.after(0, lambda: self.progress_label.config(text="50%"))
            
            # Завершение работы Парсера SQL
            self.root.after(0, lambda: self.log(f"\n[ПАРСЕР SQL] Завершено:", 'highlight'))
            self.root.after(0, lambda: self.log(f"  Найдено файлов: {scan_results.get('files_scanned', 0)}", 'info'))
            self.root.after(0, lambda: self.log(f"  Найдено проблем: {scan_results.get('total_issues', 0)}", 'info'))
            
            # Генерация отчёта
            source_name = Path(self.source_dir_var.get()).name
            output_path = Path(config['paths']['logs_dir']) / f'scan_report_{source_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            scanner.generate_report(output_path)
            
            self.root.after(0, lambda: self.log(f"\n[2/3] Результаты сканирования:", 'info'))
            self.root.after(0, lambda: self.log(f"  Найдено *.plp файлов: {scan_results.get('files_scanned', 0)}", 'info'))
            self.root.after(0, lambda: self.log(f"  Проблемных конструкций: {scan_results.get('total_issues', 0)}", 'info'))
            
            self.root.after(0, lambda: self.log(f"\n[3/3] Проблемы по типам:", 'info'))
            for issue_type, count in scan_results.get('by_type', {}).items():
                self.root.after(0, lambda t=issue_type, c=count: self.log(f"  {t}: {c}", 'info'))
            
            # Вывод AI-результатов
            if scanner.ai_results:
                self.root.after(0, lambda: self.log(f"\n[AI-АНАЛИЗ] Результаты анализа сложных правил:", 'highlight'))
                self.root.after(0, lambda: self.log(f"  Всего проанализировано: {len(scanner.ai_results)}", 'info'))
                for ai_result in scanner.ai_results[:10]:  # Показываем первые 10
                    self.root.after(0, 
                        lambda r=ai_result: self.log(
                            f"  [{r.rule_code}] строка {r.line_number}: {r.steps_summary} ({r.confidence:.0%})", 
                            'warning'
                        )
                    )
                if len(scanner.ai_results) > 10:
                    self.root.after(0, 
                        lambda: self.log(f"  ... и ещё {len(scanner.ai_results) - 10} результатов", 'info')
                    )
            
            self.root.after(0, lambda: self.log(f"\nОтчёт сохранён: {output_path}", 'info'))
            
            self.root.after(0, lambda: self.progress.config(value=100))
            self.root.after(0, lambda: self.progress_label.config(text="100%"))
            
            self.root.after(0, lambda: self._log_separator("СКАНИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО"))
            self.root.after(0, lambda: self.set_status("Готово"))
            
            # Показываем результаты
            self.root.after(0, lambda: self.btn_scan.state(['!disabled']))
            self.root.after(0, lambda: self.btn_fix.state(['!disabled']))
            self.root.after(0, lambda: self.btn_show_sql.state(['!disabled']))
            
            # Сохраняем результаты сканирования для кнопки "Показать SQL для ручного исправления"
            self.scan_results = {
                'scanner': scanner,
                'issues': scanner.issues,
                'stats': scan_results
            }
            
            self.root.after(0, 
                lambda: messagebox.showinfo("Сканирование завершено", 
                          f"Найдено *.plp файлов: {scan_results.get('files_scanned', 0)}\n"
                          f"Проблемных конструкций: {scan_results.get('total_issues', 0)}\n"
                          f"С AI-анализом: {len(scanner.ai_results)}\n"
                          f"Отчёт: {output_path}")
            )
            
        except Exception as e:
            self.log(f"[!] Ошибка сканирования: {e}", 'error')
            messagebox.showerror("Ошибка", f"Сканирование завершилось с ошибкой:\n{e}")
    
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
        if not self.source_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите исходный каталог!")
            return
        
        # Проверяем наличие каталога результатов
        if not self.result_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите каталог результатов!")
            return
        
        result_path = Path(self.result_dir_var.get())
        source_path = Path(self.source_dir_var.get())
        
        # Автоматическое формирование полного пути к каталогу результатов
        # Если исходный PATCH_IN/xxx, а результат PATCH_OUT - добавляем подкаталог xxx
        source_name = source_path.name
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
        thread = threading.Thread(target=self._run_fix, daemon=True)
        thread.start()
    
    def _run_fix(self):
        """Рабочая функция исправления (вызывается в отдельном потоке)"""
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
                self.root.after(0, lambda: self.progress.config(value=5))
                self.root.after(0, lambda: self.progress_label.config(text="5%"))
            
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
                    'exclude_patterns': ['.v????', '.bak', '.tmp']
                },
                'output': {
                    'only_modified': self.only_modified_var.get(),
                    'preserve_structure': self.preserve_structure_var.get()
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
            
            # Определение выбранных правил
            selected_rules = [code for code, var in self.selected_rules.items() if var.get()]
            self.root.after(0, lambda: self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА ({len(selected_rules)}):", 'info'))
            for rule in selected_rules:
                self.root.after(0, lambda r=rule: self.log(f"  [+] {r}", 'info'))
            
            # Загрузка рубрикатора если ещё не загружен
            if not self.rubricator_loaded:
                self.root.after(0, self.load_rubricator_on_start)
            
            # Сброс прогресса
            self.root.after(0, lambda: self.progress.config(value=0))
            self.root.after(0, lambda: self.progress_label.config(text="0%"))
            
            # Логирование вызова Парсера SQL (ПЕРЕД созданием сканера)
            self.log("\n[ПАРСЕР SQL] Начало сканирования и анализа...", 'highlight')
            self.log(f"  Источник: {source_dir}", 'debug')
            self.log(f"  Правила: {len(selected_rules)}", 'debug')
            self.root.update_idletasks()  # Принудительное обновление GUI
            
            # Создание сканера
            from analyzer.scanner import PLPlusScanner
            scanner = PLPlusScanner(config, selected_rules)
            
            # Callback для вывода в журнал
            def scan_log(message, level='info'):
                self.root.after(0, lambda m=message, l=level: self.log(m, l))
            
            # Сканирование
            scan_results = scanner.scan_directory(log_callback=scan_log)
            
            self.root.after(0, lambda: self.progress.config(value=40))
            self.root.after(0, lambda: self.progress_label.config(text="40%"))
            
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
                self.root.after(0, lambda: self.progress.config(value=0))
                self.root.after(0, lambda: self.progress_label.config(text="0%"))
                self.root.after(0, lambda: self.set_status("Готово"))
                self.root.after(0, lambda: self._log_separator("ИСПРАВЛЕНИЕ КОДА ЗАВЕРШЕНО (проблем не найдено)"))
                self.root.after(0, lambda: self.btn_scan.state(['!disabled']))
                self.root.after(0, lambda: self.btn_fix.state(['!disabled']))
                return
            
            # Создание фиксера
            from fixer.code_fixer import PLPlusFixer
            iteration = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = source_dir.name
            fixer = PLPlusFixer(config, iteration)
            
            self.root.after(0, lambda: self.progress.config(value=50))
            self.root.after(0, lambda: self.progress_label.config(text="50%"))
            
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
            
            # Передаём callback для вывода в журнал
            files_modified = fixer.fix_directory(scanner, final_results_dir, 
                                                 log_callback=scan_log, 
                                                 log_level=self.log_level_var.get())
            
            self.root.after(0, lambda: self.progress.config(value=75))
            self.root.after(0, lambda: self.progress_label.config(text="75%"))
            
            # Сохранение лога
            self.root.after(0, lambda: self.log("\n[3/5] Сохранение лога...", 'info'))
            log_path = Path(config['paths']['logs_dir']) / f'fix_log_{source_name}_{iteration}.md'
            fixer.save_log(log_path)
            
            self.root.after(0, lambda: self.progress.config(value=90))
            self.root.after(0, lambda: self.progress_label.config(text="90%"))
            
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
            
            self.root.after(0, lambda: self.progress.config(value=100))
            self.root.after(0, lambda: self.progress_label.config(text="100%"))
            
            self.root.after(0, lambda: self._log_separator("ИСПРАВЛЕНИЕ КОДА ЗАВЕРШЕНО УСПЕШНО"))
            self.root.after(0, lambda: self.set_status("Готово"))
            self.root.after(0, lambda: self.btn_scan.state(['!disabled']))
            self.root.after(0, lambda: self.btn_fix.state(['!disabled']))
            self.root.after(0, lambda: self.btn_show_sql.state(['!disabled']))
            
            # Сохраняем результаты сканирования для кнопки "Показать SQL для ручного исправления"
            self.scan_results = {
                'scanner': scanner,
                'issues': scanner.issues,
                'stats': scan_results
            }
            
            # Обновить состояние кнопок после исправления
            self.root.after(0, self._update_buttons_state)
            
            # Проверка условий для архивации
            should_archive = (
                self.preserve_structure_var.get()
            )
            
            if should_archive:
                # Запуск архивации
                self.root.after(0, lambda: self._run_archive(final_results_dir, source_dir))
            
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
    
    def _run_archive(self, results_dir: Path, source_dir: Path):
        """Рабочая функция архивации (вызывается в главном потоке)"""
        try:
            self.root.after(0, lambda: self.log("\n[5/5] Архивация результатов...", 'info'))
            self.root.after(0, lambda: self.progress.config(value=95))
            self.root.after(0, lambda: self.progress_label.config(text="95%"))
            
            archive_path = results_dir.parent / f"{results_dir.name}.zip"
            
            # Создаём архив
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(results_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(results_dir.parent)
                        zipf.write(file_path, arcname)
                        self.root.after(0, lambda f=file: self.log(f"  Добавлен: {f}", 'debug'))
            
            # Копируем .pck файл из исходного каталога в архив
            source_pck = source_dir / f"{source_dir.name}.pck"
            if source_pck.exists():
                archive_pck_path = results_dir.parent / f"{results_dir.name}.pck"
                if not archive_pck_path.exists():
                    shutil.copy2(source_pck, archive_pck_path)
                    self.root.after(0, lambda: self.log(f"  Копирован .pck файл в архив: {source_pck.name}", 'info'))
                else:
                    self.root.after(0, lambda: self.log(f"  .pck файл для архива уже существует, пропущен", 'info'))
                # Добавляем .pck в архив
                with zipfile.ZipFile(archive_path, 'a') as zipf:
                    zipf.write(archive_pck_path, f"{results_dir.name}.pck")
                    self.root.after(0, lambda: self.log(f"  Добавлен .pck в архив", 'info'))
            else:
                self.root.after(0, lambda: self.log(f"  .pck файл не найден в источнике: {source_pck}", 'warning'))
            
            # ДОПОЛНИТЕЛЬНО: Проверка и копирование .pck файла в родительский каталог результатов
            # .pck файл должен быть в PATCH_OUT, а не в PATCH_OUT/patch_RV
            result_pck_dir = results_dir.parent  # PATCH_OUT
            result_pck = result_pck_dir / f"{source_dir.name}.pck"
            if source_pck.exists():
                if not result_pck.exists():
                    try:
                        shutil.copy2(source_pck, result_pck)
                        self.root.after(0, lambda: self.log(f"  Копирован .pck файл в {result_pck_dir}: {result_pck.name}", 'info'))
                    except Exception as e:
                        self.root.after(0, lambda err=e: self.log(f"  Ошибка копирования .pck в {result_pck_dir}: {err}", 'error'))
                else:
                    self.root.after(0, lambda: self.log(f"  .pck файл в {result_pck_dir} уже существует, пропущен", 'info'))
            else:
                self.root.after(0, lambda: self.log(f"  .pck файл не найден в исходном каталоге", 'debug'))
            
            self.root.after(0, lambda: self.progress.config(value=100))
            self.root.after(0, lambda: self.progress_label.config(text="100%"))
            
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
        # Проверка: выбран ли хотя бы один файл в рубрикаторе
        any_rule_selected = any(var.get() for var in self.selected_rules.values())
        if not any_rule_selected:
            messagebox.showerror("Ошибка", "Выберите хотя бы один файл в рубрикаторе!")
            return
        
        # Запускаем генерацию в отдельном потоке
        thread = threading.Thread(target=self._run_test_generation, daemon=True)
        thread.start()
    
    def _run_test_generation(self):
        """Рабочая функция генерации тестовых файлов"""
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
                
                self.root.after(0, lambda: self.log("Использование нового генератора тестов...", 'info'))
                generator = TestGenerator(self.rubricator_dir)
                
                # Получаем выбранные правила
                selected_rules = [code for code, var in self.selected_rules.items() if var.get()]
                
                if not selected_rules:
                    self.root.after(0, lambda: self.log("Нет выбранных правил", 'warning'))
                    self.root.after(0, lambda: self.set_status("Готово"))
                    return
                
                # Генерируем файлы
                files_created = 0
                for rule_code in selected_rules:
                    self.root.after(0, lambda c=rule_code: self.log(f"Генерация для правила: {c}", 'info'))
                    
                    try:
                        file_path = generator.generate_test_file(rule_code, test_dir)
                        if file_path:
                            files_created += 1
                            self.root.after(0, lambda f=file_path.name: self.log(f"  ✅ Создан: {f}", 'success'))
                        else:
                            self.root.after(0, lambda c=rule_code: self.log(f"  ⚠️ Не удалось сгенерировать: {c}", 'warning'))
                    except Exception as e:
                        self.root.after(0, lambda c=rule_code, e=str(e): self.log(f"  ❌ Ошибка для {c}: {e}", 'error'))
                
                self.root.after(0, lambda: self._log_separator("ГЕНЕРАЦИЯ ЗАВЕРШЕНА"))
                self.root.after(0, lambda: self.log(f"\nСоздано тестовых файлов: {files_created}", 'info'))
                self.root.after(0, lambda: self.set_status("Готово"))
                
                self.root.after(0, 
                    lambda: messagebox.showinfo("Генерация завершена", 
                              f"Создано тестовых файлов: {files_created}\n\n"
                              f"Каталог: {test_dir}"))
                
            except ImportError as e:
                self.root.after(0, lambda: self.log(f"[!] Ошибка импорта TestGenerator: {e}", 'error'))
                self.root.after(0, lambda: self.set_status("Готово"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.log(f"[!] Ошибка генерации: {error_msg}", 'error'))
            self.root.after(0, lambda: self.set_status("Готово"))
    
    def _run_test_generation_legacy(self, test_dir: Path):
        """Генерация тестовых файлов по старому алгоритму (из 3.RUBRICATOR_FIXES.md)"""
        try:
            # Загружаем данные из 3.RUBRICATOR_FIXES.md
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
        """Загрузка данных об исправлениях из 3.RUBRICATOR_FIXES.md"""
        fixes = []
        try:
            file_path = self.rubricator_dir / '3.RUBRICATOR_FIXES.md'
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
            lines.append(f"-- Всего проблем: {len(issues)}")
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
            self.log(f"Всего проблем: {len(issues)}", 'info')
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
            
            # Вывод 1.RUBRICATOR_FILES.md с актуальными значениями "+/-"
            file_path = self.rubricator_dir / '1.RUBRICATOR_FILES.md'
            if file_path.exists():
                self.log(f"# {file_path}", 'info')
                self.log("# Рубрикатор: перечень файлов (с учетом текущего выбора)", 'info')
                self.log("+--+--+--------------+------------------------------------------------------------------------", 'info')
                self.log("|N|+/-|Код файла     |Имя файла", 'info')
                self.log("+--+--+--------------+------------------------------------------------------------------------", 'info')
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
                
                self.log("", 'info')
            
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
                self.log("", 'info')
                    
            # Вывод 3.RUBRICATOR_FIXES.md
            file_path = self.rubricator_dir / '3.RUBRICATOR_FIXES.md'
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
                    
                    self.log("", 'info')
            
            self.log("ВЫБРАННЫЕ ПРАВИЛА:", 'info')
            selected_count = 0
            for code, var in self.selected_rules.items():
                if var.get():
                    selected_count += 1
                    self.log(f"  [+] {code}: ВКЛ", 'info')
            
            self.log(f"\nВсего выбрано правил: {selected_count}", 'info')
            
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
