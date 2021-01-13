from datetime import datetime, timedelta
from airflow import DAG

from operators.deduplicate_and_check_against_sanctions_list_operator import (
    DeduplicateAndCheckAgainstSanctionsListOperator,
)

dag = DAG(
    "DeduplicateAndCheckAgainstSanctionsList",
    description="Deduplicate selected individuals and check them against sanctions list",
    schedule_interval=None,
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = DeduplicateAndCheckAgainstSanctionsListOperator(
    task_id="deduplicate_and_check_against_sanctions_list",
    dag=dag,
    provide_context=True,
    retries=0,
    retry_delay=timedelta(seconds=3),
)
