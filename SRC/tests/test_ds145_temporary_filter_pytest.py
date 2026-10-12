"""DS_145: тесты расширенного фильтра временных/служебных файлов.

Проверяет:
- DS_135 (регресс): timestamp-метка _YYYYMMDD_HHMMSS_ в имени.
- DS_145: расширения .bak/.tmp/.temp/.swp/.swo/.plp~/.~plp.
- DS_145: префикс ~$, точные имена .DS_Store/Thumbs.db/desktop.ini.
- DS_145: регресс — backup .plp без завершающего _ НЕ считается временным.

Запуск:
    python -m pytest SRC\tests\test_ds145_temporary_filter_pytest.py -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.scanner import is_temporary_filename


# ---------- DS_135 (регресс): timestamp ----------
def test_ds135_timestamp_marker():
    assert is_temporary_filename("foo_20261007_112105_real.plp")


def test_ds135_timestamp_at_start():
    assert is_temporary_filename("_20261007_112105_.plp")


def test_ds135_no_marker():
    assert not is_temporary_filename("foo.plp")


# ---------- DS_145: регресс — backup без _ НЕ временный ----------
def test_ds135_backup_without_trailing_underscore():
    """PSH_DEP_PRIV_GO_20261009_145514.plp — не временный (DS_135 инвариант)."""
    assert not is_temporary_filename("PSH_DEP_PRIV_GO_20261009_145514.plp")


# ---------- DS_145: расширения ----------
def test_suffix_bak():
    assert is_temporary_filename("file.bak")


def test_suffix_tmp():
    assert is_temporary_filename("file.tmp")


def test_suffix_temp():
    assert is_temporary_filename("file.temp")


def test_suffix_swp():
    assert is_temporary_filename("file.swp")


def test_suffix_swo():
    assert is_temporary_filename("file.swo")


def test_suffix_plp_tilde():
    assert is_temporary_filename("file.plp~")


def test_suffix_tilde_plp():
    assert is_temporary_filename("file.~plp")


def test_suffix_bak_plp():
    """file.bak.plp — тоже временный (заканчивается на .bak? нет — на .plp).

    .bak.plp оканчивается на .plp, но содержит .bak в имени.
    is_temporary_filename проверяет только конец имени — этот кейс НЕ временный.
    """
    assert not is_temporary_filename("file.bak.plp")


# ---------- DS_145: префикс ~$ ----------
def test_prefix_dollar():
    assert is_temporary_filename("~$file.plp")


def test_prefix_dollar_docx():
    assert is_temporary_filename("~$document.docx")


# ---------- DS_145: точные имена ----------
def test_exact_ds_store():
    assert is_temporary_filename(".DS_Store")


def test_exact_thumbs_db():
    assert is_temporary_filename("Thumbs.db")


def test_exact_desktop_ini():
    assert is_temporary_filename("desktop.ini")


# ---------- DS_145: регистронезависимость суффиксов ----------
def test_uppercase_suffix_bak():
    assert is_temporary_filename("file.BAK")


def test_uppercase_suffix_tmp():
    assert is_temporary_filename("file.TMP")


# ---------- Границы ----------
def test_empty():
    assert not is_temporary_filename("")


def test_normal_plp():
    assert not is_temporary_filename("PSH_DEP_PRIV_GO.plp")


def test_substring_bak_not_at_end():
    """foo.bakdir.plp — .bak в середине, не суффикс — не временный."""
    assert not is_temporary_filename("foo.bakdir.plp")


# ---------- DS_145: deep_scanner возвращает skipped_temporary ----------
def test_deep_scanner_returns_skipped_temporary(tmp_path):
    """DeepScanner.run() возвращает dict с ключом skipped_temporary."""
    from analyzer.deep_scanner import DeepScanner

    # Пустой каталог — DeepScanner не найдёт файлов, но вернёт skipped_temporary=0
    empty_dir = tmp_path / "empty_ik"
    empty_dir.mkdir()

    scanner = DeepScanner(
        source_dir=str(empty_dir),
        recursive=True,
        log_callback=lambda *a, **k: None,
        progress_callback=lambda *a, **k: None,
        status_callback=lambda *a, **k: None,
    )
    result, _out = scanner.run()
    assert 'skipped_temporary' in result
    assert result['skipped_temporary'] == 0


def test_deep_scanner_skips_temporary(tmp_path):
    """DeepScanner.run() считает временные файлы в skipped_temporary."""
    from analyzer.deep_scanner import DeepScanner

    ik = tmp_path / "ik_with_temp"
    ik.mkdir()
    # Обычный .plp
    (ik / "normal.plp").write_text("-- normal\n", encoding='utf-8')
    # Временные — не должны сканироваться
    (ik / "backup.bak").write_text("-- bak\n", encoding='utf-8')
    (ik / "temp.tmp").write_text("-- tmp\n", encoding='utf-8')
    (ik / "copy_20261007_112105_real.plp").write_text("-- ts\n", encoding='utf-8')

    scanner = DeepScanner(
        source_dir=str(ik),
        recursive=True,
        log_callback=lambda *a, **k: None,
        progress_callback=lambda *a, **k: None,
        status_callback=lambda *a, **k: None,
    )
    result, _out = scanner.run()
    assert 'skipped_temporary' in result
    # backup.bak и temp.tmp не .plp → не считаются в skipped_temporary
    # copy_20261007_112105_real.plp — .plp + timestamp → skipped_temporary=1
    assert result['skipped_temporary'] >= 1