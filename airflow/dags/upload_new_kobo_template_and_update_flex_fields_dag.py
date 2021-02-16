from datetime import datetime, timedelta
from airflow import DAG

from operators.upload_new_kobo_template_and_update_flex_fields_operator import (
    UploadNewKoboTemplateAndUpdateFlexFieldsOperator
)

dag = DAG(
    "UploadNewKoboTemplateAndUpdateFlexFields",
    description="Upload new KoBo template and update Flex Fields",
    schedule_interval=None,
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = UploadNewKoboTemplateAndUpdateFlexFieldsOperator(
    task_id="upload_new_kobo_template_and_update_flex_fields",
    dag=dag,
    provide_context=True,
    retries=0,
    retry_delay=timedelta(seconds=3),
)
