@echo off
REM ============================================================
REM CNT_000 Nightly - Check ARM environment.
REM DOC_ID: ARM-REG-CNT-000. Version 1.0.
REM ============================================================
setlocal EnableDelayedExpansion

set "ARM_ROOT=F:\TO_DBI"
set "CNT_ID=000"
set "LOG_DIR=%ARM_ROOT%\logs"
set "SCRIPT_NAME=%~n0"

REM Build timestamp from date/time (DD.MM.YYYY format)
for /f "tokens=1-3 delims=." %%a in ("%date%") do set "D=%%a%%b%%c"
set "TIME_PAD=%time: =0%"
for /f "tokens=1-3 delims=:," %%a in ("%TIME_PAD%") do set "T=%%a%%b%%c"
set "TS=%D%_%T%"
set "LOG_FILE=%LOG_DIR%\cnt_%CNT_ID%_%TS%.log"

echo [INFO] START: %SCRIPT_NAME% >> "%LOG_FILE%"

if not exist "%ARM_ROOT%\logs" (
    echo [ERROR] logs\ not found >> "%LOG_FILE%"
    echo [INFO] EXIT_CODE: 3 >> "%LOG_FILE%"
    endlocal
    exit /b 3
)
if not exist "%ARM_ROOT%\\tools" (
    echo [ERROR] tools\ not found >> "%LOG_FILE%"
    echo [INFO] EXIT_CODE: 3 >> "%LOG_FILE%"
    endlocal
    exit /b 3
)
if not exist "%ARM_ROOT%\EXCHANGE\OUTBOX" (
    echo [ERROR] EXCHANGE\OUTBOX\ not found >> "%LOG_FILE%"
    echo [INFO] EXIT_CODE: 3 >> "%LOG_FILE%"
    endlocal
    exit /b 3
)

echo [INFO] Directories check: OK >> "%LOG_FILE%"

if not exist "%ARM_ROOT%\EXCHANGE\DS_CNT_000_regulation.md" (
    echo [ERROR] DS_CNT_000_regulation.md not found >> "%LOG_FILE%"
    echo [INFO] EXIT_CODE: 2 >> "%LOG_FILE%"
    endlocal
    exit /b 2
)

echo [INFO] Regulation check: OK >> "%LOG_FILE%"
echo [INFO] END: %SCRIPT_NAME% >> "%LOG_FILE%"
echo [INFO] EXIT_CODE: 0 >> "%LOG_FILE%"

endlocal
exit /b 0
