# Мониторинг, логирование и оповещение для Spring Batch приложения TradeWare

## Описание работы

В рамках данного задания была разработана система мониторинга, логирования и оповещения для Spring Batch приложения обработки складских данных. Система включает в себя сбор метрик производительности, централизованное логирование и настройку алертов для проактивного обнаружения проблем.

## Архитектура решения

Реализована следующая архитектура:

**Monitoring Stack:**
- Prometheus - сбор и хранение метрик приложения
- Grafana - визуализация метрик и настройка алертов

**Logging Stack:**
- Elasticsearch - хранение и индексация логов
- Logstash - обработка и трансформация логов
- Kibana - поиск и визуализация логов
- Filebeat - сбор логов из Docker контейнеров

**Application:**
- Spring Batch приложение с интеграцией Micrometer для метрик
- PostgreSQL для хранения данных
- Spring Boot Actuator для экспорта метрик

## Структура проекта

```
task-5/results/
├── diagrams/                          # C4 диаграммы
│   ├── system-context.puml
│   ├── container-diagram.puml
│   └── component-diagram-monitoring.puml
├── src/main/java/                     # Spring Batch приложение
├── grafana/provisioning/              # Конфигурация Grafana
│   ├── datasources/
│   └── dashboards/
├── prometheus/                        # Конфигурация Prometheus
├── filebeat/                          # Конфигурация Filebeat
├── logstash/                          # Конфигурация Logstash
├── kibana/                            # Скрипты инициализации Kibana
├── ADR-001-monitoring-logging.md      # Архитектурное решение
├── docker-compose.yml                 # Оркестрация сервисов
└── README.md                          # Данный файл
```

## Предварительные требования

- Docker и Docker Compose
- JDK 17 или выше
- Минимум 4GB RAM для Docker
- Минимум 10GB свободного дискового пространства

## Инструкция по запуску

### Шаг 1: Сборка приложения

```bash
cd task-5/results
./gradlew build
```

### Шаг 2: Создание Docker образа

```bash
docker build -t batch-processing .
```

### Шаг 3: Запуск инфраструктуры

```bash
docker-compose up -d
```

### Шаг 4: Проверка статуса сервисов

```bash
docker ps
```

Все сервисы должны быть в статусе "healthy" или "running". Инициализация может занять 1-2 минуты.

### Шаг 5: Проверка работоспособности

```bash
# Проверка приложения
curl http://localhost:8080/api/status

# Проверка метрик
curl http://localhost:8080/actuator/prometheus | head -20

# Проверка Prometheus
curl http://localhost:9090/-/healthy

# Проверка Elasticsearch
curl http://localhost:9200/_cluster/health
```

## Доступ к интерфейсам

### Grafana
- URL: http://localhost:3000
- Логин: admin
- Пароль: admin
- Dashboard: http://localhost:3000/d/batch-processing-dashboard

### Kibana
- URL: http://localhost:5601
- Index Pattern создается автоматически при первом запуске
- Saved Searches доступны в разделе Discover

### Prometheus
- URL: http://localhost:9090
- Targets: http://localhost:9090/targets

### Spring Batch Application
- Status endpoint: http://localhost:8080/api/status
- Run batch job: http://localhost:8080/api/run-batch (POST)
- Metrics: http://localhost:8080/actuator/prometheus

## Запуск batch job для генерации данных

Для демонстрации работы системы мониторинга и логирования необходимо запустить batch job:

```bash
# Запуск одного job
curl -X POST http://localhost:8080/api/run-batch

# Запуск нескольких job для генерации данных
for i in {1..5}; do 
  curl -X POST http://localhost:8080/api/run-batch
  sleep 2
done
```

После выполнения:
- Метрики появятся в Grafana через 5-10 секунд
- Логи появятся в Kibana через 10-20 секунд

## Собираемые метрики

### Бизнес-метрики

| Метрика | Тип | Описание |
|---------|-----|----------|
| batch_processed_items_total | Counter | Общее количество обработанных записей |
| batch_failed_items_total | Counter | Количество ошибок при обработке |
| batch_loyalty_data_updated_total | Counter | Количество записей, обогащенных данными лояльности |
| batch_job_execution_duration_seconds | Timer | Длительность выполнения batch job |

### Системные метрики

| Метрика | Тип | Описание |
|---------|-----|----------|
| process_cpu_usage | Gauge | Использование CPU процессом (0-1) |
| jvm_memory_used_bytes | Gauge | Использование памяти JVM (heap/non-heap) |
| jvm_gc_pause_seconds | Summary | Длительность пауз сборки мусора |
| jdbc_connections_active | Gauge | Количество активных соединений с БД |

Подробное обоснование выбора метрик см. в ADR-001-monitoring-logging.md

## Настроенные алерты

В Grafana настроены следующие алерты:

