#!/usr/bin/env python3

import os
import sys
import logging
import pandas as pd
import psycopg2
from datetime import date
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataExporter:
    def __init__(self):
        load_dotenv()
        
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'freight_analytics'),
            'user': os.getenv('DB_USERNAME', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }
        
        self.export_dir = os.getenv('EXPORT_DATA_DIRECTORY', '/app/data')
        os.makedirs(self.export_dir, exist_ok=True)
        
    def connect_to_database(self):
        try:
            connection = psycopg2.connect(**self.db_config)
            logger.info("Успешное подключение к базе данных")
            return connection
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise
    
    def export_shipments(self, connection):
        today = date.today()
        filename = f"shipments_{today.strftime('%Y-%m-%d')}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        logger.info(f"Экспорт данных перевозок в файл: {filepath}")
        
        try:
            query = """
                SELECT 
                    id, 
                    tracking_number, 
                    origin, 
                    destination, 
                    created_at, 
                    updated_at, 
                    status, 
                    driver_id, 
                    vehicle_id, 
                    client_id
                FROM shipments 
                WHERE DATE(created_at) = %s
                ORDER BY created_at
            """
            
            df = pd.read_sql_query(query, connection, params=[today])
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"Экспортировано {len(df)} записей перевозок")
            return len(df)
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте перевозок: {e}")
            raise
    
    def export_shipment_events(self, connection):
        today = date.today()
        filename = f"shipment_events_{today.strftime('%Y-%m-%d')}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        logger.info(f"Экспорт событий перевозок в файл: {filepath}")
        
        try:
            query = """
                SELECT 
                    se.id,
                    se.shipment_id,
                    se.event_type,
                    se.event_description,
                    se.created_at,
                    se.location,
                    s.tracking_number
                FROM shipment_events se
                JOIN shipments s ON se.shipment_id = s.id
                WHERE DATE(se.created_at) = %s
                ORDER BY se.created_at
            """
            
            df = pd.read_sql_query(query, connection, params=[today])
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"Экспортировано {len(df)} событий перевозок")
            return len(df)
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте событий перевозок: {e}")
            raise
    
    def export_drivers(self, connection):
        today = date.today()
        filename = f"drivers_{today.strftime('%Y-%m-%d')}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        logger.info(f"Экспорт данных водителей в файл: {filepath}")
        
        try:
            query = """
                SELECT 
                    id,
                    first_name,
                    last_name,
                    license_number,
                    phone,
                    email,
                    created_at
                FROM drivers
                ORDER BY created_at
            """
            
            df = pd.read_sql_query(query, connection)
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"Экспортировано {len(df)} записей водителей")
            return len(df)
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте водителей: {e}")
            raise
    
    def export_vehicles(self, connection):
        today = date.today()
        filename = f"vehicles_{today.strftime('%Y-%m-%d')}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        logger.info(f"Экспорт данных транспорта в файл: {filepath}")
        
        try:
            query = """
                SELECT 
                    id,
                    license_plate,
                    vehicle_type,
                    capacity_kg,
                    created_at
                FROM vehicles
                ORDER BY created_at
            """
            
            df = pd.read_sql_query(query, connection)
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"Экспортировано {len(df)} записей транспорта")
            return len(df)
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте транспорта: {e}")
            raise
    
    def export_clients(self, connection):
        today = date.today()
        filename = f"clients_{today.strftime('%Y-%m-%d')}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        logger.info(f"Экспорт данных клиентов в файл: {filepath}")
        
        try:
            query = """
                SELECT 
                    id,
                    company_name,
                    contact_person,
                    phone,
                    email,
                    address,
                    created_at
                FROM clients
                ORDER BY created_at
            """
            
            df = pd.read_sql_query(query, connection)
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"Экспортировано {len(df)} записей клиентов")
            return len(df)
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте клиентов: {e}")
            raise
    
    def run_export(self):
        logger.info(f"Начинаем экспорт данных за {date.today()}")
        
        connection = None
        try:
            connection = self.connect_to_database()
            
            total_records = 0
            total_records += self.export_shipments(connection)
            total_records += self.export_shipment_events(connection)
            total_records += self.export_drivers(connection)
            total_records += self.export_vehicles(connection)
            total_records += self.export_clients(connection)
            
            logger.info(f"Экспорт завершен успешно. Всего записей: {total_records}")
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте данных: {e}")
            sys.exit(1)
        finally:
            if connection:
                connection.close()
                logger.info("Соединение с базой данных закрыто")

def main():
    logger.info("Запуск приложения экспорта данных")
    
    try:
        exporter = DataExporter()
        exporter.run_export()
        logger.info("Приложение завершило работу успешно")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Приложение завершилось с ошибкой: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()