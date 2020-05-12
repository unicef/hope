from datetime import datetime, timedelta
from airflow import DAG
from operators.merge_registration_import_data import (
    MergeRegistrationImportDataOperator
)


dag = DAG(
    "MergeRegistrationImportData",
    description="Merge Registration Import Data",
    schedule_interval=None,
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = MergeRegistrationImportDataOperator(
    task_id="merge_registration_import_data",
    dag=dag,
    provide_context=True,
    retries=3,
    retry_delay=timedelta(seconds=3),
)
