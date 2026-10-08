<#
.SYNOPSIS
    Универсальный скрипт закрытия DS-задания.
    Выполняет: bot.log -> git add -> git commit -> git push -> проверка.

.DESCRIPTION
    Соответствует DS_STANDARD.md §6.3 (9 шагов завершения DS) и §6.5.
    Запись в bot.log пишется ДО коммита (урок чата 18, п.29).
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$DsNumber,

    [Parameter(Mandatory=$true)]
    [string]$BotLogMessage,

    [Parameter(Mandatory=$true)]
    [string]$CommitMessage,

    [Parameter(Mandatory=$true)]
    [string[]]$Files,

    [switch]$Push,

    [string]$Branch = ''
)

# ============================================================
# 0. Кодировка
# ============================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
Set-Location -LiteralPath 'F:\TO_DBI'
Write-Host "Текущий каталог: $(Get-Location)"
Write-Host ""

# ============================================================
# 1. Проверки перед стартом
# ============================================================
Write-Host "=== [1/7] Проверки перед стартом ===" -ForegroundColor Cyan

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

Write-Host ""
Write-Host "[1.5] BOM-check для .md файлов:"
foreach ($f in $Files) {
    if ($f -like '*.md') {
        $full = Join-Path 'F:\TO_DBI' $f
        $bytes = [IO.File]::ReadAllBytes($full)
        $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
        $mark = if ($hasBom) { "[!!] BOM=True" } else { "[OK] BOM=False" }
        Write-Host "  $mark  $f  ($($bytes.Length) B)"
    }
}

# ============================================================
# 2. Запись в bot.log
# ============================================================
Write-Host ""
Write-Host "=== [2/7] Запись в bot.log ===" -ForegroundColor Cyan

$stamp = Get-Date -Format 'dd.MM.yyyy HH:mm:ss'
$logLine = "[$stamp] $DsNumber`: $BotLogMessage"
Add-Content -LiteralPath $botLog -Value $logLine -Encoding UTF8
Write-Host "  $logLine"

# ============================================================
# 3. git add
# ============================================================
Write-Host ""
Write-Host "=== [3/7] git add ===" -ForegroundColor Cyan

$addList = @($Files)
if ($addList -notcontains 'EXCHANGE/bot.log') {
    $addList += 'EXCHANGE/bot.log'
    Write-Host "  (EXCHANGE/bot.log добавлен автоматически)"
}

foreach ($f in $addList) {
    git add $f
    Write-Host "  git add $f"
}

Write-Host ""
Write-Host "[3.x] git status (staged):"
git status -sb

# ============================================================
# 4. git commit
# ============================================================
Write-Host ""
Write-Host "=== [4/7] git commit ===" -ForegroundColor Cyan

git commit -m $CommitMessage
$commitRc = $LASTEXITCODE

if ($commitRc -ne 0) {
    Write-Host ""
    Write-Host "[4.x] ОШИБКА коммита (rc=$commitRc)" -ForegroundColor Red
    return
}

Write-Host "  [OK] commit"

# ============================================================
# 5. git push
# ============================================================
Write-Host ""
Write-Host "=== [5/7] git push ===" -ForegroundColor Cyan

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

# ============================================================
# 6. Проверка
# ============================================================
Write-Host ""
Write-Host "=== [6/7] Проверка ===" -ForegroundColor Cyan

Write-Host ""
Write-Host "[6.1] git status -sb:"
git status -sb

Write-Host ""
Write-Host "[6.2] git log --oneline -3:"
git log --oneline -3

if ($Push) {
    Write-Host ""
    Write-Host "[6.3] git branch -vv:"
    git branch -vv
}

Write-Host ""
Write-Host "[6.4] bot.log (tail 3):"
Get-Content -LiteralPath $botLog -Tail 3 -Encoding UTF8 |
    ForEach-Object { Write-Host "  | $_" }

Write-Host ""
Write-Host "[6.5] BOM-check .md (после):"
foreach ($f in $Files) {
    if ($f -like '*.md') {
        $full = Join-Path 'F:\TO_DBI' $f
        $bytes = [IO.File]::ReadAllBytes($full)
        $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
        $mark = if ($hasBom) { "[!!] BOM=True" } else { "[OK] BOM=False" }
        Write-Host "  $mark  $f"
    }
}

# ============================================================
# 7. Сводка
# ============================================================
Write-Host ""
Write-Host "=== [7/7] Сводка ===" -ForegroundColor Green

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