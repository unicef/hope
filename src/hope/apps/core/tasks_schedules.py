from celery.schedules import crontab

PERIODIC_QUEUE = "periodic"

TASKS_SCHEDULES = {
    "sync_sanction_list": {
        "task": "hope.apps.sanction_list.celery_tasks.sync_sanction_list_task",
        "schedule": crontab(minute=0, hour=0),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "get_sync_run_rapid_pro": {
        "task": "hope.apps.payment.celery_tasks.get_sync_run_rapid_pro_task",
        "schedule": crontab(minute="*/20"),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "periodic_grievances_notifications": {
        "task": "hope.apps.grievance.celery_tasks.periodic_grievances_notifications",
        "schedule": crontab(minute="*/20"),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "extract_records_task": {
        "task": "hope.contrib.aurora.celery_tasks.extract_records_task",
        "schedule": crontab(minute=0, hour=0),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "remove_old_cash_plan_payment_verification_xls": {
        "task": "hope.apps.payment.celery_tasks.remove_old_cash_plan_payment_verification_xls",
        "schedule": crontab(minute=0, hour=0),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "check_rdi_import_periodic_task": {
        "task": "hope.apps.registration_data.celery_tasks.check_rdi_import_periodic_task",
        "schedule": crontab(minute="*/15"),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "clean_old_record_files_task": {
        "task": "hope.contrib.aurora.celery_tasks.clean_old_record_files_task",
        "schedule": crontab(minute=0, hour=0, day_of_month=1, month_of_year="2-12/2"),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "periodic_sync_payment_gateway_fsp": {
        "task": "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_fsp",
        "schedule": crontab(minute="*/30"),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "periodic_sync_payment_gateway_account_types": {
        "task": "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_account_types",
        "schedule": crontab(minute="*/30"),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "periodic_sync_payment_gateway_records": {
        "task": "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_records",
        "schedule": crontab(minute="*/30"),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "periodic_sync_payment_gateway_delivery_mechanisms": {
        "task": "hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_delivery_mechanisms",
        "schedule": crontab(minute="*/30"),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "remove_old_pdu_template_files_task": {
        "task": "hope.apps.periodic_data_update.celery_tasks.remove_old_pdu_template_files_task",
        "schedule": crontab(minute=0, hour=0),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "update_dashboard_figures_task": {
        "task": "hope.apps.dashboard.celery_tasks.update_dashboard_figures",
        "schedule": crontab(minute=0, hour=23),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "invalidate_permissions_cache_for_user_if_expired_role": {
        "task": "hope.apps.account.celery_tasks.invalidate_permissions_cache_for_user_if_expired_role",
        "schedule": crontab(minute=0, hour=0),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "periodic_sync_payment_plan_invoices_western_union_ftp": {
        "task": "hope.apps.payment.celery_tasks.periodic_sync_payment_plan_invoices_western_union_ftp",
        "schedule": crontab(minute=0, hour=0),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "periodic_send_payment_plan_reconciliation_overdue_emails": {
        "task": "hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails",
        "schedule": crontab(minute=0, hour=0),
        "options": {"queue": PERIODIC_QUEUE},
    },
    "cleanup_inactive_program_indexes_task": {
        "task": "hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_task",
        "schedule": crontab(minute=0, hour=1),
        "options": {"queue": PERIODIC_QUEUE},
    },
}
