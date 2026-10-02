@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
title Ollama и LM Studio
color 0A

REM ============================================
REM РОТАЦИЯ ЛОГА
REM ============================================
set "LOGFILE=%~dp0ollama_lms.log"
if exist "%LOGFILE%" (
    for %%A in ("%LOGFILE%") do (
        if %%~zA gtr 1048576 (
            set "ARCHIVE=%~dp0ollama_lms_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%.log"
            set "ARCHIVE=!ARCHIVE: =0!"
            move "%LOGFILE%" "!ARCHIVE!" >nul 2>&1
        )
    )
)

set "CSVFILE=%~dp0test_results.csv"
set "CONFIG_FILE=F:\TO_DBI\tools\ai_local_worker_config.json"
set "TEMP_RESULT=%~dp0temp_result.txt"
set "TEMP_FIXES=%~dp0temp_fixes.txt"

REM ============================================
REM НАСТРОЙКИ
REM ============================================
set "OLLAMA_MODEL_CODER=deepseek-coder:6.7b"
set "OLLAMA_MODEL_CHAT=llama3.1:8b"
set "LMS_MODEL=deepseek-r1-distill-qwen-7b"
set "RAM_MIN_MB=4000"
set "NUM_CTX=4096"
set "KEEP_ALIVE=30m"

:MAIN_MENU
cls
echo ============================================
echo   ПРОВЕРКА OLLAMA
echo ============================================
echo.

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Ollama не найдена.
    goto OLLAMA_DONE
)
echo [OK] Ollama найдена.
ollama --version
echo.
echo [Запущенные модели в RAM]
ollama ps
echo.
echo [Скачанные модели]
ollama list

:OLLAMA_DONE

echo.
echo ============================================
echo   ПРОВЕРКА LM STUDIO
echo ============================================
echo.

where lms >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Утилита lms не найдена.
    goto LMS_DONE
)
echo [OK] Утилита lms найдена.
echo [Статус сервера]
lms server status
echo [Загруженные модели]
lms ps
echo [Скачанные модели]
lms ls

:LMS_DONE

echo.
call :SHOW_MEMORY

:MENU
echo ============================================
echo   ГЛАВНОЕ МЕНЮ
echo ============================================
echo   0. Выход
echo   1. Ollama: deepseek-coder:6.7b + batch 10 + fallback (AI-фиксы; тест ~28 мин/61 issue)
echo   2. Ollama: llama3.1:8b (диалог; тест ~28 сек/ответ; 5/5 OK)
echo   3. LM Studio: запуск модели + сервер
echo   4. Выгрузить ОБЕ
echo   5. Показать процессы + память
echo   6. Выгрузить только Ollama
echo   7. Выгрузить только LM Studio
echo   8. Очистить окно
echo   9. Запустить тест
echo  10. Запустить чат (Chat-Ollama)
echo ============================================
set /p choice="Ваш выбор (0-10): "

if "%choice%"=="" goto EXIT
if "%choice%"=="0" goto EXIT
if "%choice%"=="1" goto OLLAMA_START_CODER
if "%choice%"=="2" goto OLLAMA_START_CHAT
if "%choice%"=="3" goto START_LMS
if "%choice%"=="4" goto UNLOAD_BOTH
if "%choice%"=="5" goto SHOW_INFO
if "%choice%"=="6" goto KILL_OLLAMA
if "%choice%"=="7" goto KILL_LMS
if "%choice%"=="8" goto CLEAR_SCREEN
if "%choice%"=="9" goto TEST_MENU
if "%choice%"=="10" goto START_CHAT
echo [ОШИБКА] Неверный выбор.
timeout /t 2 >nul
goto MENU

:CLEAR_SCREEN
cls
goto MENU

REM ============================================
REM 10 — Запуск чата
REM ============================================
:START_CHAT
echo.
echo [ДЕЙСТВИЕ] Запуск чата через Chat-Ollama...
call :LOG "START_CHAT"
powershell -NoProfile -ExecutionPolicy Bypass -Command ". $PROFILE; Chat-Ollama -Model '%OLLAMA_MODEL_CHAT%'"
echo.
echo [ИНФО] Чат завершён.
pause
goto MENU

