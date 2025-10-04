# ADR-001: Решение по мониторингу, логированию и оповещению для TradeWare Batch Processing

### Автор
Rinat Muhamedgaliev

### Дата
2025-10-01

## Контекст

TradeWare столкнулась с проблемами производительности при обработке больших объемов складских данных (до 400,000 строк в сутки, с пиками до 1,200,000 строк). Для обеспечения стабильной работы системы и быстрого реагирования на проблемы необходимо внедрить комплексное решение для мониторинга, логирования и оповещения.

### Функциональные требования

| № | Действующие лица или системы | Use Case | Описание |
| :-: | :- | :- | :- |
| 1 | DevOps инженер | Просмотр метрик приложения | Возможность просматривать метрики производительности batch-обработки в реальном времени |
| 2 | DevOps инженер | Поиск и анализ логов | Возможность искать и анализировать логи приложения для отладки проблем |
| 3 | Система мониторинга | Отправка алертов | Автоматическое оповещение при превышении пороговых значений метрик |
| 4 | Batch-приложение | Экспорт метрик | Приложение должно экспортировать метрики производительности |
| 5 | Batch-приложение | Отправка логов | Приложение должно отправлять структурированные логи |

### Нефункциональные требования

| № | Требование |
| :-: | :- |
| 1 | Минимальное влияние на производительность приложения (overhead < 5%) |
| 2 | Централизованное хранение логов с возможностью поиска |
| 3 | Retention логов минимум 30 дней |
| 4 | Retention метрик минимум 15 дней |
| 5 | Возможность масштабирования в облачной инфраструктуре GCP |
| 6 | Distributed tracing для отладки |
| 7 | Время обнаружения проблем (MTTD) < 1 минута |

## Решение

### 1. Monitoring Stack: Prometheus + Grafana

**Выбор: Prometheus для сбора метрик, Grafana для визуализации**

**Обоснование:**
- **Prometheus** - стандарт индустрии для мониторинга микросервисов
- Pull-модель минимизирует нагрузку на приложение
- Отличная интеграция со Spring Boot Actuator
- PromQL для гибких запросов к метрикам
- Grafana предоставляет мощные возможности визуализации
- Легко мигрируется в GCP (Google Cloud Monitoring совместим с Prometheus)

**Альтернативы:**
- JMX Exporter - более сложная настройка, избыточен для наших задач
- Micrometer с другими бэкендами - Prometheus проще и популярнее

### 2. Logging Stack: ELK (Elasticsearch + Logstash + Kibana)

**Выбор: ELK Stack с Filebeat для сбора логов**

**Обоснование:**
- **Elasticsearch** - мощный поиск по логам
- **Logstash** - гибкая обработка и трансформация логов
- **Kibana** - удобная визуализация и анализ
- **Filebeat** - легковесный агент сбора логов из Docker
- JSON-формат логов для структурированного анализа
- Distributed tracing через traceId/spanId
- Легко мигрируется в Google Cloud Logging

**Альтернативы:**
- Простой файловый логгинг - нет централизации и поиска
- Cloud-native решения (Google Cloud Logging) - зависимость от вендора на этапе разработки

### 3. Способ отправки метрик: Prometheus Pull Model

**Обоснование:**
- Приложение экспортирует метрики через `/actuator/prometheus`
- Prometheus забирает метрики каждые 5 секунд (scrape)
- Минимальная нагрузка на приложение
- Приложение не зависит от доступности Prometheus
- Простая настройка через Spring Boot Actuator

### 4. Способ отправки логов: Filebeat → Logstash → Elasticsearch

**Обоснование:**
- Логи пишутся в stdout в JSON формате
- Filebeat собирает логи из Docker containers
- Logstash обрабатывает и отправляет в Elasticsearch
- Минимальная нагрузка на приложение (нет прямой записи в Elasticsearch)
- Отказоустойчивость: если Elasticsearch недоступен, логи не теряются

## Собираемые метрики

### Business Metrics (Batch Processing)
1. **batch_processed_items_total** (Counter)
   - Общее количество обработанных items
   - Для отслеживания производительности и объемов

