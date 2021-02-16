from datetime import datetime, timedelta
from airflow import DAG
from operators.rdi_deduplication_operator import RDIDeduplicationOperator


dag = DAG(
    "RegistrationDataImportDeduplication",
    description="Run deduplication for registration data import",
    schedule_interval=None,
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = RDIDeduplicationOperator(
    task_id="registration_data_import_deduplication",
    dag=dag,
    provide_context=True,
    retries=0,
    retry_delay=timedelta(seconds=3),
)