REM ============================================
REM 9 — Меню тестов
REM ============================================
:TEST_MENU
cls
echo ============================================
echo   ТЕСТЫ
echo ============================================
echo.
echo   Текущий конфиг:
if exist "%CONFIG_FILE%" (
    powershell -NoProfile -Command "$c = ConvertFrom-Json (Get-Content '%CONFIG_FILE%' -Raw); Write-Host ('  model:    ' + $c.model); Write-Host ('  batch:    ' + $c.batch_size); Write-Host ('  fallback: ' + $c.fallback_on_invalid)"
)
echo.
echo   1. Краткий тест (1 запрос)
echo   2. Расширенный тест (5 issues)
echo   3. Показать историю тестов
echo   4. Показать, что тестируем
echo.
echo   0. Назад
echo ============================================
set /p testchoice="Ваш выбор (0-4): "

if "%testchoice%"=="" goto MENU
if "%testchoice%"=="0" goto MENU
if "%testchoice%"=="1" goto TEST_SHORT
if "%testchoice%"=="2" goto TEST_LONG
if "%testchoice%"=="3" goto TEST_HISTORY
if "%testchoice%"=="4" goto TEST_SHOW
echo [ОШИБКА] Неверный выбор.
timeout /t 2 >nul
goto TEST_MENU

:TEST_SHOW
cls
echo ============================================
echo   ЧТО ТЕСТИРУЕМ
echo ============================================
echo.
echo [Конфиг] %CONFIG_FILE%
if exist "%CONFIG_FILE%" (
    powershell -NoProfile -Command "$c = ConvertFrom-Json (Get-Content '%CONFIG_FILE%' -Raw); Write-Host ('  model:      ' + $c.model); Write-Host ('  batch:      ' + $c.batch_size); Write-Host ('  fallback:   ' + $c.fallback_on_invalid); Write-Host ('  ollama_url: ' + $c.ollama_url); Write-Host ('  num_ctx:    ' + $c.num_ctx)"
) else (
    echo   [ОШИБКА] Конфиг не найден
)
echo.
echo [Промпт расширенного теста (5 issues)]:
echo ----------------------------------------
(
echo You are a PL/SQL to PostgreSQL migration expert. Fix the issues below.
echo.
echo EXAMPLE:
echo Issue: line 32, code: IS_EOD_NEW boolean;, rule: BAD_PREFIX, hint: rename to v_bIS_EOD_NEW
echo Fix: {"id": 1, "line": 32, "before": "IS_EOD_NEW boolean;", "after": "v_bIS_EOD_NEW boolean;", "reason": "Add boolean prefix v_b", "confidence": 0.95}
echo.
echo ISSUES:
echo 1. line 32, code: IS_EOD_NEW boolean;, rule: BAD_PREFIX, hint: rename to v_bIS_EOD_NEW
echo 2. line 33, code: stream_num string;, rule: BAD_PREFIX, hint: rename to v_sStream_num
echo 3. line 34, code: debug_on boolean;, rule: BAD_PREFIX, hint: rename to v_bDebug_on
echo 4. line 36, code: IdFile integer;, rule: BAD_PREFIX, hint: rename to v_iIdFile
echo 5. line 67, code: idx number := 0;, rule: BAD_PREFIX, hint: rename to v_nIdx
echo.
echo Return ONLY a JSON array with exactly 5 elements.
)
echo ----------------------------------------
echo.
echo [Краткий тест]:
echo   Запрос: "Say one word: works?"
echo   num_ctx: %NUM_CTX%
echo.
pause
goto TEST_MENU

:TEST_SHORT
echo.
echo [ТЕСТ] Краткий тест
if not exist "%CONFIG_FILE%" (
    echo [ОШИБКА] Конфиг не найден
    pause
    goto TEST_MENU
)
for /f "delims=" %%M in ('powershell -NoProfile -Command "(ConvertFrom-Json (Get-Content '%CONFIG_FILE%' -Raw)).model"') do set "CURRENT_MODEL=%%M"

echo [ИНФО] Модель: %CURRENT_MODEL%
call :GET_FREE_RAM
set "RAM_BEFORE=%FREE_RAM%"
echo [ИНФО] RAM до теста: %RAM_BEFORE% МБ
echo [ИНФО] Отправляю запрос...

