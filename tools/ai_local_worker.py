# -*- coding: utf-8 -*-
"""DS_082b: Local AI worker — закрытие AI-issues через локальную LLM (Ollama).

Пайплайн обмена (DS_054, контракт не менять):
    АРМ «AI-обмен» -> EXCHANGE\\AI_IN\\AI_REQUEST_<...>.md
    rule-based fixer (DS_082a) закрывает тривиальные (35 из 96)
    local AI worker (этот скрипт) закрывает нетривиальные (61) батчами по 5
    -> EXCHANGE\\AI_OUT\\AI_RESPONSE_<...>.md (JSON-массив element)
    АРМ «Применить» -> ai_exchange.apply_fixes (§2.6, §2.7 — контракт)

Пакетный промпт (DS_082b §2.1): system + описание + batch (5 issues) + JSON
output format. Парсер ответа — ai_exchange.extract_json_array (DS_054 §2.3),
как в rule_based_fixer (§2.5).

Формат файла ответа — тот же, что у rule_based_fixer:
    # AI_RESPONSE ...
    ## Метаданные: source_file, request, rubricator
    ## Фиксы
    ```json
    [ {...}, ... ]
    ```

CLI:
    python tools/ai_local_worker.py --request EXCHANGE/AI_IN/AI_REQUEST_X.md \
        --out EXCHANGE/AI_OUT
    python tools/ai_local_worker.py --in-dir EXCHANGE/AI_IN --out-dir EXCHANGE/AI_OUT
    python tools/ai_local_worker.py --request ... --out ... --metrics temp/m.json

Конфиг: tools/ai_local_worker_config.json (модель, batch_size, timeout, ollama_url).
Ollama недоступна -> сообщение в лог, exit 1, AI_RESPONSE не создаётся (§3 тест 3).

Совместимость с Python 3.9 (TO_DBI\\python39): без `X | Y` в аннотациях.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # TO_DBI
TOOLS_DIR = Path(__file__).resolve().parent            # TO_DBI\tools
SRC_DIR = ROOT / 'SRC'                                 # ai_exchange (DS_054)
EXCHANGE_DIR = ROOT / 'EXCHANGE'
AI_IN_DIR = EXCHANGE_DIR / 'AI_IN'
AI_OUT_DIR = EXCHANGE_DIR / 'AI_OUT'
BOT_LOG = EXCHANGE_DIR / 'bot.log'                     # DS_050 §2
CONFIG_PATH = TOOLS_DIR / 'ai_local_worker_config.json'
REQUEST_PREFIX = 'AI_REQUEST_'
RESPONSE_PREFIX = 'AI_RESPONSE_'

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rule_based_fixer import parse_request              # DS_082a §2.5
from ai_exchange import extract_json_array              # DS_054 §2.3 (парсер)

# --------------------------------------------------------------- конфиг (§2.5)
DEFAULT_CONFIG = {
    'ollama_url': 'http://localhost:11434',
    'model': 'deepseek-coder:6.7b',
    'batch_size': 5,
    'temperature': 0.1,
    'num_ctx': 4096,
    'max_tokens': 2000,
    'timeout_sec': 600,
}

SYSTEM_PROMPT = 'PL/SQL migration expert.'

# JSON-схема ответа для Ollama (structured output): массив фиксов. Гарантирует
# валидный JSON и форму массива (format='json' без схемы модель трактует
# вольно — вернула один объект вместо массива).
FIX_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
            'line': {'type': 'integer'},
            'before': {'type': 'string'},
            'after': {'type': 'string'},
            'reason': {'type': 'string'},
            'confidence': {'type': 'number'},
        },
        'required': ['id', 'after', 'confidence'],
    },
}

# Правило применения (DS_082b §2.7, как CLASSIFY_RULE в rule_based_fixer §2.5).
# confidence >= 0.7 -> auto, 0.5..0.7 -> medium, < 0.5 -> manual.
CLASSIFY_RULE = {'min_confidence_auto': 0.7, 'min_confidence_medium': 0.5}


# ------------------------------------------------------------------- логирование
def log(msg, bot=False):
    """Строка в stdout; bot=True — дубль в EXCHANGE\\bot.log.

    DS_050 §2.1: в bot.log пишется только итоговая строка прогона;
    построчные skip — в stdout (как в rule_based_fixer).
    """
    text = str(msg)
    try:
        sys.stdout.write(text + '\n')
        sys.stdout.flush()
    except Exception:
        pass
    if bot:
        # DS_050 §2: формат [ДД.ММ.ГГГГ ЧЧ:ММ:СС] DS XXX: <описание>, UTF-8.
        stamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        try:
            with io.open(str(BOT_LOG), 'a', encoding='utf-8', newline='') as fh:
                fh.write(f'[{stamp}] DS 082b: {text}\r\n')
        except OSError:
            pass


def load_config(path=None):
    """Конфиг из JSON поверх значений по умолчанию (§2.2)."""
    cfg = dict(DEFAULT_CONFIG)
    p = Path(path) if path else CONFIG_PATH
    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            log(f'warning: config {p.name} не читается ({exc}), беру default')
            return cfg
        for k, v in data.items():
            if v is not None:
                cfg[k] = v
    return cfg


# ------------------------------------------------------- Ollama (§2.2, §3 тест 3)
def _http_json(url, payload=None, timeout=10):
    """GET (payload=None) / POST JSON, парсинг ответа. Исключения — наружу."""
    if payload is None:
        req = urllib.request.Request(url, method='GET')
    else:
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            url, data=body, method='POST',
            headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8', 'replace'))


def ollama_available(base_url, timeout=5):
    """Доступна ли Ollama (GET <base>/api/tags). True/False."""
    try:
        data = _http_json(base_url.rstrip('/') + '/api/tags', timeout=timeout)
    except (urllib.error.URLError, OSError, ValueError):
        return False
    return isinstance(data, dict)


def model_available(base_url, model, timeout=5):
    """Есть ли модель среди локальных (ollama list). Предупреждение, не ошибка."""
    try:
        data = _http_json(base_url.rstrip('/') + '/api/tags', timeout=timeout)
    except (urllib.error.URLError, OSError, ValueError):
        return False
    names = [m.get('name', '') for m in data.get('models', [])]
    if model in names:
        return True
    stem = model.split(':')[0]
    return any(n.split(':')[0] == stem for n in names)


def call_ollama(base_url, payload, timeout):
    """POST /api/chat.

    None — Ollama недоступна (connection refused/unreachable) -> обмен
    прерывается с exit 1 (§3 тест 3). {'error': ...} — HTTP-ошибка или таймаут
    ожидания ответа (модель грузится дольше timeout) -> батч пропускается,
    прогон продолжается: это медленная модель, а не отсутствующий сервис.
    """
    try:
        return _http_json(base_url.rstrip('/') + '/api/chat', payload,
                          timeout=timeout)
    except urllib.error.HTTPError as exc:
        detail = ''
        try:
            detail = exc.read().decode('utf-8', 'replace')[:300]
        except Exception:
            pass
        log(f'warning: ollama HTTP {exc.code}: {detail}')
        return {'error': f'HTTP {exc.code}'}
    except (socket.timeout, TimeoutError) as exc:
        log(f'warning: ollama: таймаут ответа ({exc}) — батч пропущен')
        return {'error': 'timeout'}
    except urllib.error.URLError as exc:
        log(f'warning: ollama недоступна ({exc.reason})')
        return None
    except OSError as exc:
        if isinstance(exc, ConnectionError):
            log(f'warning: ollama недоступна ({exc})')
            return None
        log(f'warning: ollama: ошибка соединения ({exc}) — батч пропущен')
        return {'error': str(exc)}


# ------------------------------------------------------------------ промпт (§2.3)
def build_prompt(batch):
    """Обёрточный user-промпт (DS_082b §2.3): английский, few-shot.

    Формат «line N, code: <code>, rule: <rule_code>, hint: <description>» и
    ровно один пример-образец ответа. Модель обязана вернуть JSON-массив без
    markdown и без объяснений.
    """
    lines = [
        'You are a PL/SQL to PostgreSQL migration expert. Fix the issues below.',
        '',
        'EXAMPLE:',
        'Issue: line 32, code: IS_EOD_NEW boolean;, rule: BAD_PREFIX, '
        'hint: rename to v_bIS_EOD_NEW',
        'Fix: {"id": 1, "line": 32, "before": "...", "after": "...", '
        '"reason": "...", "confidence": 0.95}',
        '',
        'ISSUES:',
        '',
    ]
    for iss in batch:
        desc = (iss.get('description') or '').strip().replace('\n', ' ')
        code = (iss.get('code') or '').rstrip('\n')
        lines.append(
            f'line {iss["line"]}, code: {code}, '
            f'rule: {iss.get("rule_code", "")}, hint: {desc}')
    lines += [
        '',
        f'Return ONLY a JSON array with exactly {len(batch)} elements '
        f'(one per issue above, do not repeat the example). '
        f'No explanations, no markdown, no code fences.',
    ]
    return '\n'.join(lines)


def content_of(answer):
    """Текст модели из ответа /api/chat (message.content) или /api/generate."""
    if not isinstance(answer, dict):
        return ''
    msg = answer.get('message')
    if isinstance(msg, dict) and msg.get('content'):
        return str(msg['content'])
    if answer.get('response'):
        return str(answer['response'])
    return ''


# --------------------------------------------------------- парсинг и валидация (§2.7)
def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _after_of(item):
    """after: строка или None (null = удалить строку — контракт apply_fixes)."""
    if 'after' not in item:
        return None
    value = item['after']
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return str(value)


def normalize_fixes(parsed, batch, model):
    """Ответ модели -> element-ы контракта DS_054 (§2.7).

    Element = {id, line, before, after, reason, confidence} — ровно как в
    rule_based_fixer.write_response (DS_082a §5.1), иначе apply_fixes (DS_054
    §2.6) не увидит строку: он читает fix['line'], а не fix['line_number'].

    Валидация (§2.1/§2.7): каждый issue батча должен получить ровно один
    элемент ответа. Промпт (§2.3) не содержит id (только line), поэтому
    сопоставление — по строке `line` (с потреблением элементов, чтобы
    корректно обработать несколько issue на одной строке), а при отсутствии
    совпадения — по порядку. Лишние элементы (например, эхо-повтор примера из
    промпта) игнорируются; если хотя бы для одного issue элемента нет — []
    (весь батч пропускается).
    `before` берётся из запроса, а не из ответа модели — это гарантирует
    совпадение с фактической строкой файла при apply_fixes (before mismatch).
    """
    if not isinstance(parsed, list) or not parsed:
        return []
    remaining = [c for c in parsed if isinstance(c, dict)]
    by_id = {}
    for iss in batch:
        idx = next((i for i, c in enumerate(remaining)
                    if c.get('line') == iss['line']), None)
        if idx is None:
            if not remaining:
                return []
            idx = 0
        by_id[iss['id']] = remaining.pop(idx)

    fixes = []
    for iss in batch:
        item = by_id[iss['id']]
        model_reason = str(item.get('reason', '')).strip()
        fixes.append({
            'id': iss['id'],
            'line': iss['line'],
            'before': iss.get('code') or '',
            'after': _after_of(item),
            'reason': f'ai-local: {model} — {model_reason}' if model_reason
                      else f'ai-local: {model}',
            'confidence': _to_float(item.get('confidence')),
        })
    return fixes


# ------------------------------------------------------------------ классификация (§2.7)
def classify_fix(fix):
    """Класс применения по confidence (DS_082b §2.7)."""
    conf = _to_float(fix.get('confidence'))
    if fix.get('after') is None:
        return 'noop' if conf >= CLASSIFY_RULE['min_confidence_medium'] else 'manual'
    if conf >= CLASSIFY_RULE['min_confidence_auto']:
        return 'auto'
    if conf >= CLASSIFY_RULE['min_confidence_medium']:
        return 'medium'
    return 'manual'


def classify_distribution(fixes):
    dist = {'auto': 0, 'medium': 0, 'manual': 0, 'noop': 0}
    for fix in fixes:
        dist[classify_fix(fix)] += 1
    return dist


# ---------------------------------------------------------------- запись ответа (§2.7)
def _request_tail(request_path):
    """PSH_DEP_PRIV_GO_20260926_114002 из AI_REQUEST_PSH_DEP_PRIV_GO_..._...md."""
    name = request_path.name
    if name.startswith(REQUEST_PREFIX):
        name = name[len(REQUEST_PREFIX):]
    if name.endswith('.md'):
        name = name[:-3]
    return name


def _meta_of(request_path, section):
    """Поле из блока «## Метаданные» запроса (переносится в ответ).

    В AI_REQUEST поля русские («Источник», «Рубрикатор») — как _RE_SOURCE в
    rule_based_fixer; поддержаны и английские имена.
    """
    aliases = {'source_file': ('Источник', 'source_file'),
               'rubricator': ('Рубрикаторы', 'rubricator')}
    try:
        text = Path(request_path).read_text(encoding='utf-8')
    except OSError:
        return ''
    for name in aliases.get(section, (section,)):
        m = re.search(r'^-\s*' + re.escape(name) + r':\s*(.+)$', text,
                      re.MULTILINE)
        if m:
            return m.group(1).strip()
    return ''


def write_response(request, fixes, out_dir):
    """AI_RESPONSE_<tail>.md — формат rule_based_fixer (DS_082a §5.1).

    request — dict от parse_request ({path, source, issues}); имя ответа
    строится из хвоста имени запроса, чтобы receive_from_ai (DS_054 §2.5)
    нашёл пару «запрос <-> ответ» (_find_request_for_response).

    Пустой список фиксов -> файл не пишется (§2.7: нерешённые issues остаются
    в AI — АРМ увидит no_fixes и ничего не применит).
    """
    if not fixes:
        return None
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    req_path = Path(request['path'])
    tail = _request_tail(req_path)
    path = out_dir / f'{RESPONSE_PREFIX}{tail}.md'
    lines = [
        f'# {RESPONSE_PREFIX}{tail}',
        '',
        '## Метаданные',
        f'- source_file: {request.get("source") or _meta_of(req_path, "source_file")}',
        f'- request: {req_path.name}',
        f'- rubricator: {_meta_of(req_path, "rubricator")}',
        f'- model: {request.get("model", "")}',
        f'- generated_at: {datetime.now().isoformat(timespec="seconds")}',
        '',
        '## Фиксы',
        '',
        '```json',
        json.dumps(fixes, ensure_ascii=False, indent=2),
        '```',
        '',
    ]
    path.write_text('\n'.join(lines), encoding='utf-8')
    return path


# ------------------------------------------------------------------ батчи и прогон
def chunked(items, size):
    """Разбить на батчи по size (§2.2 batch_size=5)."""
    size = max(int(size), 1)
    return [items[i:i + size] for i in range(0, len(items), size)]


def run_request(request_path, out_dir, cfg, skip_rule_codes=None, limit=None,
                metrics_path=None, filter_type=None, dry_run=False,
                verbose=False):
    """Обработать один AI_REQUEST батчами.

    Возвращает (stats, fixes). fixes is None — Ollama отвалилась в процессе:
    вызывающий обязан вернуть exit 1 и НЕ создавать AI_RESPONSE (§3 тест 3).

    skip_rule_codes — исключить правила (стенды, где часть уже закрыта
    rule-based fixer'ом). filter_type — оставить только это правило
    (§2.7 --filter-type, тест 2). limit — только первые N issues.
    dry_run — смоделировать батчи без запроса к Ollama и без записи ответа
    (§2.7 --dry-run, тест 4). verbose — печатать промпт и ответ каждого батча.
    """
    request_path = Path(request_path)
    request = parse_request(request_path)      # {path, source, issues} (§2.2)
    issues = request['issues']
    if skip_rule_codes:
        skip = set(skip_rule_codes)
        issues = [i for i in issues if i.get('rule_code') not in skip]
    if filter_type:
        issues = [i for i in issues if filter_type in i.get('rule_code', '')]
    if limit:
        issues = issues[:int(limit)]

    stats = {
        'request': request_path.name,
        'issues': len(issues),
        'batch_size': int(cfg['batch_size']),
        'batches': 0,
        'fixed': 0,
        'skipped_batches': 0,
        'invalid_json': 0,
        'ollama_errors': 0,
        'batch_times_sec': [],
        'confidences': [],
        'model': cfg['model'],
    }
    if not issues:
        log(f'{request_path.name}: issues нет — пропускаю')
        stats['classification'] = classify_distribution([])
        return stats, []

    batches = chunked(issues, cfg['batch_size'])
    stats['batches'] = len(batches)
    log(f'{request_path.name}: {len(issues)} issues, {len(batches)} батч(ов) '
        f'по {cfg["batch_size"]}, модель {cfg["model"]}')

    if dry_run:
        # --dry-run (§2.7, тест 4): план батчей без обращения к Ollama.
        for n, batch in enumerate(batches, 1):
            ids = [b['id'] for b in batch]
            log(f'dry-run batch {n}/{len(batches)} ids={ids}: '
                f'{len(batch)} issues, prompt {len(build_prompt(batch))} '
                f'символов')
            if verbose:
                print(build_prompt(batch))
        log(f'{request_path.name}: dry-run — {len(batches)} батч(ов), '
            f'Ollama не запрошена, AI_RESPONSE не создан', bot=True)
        stats['classification'] = classify_distribution([])
        return stats, []

    system_msgs = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    fixes_all = []
    for n, batch in enumerate(batches, 1):
        payload = {
            'model': cfg['model'],
            'messages': system_msgs + [
                {'role': 'user', 'content': build_prompt(batch)}],
            'stream': False,
            # JSON-схема (structured output) — Ollama возвращает валидный
            # массив фиксов без markdown (§2.3: «no markdown, no code fences»).
            'format': FIX_SCHEMA,
            'options': {
                'temperature': float(cfg['temperature']),
                'num_ctx': int(cfg['num_ctx']),
                'num_predict': int(cfg['max_tokens']),
            },
        }
        ids = [b['id'] for b in batch]
        t0 = time.monotonic()
        answer = call_ollama(cfg['ollama_url'], payload,
                             int(cfg['timeout_sec']))
        dt = time.monotonic() - t0
        stats['batch_times_sec'].append(round(dt, 1))
        if answer is None:
            log('ollama unavailable')
            stats['ollama_errors'] += 1
            return stats, None

        if str(answer.get('error', '')):
            log(f'batch {n}/{len(batches)} ids={ids}: ollama error '
                f'({answer["error"]}) — батч пропущен')
            stats['skipped_batches'] += 1
            continue

        parsed = extract_json_array(content_of(answer))
        fixes = normalize_fixes(parsed, batch, cfg['model'])
        if not fixes:
            got = len(parsed) if isinstance(parsed, list) else 'нет JSON'
            log(f'batch {n}/{len(batches)} ids={ids}: невалидный JSON '
                f'(элементов {got}, ожидалось {len(batch)}) — issues батча '
                f'остаются в AI')
            stats['invalid_json'] += 1
            stats['skipped_batches'] += 1
            continue
        fixes_all.extend(fixes)
        stats['fixed'] += len(fixes)
        stats['confidences'].extend(f['confidence'] for f in fixes)
        log(f'batch {n}/{len(batches)} ids={ids}: fixes={len(fixes)} '
            f'время={dt:.1f}с conf='
            f'{[round(f["confidence"], 2) for f in fixes]}')

    resp = write_response(request, fixes_all, out_dir)
    stats['response'] = resp.name if resp else None
    stats['classification'] = classify_distribution(fixes_all)
    if fixes_all:
        avg_conf = sum(stats['confidences']) / len(stats['confidences'])
        avg_time = sum(stats['batch_times_sec']) / len(stats['batch_times_sec'])
        pct = stats['fixed'] * 100 // stats['issues'] if stats['issues'] else 0
        log(f'{request_path.name}: итог {stats["fixed"]} из {stats["issues"]} '
            f'({pct}%), batch={stats["batches"]}, invalid_json='
            f'{stats["invalid_json"]}, skip_batch={stats["skipped_batches"]}, '
            f'avg_time={avg_time:.1f}с, avg_conf={avg_conf:.2f}, '
            f'class={stats["classification"]}, response={resp.name}', bot=True)
    else:
        log(f'{request_path.name}: 0 fixes — AI_RESPONSE не создан '
            f'(issues остаются в AI)', bot=True)
    if metrics_path:
        try:
            mp = Path(metrics_path)
            mp.parent.mkdir(parents=True, exist_ok=True)
            mp.write_text(json.dumps(stats, ensure_ascii=False, indent=2),
                          encoding='utf-8')
        except OSError as exc:
            log(f'warning: метрики не записаны ({exc})')
    return stats, fixes_all


# ------------------------------------------------------------------------- CLI
def build_parser():
    p = argparse.ArgumentParser(
        prog='ai_local_worker.py',
        description='DS_082b: закрыть AI-issues через локальную LLM (Ollama), '
                    'батчами, с записью AI_RESPONSE в контрактном формате DS_054.')
    p.add_argument('--request', help='AI_REQUEST_*.md (EXCHANGE\AI_IN\...)')
    p.add_argument('--out', help='Каталог для AI_RESPONSE (default EXCHANGE\AI_OUT)')
    p.add_argument('--in-dir', help='Пакетный режим: каталог с AI_REQUEST_*.md')
    p.add_argument('--out-dir', help='Пакетный режим: каталог для AI_RESPONSE')
    p.add_argument('--config', default=None,
                   help=f'JSON-конфиг (default {CONFIG_PATH.name})')
    p.add_argument('--model', default=None, help='Override модели Ollama')
    p.add_argument('--batch-size', type=int, default=None,
                   help='Override batch_size (default 5)')
    p.add_argument('--timeout', type=int, default=None,
                   help='Override timeout_sec (default 600)')
    p.add_argument('--ollama-url', default=None,
                   help='Override ollama_url (default http://localhost:11434)')
    p.add_argument('--skip-rule', action='append', default=[],
                   help='Исключить правило (повторяемо) — стенды после '
                        'rule-based fixer')
    p.add_argument('--filter-type', action='append', default=[],
                   help='Закрыть только issues этого типа rule-based fixer '
                        '(rubric 03/05/06/11) — стенды после rule-based')
    p.add_argument('--limit', type=int, default=None,
                   help='Только первые N issues (быстрые тесты)')
    p.add_argument('--dry-run', action='store_true',
                   help='План батчей без обращения к Ollama: сколько батчей, '
                        'по 5 issues, prompt-формат (тест 4)')
    p.add_argument('--metrics', default=None,
                   help='Записать статистику прогонов в JSON')
    p.add_argument('--check', action='store_true',
                   help='Только проверить доступность Ollama и выйти')
    p.add_argument('--list-models', action='store_true',
                   help='Списать модели Ollama (/api/tags) и выйти')
    p.add_argument('--verbose', action='store_true',
                   help='Печатать prompt каждого батча')
    return p


def list_models(base_url):
    """Модели из GET /api/tags (для --list-models)."""
    data = _http_json(f'{base_url.rstrip("/")}/api/tags')
    return [m.get('name', '?') for m in data.get('models', [])]


def main(argv=None):
    args = build_parser().parse_args(argv)

    cfg = load_config(args.config)
    if args.model:
        cfg['model'] = args.model
    if args.batch_size:
        cfg['batch_size'] = args.batch_size
    if args.timeout:
        cfg['timeout_sec'] = args.timeout
    if args.ollama_url:
        cfg['ollama_url'] = args.ollama_url.rstrip('/')

    if args.list_models:
        try:
            names = list_models(cfg['ollama_url'])
        except (urllib.error.URLError, OSError) as exc:
            log(f'ollama unavailable: {exc} (нет ответа {cfg["ollama_url"]})')
            return 1
        if not names:
            log(f'models: нет (Ollama {cfg["ollama_url"]} не вернула моделей)')
            return 0
        log('models: ' + ', '.join(names))
        return 0

    if args.check:
        if ollama_available(cfg['ollama_url']):
            log(f'ollama available: {cfg["ollama_url"]} (model={cfg["model"]})')
            return 0
        log(f'ollama unavailable: {cfg["ollama_url"]} — AI_RESPONSE не '
            f'создаётся (обмен не начинается)')
        return 1

    jobs = []
    if args.request:
        req = Path(args.request)
        if not req.is_file():
            log(f'ошибка: запрос не найден: {req}')
            return 2
        jobs.append((req, Path(args.out) if args.out else AI_OUT_DIR))
    elif args.in_dir:
        for req in sorted(Path(args.in_dir).glob(f'{REQUEST_PREFIX}*.md')):
            jobs.append((req, Path(args.out_dir) if args.out_dir else AI_OUT_DIR))
        if not jobs:
            log(f'ошибка: в {args.in_dir} нет {REQUEST_PREFIX}*.md')
            return 2
    else:
        log('ошибка: нужен --request или --in-dir (--check — проверить Ollama)')
        return 2

    all_stats, aborted = [], False
    for req, out in jobs:
        stats, fixes = run_request(req, out, cfg,
                                   skip_rule_codes=args.skip_rule,
                                   limit=args.limit,
                                   filter_type=args.filter_type,
                                   dry_run=args.dry_run,
                                   verbose=args.verbose)
        all_stats.append(stats)
        if fixes is None:                       # Ollama отвалилась в процессе
            log('ollama unavailable: обмен прерван, AI_RESPONSE не создаётся')
            aborted = True
            break

    if args.metrics:
        try:
            mp = Path(args.metrics)
            mp.parent.mkdir(parents=True, exist_ok=True)
            mp.write_text(json.dumps(all_stats, ensure_ascii=False, indent=2),
                          encoding='utf-8')
        except OSError as exc:
            log(f'warning: метрики не записаны ({exc})')
    return 1 if aborted else 0


if __name__ == '__main__':
    sys.exit(main())
