<#
.SYNOPSIS
    Универсальный скрипт закрытия DS-задания (v2).
    Выполняет: создание файлов задания/отчёта (если переданы),
    bot.log -> git add -> git commit -> git push -> проверка.

.DESCRIPTION
    Соответствует DS_STANDARD.md §6.3 (9 шагов завершения DS) и §6.5.
    Запись в bot.log пишется ДО коммита (урок чата 18, п.29).
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$DsNumber,

    [string]$DsFileName = '',

    [string]$TaskBody = '',

    [string]$ReportBody = '',

    [Parameter(Mandatory=$true)]
    [string]$BotLogMessage,

    [Parameter(Mandatory=$true)]
    [string]$CommitMessage,

    [string[]]$Files = @(),

    [switch]$Push,

    [string]$Branch = '',

    [string]$InboxFile = ''
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
Set-Location -LiteralPath 'F:\TO_DBI'
Write-Host "Текущий каталог: $(Get-Location)"
Write-Host ""

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

Write-Host "=== [1/8] Проверки перед стартом ===" -ForegroundColor Cyan

Write-Host ""
Write-Host "[1.1] git status -sb (до):"
git status -sb

$currentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
Write-Host ""
Write-Host "[1.2] Текущая ветка: $currentBranch"
if ([string]::IsNullOrWhiteSpace($Branch)) {
    $Branch = $currentBranch
}
Write-Host "      Ветка для push: $Branch"

$botLog = 'F:\TO_DBI\EXCHANGE\bot.log'
if (-not (Test-Path -LiteralPath $botLog)) {
    Write-Host "[1.3] ОШИБКА: $botLog не найден" -ForegroundColor Red
    return
}
Write-Host "[1.3] bot.log: $botLog"

if ($Files.Count -gt 0) {
    Write-Host ""
    Write-Host "[1.4] Проверка файлов из -Files:"
    $missing = @()
    foreach ($f in $Files) {
        $full = Join-Path 'F:\TO_DBI' $f
        if (Test-Path -LiteralPath $full) {
            Write-Host "  [OK] $f"
        } else {
            Write-Host "  [!!] $f - НЕ НАЙДЕН" -ForegroundColor Yellow
            $missing += $f
        }
    }
    if ($missing.Count -gt 0) {
        Write-Host ""
        Write-Host "ПРОДОЛЖАТЬ нельзя: отсутствуют файлы: $($missing -join ', ')" -ForegroundColor Red
        return
    }
}

Write-Host ""
Write-Host "=== [2/8] Создание файлов задания/отчёта ===" -ForegroundColor Cyan

$taskPath = ''
$reportPath = ''

if (-not [string]::IsNullOrWhiteSpace($DsFileName) -and -not [string]::IsNullOrWhiteSpace($TaskBody)) {
    $taskPath = Join-Path 'F:\TO_DBI\EXCHANGE\PROCESSED' $DsFileName
    [System.IO.File]::WriteAllText($taskPath, $TaskBody, $utf8NoBom)
    Write-Host "[2.1] Задание: $taskPath"
} elseif (-not [string]::IsNullOrWhiteSpace($DsFileName)) {
    Write-Host "[2.1] TaskBody не передан — файл задания не создаётся" -ForegroundColor Yellow
}

