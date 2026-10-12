"""DS_144a: архив — внутри сразу содержимое ИППУ, без обёртки patch_XXX/."""
import os
import zipfile
from pathlib import Path

import pytest


def _build_tree(base: Path):
    """Создаёт ИК-подобную структуру: base/patch_X/sub/a.plp, base/patch_X/b.plp."""
    patch = base / "patch_PSH_DEP_PRIV_GO"
    (patch / "sub").mkdir(parents=True, exist_ok=True)
    (patch / "b.plp").write_text("B", encoding="utf-8")
    (patch / "sub" / "a.plp").write_text("A", encoding="utf-8")
    return patch


def _archive_tree(results_dir: Path, archive_path: Path):
    """Повторяет логику _run_archive после DS_144a (arcname от results_dir)."""
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(results_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(results_dir)
                zipf.write(file_path, arcname)


def test_archive_no_wrapper_name(tmp_path):
    """Имя архива = имя ИППУ (results_dir.name)."""
    patch = _build_tree(tmp_path / "PATCH_OUT")
    archive_path = patch.parent / f"{patch.name}.zip"
    _archive_tree(patch, archive_path)
    assert archive_path.exists()
    assert archive_path.name == "patch_PSH_DEP_PRIV_GO.zip"


def test_archive_entries_no_patch_wrapper(tmp_path):
    """Внутри архива нет обёртки patch_XXX/ — сразу подкаталоги ИППУ."""
    patch = _build_tree(tmp_path / "PATCH_OUT")
    archive_path = patch.parent / f"{patch.name}.zip"
    _archive_tree(patch, archive_path)

    with zipfile.ZipFile(archive_path) as zipf:
        names = zipf.namelist()

    # Ожидание: b.plp, sub/a.plp — без patch_PSH_DEP_PRIV_GO/ в начале
    assert "b.plp" in names
    assert "sub/a.plp" in names
    # Ни одна запись не начинается с имени ИППУ
    assert not any(n.startswith("patch_PSH_DEP_PRIV_GO/") for n in names), names


def test_archive_entries_content(tmp_path):
    """Содержимое внутри архива совпадает с файлами."""
    patch = _build_tree(tmp_path / "PATCH_OUT")
    archive_path = patch.parent / f"{patch.name}.zip"
    _archive_tree(patch, archive_path)

    with zipfile.ZipFile(archive_path) as zipf:
        assert zipf.read("b.plp") == b"B"
        assert zipf.read("sub/a.plp") == b"A"


def test_archive_flat_files_no_subdirs(tmp_path):
    """Плоский набор файлов без подкаталогов — записи по именам."""
    patch = tmp_path / "PATCH_OUT" / "patch_PSH_DEP_PRIV_GO"
    patch.mkdir(parents=True)
    (patch / "x.plp").write_text("X", encoding="utf-8")
    (patch / "y.plp").write_text("Y", encoding="utf-8")

    archive_path = patch.parent / f"{patch.name}.zip"
    _archive_tree(patch, archive_path)

    with zipfile.ZipFile(archive_path) as zipf:
        names = sorted(zipf.namelist())
    assert names == ["x.plp", "y.plp"]
