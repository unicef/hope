from datetime import datetime, timedelta
from airflow import DAG
from operators.registration_kobo_import_operator import (
    RegistrationKoboImportOperator
)


dag = DAG(
    "CreateRegistrationDataImportKobo",
    description="Create Registration Data Import from Kobo project",
    schedule_interval=None,
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = RegistrationKoboImportOperator(
    task_id="create_registration_data_import_from_kobo",
    dag=dag,
    provide_context=True,
    retries=0,
    retry_delay=timedelta(seconds=3),
)
