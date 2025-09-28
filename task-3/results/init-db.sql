-- Создание таблицы перевозок
CREATE TABLE IF NOT EXISTS shipments (
    id BIGSERIAL PRIMARY KEY,
    tracking_number VARCHAR(50) NOT NULL UNIQUE,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    driver_id BIGINT,
    vehicle_id BIGINT,
    client_id BIGINT
);

-- Создание таблицы событий перевозок
CREATE TABLE IF NOT EXISTS shipment_events (
    id BIGSERIAL PRIMARY KEY,
    shipment_id BIGINT NOT NULL REFERENCES shipments(id),
    event_type VARCHAR(100) NOT NULL,
    event_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(255)
);

-- Создание таблицы водителей
CREATE TABLE IF NOT EXISTS drivers (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) NOT NULL UNIQUE,
    phone VARCHAR(20),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы транспорта
CREATE TABLE IF NOT EXISTS vehicles (
    id BIGSERIAL PRIMARY KEY,
    license_plate VARCHAR(20) NOT NULL UNIQUE,
    vehicle_type VARCHAR(50) NOT NULL,
    capacity_kg INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы клиентов
CREATE TABLE IF NOT EXISTS clients (
    id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Добавление внешних ключей
ALTER TABLE shipments 
ADD CONSTRAINT fk_shipments_driver FOREIGN KEY (driver_id) REFERENCES drivers(id),
ADD CONSTRAINT fk_shipments_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
ADD CONSTRAINT fk_shipments_client FOREIGN KEY (client_id) REFERENCES clients(id);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_shipments_created_at ON shipments(created_at);
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipment_events_shipment_id ON shipment_events(shipment_id);
CREATE INDEX IF NOT EXISTS idx_shipment_events_created_at ON shipment_events(created_at);

-- Вставка тестовых данных
INSERT INTO drivers (first_name, last_name, license_number, phone, email) VALUES
('Иван', 'Петров', 'DL123456', '+7-900-123-4567', 'ivan.petrov@example.com'),
('Сергей', 'Сидоров', 'DL234567', '+7-900-234-5678', 'sergey.sidorov@example.com'),
('Алексей', 'Козлов', 'DL345678', '+7-900-345-6789', 'alexey.kozlov@example.com'),
('Дмитрий', 'Новиков', 'DL456789', '+7-900-456-7890', 'dmitry.novikov@example.com'),
('Андрей', 'Морозов', 'DL567890', '+7-900-567-8901', 'andrey.morozov@example.com');

INSERT INTO vehicles (license_plate, vehicle_type, capacity_kg) VALUES
('А123БВ777', 'Грузовик', 5000),
('В456ГД123', 'Фургон', 2000),
('С789ЕЖ456', 'Грузовик', 7000),
('Д012ЗИ789', 'Фургон', 1500),
('Е345КЛ012', 'Грузовик', 10000);

INSERT INTO clients (company_name, contact_person, phone, email, address) VALUES
('ООО "Логистика Плюс"', 'Мария Иванова', '+7-495-123-4567', 'maria@logistics-plus.ru', 'Москва, ул. Логистическая, 1'),
('ИП "Быстрая Доставка"', 'Петр Сидоров', '+7-812-234-5678', 'petr@fast-delivery.ru', 'СПб, пр. Доставки, 15'),
('ЗАО "Транспортные Решения"', 'Анна Козлова', '+7-495-345-6789', 'anna@transport-solutions.ru', 'Москва, ул. Транспортная, 25'),
('ООО "Грузовик"', 'Михаил Новиков', '+7-495-456-7890', 'mikhail@gruzovik.ru', 'Москва, ул. Грузовая, 10'),
('ИП "Экспресс Логистика"', 'Елена Морозова', '+7-812-567-8901', 'elena@express-logistics.ru', 'СПб, ул. Экспрессная, 5');

-- Генерируем тестовые данные за последние несколько дней
INSERT INTO shipments (tracking_number, origin, destination, created_at, updated_at, status, driver_id, vehicle_id, client_id) VALUES
-- Данные за сегодня
('TRK001', 'Москва', 'Санкт-Петербург', CURRENT_TIMESTAMP - INTERVAL '2 hours', CURRENT_TIMESTAMP - INTERVAL '1 hour', 'in_transit', 1, 1, 1),
('TRK002', 'Санкт-Петербург', 'Москва', CURRENT_TIMESTAMP - INTERVAL '1 hour', CURRENT_TIMESTAMP - INTERVAL '30 minutes', 'delivered', 2, 2, 2),
('TRK003', 'Москва', 'Казань', CURRENT_TIMESTAMP - INTERVAL '3 hours', CURRENT_TIMESTAMP - INTERVAL '2 hours', 'in_transit', 3, 3, 3),
('TRK004', 'Казань', 'Москва', CURRENT_TIMESTAMP - INTERVAL '4 hours', CURRENT_TIMESTAMP - INTERVAL '3 hours', 'delivered', 4, 4, 4),
('TRK005', 'Москва', 'Екатеринбург', CURRENT_TIMESTAMP - INTERVAL '5 hours', CURRENT_TIMESTAMP - INTERVAL '4 hours', 'in_transit', 5, 5, 5),

-- Данные за вчера
('TRK006', 'Санкт-Петербург', 'Москва', CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '2 hours', 'delivered', 1, 1, 1),
('TRK007', 'Москва', 'Новосибирск', CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '1 hour', CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '3 hours', 'delivered', 2, 2, 2),
('TRK008', 'Новосибирск', 'Москва', CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '2 hours', CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '4 hours', 'delivered', 3, 3, 3),

-- Данные за позавчера
('TRK009', 'Москва', 'Краснодар', CURRENT_TIMESTAMP - INTERVAL '2 days', CURRENT_TIMESTAMP - INTERVAL '2 days' + INTERVAL '1 hour', 'delivered', 4, 4, 4),
('TRK010', 'Краснодар', 'Москва', CURRENT_TIMESTAMP - INTERVAL '2 days' + INTERVAL '1 hour', CURRENT_TIMESTAMP - INTERVAL '2 days' + INTERVAL '2 hours', 'delivered', 5, 5, 5);

INSERT INTO shipment_events (shipment_id, event_type, event_description, created_at, location) VALUES
(1, 'pickup', 'Груз принят к перевозке', CURRENT_TIMESTAMP - INTERVAL '2 hours', 'Москва, склад А'),
(1, 'departure', 'Грузовик отправился в путь', CURRENT_TIMESTAMP - INTERVAL '1 hour 30 minutes', 'Москва'),
(2, 'pickup', 'Груз принят к перевозке', CURRENT_TIMESTAMP - INTERVAL '1 hour', 'Санкт-Петербург, склад Б'),
(2, 'delivery', 'Груз доставлен получателю', CURRENT_TIMESTAMP - INTERVAL '30 minutes', 'Москва, адрес доставки'),
(3, 'pickup', 'Груз принят к перевозке', CURRENT_TIMESTAMP - INTERVAL '3 hours', 'Москва, склад В'),
(3, 'departure', 'Грузовик отправился в путь', CURRENT_TIMESTAMP - INTERVAL '2 hours 30 minutes', 'Москва'),
(4, 'pickup', 'Груз принят к перевозке', CURRENT_TIMESTAMP - INTERVAL '4 hours', 'Казань, склад Г'),
(4, 'delivery', 'Груз доставлен получателю', CURRENT_TIMESTAMP - INTERVAL '3 hours', 'Москва, адрес доставки'),
(5, 'pickup', 'Груз принят к перевозке', CURRENT_TIMESTAMP - INTERVAL '5 hours', 'Москва, склад Д'),
(5, 'departure', 'Грузовик отправился в путь', CURRENT_TIMESTAMP - INTERVAL '4 hours 30 minutes', 'Москва');