2. **batch_failed_items_total** (Counter)
   - Количество ошибок обработки
   - Для алертинга при росте ошибок

3. **batch_loyalty_data_updated_total** (Counter)
   - Количество обогащений данными лояльности
   - Для контроля корректности обработки

4. **batch_job_execution_duration_seconds** (Timer)
   - Длительность выполнения job
   - Для мониторинга производительности и SLA

### System Metrics (JVM/Spring Boot)
5. **process_cpu_usage** - Использование CPU
6. **jvm_memory_used_bytes** - Использование памяти (heap/non-heap)
7. **jvm_gc_pause_seconds** - Пауза GC
8. **jdbc_connections_active** - Активные DB соединения

## Конфигурация алертов

### Alert 1: High CPU Usage (Warning)
```yaml
Condition: process_cpu_usage > 80%
Duration: 1 минута
Severity: Warning
Action: Email/Slack notification
```

**Обоснование:** CPU > 80% более минуты может указывать на проблему производительности

### Alert 2: High Memory Usage (Warning)
```yaml
Condition: (heap_used / heap_max) > 85%
Duration: 2 минуты
Severity: Warning
Action: Email/Slack notification
```

**Обоснование:** Высокое использование памяти может привести к OutOfMemoryError

### Alert 3: Batch Job Failures (Critical)
```yaml
Condition: batch_failed_items_total > 0
Duration: Immediate
Severity: Critical
Action: Email/Slack/PagerDuty
```

**Обоснование:** Любая ошибка в batch-обработке требует немедленного внимания

### Alert 4: Slow Job Execution (Warning)
```yaml
Condition: batch_job_execution_duration > 60s
Duration: Immediate
Severity: Warning
Action: Email notification
```

**Обоснование:** Долгая обработка может указывать на проблемы с базой данных

## Архитектура логирования

### Формат логов: JSON с Logstash Logback Encoder
```json
{
  "timestamp": "2025-10-01T22:43:25.133Z",
  "level": "INFO",
  "logger": "com.example.batchprocessing.ProductItemProcessor",
  "msg": "Processing product: Product[productId=1]",
  "traceId": "68ddae8dd9fc8551872d9bd190331716",
  "spanId": "6ebd5a5320cc64c3",
  "thread": "http-nio-8080-exec-10"
}
```

**Преимущества:**
- Структурированный формат для автоматического парсинга
- TraceId для distributed tracing
- Легко фильтровать и искать в Kibana

### Уровни логирования
- **DEBUG**: Детальная информация о обработке (только в dev)
- **INFO**: Нормальные операции (старт/завершение job, обработка items)
- **WARN**: Потенциальные проблемы (отсутствие loyalty data)
- **ERROR**: Ошибки обработки (требуют внимания)

## Масштабирование в облако (GCP)

### Migration Path:
1. **Prometheus** → Google Cloud Monitoring (совместимый с Prometheus API)
2. **Grafana** → Google Cloud Monitoring Dashboards
3. **Elasticsearch** → Elasticsearch Service on GCP
4. **Filebeat/Logstash** → Google Cloud Logging agent

Все решения совместимы с GCP и легко мигрируются.

## Недостатки, ограничения, риски

### Недостатки выбранного решения:
- Дополнительные ресурсы для ELK stack (~2GB RAM минимум)
- Необходимость обучения команды работе с Prometheus/Grafana/Kibana
- Дополнительная сложность инфраструктуры и развертывания
- Требуется отдельная система для хранения метрик и логов

### Ограничения:
- Prometheus имеет ограничения на retention метрик (по умолчанию 15 дней)
- Elasticsearch может потребовать значительных ресурсов при росте объема логов
- Filebeat добавляет задержку в доставке логов (~5-10 секунд)
- Grafana alerts требуют дополнительной настройки notification channels

### Риски:
- Elasticsearch может требовать тюнинга и оптимизации при больших объемах логов
- Необходим регулярный мониторинг самих систем мониторинга (мониторинг мониторинга)
- При падении Elasticsearch логи могут теряться (необходим буфер в Logstash)
- Prometheus pull model требует доступности приложения для scraping
- При высокой нагрузке возможно увеличение latency метрик

