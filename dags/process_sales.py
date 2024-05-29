from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests


data_job1 = {
    'date': '2022-08-10',
    'base_path': '/Users/admin/Desktop/Data_engineering_L2/file_storage/raw/sales/' + '2022-08-10'
}

data_job2 = {
    'raw_dir': '/Users/admin/Desktop/Data_engineering_L2/file_storage/raw/sales/' + '2022-08-10',
    'stg_dir': '/Users/admin/Desktop/Data_engineering_L2/file_storage/stg/sales/' + '2022-08-10',
}


def run_job_1():
    print('Starting job 1')
    response = requests.post('http://host.docker.internal:8081/', json=data_job1)
    # assert response.status_code == 200
    print(response.text)


def run_job_2():
    print('Starting job 2')
    response = requests.post('http://host.docker.internal:8082/', json=data_job2)
    # assert response.status_code == 200
    print(response.text)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['gurlenko.1488@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': 5,
}

with DAG(    
    dag_id='process_sales',
    start_date=datetime(2022, 8, 9),
    # end_date=datetime(2022, 8, 12),
    default_args=default_args,
    schedule_interval="0 1 * * *",
    max_active_runs=1,
    catchup=True) as dag:

    extract_data_from_api = PythonOperator(
        task_id='extract_data_from_api',
        python_callable=run_job_1,
    )


    convert_to_avro = PythonOperator(
        task_id = 'convert_to_avro',
        python_callable = run_job_2,
    )

    extract_data_from_api >> convert_to_avro