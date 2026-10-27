# -*- coding: utf-8 -*-
import os

REPORTS = r'F:\TO_DBI\PS\CHAT_RULES\Отчеты'
STARTS  = r'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов'
PAMYATKA = os.path.join(REPORTS, 'Памятка_чатов.txt')
REPORT71 = os.path.join(REPORTS, '71.Отчёт.txt')
START72  = os.path.join(STARTS,  '72.Старт.txt')

def w_nobom(path, text):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('WRITE:', os.path.basename(path), 'len=', len(text))

def main():
    lines = []
    if os.path.exists(PAMYATKA):
        with open(PAMYATKA, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
    print('PAMYATKA lines=', len(lines))

    m71 = 'Чат 71:'
    m72 = 'Чат 72:'
    l71 = 'Чат 71: LG 2026-10-27 — ЗАКРЫТ. Долг 1: _plp_iter_declarations + NAME in [TYPE]; _check_plp_not_mentioned + public func/proc, procedure, method, batch method. Фикс elif == in (integer не превращается в in). Тест test_ds71_not_mentioned_real.py (3 теста) + fixtures/ds71_in_type.plp. Коммит b3100ad (3 files, 150 ins), push OK, HEAD=origin. Регресс 389 passed / 0 failed.'
    l72 = 'Чат 72: LG 2026-10-27 — старт. Долги: 1) throw->return в PS 5.1; 2) сообщения proc/method; 3) type_str для in не нормализован; 4) грязные фоновые не коммитить; 5) *.ds*bak не коммитить.'

    out = []
    seen71 = False
    seen72 = False
    for ln in lines:
        if ln.startswith(m71):
            out.append(l71); seen71 = True; continue
        if ln.startswith(m72):
            out.append(l72); seen72 = True; continue
        out.append(ln)
    if not seen71: out.append(l71)
    if not seen72: out.append(l72)
    w_nobom(PAMYATKA, '\n'.join(out) + '\n')
    print('OK pamyatka')

    rep = []
    rep.append('# Отчёт чата 71 (2026-10-27, LG)')
    rep.append('')
    rep.append('## Главное')
    rep.append('- Долг 1 (из чата 70) ЗАКРЫТ: _plp_iter_declarations + NAME in [TYPE]; _check_plp_not_mentioned + public func/proc, procedure, method, batch method.')
    rep.append('- scanner.py: +21/-0 (git diff --numstat 21 0), LF, py_compile=0 strict_syntax=0.')
    rep.append('- Тест test_ds71_not_mentioned_real.py (3 теста) + fixtures/ds71_in_type.plp.')
    rep.append('- Полный регресс: 389 passed / 0 failed (386 + 3 новых).')
    rep.append('- Коммит b3100ad (3 files, 150 insertions), push OK, HEAD==origin, ahead нет.')
    rep.append('')
    rep.append('## Что сделано')
    rep.append('- 71_00: старт, Памятка (chat71_00_maker.py).')
    rep.append('- 71_01..71_01c: разведка _plp_iter_declarations и _check_plp_not_mentioned в SRC/analyzer/scanner.py; фикстуры patch_suboptimal_test_3.')
    rep.append('- 71_02..71_02b: зонд дизайна + своя фикстура ds71_in_type.plp (in [TYPE], public func/proc, method, batch method, used, Default_Mes).')
    rep.append('- 71_03..71_03h: патч scanner.py через 6 .txt-фрагментов + короткий python-патчер (PS-экранирование, 61_5/64_2/66_1).')
    rep.append('- 71_03i..71_03k: диагностика, LF-нормализация, фикс elif == in (integer не превращается в in).')
    rep.append('- 71_04..71_04d: test_ds71_not_mentioned_real.py (фикс regex), 13 passed в точечном.')
    rep.append('- 71_05: полный регресс 389 passed / 0 failed.')
    rep.append('- 71_06: коммит b3100ad, push OK, HEAD==origin. Предохранитель throw не прервал (долг 1).')
    rep.append('')
    rep.append('## Долги 71 -> 72')
    rep.append('1. throw без try/catch в PS 5.1 не прерывает скрипт. Заменить на return + Stop-Transcript или try/catch.')
    rep.append('2. _check_plp_not_mentioned: kind proc/method/batch_method -> ветка else. Кандидат: отдельные сообщения.')
    rep.append('3. type_str для in [TYPE] не нормализован до in. Намеренно; отдельная правка.')
    rep.append('4. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1, free_memory.ps1, free_memory_profiles.txt) — не коммитить.')
    rep.append('5. Бэкапы *.ds*bak — не коммитить; при желании — .gitignore.')
    rep.append('')
    rep.append('## Артефакты')
    rep.append('- Коммит: b3100ad (3 files: scanner.py + test_ds71_not_mentioned_real.py + fixtures/ds71_in_type.plp, +150).')
    rep.append('- Бэкапы: scanner.py.ds71_03bak, scanner.py.ds71_03k_prev, scanner.py.ds70_01bak (не коммитились).')
    rep.append('- Патчеры: chat71_03_patch_scanner.py, chat71_03k_fix_in_type.py, chat71_04d_fix_test.py.')
    rep.append('- Мейкеры: chat71_00_maker.py, chat72_00_maker.py.')
    rep.append('- Зонды: chat71_02_probe.py, chat71_02b_probe_fixture.py, chat71_04b_probe_not_mentioned.py.')
    rep.append('- Фрагменты: chat71_03_frag_*.txt (6 шт.).')
    rep.append('- Логи: F:\\TO_DBI\\PS\\LG_71_*.log.')
    w_nobom(REPORT71, '\n'.join(rep) + '\n')

    st = []
    st.append('============================================')
    st.append('  72.СТАРТ (сгенерировано 2026-10-27 из чата 71)')
    st.append('  Хост: LGGRAMA8V7Q8U (hostTag=LG) / MATEBOOKE (hostTag=MBE)')
    st.append('============================================')
    st.append('')
    st.append('## Где искать правила (ОБЯЗАТЕЛЬНО в новом чате)')
    st.append(r'F:\TO_DBI\PS\CHAT_RULES\')
    st.append('  00_INDEX.md')
    st.append('  Отчеты - +71')
    st.append('  Скрипты чатов - +chat72_*')
    st.append('  Старт новых чатов - +72')
    st.append('')
    st.append('## Статус на 2026-10-27 (после чата 71)')
    st.append('- HEAD = b3100ad. origin/feature/dockerization = b3100ad, ahead нет.')
    st.append('- Долг 1 ЗАКРЫТ: _plp_iter_declarations + NAME in [TYPE]; _check_plp_not_mentioned + public func/proc, procedure, method, batch method.')
    st.append('- Тест test_ds71_not_mentioned_real.py (3 теста) + fixtures/ds71_in_type.plp.')
    st.append('- Полный регресс: 389 passed / 0 failed.')
    st.append('')
    st.append('## Долги 71 -> 72')
    st.append('1. throw без try/catch в PS 5.1 не прерывает. Заменить на return + Stop-Transcript или try/catch.')
    st.append('2. _check_plp_not_mentioned: kind proc/method/batch_method -> ветка else. Кандидат: отдельные сообщения.')
    st.append('3. type_str для in [TYPE] не нормализован до in. Намеренно; отдельная правка при необходимости.')
    st.append('4. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1, free_memory.ps1, free_memory_profiles.txt) — не коммитить.')
    st.append('5. Бэкапы *.ds*bak — не коммитить; при желании — .gitignore.')
    st.append('')
    st.append('## Первые шаги чата 72')
    st.append('1. Прочитать CHAT_RULES/Старт новых чатов/01_08 .../00_INDEX.md -> 01..08.')
    st.append('2. Прочитать Отчеты/71.Отчёт.txt.')
    st.append('3. Взять долг 1 (throw->return) или долг 2 (сообщения proc/method) — или новую задачу.')
    st.append('4. Действовать по регламентам: 04, 05, 06, 07, 61_1, 64_2, 64_3, 64_4, 65_1, 65_2, 66_1, 66_2, 67_1.')
    st.append('')
    st.append('## Правила PS (краткая выжимка)')
    st.append('1-13, 60_1..60_9, 61_1..61_7, 62_1, 63_1, 64_1..64_4, 64_10, 65_1, 65_2, 66_1, 66_2, 67_1.')
    w_nobom(START72, '\n'.join(st) + '\n')

    print('DONE')

if __name__ == '__main__':
    main()
