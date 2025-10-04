# Task 5 - Monitoring & Logging

## Подготовка окружения

```bash
# Установка зависимостей
./gradlew build
```

## Создание образа

```bash
docker build . -t batch-processing
```

## Запуск приложения

```bash
docker-compose up
```

## Инициализация БД

Создать таблицы используя скрипт:
`task-5/initial/src/main/resources/schema-all.sql`

## Компоненты

- PostgreSQL (порт 5432)
- batch-processing
- grafana
- prometheus
- filebeat
- logstash
- elasticsearch