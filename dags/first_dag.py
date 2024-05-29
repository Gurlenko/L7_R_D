from typing import Iterable
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.context import Context
from airflow.utils.task_group import TaskGroup
from airflow.providers.http.hooks.http import HttpHook
from airflow.models.taskinstance import TaskInstance
from airflow.operators.branch import BaseBranchOperator
from airflow.models.variable import Variable
from airflow.operators.email import EmailOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime
import json


class RateBaseOperator(BaseBranchOperator):

    def choose_branch(self, context: Context):
        ti: TaskInstance = context.get('ti')
        rate = ti.xcom_pull(task_ids='get_rates', key='rate')
        previous_rate = Variable.get(key='previous_rate', default_var=0.0)
        Variable.set(key='previous_rate', value=rate)
        if float(rate) > float(previous_rate):
            return 'go_up'
        return 'go_down'



def get_rate(**kwargs):
    HttpHook_hook = HttpHook(
    method='GET',
    http_conn_id='coin_conn',
    )
    ti: TaskInstance = kwargs.get('ti')
    response = HttpHook_hook.run('v1/bpi/currentprice.json')
    current_rate = float(json.loads(response.content)['bpi']['USD']['rate_float'])
    print(f"Current rate {current_rate}")
    ti.xcom_push('rate', current_rate)
    return current_rate

DEFAULT_ARGS = {
    'depends_on_past': False,
    'email' : 'gurlenko.13032001@gmail.com',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': 30
}


with DAG(
    dag_id='example_dag_1',
    start_date=datetime(year=2024, month=5, day=28),
    schedule_interval='0 0 * * *',
    default_args=DEFAULT_ARGS,
    tags=['Sales', 'R_D']
) as dag:

    start_task = EmptyOperator(
        task_id = 'start'
    )

    get_rate_task = bash_task = PythonOperator(
            task_id="get_rates",
            python_callable=get_rate,
        )
    
    branch_task = RateBaseOperator(
        task_id = 'branch_rate'
    )

    go_up = EmptyOperator(
        task_id = 'go_up'
    )

    go_down = EmptyOperator(
        task_id = 'go_down'
    )

    send_email_task = EmailOperator(
        task_id = 'send_email',
        to= DEFAULT_ARGS['email'],
        subject='tipidor',
        html_content= '<h1>Tu LOX</h1>'
        somne = TriggerRule.
    )

start_task >> get_rate_task >> branch_task
branch_task >> go_up
branch_task >> go_down