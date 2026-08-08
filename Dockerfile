# ============================================================
# Dockerfile — АРМ "Адаптация под DBI"
# Multi-stage сборка для минимизации размера образа
# ============================================================

# -----------------------------------------------------------
# Этап 1: Сборка зависимостей (опционально, для кэширования)
# -----------------------------------------------------------
FROM python:3.10-slim AS deps

WORKDIR /build

# Копируем requirements.txt для кэширования pip
COPY requirements.txt .

# Устанавливаем зависимости (если есть внешние)
# В данном проекте все зависимости — стандартная библиотека Python
RUN pip install --no-cache-dir --upgrade pip \
    && if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# -----------------------------------------------------------
# Этап 2: Исполняемый образ (минимальный)
# -----------------------------------------------------------
FROM python:3.10-slim AS runtime

# Метаданные
ARG APP_VERSION=v26.2.005
ARG BUILD_DATE
ARG VCS_REF

LABEL org.opencontainers.image.title="ARM-DBI-Adaptation" \
      org.opencontainers.image.description="АРМ Адаптация под DBI — автоматическая адаптация PLPlus-кода для миграции с Oracle на PostgreSQL" \
      org.opencontainers.image.vendor="Народный Банк" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.source="https://github.com/VitalyBashkirov/TO_DBI_2026.08.06" \
      org.opencontainers.image.licenses="Proprietary"

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION} \
    MODE=gui \
    SRC_DIR=patch_WORK \
    DST_DIR=patch_WORK \
    LOG_LEVEL=INFO \
    DISPLAY=:0

# Установка системных зависимостей:
# - fonts-liberation: шрифт для корректного отображения кириллицы в tkinter
# - x11-utils: утилиты X11 для headless-режима (xdpyinfo и др.)
# - zip: архивация результатов
RUN apt-get update && apt-get install -y --no-install-recommends \
        fonts-liberation \
        x11-utils \
        zip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Создаём системного пользователя (не root!)
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Рабочая директория
WORKDIR /app

# Копируем зависимости из этапа 1
COPY --from=deps /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Копируем исходный код приложения
COPY SRC/ ./SRC/
COPY RubricatorTemp/ ./RubricatorTemp/
COPY DATA/ ./DATA/

# Копируем entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Создаём директории для данных (точки монтирования)
RUN mkdir -p /app/PATCH_IN /app/PATCH_OUT /app/logs

# Меняем владельца (не root!)
RUN chown -R appuser:appuser /app

# Переключаемся на непривилегированного пользователя
USER appuser

# Порты (для GUI через X11 — порт 6000, но не публикуем, используем volume)
EXPOSE 6000

# Точка входа
ENTRYPOINT ["/entrypoint.sh"]

# Команда по умолчанию — запуск GUI
CMD ["python", "SRC/gui_app.py"]
