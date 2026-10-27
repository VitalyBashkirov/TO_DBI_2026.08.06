Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'

$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$gitignore = Join-Path $root '.gitignore'
$relRules = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/01_Правила_PS.md'
$relTempl = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/07_Шаблон_PS.md'

$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' }
elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' }
else { throw "Неизвестный хост: $hostName" }

$log = Join-Path $PSDir "${hostTag}_74_03c_recon.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName root=$root"

$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    Write-Host "=== 1. .gitignore существует? ==="
    if (Test-Path -LiteralPath $gitignore) {
        $it = Get-Item -LiteralPath $gitignore
        Write-Host ("  Length=" + $it.Length + " LastWriteTime=" + $it.LastWriteTime.ToString("s"))
    } else {
        Write-Host "  .gitignore НЕТ"
    }

    Write-Host "=== 2. .gitignore строки 95-120 (с номерами) ==="
    if (Test-Path -LiteralPath $gitignore) {
        $lines = [System.IO.File]::ReadAllLines($gitignore, [System.Text.Encoding]::UTF8)
        $from = 95; $to = [Math]::Min(120, $lines.Length)
        for ($i = $from; $i -le $to; $i++) {
            if ($i -ge 1 -and $i -le $lines.Length) {
                Write-Host ("  {0,4}: {1}" -f $i, $lines[$i-1])
            }
        }
    }

    Write-Host "=== 3. Все строки .gitignore, содержащие PS ==="
    if (Test-Path -LiteralPath $gitignore) {
        $idx = 0
        foreach ($ln in [System.IO.File]::ReadAllLines($gitignore, [System.Text.Encoding]::UTF8)) {
            $idx++
            if ($ln -match 'PS') { Write-Host ("  {0,4}: {1}" -f $idx, $ln) }
        }
    }

    Write-Host "=== 4. git check-ignore -v по нашим .md ==="
    & git -C $root check-ignore -v -- $relRules $relTempl 2>&1 | Out-String | Write-Host

    Write-Host "=== 5. git log -- PS/CHAT_RULES (вся история, все ветки) ==="
    & git -C $root log --oneline --all -- 'PS/CHAT_RULES' 2>&1 | Out-String | Write-Host

    Write-Host "=== 6. git log -- 01_Правила_PS.md (вся история) ==="
    & git -C $root log --oneline --all -- $relRules 2>&1 | Out-String | Write-Host

    Write-Host "=== 7. git log -5 -- .gitignore ==="
    & git -C $root log --oneline -5 -- .gitignore 2>&1 | Out-String | Write-Host

    Write-Host "=== 8. git log -5 --oneline (общая вершина) ==="
    & git -C $root log --oneline -5 2>&1 | Out-String | Write-Host

    Write-Host "=== 9. Поиск коммита 73_03b / 64_11 в сообщениях ==="
    & git -C $root log --all --oneline --grep='73_03b' 2>&1 | Out-String | Write-Host
    & git -C $root log --all --oneline --grep='64_11' 2>&1 | Out-String | Write-Host
    & git -C $root log --all --oneline --grep='Правила' 2>&1 | Out-String | Write-Host

    Write-Host "=== 10. rev-parse HEAD / ветка ==="
    & git -C $root rev-parse HEAD 2>&1 | Out-String | Write-Host
    & git -C $root rev-parse --abbrev-ref HEAD 2>&1 | Out-String | Write-Host
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
} finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "LOG: $log" -ForegroundColor Green
}
