@echo off
REM ============================================================
REM CNT Nightly Template - DO NOT RUN. Copy and fill.
REM DOC_ID: ARM-REG-CNT-000. Version 1.0.
REM ============================================================
setlocal EnableDelayedExpansion

set "ARM_ROOT=F:\TO_DBI"
set "CNT_ID=XXX"
set "LOG_DIR=%ARM_ROOT%\logs"
set "SCRIPT_NAME=%~n0"

REM Build timestamp from date/time (DD.MM.YYYY format)
for /f "tokens=1-3 delims=." %%a in ("%date%") do set "D=%%a%%b%%c"
set "TIME_PAD=%time: =0%"
for /f "tokens=1-3 delims=:," %%a in ("%TIME_PAD%") do set "T=%%a%%b%%c"
set "TS=%D%_%T%"
set "LOG_FILE=%LOG_DIR%\cnt_%CNT_ID%_%TS%.log"

echo [INFO] START: %SCRIPT_NAME% >> "%LOG_FILE%"

REM --- Check input data (fill in) ---
REM if not exist "%ARM_ROOT%\input.dat" (
REM     echo [ERROR] EXIT_CODE: 2 (input data missing) >> "%LOG_FILE%"
REM     endlocal
REM     exit /b 2
REM )

REM --- Main logic (fill in) ---
REM ...

REM --- END ---
echo [INFO] END: %SCRIPT_NAME% >> "%LOG_FILE%"
echo [INFO] EXIT_CODE: 0 >> "%LOG_FILE%"

endlocal
exit /b 0
