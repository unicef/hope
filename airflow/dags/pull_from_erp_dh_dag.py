from datetime import datetime, timedelta
from airflow import DAG
from operators.pull_from_erp_dh_operator import PullFromErpDh


dag = DAG(
    "PullFromErpDh",
    description="Pull data from erp datahub schema",
    schedule_interval="@hourly",
    start_date=datetime.now() - timedelta(hours=23, minutes=30),
)

django_operator = PullFromErpDh(
    task_id="pull_from_erp_dh",
    dag=dag,
    provide_context=True,
    retries=3,
    retry_delay=timedelta(seconds=3),
)
