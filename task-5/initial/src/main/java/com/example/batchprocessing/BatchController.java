package com.example.batchprocessing;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

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
	public String status() {
		return "Batch Processing Application is running";
	}

	@PostMapping("/run-batch")
	public String runBatch() {
		try {
			log.info("Starting batch job via REST API...");
			JobParameters jobParameters = new JobParametersBuilder()
				.addLong("time", System.currentTimeMillis())
				.toJobParameters();
			jobLauncher.run(importProductJob, jobParameters);
			log.info("Batch job completed successfully via REST API");
			return "Batch job completed successfully";
		} catch (Exception e) {
			log.error("Error running batch job via REST API", e);
			return "Error: " + e.getMessage();
		}
	}
}
