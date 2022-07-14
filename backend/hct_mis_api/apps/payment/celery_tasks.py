import logging

from hct_mis_api.apps.core.celery import app

logger = logging.getLogger(__name__)


@app.task
def get_sync_run_rapid_pro_task():
    logger.info(f"get_sync_run_rapid_pro_task start")

    try:
        from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
            CheckRapidProVerificationTask,
        )

        CheckRapidProVerificationTask().execute()
    except Exception as e:
        logger.exception(e)
        raise

    logger.info(f"get_sync_run_rapid_pro_task end")


@app.task
def fsp_generate_xlsx_report_task(fsp_id):
    logger.info("fsp_generate_xlsx_report_task start")

    try:
        from hct_mis_api.apps.payment.services.generate_fsp_xlsx_service import (
            GenerateReportService,
        )
        from hct_mis_api.apps.payment.models import FinancialServiceProvider

        fsp = FinancialServiceProvider.objects.get(id=fsp_id)
        service = GenerateReportService(fsp=fsp)
        service.generate_report()
    except Exception as e:
        logger.exception(e)

    logger.info("fsp_generate_xlsx_report_task end")
