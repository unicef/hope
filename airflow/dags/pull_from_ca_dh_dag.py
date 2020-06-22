from datetime import datetime, timedelta
from airflow import DAG
from operators.pull_from_ca_dh_operator import (
    PullFromCaDh
)


dag = DAG(
    "PullFromCaDh",
    description="Pull data from cash assist datahub schema",
    schedule_interval="@hourly",
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = PullFromCaDh(
    task_id="pull_from_ca_dh",
    dag=dag,
    provide_context=True,
    retries=3,
    retry_delay=timedelta(seconds=3),
)
