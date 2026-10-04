import yaml, sys
d = yaml.safe_load(open(r'F:\TO_DBI\.continue\config.yaml', encoding='utf-8'))
assert 'embeddingsProvider' in d, 'embeddingsProvider missing'
ep = d['embeddingsProvider']
assert ep.get('model') == 'nomic-embed-text', 'wrong model'
sys.exit(0)
