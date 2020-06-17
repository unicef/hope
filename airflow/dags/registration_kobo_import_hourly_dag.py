from datetime import datetime, timedelta
from airflow import DAG
from operators.registration_kobo_import_operator_hourly import (
    RegistrationKoboImportHourlyOperator
)


dag = DAG(
    "CreateFromNotStartedRegistrationDataImportKobo",
    description="Create Registration Data Import from Kobo project",
    schedule_interval="@hourly",
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = RegistrationKoboImportHourlyOperator(
    task_id="create_not_started_registration_data_import_from_kobo",
    dag=dag,
    provide_context=True,
    retries=0,
    retry_delay=timedelta(seconds=3),
)
