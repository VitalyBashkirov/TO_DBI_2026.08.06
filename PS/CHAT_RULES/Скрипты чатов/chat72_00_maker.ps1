Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$Scripts = 'F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов'
$Gen = Join-Path $Scripts 'chat72_00_maker.py'

$py = New-Object System.Collections.Generic.List[string]
$py.Add("# -*- coding: utf-8 -*-")
$py.Add("import os")
$py.Add("")
$py.Add("REPORTS = r'F:\TO_DBI\PS\CHAT_RULES\Отчеты'")
$py.Add("STARTS  = r'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов'")
$py.Add("PAMYATKA = os.path.join(REPORTS, 'Памятка_чатов.txt')")
$py.Add("REPORT71 = os.path.join(REPORTS, '71.Отчёт.txt')")
$py.Add("START72  = os.path.join(STARTS,  '72.Старт.txt')")
$py.Add("")
$py.Add("def w_nobom(path, text):")
$py.Add("    with open(path, 'w', encoding='utf-8', newline='\n') as f:")
$py.Add("        f.write(text)")
$py.Add("    print('WRITE:', os.path.basename(path), 'len=', len(text))")
$py.Add("")
$py.Add("def main():")
$py.Add("    lines = []")
$py.Add("    if os.path.exists(PAMYATKA):")
$py.Add("        with open(PAMYATKA, 'r', encoding='utf-8') as f:")
$py.Add("            lines = f.read().splitlines()")
$py.Add("    print('PAMYATKA lines=', len(lines))")
$py.Add("")
$py.Add("    m71 = 'Чат 71:'")
$py.Add("    l71 = 'Чат 71: LG 2026-10-27 — ЗАКРЫТ. Долг 1: _plp_iter_declarations + NAME in [TYPE]; _check_plp_not_mentioned: public func/proc, procedure, method, batch method. Фикс elif == ''in'' (integer не превращается в in). Тест test_ds71_not_mentioned_real.py (3 теста) + fixtures/ds71_in_type.plp. Коммит b3100ad (3 files, 150 ins), push OK, HEAD=origin. Регресс 389 passed / 0 failed.'")
$py.Add("    m72 = 'Чат 72:'")
$py.Add("    l72 = 'Чат 72: LG 2026-10-27 — старт. Долги: 1) throw->return в PS 5.1; 2) сообщения proc/method; 3) type_str in не нормализован; 4) грязные фоновые не коммитить; 5) *.ds*bak не коммитить.'")
$py.Add("")
$py.Add("    out = []")
$py.Add("    seen71 = False")
$py.Add("    seen72 = False")
$py.Add("    for ln in lines:")
$py.Add("        if ln.startswith(m71):")
$py.Add("            out.append(l71); seen71 = True; continue")
$py.Add("        if ln.startswith(m72):")
$py.Add("            out.append(l72); seen72 = True; continue")
$py.Add("        out.append(ln)")
$py.Add("    if not seen71: out.append(l71)")
$py.Add("    if not seen72: out.append(l72)")
$py.Add("    w_nobom(PAMYATKA, '\n'.join(out) + '\n')")
$py.Add("    print('OK pamyatka')")
$py.Add("")
$py.Add("    rep = []")
$py.Add("    rep.append('# Отчёт чата 71 (2026-10-27, LG)')")
$py.Add("    rep.append('')")
$py.Add("    rep.append('## Главное')")
$py.Add("    rep.append('- Долг 1 (из чата 70) ЗАКРЫТ: _plp_iter_declarations + NAME in [TYPE]; _check_plp_not_mentioned + public func/proc, procedure, method, batch method.')")
$py.Add("    rep.append('- scanner.py: +21/-0 (git diff --numstat 21 0), LF, py_compile=0 strict_syntax=0.')")
$py.Add("    rep.append('- Тест test_ds71_not_mentioned_real.py (3 теста) + fixtures/ds71_in_type.plp.')")
$py.Add("    rep.append('- Полный регресс: 389 passed / 0 failed (386 + 3 новых).')")
$py.Add("    rep.append('- Коммит b3100ad (3 files, 150 insertions), push OK, HEAD==origin, ahead нет.')")
$py.Add("    rep.append('')")
$py.Add("    rep.append('## Что сделано')")
$py.Add("    rep.append('- 71_00: старт, Памятка (chat71_00_maker.py).')")
$py.Add("    rep.append('- 71_01..71_01c: разведка _plp_iter_declarations и _check_plp_not_mentioned в SRC/analyzer/scanner.py; фикстуры patch_suboptimal_test_3.')")
$py.Add("    rep.append('- 71_02..71_02b: зонд дизайна + своя фикстура ds71_in_type.plp (in [TYPE], public func/proc, method, batch method, used, Default_Mes).')")
$py.Add("    rep.append('- 71_03..71_03h: патч scanner.py через 6 .txt-фрагментов + короткий python-патчер (PS-экранирование, 61_5/64_2/66_1).')")
$py.Add("    rep.append('- 71_03i..71_03k: диагностика, LF-нормализация, фикс elif == 'in' (integer не превращается в in).')")
$py.Add("    rep.append('- 71_04..71_04d: test_ds71_not_mentioned_real.py (фикс \\\\s/\\\\w), 13 passed в точечном.')")
$py.Add("    rep.append('- 71_05: полный регресс 389 passed / 0 failed.')")
$py.Add("    rep.append('- 71_06: коммит b3100ad, push OK, HEAD==origin. Предохранитель throw не прервал (долг 1).')")
$py.Add("    rep.append('')")
$py.Add("    rep.append('## Долги 71 -> 72')")
$py.Add("    rep.append('1. throw без try/catch в PS 5.1 не прерывает скрипт. Заменить на return + Stop-Transcript или try/catch.')")
$py.Add("    rep.append('2. _check_plp_not_mentioned: kind proc/method/batch_method -> ветка else. Кандидат: отдельные сообщения.')")
$py.Add("    rep.append('3. type_str для in [TYPE] не нормализован до ''in''. Намеренно; отдельная правка.')")
$py.Add("    rep.append('4. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1, free_memory.ps1, free_memory_profiles.txt) — не коммитить.')")
$py.Add("    rep.append('5. Бэкапы *.ds*bak — не коммитить; при желании — .gitignore.')")
$py.Add("    rep.append('')")
$py.Add("    rep.append('## Артефакты')")
$py.Add("    rep.append('- Коммит: b3100ad (3 files: scanner.py + test_ds71_not_mentioned_real.py + fixtures/ds71_in_type.plp, +150).')")
$py.Add("    rep.append('- Бэкапы: scanner.py.ds71_03bak, scanner.py.ds71_03k_prev, scanner.py.ds70_01bak (не коммитились).')")
$py.Add("    rep.append('- Патчеры: chat71_03_patch_scanner.py, chat71_03k_fix_in_type.py, chat71_04d_fix_test.py.')")
$py.Add("    rep.append('- Мейкеры: chat71_00_maker.py, chat72_00_maker.py.')")
$py.Add("    rep.append('- Зонды: chat71_02_probe.py, chat71_02b_probe_fixture.py, chat71_04b_probe_not_mentioned.py.')")
$py.Add("    rep.append('- Фрагменты: chat71_03_frag_*.txt (6 шт.).')")
$py.Add("    rep.append('- Логи: F:\\\\TO_DBI\\\\PS\\\\LG_71_*.log.')")
$py.Add("    w_nobom(REPORT71, '\n'.join(rep) + '\n')")
$py.Add("")
$py.Add("    st = []")
$py.Add("    st.append('============================================')")
$py.Add("    st.append('  72.СТАРТ (сгенерировано 2026-10-27 из чата 71)')")
$py.Add("    st.append('  Хост: LGGRAMA8V7Q8U (hostTag=LG) / MATEBOOKE (hostTag=MBE)')")
$py.Add("    st.append('============================================')")
$py.Add("    st.append('')")
$py.Add("    st.append('## Где искать правила (ОБЯЗАТЕЛЬНО в новом чате)')")
$py.Add("    st.append(r'F:\TO_DBI\PS\CHAT_RULES\\')")
$py.Add("    st.append('  00_INDEX.md')")
$py.Add("    st.append('  Отчеты\\ — +71')")
$py.Add("    st.append('  Скрипты чатов\\ — +chat72_*')")
$py.Add("    st.append('  Старт новых чатов\\ — +72')")
$py.Add("    st.append('')")
$py.Add("    st.append('## Статус на 2026-10-27 (после чата 71)')")
$py.Add("    st.append('- HEAD = b3100ad. origin/feature/dockerization = b3100ad, ahead нет.')")
$py.Add("    st.append('- Долг 1 ЗАКРЫТ: _plp_iter_declarations + NAME in [TYPE]; _check_plp_not_mentioned + public func/proc, procedure, method, batch method.')")
$py.Add("    st.append('- Тест test_ds71_not_mentioned_real.py (3 теста) + fixtures/ds71_in_type.plp.')")
$py.Add("    st.append('- Полный регресс: 389 passed / 0 failed.')")
$py.Add("    st.append('')")
$py.Add("    st.append('## Долги 71 -> 72')")
$py.Add("    st.append('1. throw без try/catch в PS 5.1 не прерывает. Заменить на return + Stop-Transcript или try/catch.')")
$py.Add("    st.append('2. _check_plp_not_mentioned: kind proc/method/batch_method -> ветка else. Кандидат: отдельные сообщения.')")
$py.Add("    st.append('3. type_str in [TYPE] не нормализован до ''in''. Намеренно; отдельная правка при необходимости.')")
$py.Add("    st.append('4. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1, free_memory.ps1, free_memory_profiles.txt) — не коммитить.')")
$py.Add("    st.append('5. Бэкапы *.ds*bak — не коммитить; при желании — .gitignore.')")
$py.Add("    st.append('')")
$py.Add("    st.append('## Первые шаги чата 72')")
$py.Add("    st.append('1. Прочитать CHAT_RULES\\Старт новых чатов\\01_08 ...\\00_INDEX.md -> 01..08.')")
$py.Add("    st.append('2. Прочитать Отчеты\\71.Отчёт.txt.')")
$py.Add("    st.append('3. Взять долг 1 (throw->return) или долг 2 (сообщения proc/method) — или новую задачу.')")
$py.Add("    st.append('4. Действовать по регламентам: 04, 05, 06, 07, 61_1, 64_2, 64_3, 64_4, 65_1, 65_2, 66_1, 66_2, 67_1.')")
$py.Add("    st.append('')")
$py.Add("    st.append('## Правила PS (краткая выжимка)')")
$py.Add("    st.append('1-13, 60_1..60_9, 61_1..61_7, 62_1, 63_1, 64_1..64_4, 64_10, 65_1, 65_2, 66_1, 66_2, 67_1.')")
$py.Add("    w_nobom(START72, '\n'.join(st) + '\n')")
$py.Add("")
$py.Add("    print('DONE')")
$py.Add("")
$py.Add("if __name__ == '__main__':")
$py.Add("    main()")

