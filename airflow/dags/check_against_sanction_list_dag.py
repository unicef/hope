from datetime import datetime, timedelta
from airflow import DAG

from operators.check_against_sanction_list_operator import (
    CheckAgainstSanctionListOperator,
)

dag = DAG(
    "CheckAgainstSanctionList",
    description="Check uploaded xlsx file against Sanction List",
    schedule_interval=None,
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = CheckAgainstSanctionListOperator(
    task_id="check_against_sanction_list",
    dag=dag,
    provide_context=True,
    retries=0,
    retry_delay=timedelta(seconds=3),
)
