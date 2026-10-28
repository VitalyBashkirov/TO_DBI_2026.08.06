Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$PSDir = 'F:\TO_DBI\PS'
$root = 'F:\TO_DBI'
$relSelf = 'PS/CHAT_RULES/Скрипты чатов/chat76_02_all.ps1'
$relStart = 'PS/CHAT_RULES/Старт новых чатов/76.Старт.txt'
$relPam = 'PS/CHAT_RULES/Отчеты/Памятка_чатов.txt'
$relEnv = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/08_Окружение.md'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' } elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' } else { throw 'Неизвестный хост: ' + $hostName }
$log = Join-Path $PSDir ($hostTag + '_76_02_start.log')
Start-Transcript -Path $log -Force
Write-Host 'hostTag=' $hostTag
$oldEAP = $ErrorActionPreference
try {
    $encNoBom = New-Object System.Text.UTF8Encoding($false)
    $startPath = Join-Path $root $relStart
    $startLines = New-Object System.Collections.Generic.List[string]
    $startLines.Add('76.СТАРТ (сгенерировано 2026-10-28 из чата 76; инцидент 68 — восстановление .git)')
    $startLines.Add('Хост: LGGRAMA8V7Q8U (LG) / MATEBOOKE (MBE)')
    $startLines.Add('')
    $startLines.Add('HEAD = 53ec851 (68_06: recovery - DS_186 fix + rubricator restore). origin == HEAD, ahead нет.')
    $startLines.Add('Регресс на MBE (68_06k): 402 passed / 0 skipped. test_ds186 — 1 passed.')
    $startLines.Add('Действуют: 64_11..64_16, ДВОБ, 65_1..65_3, 66_1/66_2, 67_1, 68_1, 68_07.')
    $startLines.Add('ИНЦИДЕНТ 68: NTFS-порча F: (коррапт .git/objects, temp/__init__.py, 69.Отчёт.txt). .git восстановлен из origin.')
    $startLines.Add('68_06: scanner.py (pattern return/raise/pragma/message/app_error), 4.RUBRICATOR_PROMPT v5.json 5.3.1, test_ds186 (config paths/scan).')
    $startLines.Add('ДОЛГИ 68 -> 76:')
    $startLines.Add('  1. chkdsk F: /scan (admin) -> chkdsk /f (offline) после бэкапа (клон F:\TO_DBI_clone_20261028 есть).')
    $startLines.Add('  2. temp_broken_20261028\__init__.py — битый; НЕ трогать до chkdsk.')
    $startLines.Add('  3. Сотни D/M в git status из-за порчи F: — не коммитить (git add -A падает).')
    $startLines.Add('  4. pytest.ini в SRC/tests — локальный обход temp; решение (коммит/ignore) — в 76.')
    $startLines.Add('  5. chat76_01f_gen/all.ps1 — исчезли (порча); 76_01f уже в origin (7b3fea6).')
    $startLines.Add('')
    $startLines.Add('ПЕРВЫЕ ШАГИ ЧАТА 76:')
    $startLines.Add('  1. Прочитать 00_INDEX.md -> 01..08; 01_Правила_PS.md: 64_11..64_16, 68_07.')
    $startLines.Add('  2. Прочитать Отчеты\74.Отчёт.txt, 68.Отчёт.txt (создать), 76_00..76_02 в git.')
    $startLines.Add('  3. Взять долг 1 (chkdsk на LG) — или новую задачу.')
    $startLines.Add('  4. Действовать по 04, 05, 06, 07, 64_11..64_16, 65_1..65_3, 66_1/66_2, 67_1, 68_1, 68_07.')
    $startLines.Add('')
    $startLines.Add('68_07 (НОВОЕ): перед сменой хоста MBE <-> LG — проверить F: (vol F:, .git, ключевые файлы). Без проверки — никаких коммитов, чекдиск/ф.')
    [System.IO.File]::WriteAllLines($startPath, $startLines, $encNoBom)
    Write-Host 'start written:' $startPath $startLines.Count 'lines'
    $pamPath = Join-Path $root $relPam
    $pamAdd = New-Object System.Collections.Generic.List[string]
    $pamAdd.Add('')
    $pamAdd.Add('--- ЧАТ 68 (2026-10-27..28, MBE) ---')
    $pamAdd.Add('68_06a..k: DS_186 fix (scanner.py + 4.RUBRICATOR_PROMPT v5.json 5.3.0->5.3.1 + test_ds186). test_ds186: 1 passed.')
    $pamAdd.Add('Инцидент 68: NTFS-порча F: -> .git/objects битый. .git восстановлен из origin (клон F:\TO_DBI_clone_20261028).')
    $pamAdd.Add('68_06: recovery = 53ec851 (3 файла), запушен в origin/feature/dockerization.')
    $pamAdd.Add('Новое правило 68_07: проверка F: перед сменой хоста MBE<->LG.')
    $pamAdd.Add('')
    [System.IO.File]::AppendAllLines($pamPath, $pamAdd, $encNoBom)
    Write-Host 'pam updated:' $pamPath
    $envPath = Join-Path $root $relEnv
    $envAdd = New-Object System.Collections.Generic.List[string]
    $envAdd.Add('')
    $envAdd.Add('## 68_07. Проверка F: перед сменой хоста MBE <-> LG (чат 68)')
    $envAdd.Add('')
    $envAdd.Add('При смене хоста MBE <-> LG (F: — переносной SSD) ОБЯЗАТЕЛЬНО проверить:')
    $envAdd.Add('  - vol F: (метка Ai NFTS, серийник E82B-3734)')
    $envAdd.Add('  - Test-Path F:\TO_DBI\.git и git -C F:\TO_DBI rev-parse --is-inside-work-tree')
    $envAdd.Add('  - git -C F:\TO_DBI log -1 --oneline (должен быть известный HEAD)')
    $envAdd.Add('  - чтение ключевых файлов (scanner.py, 4.RUBRICATOR_PROMPT v5.json) через ReadAllBytes')
    $envAdd.Add('Без проверки ЗАПРЕЩЕНО: git commit/push, chkdsk /f, Remove-Item/Move-Item крупных каталогов.')
    $envAdd.Add('')
    [System.IO.File]::AppendAllLines($envPath, $envAdd, $encNoBom)
    Write-Host 'env updated:' $envPath
    $msgFile = Join-Path $PSDir ($hostTag + '_76_02_msg.txt')
    $msgLines = New-Object System.Collections.Generic.List[string]
    $msgLines.Add('68_06: 76_02 - старт 76 + памятка чатов + 68_07')
    $msgLines.Add('')
    $msgLines.Add('- 76.Старт.txt: HEAD=53ec851, инцидент 68, долги, первые шаги.')
    $msgLines.Add('- Памятка_чатов.txt: раздел 68 (DS_186 fix, инцидент .git, 68_07).')
    $msgLines.Add('- 08_Окружение.md: 68_07 (проверка F: перед сменой хоста).')
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join "`r`n"), $encNoBom)
    $mb = [System.IO.File]::ReadAllBytes($msgFile)
    if ($mb.Length -ge 3 -and $mb[0] -eq 0xEF -and $mb[1] -eq 0xBB -and $mb[2] -eq 0xBF) { throw 'msgfile с BOM' }
    Write-Host 'msgfile:' $msgFile $mb.Length 'B no-BOM OK'
    $ErrorActionPreference = 'Continue'
    & git -C $root add -- $relStart $relPam $relEnv $relSelf 2>&1 | Out-String | Write-Host
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
    Write-Host 'Готово: 76_02 закоммичен, запушен'
} catch { Write-Host 'ERROR:' $_ -ForegroundColor Red }
finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host 'LOG:' $log -ForegroundColor Green
}
