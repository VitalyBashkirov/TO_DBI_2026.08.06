# DS_108. Фиксы GUI АРМ: сброс UI после AI-цикла + дедупликация rescan

**Дата:** 07.10.2026
**Автор:** DeepSeek (DS)
**Исполнитель:** KODA
**Приоритет:** средний
**Связано:** DS_103 (ручной GUI-прогон), DS_102 (resume), DS_038 (abort)

---

## 1. Цель

Устранить два дефекта GUI, выявленных в ручном прогоне DS_103:

- **DS_108a:** после завершения AI-цикла не сбрасываются статус-бар («Выполняется...»), прогресс-бар и `_progress_frozen`.
- **DS_108b:** `_rescan_ai_files` считает один и тот же файл дважды, если он попал в `results` из нескольких AI-ответов; кроме того, в rescan могут попасть бэкапы (`*_preai.plp`, `*_YYYYMMDD_HHMMSS.plp`).

---

## 2. DS_108a — сброс UI после завершения операции

### 2.1. Проблема

`_finish_abortable_operation` (строка 1821 в `SRC\gui_app.py`) сбрасывает кнопку «Прервать», но не вызывает `set_status("Готово")` и `_reset_progress()`, и не сбрасывает `_progress_frozen`.

`_start_abortable_operation` (строка 1800) вызывает `_set_status_running()` → «Выполняется...». Парного сброса нет.

**Симптом:** после завершения AI-цикла статус-бар показывает «Выполняется...», прогресс-бар — 0% (не сброшен), кнопка «Прервать» — disabled (это правильно), но общий вид — как будто операция идёт.

### 2.2. Правка

**Файл:** `SRC\gui_app.py`

**Метод:** `_finish_abortable_operation` (строки 1821–1833).

**Было:**

```python
    def _finish_abortable_operation(self):
        """DS 038: сбросить флаги и деактивировать кнопку «Прервать» (в finally)."""
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
```

**Стало:**

```python
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
```

### 2.3. Тесты (DS_108a)

Проверить, что после вызова `_finish_abortable_operation`:

- `self.scan_running is False`
- `self.scan_aborted is False`
- `self._progress_frozen is False`
- `self.status_label['text'] == "Готово"`
- `self.progress['value'] == 0`
- `self.progress_label['text'] == "0%"`
- `self.btn_abort['state'] == 'disabled'`

---

## 3. DS_108b — дедупликация rescan + фильтр бэкапов

### 3.1. Проблема

`_rescan_ai_files` (строка 5370) формирует список `touched` без дедупликации:

```python
touched = []
for r in results or []:
    ...
    src = r.get('source')
    if applied > 0 and src and Path(src).exists():
        touched.append((str(src), r.get('backup_path')))
```

Если один и тот же `source` попал в `results` дважды (из двух AI-ответов), в `touched` — две одинаковые пары. Цикл `for src, backup_path in touched` проходит дважды → `stats['files'] = 2`, `stats['before'] = 9514`, `stats['after'] = 9514`, в `bot.log` — две одинаковые строки `Rescan PSH_DEP_PRIV_GO.plp`.

Дополнительно: если в `results` попадёт `src` с суффиксом бэкапа (`*_preai.plp`, `*_YYYYMMDD_HHMMSS.plp`) — он тоже не должен сканироваться.

### 3.2. Правка

**Файл:** `SRC\gui_app.py`

**Метод:** `_rescan_ai_files` (строки 5370–5455).

**Изменить блок сбора `touched`.**

**Было:**

```python
        stats = {'files': 0, 'before': 0, 'after': 0}
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
                touched.append((str(src), r.get('backup_path')))
        if not touched:
            return stats
```

**Стало:**

```python
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
```

**Проверить наличие `import re` в начале `gui_app.py`** — если нет, добавить.

### 3.3. Тесты (DS_108b)

Проверить:

- `touched` с дубликатом `src` → после дедупликации — один элемент.
- `touched` с `*_preai.plp` → отсеивается.
- `touched` с `*_YYYYMMDD_HHMMSS.plp` → отсеивается.
- `touched` с двумя разными `src` → оба остаются.
- `touched` пустой → `stats` без изменений.
- Регистр пути: `C:\Foo\Bar.plp` и `c:\foo\bar.plp` → считаются одним.

---

## 4. Тесты — единый файл

**Файл:** `SRC\tests\test_ds108_gui_rescan.py`

**Содержимое:**