### 1. High CPU Usage
- Условие: process_cpu_usage > 80%
- Длительность: 1 минута
- Уровень: Warning

### 2. High Memory Usage
- Условие: (heap_used / heap_max) > 85%
- Длительность: 2 минуты
- Уровень: Warning

### 3. Batch Job Failures
- Условие: batch_failed_items_total > 0
- Длительность: Immediate
- Уровень: Critical

### 4. Slow Job Execution
- Условие: batch_job_execution_duration > 60 секунд
- Длительность: Immediate
- Уровень: Warning

Обоснование конфигурации алертов см. в ADR-001-monitoring-logging.md

## Работа с логами

### Формат логов

Приложение выводит логи в JSON формате с поддержкой distributed tracing:

```json
{
  "timestamp": "2025-10-01T22:43:25.133Z",
  "level": "INFO",
  "logger": "com.example.batchprocessing.ProductItemProcessor",
  "msg": "Processing product: Product[productId=1]",
  "traceId": "68ddae8dd9fc8551872d9bd190331716",
  "spanId": "6ebd5a5320cc64c3"
}
```

### Поиск логов в Kibana

Примеры запросов для поиска в Kibana:

**Все логи приложения:**
```
container.name: *-app-* AND msg: *
```

**Только ошибки:**
```
level: ERROR
```

**Логи конкретного job execution:**
```
traceId: "68ddae8dd9fc8551872d9bd190331716"
```

**Обработка конкретного продукта:**
```
msg: *productId=1*
```

### Автоматически созданные Saved Searches

При запуске системы автоматически создаются:
1. "Batch Processing Application Logs" - все логи приложения
2. "Batch Job Execution" - логи выполнения batch jobs

## Просмотр метрик в Grafana

Dashboard "Batch Processing Monitoring" содержит следующие панели:

1. CPU Usage (%) - использование процессора
2. Memory Used (Heap) - использование heap памяти в байтах
3. Processing Rate - скорость обработки записей в секунду
4. Total Processed Items - общее количество обработанных записей
5. Total Failed Items - общее количество ошибок
6. Loyalty Data Updated - количество обогащений данными лояльности
7. Job Execution Duration - длительность выполнения jobs в секундах

Dashboard обновляется автоматически каждые 5 секунд.

## Примеры запросов в Prometheus

**Всего обработано записей:**
```
batch_processed_items_total
```

**Скорость обработки (записей в секунду):**
```
rate(batch_processed_items_total[1m])
```

**Максимальное время выполнения job:**
```
batch_job_execution_duration_seconds_max
```

**Использование CPU:**
```
process_cpu_usage * 100
```

**Использование памяти в процентах:**
```
(jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"}) * 100
```

## Остановка системы

```bash
# Остановка всех контейнеров
docker-compose down

# Остановка с удалением volumes
docker-compose down -v
```

## Масштабирование в облако

Разработанное решение легко масштабируется в Google Cloud Platform:

- Prometheus → Google Cloud Monitoring (совместимость с Prometheus API)
- Grafana → Google Cloud Dashboards
- Elasticsearch → Elasticsearch Service on GCP
- PostgreSQL → Cloud SQL for PostgreSQL

Подробный миграционный план см. в ADR-001-monitoring-logging.md

## Устранение неполадок

### Grafana не показывает данные

```bash
# Проверить targets в Prometheus
curl http://localhost:9090/api/v1/targets

# Перезапустить Grafana
docker restart grafana
```

### Логи не появляются в Kibana

```bash
# Проверить статус Filebeat
docker logs filebeat

# Проверить индексы в Elasticsearch
curl http://localhost:9200/_cat/indices?v

# Проверить инициализацию Kibana
docker logs kibana-init
```

### Приложение не запускается

```bash
# Просмотр логов приложения
docker logs initial-app-1

# Проверка подключения к PostgreSQL
docker logs initial-postgresdb-1

# Тест подключения к БД
docker exec -it initial-postgresdb-1 psql -U postgres -d productsdb -c "SELECT 1"
```

## Дополнительная документация

- **ADR-001-monitoring-logging.md** - полное архитектурное решение с обоснованиями
- **diagrams/** - C4 диаграммы системы (PlantUML)
  - system-context.puml - контекстная диаграмма
  - container-diagram.puml - диаграмма контейнеров
  - component-diagram-monitoring.puml - компонентная диаграмма с мониторингом

## Технологический стек

- Java 17
- Spring Boot 3.2.0
- Spring Batch
- Micrometer (метрики)
- Logback с Logstash Encoder (логирование)
- PostgreSQL (база данных)
- Prometheus v3.4.0
- Grafana v12.0.1
- Elasticsearch v7.17.28
- Logstash v7.17.28
- Kibana v7.17.28
- Filebeat v7.17.28
- Docker Compose v3.8
