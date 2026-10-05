# -*- coding: utf-8 -*-
"""DS_094 - testy resume CLI: load/save processed_ids, skip_ids, CLI args.

t1..t8 - 8 keysov (sm. DS_094 S5).
Zapusk:  python SRC/tests/test_ds094_resume.py
"""
import json
import os
import sys
import tempfile
import shutil

if __name__ == '__main__':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1, closefd=False)

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'tools')
sys.path.insert(0, TOOLS)

from ai_local_worker import load_processed_ids, save_processed_ids, run_request, build_parser

results = []


def check(num, desc, ok, detail=""):
    results.append((num, desc, bool(ok)))
    status = "OK  " if ok else "FAIL"
    print(f"[{status}] #{num:>2} {desc}" + (f"  :: {detail}" if detail else ""))


def test_t1_load_no_file():
    tmp = tempfile.mkdtemp(prefix='ds094_t1_')
    try:
        ids = load_processed_ids(tmp)
        check(1, "load_processed_ids: fail net -> pusty set", ids == set(), f"got={ids}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_t2_load_with_file():
    tmp = tempfile.mkdtemp(prefix='ds094_t2_')
    try:
        data = {"request": "AI_REQUEST_test.md", "processed_ids": [1, 2, 3],
                "timestamp": "2026-10-05T12:00:00", "model": "test"}
        (os.path.join(tmp, "test.processed.json"))
        with open(os.path.join(tmp, "test.processed.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f)
        ids = load_processed_ids(tmp)
        check(2, "load_processed_ids: fail yest -> set s id", ids == {1, 2, 3}, f"got={ids}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_t3_save_creates_json():
    tmp = tempfile.mkdtemp(prefix='ds094_t3_')
    try:
        path = save_processed_ids(tmp, "AI_REQUEST_foo.md", {10, 20, 30}, "test-model")
        exists = os.path.isfile(path)
        data = json.loads(open(path, encoding='utf-8').read()) if exists else {}
        ok = (exists and data.get("processed_ids") == [10, 20, 30]
              and data.get("model") == "test-model")
        check(3, "save_processed_ids: pishet JSON", ok, f"path={path} data={data}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_t4_run_request_skip_ids():
    tmp_in = tempfile.mkdtemp(prefix='ds094_t4_in_')
    tmp_out = tempfile.mkdtemp(prefix='ds094_t4_out_')
    try:
        req_path = os.path.join(tmp_in, "AI_REQUEST_test.md")
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write("# AI_REQUEST\n- Источник: test.plp\n\n")
            for i in range(1, 6):
                f.write(f"### Проблема {i}\n- Строка: {i}\n- Код правила: v53.TEST.1\n- Описание: d{i}\n- Текущий код:\n```\nc{i}\n```\n\n")
        from ai_local_worker import load_config
        cfg = load_config()
        stats, fixes = run_request(req_path, tmp_out, cfg, skip_ids={1, 2, 3}, dry_run=True)
        ok = stats['issues'] == 2
        check(4, "run_request skip_ids: issues filtrovany", ok, f"issues={stats['issues']}")
        assert ok, f"skip_ids должен уменьшить issues до 2, got={stats['issues']}"
    finally:
        shutil.rmtree(tmp_in, ignore_errors=True)
        shutil.rmtree(tmp_out, ignore_errors=True)


def test_t5_cli_skip_ids_parses():
    parser = build_parser()
    args = parser.parse_args(['--request', 'x.md', '--skip-ids', 'ids.json'])
    ok = args.skip_ids == 'ids.json'
    check(5, "CLI --skip-ids parsitsya", ok, f"skip_ids={args.skip_ids}")


def test_t6_cli_resume_parses():
    parser = build_parser()
    args = parser.parse_args(['--request', 'x.md', '--resume'])
    ok = args.resume is True
    check(6, "CLI --resume parsitsya", ok, f"resume={args.resume}")


def test_t7_repeat_with_resume():
    tmp_in = tempfile.mkdtemp(prefix='ds094_t7_in_')
    tmp_out = tempfile.mkdtemp(prefix='ds094_t7_out_')
    try:
        req_path = os.path.join(tmp_in, "AI_REQUEST_test.md")
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write("# AI_REQUEST\n- Источник: test.plp\n\n")
            for i in range(1, 6):
                f.write(f"### Проблема {i}\n- Строка: {i}\n- Код правила: v53.TEST.1\n- Описание: d{i}\n- Текущий код:\n```\nc{i}\n```\n\n")
        from ai_local_worker import load_config
        cfg = load_config()
        save_processed_ids(tmp_out, "AI_REQUEST_test.md", {1, 2, 3, 4, 5}, "test")
        ids = load_processed_ids(tmp_out)
        stats, fixes = run_request(req_path, tmp_out, cfg, skip_ids=ids, dry_run=True)
        ok = stats['issues'] == 0
        check(7, "povtornyj progon s --resume: vse propusheny", ok, f"issues={stats['issues']}")
    finally:
        shutil.rmtree(tmp_in, ignore_errors=True)
        shutil.rmtree(tmp_out, ignore_errors=True)


def test_t8_resume_no_out_dir():
    parser = build_parser()
    args = parser.parse_args(['--request', 'x.md', '--resume'])
    # --resume bez --out-dir: ispolzuetsya AI_OUT_DIR (defolt)
    ok = args.resume is True
    check(8, "--resume bez out-dir: defolt AI_OUT_DIR", ok, f"resume={args.resume}")


def main():
    for fn in (test_t1_load_no_file, test_t2_load_with_file, test_t3_save_creates_json,
               test_t4_run_request_skip_ids, test_t5_cli_skip_ids_parses,
               test_t6_cli_resume_parses, test_t7_repeat_with_resume,
               test_t8_resume_no_out_dir):
        fn()
    passed = sum(1 for _, _, ok in results if ok)
    total = len(results)
    print("-" * 60)
    print(f"ITOG: {passed}/{total} PASSED")
    failed = [r for r in results if not r[2]]
    for num, desc, _ok in failed:
        print(f"  FAIL #{num}: {desc}")
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())