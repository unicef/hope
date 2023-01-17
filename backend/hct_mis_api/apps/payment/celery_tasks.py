import datetime
import logging
from typing import Dict

from django.contrib.auth import get_user_model

from sentry_sdk import configure_scope

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    XlsxCashPlanPaymentVerificationFile,
)
from hct_mis_api.apps.payment.xlsx.XlsxVerificationExportService import (
    XlsxVerificationExportService,
)
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
@sentry_tags
def get_sync_run_rapid_pro_task() -> None:
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
@sentry_tags
def create_cash_plan_payment_verification_xls(cash_plan_payment_verification_id: str, user_id: str) -> None:
    try:
        user = get_user_model().objects.get(pk=user_id)
        cash_plan_payment_verification = CashPlanPaymentVerification.objects.get(id=cash_plan_payment_verification_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", cash_plan_payment_verification.business_area)

            service = XlsxVerificationExportService(cash_plan_payment_verification)
            # if no file will start creating it
            if not getattr(cash_plan_payment_verification, "xlsx_cashplan_payment_verification_file", None):
                service.save_xlsx_file(user)

            cash_plan_payment_verification.xlsx_file_exporting = False
            cash_plan_payment_verification.save()
            service.send_email(user, cash_plan_payment_verification_id)
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def remove_old_cash_plan_payment_verification_xls(past_days: int = 30) -> None:
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


@app.task
@log_start_and_end
@sentry_tags
def create_cash_plan_reconciliation_xlsx(
    reconciliation_xlsx_file_id: str,
    column_mapping: Dict,
    cash_plan_form_data: Dict,
    currency: str,
    delivery_type: str,
    delivery_date: str,
    program_id: str,
    service_provider_id: str,
) -> None:
    try:
        from hct_mis_api.apps.core.models import StorageFile
        from hct_mis_api.apps.payment.models import ServiceProvider
        from hct_mis_api.apps.payment.services.create_cash_plan_from_reconciliation import (
            CreateCashPlanReconciliationService,
        )
        from hct_mis_api.apps.program.models import Program

        reconciliation_xlsx_obj = StorageFile.objects.get(id=reconciliation_xlsx_file_id)
        business_area = reconciliation_xlsx_obj.business_area

        with configure_scope() as scope:
            scope.set_tag("business_area", business_area)

            cash_plan_form_data["program"] = Program.objects.get(id=program_id)
            cash_plan_form_data["service_provider"] = ServiceProvider.objects.get(id=service_provider_id)

            service = CreateCashPlanReconciliationService(
                business_area,
                reconciliation_xlsx_obj.file,
                column_mapping,
                cash_plan_form_data,
                currency,
                delivery_type,
                delivery_date,
            )

            try:
                service.parse_xlsx()
                error_msg = None
            except Exception as e:
                error_msg = f"Error parse xlsx: {e} \nFile name: {reconciliation_xlsx_obj.file_name}"

            service.send_email(reconciliation_xlsx_obj.created_by, reconciliation_xlsx_obj.file_name, error_msg)
            # remove file every time
            reconciliation_xlsx_obj.file.delete()
            reconciliation_xlsx_obj.delete()

    except Exception as e:
        logger.exception(e)
        raise
