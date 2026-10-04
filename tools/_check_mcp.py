import yaml, sys
d = yaml.safe_load(open(r'F:\TO_DBI\.continue\config.yaml', encoding='utf-8'))
m = [s['name'] for s in d.get('mcpServers', [])]
assert sorted(m) == ['filesystem', 'git', 'shell'], 'mcpServers wrong: %s' % m
# Check env params
for s in d['mcpServers']:
    if s['name'] == 'shell':
        assert 'MCP_SHELL_ALLOW' in s.get('env', {}), 'MCP_SHELL_ALLOW missing'
    elif s['name'] == 'git':
        assert s.get('env', {}).get('MCP_GIT_MODE') == 'readonly', 'git not readonly'
    elif s['name'] == 'filesystem':
        assert 'MCP_FS_ROOTS_RW' in s.get('env', {}), 'ROOTS_RW missing'
        assert 'MCP_FS_ROOTS_RO' in s.get('env', {}), 'ROOTS_RO missing'
sys.exit(0)
