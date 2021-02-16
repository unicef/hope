from hct_mis_api.apps.core.celery import app


@app.task
def sync_sanction_list_task():
    from hct_mis_api.apps.sanction_list.tasks.load_xml import LoadSanctionListXMLTask

    LoadSanctionListXMLTask().execute()


@app.task
def check_against_sanction_list_task(uploaded_file_id, original_file_name):
    from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list import (
        CheckAgainstSanctionListTask,
    )

    CheckAgainstSanctionListTask().execute(
        uploaded_file_id=uploaded_file_id,
        original_file_name=original_file_name,
    )

