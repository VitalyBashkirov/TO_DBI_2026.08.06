# -*- coding: utf-8 -*-
"""DS_CNT_005c: SQLite + numpy store."""
import os
import sqlite3
import numpy as np
from . import config


def init_db():
    os.makedirs(config.STORE_DIR, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file TEXT NOT NULL,
        chunk_no INTEGER NOT NULL,
        text TEXT NOT NULL,
        hash TEXT NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('schema_version', ?)",
                 (config.SCHEMA_VERSION,))
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('model', ?)",
                 (config.MODEL,))
    conn.commit()
    return conn


def get_hash_for_file(conn, filepath):
    row = conn.execute('SELECT hash FROM chunks WHERE file=? LIMIT 1',
                       (filepath,)).fetchone()
    return row[0] if row else None


def clear_file(conn, filepath):
    conn.execute('DELETE FROM chunks WHERE file=?', (filepath,))
    conn.commit()


def insert_chunks(conn, filepath, chunks, hashes):
    for i, (txt, h) in enumerate(zip(chunks, hashes)):
        conn.execute('INSERT INTO chunks (file, chunk_no, text, hash) VALUES (?,?,?,?)',
                     (filepath, i, txt, h))
    conn.commit()


def get_all_embeddings(conn):
    rows = conn.execute('SELECT id, file, chunk_no, text FROM chunks ORDER BY id').fetchall()
    return rows


def save_embeddings_numpy(embeddings):
    if embeddings:
        arr = np.array(embeddings, dtype=np.float32)
        np.save(config.NPY_PATH, arr)


def load_embeddings_numpy():
    if os.path.exists(config.NPY_PATH):
        return np.load(config.NPY_PATH)
    return np.array([], dtype=np.float32)


def count_chunks(conn):
    return conn.execute('SELECT COUNT(*) FROM chunks').fetchone()[0]


def needs_reindex(conn, filepath, filehash):
    old = get_hash_for_file(conn, filepath)
    return old != filehash


def full_reindex(conn):
    conn.execute('DELETE FROM chunks')
    conn.commit()
