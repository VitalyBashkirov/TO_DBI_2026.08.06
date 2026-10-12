"""DS_144b: тесты _copy_files_to_result (копирование ИК -> КР по шаблону).

Без Tkinter: используется фейковый объект с минимальным self.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SRC = Path(__file__).resolve().parent.parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import gui_app


class _FakeRoot:
    def after(self, _delay, fn=None, *a, **k):
        if fn is not None:
            try:
                fn(*a, **k)
            except Exception:
                pass


def _make_app():
    """Объект с минимальным набором атрибутов для _copy_files_to_result."""
    obj = SimpleNamespace()
    obj.root = _FakeRoot()
    obj.log = lambda *a, **k: None
    # Методы берём из DBIMigrationApp через unbound-функцию.
    obj._matches_pattern = gui_app.DBIMigrationApp._matches_pattern.__get__(obj)
    obj._copy_files_to_result = gui_app.DBIMigrationApp._copy_files_to_result.__get__(obj)
    return obj


def _build_tree(base: Path):
    """ИК: base/sub/a.plp, base/b.plp, base/c.txt, base/sub/d.txt, base/e.mcs."""
    (base / "sub").mkdir(parents=True, exist_ok=True)
    (base / "sub" / "a.plp").write_text("A", encoding="utf-8")
    (base / "b.plp").write_text("B", encoding="utf-8")
    (base / "c.txt").write_text("C", encoding="utf-8")
    (base / "sub" / "d.txt").write_text("D", encoding="utf-8")
    (base / "e.mcs").write_text("E", encoding="utf-8")


def test_copy_pattern_empty_aborts(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    res = app._copy_files_to_result(src, dst, "", True, False)
    assert res["aborted"] == "Не указаны шаблоны файлов"
    assert res["copied"] == 0


def test_copy_pattern_whitespace_aborts(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    res = app._copy_files_to_result(src, dst, "   ", True, False)
    assert res["aborted"] == "Не указаны шаблоны файлов"


def test_copy_pattern_only_plp_recursive(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    res = app._copy_files_to_result(src, dst, "**/*.plp", True, False)
    assert res["aborted"] is None
    # .plp: b.plp + sub/a.plp = 2
    # не-.plp: c.txt, sub/d.txt, e.mcs = 3 (копируются всегда)
    # итого: 5
    assert res["copied"] == 5
    assert (dst / "b.plp").exists()
    assert (dst / "sub" / "a.plp").exists()
    assert (dst / "c.txt").exists()
    assert (dst / "sub" / "d.txt").exists()
    assert (dst / "e.mcs").exists()


def test_copy_pattern_only_plp_root(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    res = app._copy_files_to_result(src, dst, "*.plp", True, False)
    # .plp: только b.plp (корень) = 1
    # не-.plp: c.txt, sub/d.txt, e.mcs = 3 (копируются всегда, рекурсивно)
    assert res["copied"] == 4
    assert (dst / "b.plp").exists()
    assert not (dst / "sub" / "a.plp").exists()
    assert (dst / "c.txt").exists()
    assert (dst / "sub" / "d.txt").exists()


def test_copy_pattern_all_files_recursive(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    res = app._copy_files_to_result(src, dst, "**/*.*", True, False)
    # .plp: 2; не-.plp: 3; итого 5
    assert res["copied"] == 5


def test_copy_pattern_all_files_root(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    res = app._copy_files_to_result(src, dst, "*.*", True, False)
    # .plp: только b.plp; не-.plp: всё равно всё (для контекста) = 3
    # итого 4
    assert res["copied"] == 4


def test_copy_pattern_only_edited(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    edited = {str((src / "sub" / "a.plp").resolve()), str((src / "b.plp").resolve())}
    res = app._copy_files_to_result(src, dst, "**/*.plp", True, True, edited)
    # .plp только edited: sub/a.plp, b.plp = 2
    # не-.plp: 3
    # итого 5
    assert res["copied"] == 5
    assert (dst / "sub" / "a.plp").exists()
    assert (dst / "b.plp").exists()


def test_copy_pattern_only_edited_partial(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    # Только один файл edited
    edited = {str((src / "b.plp").resolve())}
    res = app._copy_files_to_result(src, dst, "**/*.plp", True, True, edited)
    # .plp только b.plp = 1; не-.plp = 3
    assert res["copied"] == 4
    assert (dst / "b.plp").exists()
    assert not (dst / "sub" / "a.plp").exists()


def test_copy_pattern_preserve_structure(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    res = app._copy_files_to_result(src, dst, "**/*.plp", True, False)
    assert (dst / "sub" / "a.plp").exists()
    assert (dst / "sub" / "d.txt").exists()


def test_copy_pattern_flat(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    res = app._copy_files_to_result(src, dst, "**/*.plp", False, False)
    # плоско: все в корень dst
    assert (dst / "a.plp").exists()
    assert (dst / "b.plp").exists()
    assert not (dst / "sub").exists() or not (dst / "sub" / "a.plp").exists()


def test_copy_pattern_collision_aborts(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    # два .plp с одинаковым именем в разных подкаталогах
    (src / "d1").mkdir(parents=True)
    (src / "d2").mkdir(parents=True)
    (src / "d1" / "conf.plp").write_text("1", encoding="utf-8")
    (src / "d2" / "conf.plp").write_text("2", encoding="utf-8")
    res = app._copy_files_to_result(src, dst, "**/*.plp", False, False)
    assert res["aborted"] is not None
    assert "Коллизия" in res["aborted"]


def test_copy_pattern_non_plp_always(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    # Шаблон только .plp; но .txt/.mcs должны скопироваться
    res = app._copy_files_to_result(src, dst, "**/*.plp", True, False)
    assert (dst / "c.txt").exists()
    assert (dst / "e.mcs").exists()
    assert (dst / "sub" / "d.txt").exists()


def test_copy_pattern_idempotent(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    res1 = app._copy_files_to_result(src, dst, "**/*.plp", True, False)
    assert res1["copied"] == 5
    # повторный вызов — все уже есть
    res2 = app._copy_files_to_result(src, dst, "**/*.plp", True, False)
    assert res2["copied"] == 0
    assert res2["skipped"] == 5
    assert res2["aborted"] is None


def test_copy_pattern_multi_mask(tmp_path):
    app = _make_app()
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    _build_tree(src)
    # Шаблон: plp + mcs (несколькими масками)
    res = app._copy_files_to_result(src, dst, "**/*.plp;**/*.mcs", True, False)
    # .plp: 2; .mcs: 1 (по шаблону); не-.plp: 2 txt
    assert (dst / "b.plp").exists()
    assert (dst / "sub" / "a.plp").exists()
    assert (dst / "e.mcs").exists()
