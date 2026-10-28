Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root = 'F:\TO_DBI'
$relSelf = 'PS/CHAT_RULES/Скрипты чатов/chat77_01_reports.ps1'
$relRep68 = 'PS/CHAT_RULES/Отчеты/68.Отчёт.txt'
$relRep76 = 'PS/CHAT_RULES/Отчеты/76.Отчёт.txt'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_77_01_reports.log')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    $encNoBom = New-Object System.Text.UTF8Encoding($false)
    $p68 = Join-Path $root $relRep68
    $r68 = New-Object System.Collections.Generic.List[string]
    $r68.Add('# Отчёт чата 68 (2026-10-27..28, MBE)')
    $r68.Add('')
    $r68.Add('## Главное')
    $r68.Add('- DS_186: SUBOPTIMAL_QUERY_WROWNUM — расширен pattern (return/raise/pragma error/message.error/app_error).')
    $r68.Add('- scanner.py: r-for-pattern расширен; py_compile rc=0.')
    $r68.Add('- DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json: version 5.3.0 -> 5.3.1 + pattern. Восстановлен из backup_68.')
    $r68.Add('- SRC/tests/test_ds186_wrownum_return_pragma.py: config paths/scan (PLPlusScanner); 1 passed (68_06k).')
    $r68.Add('')
    $r68.Add('## ИНЦИДЕНТ 68: NTFS-порча F:')
    $r68.Add('- .git/objects битый (corrupt loose object: 0a0858, 131c64, 168f4f и др.).')
    $r68.Add('- .git восстановлен из origin/feature/dockerization (7b3fea6) через клон F:\TO_DBI_clone_20261028.')
    $r68.Add('- .gitignore был заменён транскриптом LG_74_05c_gitignore.log (2359 B).')
    $r68.Add('- .gitignore восстановлен из 53ec851 (PS/*, !PS/CHAT_RULES/, !PS/CHAT_RULES/**).')
    $r68.Add('- temp_broken_20261028\__init__.py — битый (WinError 1392), tools/ — битый, 69.Отчёт.txt — short read.')
    $r68.Add('- chkdsk F: /scan -> Access denied + snapshot error. /f offline — на LG (admin).')
    $r68.Add('')
    $r68.Add('## Коммиты 68')
    $r68.Add('- 68_06: 53ec851 (scanner.py + 4.RUBRICATOR_PROMPT v5.json 5.3.1 + test_ds186).')
    $r68.Add('- .git восстановлен из 7b3fea6; 53ec851 запушен в origin.')
    $r68.Add('')
    $r68.Add('## Долги 68 -> 77')
    $r68.Add('1. chkdsk F: /scan -> /f (LG, admin, offline). Починит temp_broken_20261028, tools/, .git/objects (старые).')
    $r68.Add('2. pytest.ini в SRC/tests — локальный обход temp; решить: коммит/ignore.')
    $r68.Add('3. 76.Старт.txt (53ec851) и 77.Старт.txt (f414282) — актуализировать на 8e13bf6.')
    [System.IO.File]::WriteAllLines($p68, $r68, $encNoBom)
    Write-Host 'report 68 written:' $p68 $r68.Count 'lines'
    $p76 = Join-Path $root $relRep76
    $r76 = New-Object System.Collections.Generic.List[string]
    $r76.Add('# Отчёт чата 76 (2026-10-28, MBE)')
    $r76.Add('')
    $r76.Add('## Главное')
    $r76.Add('- 76_00: старт (HEAD d5cc216).')
    $r76.Add('- 76_01d: ИКА — 3 .plp-фикстуры (sample_bad_prefix, sample_not_mentioned, sample_code_in_comment) + .gitignore PATCH_IN/* + самокоммит B.')
    $r76.Add('  Коммит: 8a148b3 (push 82d6e09..8a148b3).')
    $r76.Add('- 76_01f: fix test 02 (from analyzer import scanner) + .gitignore PATCH_IN/*. Коммит: 7b3fea6.')
    $r76.Add('  Причина: scanner.py в SRC/analyzer (не SRC); test_ds74_01_02 ожидал top-level scanner.')
    $r76.Add('- 68_06 (в чате 76): DS_186 fix — scanner.py + 4.RUBRICATOR_PROMPT v5.json 5.3.1 + test_ds186 (1 passed). Коммит: 53ec851.')
    $r76.Add('- ИНЦИДЕНТ 68: NTFS-порча F: -> .git/objects битый -> .git восстановлен из origin (7b3fea6); .gitignore из 53ec851.')
    $r76.Add('- 76_02: 76.Старт.txt + памятка + 68_07 + fix .gitignore. Коммит: f414282.')
    $r76.Add('- 77_00: старт чата 77 + памятка (чат 76). Коммит: 8e13bf6.')
    $r76.Add('')
    $r76.Add('## Регресс')
    $r76.Add('- На MBE (68_06k): 402 passed / 0 skipped. test_ds186 — 1 passed.')
    $r76.Add('- Было на LG (74): 401 passed / 1 skipped (02_k1_ika_has_plp skip, ИКА пуст).')
    $r76.Add('- После 76_01d (ИКА 3 .plp) -> 02 должен пройти; на MBE 68_06k — 402/0.')
    $r76.Add('')
    $r76.Add('## Коммиты 76 (в порядке)')
    $r76.Add('- 8a148b3 76_01d: ИКА — 3 .plp-фикстуры + самокоммит B.')
    $r76.Add('- 7b3fea6 76_01f: fix test 02 (from analyzer import scanner) + .gitignore PATCH_IN/*.')
    $r76.Add('- 53ec851 68_06: recovery - DS_186 fix + rubricator restore.')
    $r76.Add('- f414282 76_02: 76.Старт + памятка + 68_07 + fix .gitignore (restore from 53ec851).')
    $r76.Add('- 8e13bf6 77_00: старт чата 77 + памятка (чат 76).')
    $r76.Add('')
    $r76.Add('## Долги 76 -> 77')
    $r76.Add('1. chkdsk F: /scan -> /f (LG, admin, offline). Бэкап: клон F:\TO_DBI_clone_20261028.')
    $r76.Add('2. pytest.ini (SRC/tests) — решить: коммит или .gitignore.')
    $r76.Add('3. 76.Старт.txt (53ec851) и 77.Старт.txt (f414282) — актуализировать на 8e13bf6.')
    $r76.Add('4. chat76_01f_gen/all.ps1 — исчезли из F: (порча); 76_01f уже в origin (7b3fea6) — не восстанавливать.')
    $r76.Add('5. ERROR: в 76_02b (warning temp_broken) — ложный; после chkdsk /f исчезнет.')
    [System.IO.File]::WriteAllLines($p76, $r76, $encNoBom)
    Write-Host 'report 76 written:' $p76 $r76.Count 'lines'
    $msgFile = Join-Path $PSDir ($hostTag + '_77_01_msg.txt')
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('77_01: отчёты 68 + 76')
    $msgLines.Add('')
    $msgLines.Add('- 68.Отчёт.txt: DS_186 fix, инцидент NTFS-порчи F:, восстановление .git, коммиты, долги.')
    $msgLines.Add('- 76.Отчёт.txt: 76_01d, 76_01f, 68_06, инцидент, 76_02, 77_00, регресс 402/0, долги.')
    $msgLines.Add('- chat77_01_reports.ps1: generator (self-commit B).')
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encNoBom)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $ErrorActionPreference = 'Continue'
    & git -C $root add -- $relRep68 $relRep76 $relSelf 2>&1 | Out-String | Write-Host
    $addRc = $LASTEXITCODE
    Write-Host 'git add rc=' $addRc
    if ($addRc -ne 0) { throw 'git add rc=' + $addRc }
    & git -C $root commit -F $msgFile 2>&1 | Out-String | Write-Host
    $commitRc = $LASTEXITCODE
    Write-Host 'git commit rc=' $commitRc
    if ($commitRc -ne 0) { throw 'git commit rc=' + $commitRc }
    & git -C $root push origin feature/dockerization 2>&1 | Out-String | Write-Host
    $pushRc = $LASTEXITCODE
    Write-Host 'git push rc=' $pushRc
    if ($pushRc -ne 0) { throw 'git push rc=' + $pushRc }
    $sb = & git -C $root status -sb 2>&1
    $sb | Select-Object -First 1 | Out-String | Write-Host
    if ($sb -match '\[ahead \d+\]') { throw 'После push осталось [ahead N]' }
    & git -C $root log -1 --oneline 2>&1 | Out-String | Write-Host
    Write-Host 'Готово: 77_01 закоммичен, запушен'
} catch { Write-Host 'ERROR:' $_ -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
