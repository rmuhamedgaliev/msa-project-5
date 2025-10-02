# Task 6: API для запуска Spring Batch с трейсингом

## Что сделано

Доработал Spring Batch приложение из Task 5:
- Batch задача запускается через REST API, а не автоматически
- Написал Python клиент, который вызывает API
- Добавил OpenTelemetry для distributed tracing
- Подключил Jaeger для визуализации трейсов
- В логах теперь traceId, spanId и URI для отслеживания запросов

## Запуск

### Сборка и старт

```bash
cd task-6/results
./gradlew clean build
docker build -t batch-processing .
docker-compose up -d
```

Подождите минуту пока все запустится.

### Перезапуск клиента

Клиент запускается автоматически, но может стартануть раньше приложения. Если нужно - перезапустите:

```bash
docker-compose restart batch-client
```

## Доступ к сервисам

- **Приложение**: http://localhost:8080
- **Jaeger** (трейсы): http://localhost:16686
- **Kibana** (логи): http://localhost:5601
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Как работает трейсинг

### OpenTelemetry

**Java (Spring Boot):**
- Использует Micrometer Tracing с OpenTelemetry bridge
- Автоматически создает spans для HTTP запросов
- Отправляет трейсы в Jaeger через OTLP
- TraceId и SpanId автоматом добавляются в логи

**Python клиент:**
- OpenTelemetry SDK для создания spans
- Автоматическая инструментация requests библиотеки
- Отправка трейсов в Jaeger через OTLP HTTP

### Jaeger UI

1. Открыть http://localhost:16686
2. Выбрать сервис `batch-client` или `batch-processing`
3. Нажать "Find Traces"
4. Кликнуть на любой трейс

Увидите:
- Waterfall диаграмму всех операций
- Время выполнения каждого span
- HTTP метод, URL, status code
- Связь между клиентом и сервером

### Корреляция с логами

Главная фишка - можно связать трейсы и логи:

1. В Jaeger найти интересный трейс и скопировать traceId
2. В Kibana вставить в поиск: `traceId:"<ваш-trace-id>"`
3. Увидеть все логи этого конкретного запроса

Это помогает понять что происходило на каждом этапе и быстро найти причину ошибки.

## Формат логов

Логи в JSON с полями:
```json
{
  "timestamp": "2025-10-01T23:26:49.613762786Z",
  "traceId": "1bd6c7e0d5b91805148ab4ce80ea9263",
  "spanId": "b2486471a8d58aa6",
  "uri": "/api/run-batch",
  "level": "INFO",
  "msg": "Starting batch job via REST API"
}
```

## API endpoints

**GET /api/status**
- Проверка что приложение живо

**POST /api/run-batch**
- Запуск batch job
- Возвращает результат выполнения

Пример:
```bash
curl -X POST http://localhost:8080/api/run-batch
```

## Что изменилось по сравнению с Task 5

1. `build.gradle` - добавил OpenTelemetry зависимости вместо Brave
2. `application.properties` - настроил OTLP endpoint для Jaeger
3. `BatchController.java` - добавил MDC для traceId/spanId/uri в логи
4. `JobRunner.java` - убрал автозапуск, теперь только через API
5. Добавил Python клиент с OpenTelemetry SDK
6. `docker-compose.yml` - добавил Jaeger и batch-client сервисы

## Остановка

```bash
docker-compose down -v
```
