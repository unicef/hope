from datetime import datetime, timedelta
from airflow import DAG
from operators.registration_xlsx_import_operator_hourly import (
    RegistrationXLSXImportHourlyOperator
)


dag = DAG(
    "CreateFromNotStartedRegistrationDataImportXLSX",
    description="Create Registration Data Import from xlsx file",
    schedule_interval='@hourly',
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = RegistrationXLSXImportHourlyOperator(
    task_id="create_not_started_registration_data_import_from_xlsx",
    dag=dag,
    provide_context=True,
    retries=0,
    retry_delay=timedelta(seconds=3),
)
