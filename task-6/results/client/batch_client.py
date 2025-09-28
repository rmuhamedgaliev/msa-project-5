import requests
import time
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

logger = logging.getLogger("BatchClient")

resource = Resource(attributes={
    "service.name": "batch-client"
})

provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4318/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)

trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

RequestsInstrumentor().instrument()

class BatchJobClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def trigger_batch_job(self):
        uri = f"{self.base_url}/api/run-batch"
        
        with tracer.start_as_current_span("trigger_batch_job") as span:
            span.set_attribute("http.method", "POST")
            span.set_attribute("http.url", uri)
            span.set_attribute("service.name", "batch-client")
            
            logger.info(f"Triggering batch job at {uri}")
            
            try:
                response = self.session.post(uri, timeout=30)
                
                span.set_attribute("http.status_code", response.status_code)
                
                if response.status_code == 200:
                    logger.info(f"Batch job triggered successfully: {response.text}")
                    span.set_attribute("job.status", "success")
                    return True
                else:
                    logger.error(f"Failed to trigger batch job: {response.status_code} - {response.text}")
                    span.set_attribute("job.status", "failed")
                    span.set_attribute("error", True)
                    return False
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error calling batch API: {str(e)}")
                span.set_attribute("error", True)
                span.record_exception(e)
                return False
    
    def check_status(self):
        uri = f"{self.base_url}/api/status"
        
        with tracer.start_as_current_span("check_application_status") as span:
            span.set_attribute("http.method", "GET")
            span.set_attribute("http.url", uri)
            
            logger.info(f"Checking application status at {uri}")
            
            try:
                response = self.session.get(uri, timeout=10)
                
                span.set_attribute("http.status_code", response.status_code)
                
                if response.status_code == 200:
                    logger.info(f"Application is running: {response.text}")
                    span.set_attribute("app.status", "healthy")
                    return True
                else:
                    logger.warning(f"Application returned status {response.status_code}")
                    span.set_attribute("app.status", "unhealthy")
                    return False
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking status: {str(e)}")
                span.set_attribute("error", True)
                span.record_exception(e)
                return False

def main():
    with tracer.start_as_current_span("batch_client_main") as main_span:
        main_span.set_attribute("service.name", "batch-client")
        main_span.set_attribute("operation.type", "batch_trigger")
        
        client = BatchJobClient("http://app:8080")
        
        logger.info("Starting batch job client")
        
        time.sleep(5)
        
        if not client.check_status():
            logger.error("Application is not available")
            main_span.set_attribute("error", True)
            return
        
        success_count = 0
        fail_count = 0
        
        for i in range(5):
            with tracer.start_as_current_span(f"job_execution_{i+1}") as job_span:
                job_span.set_attribute("job.iteration", i+1)
                logger.info(f"Starting job execution #{i+1}")
                
                if client.trigger_batch_job():
                    success_count += 1
                    job_span.set_attribute("result", "success")
                else:
                    fail_count += 1
                    job_span.set_attribute("result", "failed")
                
                if i < 4:
                    time.sleep(3)
        
        main_span.set_attribute("total.success", success_count)
        main_span.set_attribute("total.failed", fail_count)
        
        logger.info(f"Job execution completed. Success: {success_count}, Failed: {fail_count}")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
