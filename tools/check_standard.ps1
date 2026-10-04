# DS_CNT_007: обёртка над tools\check_standard.py.
# Проверка файла на соответствие DS_STANDARD.md (раздел 2) через Ollama.
$ErrorActionPreference = "Stop"
$arm = "F:\TO_DBI"
Set-Location $arm
python "$arm\tools\check_standard.py" @args
exit $LASTEXITCODE
