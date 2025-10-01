-- Создание таблиц для TradeWare ETL системы

CREATE TABLE IF NOT EXISTS products (
    productId BIGINT NOT NULL PRIMARY KEY,
    productSku BIGINT NOT NULL,
    productName VARCHAR(20),
    productAmount BIGINT,
    productData VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS loyality_data (
    productSku BIGINT NOT NULL PRIMARY KEY,
    loyalityData VARCHAR(120)
);

-- Вставка тестовых данных лояльности
INSERT INTO loyality_data (productSku, loyalityData) VALUES 
(20001, 'Loyality_on'),
(30001, 'Loyality_on'),
(50001, 'Loyality_on'),
(60001, 'Loyality_on')
ON CONFLICT (productSku) DO NOTHING;

-- Создание индексов для оптимизации производительности
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(productSku);
CREATE INDEX IF NOT EXISTS idx_loyality_sku ON loyality_data(productSku);
