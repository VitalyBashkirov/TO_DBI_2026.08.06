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
$root     = 'F:\TO_DBI'
$rulesDir = 'F:\TO_DBI\PS\CHAT_RULES'
$reports  = Join-Path $rulesDir 'Отчеты'
$starts   = Join-Path $rulesDir 'Старт новых чатов'
$rulesPs  = Join-Path $rulesDir 'Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п\01_Правила_PS.md'
$pam      = Join-Path $reports 'Памятка_чатов.txt'
$rep73    = Join-Path $reports '73.Отчёт.txt'
$start74  = Join-Path $starts  '74.Старт.txt'
$log      = Join-Path $PSDir "${hostTag}_73_03_final.log"
$msgFile  = Join-Path $PSDir 'chat73_msg_final.txt'

$encNoBom = New-Object System.Text.UTF8Encoding($false)
Start-Transcript -Path $log -Force
Write-Host "hostTag=$hostTag host=$hostName root=$root"

try {
    if (-not (Test-Path $rulesPs)) { throw "Нет 01_Правила_PS.md" }
    if (-not (Test-Path $pam))     { throw "Нет Памятки" }
    if (-not (Test-Path $reports)) { throw "Нет каталога Отчеты" }
    if (-not (Test-Path $starts))  { throw "Нет каталога Старт новых чатов" }

    Write-Host "=== 1. 65_3 в 01_Правила_PS.md ==="
    $rp = [System.IO.File]::ReadAllText($rulesPs, [System.Text.Encoding]::UTF8)
    $bakRules = "$rulesPs.ds73_03bak"
    if (-not (Test-Path $bakRules)) { Copy-Item -LiteralPath $rulesPs -Destination $bakRules -Force }
    $has653 = $rp -match "## 65_3\\."
    Write-Host ("HAS_65_3: " + $has653)
    if (-not $has653) {
        $q = [char]96
        $nl = [Environment]::NewLine
        $B = New-Object System.Collections.Generic.List[string]
        $B.Add("")
        $B.Add("## 65_3. BOM при правке существующих .py: сохранять исходный формат файла (чат 73)")
        $B.Add("")
        $B.Add("Живой инцидент 73_02b_v4 -> 73_02c:")
        $B.Add("- scanner.py в репозитории лежал БЕЗ BOM. Патч перезаписал его через UTF8Encoding($true) (BOM) — и два старых теста (test_ds153d_scanner_selected_rules.py, test_ds154_scanner_oq1.py), читающие scanner.py через open(..., encoding=" + $q + "utf-8" + $q + ") (без -sig), упали на SyntaxError: invalid non-printable character U+FEFF. Полный регресс: 2 failed, 387 passed.")
    $R.Add("- Долг 1 ЗАКРЫТ: type_str для NAME in [TYPE] -> in. Коммит 49b46a4 (2 files, +5/-2), push OK, HEAD==origin, ahead нет.")
    $R.Add("- Долг 4 ЗАКРЫТ: 65_2 уточнён (WriteAllLines массивом PS-строк как предпочтительный способ; python-мейкеры устарели; интерактивная вставка — без верхнеуровневых try/finally/if-else).")
    $R.Add("- Полный регресс: 389 passed / 0 failed (после 73_02c).")
    $R.Add("- Новое правило 65_3 (живой инцидент 73_02b_v4 -> 73_02c): при правке существующих .py/.ps1 сохранять исходный формат BOM.")
    $R.Add("")
    $R.Add("## Что сделано")
    $R.Add("- 73_00: Памятка обновлена (чат 72 -> ЗАКРЫТ, чат 73 -> В РАБОТЕ). Лог отсутствует — инцидент вставки (finally вне try в консоли); результат корректен, не восстанавливаем.")
    $R.Add("- 73_01: 65_2 уточнён в 01_Правила_PS.md (21851 B, no-BOM). Живой инцидент 73_01: `$pattern` съеден в консоли (66_1) — учтено в 65_2.")
    $R.Add("- 73_02a / _fix / _v3: recon scanner.py (SRC/analyzer/scanner.py, 2903 строк): decl_re, _plp_iter_declarations (строки 932-965), ветка in [TYPE] -> group(2) = ""in [BRANCH]"", нормализация не срабатывала.")
    $R.Add("- 73_02b / _v2 / _v3: попытки патча — вставка в консоль рвалась (вложенные кавычки, base64-якорь не совпал). 73_02b_v3: откат сработал (68_1 подтверждён живым).")
    $R.Add("- 73_02b_v4: патч применён, AST OK, точечный 3 passed, но полный регресс 2 failed — BOM на scanner.py сломал test_ds153d/test_ds154 (читают через utf-8 без -sig). Откат из бэкапов.")
    $R.Add("- 73_02c: патч + тест записаны no-BOM (сохраняя формат). Точечный 3 passed, полный 389 passed. Коммит 49b46a4, push OK.")
    $R.Add("- 73_03: 65_3 вписан; 73.Отчёт.txt и 74.Старт.txt созданы; Памятка обновлена (строка 73 + раздел 74); коммит 01_Правила_PS.md.")
    $R.Add("")
    $R.Add("## Долги 73 -> 74")
    $R.Add("1. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1, free_memory.ps1, free_memory_profiles.txt) — не коммитить.")
    $R.Add("2. Бэкапы *.ds*bak — не коммитить; при желании — .gitignore.")
    $R.Add("3. Интерактивная вставка в консоль: подтверждён класс инцидентов (73_00 finally, 73_01 `$pattern`, 73_02b вложенные кавычки/base64). Правило 65_2/65_3 уже фиксирует; соблюдать буквально.")
    $R.Add("4. BOM при правке существующих .py/.ps1 — 65_3; проверить, нет ли ещё файлов с такой же ловушкой (тесты, читающие без -sig).")
    $R.Add("")
    $R.Add("## Артефакты")
    $R.Add("- Коммит: 49b46a4 (scanner.py + test_ds71_not_mentioned_real.py, +5/-2).")
    $R.Add("- Правило 65_2 (уточнено, 73_01) и 65_3 (новое, 73_03) в 01_Правила_PS.md.")
    $R.Add("- Бэкапы: scanner.py.ds73_02bak, test_ds71_not_mentioned_real.py.ds73_02bak, 01_Правила_PS.md.ds73_01bak, 01_Правила_PS.md.ds73_03bak, Памятка_чатов.txt.ds73_00bak. Не коммитить.")
    $R.Add("- Скрипты чатов: chat73_00_pamyatka.ps1 (не записан), chat73_01_fix65.ps1, chat73_02a_recon.ps1, chat73_02a_fix_recon.ps1, chat73_02a_v3_recon.ps1, chat73_02b_patch.ps1, chat73_02b_v2.ps1, chat73_02b_v3.ps1, chat73_02b_v4.ps1, chat73_02b_check.ps1, chat73_02c.ps1, chat73_03_final.ps1.")
    $R.Add("- msgfile: chat73_msg.txt (no-BOM), chat73_msg_final.txt (no-BOM).")
    $R.Add("- Логи: F:\TO_DBI\PS\LG_73_*.log.")
    $R.Add("")
    $R.Add("## Итог чата 73")
    $R.Add("Долги 1 и 4 закрыты. Новое правило 65_3. HEAD = 49b46a4, origin == HEAD, ahead нет.")
    [System.IO.File]::WriteAllText($rep73, ($R -join [Environment]::NewLine), $encNoBom)
    Write-Host ("WROTE 73.Отчёт.txt: " + (Get-Item $rep73).Length + " B")

    Write-Host "=== 3. 74.Старт.txt ==="
    $S = New-Object System.Collections.Generic.List[string]
    $S.Add("============================================")
    $S.Add("  74.СТАРТ (сгенерировано 2026-10-27 из чата 73)")
    $S.Add("  Хост: LGGRAMA8V7Q8U (hostTag=LG) / MATEBOOKE (hostTag=MBE)")
    $S.Add("============================================")
    $S.Add("")
    $S.Add("## Где искать правила (ОБЯЗАТЕЛЬНО в новом чате)")
    $S.Add("F:\TO_DBI\PS\CHAT_RULES")
    $S.Add("  00_INDEX.md")
    $S.Add("  Отчеты\ — +73")
    $S.Add("  Скрипты чатов\ — +chat73_*")
    $S.Add("  Старт новых чатов\ — +74")
    $S.Add("  Старт новых чатов\01_08 Правила,регламенты,сокращения и т.п")
    $S.Add("      00_INDEX.md, 01_Правила_PS.md (включая 65_2, 65_3, 68_1), 02_Сокращения_GUI.md, 03_Матрица_флагов.md,")
    $S.Add("      04_Регламент_логов.md, 05_Регламент_тестов.md, 06_Регламент_коммитов.md, 07_Шаблон_PS.md, 08_Окружение.md")
    $S.Add("")
    $S.Add("## Статус на 2026-10-27 (после чата 73)")
    $S.Add("- HEAD = 49b46a4. origin/feature/dockerization = 49b46a4, ahead нет.")
    $S.Add("- Долг 1 ЗАКРЫТ: type_str для NAME in [TYPE] -> in (scanner.py _plp_iter_declarations, re.match(r'^in\s*\[')).")
    $S.Add("- Долг 4 ЗАКРЫТ: 65_2 уточнён (WriteAllLines массивом PS-строк; python-мейкеры устарели; интерактивная вставка — без верхнеуровневых try/finally/if-else).")
    $S.Add("- Новое правило 65_3: при правке существующих .py/.ps1 сохранять исходный формат BOM (живой инцидент 73_02b_v4 -> 73_02c: BOM на scanner.py сломал 2 теста, читающих через utf-8 без -sig).")
    $S.Add("- Полный регресс: 389 passed / 0 failed.")
    $S.Add("")
    $S.Add("## Долги 73 -> 74")
    $S.Add("1. Грязные фоновые (EXCHANGE/bot.log, Ollama и LM Studio.bat, SRC/settings.json, test_all_models.ps1, free_memory.ps1, free_memory_profiles.txt) — не коммитить.")
    $S.Add("2. Бэкапы *.ds*bak — не коммитить; при желании — .gitignore.")
    $S.Add("3. Интерактивная вставка в консоль: класс инцидентов подтверждён (73_00 finally, 73_01 `$pattern`, 73_02b вложенные кавычки/base64). Соблюдать 65_2/65_3 буквально.")
    $S.Add("4. BOM при правке существующих .py/.ps1 — 65_3; проверить, нет ли других тестов, читающих без -sig.")
    $S.Add("")
    $S.Add("## Первые шаги чата 74")
    $S.Add("1. Прочитать CHAT_RULES\Старт новых чатов\01_08 ...\00_INDEX.md -> 01..08; отдельно 01_Правила_PS.md — 65_2, 65_3, 68_1.")
    $S.Add("2. Прочитать Отчеты\73.Отчёт.txt.")
    $S.Add("3. Взять долг 3/4 (дисциплина вставки / BOM-ловушки) — или новую задачу.")
    $S.Add("4. Действовать по регламентам: 04, 05, 06, 07, 61_1, 64_2, 64_3, 64_4, 65_1, 65_2, 65_3, 66_1, 66_2, 67_1, 68_1.")
    $S.Add("")
    $S.Add("## Правила PS (краткая выжимка)")
    $S.Add("1-13, 60_1..60_9, 61_1..61_7, 62_1, 63_1, 64_1..64_4, 64_10, 65_1, 65_2, 65_3, 66_1, 66_2, 67_1, 68_1.")
    $S.Add("")
    $S.Add("## Заметки по практике 73")
    $S.Add("- 65_2 уточнён: WriteAllLines массивом PS-строк — предпочтительный способ; в консоли без try/finally/if-else; тело — в .ps1 через -File.")
    $S.Add("- 65_3: сохранять исходный формат BOM при правке существующих .py/.ps1.")
    $S.Add("- 73_02b_v4 -> 73_02c: живой инцидент BOM; откат из бэкапов сработал (68_1).")
    $S.Add("- git commit — только -F <msgfile>, msgfile UTF-8 no-BOM.")
    $S.Add("- push после commit — в том же шаге; при отказе push: git reset --soft HEAD~1.")
    [System.IO.File]::WriteAllText($start74, ($S -join [Environment]::NewLine), $encNoBom)
    Write-Host ("WROTE 74.Старт.txt: " + (Get-Item $start74).Length + " B")

    Write-Host "=== 4. Памятка (строка 73 + раздел 74) ==="
    $pamOld = [System.IO.File]::ReadAllText($pam, [System.Text.Encoding]::UTF8)
    $bakPam = "$pam.ds73_03bak"
    if (-not (Test-Path $bakPam)) { Copy-Item -LiteralPath $pam -Destination $bakPam -Force }
    $has73line = $pamOld -match "=== Чат 73"
    if (-not $has73line) {
        $P = New-Object System.Collections.Generic.List[string]
        $P.Add("")
        $P.Add("=== Чат 73 (2026-10-27, LG) — ЗАКРЫТ ===")
        $P.Add("73_02c: долг 1 ЗАКРЫТ — type_str для NAME in [TYPE] -> in. Коммит 49b46a4, push OK, HEAD==origin, ahead нет. Полный регресс 389 passed.")
        $P.Add("73_01: долг 4 ЗАКРЫТ — 65_2 уточнён (WriteAllLines массивом, интерактивная вставка без try/finally/if-else).")
        $P.Add("73_03: новое правило 65_3 (BOM при правке существующих .py/.ps1 — сохранять формат; живой инцидент 73_02b_v4 -> 73_02c).")
        $P.Add("")
        $P.Add("=== Чат 74 (2026-10-27, LG) — ОЖИДАЕТ ===")
        $P.Add("План: 74_00 (Памятка/старт) -> 74_01 (долг 3/4: дисциплина вставки / BOM-ловушки) -> 74_02 (новая задача).")
        $add = ($P -join [Environment]::NewLine)
        $pamNew = $pamOld.TrimEnd() + [Environment]::NewLine + $add + [Environment]::NewLine
        [System.IO.File]::WriteAllText($pam, $pamNew, $encNoBom)
        Write-Host "WROTE Памятка: 73 + 74 OK"
    } else { Write-Host "SKIP Памятка (уже есть)" }

    Write-Host "=== 5. msgfile + git ==="
    $msgLines = @(
        "DS_73: финал — 65_3 (BOM при правке .py/.ps1), отчёт 73, старт 74"
        ""
        "- 01_Правила_PS.md: новое правило 65_3 (сохранять исходный формат BOM при правке существующих файлов; живой инцидент 73_02b_v4 -> 73_02c)."
        "- Отчеты/73.Отчёт.txt, Старт новых чатов/74.Старт.txt, Памятка_чатов.txt (73 + 74)."
    )
    [System.IO.File]::WriteAllText($msgFile, ($msgLines -join [Environment]::NewLine), $encNoBom)
    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try {
        & git -C $root add -- "PS/CHAT_RULES/Старт новых чатов/01_08 Правила,регламенты,сокращения и т.п/01_Правила_PS.md" 2>&1 | ForEach-Object { Write-Host $_ }
        & git -C $root status -sb 2>&1 | ForEach-Object { Write-Host $_ }
        & git -C $root commit -F $msgFile 2>&1 | ForEach-Object { Write-Host $_ }
        $commitRc = $LASTEXITCODE
        Write-Host "COMMIT_RC: $commitRc"
        if ($commitRc -ne 0) { throw "git commit rc=$commitRc" }
        & git -C $root push origin feature/dockerization 2>&1 | ForEach-Object { Write-Host $_ }
        $pushRc = $LASTEXITCODE
        Write-Host "PUSH_RC: $pushRc"
        if ($pushRc -ne 0) {
            & git -C $root reset --soft HEAD~1 2>&1 | ForEach-Object { Write-Host $_ }
            throw "push fail, reset --soft HEAD~1"
        }
        & git -C $root status -sb 2>&1 | ForEach-Object { Write-Host $_ }
        & git -C $root log -1 --oneline 2>&1 | ForEach-Object { Write-Host $_ }
    } finally { $ErrorActionPreference = $oldEAP }

    Write-Host "=== 6. Проверки ==="
    Write-Host ("REPORT_LEN: " + ([System.IO.File]::ReadAllText($rep73, [System.Text.Encoding]::UTF8)).Length)
    Write-Host ("START_LEN:  " + ([System.IO.File]::ReadAllText($start74, [System.Text.Encoding]::UTF8)).Length)
    Write-Host ("PAM_LEN:    " + ([System.IO.File]::ReadAllText($pam, [System.Text.Encoding]::UTF8)).Length)
    Write-Host ("RULES_LEN:  " + ([System.IO.File]::ReadAllText($rulesPs, [System.Text.Encoding]::UTF8)).Length)

    Write-Host "OK: 73_03 завершён"
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
