from hct_mis_api.apps.core.celery import app


@app.task
def pull_from_erp_datahub_task():
    from hct_mis_api.apps.erp_datahub.tasks.pull_from_erp_datahub import (
        PullFromErpDatahubTask,
    )

    PullFromErpDatahubTask().execute()
