from hct_mis_api.apps.core.celery import app


@app.task
def get_sync_run_rapid_pro_task():
    from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import CheckRapidProVerificationTask

    CheckRapidProVerificationTask().execute()
