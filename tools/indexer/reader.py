# -*- coding: utf-8 -*-
"""DS_CNT_005c: File reader. DS_CNT_014: LARGE_FILE_LIMITS, EXCLUDE_FILES."""
import os
import fnmatch
import hashlib
from . import config


def is_excluded(path, rel_path):
    norm = rel_path.replace(chr(92), '/')
    parts = norm.split('/')
    for p in parts:
        if p in config.EXCLUDE_DIRS:
            return True
    for exc in config.EXCLUDE_SUBPATHS:
        if norm.startswith(exc):
            return True
    fname = os.path.basename(rel_path)
    for g in config.EXCLUDE_GLOBS:
        if fnmatch.fnmatch(fname, g):
            return True
    # DS_CNT_014: точные исключения файлов
    if norm in getattr(config, 'EXCLUDE_FILES', set()):
        return True
    # DS_CNT_014: исключить не-MD файлы в корне проекта
    root_globs = getattr(config, 'ROOT_EXCLUDE_GLOBS', set())
    if '/' not in norm:
        for pattern in root_globs:
            if fnmatch.fnmatch(fname, pattern):
                return True
    # DS_CNT_014: DATA/*.md — только корень DATA, подкаталоги индексируются
    if norm.startswith('DATA/') and norm.endswith('.md'):
        rest = norm[len('DATA/'):]
        if '/' not in rest:
            return True
    return False


def read_files(root=None):
    root = root or config.ARM_ROOT
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in config.EXCLUDE_DIRS]
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, root)
            if is_excluded(fpath, rel):
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in config.TEXT_EXTENSIONS:
                continue
            try:
                sz = os.path.getsize(fpath)
            except OSError:
                continue
            if sz > config.MAX_FILE_SIZE:
                continue
            # DS_CNT_014: фильтр больших файлов по расширению
            limits = getattr(config, 'LARGE_FILE_LIMITS', {})
            if ext in limits and sz > limits[ext]:
                continue
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            except OSError:
                continue
            if not text.strip():
                continue
            h = hashlib.sha256(text.encode()).hexdigest()[:16]
            results.append({
                'file': rel,
                'abs': fpath,
                'text': text,
                'hash': h,
                'size': sz,
            })
    return results


def chunk_text(text, size=None, overlap=None):
    size = size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP
    words = text.split()
    chunks = []
    step = size - overlap
    if step < 1:
        step = size
    for i in range(0, len(words), step):
        chunk_words = words[i:i + size]
        if chunk_words:
            chunks.append(' '.join(chunk_words))
        if i + size >= len(words):
            break
    return chunks