if exist "%TEMP_RESULT%" del "%TEMP_RESULT%" >nul 2>&1
powershell -NoProfile -Command "$body = ConvertTo-Json @{ model = '%CURRENT_MODEL%'; messages = @(@{ role = 'user'; content = 'Say one word: works?' }); stream = $false; options = @{ num_ctx = %NUM_CTX% } }; $sw = [Diagnostics.Stopwatch]::StartNew(); try { $r = Invoke-RestMethod -Uri http://localhost:11434/api/chat -Method Post -Body $body -ContentType 'application/json' -ErrorAction Stop; $sw.Stop(); $sec = [math]::Round($sw.Elapsed.TotalSeconds,2); Set-Content -Path '%TEMP_RESULT%' -Value $sec; Write-Host '[OK] Ответ:' $r.message.content; Write-Host '[OK] Время:' $sec 'сек'; exit 0 } catch { $sw.Stop(); $sec = [math]::Round($sw.Elapsed.TotalSeconds,2); Set-Content -Path '%TEMP_RESULT%' -Value $sec; Write-Host '[ОШИБКА]' $_.Exception.Message; exit 1 }"

set "TEST_STATUS=OK"
if !errorlevel! neq 0 set "TEST_STATUS=FAIL"

set "TEST_TIME=?"
if exist "%TEMP_RESULT%" (
    for /f "delims=" %%T in ('type "%TEMP_RESULT%"') do set "TEST_TIME=%%T"
)

call :GET_FREE_RAM
set "RAM_AFTER=%FREE_RAM%"
echo [ИНФО] RAM после теста: %RAM_AFTER% МБ

call :LOG_TEST "short" "ollama" "%CURRENT_MODEL%" "%RAM_BEFORE%" "%RAM_AFTER%" "%TEST_TIME%" "%TEST_STATUS%" "1"
call :LOG "TEST_SHORT: model=%CURRENT_MODEL%, time=%TEST_TIME%s, ram=%RAM_BEFORE%->%RAM_AFTER%, status=%TEST_STATUS%"

if exist "%TEMP_RESULT%" del "%TEMP_RESULT%" >nul 2>&1

echo.
echo [ГОТОВО] Тест завершён: %TEST_STATUS%
pause
goto TEST_MENU

:TEST_LONG
echo.
echo [ТЕСТ] Расширенный тест
if not exist "%CONFIG_FILE%" (
    echo [ОШИБКА] Конфиг не найден
    pause
    goto TEST_MENU
)
for /f "delims=" %%M in ('powershell -NoProfile -Command "(ConvertFrom-Json (Get-Content '%CONFIG_FILE%' -Raw)).model"') do set "CURRENT_MODEL=%%M"

echo [ИНФО] Модель: %CURRENT_MODEL%
call :GET_FREE_RAM
set "RAM_BEFORE=%FREE_RAM%"
echo [ИНФО] RAM до теста: %RAM_BEFORE% МБ

set "PROMPT_FILE=%~dp0temp_prompt.txt"
(
echo You are a PL/SQL to PostgreSQL migration expert. Fix the issues below.
echo.
echo EXAMPLE:
echo Issue: line 32, code: IS_EOD_NEW boolean;, rule: BAD_PREFIX, hint: rename to v_bIS_EOD_NEW
echo Fix: {"id": 1, "line": 32, "before": "IS_EOD_NEW boolean;", "after": "v_bIS_EOD_NEW boolean;", "reason": "Add boolean prefix v_b", "confidence": 0.95}
echo.
echo ISSUES:
echo 1. line 32, code: IS_EOD_NEW boolean;, rule: BAD_PREFIX, hint: rename to v_bIS_EOD_NEW
echo 2. line 33, code: stream_num string;, rule: BAD_PREFIX, hint: rename to v_sStream_num
echo 3. line 34, code: debug_on boolean;, rule: BAD_PREFIX, hint: rename to v_bDebug_on
echo 4. line 36, code: IdFile integer;, rule: BAD_PREFIX, hint: rename to v_iIdFile
echo 5. line 67, code: idx number := 0;, rule: BAD_PREFIX, hint: rename to v_nIdx
echo.
echo Return ONLY a JSON array with exactly 5 elements.
) > "%PROMPT_FILE%"

