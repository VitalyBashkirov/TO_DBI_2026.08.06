# -*- coding: utf-8 -*-
"""DS_CNT_005c: Semantic query (cosine similarity)."""
import numpy as np
from . import config, store, embedder


def query(text, top_k=5):
    conn = store.init_db()
    rows = store.get_all_embeddings(conn)
    conn.close()

    if not rows:
        return []

    stored_embs = store.load_embeddings_numpy()
    if stored_embs.size == 0 or len(stored_embs) != len(rows):
        return []

    try:
        q_emb = embedder.get_embedding(text)
    except RuntimeError:
        return []

    if not q_emb:
        return []

    q_vec = np.array(q_emb, dtype=np.float32)
    q_norm = np.linalg.norm(q_vec)
    if q_norm == 0:
        return []

    norms = np.linalg.norm(stored_embs, axis=1)
    norms[norms == 0] = 1

    sims = stored_embs.dot(q_vec) / (norms * q_norm)

    top_indices = np.argsort(sims)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if idx < len(rows):
            r = rows[idx]
            results.append({
                'file': r[1],
                'chunk_no': r[2],
                'text': r[3][:200],
                'score': float(sims[idx]),
            })
    return results
