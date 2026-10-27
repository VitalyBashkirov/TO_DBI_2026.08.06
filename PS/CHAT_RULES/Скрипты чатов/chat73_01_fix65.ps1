Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' }
elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' }
else { throw "Неизвестный хост: $hostName" }
$PSDir    = 'F:\TO_DBI\PS'
$rulesDir = 'F:\TO_DBI\PS\CHAT_RULES'
$p       = Join-Path $rulesDir 'Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п\01_Правила_PS.md'
$log     = Join-Path $PSDir "${hostTag}_73_01_fix65.log"
$encNoBom = New-Object System.Text.UTF8Encoding($false)
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName rules=$p"
try {
    if (-not (Test-Path $p)) { throw "Нет файла правил: $p" }
    if ((Get-Item $p).Length -le 0) { throw "Файл правил пуст: $p" }
    $bak = "$p.ds73_01bak"
    Copy-Item -LiteralPath $p -Destination $bak -Force
    Write-Host "BAK: $bak ($((Get-Item $bak).Length) B)"
    $old = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
    Write-Host "OLD_LEN: $($old.Length)"
    $B = New-Object System.Collections.Generic.List[string]
    $B.Add('## 65_2. Генерация отчётов и стартов новых чатов — WriteAllLines массивом PS-строк (чат 65; уточнено в 73)')
    $B.Add('')
    $B.Add('Тексты отчётов и стартов пишутся не вручную и не python-мейкером, а PS-скриптом (одним блоком, 62_1/64_1).')
    $B.Add('')
    $B.Add('Предпочтительный способ записи — [System.IO.File]::WriteAllLines массивом PS-строк.')
    $B.Add('')
    $B.Add('- Массив: System.Collections.Generic.List[string], ровно одна строка файла на элемент (61_7).')
    $B.Add('- Кодировка: .md/.txt/.json/msgfile — UTF-8 no-BOM (11, 64_4); .ps1/.py с кириллицей — UTF-8 BOM (64_4).')
    $B.Add('- Запись — последней строкой после всех проверок (64_2). Бэкап исходника — ДО записи.')
    $B.Add('- После записи — проверка: размер, BOM-детект, ключевые маркеры.')
    $B.Add('')
    $B.Add('python-мейкеры, генерирующие PS-строки, — устарели (долг 6, чат 72): не использовать.')
    $B.Add('')
    $B.Add('Интерактивная вставка (7, 64_2, инциденты 72_02b, 73_00, 73_01):')
    $B.Add('- Консольный стартовый блок не должен содержать try/finally, if/else на верхнем уровне — PS 5.1 в построчной вставке рвёт их.')
    $B.Add('- Всё тело (try/catch/finally, Start-Transcript, правки) — внутри .ps1, запуск через powershell -NoProfile -ExecutionPolicy Bypass -File.')
    $B.Add('- В консоли — только: запись .ps1 через WriteAllLines массивом + BOM-проверка + & powershell -File F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов\chat73_01_fix65.ps1.')
    $B.Add('- Тогда Start-Transcript внутри .ps1 открывается гарантированно, лог создаётся.')
    $newBlock = ($B -join "`r`n")
    $pattern = '(?s)## 65_2\..*?(?=\r?\n## |\z)'
    $m = [regex]::Matches($old, $pattern)
    if ($m.Count -lt 1) { throw "Блок ## 65_2. не найден" }
    Write-Host "FOUND_65_2: $($m.Count) (заменяем последний)"
    $last = $m[$m.Count - 1]
    $new = $old.Substring(0, $last.Index) + $newBlock + $old.Substring($last.Index + $last.Length)
    [System.IO.File]::WriteAllText($p, $new, $encNoBom)
    Write-Host "WROTE: $p ($((Get-Item $p).Length) B)"
    $chk = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
    Write-Host "NEW_LEN: $($chk.Length)"
    if ($chk.Length -le $old.Length) { throw "Размер не вырос: old=$($old.Length) new=$($chk.Length)" }
    if ($chk -notmatch 'уточнено в 73') { throw 'Нет маркера уточнено в 73' }
    if ($chk -notmatch 'верхнем уровне') { throw 'Нет маркера верхнем уровне' }
    $b = [System.IO.File]::ReadAllBytes($p)
    $isBom = ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
    Write-Host "RULES_BOM: $isBom (ожидается False)"
    if ($isBom) { throw "01_Правила_PS.md с BOM — 64_4" }
    Write-Host "OK: 73_01 завершён"
}
catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    throw
}
finally {
    Stop-Transcript -ErrorAction SilentlyContinue
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "LOG: $log" -ForegroundColor Green
}