echo [ИНФО] Отправляю промпт с 5 issues...

if exist "%TEMP_RESULT%" del "%TEMP_RESULT%" >nul 2>&1
if exist "%TEMP_FIXES%" del "%TEMP_FIXES%" >nul 2>&1

powershell -NoProfile -Command "$prompt = Get-Content '%PROMPT_FILE%' -Raw; $body = ConvertTo-Json @{ model = '%CURRENT_MODEL%'; messages = @(@{ role = 'user'; content = $prompt }); stream = $false; options = @{ num_ctx = %NUM_CTX% }; keep_alive = '%KEEP_ALIVE%' }; $sw = [Diagnostics.Stopwatch]::StartNew(); try { $r = Invoke-RestMethod -Uri http://localhost:11434/api/chat -Method Post -Body $body -ContentType 'application/json' -ErrorAction Stop; $sw.Stop(); $sec = [math]::Round($sw.Elapsed.TotalSeconds,2); Set-Content -Path '%TEMP_RESULT%' -Value $sec; $c = $r.message.content; Write-Host '[OK] Время:' $sec 'сек'; $json = [regex]::Match($c, '\[.*\]', 'Singleline').Value; if ($json) { $arr = ConvertFrom-Json $json; $cnt = $arr.Count; Set-Content -Path '%TEMP_FIXES%' -Value $cnt; Write-Host '[OK] JSON валидный, элементов:' $cnt } else { Write-Host '[ОШИБКА] JSON не найден'; Set-Content -Path '%TEMP_FIXES%' -Value 0 }; Write-Host ''; Write-Host $c.Substring(0, [Math]::Min(400, $c.Length)); exit 0 } catch { $sw.Stop(); $sec = [math]::Round($sw.Elapsed.TotalSeconds,2); Set-Content -Path '%TEMP_RESULT%' -Value $sec; Set-Content -Path '%TEMP_FIXES%' -Value 0; Write-Host '[ОШИБКА]' $_.Exception.Message; exit 1 }"

set "TEST_STATUS=OK"
if !errorlevel! neq 0 set "TEST_STATUS=FAIL"

set "TEST_TIME=?"
if exist "%TEMP_RESULT%" (
    for /f "delims=" %%T in ('type "%TEMP_RESULT%"') do set "TEST_TIME=%%T"
)

set "TEST_FIXES=0"
if exist "%TEMP_FIXES%" (
    for /f "delims=" %%F in ('type "%TEMP_FIXES%"') do set "TEST_FIXES=%%F"
)

call :GET_FREE_RAM
set "RAM_AFTER=%FREE_RAM%"
echo [ИНФО] RAM после теста: %RAM_AFTER% МБ

call :LOG_TEST "long5" "ollama" "%CURRENT_MODEL%" "%RAM_BEFORE%" "%RAM_AFTER%" "%TEST_TIME%" "%TEST_STATUS%" "%TEST_FIXES%/5"
call :LOG "TEST_LONG: model=%CURRENT_MODEL%, time=%TEST_TIME%s, fixes=%TEST_FIXES%/5, ram=%RAM_BEFORE%->%RAM_AFTER%, status=%TEST_STATUS%"

if exist "%PROMPT_FILE%" del "%PROMPT_FILE%" >nul 2>&1
if exist "%TEMP_RESULT%" del "%TEMP_RESULT%" >nul 2>&1
if exist "%TEMP_FIXES%" del "%TEMP_FIXES%" >nul 2>&1

echo.
echo [ГОТОВО] Тест завершён: %TEST_STATUS%
pause
goto TEST_MENU

:TEST_HISTORY
cls
echo ============================================
echo   ИСТОРИЯ ТЕСТОВ
echo ============================================
if not exist "%CSVFILE%" (
    echo [ИНФО] История пуста.
    pause
    goto TEST_MENU
)
powershell -NoProfile -Command "if (Test-Path '%CSVFILE%') { $rows = Import-Csv '%CSVFILE%'; $rows | Format-Table -AutoSize | Out-String -Width 250 | Write-Host } else { Write-Host '[ИНФО] История пуста.' }"
echo.
pause
goto TEST_MENU

:GET_FREE_RAM
for /f "delims=" %%R in ('powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024)"') do set "FREE_RAM=%%R"
exit /b

