"""DS_135: тесты is_temporary_filename (временные метки в именах файлов).

Запуск:
    python -m pytest SRC\tests\test_ds135_temporary.py -v
"""
import sys
from pathlib import Path

# Добавляем SRC в sys.path для импорта analyzer.scanner
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.scanner import is_temporary_filename


def test_temp_marker_basic():
    """Метка _YYYYMMDD_HHMMSS_ в имени — временный файл."""
    assert is_temporary_filename("foo_20261007_112105_real.plp")


def test_temp_marker_other_suffix_b():
    """Метка _YYYYMMDD_HHMMSS_ + произвольный суффикс — временный."""
    assert is_temporary_filename("foo_20261007_112105_something.plp")


def test_temp_marker_other_suffix():
    """Метка + другой суффикс — временный."""
    assert is_temporary_filename("foo_20261007_112105_other.plp")


def test_temp_marker_at_start():
    """Метка в начале имени — временный."""
    assert is_temporary_filename("_20261007_112105_.plp")


def test_no_marker():
    """Без метки — обычный файл."""
    assert not is_temporary_filename("foo.plp")


def test_short_date():
    """7 цифр даты — не метка."""
    assert not is_temporary_filename("foo_2026100_112105.plp")


def test_short_time():
    """5 цифр времени — не метка."""
    assert not is_temporary_filename("foo_20261007_11210.plp")


def test_no_trailing_underscore():
    """Метка без завершающего _ — не считается временным (backup .plp)."""
    assert not is_temporary_filename("PSH_DEP_PRIV_GO_20261009_145514.plp")


def test_empty():
    """Пустая строка — не временный."""
    assert not is_temporary_filename("")


def test_none_like():
    """Пустое значение — не временный."""
    assert not is_temporary_filename("")


def test_typical_backup():
    """Реальный пример из каталога — временный."""
    assert is_temporary_filename("PSH_DEP_PRIV_GO_20261007_112105_real.plp")


def test_typical_normal():
    """Реальный обычный .plp — не временный."""
    assert not is_temporary_filename("PSH_DEP_PRIV_GO.plp")
