import logging
import datetime

from django.contrib.auth import get_user_model

from hct_mis_api.apps.payment.models import XlsxCashPlanPaymentVerificationFile, CashPlanPaymentVerification
from hct_mis_api.apps.payment.xlsx.XlsxVerificationExportService import XlsxVerificationExportService
from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
def get_sync_run_rapid_pro_task():
    try:
        from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
            CheckRapidProVerificationTask,
        )

        CheckRapidProVerificationTask().execute()
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
def create_cash_plan_payment_verification_xls(cash_plan_payment_verification_id, user_id):
    try:
        user = get_user_model().objects.get(pk=user_id)
        cash_plan_payment_verification = CashPlanPaymentVerification.objects.get(id=cash_plan_payment_verification_id)
        service = XlsxVerificationExportService(cash_plan_payment_verification)
        # if no file will start creating it
        if not getattr(cash_plan_payment_verification, 'xlsx_cashplan_payment_verification_file', None):
            service.save_xlsx_file(user)

        cash_plan_payment_verification.xlsx_file_exporting = False
        cash_plan_payment_verification.save()
        service.send_email(user, cash_plan_payment_verification_id)
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
def remove_old_cash_plan_payment_verification_xls(past_days=30):
    """Remove old Payment Verification report XLSX files"""
    try:
        days = datetime.datetime.now() - datetime.timedelta(days=past_days)
        files_qs = XlsxCashPlanPaymentVerificationFile.objects.filter(created_at__lte=days)
        if files_qs:
            inf = files_qs.delete()
            logger.info(f"Removed old XlsxCashPlanPaymentVerificationFile: {inf}")

    except Exception as e:
        logger.exception(e)
        raise
