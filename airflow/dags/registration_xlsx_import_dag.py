from datetime import datetime, timedelta
from airflow import DAG
from operators.registration_xlsx_import_operator import (
    RegistrationXLSXImportOperator
)


dag = DAG(
    "CreateRegistrationDataImportXLSX",
    description="Create Registration Data Import from xlsx file",
    schedule_interval=None,
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = RegistrationXLSXImportOperator(
    task_id="create_registration_data_import_from_xlsx",
    dag=dag,
    provide_context=True,
    retries=3,
    retry_delay=timedelta(seconds=3),
)
