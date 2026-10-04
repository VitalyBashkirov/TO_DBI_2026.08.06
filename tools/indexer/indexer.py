# -*- coding: utf-8 -*-
"""DS_CNT_005c: Main indexer loop."""
import os
import time
import logging
import numpy as np
from . import config, reader, embedder, store

LOG_PATH = os.path.join(config.ARM_ROOT, 'logs', 'ds_cnt_005c_index.log')
EXIT_PATH = os.path.join(config.ARM_ROOT, 'logs', 'ds_cnt_005c.exit')


def setup_logging():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        force=True,
    )


def _build_file_embedding_map(conn, old_numpy):
    """Map file -> [embeddings] from old DB rows + old numpy."""
    if old_numpy is None or old_numpy.size == 0:
        return {}
    rows = store.get_all_embeddings(conn)
    if len(rows) != old_numpy.shape[0]:
        return {}
    file_map = {}
    for i, row in enumerate(rows):
        f = row[1]
        if f not in file_map:
            file_map[f] = []
        file_map[f].append(old_numpy[i].tolist())
    return file_map


def run_index(root=None, full=False):
    setup_logging()
    log = logging.getLogger(__name__)
    log.info('=== DS_CNT_005c index START ===')
    t0 = time.time()

    conn = store.init_db()

    # Load old numpy for incremental runs
    old_numpy = None
    file_emb_map = {}
    if not full:
        old_numpy = store.load_embeddings_numpy()
        if old_numpy.size > 0:
            file_emb_map = _build_file_embedding_map(conn, old_numpy)
            log.info('Loaded %d old embeddings, %d file groups',
                     old_numpy.shape[0], len(file_emb_map))

    if full:
        log.info('Full reindex: clearing all chunks')
        store.full_reindex(conn)

    log.info('Reading files from %s', root or config.ARM_ROOT)
    files = reader.read_files(root)
    log.info('Found %d files to index', len(files))

    total_chunks = 0
    skipped = 0
    embedded = 0
    failed = 0

    for i, finfo in enumerate(files):
        filepath = finfo['file']
        filehash = finfo['hash']

        if not full and not store.needs_reindex(conn, filepath, filehash):
            skipped += 1
            continue

        store.clear_file(conn, filepath)
        file_emb_map.pop(filepath, None)
        chunks = reader.chunk_text(finfo['text'])
        if not chunks:
            continue

        hashes = [finfo['hash']] * len(chunks)
        store.insert_chunks(conn, filepath, chunks, hashes)
        total_chunks += len(chunks)

        file_embs = []
        for ch in chunks:
            emb = embedder.get_embedding(ch)
            if emb is not None:
                file_embs.append(emb)
                embedded += 1
            else:
                failed += 1
        if file_embs:
            file_emb_map[filepath] = file_embs

        if (i + 1) % 20 == 0:
            log.info('Progress: %d/%d files, %d chunks, %d embedded, %d failed',
                     i + 1, len(files), total_chunks, embedded, failed)

    # Rebuild complete numpy in DB row order
    all_rows = store.get_all_embeddings(conn)
    complete_numpy = []
    for row in all_rows:
        f = row[1]
        chunk_no = row[2]
        if f in file_emb_map and chunk_no < len(file_emb_map[f]):
            complete_numpy.append(file_emb_map[f][chunk_no])
        else:
            complete_numpy.append([0.0] * 768)

    store.save_embeddings_numpy(complete_numpy)
    count = store.count_chunks(conn)
    elapsed = time.time() - t0

    log.info('=== DS_CNT_005c index DONE ===')
    log.info('Files: %d, Skipped: %d, Chunks: %d, Embedded: %d, Failed: %d, '
             'Numpy rows: %d, DB rows: %d, Time: %.1fs',
             len(files), skipped, total_chunks, embedded, failed,
             len(complete_numpy), count, elapsed)

    with open(EXIT_PATH, 'w') as f:
        f.write('0')

    conn.close()
    return {
        'files': len(files),
        'skipped': skipped,
        'chunks': total_chunks,
        'embedded': embedded,
        'failed': failed,
        'total_in_db': count,
        'time': elapsed,
    }