:GET_TIME_NOW
set "T=%time: =0%"
for /f "tokens=1-3 delims=:," %%a in ("%T%") do set "TIME_NOW=%%a:%%b:%%c"
exit /b

:LOG_TEST
set "T=%~1"
set "API=%~2"
set "M=%~3"
set "RB=%~4"
set "RA=%~5"
set "TS=%~6"
set "ST=%~7"
set "FX=%~8"

call :GET_TIME_NOW

if not exist "%CSVFILE%" (
    echo date, time, test, api, model, ram_before_mb, ram_after_mb, time_sec, status, fixes > "%CSVFILE%"
)

echo %date%, %TIME_NOW%, %T%, %API%, %M%, %RB%, %RA%, %TS%, %ST%, %FX% >> "%CSVFILE%"
exit /b

REM ============================================
REM 1 — deepseek-coder:6.7b + batch 10 + fallback
REM ============================================
:OLLAMA_START_CODER
echo.
echo [ДЕЙСТВИЕ] Запуск Ollama с %OLLAMA_MODEL_CODER%...
call :LOG "START_CODER: model=%OLLAMA_MODEL_CODER%"

echo [ИНФО] Проверяю наличие модели...
call :CHECK_MODEL_EXISTS "%OLLAMA_MODEL_CODER%"
if not "%CHECK_RESULT%"=="0" (
    echo [ОШИБКА] Модель %OLLAMA_MODEL_CODER% не найдена.
    echo         Скачайте: ollama pull %OLLAMA_MODEL_CODER%
    call :LOG "ERROR: model not found"
    pause
    goto MENU
)
echo [OK] Модель найдена.

echo [ИНФО] Проверяю RAM (нужно %RAM_MIN_MB% МБ)...
call :CHECK_RAM %RAM_MIN_MB%
if not "%RAM_RESULT%"=="0" (
    echo [ВНИМАНИЕ] Свободно меньше %RAM_MIN_MB% МБ ОЗУ.
    call :LOG "WARN: low RAM"
    pause
)
echo [OK] RAM достаточно.

taskkill /IM "ollama.exe" /F >nul 2>&1
taskkill /IM "ollama app.exe" /F >nul 2>&1
timeout /t 2 >nul

start "" "ollama app.exe"
echo [ИНФО] Ожидание запуска Ollama (8 сек)...
timeout /t 8 >nul

echo [ИНФО] Загружаю модель %OLLAMA_MODEL_CODER% в RAM (ctx=%NUM_CTX%, keep=%KEEP_ALIVE%)...
set TRIES=0
:LOAD_CODER_RETRY
set /a TRIES+=1
call :OLLAMA_LOAD "%OLLAMA_MODEL_CODER%"
if not "%LOAD_RESULT%"=="0" (
    if !TRIES! lss 5 (
        echo [ИНФО] Попытка !TRIES! не удалась...
        timeout /t 5 >nul
        goto LOAD_CODER_RETRY
    ) else (
        echo [ОШИБКА] Не удалось загрузить модель.
        call :LOG "ERROR: coder load failed"
        pause
        goto MENU
    )
)
echo [OK] Модель загружена.
call :LOG "OK: coder loaded"

call :UPDATE_WORKER_CONFIG "%OLLAMA_MODEL_CODER%" 10 true

echo.
echo [Загруженные модели Ollama]
ollama ps
call :SHOW_UNTIL
echo.
echo [ГОТОВО] Конфиг обновлён.
call :SHOW_MEMORY
pause
goto MENU

REM ============================================
REM 2 — llama3.1:8b (диалог)
REM ============================================
:OLLAMA_START_CHAT
echo.
echo [ДЕЙСТВИЕ] Запуск Ollama с %OLLAMA_MODEL_CHAT%...
call :LOG "START_CHAT_MODEL: model=%OLLAMA_MODEL_CHAT%"

echo [ИНФО] Проверяю наличие модели...
call :CHECK_MODEL_EXISTS "%OLLAMA_MODEL_CHAT%"
if not "%CHECK_RESULT%"=="0" (
    echo [ОШИБКА] Модель %OLLAMA_MODEL_CHAT% не найдена.
    echo         Скачайте: ollama pull %OLLAMA_MODEL_CHAT%
    call :LOG "ERROR: chat model not found"
    pause
    goto MENU
)
echo [OK] Модель найдена.

