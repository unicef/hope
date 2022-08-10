import logging
import datetime

from concurrency.api import disable_concurrency
from django.db.transaction import atomic
from django.utils import timezone
from sentry_sdk import configure_scope

from django.contrib.auth import get_user_model

from hct_mis_api.apps.payment.models import XlsxCashPlanPaymentVerificationFile, CashPlanPaymentVerification
from hct_mis_api.apps.payment.xlsx.XlsxVerificationExportService import XlsxVerificationExportService
from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
@sentry_tags
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
def fsp_generate_xlsx_report_task(fsp_id):
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
        raise


@app.task
@log_start_and_end
@sentry_tags
def create_cash_plan_payment_verification_xls(cash_plan_payment_verification_id, user_id):
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
            service.send_email(service.get_context(user))
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
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


@app.task
@log_start_and_end
@sentry_tags
def create_payment_plan_payment_list_xlsx(payment_plan_id, user_id):
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportService import XlsxPaymentPlanExportService

        user = get_user_model().objects.get(pk=user_id)
        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", payment_plan.business_area)

            if not payment_plan.has_payment_plan_payment_list_xlsx_file:
                service = XlsxPaymentPlanExportService(payment_plan)
                service.save_xlsx_file(user)

            payment_plan.status_lock()
            payment_plan.save()

            service.send_email(service.get_context(user))

    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def payment_plan_apply_steficon(payment_plan_id):
    from hct_mis_api.apps.steficon.models import RuleCommit
    from hct_mis_api.apps.payment.models import PaymentPlan, Payment

    try:
        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        with configure_scope() as scope:
            scope.set_tag("business_area", payment_plan.business_area)

            rule: RuleCommit = payment_plan.steficon_rule
            if not rule:
                raise Exception("PaymentPlan does not have a Steficon rule")
    except Exception as e:
        logger.exception(e)
        raise
    try:
        payment_plan.status = PaymentPlan.Status.STEFICON_RUN
        payment_plan.steficon_applied_date = timezone.now()
        payment_plan.save()
        updates = []
        with atomic():
            entry: Payment
            for entry in payment_plan.payments.all_active_payments:
                pass
                # TODO: not sure how will work steficon function
                # result = rule.execute({"household": entry.household, "payment_plan": payment_plan})
                # entry.entitlement_quantity = result.entitlement_quantity
                # updates.append(entry)
            Payment.objects.bulk_update(updates, ["entitlement_quantity", "entitlement_quantity_usd"])
        payment_plan.status = PaymentPlan.Status.STEFICON_COMPLETED
        payment_plan.steficon_applied_date = timezone.now()
        with disable_concurrency(payment_plan):
            payment_plan.save()
    except Exception as e:
        logger.exception(e)
        payment_plan.steficon_applied_date = timezone.now()
        payment_plan.status = PaymentPlan.Status.STEFICON_ERROR
        payment_plan.save()
        raise
