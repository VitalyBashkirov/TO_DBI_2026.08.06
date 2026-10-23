# -*- coding: utf-8 -*-
"""DS_181: pre-AI копии (_preai) должны писаться в PATCH_CALC/backups, не в PATCH_IN."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from SRC.ai_exchange import _preai_target_dir  # noqa: E402


def test_preai_target_under_patch_in_keeps_relpath():
    src = ROOT / "PATCH_IN" / "patch_X" / "ENTITY" / "DEPN" / "PSH_ED_PRC_SCHM_20261022_124954_preai.plp"
    d = _preai_target_dir(src)
    # каталог должен быть под PATCH_CALC/backups/patch_X/ENTITY/DEPN
    parts = d.parts
    assert "PATCH_CALC" in parts, parts
    assert "backups" in parts, parts
    assert parts[-3:] == ("patch_X", "ENTITY", "DEPN"), parts


def test_preai_target_outside_patch_in_is_flat():
    src = ROOT / "SOME_OTHER" / "foo.plp"
    d = _preai_target_dir(src)
    assert d == ROOT / "PATCH_CALC" / "backups", d


def test_preai_target_returns_path_type():
    src = ROOT / "PATCH_IN" / "a" / "b.plp"
    d = _preai_target_dir(src)
    assert isinstance(d, Path)


def test_preai_filename_preserved_in_call_site():
    """Имя файла формируется в process_response; проверяем, что шаблон не изменился
    и что путь-каталог берётся из _preai_target_dir."""
    import io
    src_path = ROOT / "SRC" / "ai_exchange.py"
    with io.open(src_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "_preai_target_dir(source, base)" in text
    assert "_preai_backup_dir" in text
    assert "PATCH_CALC" in text
    assert "{source.stem}_{ts}_preai{source.suffix}" in text