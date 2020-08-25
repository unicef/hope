from datetime import datetime, timedelta
from airflow import DAG
from operators.get_rapidpro_verification_operator import (
    GetRapidProVerificationsOperator
)


dag = DAG(
    "PullFromCaDh",
    description="Get results from RAPIDPRO API and verify existing verifications",
    schedule_interval="@hourly",
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = GetRapidProVerificationsOperator(
    task_id="get_rapidpro_verification",
    dag=dag,
    provide_context=True,
    retries=3,
    retry_delay=timedelta(seconds=3),
)
