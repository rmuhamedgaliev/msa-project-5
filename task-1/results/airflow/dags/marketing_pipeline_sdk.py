from datetime import datetime, timedelta
from airflow import DAG
from airflow.sdk import task
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.task.trigger_rule import TriggerRule
import pandas as pd
import json
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_success_email():
    print("Отправка email об успешном выполнении пайплайна с отчетами") 
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        orders_df = pd.read_csv('/opt/airflow/results/orders_processed.csv')
        summary_data = {
            'metric': [
                'Общее количество заказов',
                'Успешных заказов',
                'Проблемных заказов',
                'Общая сумма заказов',
                'Средний чек'
            ],
            'value': [
                len(orders_df),
                len(orders_df[orders_df['status'] == 'completed']),
                len(orders_df[orders_df['status'] != 'completed']),
                f"{orders_df['amount'].sum():.2f}",
                f"{orders_df['amount'].mean():.2f}"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_file = '/opt/airflow/results/executive_summary_report.csv'
        summary_df.to_csv(summary_file, index=False, encoding='utf-8')
        print(f"Создан сводный отчет: {summary_file}")
    except Exception as e:
        print(f"Ошибка создания сводного отчета: {e}")
        summary_file = None
    
    body = f"""
    Пайплайн Marketing Data Pipeline выполнен успешно!
    
    Анализ заказов по статусам завершен.
    Результаты сохранены в /opt/airflow/results/
    
    Время выполнения: {current_time}
    
    Вложения:
    - executive_summary_report.csv - Сводка по успешным и проблемным заказам
    - orders_processed.csv - Данные заказов с разбивкой по статусам
    """.strip()
    
    send_email_with_attachments('admin@company.com', 'Успешное выполнение пайплайна - Отчеты', body, summary_file)

def send_error_email(context):
    try:
        print("Отправка email об ошибке в пайплайне")
        task_instance = context.get('task_instance')
        task_id = task_instance.task_id if task_instance else 'unknown'
        dag_id = context.get('dag').dag_id if context.get('dag') else 'unknown'
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        body = f"""
        Ошибка в пайплайне Marketing Data Pipeline!
        
        Задача: {task_id}
        DAG: {dag_id}
        Время ошибки: {current_time}
        
        Пожалуйста, проверьте логи для получения подробной информации.
        """.strip()
        
        send_email('admin@company.com', 'Ошибка в пайплайне', body)
        print(f"Email об ошибке отправлен для задачи {task_id}")
        
    except Exception as e:
        print(f"Ошибка при отправке email об ошибке: {str(e)}")
        logging.error(f"Ошибка при отправке email об ошибке: {str(e)}")

def send_email(email_to, subject, body):
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = "airflow@company.com"
        msg["To"] = email_to

        with smtplib.SMTP('mailhog', 1025) as server:
            server.sendmail("airflow@company.com", email_to, msg.as_string())
        print(f"Email отправлен успешно на {email_to}")
    except Exception as e:
        print(f"Ошибка отправки email: {e}")

def send_email_with_attachments(email_to, subject, body, summary_file=None):
    try:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = "airflow@company.com"
        msg["To"] = email_to

        msg.attach(MIMEText(body, "plain", "utf-8"))

        attachments = []
        
        if summary_file and os.path.exists(summary_file):
            attachments.append(summary_file)
        
        data_files = [
            '/opt/airflow/results/orders_processed.csv'
        ]
        
        for file_path in data_files:
            if os.path.exists(file_path):
                attachments.append(file_path)

        for file_path in attachments:
            try:
                with open(file_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                filename = os.path.basename(file_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
                print(f"Прикреплен файл: {filename}")
            except Exception as e:
                print(f"Ошибка прикрепления файла {file_path}: {e}")

        with smtplib.SMTP('mailhog', 1025) as server:
            server.sendmail("airflow@company.com", email_to, msg.as_string())
        print(f"Email с вложениями отправлен успешно на {email_to}")
    except Exception as e:
        print(f"Ошибка отправки email с вложениями: {e}")

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'marketing_data_pipeline_sdk',
    default_args=default_args,
    description='Демо пайплайн для маркетингового отдела - POC Task 1',
    schedule=None,
    catchup=False,
    tags=['marketing', 'task1', 'poc'],
    dag_display_name='Демо пайплайн для маркетингового отдела - POC Task 1',
) as dag:

    @task(retries=1, retry_delay=timedelta(minutes=1), on_failure_callback=send_error_email)
    def read_from_files():
        try:
            import random
            
            if random.random() < 0.8:
                raise Exception("Симуляция ошибки чтения файлов - файл поврежден")
            
            df = pd.read_csv('/opt/airflow/sample_data/orders.csv')
            source = "CSV Files"
            
            os.makedirs('/opt/airflow/results', exist_ok=True)
            df.to_csv('/opt/airflow/results/orders_processed.csv', index=False)
            
            stats = {
                'total_orders': len(df),
                'completed_orders': len(df[df['status'] == 'completed']),
                'problem_orders': len(df[df['status'] != 'completed']),
                'total_revenue': float(df['amount'].sum()),
                'avg_order_value': float(df['amount'].mean()),
                'source': source
            }
            
            logging.info(f"Извлечено {len(df)} заказов из файловой системы")
            return stats
            
        except Exception as e:
            logging.error(f"Ошибка чтения из файлов: {str(e)}")
            raise

    @task(retries=2, retry_delay=timedelta(minutes=1), on_failure_callback=send_error_email)
    def analyze_orders(orders_stats):
        try:
            import random
            
            if random.random() < 0.15:
                raise Exception("Симуляция ошибки анализа - недостаточно данных для анализа")
            
            total_orders = orders_stats['total_orders']
            completed_orders = orders_stats['completed_orders']
            problem_orders = orders_stats['problem_orders']
            total_revenue = orders_stats['total_revenue']
            
            success_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
            
            logging.info(f"Анализ заказов:")
            logging.info(f"  - Всего заказов: {total_orders}")
            logging.info(f"  - Успешных заказов: {completed_orders}")
            logging.info(f"  - Проблемных заказов: {problem_orders}")
            logging.info(f"  - Процент успеха: {success_rate:.1f}%")
            logging.info(f"  - Общая выручка: {total_revenue:.2f}")
            
            analysis_result = {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'problem_orders': problem_orders,
                'total_revenue': total_revenue,
                'success_rate': success_rate
            }
            
            with open('/opt/airflow/results/orders_analysis.json', 'w') as f:
                json.dump(analysis_result, f, indent=2)
            
            logging.info("Анализ заказов завершен")
            return analysis_result
                
        except Exception as e:
            logging.error(f"Ошибка анализа заказов: {str(e)}")
            raise

    @task.branch(retries=1, retry_delay=timedelta(minutes=1), on_failure_callback=send_error_email)
    def decide_processing_path(analysis_result):
        try:
            import random
            
            if random.random() < 0.1:
                raise Exception("Симуляция ошибки принятия решения - система недоступна")
            
            completed_orders = analysis_result['completed_orders']
            problem_orders = analysis_result['problem_orders']
            
            logging.info(f"Принятие решения о ветвлении:")
            logging.info(f"  - Успешных заказов: {completed_orders}")
            logging.info(f"  - Проблемных заказов: {problem_orders}")
            
            if completed_orders >= problem_orders:
                logging.info("Успешных заказов больше или равно - выбираем обработку успешных заказов")
                return 'process_successful_orders'
            else:
                logging.info("Проблемных заказов больше - выбираем обработку проблемных заказов")
                return 'process_problem_orders'
                
        except Exception as e:
            logging.error(f"Ошибка принятия решения: {str(e)}")
            return 'process_problem_orders'

    @task(retries=2, retry_delay=timedelta(minutes=1), on_failure_callback=send_error_email)
    def process_successful_orders():
        try:
            import random
            
            if random.random() < 0.08:
                raise Exception("Симуляция ошибки обработки успешных заказов - база данных недоступна")
            
            logging.info("Обработка успешных заказов")
            
            orders_df = pd.read_csv('/opt/airflow/results/orders_processed.csv')
            successful_orders = orders_df[orders_df['status'] == 'completed']
            
            report = {
                'processing_type': 'successful_orders',
                'count': len(successful_orders),
                'total_value': float(successful_orders['amount'].sum()),
                'avg_value': float(successful_orders['amount'].mean()),
                'status_breakdown': successful_orders['status'].value_counts().to_dict(),
                'generated_at': datetime.now().isoformat()
            }
            
            with open('/opt/airflow/results/successful_orders_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            logging.info(f"Обработано {len(successful_orders)} успешных заказов")
            return report
                
        except Exception as e:
            logging.error(f"Ошибка обработки успешных заказов: {str(e)}")
            raise

    @task(retries=2, retry_delay=timedelta(minutes=1), on_failure_callback=send_error_email)
    def process_problem_orders():
        try:
            import random
            
            if random.random() < 0.12:
                raise Exception("Симуляция ошибки обработки проблемных заказов - система аналитики недоступна")
            
            logging.info("Обработка проблемных заказов")
            
            orders_df = pd.read_csv('/opt/airflow/results/orders_processed.csv')
            problem_orders = orders_df[orders_df['status'] != 'completed']
            
            report = {
                'processing_type': 'problem_orders',
                'count': len(problem_orders),
                'total_value': float(problem_orders['amount'].sum()),
                'avg_value': float(problem_orders['amount'].mean()),
                'status_breakdown': problem_orders['status'].value_counts().to_dict(),
                'generated_at': datetime.now().isoformat()
            }
            
            with open('/opt/airflow/results/problem_orders_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            logging.info(f"Обработано {len(problem_orders)} проблемных заказов")
            return report
                
        except Exception as e:
            logging.error(f"Ошибка обработки проблемных заказов: {str(e)}")
            raise

    @task(retries=2, retry_delay=timedelta(minutes=1), on_failure_callback=send_error_email, trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
    def create_executive_summary(**context):
        try:
            executive_summary = {
                'executive_summary': {
                    'pipeline_name': 'Marketing Data Processing Pipeline',
                    'execution_date': context.get('ds', context.get('logical_date', datetime.now().strftime('%Y-%m-%d'))),
                    'execution_status': 'completed',
                    'processing_type': 'status_based_branching',
                    'key_metrics': {
                        'total_orders_processed': 'Available in detailed reports',
                        'status_analysis': 'Completed with branching',
                        'processing_paths': 'Successful/Problematic orders processing'
                    },
                    'next_steps': [
                        'Review status-based processing results',
                        'Analyze order status trends',
                        'Schedule next pipeline run',
                        'Monitor order statuses'
                    ],
                    'generated_at': datetime.now().isoformat()
                }
            }
            
            try:
                with open('/opt/airflow/results/executive_summary.json', 'w') as f:
                    json.dump(executive_summary, f, indent=2)
                logging.info(f"Файл executive_summary.json создан успешно")
            except Exception as e:
                logging.error(f"Ошибка создания файла executive_summary.json: {str(e)}")
                with open('/opt/airflow/results/executive_summary.json', 'w') as f:
                    json.dump(executive_summary, f, indent=2)
            
            logging.info("Создана исполнительная сводка")
            return executive_summary
            
        except Exception as e:
            logging.error(f"Ошибка создания исполнительной сводки: {str(e)}")
            raise

        @task(trigger_rule=TriggerRule.ONE_FAILED)
        def send_immediate_failure_alert(**context):
            failed_tasks = []
            task_instance = context.get('task_instance')
            
            if task_instance and task_instance.state == 'failed':
                failed_tasks.append(task_instance.task_id)
            
            if failed_tasks:
                body = f"""
                СРОЧНО: Ошибка в пайплайне Marketing Data Pipeline!
                
                Упавшие задачи: {', '.join(failed_tasks)}
                Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                Пайплайн остановлен. Требуется вмешательство.
                """
                
                send_email('admin@company.com', 'СРОЧНО: Ошибка в пайплайне', body)
                print(f"Отправлено срочное уведомление об ошибке в: {failed_tasks}")
            
            return {"failed_tasks": failed_tasks}

    @task(retries=1, retry_delay=timedelta(minutes=1), on_failure_callback=send_error_email, trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
    def send_notification():
        send_success_email()
        return "Success email sent"

    start_pipeline = EmptyOperator(
        task_id='start_pipeline',
        dag=dag
    )
    start_pipeline.display_name = "Запуск пайплайна"

    read_files_task = read_from_files()
    read_files_task.display_name = "Чтение из файловой системы"

    analyze_orders_task = analyze_orders(read_files_task)
    analyze_orders_task.display_name = "Анализ данных"

    decide_path_task = decide_processing_path(analyze_orders_task)
    decide_path_task.display_name = "Принятие решения о ветвлении"

    process_successful_task = process_successful_orders()
    process_successful_task.display_name = "Обработка успешных заказов"

    process_problem_task = process_problem_orders()
    process_problem_task.display_name = "Обработка проблемных заказов"

    executive_summary_task = create_executive_summary()
    executive_summary_task.display_name = "Создание исполнительной сводки"

    notification_task = send_notification()
    notification_task.display_name = "Отправка уведомления"

    failure_alert = send_immediate_failure_alert()
    failure_alert.display_name = "Срочное уведомление об ошибке"

    end_pipeline = EmptyOperator(
        task_id='end_pipeline',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
        dag=dag
    )
    end_pipeline.display_name = "Завершение пайплайна"

    start_pipeline >> read_files_task >> analyze_orders_task >> decide_path_task
    decide_path_task >> [process_successful_task, process_problem_task]
    [process_successful_task, process_problem_task] >> executive_summary_task >> notification_task >> end_pipeline

    [read_files_task, analyze_orders_task, decide_path_task, process_successful_task, process_problem_task] >> failure_alert