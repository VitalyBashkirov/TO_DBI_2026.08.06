Clear-Host
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$ErrorActionPreference = 'Stop'
$Scripts = 'F:\TO_DBI\PS\CHAT_RULES\Скрипты чатов'
$log = 'F:\TO_DBI\PS\LG_71_03d1_make_frags.log'
Start-Transcript -Path $log -Force
Write-Host "hostTag=LG host=$env:COMPUTERNAME"
$encNoBom = New-Object System.Text.UTF8Encoding($false)

$oldA = @(
"        decl_re = re.compile("
"            r'^\\s*(\\w+)\\s+('",
"            r'integer|number|string|varchar2|date|boolean|timestamp|rowtype'",
"            r'|(?:ref\\s*)?\\[[\\w\\d_]+\\]'",
"            r'|&[\\w.]+'",
"            r')\\s*(\\(\\s*\\d+\\s*\\))?\\s*(?::=|;)',",
"            re.IGNORECASE",
"        )"
)
$newA = @(
"        decl_re = re.compile("
"            r'^\\s*(\\w+)\\s+('",
"            r'integer|number|string|varchar2|date|boolean|timestamp|rowtype'",
"            r'|(?:ref\\s*)?\\[[\\w\\d_]+\\]'",
"            r'|in\\s+\\[[\\w\\d_]+\\]'",
"            r'|&[\\w.]+'",
"            r')\\s*(\\(\\s*\\d+\\s*\\))?\\s*(?::=|;)',",
"            re.IGNORECASE",
"        )"
)
$oldA2 = @(
"                if type_str.lower().startswith('ref'):"
"                    type_str = 'ref'"
)
$newA2 = @(
"                if type_str.lower().startswith('ref'):"
"                    type_str = 'ref'"
"                elif type_str.lower().startswith('in'):"
"                    type_str = 'in'"
)
$oldB = @(
"        # Объявленные функции"
"        func_re = re.compile(r'^\\s*function\\s+(\\w+)\\s*\(', re.IGNORECASE)"
"        for i, line in enumerate(lines, 1):"
"            stripped = line.strip()"
"            if stripped.startswith('--'):"
"                continue"
"            fm = func_re.match(line)"
"            if fm:"
"                declared[fm.group(1)] = (i, 'func', stripped)"
)
$newB = @(
"        # Объявленные функции"
"        func_re = re.compile(r'^\\s*function\\s+(\\w+)\\s*\(', re.IGNORECASE)"
"        for i, line in enumerate(lines, 1):"
"            stripped = line.strip()"
"            if stripped.startswith('--'):"
"                continue"
"            fm = func_re.match(line)"
"            if fm:"
"                declared[fm.group(1)] = (i, 'func', stripped)"
"
"        # DS71: public function/procedure, procedure, method, batch method"
"        extra_kinds = ("
"            (re.compile(r'^\\s*batch\\s+method\\s+(\\w+)\\s+is\\b', re.IGNORECASE), 'batch_method'),"
"            (re.compile(r'^\\s*method\\s+(\\w+)\\s+is\\b', re.IGNORECASE), 'method'),"
"            (re.compile(r'^\\s*public\\s+function\\s+(\\w+)\\s*\(', re.IGNORECASE), 'func'),"
"            (re.compile(r'^\\s*public\\s+procedure\\s+(\\w+)\\s*\(', re.IGNORECASE), 'proc'),"
"            (re.compile(r'^\\s*procedure\\s+(\\w+)\\s*\(', re.IGNORECASE), 'proc'),"
"        )"
"        for i, line in enumerate(lines, 1):"
"            stripped = line.strip()"
"            if stripped.startswith('--'):"
"                continue"
"            for rx, kind in extra_kinds:"
"                m = rx.match(line)"
"                if m:"
"                    declared[m.group(1)] = (i, kind, stripped)"
"                    break"
)

function W([string]$path, [string[]]$arr) {
    [System.IO.File]::WriteAllLines($path, $arr, $encNoBom)
    $b = [System.IO.File]::ReadAllBytes($path)
    $isBom = ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
    Write-Host ("W {0} size={1} isBom={2}" -f $path, $b.Length, $isBom)
    if ($isBom) { throw "BOM found in $path" }
}

$base = $Scripts
W (Join-Path $base "chat71_03_frag_old_A.txt")  $oldA
W (Join-Path $base "chat71_03_frag_new_A.txt")  $newA
W (Join-Path $base "chat71_03_frag_old_A2.txt") $oldA2
W (Join-Path $base "chat71_03_frag_new_A2.txt") $newA2
W (Join-Path $base "chat71_03_frag_old_B.txt")  $oldB
W (Join-Path $base "chat71_03_frag_new_B.txt")  $newB
Write-Host "FRAGS DONE"
Stop-Transcript
Write-Host "LOG: $log" -ForegroundColor Green
