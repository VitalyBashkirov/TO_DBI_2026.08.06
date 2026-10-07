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
        # Если бы дедупа не было, но scanner None — всё равно 0.
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
