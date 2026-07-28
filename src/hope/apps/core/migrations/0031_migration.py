from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

# Task paths retired by the celery refactor (#5815). Beat raises
# KeyError on every tick for a PeriodicTask row still pointing at one of these.
RETIRED_TASK_PATHS = frozenset(
    {
        "hope.apps.account.celery_tasks.invalidate_permissions_cache_for_user_if_expired_role",
        "hope.apps.dashboard.celery_tasks.update_dashboard_figures_async_task",
        "hope.apps.grievance.celery_tasks.periodic_grievances_notifications",
        "hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_task",
        "hope.apps.household.celery_tasks.interval_recalculate_population_fields_task",
        "hope.apps.household.celery_tasks.recalculate_population_fields_task",
        "hope.apps.payment.celery_tasks.get_sync_run_rapid_pro_task",
        "hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails",
        "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_account_types",
        "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_delivery_mechanisms",
        "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_fsp",
        "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_records",
        "hope.apps.payment.celery_tasks.periodic_sync_payment_plan_invoices_western_union_ftp",
        "hope.apps.payment.celery_tasks.remove_old_cash_plan_payment_verification_xls",
        "hope.apps.periodic_data_update.celery_tasks.remove_old_pdu_template_files_task",
        "hope.apps.registration_data.celery_tasks.check_rdi_import_periodic_task",
        "hope.apps.sanction_list.celery_tasks.sync_sanction_list_task",
        "hope.contrib.aurora.celery_tasks.extract_records_task",
        "hope.contrib.aurora.celery_tasks.clean_old_record_files_task",
    }
)

# Two live rows a DB row already occupied by name, so beat's get_or_create
# never overwrote their stale task. Repointed, not deleted, to keep history.
REPOINTS = {
    "cleanup_inactive_program_indexes_task": (
        "hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_async_task"
    ),
    "update_dashboard_figures_async_task": "hope.apps.dashboard.celery_tasks.update_dashboard_figures",
}

# Rows whose task still resolves, so they raise no KeyError, but that duplicate a
# live row and fire it a second time.
RETIRED_DUPLICATES = (("update_dashboard_figures_task", "hope.apps.dashboard.celery_tasks.update_dashboard_figures"),)


def repoint_and_drop_stale_periodic_tasks(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    # Repoint before the delete: it moves these live rows off their retired task
    # so the blocklist delete skips them, keeping their history and PK.
    for name, task in REPOINTS.items():
        PeriodicTask.objects.filter(name=name).exclude(task=task).update(task=task)

    PeriodicTask.objects.filter(task__in=RETIRED_TASK_PATHS).delete()

    for name, task in RETIRED_DUPLICATES:
        PeriodicTask.objects.filter(name=name, task=task).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0030_migration"),
        ("django_celery_beat", "0019_alter_periodictasks_options"),
    ]

    operations = [
        migrations.RunPython(repoint_and_drop_stale_periodic_tasks, migrations.RunPython.noop),
    ]
