from hct_mis_api.apps.core.celery import app


@app.task
def send_target_population_task():
    from hct_mis_api.apps.mis_datahub.tasks.send_tp_to_datahub import SendTPToDatahubTask

    SendTPToDatahubTask().execute()
