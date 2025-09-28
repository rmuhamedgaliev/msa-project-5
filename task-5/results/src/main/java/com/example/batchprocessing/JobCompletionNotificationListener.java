package com.example.batchprocessing;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.batch.core.BatchStatus;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.JobExecutionListener;
import org.springframework.jdbc.core.DataClassRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.MeterRegistry;

@Component
public class JobCompletionNotificationListener implements JobExecutionListener {

	private static final Logger log = LoggerFactory.getLogger(JobCompletionNotificationListener.class);

	private final JdbcTemplate jdbcTemplate;
	private final MeterRegistry meterRegistry;
	private final Timer jobExecutionTimer;

	public JobCompletionNotificationListener(JdbcTemplate jdbcTemplate, MeterRegistry meterRegistry) {
		this.jdbcTemplate = jdbcTemplate;
		this.meterRegistry = meterRegistry;
		this.jobExecutionTimer = Timer.builder("batch_job_execution_duration")
			.description("Duration of batch job execution")
			.register(meterRegistry);
	}

	@Override
	public void beforeJob(JobExecution jobExecution) {
		log.info("Starting batch job execution...");
	}

	@Override
	public void afterJob(JobExecution jobExecution) {
		long duration = java.time.Duration.between(jobExecution.getStartTime(), jobExecution.getEndTime()).toMillis();
		jobExecutionTimer.record(duration, java.util.concurrent.TimeUnit.MILLISECONDS);

		if (jobExecution.getStatus() == BatchStatus.COMPLETED) {
			log.info("Job completed successfully! Time to verify the results");

			jdbcTemplate.query("SELECT productId, productSku, productName, productAmount, productData FROM products ORDER BY id DESC LIMIT 5",
				new DataClassRowMapper<>(Product.class))
				.forEach(product -> log.info("Found <{}> in the database.", product));
		} else {
			log.warn("Job failed with status: {}", jobExecution.getStatus());
		}
	}
}
