# DS_CNT_007: обёртка над tools\explain_log.py.
# Разбор хвоста EXCHANGE\bot.log через Ollama.
$ErrorActionPreference = "Stop"
$arm = "F:\TO_DBI"
Set-Location $arm
python "$arm\tools\explain_log.py" @args
exit $LASTEXITCODE
