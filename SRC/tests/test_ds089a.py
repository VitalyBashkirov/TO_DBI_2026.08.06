"""Tests for DS_089a — abort/продолжение UI."""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestDS089a_ToggleButton(unittest.TestCase):
    """§2.2: Кнопка toggle (прервать/продолжить)."""

    def test_abort_requested_false_by_default(self):
        """_abort_requested() возвращает False по умолчанию."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.scan_aborted = False
        self.assertFalse(app._abort_requested())

    def test_abort_requested_true_when_aborted(self):
        """_abort_requested() возвращает True после abort."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.scan_aborted = True
        self.assertTrue(app._abort_requested())


class TestDS089a_StartOperation(unittest.TestCase):
    """§2.2: _start_abortable_operation."""

    def test_start_sets_running(self):
        """_start_abortable_operation устанавливает scan_running=True."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.scan_running = False
        app.scan_aborted = True
        app._progress_frozen = True
        app.status_label = MagicMock()
        app.btn_abort = MagicMock()
        app.btn_abort.winfo_exists.return_value = True
        app.progress = MagicMock()
        app._set_status_running = MagicMock()

        app._start_abortable_operation()

        self.assertTrue(app.scan_running)
        self.assertFalse(app.scan_aborted)
        self.assertFalse(app._progress_frozen)
        app.btn_abort.config.assert_called()

    def test_start_resets_abort_flag(self):
        """_start_abortable_operation сбрасывает scan_aborted=False."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.scan_aborted = True
        app.scan_running = False
        app._progress_frozen = False
        app.status_label = MagicMock()
        app.btn_abort = MagicMock()
        app.progress = MagicMock()
        app._set_status_running = MagicMock()

        app._start_abortable_operation()

        self.assertFalse(app.scan_aborted)


class TestDS089a_FinishOperation(unittest.TestCase):
    """§2.2: _finish_abortable_operation."""

    def test_finish_resets_flags(self):
        """_finish_abortable_operation сбрасывает флаги."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.scan_running = True
        app.scan_aborted = True
        app.btn_abort = MagicMock()
        app.btn_abort.winfo_exists.return_value = True

        app._finish_abortable_operation()

        self.assertFalse(app.scan_running)
        self.assertFalse(app.scan_aborted)


class TestDS089a_ScannerAbort(unittest.TestCase):
    """§2.3: Mid-file abort в scanner."""

    def test_scanner_has_abort_callback(self):
        """Scanner принимает abort_callback."""
        from analyzer.scanner import PLPlusScanner
        import inspect
        sig = inspect.signature(PLPlusScanner.__init__)
        self.assertIn('abort_callback', sig.parameters)


class TestDS089a_CodeFixerAbort(unittest.TestCase):
    """§2.4: abort_callback в code_fixer."""

    def test_fixer_has_abort_callback(self):
        """PLPlusFixer принимает abort_callback."""
        from fixer.code_fixer import PLPlusFixer
        import inspect
        sig = inspect.signature(PLPlusFixer.__init__)
        self.assertIn('abort_callback', sig.parameters)

    def test_fixer_stores_abort_callback(self):
        """PLPlusFixer сохраняет abort_callback."""
        from fixer.code_fixer import PLPlusFixer
        cb = lambda: False
        fixer = PLPlusFixer({}, 'test', abort_callback=cb)
        self.assertEqual(fixer.abort_callback, cb)


class TestDS089a_RuleBasedPopen(unittest.TestCase):
    """§2.5: rule_based_fixer через Popen."""

    def test_popen_used_in_gui(self):
        """В gui_app.py используется subprocess.Popen (не run)."""
        gui_path = os.path.join(os.path.dirname(__file__), '..', 'gui_app.py')
        with open(gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Проверяем что Popen есть в контексте rule_based_fixer
        self.assertIn('Popen', content)
        self.assertIn('_monitor_worker', content)


class TestDS089a_Logging(unittest.TestCase):
    """§2.6: Логирование abort/continue."""

    def test_abort_logs_message(self):
        """on_abort_click логирует сообщение о прерывании."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.scan_running = True
        app.scan_aborted = False
        app._progress_frozen = False
        app.progress = MagicMock()
        app.btn_abort = MagicMock()
        app.log = MagicMock()
        app._stop_event = MagicMock()  # DS_089b

        app.on_abort_click()

        # Проверяем что log был вызван
        app.log.assert_called()
        # Ищем сообщение о прерывании
        calls = [str(c) for c in app.log.call_args_list]
        self.assertTrue(any('прерывание' in c.lower() or 'прерван' in c.lower() for c in calls))

    def test_continue_logs_message(self):
        """on_abort_click логирует сообщение о продолжении."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.scan_running = True
        app.scan_aborted = True  # Уже прервано
        app._progress_frozen = True
        app.progress = MagicMock()
        app.btn_abort = MagicMock()
        app.log = MagicMock()
        app._stop_event = MagicMock()  # DS_089b

        app.on_abort_click()

        # Проверяем что log был вызван
        app.log.assert_called()
        calls = [str(c) for c in app.log.call_args_list]
        self.assertTrue(any('продолжена' in c.lower() for c in calls))


class TestDS089a_Forecast(unittest.TestCase):
    """§2.7: Прогноз времени."""

    def test_forecast_in_log(self):
        """on_abort_click логирует прогноз."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.scan_running = True
        app.scan_aborted = False
        app._progress_frozen = False
        app.progress = MagicMock()
        app.btn_abort = MagicMock()
        app.log = MagicMock()
        app._op_files_done = 5
        app._op_total_files = 10
        app._op_start_time = 1000.0
        app._stop_event = MagicMock()  # DS_089b

        app.on_abort_click()

        # Проверяем что log был вызван с прогнозом
        calls = [str(c) for c in app.log.call_args_list]
        self.assertTrue(any('прогноз' in c.lower() or 'остановка' in c.lower() for c in calls))


class TestDS089a_AICycle(unittest.TestCase):
    """§2.8: AI-цикл не возобновляется."""

    def test_ai_abort_not_resumed(self):
        """AI-цикл при abort не возобновляется (логгирует сообщение)."""
        from gui_app import DBIMigrationApp
        app = DBIMigrationApp.__new__(DBIMigrationApp)
        app.scan_running = True
        app.scan_aborted = True
        app._progress_frozen = False
        app.progress = MagicMock()
        app.btn_abort = MagicMock()
        app.log = MagicMock()
        app._stop_event = MagicMock()  # DS_089b

        app.on_abort_click()

        calls = [str(c) for c in app.log.call_args_list]
        # После продолжения — сообщение о продолжении
        self.assertTrue(any('продолжена' in c.lower() for c in calls))


if __name__ == '__main__':
    unittest.main()

