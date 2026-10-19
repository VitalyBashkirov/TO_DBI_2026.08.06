#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS_147b: валидация сгенерированных .plp через PLPlusScanner.

Контракт:
  python tools\\validate_gen_plp.py -d <dir_or_file> [-o <log>] [--rules <csv>]

- -d        каталог (все *.plp) или один .plp; обязательный.
- -o        лог (по умолчанию <dir>\\validation.log).
- --rules   ожидаемые коды (csv). Без флага — из мета-блоков .plp (-- Правило: <code>).

Код возврата: 0 — все ожидаемые сработали; 1 — есть пропуски / ошибки.
Лог: UTF-8, BOM=False, многострочный.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "SRC"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

DEFAULT_RUBRICATOR_DIR = PROJECT_ROOT / "DATA" / "Рубрикатор v5"
RE_RULE = re.compile(r"^--\s*Правило:\s*(\S+)\s*$")


def _parse_csv(value):
    if not value:
        return None
    parts = [p.strip() for p in value.split(",") if p.strip()]
    return parts or None


def _build_parser():
    p = argparse.ArgumentParser(
        prog="validate_gen_plp",
        description="DS_147b: валидация сгенерированных .plp через PLPlusScanner.",
    )
    p.add_argument("-d", "--dir", required=True,
                   help="Каталог с *.plp или один .plp-файл.")
    p.add_argument("-o", "--out-log", default=None,
                   help="Лог (по умолчанию <dir>\\validation.log).")
    p.add_argument("--rules", default=None,
                   help="CSV ожидаемых кодов. Без флага — из мета-блоков .plp.")
    p.add_argument("--rubricator-dir", default=str(DEFAULT_RUBRICATOR_DIR),
                   help="Каталог рубрикатора v5 (по умолчанию DATA\\Рубрикатор v5).")
    return p


def _collect_plp(target):
    p = Path(target)
    if p.is_file() and p.suffix.lower() == ".plp":
        return [p]
    if p.is_dir():
        return sorted(p.glob("*.plp"))
    return []


def _extract_rules_from_plp(plp_path):
    codes = []
    try:
        text = plp_path.read_text(encoding="utf-8-sig")
    except Exception:
        return codes
    for line in text.splitlines():
        m = RE_RULE.match(line.strip())
        if m:
            codes.append(m.group(1))
    return codes


def _build_scanner(rubricator_dir):
    from rubricator_prompts import RubricatorPrompts
    from analyzer.scanner import PLPlusScanner
    loader = RubricatorPrompts(Path(rubricator_dir))
    with contextlib.redirect_stdout(io.StringIO()):
        ok = loader.load()
    if not ok:
        raise RuntimeError(f"Не удалось загрузить рубрикатор: {rubricator_dir}")
    config = {
        "paths": {"source_dir": str(Path(rubricator_dir).parent)},
        "scan": {"file_pattern": "**/*.plp", "recursive": True, "exclude_patterns": []},
    }
    with contextlib.redirect_stdout(io.StringIO()):
        scanner = PLPlusScanner(
            config=config,
            selected_rules=None,
            rubricator_prompts=loader,
        )
    return scanner


def main(argv=None):
    args = _build_parser().parse_args(argv)
    target = Path(args.dir)
    plp_files = _collect_plp(target)
    if not plp_files:
        print(f"[FATAL] Нет .plp в {target}", file=sys.stderr)
        return 1

    if args.out_log:
        log_path = Path(args.out_log)
    else:
        base = target if target.is_dir() else target.parent
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = base / f"validation_{ts}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    rules_csv = _parse_csv(args.rules)
    rubricator_dir = Path(args.rubricator_dir)

    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    try:
        scanner = _build_scanner(rubricator_dir)
    except Exception as e:
        log(f"[FATAL] Не удалось создать PLPlusScanner: {type(e).__name__}: {e}")
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        return 1

    log("=== DS_147b validate_gen_plp ===")
    log(f"target    : {target}")
    log(f"plp_files : {len(plp_files)}")
    log(f"rules_arg : {rules_csv}")
    log(f"log       : {log_path}")
    log("")

    total_pass = 0
    total_fail = 0

    for plp in plp_files:
        if rules_csv:
            expected = list(rules_csv)
        else:
            expected = _extract_rules_from_plp(plp)

        log(f"[FILE] {plp.name}")
        log(f"  expected ({len(expected)}): {expected}")

        if not expected:
            log("  [WARN] ожидаемые правила не заданы и не найдены в мета-блоках")
            log("")
            continue

        try:
            with contextlib.redirect_stdout(io.StringIO()):
                issues = scanner.scan_file(plp)
        except Exception as e:
            log(f"  [FATAL] scan_file: {type(e).__name__}: {e}")
            total_fail += len(expected)
            log("")
            continue

        found = {getattr(i, "issue_type", "") for i in issues}
        log(f"  found ({len(found)}): {sorted(found)}")

        for code in expected:
            if code in found:
                log(f"  PASS {code}")
                total_pass += 1
            else:
                log(f"  FAIL {code}")
                total_fail += 1
        log("")

    log("=== ИТОГ ===")
    log(f"PASS: {total_pass}")
    log(f"FAIL: {total_fail}")

    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    log(f"Лог: {log_path}")

    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
