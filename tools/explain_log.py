# -*- coding: utf-8 -*-
"""DS_CNT_007: explain-log.

Разбор последних N строк EXCHANGE\bot.log через локальную Ollama
(qwen2.5-coder:3b). Заменяет slash-команду /explain-log.

Write target: только logs\ (см. матрицу доступа CNT).
"""
import sys
import os
import json
import http.client

ARM_ROOT = r'F:\TO_DBI'
LOGS = os.path.join(ARM_ROOT, 'logs')
MODEL = 'qwen2.5-coder:3b'
OLLAMA_HOST = 'localhost'
OLLAMA_PORT = 11434
NUM_CTX = 4096
TAIL_LINES = 200
OUT_FILE = os.path.join(LOGS, 'ds_cnt_007_explain_log.md')
BOT_LOG = os.path.join(ARM_ROOT, 'EXCHANGE', 'bot.log')


def tail(path, n):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    return ''.join(lines[-n:])


def ollama_generate(prompt):
    payload = json.dumps({
        'model': MODEL,
        'prompt': prompt,
        'stream': False,
        'options': {'num_ctx': NUM_CTX, 'temperature': 0.1,
                    'num_predict': 600},
    }).encode('utf-8')
    conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=600)
    conn.request('POST', '/api/generate', body=payload,
                 headers={'Content-Type': 'application/json'})
    resp = conn.getresponse()
    body = resp.read().decode('utf-8')
    conn.close()
    if resp.status != 200:
        raise RuntimeError('Ollama %d: %s' % (resp.status, body[:200]))
    return json.loads(body).get('response', '')


def main():
    log_text = tail(BOT_LOG, TAIL_LINES)

    prompt = (
        'Разбери последние %d строк лога bot.log проекта TO_DBI.\n'
        'Формат записей: [ДД.ММ.ГГГГ ЧЧ:ММ:СС] DS XXX: <описание>.\n'
        'Выдели: (1) ошибки/невыполненные задачи; (2) предупреждения/'
        '"частично"/"приостановлен"; (3) аномалии (транслит вместо '
        'кириллицы, отсутствие даты, странные коды). По каждому — '
        'шаг диагностики. Кратко, списком.\n\n=== ЛОГ ===\n%s'
    ) % (TAIL_LINES, log_text)

    result = ollama_generate(prompt)

    os.makedirs(LOGS, exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('# /explain-log: bot.log (tail %d)\n\n' % TAIL_LINES)
        f.write('Модель: %s\n\n' % MODEL)
        f.write(result)

    print(result)
    return 0


if __name__ == '__main__':
    sys.exit(main())