if (-not [string]::IsNullOrWhiteSpace($DsFileName) -and -not [string]::IsNullOrWhiteSpace($ReportBody)) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($DsFileName)
    $reportName = "${baseName}_report.md"
    $reportPath = Join-Path 'F:\TO_DBI\EXCHANGE\OUTBOX' $reportName
    [System.IO.File]::WriteAllText($reportPath, $ReportBody, $utf8NoBom)
    Write-Host "[2.2] Отчёт: $reportPath"
} elseif (-not [string]::IsNullOrWhiteSpace($DsFileName)) {
    Write-Host "[2.2] ReportBody не передан — файл отчёта не создаётся" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== [2.5/8] Очистка INBOX ===" -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($InboxFile)) {
    Write-Host "[2.5] InboxFile не задан (ок)"
} else {
    $inboxPath = Join-Path 'F:\TO_DBI' $InboxFile
    if (Test-Path -LiteralPath $inboxPath) {
        Remove-Item -LiteralPath $inboxPath -Force
        Write-Host "[2.5] INBOX удалён: $inboxPath"
    } else {
        Write-Host "[2.5] INBOX не найден (ок): $inboxPath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== [3/8] Запись в bot.log ===" -ForegroundColor Cyan

$stamp = Get-Date -Format 'dd.MM.yyyy HH:mm:ss'
$logLine = "[$stamp] $DsNumber`: $BotLogMessage"
Add-Content -LiteralPath $botLog -Value $logLine -Encoding UTF8
Write-Host "  $logLine"

Write-Host ""
Write-Host "=== [4/8] git add ===" -ForegroundColor Cyan

$addList = @()
foreach ($f in $Files) { $addList += $f }
if (-not [string]::IsNullOrWhiteSpace($taskPath)) { $addList += "EXCHANGE/PROCESSED/$DsFileName" }
if (-not [string]::IsNullOrWhiteSpace($reportPath)) { $addList += "EXCHANGE/OUTBOX/$([System.IO.Path]::GetFileName($reportPath))" }
if ($addList -notcontains 'EXCHANGE/bot.log') { $addList += 'EXCHANGE/bot.log' }

foreach ($f in $addList) {
    git add $f
    Write-Host "  git add $f"
}

Write-Host ""
Write-Host "[4.x] git status (staged):"
git status -sb

Write-Host ""
Write-Host "=== [5/8] git commit ===" -ForegroundColor Cyan

git commit -m $CommitMessage
$commitRc = $LASTEXITCODE

if ($commitRc -ne 0) {
    Write-Host ""
    Write-Host "[5.x] ОШИБКА коммита (rc=$commitRc)" -ForegroundColor Red
    return
}
Write-Host "  [OK] commit"

Write-Host ""
Write-Host "=== [6/8] git push ===" -ForegroundColor Cyan

if ($Push) {
    Write-Host "  git push origin $Branch"
    git push origin $Branch
    $pushRc = $LASTEXITCODE
    if ($pushRc -ne 0) {
        Write-Host "  [!!] push вернул rc=$pushRc" -ForegroundColor Yellow
    } else {
        Write-Host "  [OK] push"
    }
} else {
    Write-Host "  push НЕ выполняется (-Push не указан)"
}

Write-Host ""
Write-Host "=== [7/8] Проверка ===" -ForegroundColor Cyan

Write-Host ""
Write-Host "[7.1] git status -sb:"
git status -sb

Write-Host ""
Write-Host "[7.2] git log --oneline -3:"
git log --oneline -3

if ($Push) {
    Write-Host ""
    Write-Host "[7.3] git branch -vv:"
    git branch -vv
}

Write-Host ""
Write-Host "[7.4] bot.log (tail 3):"
Get-Content -LiteralPath $botLog -Tail 3 -Encoding UTF8 |
    ForEach-Object { Write-Host "  | $_" }

Write-Host ""
Write-Host "[7.5] BOM-check созданных файлов:"
foreach ($p in @($taskPath, $reportPath)) {
    if (-not [string]::IsNullOrWhiteSpace($p) -and (Test-Path -LiteralPath $p)) {
        $bytes = [IO.File]::ReadAllBytes($p)
        $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
        $mark = if ($hasBom) { "[!!] BOM=True" } else { "[OK] BOM=False" }
        Write-Host "  $mark  $([System.IO.Path]::GetFileName($p))  ($($bytes.Length) B)"
    }
}

Write-Host ""
Write-Host "=== [8/8] Сводка ===" -ForegroundColor Green

$headHash = (git rev-parse --short HEAD).Trim()
$headMsg  = (git log -1 --pretty=%s).Trim()
$ahead    = (git status -sb | Select-String 'ahead \d+').Matches.Value

Write-Host "  DS:            $DsNumber"
Write-Host "  Commit:        $headHash"
Write-Host "  Message:       $headMsg"
Write-Host "  Branch:        $Branch"
Write-Host "  Push:          $(if ($Push) {'выполнен'} else {'НЕ выполнен'})"
if ($ahead) {
    Write-Host "  Статус:        $ahead" -ForegroundColor Yellow
} else {
    Write-Host "  Статус:        синхронизировано с origin" -ForegroundColor Green
}
Write-Host ""
Write-Host "DS $DsNumber закрыт." -ForegroundColor Green