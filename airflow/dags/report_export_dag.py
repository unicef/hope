from datetime import datetime, timedelta
from airflow import DAG
from operators.report_export_operator import ReportExportOperator


dag = DAG(
    "ReportExport",
    description="Generate report file",
    schedule_interval=None,
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = ReportExportOperator(
    task_id="report_export",
    dag=dag,
    provide_context=True,
    retries=0,
    retry_delay=timedelta(seconds=3),
)
