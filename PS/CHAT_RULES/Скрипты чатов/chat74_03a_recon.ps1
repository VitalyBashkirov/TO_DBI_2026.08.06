Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'

$PSDir = 'F:\TO_DBI\PS'
$root  = 'F:\TO_DBI'
$base  = 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п'
$rules = Join-Path $base '01_Правила_PS.md'
$templ = Join-Path $base '07_Шаблон_PS.md'
$relRules = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/01_Правила_PS.md'
$relTempl = 'PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/07_Шаблон_PS.md'

$hostName = $env:COMPUTERNAME
if ($hostName -like 'LGGram*') { $hostTag = 'LG' }
elseif ($hostName -like 'MateBook*') { $hostTag = 'MBE' }
else { throw "Неизвестный хост: $hostName" }

$log = Join-Path $PSDir "${hostTag}_74_03a_recon.log"
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName root=$root"
Write-Host "rules=$rules"
Write-Host "templ=$templ"
Write-Host "relRules=$relRules"
Write-Host "relTempl=$relTempl"

$oldEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    Write-Host "=== 1. Test-Path / Get-Item ==="
    foreach ($p in @($rules, $templ)) {
        $exists = Test-Path -LiteralPath $p
        Write-Host "Test-Path -LiteralPath: $p -> $exists"
        if ($exists) {
            $it = Get-Item -LiteralPath $p
            Write-Host ("  Length=" + $it.Length + " LastWriteTime=" + $it.LastWriteTime.ToString("s"))
        }
    }

    Write-Host "=== 2. Маркеры ==="
    if (Test-Path -LiteralPath $rules) {
        $txt = [System.IO.File]::ReadAllText($rules, [System.Text.Encoding]::UTF8)
        Write-Host ("rules.Contains(## 64_11.) = " + $txt.Contains("## 64_11."))
    }
    if (Test-Path -LiteralPath $templ) {
        $txt2 = [System.IO.File]::ReadAllText($templ, [System.Text.Encoding]::UTF8)
        Write-Host ("templ.Contains(LOG:) = " + $txt2.Contains("LOG:"))
    }

    Write-Host "=== 3. git ls-files ==="
    & git -C $root ls-files -- $relRules $relTempl 2>&1 | Out-String | Write-Host

    Write-Host "=== 4. git status --porcelain -- наши пути ==="
    & git -C $root status --porcelain -- $relRules $relTempl 2>&1 | Out-String | Write-Host

    Write-Host "=== 5. git check-ignore -v ==="
    & git -C $root check-ignore -v -- $relRules $relTempl 2>&1 | Out-String | Write-Host

    Write-Host "=== 6. git diff --name-only (unstaged) ==="
    & git -C $root diff --name-only 2>&1 | Out-String | Write-Host

    Write-Host "=== 7. git diff --cached --name-only (staged) ==="
    & git -C $root diff --cached --name-only 2>&1 | Out-String | Write-Host

    Write-Host "=== 8. git status -sb (целиком) ==="
    & git -C $root status -sb 2>&1 | Out-String | Write-Host

    Write-Host "=== 9. Фактические файлы (Recurse) ==="
    Get-ChildItem 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов' -Recurse -Filter '01_Правила_PS.md' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_.FullName }
    Get-ChildItem 'F:\TO_DBI\PS\CHAT_RULES\Старт новых чатов' -Recurse -Filter '07_Шаблон_PS.md' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_.FullName }

    Write-Host "=== 10. git rev-parse ==="
    & git -C $root rev-parse --show-toplevel 2>&1 | Out-String | Write-Host
    & git -C $root rev-parse HEAD 2>&1 | Out-String | Write-Host
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
} finally {
    $ErrorActionPreference = $oldEAP
    Stop-Transcript
    Get-ChildItem $PSDir -File | Where-Object { $_.Length -eq 0 -and $_.Name -ne (Split-Path $log -Leaf) -and $_.LastWriteTime -lt (Get-Date).AddMinutes(-1) } | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "LOG: $log" -ForegroundColor Green
}
