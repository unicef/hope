from datetime import datetime, timedelta
from airflow import DAG
from operators.test_connection import TestConnectionOperator


dag = DAG(
    "Test_Connection",
    description="Test Django connections",
    schedule_interval=timedelta(days=1),
    start_date=datetime.now() - timedelta(days=1),

)

django_operator = TestConnectionOperator(
    task_id="django_orm_connect",
    dag=dag,
)
