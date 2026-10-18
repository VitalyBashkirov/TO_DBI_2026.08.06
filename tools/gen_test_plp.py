#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS_147a: CLI-генератор тестовых .plp (аналог GUI _run_test_generation).

Контракт:
  python tools\\gen_test_plp.py -s <ИК> [-o <dir>] [--rules <csv>] [--priorities <csv>] [--dry-run]

- -s            источник (например, PlpCheck); обязательный. sources=[s].
- -o            каталог для .plp и .log. По умолчанию DATA\\generated_plp\\
- --rules       csv кодов правил. Если задан -> rule_codes=<csv> в generate().
                Иначе -> все правила, прошедшие фильтры (sources+priorities).
- --priorities  csv приоритетов (HIGH,MEDIUM,LOW), опционально.
- --dry-run     не писать .plp, только лог (N правил + список кодов).

Код возврата: 0 — успех (в т.ч. dry-run); 1 — ошибка.
Лог: <out-dir>\\gen_<s>_<YYYYMMDD_HHMMSS>.log, UTF-8, BOM=False.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "SRC"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

DEFAULT_OUT = PROJECT_ROOT / "DATA" / "generated_plp"
DEFAULT_RUBRICATOR_DIR = PROJECT_ROOT / "DATA" / "Рубрикатор v5"


def _parse_csv(value):
    if not value:
        return None
    parts = [p.strip() for p in value.split(",") if p.strip()]
    return parts or None


def _build_parser():
    p = argparse.ArgumentParser(
        prog="gen_test_plp",
        description="DS_147a: CLI-генератор тестовых .plp (TestGeneratorV2).",
    )
    p.add_argument("-s", "--source", required=True,
                   help="Источник (например, PlpCheck). sources=[s].")
    p.add_argument("-o", "--out-dir", default=str(DEFAULT_OUT),
                   help="Каталог для .plp и .log (по умолчанию DATA\\generated_plp).")
    p.add_argument("--rules", default=None,
                   help="CSV кодов правил. Без флага — все прошедшие фильтры.")
    p.add_argument("--priorities", default=None,
                   help="CSV приоритетов (HIGH,MEDIUM,LOW), опционально.")
    p.add_argument("--rubricator-dir", default=str(DEFAULT_RUBRICATOR_DIR),
                   help="Каталог рубрикатора v5 (по умолчанию DATA\\Рубрикатор v5).")
    p.add_argument("--dry-run", action="store_true",
                   help="Не писать .plp, только лог (N правил + список кодов).")
    return p


def main(argv=None):
    args = _build_parser().parse_args(argv)

    out_dir = Path(args.out_dir)
    rubricator_dir = Path(args.rubricator_dir)
    rules_csv = _parse_csv(args.rules)
    priorities_csv = _parse_csv(args.priorities)
    source = args.source.strip()
    if not source:
        print("[FATAL] -s/--source пустой", file=sys.stderr)
        return 1

    if not (rubricator_dir / "4.RUBRICATOR_PROMPT v5.json").exists():
        print(f"[FATAL] Нет v5.json в {rubricator_dir}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = out_dir / f"gen_{source}_{ts}.log"

    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    try:
        from analyzer.test_generator_v2 import TestGeneratorV2

        gen = TestGeneratorV2(
            rubricator_dir=rubricator_dir,
            sources=[source],
            priorities=priorities_csv,
        )

        selected = gen.select_rules(rules_csv)

        log("=== DS_147a gen_test_plp ===")
        log(f"source      : {source}")
        log(f"out_dir     : {out_dir}")
        log(f"rubricator  : {rubricator_dir}")
        log(f"rules_arg   : {rules_csv}")
        log(f"priorities  : {priorities_csv}")
        log(f"dry_run     : {args.dry_run}")
        log(f"rules_total : {len(selected)}")

        if not selected:
            log("[WARN] Правил не найдено по заданным фильтрам")
            log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
            log(f"Лог: {log_path}")
            return 1

        if rules_csv:
            missing = [r for r in rules_csv if r not in gen.rules]
            if missing:
                log(f"[WARN] В v5.json нет правил (пропущено): {len(missing)}")
                for r in missing:
                    log(f"  - {r}")

        for i, code in enumerate(selected, 1):
            log(f"  [{i:3d}] {code}")

        if args.dry_run:
            log("[DRY-RUN] .plp не создаются")
            log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
            log(f"Лог: {log_path}")
            return 0

        result = gen.generate(
            rule_codes=selected,
            mode="single",
            out_dir=out_dir,
        )
        if result is None:
            log("[WARN] generate() вернул None")
            log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
            log(f"Лог: {log_path}")
            return 1

        log(f"[OK] Создан: {result}")
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        log(f"Лог: {log_path}")
        return 0

    except Exception as e:
        log(f"[FATAL] {type(e).__name__}: {e}")
        try:
            log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
            print(f"Лог: {log_path}")
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