$encBom = New-Object System.Text.UTF8Encoding($true)
[System.IO.File]::WriteAllLines($Gen, $py, $encBom)
$gb = [System.IO.File]::ReadAllBytes($Gen)
$gBom = ($gb.Length -ge 3 -and $gb[0] -eq 0xEF -and $gb[1] -eq 0xBB -and $gb[2] -eq 0xBF)
Write-Host ("GEN: $Gen size={0} isBom={1}" -f $gb.Length, $gBom)
if (-not $gBom) { throw "BOM не записан: $Gen" }

$pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pyCmd) { $python = $pyCmd.Source } else { throw "python.exe не найден" }
$log = 'F:\TO_DBI\PS\LG_71_07b_maker.log'
Start-Transcript -Path $log -Force
Write-Host "hostTag=LG host=$env:COMPUTERNAME"
$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& $python $Gen 2>&1 | Out-String | Write-Host
$rc = $LASTEXITCODE
$ErrorActionPreference = $oldEAP
Write-Host "maker_exitcode=$rc"

$Reports = 'F:\TO_DBI\PS\CHAT_RULES\Отчеты'
$Starts  = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов'
$encU = [System.Text.Encoding]::UTF8
$names = @(
  @{ P = (Join-Path $Reports 'Памятка_чатов.txt'); T = 'Памятка_чатов.txt' },
  @{ P = (Join-Path $Reports '71.Отчёт.txt');     T = '71.Отчёт.txt' },
  @{ P = (Join-Path $Starts  '72.Старт.txt');     T = '72.Старт.txt' }
)
foreach ($n in $names) {
    if (-not (Test-Path $n.P)) { Write-Host ("MISSING: {0}" -f $n.T); continue }
    $b = [System.IO.File]::ReadAllBytes($n.P)
    $isBom = ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
    Write-Host ("{0}: size={1} isBom={2}" -f $n.T, $b.Length, $isBom)
    if ($isBom) { throw ("BOM в .txt: {0}" -f $n.T) }
}

$pam = Join-Path $Reports 'Памятка_чатов.txt'
$t = [System.IO.File]::ReadAllText($pam, $encU)
$tl = $t -split "`r?`n"
Write-Host "--- pamyatka tail (last 4) ---"
($tl | Select-Object -Last 4) | ForEach-Object { Write-Host $_ }

$s72 = Join-Path $Starts '72.Старт.txt'
$t72 = [System.IO.File]::ReadAllText($s72, $encU)
$l72 = $t72 -split "`r?`n"
Write-Host "--- 72.Старт head (first 10) ---"
($l72 | Select-Object -First 10) | ForEach-Object { Write-Host $_ }

Stop-Transcript
Write-Host "PS1 LOG: $log" -ForegroundColor Green
