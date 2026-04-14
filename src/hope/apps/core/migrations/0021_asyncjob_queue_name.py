from django.conf import settings
from django.db import migrations, models

PERIODIC_QUEUE = "periodic"
PERIODIC_JOB_NAMES = [
    "sync_sanction_list_async_task",
    "get_sync_run_rapid_pro_async_task",
    "periodic_grievances_notifications_async_task",
    "remove_old_cash_plan_payment_verification_xlsx_async_task",
    "periodic_sync_payment_gateway_fsp_async_task",
    "periodic_sync_payment_gateway_account_types_async_task",
    "periodic_sync_payment_gateway_records_async_task",
    "periodic_sync_payment_gateway_delivery_mechanisms_async_task",
    "remove_old_pdu_template_files_async_task",
    "invalidate_permissions_cache_for_user_if_expired_role_async_task",
    "periodic_sync_payment_plan_invoices_western_union_ftp_async_task",
    "periodic_send_payment_plan_reconciliation_overdue_emails_async_task",
    "cleanup_indexes_in_inactive_programs_async_task",
    "interval_recalculate_population_fields_async_task",
]


def mark_periodic_async_jobs(apps, schema_editor):
    AsyncJob = apps.get_model("core", "AsyncJob")
    AsyncJob.objects.filter(job_name__in=PERIODIC_JOB_NAMES).update(queue_name=PERIODIC_QUEUE)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0020_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="asyncjob",
            name="queue_name",
            field=models.CharField(
                db_index=True,
                default=settings.CELERY_TASK_DEFAULT_QUEUE,
                max_length=255,
            ),
        ),
        migrations.RunPython(mark_periodic_async_jobs, migrations.RunPython.noop),
    ]
