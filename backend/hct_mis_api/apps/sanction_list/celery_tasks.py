import logging

from hct_mis_api.config.celery import app

logger = logging.getLogger(__name__)


@app.task
def sync_sanction_list_task():
    logger.info("sync_sanction_list_task start")

    try:
        from hct_mis_api.apps.sanction_list.tasks.load_xml import LoadSanctionListXMLTask

        LoadSanctionListXMLTask().execute()
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("sync_sanction_list_task end")


@app.task
def check_against_sanction_list_task(uploaded_file_id, original_file_name):
    logger.info("check_against_sanction_list_task start")

    try:
        from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list import CheckAgainstSanctionListTask

        CheckAgainstSanctionListTask().execute(
            uploaded_file_id=uploaded_file_id,
            original_file_name=original_file_name,
        )
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("check_against_sanction_list_task end")
