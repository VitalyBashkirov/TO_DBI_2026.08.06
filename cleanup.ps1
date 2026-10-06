# ============================================================
#  cleanup.ps1 v3 — очистка памяти и автозагрузки
#  Запускать ОТ ИМЕНИ АДМИНИСТРАТОРА
#
#  Параметры:
#    -DryRun          — только показать, ничего не снимать
#    -SkipServices    — не трогать службы
#    -SkipStartup     — не чистить Startup и реестр Run
#    -SkipWebView     — не снимать msedgewebview2 (если открыт Office/Teams)
#    -CleanUserRun    — удалить Teams / Yandex.Telemost / LM Studio из HKCU\Run
#    -CleanEdge       — удалить MicrosoftEdgeAutoLaunch_* из HKCU\Run
#    -AddProc <names> — добавить свои процессы в список
#    -LogPath <path>  — путь к логу (по умолчанию рядом со скриптом)
#    -ReportCsv <path>— путь к CSV-отчёту
# ============================================================

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$SkipServices,
    [switch]$SkipStartup,
    [switch]$SkipWebView,
    [switch]$CleanUserRun,
    [switch]$CleanEdge,
    [string[]]$AddProc = @(),
    [string]$LogPath,
    [string]$ReportCsv
)

# ---------- Пути по умолчанию ----------
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $LogPath)    { $LogPath   = Join-Path $scriptDir 'cleanup.log' }
if (-not $ReportCsv)  { $ReportCsv = Join-Path $scriptDir 'cleanup_report.csv' }

# ---------- Проверка прав ----------
$isAdmin = ([Security.Principal.WindowsPrincipal]::new(
    [Security.Principal.WindowsIdentity]::GetCurrent()
)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[!] Запустите от имени администратора." -ForegroundColor Red
    exit 1
}

# ---------- Логирование ----------
function Write-Log {
    param([string]$Message, [string]$Level = 'INFO')
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$ts][$Level] $Message"
    Add-Content -Path $LogPath -Value $line -Encoding UTF8
    switch ($Level) {
        'OK'    { Write-Host "  [OK] $Message" -ForegroundColor Green }
        'WARN'  { Write-Host "  [--] $Message" -ForegroundColor Yellow }
        'ERR'   { Write-Host "  [!!] $Message" -ForegroundColor Red }
        'SKIP'  { Write-Host "  [SKIP] $Message" -ForegroundColor DarkGray }
        'HEAD'  { Write-Host "`n=== $Message ===" -ForegroundColor Cyan }
        default { Write-Host "  $Message" }
    }
}

# ---------- Защита: эти процессы не снимаем никогда ----------
$protected = @(
    'System','Idle','Registry','Memory Compression','Secure System',
    'csrss','wininit','winlogon','services','lsass','smss','dwm',
    'svchost','fontdrvhost','ctfmon','explorer','audiodg','WUDFHost',
    'MsMpEng','avp',
    'StartMenuExperienceHost','SearchHost','ShellHost','ShellExperienceHost',
    'TextInputHost','TabTip','RuntimeBroker','sihost','taskhostw',
    'powershell','pwsh','cmd','WindowsTerminal','conhost',
    'QtWebEngineProcess'   # общий хост — рушит UI чужих приложений
)

# ---------- Списки процессов ----------
$procsSafe = @(
    'msedge','msedgewebview2',
    'kpm','kpm_service',
    'Widgets',
    'OneDrive','OneDrive.Sync.Service',
    'GoogleDriveFS',
    'M365Copilot',
    'CrossDeviceService',
    'MBAMessageCenter',
    'OfficeClickToRun',
    'AnyDesk',
    'TeamViewer','tv_w32','tv_x64',
    'YandexTelemost',
    'FortiClient','FortiClientConsole','FortiESNAC','FortiTray','FortiSSLVPNdaemon'
)

if ($SkipWebView) {
    $procsSafe = $procsSafe | Where-Object { $_ -ne 'msedgewebview2' }
}

if ($AddProc.Count -gt 0) {
    $procsSafe += $AddProc
}

# ---------- Службы -> Manual ----------
$svcsToManual = @(
    'AnyDesk','TeamViewer',
    'FortiClient','FortiESNAC','FortiTray','FortiSSLVPNdaemon',
    'HwMdcService','HuaweiPCManager'
)

# ---------- Службы -> Disabled ----------
$svcsToDisabled = @(
    'FA_Scheduler'
)

# ---------- Ярлыки в Startup, которые удаляем ----------
$startupLinks = @(
    'Ollama.lnk',
    'AnyDesk.lnk',
    'TeamViewer.lnk'
    # ShareX.lnk НЕ трогаем — вы решили оставить
)

# ---------- Run keys: точные имена для удаления ----------
# Всегда удаляем (если есть):
$runKeyNamesAlways = @(
    'Ollama','AnyDesk','TeamViewer'
)

