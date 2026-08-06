#!/usr/bin/env python3
"""
АРМ "Адаптация под DBI" v26.2.001
Графический интерфейс для миграции PLPlus кода на DBI
Версия: 2026 2-й квартал (апрель-июнь), версия 001
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, Menu
from pathlib import Path
import json
import os
from datetime import datetime
import threading


class DBIMigrationApp:
    """Основное приложение"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("АРМ 'Адаптация под DBI' v26.2.001")
        self.root.geometry("1400x900")
        
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
        
        # Выбранные правила
        self.selected_rules = {}
        self.rule_checkboxes = {}  # Для доступа к виджетов
        
        # Ссылки на поля ввода для привязки событий
        self.source_entry = None
        self.result_entry = None
        
        # Создаём главное меню
        self._create_menu()
        
        # Создаём интерфейс
        self._create_widgets()
        
        # Загрузка настроек
        self.load_settings()
        
        # Привязка событий для поля ввода
        self._bind_entry_events()
    
    def _create_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
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
        self.root.bind('<F6>', lambda e: self.start_fix())
    
    def _create_widgets(self):
        """Создание виджетов"""
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
        
        # Секция 1 - Пути и настройки сканирования (ОБЪЕДИНЕНЫ)
        paths_frame = ttk.LabelFrame(scrollable_frame, text="1. Пути и настройки сканирования", padding="10")
        paths_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Пути к каталогам
        ttk.Label(paths_frame, text="Исходный каталог:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.source_entry = ttk.Entry(paths_frame, textvariable=self.source_dir_var, width=60)
        self.source_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        ttk.Button(paths_frame, text="...", command=self.browse_source, width=3).grid(row=0, column=2, padx=5)
        
        ttk.Label(paths_frame, text="Каталог результатов:").grid(row=0, column=3, sticky=tk.W, padx=5)
        self.result_entry = ttk.Entry(paths_frame, textvariable=self.result_dir_var, width=60)
        self.result_entry.grid(row=0, column=4, padx=5, sticky=tk.EW)
        ttk.Button(paths_frame, text="...", command=self.browse_result, width=3).grid(row=0, column=5, padx=5)
        
        # Настройки сканирования
        ttk.Label(paths_frame, text="Шаблон:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(paths_frame, textvariable=self.file_pattern_var, width=30).grid(row=1, column=1, padx=5, sticky=tk.W)
        ttk.Checkbutton(paths_frame, text="Сканировать подкаталоги", variable=self.scan_recursive_var).grid(row=1, column=2, padx=20, sticky=tk.W)
        
        paths_frame.grid_columnconfigure(1, weight=1)
        paths_frame.grid_columnconfigure(4, weight=1)
        
        # Секция 2 - Рубрикатор
        rules_frame = ttk.LabelFrame(scrollable_frame, text="2. Рубрикатор. Выбор корректировок", padding="10")
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Загрузка файлов рубрикатора
        self._load_rubricator_files()
        
        # Treeview с прокруткой
        tree_scroll_y = ttk.Scrollbar(rules_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(rules_frame, orient=tk.HORIZONTAL)
        
        self.rules_tree = ttk.Treeview(rules_frame, 
                                       yscrollcommand=tree_scroll_y.set, 
                                       xscrollcommand=tree_scroll_x.set,
                                       show='headings')  # Без колонки #0 (иконки)
        
        tree_scroll_y.config(command=self.rules_tree.yview)
        tree_scroll_x.config(command=self.rules_tree.xview)
        
        # Настройка колонок: Выбрано | Код файла | Полное имя файла
        self.rules_tree['columns'] = ('selected', 'code', 'name')
        self.rules_tree.column('selected', width=80, minwidth=80, anchor=tk.CENTER)
        self.rules_tree.column('code', width=150, minwidth=100, anchor=tk.W)
        self.rules_tree.column('name', width=600, minwidth=400, anchor=tk.W)
        
        # Заголовки
        self.rules_tree.heading('selected', text='Выбрано', anchor=tk.CENTER)
        self.rules_tree.heading('code', text='Код файла', anchor=tk.W)
        self.rules_tree.heading('name', text='Полное имя файла', anchor=tk.W)
        
        # Размещаем Treeview и скроллы
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.rules_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Заполняем Treeview
        self._populate_rules_tree()
        
        # Секция 3 - Опции сканирования и исправления. Логирование (ОБЪЕДИНЕНЫ)
        options_frame = ttk.LabelFrame(scrollable_frame, text="3. Опции сканирования и исправления. Логирование", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Опции вывода
        ttk.Checkbutton(options_frame, text="Только модифицированные файлы", 
                       variable=self.only_modified_var).grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Checkbutton(options_frame, text="Сохранить структуру каталогов", 
                       variable=self.preserve_structure_var).grid(row=0, column=1, sticky=tk.W, padx=20)
        
        # Уровень логирования
        ttk.Label(options_frame, text="Уровень:").grid(row=0, column=2, sticky=tk.W, padx=30)
        ttk.Combobox(options_frame, textvariable=self.log_level_var, 
                    values=["Минимальный", "Подробный"], 
                    state="readonly", width=15).grid(row=0, column=3, padx=5, sticky=tk.W)
        
        # Панель управления
        control_frame = ttk.Frame(scrollable_frame, padding="10")
        control_frame.pack(fill=tk.X)
        
        self.btn_scan = ttk.Button(control_frame, text="🔍 Сканировать", command=self.start_scan, width=20)
        self.btn_scan.pack(side=tk.LEFT, padx=5)
        
        self.btn_fix = ttk.Button(control_frame, text="✏️ Исправить код", command=self.start_fix, width=20)
        self.btn_fix.pack(side=tk.LEFT, padx=5)
        
        self.btn_rubricator = ttk.Button(control_frame, text="📖 Открыть рубрикатор", command=self.open_rubricator, width=25)
        self.btn_rubricator.pack(side=tk.LEFT, padx=5)
        
        # Журнал выполнения
        journal_frame = ttk.LabelFrame(scrollable_frame, text="Журнал выполнения", padding="10")
        journal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Журнал с вертикальной и горизонтальной прокруткой
        log_scroll_y = ttk.Scrollbar(journal_frame, orient=tk.VERTICAL)
        log_scroll_x = ttk.Scrollbar(journal_frame, orient=tk.HORIZONTAL)
        
        self.log_text = scrolledtext.ScrolledText(journal_frame, 
                                                  wrap=tk.NONE,
                                                  font=('Consolas', 9),
                                                  yscrollcommand=log_scroll_y.set,
                                                  xscrollcommand=log_scroll_x.set,
                                                  height=15)  # Высота под 15 строк
        
        log_scroll_y.config(command=self.log_text.yview)
        log_scroll_x.config(command=self.log_text.xview)
        
        # Размещаем скроллы и журнал
        log_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        log_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Цвета для логов
        self.log_text.tag_configure('info', foreground='black')
        self.log_text.tag_configure('warning', foreground='orange')
        self.log_text.tag_configure('error', foreground='red')
        self.log_text.tag_configure('success', foreground='green')
        self.log_text.tag_configure('debug', foreground='gray')
        
        # Кнопки управления журналом (ПОД полем журнала)
        journal_buttons = ttk.Frame(journal_frame)
        journal_buttons.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        ttk.Button(journal_buttons, text="🗑️ Очистить журнал", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(journal_buttons, text="📋 Копировать", command=self.copy_log).pack(side=tk.LEFT, padx=5)
        
        # Индикатор выполнения (под журналом) - процент в той же строке
        progress_frame = ttk.Frame(scrollable_frame, padding="10")
        progress_frame.pack(fill=tk.X)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_label = ttk.Label(progress_frame, text="0%", width=10)
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        # Подвал (статус-бар)
        self.status_bar = ttk.Label(scrollable_frame, text="", relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        self.status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    def _load_rubricator_files(self):
        """Загрузка информации о файлах рубрикатора"""
        try:
            file_path = self.rubricator_dir / '1.RUBRICATOR_FILES.md'
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if '|' in line and not line.startswith('|---'):
                            parts = [p.strip() for p in line.split('|')]
                            if len(parts) >= 3:
                                code = parts[1] if len(parts) > 1 else ''
                                name = parts[2] if len(parts) > 2 else ''
                                if code and not code.startswith('№'):
                                    self.rubricator_files[code] = name
        except Exception as e:
            print(f"Ошибка загрузки файлов рубрикатора: {e}")
    
    def _populate_rules_tree(self):
        """Заполнение Treeview правилами"""
        # Очищаем дерево
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        
        # Загружаем правила из рубрикатора
        rules = self._load_rules()
        
        for code, description in rules.items():
            # Получаем полное имя из 1.RUBRICATOR_FILES.md
            full_name = self.rubricator_files.get(code, description)
            
            # Создаём переменную для чекбокса
            var = tk.BooleanVar(value=True)
            self.selected_rules[code] = var
            
            # Вставляем в дерево (без иконки)
            item_id = self.rules_tree.insert('', tk.END, 
                                            values=('✓', code, full_name))
            self.rule_checkboxes[code] = (item_id, var)
        
        # Обработчик клика для переключения чекбокса
        self.rules_tree.bind('<Button-1>', self._on_rule_click)
    
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
                    self.log(f"Правило {code}: {'включено' if var.get() else 'выключено'}", 'debug')
                    break
    
    def _bind_entry_events(self):
        """Привязка событий для поля ввода - логирование только при потере фокуса"""
        # Привязываем события потери фокуса для полей ввода
        if self.source_entry:
            self.source_entry.bind('<FocusOut>', self._on_source_focus_out)
        if self.result_entry:
            self.result_entry.bind('<FocusOut>', self._on_result_focus_out)
    
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
            self.source_dir_var.set(directory)
            # Логирование только при потере фокуса, здесь - мгновенно
            self.log(f"Исходный каталог: {directory}", 'info')
    
    def browse_result(self):
        """Выбор каталога результатов"""
        directory = filedialog.askdirectory()
        if directory:
            self.result_dir_var.set(directory)
            # Логирование только при потере фокуса, здесь - мгновенно
            self.log(f"Каталог результатов: {directory}", 'info')
    
    def log(self, message: str, level: str = 'info'):
        """Добавление сообщения в журнал"""
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n", level)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """Очистка журнала"""
        self.log_text.delete('1.0', tk.END)
        self.log("Журнал очищен", 'info')
    
    def copy_log(self):
        """Копирование журнала в буфер"""
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
                self.log("Настройки загружены", 'info')
            except Exception as e:
                self.log(f"Ошибка загрузки настроек: {e}", 'error')
        else:
            self.log("Настройки не найдены. Используются значения по умолчанию", 'info')
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        settings_path = Path(__file__).parent / 'settings.json'
        settings = {
            'source_dir': self.source_dir_var.get(),
            'result_dir': self.result_dir_var.get(),
            'file_pattern': self.file_pattern_var.get(),
            'log_level': self.log_level_var.get(),
            'recursive': self.scan_recursive_var.get(),
            'only_modified': self.only_modified_var.get(),
            'preserve_structure': self.preserve_structure_var.get()
        }
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.log("Настройки сохранены", 'success')
        except Exception as e:
            self.log(f"Ошибка сохранения настроек: {e}", 'error')
    
    def show_project_structure(self):
        """Показ структуры проекта"""
        self.log("\n" + "="*80, 'info')
        self.log("СТРУКТУРА ПРОЕКТА", 'info')
        self.log("="*80, 'info')
        
        project_root = Path(__file__).parent.parent
        for item in project_root.rglob('*'):
            if not item.name.startswith('.') and item.is_file():
                rel_path = item.relative_to(project_root)
                self.log(f"  📄 {rel_path}", 'info')
    
    def show_documentation(self):
        """Показ документации"""
        self.log("\n" + "="*80, 'info')
        self.log("ДОКУМЕНТАЦИЯ", 'info')
        self.log("="*80, 'info')
        
        docs_path = Path(__file__).parent / 'AI_DOCS'
        if docs_path.exists():
            for doc_file in docs_path.glob('*.txt'):
                self.log(f"  📖 {doc_file.name}", 'info')
                self.log(f"     Полный путь: {doc_file}", 'debug')
        else:
            self.log("  [!] Документация не найдена", 'warning')
    
    def set_status(self, message: str):
        """Установка сообщения в подвале"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
        
    def show_about(self):
        """Показ информации о программе"""
        messagebox.showinfo(
            "О программе",
            "АРМ 'Адаптация под DBI' v26.2.001\n\n"
            "Автоматизированное рабочее место для миграции\n"
            "PLPlus-кода с Oracle на PostgreSQL (2MCA DBI).\n\n"
            "Разработчик: NLP-Core-Team\n"
            f"Дата: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            "Версия: 2026 2-й квартал (апрель-июнь), версия 001"
        )
        self.log("Открыто окно 'О программе'", 'info')
    
    def load_rubricator_on_start(self):
        """Загрузка рубрикатора при запуске"""
        self.set_status("Загрузка рубрикатора...")
        self.log("Загрузка рубрикатора...", 'info')
        
        if not self.rubricator_dir.exists():
            self.log(f"[!] Каталог рубрикатора не найден: {self.rubricator_dir}", 'error')
            self.set_status("Готов")
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
        
        self.set_status("Готов")
    
    def start_scan(self):
        """Запуск сканирования"""
        if not self.source_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите исходный каталог!")
            return
        
        self.set_status("Сканирование...")
        self.log("\n" + "=" * 80, 'info')
        self.log("НАЧАЛО СКАНИРОВАНИЯ", 'info')
        self.log("=" * 80, 'info')
        
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
        self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА ({len(selected_rules)}):", 'info')
        for rule in selected_rules:
            self.log(f"  [+] {rule}", 'info')
        
        # Загрузка рубрикатора если ещё не загружен
        if not self.rubricator_loaded:
            self.load_rubricator_on_start()
        
        # Сброс прогресса
        self.progress.config(value=0)
        self.progress_label.config(text="0%")
        self.root.update_idletasks()
        
        # Создание сканера
        from analyzer.scanner import PLPlusScanner
        scanner = PLPlusScanner(config, selected_rules)
        
        self.progress.config(value=10)
        self.progress_label.config(text="10%")
        self.root.update_idletasks()
        
        scan_results = scanner.scan_directory()
        
        self.log(f"\n[1/3] Сканирование файлов...", 'info')
        self.log(f"  Найдено файлов: {scan_results.get('files_scanned', 0)}", 'info')
        self.log(f"  Проблемных конструкций: {scan_results.get('total_issues', 0)}", 'info')
        
        # При уровне "Подробный" выводим детали сканирования
        if self.log_level_var.get() == 'Подробный':
            self.log("\n  Найденные файлы:", 'info')
            issues_by_file = scanner.get_issues_by_file()
            
            fix_descriptions = {}
            if self.rubricator_loaded:
                from fixer.markdown_rubricator_loader import MarkdownRubricatorLoader
                rubricator = MarkdownRubricatorLoader(str(self.rubricator_dir))
                for fix in rubricator.get_enabled_fixes():
                    fix_descriptions[fix.code] = fix.short_description.replace('`', '')
            
            for file_path, issues in issues_by_file.items():
                full_path = Path(self.source_dir_var.get()) / file_path
                self.log(f"    📄 {full_path} ({len(issues)} проблем)", 'info')
                for issue in issues:
                    short_desc = fix_descriptions.get(issue.issue_type, issue.issue_type)
                    self.log(f"      [{issue.issue_type}] {short_desc}", 'info')
                    self.log(f"        Строка {issue.line_number}: {issue.original_code[:100]}", 'info')
        
        self.progress.config(value=50)
        self.progress_label.config(text="50%")
        self.root.update_idletasks()
        
        # Генерация отчёта
        source_name = Path(self.source_dir_var.get()).name
        output_path = Path(config['paths']['logs_dir']) / f'scan_report_{source_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        scanner.generate_report(output_path)
        
        self.log(f"\n[2/3] Результаты сканирования:", 'info')
        self.log(f"  Найдено файлов: {scan_results.get('files_scanned', 0)}", 'info')
        self.log(f"  Проблемных конструкций: {scan_results.get('total_issues', 0)}", 'info')
        
        self.log(f"\n[3/3] Проблемы по типам:", 'info')
        for issue_type, count in scan_results.get('by_type', {}).items():
            self.log(f"  {issue_type}: {count}", 'info')
        
        self.log(f"\nОтчёт сохранён: {output_path}", 'info')
        
        self.progress.config(value=100)
        self.progress_label.config(text="100%")
        self.root.update_idletasks()
        
        self.log("\n" + "=" * 80, 'success')
        self.log("СКАНИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО", 'success')
        self.log("=" * 80, 'success')
        
        self.set_status("Готов")
        
        messagebox.showinfo("Сканирование завершено", 
                          f"Найдено файлов: {scan_results.get('files_scanned', 0)}\n"
                          f"Проблемных конструкций: {scan_results.get('total_issues', 0)}\n\n"
                          f"Отчёт: {output_path}")
    
    def start_fix(self):
        """Запуск исправления кода"""
        if not self.source_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите исходный каталог!")
            return
        
        if not self.result_dir_var.get():
            messagebox.showerror("Ошибка", "Укажите каталог результатов!")
            return
        
        self.set_status("Исправление кода...")
        self.log("\n" + "=" * 80, 'info')
        self.log("НАЧАЛО ИСПРАВЛЕНИЯ КОДА", 'info')
        self.log("=" * 80, 'info')
        
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
        self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА ({len(selected_rules)}):", 'info')
        for rule in selected_rules:
            self.log(f"  [+] {rule}", 'info')
        
        # Загрузка рубрикатора если ещё не загружен
        if not self.rubricator_loaded:
            self.load_rubricator_on_start()
        
        # Сброс прогресса
        self.progress.config(value=0)
        self.progress_label.config(text="0%")
        self.root.update_idletasks()
        
        # Создание сканера
        from analyzer.scanner import PLPlusScanner
        scanner = PLPlusScanner(config, selected_rules)
        
        self.log("\n[1/4] Сканирование файлов...", 'info')
        self.progress.config(value=10)
        self.progress_label.config(text="10%")
        self.root.update_idletasks()
        
        scan_results = scanner.scan_directory()
        
        self.log(f"  Найдено файлов: {scan_results.get('files_scanned', 0)}", 'info')
        self.log(f"  Проблемных конструкций: {scan_results.get('total_issues', 0)}", 'info')
        
        if scan_results.get('total_issues', 0) == 0:
            self.log("\n[!] Проблем не найдено. Исправление не требуется.", 'warning')
            self.progress.config(value=0)
            self.progress_label.config(text="0%")
            self.set_status("Готов")
            
            self.log("=" * 80, 'warning')
            self.log("ИСПРАВЛЕНИЕ КОДА ЗАВЕРШЕНО (проблем не найдено)", 'warning')
            self.log("=" * 80, 'warning')
            return
        
        # Создание фиксера
        from fixer.code_fixer import PLPlusFixer
        iteration = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_name = Path(self.source_dir_var.get()).name
        fixer = PLPlusFixer(config, iteration)
        
        self.log("\n[2/4] Применение исправлений...", 'info')
        self.progress.config(value=40)
        self.progress_label.config(text="40%")
        self.root.update_idletasks()
        
        results_dir = Path(config['paths']['results_dir']) / f"{source_name}_v{iteration}"
        results_dir.mkdir(parents=True, exist_ok=True)
        self.log(f"  Каталог результатов: {results_dir}", 'info')
        
        # Передаём callback для вывода в журнал
        files_modified = fixer.fix_directory(scanner, results_dir, log_callback=self.log, log_level=self.log_level_var.get())
        
        self.progress.config(value=75)
        self.progress_label.config(text="75%")
        self.root.update_idletasks()
        
        # Сохранение лога
        self.log("\n[3/4] Сохранение лога...", 'info')
        log_path = Path(config['paths']['logs_dir']) / f'fix_log_{source_name}_{iteration}.md'
        fixer.save_log(log_path)
        
        self.progress.config(value=90)
        self.progress_label.config(text="90%")
        self.root.update_idletasks()
        
        # Вывод результатов
        self.log("\n[4/4] Финализация...", 'info')
        self.log(f"\nРЕЗУЛЬТАТЫ:", 'info')
        self.log(f"  Обработано файлов: {scan_results.get('files_scanned', 0)}", 'info')
        self.log(f"  Исправлено конструкций: {scan_results.get('total_issues', 0)}", 'info')
        self.log(f"  Создано файлов: {files_modified}", 'info')
        self.log(f"  Результаты: {results_dir}", 'info')
        self.log(f"  Лог: {log_path}", 'info')
        
        self.progress.config(value=100)
        self.progress_label.config(text="100%")
        self.root.update_idletasks()
        
        self.log("\n" + "=" * 80, 'success')
        self.log("ИСПРАВЛЕНИЕ КОДА ЗАВЕРШЕНО УСПЕШНО", 'success')
        self.log("=" * 80, 'success')
        
        self.set_status("Готов")
        
        messagebox.showinfo("Исправление завершено", 
                          f"Обработано файлов: {scan_results.get('files_scanned', 0)}\n"
                          f"Исправлено конструкций: {scan_results.get('total_issues', 0)}\n"
                          f"Создано файлов: {files_modified}\n\n"
                          f"Результаты: {results_dir}")
    
    def open_rubricator(self):
        """Открытие рубрикатора"""
        self.set_status("Открытие рубрикатора...")
        self.log("\n" + "="*80, 'info')
        self.log("-= ОТКРЫТИЕ РУБРИКАТОРА =-", 'info')
        self.log("", 'info')
        
        try:
            if not self.rubricator_loaded:
                self.load_rubricator_on_start()
            else:
                selected_codes = {code for code, var in self.selected_rules.items() if var.get()}
                
                # Вывод 1.RUBRICATOR_FILES.md
                file_path = self.rubricator_dir / '1.RUBRICATOR_FILES.md'
                if file_path.exists():
                    self.log(f"# {file_path}", 'info')
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.strip().split('\n')
                        for line in lines[:50]:
                            self.log(line, 'info')
                    self.log("", 'info')
                
                # Вывод 2.RUBRICATOR_CATEGORIES.md
                file_path = self.rubricator_dir / '2.RUBRICATOR_CATEGORIES.md'
                if file_path.exists():
                    self.log(f"# {file_path}", 'info')
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.strip().split('\n')
                        for line in lines[:50]:
                            self.log(line, 'info')
                    self.log("", 'info')
                
                # Вывод 3.RUBRICATOR_FIXES.md
                file_path = self.rubricator_dir / '3.RUBRICATOR_FIXES.md'
                if file_path.exists():
                    self.log(f"# {file_path}", 'info')
                    self.log("# Рубрикатор: перечень исправлений (с учетом выбранных правил)", 'info')
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.strip().split('\n')
                        
                        for line in lines[2:]:
                            if not line.strip():
                                continue
                            
                            if '|---' in line:
                                self.log(line, 'info')
                                continue
                            
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
                
        except Exception as e:
            self.log(f"[!] Ошибка открытия рубрикатора: {str(e)}", 'error')
    
        self.set_status("Готов")
    
    def on_close(self):
        """Закрытие приложения"""
        self.save_settings()
        self.log("Настройки сохранены. Приложение закрывается...", 'info')
        self.root.destroy()


def main():
    """Точка входа приложения"""
    print("Запуск АРМ 'Адаптация под DBI' v26.2.001...")
    root = tk.Tk()
    
    app = DBIMigrationApp(root)
    
    # Обработка закрытия
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    
    root.mainloop()
    print("Приложение закрыто")


if __name__ == '__main__':
    main()
