from celery.schedules import crontab

TASKS_SCHEDULES = {
    "debug_task": {
        "task": "hct_mis_api.apps.core.celery_tasks.debug_task",
        "schedule": crontab(),
    },
}
