CREATE TABLE products  (
    id BIGSERIAL PRIMARY KEY,
    productId BIGINT NOT NULL,
    productSku BIGINT NOT NULL,
    productName VARCHAR(20),
    productAmount BIGINT,
    productData VARCHAR(120),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loyality_data  (
    productSku BIGINT NOT NULL PRIMARY KEY,
    loyalityData VARCHAR(120)
);

INSERT INTO loyality_data (productSku, loyalityData) VALUES 
(20001, 'Loyality_on'),
(30001, 'Loyality_off'),
(40001, 'Loyality_on'),
(50001, 'Loyality_off'),
(60001, 'Loyality_on');