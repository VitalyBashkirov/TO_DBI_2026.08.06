Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root = 'F:\TO_DBI'
$relSelf = 'PS/CHAT_RULES/Скрипты чатов/chat77_00_start.ps1'
$relStart = 'PS/CHAT_RULES/Старт новых чатов/77.Старт.txt'
$relPam = 'PS/CHAT_RULES/Отчеты/Памятка_чатов.txt'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_77_00_start.log')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    $encNoBom = New-Object System.Text.UTF8Encoding($false)
    $startPath = Join-Path $root $relStart
    $startLines = New-Object System.Collections.Generic.List[string]
    $startLines.Add('77.СТАРТ (сгенерировано 2026-10-28 из чата 76; инцидент 68 — восстановление .git)')
    $startLines.Add('Хост: LGGRAMA8V7Q8U (LG) / MATEBOOKE (MBE)')
    $startLines.Add('')
    $startLines.Add('## Где искать правила (ОБЯЗАТЕЛЬНО в новом чате)')
    $startLines.Add('F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п\')
    $startLines.Add('  00_INDEX.md -> 01..08; 01_Правила_PS.md: 64_11..64_16, 68_07.')
    $startLines.Add('')
    $startLines.Add('## Статус на 2026-10-28 (после чата 76)')
    $startLines.Add('- HEAD = f414282; origin == HEAD, ahead нет.')
    $startLines.Add('- Регресс на MBE (68_06k): 402 passed / 0 skipped. test_ds186 — 1 passed.')
    $startLines.Add('- Действуют: 64_11..64_16, ДВОБ, 65_1..65_3, 66_1/66_2, 67_1, 68_1, 68_07.')
    $startLines.Add('- .git восстановлен из origin (7b3fea6) после NTFS-порчи F:; .gitignore восстановлен из 53ec851.')
    $startLines.Add('- 76_02: f414282 (76.Старт + памятка + 68_07 + fix .gitignore).')
    $startLines.Add('- 68_06: 53ec851 (scanner.py + 4.RUBRICATOR_PROMPT v5.json 5.3.1 + test_ds186).')
    $startLines.Add('- 76_01f: 7b3fea6 (fix test 02 from analyzer import scanner).')
    $startLines.Add('- 76_01d: 8a148b3 (ИКА: 3 .plp-фикстуры).')
    $startLines.Add('')
    $startLines.Add('## ИНЦИДЕНТ 68 (NTFS-порча F:)')
    $startLines.Add('- .git/objects битый -> .git восстановлен из origin/feature/dockerization (7b3fea6).')
    $startLines.Add('- .gitignore был заменен транскриптом LG_74_05c_gitignore.log -> восстановлен из 53ec851.')
    $startLines.Add('- temp_broken_20261028\__init__.py, tools/, 69.Отчёт.txt — битые (git status: could not open directory).')
    $startLines.Add('- chkdsk F: /scan -> Access denied (нужен admin); /f offline — на LG после перезагрузки.')
    $startLines.Add('')
    $startLines.Add('## Долги 76 -> 77')
    $startLines.Add('1. chkdsk F: /scan (admin) -> chkdsk /f (offline) — на LG; бэкап: клон F:\TO_DBI_clone_20261028.')
    $startLines.Add('   Ожидаемо: temp_broken_20261028, tools/, .git/objects починятся/исчезнут; сотни D/M в git status уйдут.')
    $startLines.Add('2. 77.Старт.txt — HEAD = f414282 (актуальный); 76.Старт.txt устарел (53ec851) — можно удалить или оставить для истории.')
    $startLines.Add('3. pytest.ini в SRC/tests (локальный обход temp) — решить: коммит или .gitignore.')
    $startLines.Add('4. chat76_01f_gen/all.ps1 — исчезли из F: (порча); 76_01f уже в origin (7b3fea6) — не восстанавливать.')
    $startLines.Add('5. ERROR: в 76_02b (warning temp_broken) — ложный; после chkdsk /f исчезнет.')
    $startLines.Add('')
    $startLines.Add('## 68_07 (НОВОЕ, действует)')
    $startLines.Add('Перед сменой хоста MBE <-> LG ОБЯЗАТЕЛЬНО проверить F: (vol F: Ai NFTS E82B-3734, .git рабочий, ключевые файлы читаются).')
    $startLines.Add('Без проверки ЗАПРЕЩЕНО: git commit/push, chkdsk /f, Remove-Item/Move-Item крупных каталогов.')
    $startLines.Add('')
    $startLines.Add('## Первые шаги чата 77')
    $startLines.Add('1. Прочитать 00_INDEX.md -> 01..08; 01_Правила_PS.md: 64_11..64_16, 68_07.')
    $startLines.Add('2. Прочитать Отчеты\74.Отчёт.txt, 68.Отчёт.txt (создать), 76_00..76_02 в git.')
    $startLines.Add('3. chkdsk F: /scan (admin) -> /f (offline) — на LG (или другая задача).')
    $startLines.Add('4. Действовать по 04, 05, 06, 07, 64_11..64_16, 65_1..65_3, 66_1/66_2, 67_1, 68_1, 68_07.')
    [System.IO.File]::WriteAllLines($startPath, $startLines, $encNoBom)
    Write-Host 'start written:' $startPath $startLines.Count 'lines'
    $pamPath = Join-Path $root $relPam
    $pamAdd = New-Object System.Collections.Generic.List[string]
    $pamAdd.Add('')
    $pamAdd.Add('--- ЧАТ 76 (2026-10-28, MBE) ---')
    $pamAdd.Add('76_01d: ИКА 3 .plp + самокоммит B (8a148b3).')
    $pamAdd.Add('76_01f: fix test 02 (from analyzer import scanner) + .gitignore PATCH_IN (7b3fea6).')
    $pamAdd.Add('68_06a..k: DS_186 fix (scanner.py + 4.RUBRICATOR_PROMPT v5.json 5.3.1 + test_ds186). test_ds186: 1 passed.')
    $pamAdd.Add('Инцидент 68: NTFS-порча F: -> .git/objects битый -> .git восстановлен из origin (клон F:\TO_DBI_clone_20261028).')
    $pamAdd.Add('68_06: recovery = 53ec851 (3 файла) + 76_02: f414282 (старт 76 + памятка + 68_07 + .gitignore fix).')
    $pamAdd.Add('Долги 77: chkdsk F:, pytest.ini, temp_broken_20261028, tools/, .gitignore (восстановлен).')
    $pamAdd.Add('')
    [System.IO.File]::AppendAllLines($pamPath, $pamAdd, $encNoBom)
    Write-Host 'pam updated:' $pamPath
    $msgFile = Join-Path $PSDir ($hostTag + '_77_00_msg.txt')
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('77_00: старт чата 77 + памятка (чат 76)')
    $msgLines.Add('')
    $msgLines.Add('- 77.Старт.txt: HEAD=f414282, инцидент 68, долги 76->77, 68_07, первые шаги 77.')
    $msgLines.Add('- Памятка_чатов.txt: раздел 76 (76_01d/01f, 68_06, инцидент .git, 76_02).')
    $msgLines.Add('- chat77_00_start.ps1: generator (self-commit B).')
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encNoBom)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $ErrorActionPreference = 'Continue'
    & git -C $root add -- $relStart $relPam $relSelf 2>&1 | Out-String | Write-Host
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
    $sb | Select-Object -First 3 | Out-String | Write-Host
    if ($sb -match '\[ahead \d+\]') { throw 'После push осталось [ahead N]' }
    & git -C $root log -1 --oneline 2>&1 | Out-String | Write-Host
    Write-Host 'Готово: 77_00 закоммичен, запушен'
} catch { Write-Host 'ERROR:' $_ -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
