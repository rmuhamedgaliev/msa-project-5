# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY app/requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY app/data_export.py .

# Создаем директорию для экспорта данных
RUN mkdir -p /app/data

# Устанавливаем права на запись в директорию данных
RUN chmod 755 /app/data

# Указываем пользователя для безопасности
RUN useradd -r -s /bin/false appuser && \
    chown -R appuser:appuser /app
USER appuser

# Указываем точку входа
ENTRYPOINT ["python", "data_export.py"]
