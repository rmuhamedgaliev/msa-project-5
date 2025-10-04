package com.example.batchprocessing;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.servlet.http.HttpServletRequest;

@RestController
@RequestMapping("/api")
public class BatchController {

    private static final Logger log = LoggerFactory.getLogger(BatchController.class);

    private final JobLauncher jobLauncher;
    private final Job importProductJob;

    public BatchController(JobLauncher jobLauncher, Job importProductJob) {
        this.jobLauncher = jobLauncher;
        this.importProductJob = importProductJob;
    }

    @GetMapping("/status")
    public String status(
            HttpServletRequest request,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceId,
            @RequestHeader(value = "X-Span-Id", required = false) String spanId) {
        
        setupMDC(request, traceId, spanId);
        
        log.info("Status check requested");
        
        clearMDC();
        
        return "Batch Processing Application is running";
    }

    @PostMapping("/run-batch")
    public String runBatch(
            HttpServletRequest request,
            @RequestHeader(value = "X-Trace-Id", required = false) String traceId,
            @RequestHeader(value = "X-Span-Id", required = false) String spanId) {
        
        setupMDC(request, traceId, spanId);
        
        try {
            log.info("Starting batch job via REST API");
            
            JobParameters jobParameters = new JobParametersBuilder()
                .addLong("time", System.currentTimeMillis())
                .addString("traceId", traceId != null ? traceId : MDC.get("traceId"))
                .toJobParameters();
            
            jobLauncher.run(importProductJob, jobParameters);
            
            log.info("Batch job completed successfully via REST API");
            
            return "Batch job completed successfully";
            
        } catch (Exception e) {
            log.error("Error running batch job via REST API", e);
            return "Error: " + e.getMessage();
        } finally {
            clearMDC();
        }
    }
    
    private void setupMDC(HttpServletRequest request, String traceId, String spanId) {
        if (traceId != null && !traceId.isEmpty()) {
            MDC.put("traceId", traceId);
        }
        if (spanId != null && !spanId.isEmpty()) {
            MDC.put("spanId", spanId);
        }
        
        String uri = request.getRequestURI();
        MDC.put("uri", uri);
        
        log.debug("MDC setup: traceId={}, spanId={}, uri={}", 
                 MDC.get("traceId"), MDC.get("spanId"), uri);
    }
    
    private void clearMDC() {
        MDC.remove("uri");
    }
}
