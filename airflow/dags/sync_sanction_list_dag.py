from datetime import datetime, timedelta

from airflow import DAG
from operators.sync_sanction_list_operator import (
    SyncSanctionListOperator,
)

dag = DAG(
    "SyncSanctionList",
    description="Sync Sanction List Daily",
    schedule_interval="@daily",
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = SyncSanctionListOperator(
    task_id="sync_sanction_list",
    dag=dag,
    provide_context=True,
    retries=0,
    retry_delay=timedelta(seconds=3),
)