# Дополнительно при -CleanUserRun:
$runKeyNamesUser = @(
    'Teams',
    'Yandex.Telemost',
    'electron.app.LM Studio'
    # OneDrive / GoogleDriveFS / kpm — уже удалены ранее
    # YandexDisk2 / Opera Browser Assistant / Docker Desktop / Lightshot —
    #   НЕ трогаем, оставлены по решению пользователя
)

# Дополнительно при -CleanEdge:
$runKeyPrefixesUser = @(
    'MicrosoftEdgeAutoLaunch_'
)

# ---------- Белый список: НИКОГДА не удалять из Run ----------
# Если имя ключа совпадает с префиксом из этого списка — пропускаем,
# даже если оно попало в runKeyNamesUser.
$runKeyWhitelistPrefixes = @(
    'YandexBrowserAutoLaunch_',
    'YandexDisk',
    'Opera',
    'Docker',
    'Lightshot',
    'HuaweiKeyboardAPP',
    'SecurityHealth',
    'Speech Recognition'
)

# ---------- Старт ----------
"" | Out-File $LogPath -Encoding UTF8 -Force
Write-Log ("cleanup.ps1 v3 started (DryRun={0}, SkipServices={1}, SkipStartup={2}, SkipWebView={3}, CleanUserRun={4}, CleanEdge={5})" -f `
    $DryRun, $SkipServices, $SkipStartup, $SkipWebView, $CleanUserRun, $CleanEdge) 'HEAD'

$before = (Get-Process | Measure-Object WorkingSet64 -Sum).Sum
Write-Log ("Memory before: {0} MB" -f [math]::Round($before/1MB,1))

# ============================================================
#  1. Процессы
# ============================================================
Write-Log "1. Killing processes" 'HEAD'

$killedCount = 0
$killedMb    = 0

foreach ($p in $procsSafe) {
    $found = Get-Process -Name $p -ErrorAction SilentlyContinue
    if (-not $found) { continue }

    foreach ($proc in $found) {
        if ($protected -contains $proc.Name) {
            Write-Log ("protected: {0} (PID {1})" -f $proc.Name, $proc.Id) 'SKIP'
            continue
        }

        $ramMb = [math]::Round($proc.WorkingSet64/1MB, 1)

        if ($DryRun) {
            Write-Log ("[DRY] would kill {0} (PID {1}), {2} MB" -f $proc.Name, $proc.Id, $ramMb)
            continue
        }

        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction Stop
            Write-Log ("killed {0} (PID {1}), {2} MB" -f $proc.Name, $proc.Id, $ramMb) 'OK'
            $killedCount++
            $killedMb += $ramMb
        } catch {
            Write-Log ("failed {0} (PID {1}): {2}" -f $proc.Name, $proc.Id, $_.Exception.Message) 'WARN'
        }
    }
}

if (-not $DryRun) {
    Write-Log ("Processes killed: {0}, total {1} MB" -f $killedCount, [math]::Round($killedMb,1))
}

# ============================================================
#  2. Службы -> Manual
# ============================================================
if (-not $SkipServices) {
    Write-Log "2. Setting services to Manual / Disabled" 'HEAD'

    foreach ($s in $svcsToManual) {
        $svc = Get-Service -Name $s -ErrorAction SilentlyContinue
        if (-not $svc) { continue }

        if ($DryRun) {
            Write-Log ("[DRY] would stop and set {0} -> Manual" -f $s)
            continue
        }

        $stopped = $false
        try {
            if ($svc.Status -ne 'Stopped') {
                Stop-Service -Name $s -Force -ErrorAction Stop
                Write-Log ("stopped ${s} (Stop-Service)") 'OK'
                $stopped = $true
            } else {
                $stopped = $true
            }
        } catch { }

        if (-not $stopped) {
            sc.exe stop $s | Out-Null
            Start-Sleep -Milliseconds 800
            $svc.Refresh()
            if ($svc.Status -eq 'Stopped') {
                Write-Log ("stopped ${s} (sc.exe)") 'OK'
            } else {
                Write-Log ("could not stop ${s}: still $($svc.Status)") 'WARN'
            }
        }

        try {
            Set-Service -Name $s -StartupType Manual -ErrorAction Stop
            Write-Log ("${s} -> Manual") 'OK'
        } catch {
            Write-Log ("could not set ${s} to Manual: $($_.Exception.Message)") 'WARN'
        }
    }

    foreach ($s in $svcsToDisabled) {
        $svc = Get-Service -Name $s -ErrorAction SilentlyContinue
        if (-not $svc) { continue }

        if ($DryRun) {
            Write-Log ("[DRY] would stop and set {0} -> Disabled" -f $s)
            continue
        }

        Stop-Service -Name $s -Force -ErrorAction SilentlyContinue
        try {
            Set-Service -Name $s -StartupType Disabled -ErrorAction Stop
            Write-Log ("${s} -> Disabled") 'OK'
        } catch {
            Write-Log ("could not set ${s} to Disabled: $($_.Exception.Message)") 'WARN'
        }
    }
} else {
    Write-Log "2. Services — skipped" 'HEAD'
}

# ============================================================
#  3. Ярлыки в Startup
# ============================================================
if (-not $SkipStartup) {
    Write-Log "3. Cleaning Startup folder" 'HEAD'

    $startupDirs = @(
        (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'),
        (Join-Path $env:ProgramData 'Microsoft\Windows\Start Menu\Programs\Startup')
    )

    foreach ($dir in $startupDirs) {
        if (-not (Test-Path $dir)) { continue }
        foreach ($lnk in $startupLinks) {
            $path = Join-Path $dir $lnk
            if (Test-Path $path) {
                if ($DryRun) {
                    Write-Log ("[DRY] would remove $path")
                } else {
                    try {
                        Remove-Item $path -Force -ErrorAction Stop
                        Write-Log ("removed $path") 'OK'
                    } catch {
                        Write-Log ("failed to remove ${path}: $($_.Exception.Message)") 'WARN'
                    }
                }
            }
        }
    }
} else {
    Write-Log "3. Startup — skipped" 'HEAD'
}

# ============================================================
#  4. Реестр Run
# ============================================================
if (-not $SkipStartup) {
    Write-Log "4. Cleaning Run keys" 'HEAD'

    $runKeys = @(
        'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run',
        'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run'
    )

    # Собираем итоговый список точных имён
    $namesToRemove = @($runKeyNamesAlways)
    if ($CleanUserRun) {
        $namesToRemove += $runKeyNamesUser
        Write-Log "  (-CleanUserRun: Teams / Yandex.Telemost / LM Studio)" 'INFO'
    }

    # Префиксы для удаления
    $prefixesToRemove = @()
    if ($CleanEdge) {
        $prefixesToRemove += $runKeyPrefixesUser
        Write-Log "  (-CleanEdge: MicrosoftEdgeAutoLaunch_*)" 'INFO'
    }

    foreach ($k in $runKeys) {
        if (-not (Test-Path $k)) { continue }
        $props = (Get-Item $k).Property
        foreach ($name in $props) {

            # Белый список — пропускаем
            $whitelisted = $false
            foreach ($wl in $runKeyWhitelistPrefixes) {
                if ($name -like "$wl*") { $whitelisted = $true; break }
            }
            if ($whitelisted) {
                Write-Log ("whitelisted: $k -> $name") 'SKIP'
                continue
            }

            $matchExact  = $namesToRemove -contains $name
            $matchPrefix = $false
            foreach ($pref in $prefixesToRemove) {
                if ($name -like "$pref*") { $matchPrefix = $true; break }
            }

            if ($matchExact -or $matchPrefix) {
                if ($DryRun) {
                    Write-Log ("[DRY] would remove $k -> $name")
                } else {
                    try {
                        Remove-ItemProperty -Path $k -Name $name -ErrorAction Stop
                        Write-Log ("removed $k -> $name") 'OK'
                    } catch {
                        Write-Log ("failed $k -> ${name}: $($_.Exception.Message)") 'WARN'
                    }
                }
            }
        }
    }
} else {
    Write-Log "4. Run keys — skipped" 'HEAD'
}

# ============================================================
#  5. Отчёт до/после
# ============================================================
Write-Log "5. Report" 'HEAD'

Start-Sleep -Seconds 3
$after = (Get-Process | Measure-Object WorkingSet64 -Sum).Sum
$freedMb = [math]::Round(($before - $after)/1MB, 1)

$os = Get-CimInstance Win32_OperatingSystem
$freeMb  = [math]::Round($os.FreePhysicalMemory/1KB, 0)
$totalMb = [math]::Round($os.TotalVisibleMemorySize/1KB, 0)
$freePct = [math]::Round(100*$freeMb/$totalMb, 1)

Write-Log ("Memory after: {0} MB" -f [math]::Round($after/1MB,1))
Write-Log ("Freed: {0} MB" -f $freedMb) 'OK'
Write-Log ("Free: {0} MB / {1} MB ({2} pct)" -f $freeMb, $totalMb, $freePct)

# CSV с топ-60 после
Get-Process | Sort-Object WorkingSet64 -Descending |
    Select-Object -First 60 Name, Id,
        @{N='RAM_MB';E={[math]::Round($_.WorkingSet64/1MB,1)}},
        @{N='Private_MB';E={[math]::Round($_.PrivateMemorySize64/1MB,1)}},
        @{N='CPU_s';E={[math]::Round($_.CPU,1)}},
        Path |
    Export-Csv $ReportCsv -NoTypeInformation -Encoding UTF8

Write-Log ("Report saved: $ReportCsv") 'OK'
Write-Log "Done." 'HEAD'