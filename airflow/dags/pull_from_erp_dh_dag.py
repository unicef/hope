from datetime import datetime, timedelta
from airflow import DAG
from operators.pull_from_erp_dh_operator import PullFromErpDh


dag = DAG(
    "PullFromErpDh",
    description="Pull data from erp datahub schema",
    schedule_interval="30 * * * *",
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = PullFromErpDh(
    task_id="pull_from_erp_dh",
    dag=dag,
    provide_context=True,
    retries=3,
    retry_delay=timedelta(seconds=3),
)
