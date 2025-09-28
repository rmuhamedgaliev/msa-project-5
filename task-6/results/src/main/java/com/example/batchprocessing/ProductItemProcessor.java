package com.example.batchprocessing;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.batch.item.ItemProcessor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.DataClassRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;

import java.util.concurrent.atomic.AtomicReference;

@Component
public class ProductItemProcessor implements ItemProcessor<Product, Product> {

	private static final Logger log = LoggerFactory.getLogger(ProductItemProcessor.class);

	@Autowired
	private JdbcTemplate jdbcTemplate;

	@Autowired
	private MeterRegistry meterRegistry;

	private Counter processedItemsCounter;
	private Counter failedItemsCounter;
	private Counter loyaltyDataUpdatedCounter;

	@Autowired
	public void initCounters() {
		this.processedItemsCounter = Counter.builder("batch_processed_items_total")
			.description("Total number of items processed by the batch job")
			.register(meterRegistry);

		this.failedItemsCounter = Counter.builder("batch_failed_items_total")
			.description("Total number of items that failed processing")
			.register(meterRegistry);

		this.loyaltyDataUpdatedCounter = Counter.builder("batch_loyalty_data_updated_total")
			.description("Total number of items with loyalty data updated")
			.register(meterRegistry);
	}

    @Override
	public Product process(final Product product) {
		log.info("Processing product: {}", product);

		try {
			AtomicReference<String> loyaltyData = new AtomicReference<>("Loyality_off");
			boolean loyaltyUpdated = false;

			try {
				Loyality loyalty = jdbcTemplate.queryForObject(
					"SELECT * FROM loyality_data WHERE productSku = ?",
					new DataClassRowMapper<>(Loyality.class),
					product.productSku()
				);

				if (loyalty != null) {
					loyaltyData.set(loyalty.loyalityData());
					loyaltyUpdated = true;
				}
			} catch (Exception e) {
				log.warn("No loyalty data found for product SKU: {}", product.productSku());
			}

			Product transformedProduct = new Product(
				product.productId(),
				product.productSku(),
				product.productName(),
				product.productAmount(),
				loyaltyData.get()
			);

			processedItemsCounter.increment();
			if (loyaltyUpdated) {
				loyaltyDataUpdatedCounter.increment();
			}

			log.info("Transformed product: {}", transformedProduct);
			return transformedProduct;

		} catch (Exception e) {
			log.error("Error processing product: {}", product, e);
			failedItemsCounter.increment();
			throw e;
		}
	}

}
