#!/bin/sh

echo "Waiting for Kibana to be ready..."
until curl -s http://kibana:5601/api/status | grep -q '"state":"green"'; do
  echo "Kibana is not ready yet. Waiting..."
  sleep 5
done

echo "Kibana is ready! Creating index pattern..."

# Create index pattern
curl -X POST "http://kibana:5601/api/saved_objects/index-pattern/filebeat-*" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{
    "attributes": {
      "title": "filebeat-*",
      "timeFieldName": "@timestamp",
      "fields": "[]"
    }
  }'

echo ""
echo "Setting default index pattern..."

# Set as default index pattern
curl -X POST "http://kibana:5601/api/kibana/settings/defaultIndex" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{
    "value": "filebeat-*"
  }'

echo ""
echo "Creating saved search for Batch Processing logs..."

# Create saved search for batch processing app logs
curl -X POST "http://kibana:5601/api/saved_objects/search/batch-processing-logs" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{
    "attributes": {
      "title": "Batch Processing Application Logs",
      "description": "Logs from Spring Batch application",
      "columns": ["@timestamp", "level", "logger", "msg", "traceId"],
      "sort": [["@timestamp", "desc"]],
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"query\":{\"query\":\"container.name: initial-app-1 AND msg: *\",\"language\":\"lucene\"},\"filter\":[],\"indexRefName\":\"kibanaSavedObjectMeta.searchSourceJSON.index\"}"
      }
    },
    "references": [
      {
        "id": "filebeat-*",
        "name": "kibanaSavedObjectMeta.searchSourceJSON.index",
        "type": "index-pattern"
      }
    ]
  }'

echo ""
echo "Creating saved search for Batch Job execution logs..."

# Create saved search for batch job execution
curl -X POST "http://kibana:5601/api/saved_objects/search/batch-job-execution" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{
    "attributes": {
      "title": "Batch Job Execution",
      "description": "Batch job execution logs with trace IDs",
      "columns": ["@timestamp", "level", "logger", "msg", "traceId", "spanId"],
      "sort": [["@timestamp", "desc"]],
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"query\":{\"query\":\"logger: *JobCompletionNotificationListener OR logger: *ProductItemProcessor\",\"language\":\"lucene\"},\"filter\":[],\"indexRefName\":\"kibanaSavedObjectMeta.searchSourceJSON.index\"}"
      }
    },
    "references": [
      {
        "id": "filebeat-*",
        "name": "kibanaSavedObjectMeta.searchSourceJSON.index",
        "type": "index-pattern"
      }
    ]
  }'

echo ""
echo "Kibana initialization completed! You can now access:"
echo "  - All logs: http://localhost:5601/app/discover"
echo "  - Batch Processing Logs: http://localhost:5601/app/discover#/?_a=(savedQuery:batch-processing-logs)"
echo "  - Batch Job Execution: http://localhost:5601/app/discover#/?_a=(savedQuery:batch-job-execution)"

