package com.example.batchprocessing;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.batch.item.ItemProcessor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.DataClassRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

@Component
public class ProductItemProcessor implements ItemProcessor<Product, Product> {

	private static final Logger log = LoggerFactory.getLogger(ProductItemProcessor.class);
	
	private final Map<Long, String> loyaltyCache = new ConcurrentHashMap<>();

	@Autowired
	private JdbcTemplate jdbcTemplate;

    @Override
	public Product process(final Product product) {
		try {
			final Long productId = product.productId();
			final Long productSku = product.productSku();
			final String productName = product.productName();
			final Long productAmount = product.productAmount();
			final String productData = product.productData();

			String loyaltyData = getLoyaltyData(productSku);
			
			Product transformedProduct = new Product(productId, productSku, productName, productAmount, loyaltyData);

			log.debug("Transforming product SKU {}: {} -> {}", productSku, productData, loyaltyData);

			return transformedProduct;
		} catch (Exception e) {
			log.error("Error processing product SKU {}: {}", product.productSku(), e.getMessage());
			throw new RuntimeException("Failed to process product", e);
		}
	}
	
	private String getLoyaltyData(Long productSku) {
		if (loyaltyCache.containsKey(productSku)) {
			return loyaltyCache.get(productSku);
		}
		
		String sql = "SELECT loyalityData FROM loyality_data WHERE productSku = ?";
		try {
			String loyaltyData = jdbcTemplate.queryForObject(sql, String.class, productSku);
			if (loyaltyData != null) {
				loyaltyCache.put(productSku, loyaltyData);
				return loyaltyData;
			}
		} catch (Exception e) {
			log.warn("No loyalty data found for SKU {}: {}", productSku, e.getMessage());
		}
		
		return "Loyality_off";
	}

}
