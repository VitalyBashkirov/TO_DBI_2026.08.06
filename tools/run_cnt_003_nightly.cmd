@echo off
REM run_cnt_003_nightly.cmd - CNT Stage 003
setlocal EnableDelayedExpansion
set "ARM_ROOT=F:\TO_DBI"
set "RC=0"
set "LOG_DIR=%ARM_ROOT%\logs"
set "LOG_FILE=%LOG_DIR%\ds_cnt_003.log"
set "EXIT_FILE=%LOG_DIR%\ds_cnt_003.exit"
set "ERR_FILE=%LOG_DIR%\ds_cnt_003.err"
set "LOCK_FILE=%LOG_DIR%\ds_cnt_003.lock"
set "PREV_EXIT=%LOG_DIR%\ds_cnt_002.exit"

echo locked > "%LOCK_FILE%"
>>"%LOG_FILE%" echo [INFO] START: run_cnt_003_nightly

REM --- check_deps ---
if not exist "%PREV_EXIT%" (
    >>"%LOG_FILE%" echo [ERROR] prev exit not found
    >"%EXIT_FILE%" echo 1
    set RC=1
    goto :cleanup
)
set /p PREV_CODE=<"%PREV_EXIT%"
if not "!PREV_CODE!"=="0" (
    >>"%LOG_FILE%" echo [ERROR] prev code=!PREV_CODE! neq 0
    >"%EXIT_FILE%" echo 1
    set RC=1
    goto :cleanup
)

REM Check YAML
python -c "import yaml;yaml.safe_load(open(r'%ARM_ROOT%\.continue\config.yaml',encoding='utf-8'))" 2>>"%ERR_FILE%"
if %errorlevel% neq 0 (
    >>"%LOG_FILE%" echo [ERROR] YAML invalid
    >"%EXIT_FILE%" echo 2
    set RC=2
    goto :cleanup
)

REM Check dirs
if not exist "%ARM_ROOT%\logs" (
    >>"%LOG_FILE%" echo [ERROR] logs missing
    >"%EXIT_FILE%" echo 4
    set RC=4
    goto :cleanup
)
if not exist "%ARM_ROOT%\tools" (
    >>"%LOG_FILE%" echo [ERROR] tools missing
    >"%EXIT_FILE%" echo 4
    set RC=4
    goto :cleanup
)
if not exist "%ARM_ROOT%\EXCHANGE\OUTBOX" (
    >>"%LOG_FILE%" echo [ERROR] OUTBOX missing
    >"%EXIT_FILE%" echo 4
    set RC=4
    goto :cleanup
)

REM Check write
echo test > "%LOG_DIR%\_write_test.tmp" 2>>"%ERR_FILE%"
if %errorlevel% neq 0 (
    >>"%LOG_FILE%" echo [ERROR] cannot write logs
    >"%EXIT_FILE%" echo 4
    set RC=4
    goto :cleanup
)
del "%LOG_DIR%\_write_test.tmp" 2>nul

REM --- run_main ---
REM 12.4 checklist in SEC_POLICY_AI
if not exist "%ARM_ROOT%\EXCHANGE\SEC_POLICY_AI.md" (
    >>"%LOG_FILE%" echo [ERROR] SEC_POLICY_AI.md missing
    >"%EXIT_FILE%" echo 2
    set RC=2
    goto :cleanup
)
>>"%LOG_FILE%" echo [INFO] 12.4 OK

>"%EXIT_FILE%" echo 0
>>"%LOG_FILE%" echo [INFO] EXIT_CODE: 0
goto :done

:cleanup
if exist "%LOCK_FILE%" del "%LOCK_FILE%"
endlocal & exit /b %RC%

:done
if exist "%LOCK_FILE%" del "%LOCK_FILE%"
endlocal & exit /b 0
