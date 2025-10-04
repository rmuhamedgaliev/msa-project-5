package com.example.batchprocessing;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import jakarta.annotation.PostConstruct;

@Component
public class JobRunner {

	private static final Logger log = LoggerFactory.getLogger(JobRunner.class);

	@Autowired
	private JobLauncher jobLauncher;

	@Autowired
	private Job importProductJob;

	@PostConstruct
	public void init() {
		log.info("Spring Batch application started. Use POST /api/run-batch to execute batch job.");

		new Thread(() -> {
			while (true) {
				try {
					Thread.sleep(60000);
					log.info("Application is running and ready for batch jobs...");
				} catch (InterruptedException e) {
					log.info("Background thread interrupted");
					break;
				}
			}
		}).start();
	}
}