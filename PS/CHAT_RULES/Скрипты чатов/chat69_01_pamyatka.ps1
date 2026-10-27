Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$pam = 'F:\TO_DBI\PS\CHAT_RULES\Отчеты\Памятка_чатов.txt'
if (-not (Test-Path $pam)) { throw "Нет Памятки: $pam" }
$old = [System.IO.File]::ReadAllText($pam, [System.Text.Encoding]::UTF8)
$lines68 = @(
  '',
  '## Чат 68 (2026-10-27) — ЗАВЕРШЁН',
  '- Восстановлен ИКА patch_suboptimal_test_3 (3 .plp = zip-эталон 2026.10.18_X_suboptimal_query_wrownum.zip).',
  '- wrownum: v5.json 5.3.1 + scanner.py _check_plp_suboptimal_wrownum расширены (exit|return|raise|pragma error|message.error|app_error).',
  '- ЖВ К1: блок «ВЫБОР ПОЛЬЗОВАТЕЛЯ В РУБРИКАТОРЕ» работает; К1 в бою 3 срабатывания.',
  '- Коммит a045f4d, push в origin/feature/dockerization. test_ds186 зелёный (1 passed).',
  '',
  '## Чат 69 (2026-10-27) — В РАБОТЕ',
  '- Хост: LG.',
  '- Шаг 69_01: обновление этой Памятки (67_1).',
  '- Долг 1 (план): блок «ВЫБОР ПОЛЬЗОВАТЕЛЯ В РУБРИКАТОРЕ» в отчётах (scan_report_*.md, scan_VVVxVV_*.md, plpcheck_report_*.html) — в gui_app.py, дописывание после generate_report, тесты на три формата; scanner.py не править.',
  '- Долг 2 (план): SyntaxWarning invalid escape sequence '\s' в scanner.py:1257 -> r'...'.',
  '- Долг 3 (план): PSH_PS_DEL.plp for v_ps in this(idx).[B_PS] — отдельное правило, не wrownum.',
  '',
)
$add = ($lines68 -join "`r`n")
$new = $old.TrimEnd() + "`r`n" + $add + "`r`n"
$enc = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($pam, $new, $enc)
$b = [System.IO.File]::ReadAllBytes($pam)
$isBom = ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
if ($isBom) { throw "BOM в Памятке — нарушение 64_4" }
Write-Host ("Памятка обновлена: {0} байт, BOM={1}" -f $b.Length, $isBom)
Write-Host "--- tail ---"
[System.IO.File]::ReadAllLines($pam, [System.Text.Encoding]::UTF8) | Select-Object -Last 14 | Out-String | Write-Host
Write-Host "LOG: chat69_01_pamyatka DONE" -ForegroundColor Green
