#!/bin/bash
# ============================================================
# entrypoint.sh — Точка входа контейнера АРМ "Адаптация под DBI"
# ============================================================
# Переменные окружения:
#   MODE      — "gui" (по умолчанию) или "headless"
#   SRC_DIR   — путь к исходному коду в PATCH_IN (по умолчанию patch_WORK)
#   DST_DIR   — путь к результирующему коду в PATCH_OUT (по умолчанию patch_WORK)
#   LOG_LEVEL — уровень логирования: DEBUG, INFO, WARNING, ERROR (по умолчанию INFO)
#   RULES     — JSON-строка с выбранными правилами рубрикатора (опционально)
# ============================================================

set -euo pipefail

# --- Цвета для логирования ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    case "$level" in
        INFO)    echo -e "${GREEN}[$timestamp] [INFO]    $msg${NC}" ;;
        WARNING) echo -e "${YELLOW}[$timestamp] [WARNING] $msg${NC}" ;;
        ERROR)   echo -e "${RED}[$timestamp] [ERROR]   $msg${NC}" ;;
        DEBUG)   echo -e "${CYAN}[$timestamp] [DEBUG]   $msg${NC}" ;;
    esac
    # Дублируем в лог-файл
    echo "[$timestamp] [$level] $msg" >> "$LOG_FILE"
}

# --- Конфигурация из переменных окружения ---
MODE="${MODE:-gui}"
SRC_DIR="${SRC_DIR:-patch_WORK}"
DST_DIR="${DST_DIR:-patch_WORK}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Пути
APP_DIR="/app"
PATCH_IN="$APP_DIR/PATCH_IN"
PATCH_OUT="$APP_DIR/PATCH_OUT"
LOGS_DIR="$APP_DIR/logs"

# Имя исходного и целевого каталога
SRC_PATH="$PATCH_IN/$SRC_DIR"
DST_PATH="$PATCH_OUT/$DST_DIR"

# Лог-файл
LOG_FILE="$LOGS_DIR/entrypoint_$(date '+%Y%m%d_%H%M%S').log"

# --- Проверка директорий ---
mkdir -p "$PATCH_IN" "$PATCH_OUT" "$LOGS_DIR"

log INFO "============================================"
log INFO "  АРМ Адаптация под DBI — Container Entrypoint"
log INFO "  Version: $APP_VERSION"
log INFO "  Mode: $MODE"
log INFO "============================================"

# --- Headless-режим ---
if [ "$MODE" = "headless" ]; then
    log INFO "Запуск в headless-режиме (без GUI)"
    log INFO "  Исходный каталог: $SRC_PATH"
    log INFO "  Целевой каталог:  $DST_PATH"
    log INFO "  Уровень логов:    $LOG_LEVEL"

    # Проверка наличия исходных данных
    if [ ! -d "$SRC_PATH" ] || [ -z "$(ls -A "$SRC_PATH" 2>/dev/null)" ]; then
        log ERROR "Исходный каталог пуст или не существует: $SRC_PATH"
        log ERROR "Смонтируйте данные в $PATCH_IN/<каталог> и запустите контейнер"
        exit 1
    fi

    # Создаём целевой каталог
    mkdir -p "$DST_PATH"

    # Переносим данные в целевой каталог (структура сохраняется)
    cp -a "$SRC_PATH/." "$DST_PATH/"
    log INFO "Данные скопированы в $DST_PATH"

    # Запуск сканирования
    log INFO "=== Запуск сканирования (F5) ==="
    if [ -f "$APP_DIR/SRC/gui_app.py" ]; then
        python "$APP_DIR/SRC/gui_app.py" --headless \
            --src-dir "$DST_PATH" \
            --log-level "$LOG_LEVEL" \
            --scan-only
        SCAN_EXIT=$?
    else
        log ERROR "Файл gui_app.py не найден в $APP_DIR/SRC/"
        exit 1
    fi

    if [ $SCAN_EXIT -ne 0 ]; then
        log ERROR "Сканирование завершилось с ошибкой (код $SCAN_EXIT)"
        exit $SCAN_EXIT
    fi
    log INFO "Сканирование завершено успешно"

    # Проверка: есть ли проблемы для исправления
    SCAN_REPORT="$LOGS_DIR/scan_report_*.md"
    if ls "$SCAN_REPORT" 1>/dev/null 2>&1; then
        log INFO "Отчёт сканирования сохранён в $LOGS_DIR/"

        # Запуск исправления
        log INFO "=== Запуск исправления кода (F6) ==="
        if [ -f "$APP_DIR/SRC/gui_app.py" ]; then
            python "$APP_DIR/SRC/gui_app.py" --headless \
                --src-dir "$DST_PATH" \
                --log-level "$LOG_LEVEL" \
                --fix-only
            FIX_EXIT=$?
        else
            log ERROR "Файл gui_app.py не найден"
            exit 1
        fi

        if [ $FIX_EXIT -ne 0 ]; then
            log ERROR "Исправление завершилось с ошибкой (код $FIX_EXIT)"
            exit $FIX_EXIT
        fi
        log INFO "Исправление завершено успешно"
    else
        log WARNING "Отчёт сканирования не найден — пропуск исправления"
    fi

    # Архивация результатов
    log INFO "=== Архивация результатов ==="
    if command -v zip >/dev/null 2>&1; then
        ARCHIVE_NAME="patch_${DST_DIR}_$(date '+%Y%m%d_%H%M%S').zip"
        (cd "$PATCH_OUT" && zip -r "$ARCHIVE_NAME" "$DST_DIR" >/dev/null 2>&1)
        log INFO "Архив создан: $PATCH_OUT/$ARCHIVE_NAME"
    else
        # Fallback: tar.gz
        ARCHIVE_NAME="patch_${DST_DIR}_$(date '+%Y%m%d_%H%M%S').tar.gz"
        tar -czf "$PATCH_OUT/$ARCHIVE_NAME" -C "$PATCH_OUT" "$DST_DIR"
        log INFO "Архив создан: $PATCH_OUT/$ARCHIVE_NAME"
    fi

    log INFO "============================================"
    log INFO "  Headless-режим завершён успешно"
    log INFO "  Логи: $LOGS_DIR/"
    log INFO "  Результаты: $PATCH_OUT/"
    log INFO "============================================"
    exit 0
fi

# --- GUI-режим (по умолчанию) ---
log INFO "Запуск в GUI-режиме"

# Проверка X11
if [ -n "$DISPLAY" ]; then
    log INFO "X11-дисплей обнаружен: $DISPLAY"
else
    log WARNING "X11-дисплей не обнаружен. Запуск GUI может не сработать."
    log WARNING "Для GUI-режима используйте -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix"
    log WARNING "Или запустите в headless-режиме: -e MODE=headless"
fi

log INFO "Запуск gui_app.py..."
exec python "$APP_DIR/SRC/gui_app.py" "$@"
