from celery.schedules import crontab

from hope.apps.core.celery_queues import CELERY_QUEUE_PERIODIC


def periodic_queue_options() -> dict[str, str]:
    return {"queue": CELERY_QUEUE_PERIODIC}


TASKS_SCHEDULES = {
    "sync_sanction_list_async_task": {
        "task": "hope.apps.sanction_list.celery_tasks.sync_sanction_list_async_task",
        "schedule": crontab(minute=0, hour=0),
        "options": periodic_queue_options(),
    },
    "get_sync_run_rapid_pro_async_task": {
        "task": "hope.apps.payment.celery_tasks.get_sync_run_rapid_pro_async_task",
        "schedule": crontab(minute="*/20"),
        "options": periodic_queue_options(),
    },
    "periodic_grievances_notifications_async_task": {
        "task": "hope.apps.grievance.celery_tasks.periodic_grievances_notifications_async_task",
        "schedule": crontab(minute="*/20"),
        "options": periodic_queue_options(),
    },
    "extract_records_async_task": {
        "task": "hope.contrib.aurora.celery_tasks.extract_records_async_task",
        "schedule": crontab(minute=0, hour=0),
        "options": periodic_queue_options(),
    },
    "remove_old_cash_plan_payment_verification_xlsx_async_task": {
        "task": "hope.apps.payment.celery_tasks.remove_old_cash_plan_payment_verification_xlsx_async_task",
        "schedule": crontab(minute=0, hour=0),
        "options": periodic_queue_options(),
    },
    "clean_old_record_files_async_task": {
        "task": "hope.contrib.aurora.celery_tasks.clean_old_record_files_async_task",
        "schedule": crontab(minute=0, hour=0, day_of_month=1, month_of_year="2-12/2"),
        "options": periodic_queue_options(),
    },
    "periodic_sync_payment_gateway_fsp_async_task": {
        "task": "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_fsp_async_task",
        "schedule": crontab(minute="*/30"),
        "options": periodic_queue_options(),
    },
    "periodic_sync_payment_gateway_account_types_async_task": {
        "task": "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_account_types_async_task",
        "schedule": crontab(minute="*/30"),
        "options": periodic_queue_options(),
    },
    "periodic_sync_payment_gateway_records_async_task": {
        "task": "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_records_async_task",
        "schedule": crontab(minute="*/30"),
        "options": periodic_queue_options(),
    },
    "periodic_sync_payment_gateway_delivery_mechanisms_async_task": {
        "task": "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_delivery_mechanisms_async_task",
        "schedule": crontab(minute="*/30"),
        "options": periodic_queue_options(),
    },
    "remove_old_pdu_template_files_async_task": {
        "task": "hope.apps.periodic_data_update.celery_tasks.remove_old_pdu_template_files_async_task",
        "schedule": crontab(minute=0, hour=0),
        "options": periodic_queue_options(),
    },
    "update_dashboard_figures_async_task": {
        "task": "hope.apps.dashboard.celery_tasks.update_dashboard_figures",
        "schedule": crontab(minute=0, hour=23),
        "options": periodic_queue_options(),
    },
    "invalidate_permissions_cache_for_user_if_expired_role_async_task": {
        "task": "hope.apps.account.celery_tasks.invalidate_permissions_cache_for_user_if_expired_role_async_task",
        "schedule": crontab(minute=0, hour=0),
        "options": periodic_queue_options(),
    },
    "periodic_sync_payment_plan_invoices_western_union_ftp_async_task": {
        "task": "hope.apps.payment.celery_tasks.periodic_sync_payment_plan_invoices_western_union_ftp_async_task",
        "schedule": crontab(minute=0, hour=0),
        "options": periodic_queue_options(),
    },
    "periodic_send_payment_plan_reconciliation_overdue_emails_async_task": {
        "task": "hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task",
        "schedule": crontab(minute=0, hour=0),
        "options": periodic_queue_options(),
    },
    "cleanup_inactive_program_indexes_task": {
        "task": "hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_async_task",
        "schedule": crontab(minute=0, hour=1),
        "options": periodic_queue_options(),
    },
    "recover_missing_async_jobs_async_task": {
        "task": "hope.apps.core.celery_tasks.recover_missing_async_jobs_async_task",
        "schedule": crontab(minute="*/10"),
        "options": periodic_queue_options(),
    },
    "cleanup_old_periodic_async_jobs_async_task": {
        "task": "hope.apps.core.celery_tasks.cleanup_old_periodic_async_jobs_async_task",
        "schedule": crontab(minute=0, hour=2),
        "options": periodic_queue_options(),
    },
    "interval_recalculate_population_fields_async_task": {
        "task": "hope.apps.household.celery_tasks.interval_recalculate_population_fields_async_task",
        "schedule": crontab(minute=0, hour=0),
        "options": periodic_queue_options(),
    },
}
