from celery.schedules import crontab

TASKS_SCHEDULES = {
    "sync_sanction_list": {
        "task": "hct_mis_api.apps.sanction_list.celery_tasks.sync_sanction_list_task",
        "schedule": crontab(minute=0, hour=0),
    },
    "pull_from_cashassist_datahub_task": {
        "task": "hct_mis_api.apps.cash_assist_datahub.celery_tasks.pull_from_cashassist_datahub_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "fix_exchange_rates_task": {
        "task": "hct_mis_api.apps.cash_assist_datahub.celery_tasks.fix_exchange_rates_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "get_sync_run_rapid_pro": {
        "task": "hct_mis_api.apps.payment.celery_tasks.get_sync_run_rapid_pro_task",
        "schedule": crontab(minute="*/20"),
    },
    "periodic_grievances_notifications": {
        "task": "hct_mis_api.apps.grievance.celery_tasks.periodic_grievances_notifications",
        "schedule": crontab(minute="*/20"),
    },
    "sync_to_mis_datahub": {
        "task": "hct_mis_api.apps.erp_datahub.celery_tasks.sync_to_mis_datahub_task",
        "schedule": crontab(minute="*/20"),
    },
    "recalculate_population_fields_task": {
        "task": "hct_mis_api.apps.household.celery_tasks.recalculate_population_fields_task",
        "schedule": crontab(hour="*/24"),
    },
    "extract_records_task": {
        "task": "hct_mis_api.apps.registration_datahub.celery_tasks.extract_records_task",
        "schedule": crontab(hour="*/24"),
    },
    "remove_old_cash_plan_payment_verification_xls": {
        "task": "hct_mis_api.apps.payment.celery_tasks.remove_old_cash_plan_payment_verification_xls",
        "schedule": crontab(hour="*/24"),
    },
}
