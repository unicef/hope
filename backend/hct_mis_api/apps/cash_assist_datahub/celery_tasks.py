from hct_mis_api.apps.core.celery import app


@app.task
def pull_from_erp_dh_task():
    from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import PullFromDatahubTask

    PullFromDatahubTask().execute()
