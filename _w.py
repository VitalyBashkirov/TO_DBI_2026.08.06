f = open('F:/TO_DBI_AGENTS.md', 'w', encoding='utf-8', newline='\r\n')
for line in lines:
    f.write(line + '\n')
f.close()
print('Done')
