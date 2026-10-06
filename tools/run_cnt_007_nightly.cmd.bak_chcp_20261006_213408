@echo off
chcp 65001 >nul
REM DS_CNT_007: nightly pipeline (index + check-standard + explain-log + report)
setlocal

set ARM=F:\TO_DBI
set LOGS=%ARM%\logs
set EXIT=%LOGS%\ds_cnt_007.exit

echo [%date% %time%] DS_CNT_007 START >> "%LOGS%\ds_cnt_007.log"

REM :run_main
call "%ARM%\tools\run_cnt_005c_index.cmd"
if errorlevel 1 (
    echo %errorlevel% > "%EXIT%"
    echo [%date% %time%] DS_CNT_007 INDEX_FAIL >> "%LOGS%\ds_cnt_007.log"
    endlocal
    exit /b %errorlevel%
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%ARM%\tools\check_standard.ps1" >> "%LOGS%\ds_cnt_007.log" 2>&1
if errorlevel 1 (
    echo %errorlevel% > "%EXIT%"
    echo [%date% %time%] DS_CNT_007 CHECKSTD_FAIL >> "%LOGS%\ds_cnt_007.log"
    endlocal
    exit /b %errorlevel%
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%ARM%\tools\explain_log.ps1" >> "%LOGS%\ds_cnt_007.log" 2>&1
if errorlevel 1 (
    echo %errorlevel% > "%EXIT%"
    echo [%date% %time%] DS_CNT_007 EXPLAINLOG_FAIL >> "%LOGS%\ds_cnt_007.log"
    endlocal
    exit /b %errorlevel%
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%ARM%\tools\make_pilot_report.ps1" >> "%LOGS%\ds_cnt_007.log" 2>&1
set RC=%errorlevel%

echo %RC% > "%EXIT%"
echo [%date% %time%] DS_CNT_007 DONE RC=%RC% >> "%LOGS%\ds_cnt_007.log"

endlocal
exit /b %RC%