echo [ИНФО] Проверяю RAM (нужно %RAM_MIN_MB% МБ)...
call :CHECK_RAM %RAM_MIN_MB%
if not "%RAM_RESULT%"=="0" (
    echo [ВНИМАНИЕ] Свободно меньше %RAM_MIN_MB% МБ ОЗУ.
    call :LOG "WARN: low RAM"
    pause
)
echo [OK] RAM достаточно.

taskkill /IM "ollama.exe" /F >nul 2>&1
taskkill /IM "ollama app.exe" /F >nul 2>&1
timeout /t 2 >nul

start "" "ollama app.exe"
echo [ИНФО] Ожидание запуска Ollama (8 сек)...
timeout /t 8 >nul

echo [ИНФО] Загружаю модель %OLLAMA_MODEL_CHAT% в RAM (ctx=%NUM_CTX%, keep=%KEEP_ALIVE%)...
set TRIES=0
:LOAD_CHAT_RETRY
set /a TRIES+=1
call :OLLAMA_LOAD "%OLLAMA_MODEL_CHAT%"
if not "%LOAD_RESULT%"=="0" (
    if !TRIES! lss 5 (
        echo [ИНФО] Попытка !TRIES! не удалась...
        timeout /t 5 >nul
        goto LOAD_CHAT_RETRY
    ) else (
        echo [ОШИБКА] Не удалось загрузить модель.
        call :LOG "ERROR: chat model load failed"
        pause
        goto MENU
    )
)
echo [OK] Модель загружена.
call :LOG "OK: chat model loaded"

echo.
echo [Загруженные модели Ollama]
ollama ps
call :SHOW_UNTIL
echo.
echo [ИНФО] Для диалога запустите пункт 10 или Chat-Ollama вручную.
call :SHOW_MEMORY
pause
goto MENU

REM ============================================
REM 3 — LM Studio
REM ============================================
:START_LMS
echo.
echo [ДЕЙСТВИЕ] Запуск LM Studio с %LMS_MODEL%...
call :LOG "START_LMS: model=%LMS_MODEL%"

taskkill /IM "LM Studio.exe" /F >nul 2>&1
taskkill /IM "LMS.exe" /F >nul 2>&1
timeout /t 2 >nul

start "" "lms"
timeout /t 5 >nul

echo [ИНФО] Загружаю модель %LMS_MODEL%...
lms load %LMS_MODEL%
if %errorlevel% equ 0 (
    echo [OK] Модель загружена.
    call :LOG "OK: LMS model loaded"
) else (
    echo [ОШИБКА] Модель не загружена.
    call :LOG "ERROR: LMS model load failed"
)

echo [ИНФО] Запускаю сервер LM Studio...
lms server start
if %errorlevel% equ 0 (
    echo [OK] Сервер запущен.
    call :LOG "OK: LMS server started"
) else (
    echo [ОШИБКА] Сервер не запущен.
    call :LOG "ERROR: LMS server start failed"
)

echo.
echo [Статус сервера]
lms server status
echo.
echo [Загруженные модели]
lms ps
echo.
echo [API] http://localhost:1234
call :SHOW_MEMORY
pause
goto MENU

REM ============================================
REM 4 — Выгрузить обе
REM ============================================
:UNLOAD_BOTH
echo [ДЕЙСТВИЕ] Выгружаю обе...
call :LOG "UNLOAD_BOTH"
taskkill /IM "ollama.exe" /F >nul 2>&1
taskkill /IM "ollama app.exe" /F >nul 2>&1
taskkill /IM "LM Studio.exe" /F >nul 2>&1
taskkill /IM "LMS.exe" /F >nul 2>&1
echo [OK] Обе выгружены.
call :SHOW_MEMORY
pause
goto MENU

:KILL_OLLAMA
echo [ДЕЙСТВИЕ] Выгружаю Ollama...
call :LOG "KILL_OLLAMA"
taskkill /IM "ollama.exe" /F >nul 2>&1
taskkill /IM "ollama app.exe" /F >nul 2>&1
echo [OK] Ollama выгружена.
call :SHOW_MEMORY
pause
goto MENU

