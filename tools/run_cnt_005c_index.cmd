@echo off
REM DS_CNT_005c: Nightly semantic indexer
REM Runs python -m tools.indexer.cli index --path F:\TO_DBI
setlocal

set ARM=F:\TO_DBI
set LOGS=%ARM%\logs
set EXIT=%LOGS%\ds_cnt_005c.exit

echo [%date% %time%] DS_CNT_005c START >> "%LOGS%\ds_cnt_005c_run.log"

REM :check_deps
if not exist "%LOGS%" (
    echo ERROR: logs dir missing
    echo 4 > "%EXIT%"
    exit /b 4
)

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: python not found
    echo 3 > "%EXIT%"
    exit /b 3
)

if not exist "%ARM%\.continue\config.yaml" (
    echo ERROR: config.yaml missing
    echo 2 > "%EXIT%"
    exit /b 2
)

REM Check Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama not available
    echo 3 > "%EXIT%"
    exit /b 3
)

REM :run_main
cd /d "%ARM%"
python -m tools.indexer.cli index --path "%ARM%" >> "%LOGS%\ds_cnt_005c_run.log" 2>&1
set RC=%errorlevel%

echo %RC% > "%EXIT%"
echo [%date% %time%] DS_CNT_005c DONE RC=%RC% >> "%LOGS%\ds_cnt_005c_run.log"

endlocal
exit /b %RC%
