# -*- coding: utf-8 -*-
"""
DS_183b: per-host override настроек (локальный файл поверх общего settings.json).

Идея: SRC/settings.json общий для хостов MBE и LG (один SSD F:).
K4-модель различается (MBE -> 3b, LG -> 7b). Локальный файл
%APPDATA%\\TO_DBI\\<COMPUTERNAME>.local.json переопределяет ТОЛЬКО
ключ 'k4_model'. Общий settings.json не изменяется.

Формат: {"k4_model": "qwen2.5-coder:3b"} или {"k4_model": "qwen2.5-coder:7b"}.
Битый / отсутствующий / без ключа -> тихий fallback на общий k4_model.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable, Optional


DEFAULT_K4_MODEL = "qwen2.5-coder:3b"


def local_settings_path(computer_name: Optional[str] = None,
                        appdata: Optional[str] = None) -> Path:
    """Путь к локальному override-файлу: %APPDATA%\\TO_DBI\\<COMPUTERNAME>.local.json."""
    if appdata is None:
        appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    if computer_name is None:
        computer_name = os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "UNKNOWN"
    return Path(appdata) / "TO_DBI" / f"{computer_name}.local.json"


def apply_local_k4_override(common_model: str,
                            computer_name: Optional[str] = None,
                            appdata: Optional[str] = None,
                            log: Optional[Callable[[str], None]] = None) -> str:
    """
    Вернуть k4_model с учётом локального override.
    - common_model: значение из общего settings.json
    - если локальный файл есть и в нём валидный k4_model -> вернуть его
    - иначе -> вернуть common_model (fallback, без исключений)
    """
    if not common_model:
        common_model = DEFAULT_K4_MODEL
    try:
        p = local_settings_path(computer_name=computer_name, appdata=appdata)
    except Exception:
        return common_model
    if not p.exists():
        return common_model
    try:
        with open(p, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except Exception:
        if log:
            try:
                log(f"DS_183b: локальный override не прочитан ({p}) — fallback на общий k4_model")
            except Exception:
                pass
        return common_model
    if not isinstance(data, dict):
        return common_model
    model = data.get("k4_model")
    if not isinstance(model, str) or not model.strip():
        return common_model
    model = model.strip()
    if log:
        try:
            log(f"DS_183b: k4_model локально переопределён: {model} ({p})")
        except Exception:
            pass
    return model