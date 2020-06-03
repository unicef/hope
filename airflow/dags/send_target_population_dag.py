from datetime import datetime, timedelta
from airflow import DAG
from operators.send_target_population import (
    SendTargetPopulationOperator
)


dag = DAG(
    "SendTargetPopulation",
    description="Send target population data to datahub",
    schedule_interval=None,
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = SendTargetPopulationOperator(
    task_id="send_target_population",
    dag=dag,
    provide_context=True,
    retries=3,
    retry_delay=timedelta(seconds=3),
)
