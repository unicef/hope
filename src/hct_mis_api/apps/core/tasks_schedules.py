from celery.schedules import crontab

TASKS_SCHEDULES = {
    "sync_sanction_list": {
        "task": "hct_mis_api.apps.sanction_list.celery_tasks.sync_sanction_list_task",
        "schedule": crontab(minute=0, hour=0),
    },
    "get_sync_run_rapid_pro": {
        "task": "hct_mis_api.apps.payment.celery_tasks.get_sync_run_rapid_pro_task",
        "schedule": crontab(minute="*/20"),
    },
    "periodic_grievances_notifications": {
        "task": "hct_mis_api.apps.grievance.celery_tasks.periodic_grievances_notifications",
        "schedule": crontab(minute="*/20"),
    },
    # "recalculate_population_fields_task": {
    #     "task": "hct_mis_api.apps.household.celery_tasks.interval_recalculate_population_fields_task",
    #     "schedule": crontab(hour="*/24"),
    # },
    "extract_records_task": {
        "task": "hct_mis_api.contrib.aurora.celery_tasks.extract_records_task",
        "schedule": crontab(hour="*/24"),
    },
    "remove_old_cash_plan_payment_verification_xls": {
        "task": "hct_mis_api.apps.payment.celery_tasks.remove_old_cash_plan_payment_verification_xls",
        "schedule": crontab(hour="*/24"),
    },
    "check_rdi_import_periodic_task": {
        "task": "hct_mis_api.apps.registration_datahub.celery_tasks.check_rdi_import_periodic_task",
        "schedule": crontab(minute="*/15"),
    },
    "clean_old_record_files_task": {
        "task": "hct_mis_api.contrib.aurora.celery_tasks.clean_old_record_files_task",
        "schedule": crontab(month_of_year="2-12/2"),
    },
    "periodic_sync_payment_gateway_fsp": {
        "task": "hct_mis_api.apps.payment.celery_tasks.periodic_sync_payment_gateway_fsp",
        "schedule": crontab(minute="*/30"),
    },
    "periodic_sync_payment_gateway_account_types": {
        "task": "hct_mis_api.apps.payment.celery_tasks.periodic_sync_payment_gateway_account_types",
        "schedule": crontab(minute="*/30"),
    },
    "periodic_sync_payment_gateway_records": {
        "task": "hct_mis_api.apps.payment.celery_tasks.periodic_sync_payment_gateway_records",
        "schedule": crontab(minute="*/30"),
    },
    "periodic_sync_payment_gateway_delivery_mechanisms": {
        "task": "hct_mis_api.apps.payment.celery_tasks.periodic_sync_payment_gateway_delivery_mechanisms",
        "schedule": crontab(minute="*/30"),
    },
    "remove_old_pdu_template_files_task": {
        "task": "hct_mis_api.apps.periodic_data_update.celery_tasks.remove_old_pdu_template_files_task",
        "schedule": crontab(hour="*/24"),
    },
    "update_dashboard_figures_task": {
        "task": "hct_mis_api.apps.dashboard.celery_tasks.update_dashboard_figures",
        "schedule": crontab(hour="*/24"),
    },
}
