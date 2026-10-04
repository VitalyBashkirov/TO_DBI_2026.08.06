# -*- coding: utf-8 -*-
"""DS_CNT_005c: Ollama embedder (http.client + socket timeout + rate limit)."""
import socket
import json
import time
import http.client
from . import config

socket.setdefaulttimeout(15)
MAX_CHARS = 2048

# Rate limit: 1 req/sec (p. 1.14 regulation)
_last_request_time = 0.0
RATE_LIMIT_SEC = 1.0
MAX_RETRIES = 3
RETRY_PAUSE_SEC = 5.0


def _rate_limit():
    """Enforce minimum 1 sec between requests to Ollama."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < RATE_LIMIT_SEC:
        time.sleep(RATE_LIMIT_SEC - elapsed)
    _last_request_time = time.time()


def get_embedding(text):
    """Get embedding from Ollama with rate limit and retry."""
    text = text[:MAX_CHARS]
    for attempt in range(1, MAX_RETRIES + 1):
        _rate_limit()
        try:
            conn = http.client.HTTPConnection('localhost', 11434, timeout=15)
            payload = json.dumps({'model': config.MODEL, 'prompt': text})
            conn.request('POST', '/api/embeddings', body=payload,
                         headers={'Content-Type': 'application/json'})
            resp = conn.getresponse()
            body = resp.read()
            conn.close()
            if resp.status == 200:
                emb = json.loads(body).get('embedding', [])
                return emb if emb else None
            # Non-200: retry
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_PAUSE_SEC)
                continue
            return None
        except Exception:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_PAUSE_SEC)
                continue
            return None
    return None


def embed_batch(texts):
    """Embed list of texts with rate limit between each."""
    return [get_embedding(t) for t in texts]
