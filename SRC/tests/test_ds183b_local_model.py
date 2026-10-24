# -*- coding: utf-8 -*-
"""DS_183b: per-host override k4_model через %APPDATA%\\TO_DBI\\<COMPUTERNAME>.local.json."""
import io
import json
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from local_settings import (  # noqa: E402
    DEFAULT_K4_MODEL,
    apply_local_k4_override,
    local_settings_path,
)


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def test_local_settings_path_uses_computername(tmp_path):
    p = local_settings_path(computer_name="MATEBOOKE", appdata=str(tmp_path))
    assert p == tmp_path / "TO_DBI" / "MATEBOOKE.local.json"


def test_no_local_file_falls_back_to_common(tmp_path):
    common = "qwen2.5-coder:7b"
    got = apply_local_k4_override(common, computer_name="MATEBOOKE", appdata=str(tmp_path))
    assert got == common


def test_local_file_overrides_common(tmp_path):
    p = local_settings_path(computer_name="MATEBOOKE", appdata=str(tmp_path))
    _write(p, json.dumps({"k4_model": "qwen2.5-coder:3b"}))
    got = apply_local_k4_override("qwen2.5-coder:7b",
                                  computer_name="MATEBOOKE", appdata=str(tmp_path))
    assert got == "qwen2.5-coder:3b"


def test_broken_json_falls_back(tmp_path):
    p = local_settings_path(computer_name="MATEBOOKE", appdata=str(tmp_path))
    _write(p, "{ not a json")
    got = apply_local_k4_override("qwen2.5-coder:7b",
                                  computer_name="MATEBOOKE", appdata=str(tmp_path))
    assert got == "qwen2.5-coder:7b"


def test_missing_key_falls_back(tmp_path):
    p = local_settings_path(computer_name="MATEBOOKE", appdata=str(tmp_path))
    _write(p, json.dumps({"other": "x"}))
    got = apply_local_k4_override("qwen2.5-coder:7b",
                                  computer_name="MATEBOOKE", appdata=str(tmp_path))
    assert got == "qwen2.5-coder:7b"


def test_empty_or_non_string_model_falls_back(tmp_path):
    p = local_settings_path(computer_name="MATEBOOKE", appdata=str(tmp_path))
    _write(p, json.dumps({"k4_model": ""}))
    got = apply_local_k4_override("qwen2.5-coder:7b",
                                  computer_name="MATEBOOKE", appdata=str(tmp_path))
    assert got == "qwen2.5-coder:7b"


def test_common_empty_uses_default(tmp_path):
    got = apply_local_k4_override("", computer_name="MATEBOOKE", appdata=str(tmp_path))
    assert got == DEFAULT_K4_MODEL