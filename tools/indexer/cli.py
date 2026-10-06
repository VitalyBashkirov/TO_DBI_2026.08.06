# -*- coding: utf-8 -*-
"""DS_CNT_005c: CLI interface."""
import sys
import argparse
from . import config, indexer, query, store


def main():
    try:
        parser = argparse.ArgumentParser(description='DS_CNT_005c Indexer')
        sub = parser.add_subparsers(dest='cmd')

        p_idx = sub.add_parser('index', help='Build/update index')
        p_idx.add_argument('--path', default=config.ARM_ROOT)
        p_idx.add_argument('--full', action='store_true')

        p_q = sub.add_parser('query', help='Semantic search')
        p_q.add_argument('text')
        p_q.add_argument('--top', type=int, default=5)

        sub.add_parser('stats', help='Index statistics')

        args = parser.parse_args()

        if args.cmd == 'index':
            result = indexer.run_index(root=args.path, full=args.full)
            print('Index done: %d files, %d chunks, %d embedded (%.1fs)' %
                  (result['files'], result['chunks'], result['embedded'], result['time']))
            return 0

        elif args.cmd == 'query':
            results = query.query(args.text, top_k=args.top)
            if not results:
                print('No results (index empty or Ollama unavailable).')
                return 1
            print('Top-%d results for: %s' % (args.top, args.text))
            print('-' * 60)
            for i, r in enumerate(results, 1):
                print('%d. [%.3f] %s (chunk %d)' % (i, r['score'], r['file'], r['chunk_no']))
                print('   %s...' % r['text'][:100])
            return 0

        elif args.cmd == 'stats':
            conn = store.init_db()
            count = store.count_chunks(conn)
            files = conn.execute('SELECT COUNT(DISTINCT file) FROM chunks').fetchone()[0]
            conn.close()
            print('Index stats:')
            print('  Chunks: %d' % count)
            print('  Files: %d' % files)
            print('  DB: %s' % config.DB_PATH)
            print('  NPY: %s' % config.NPY_PATH)
            return 0

        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        # DS_100a: graceful exit pri Ctrl+C (analog SIGINT — 130)
        print("\n[DS_100a] Interrupted by user (Ctrl+C / window close)", flush=True)
        return 130


if __name__ == '__main__':
    sys.exit(main())