:KILL_LMS
echo [ДЕЙСТВИЕ] Выгружаю LM Studio...
call :LOG "KILL_LMS"
taskkill /IM "LM Studio.exe" /F >nul 2>&1
taskkill /IM "LMS.exe" /F >nul 2>&1
echo [OK] LM Studio выгружена.
call :SHOW_MEMORY
pause
goto MENU

:SHOW_INFO
echo.
echo [Процессы Ollama]
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if !errorlevel! equ 0 (tasklist /FI "IMAGENAME eq ollama.exe") else (echo [ИНФО] Нет ollama.exe.)
echo.
echo [Процессы LM Studio]
tasklist /FI "IMAGENAME eq LM Studio.exe" 2>nul | find /I "LM Studio.exe" >nul
if !errorlevel! equ 0 (tasklist /FI "IMAGENAME eq LM Studio.exe") else (echo [ИНФО] Нет LM Studio.exe.)
call :SHOW_MEMORY
pause
goto MENU

REM ============================================
REM ФУНКЦИИ
REM ============================================
:SHOW_MEMORY
echo.
echo ============================================
echo   СВОБОДНАЯ ПАМЯТЬ
echo ============================================
powershell -NoProfile -Command "$os = Get-CimInstance Win32_OperatingSystem; $free = [math]::Round($os.FreePhysicalMemory / 1024); $used = $os.TotalVisibleMemorySize/1024 - $free; Write-Host ('Всего: ' + [math]::Round($os.TotalVisibleMemorySize/1024) + ' МБ'); Write-Host ('Занято: ' + [math]::Round($used) + ' МБ'); Write-Host ('Свободно: ' + $free + ' МБ')"
echo.
exit /b

:SHOW_UNTIL
echo.
echo [ИНФО] Модель в RAM до UNTIL (keep_alive=%KEEP_ALIVE%).
exit /b

:CHECK_MODEL_EXISTS
set "M=%~1"
set "CHECK_RESULT=1"
ollama list 2>nul | find /I "%M%" >nul
if !errorlevel! equ 0 set "CHECK_RESULT=0"
exit /b

:CHECK_RAM
set "MIN_MB=%~1"
set "RAM_RESULT=1"
powershell -NoProfile -Command "if (((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory) -ge %MIN_MB%) { exit 0 } else { exit 1 }"
if !errorlevel! equ 0 set "RAM_RESULT=0"
exit /b

:OLLAMA_LOAD
set "M=%~1"
set "LOAD_RESULT=1"
powershell -NoProfile -Command "$body = ConvertTo-Json @{ model = '%M%'; messages = @(@{ role = 'user'; content = 'hi' }); stream = $false; options = @{ num_ctx = %NUM_CTX% }; keep_alive = '%KEEP_ALIVE%' }; try { Invoke-RestMethod -Uri http://localhost:11434/api/chat -Method Post -Body $body -ContentType 'application/json' -ErrorAction Stop | Out-Null; exit 0 } catch { exit 1 }"
if !errorlevel! equ 0 set "LOAD_RESULT=0"
exit /b

:LOG
set "MSG=%~1"
echo [%date% %time%] %MSG% >> "%LOGFILE%"
exit /b

:UPDATE_WORKER_CONFIG
set "MODEL=%~1"
set "BATCH=%~2"
set "FALLBACK=%~3"

powershell -NoProfile -Command "$cfg = @{ ollama_url = 'http://localhost:11434'; model = '%MODEL%'; batch_size = %BATCH%; fallback_batch_size = 5; fallback_on_invalid = $%FALLBACK%; temperature = 0.1; num_ctx = %NUM_CTX%; max_tokens = 2000; timeout_sec = 600; merge_same_line = $true }; Set-Content -Path '%CONFIG_FILE%' -Value (ConvertTo-Json $cfg -Depth 5) -Encoding UTF8"

if !errorlevel! equ 0 (
    echo [OK] Конфиг обновлён.
    call :LOG "config updated: model=%MODEL% batch=%BATCH%"
) else (
    echo [ОШИБКА] Не удалось обновить конфиг.
    call :LOG "ERROR: config update failed"
)
exit /b

:EXIT
echo.
echo Выход...
call :LOG "EXIT"
timeout /t 2 >nul
endlocal
exit