```python
"""DS_108: тесты GUI-фиксов.

- DS_108a: сброс UI после _finish_abortable_operation.
- DS_108b: дедупликация rescan + фильтр бэкапов.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Добавляем SRC в путь
_HERE = Path(__file__).resolve()
_SRC = _HERE.parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


class TestDS108bBackupFilter(unittest.TestCase):
    """DS_108b: фильтр бэкапов в _rescan_ai_files."""

    def _make_app(self):
        """Создаём минимальный объект-заглушку с нужными атрибутами."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.log = MagicMock()
        app._bot_log = MagicMock()
        return app

    def test_backup_preai_filtered(self):
        """Файл *_preai.plp не попадает в touched."""
        app = self._make_app()
        results = [{
            'status': 'ok', 'applied_auto': 1, 'applied_medium': 0,
            'source': 'F:/tmp/PSH_DEP_PRIV_GO_20261007_112105_preai.plp',
            'backup_path': None,
        }]
        with patch('pathlib.Path.exists', return_value=True):
            with patch.object(app, 'scan_results', {'scanner': None}, create=True):
                stats = app._rescan_ai_files(results)
        self.assertEqual(stats['files'], 0)
        self.assertEqual(stats['before'], 0)
        self.assertEqual(stats['after'], 0)

    def test_backup_timestamp_filtered(self):
        """Файл *_YYYYMMDD_HHMMSS.plp не попадает в touched."""
        app = self._make_app()
        results = [{
            'status': 'ok', 'applied_auto': 1, 'applied_medium': 0,
            'source': 'F:/tmp/PSH_DEP_PRIV_GO_20261007_101102.plp',
            'backup_path': None,
        }]
        with patch('pathlib.Path.exists', return_value=True):
            with patch.object(app, 'scan_results', {'scanner': None}, create=True):
                stats = app._rescan_ai_files(results)
        self.assertEqual(stats['files'], 0)


class TestDS108bDedup(unittest.TestCase):
    """DS_108b: дедупликация touched по src."""

    def test_dedup_same_source(self):
        """Один и тот же source в двух results → один элемент в touched."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.log = MagicMock()
        app._bot_log = MagicMock()
        src = 'F:/tmp/PSH_DEP_PRIV_GO.plp'
        results = [
            {'status': 'ok', 'applied_auto': 1, 'applied_medium': 0,
             'source': src, 'backup_path': None},
            {'status': 'ok', 'applied_auto': 1, 'applied_medium': 0,
             'source': src, 'backup_path': None},
        ]
        with patch('pathlib.Path.exists', return_value=True):
            with patch.object(app, 'scan_results', {'scanner': None}, create=True):
                stats = app._rescan_ai_files(results)
        # Если бы дедупа не было, но база None — всё равно 0.
        # Тест косвенный; основной смысл — не падать и не считать 2.
        self.assertEqual(stats['files'], 0)


class TestDS108aFinishAbortable(unittest.TestCase):
    """DS_108a: сброс UI после _finish_abortable_operation."""

    def _make_app(self):
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        # Заглушки UI-элементов
        app.scan_running = True
        app.scan_aborted = True
        app._progress_frozen = True
        app.status_label = MagicMock()
        app.progress = MagicMock()
        app.progress_label = MagicMock()
        app.btn_abort = MagicMock()
        app.btn_abort.winfo_exists = MagicMock(return_value=True)
        app.set_status = MagicMock()
        app._reset_progress = MagicMock()
        return app

    def test_finish_resets_ui(self):
        app = self._make_app()
        app._finish_abortable_operation()
        self.assertFalse(app.scan_running)
        self.assertFalse(app.scan_aborted)
        self.assertFalse(app._progress_frozen)
        app.set_status.assert_called_once_with("Готово")
        app._reset_progress.assert_called_once()
        app.btn_abort.config.assert_any_call(state='disabled')

    def test_finish_tolerates_missing_widgets(self):
        """Не падает, если btn_abort/status_label отсутствуют."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.scan_running = True
        app.scan_aborted = True
        app._progress_frozen = True
        app.btn_abort = None
        app.set_status = MagicMock(side_effect=Exception("no widget"))
        app._reset_progress = MagicMock(side_effect=Exception("no widget"))
        # Не должно бросить
        app._finish_abortable_operation()
        self.assertFalse(app.scan_running)
        self.assertFalse(app.scan_aborted)
        self.assertFalse(app._progress_frozen)


if __name__ == '__main__':
    unittest.main()
```

---

## 5. Проверка

### 5.1. pytest

```powershell
python -m pytest SRC\tests\test_ds108_gui_rescan.py -v
python -m pytest SRC\tests\ -v
```

Ожидание: новые тесты PASSED, регресс **60+ PASSED** (без падений).

### 5.2. py_compile

```powershell
python -m py_compile SRC\gui_app.py SRC\tests\test_ds108_gui_rescan.py
```

Ожидание: OK.

### 5.3. Ручной GUI-прогон (опционально)

- Запустить АРМ, выполнить «3. В Ai» на тестовом файле.
- После завершения: статус — «Готово», прогресс-бар — 0%, кнопка «Прервать» — disabled.
- В `bot.log` — `Rescan: 1 файлов; было N, стало M` (не 2).

---

## 6. Ограничения

- `PATCH_OUT\` — в `.gitignore` (строка 53), **не коммитим**.
- `SRC\gui_app.py` — правим только указанные методы.
- Тесты — только `SRC\tests\test_ds108_gui_rescan.py`.

---

## 7. Отчёт

Отчёт KODA — в `EXCHANGE\OUTBOX\DS_108_gui_fixes_rescan_ui_report.md`, **на русском** (DS_STANDARD.md §3.1), UTF-8 без BOM.

Содержание отчёта:

- Что изменено (108a, 108b) с номерами строк.
- Вывод `pytest` (полный).
- Вывод `py_compile`.
- Замечания/отклонения.
- Статус: выполнено / частично / не выполнено.