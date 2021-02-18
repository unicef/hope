from datetime import datetime, timedelta
from airflow import DAG
from operators.dashboard_report_export_operator import (
    DashboardReportExportOperator,
)


dag = DAG(
    "DashboardReportExport",
    description="Generate dashboard report file",
    schedule_interval=None,
    start_date=datetime.now() - timedelta(days=1),
)

django_operator = DashboardReportExportOperator(
    task_id="dashboard_report_export",
    dag=dag,
    provide_context=True,
    retries=0,
    retry_delay=timedelta(seconds=3),
)
