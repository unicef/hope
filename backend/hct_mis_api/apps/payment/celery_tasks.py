import logging
import datetime
import traceback
import django_fsm

from concurrency.api import disable_concurrency
from django.contrib.admin.options import get_content_type_for_model
from django.db.transaction import atomic
from django.utils import timezone
from sentry_sdk import configure_scope

from django.contrib.auth import get_user_model

from hct_mis_api.apps.payment.models import XlsxCashPlanPaymentVerificationFile, CashPlanPaymentVerification
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanPerFspImportService import XlsxPaymentPlanImportPerFspService
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
            for obj in files_qs:
                obj.file.delete(save=False)
                obj.delete()

            logger.info(f"Removed old XlsxCashPlanPaymentVerificationFile: {files_qs.count()}")

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

            # regenerate always xlsx
            service = XlsxPaymentPlanExportService(payment_plan)
            service.save_xlsx_file(user)
            try:
                payment_plan.status_lock()
            except django_fsm.TransitionNotAllowed:
                pass  # for now this can be ignored
            payment_plan.save()

            service.send_email(service.get_context(user))

    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def create_payment_plan_payment_list_xlsx_per_fsp(payment_plan_id, user_id):
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportService import XlsxPaymentPlanExportService

        user = get_user_model().objects.get(pk=user_id)
        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", payment_plan.business_area)

            # regenerate always xlsx
            service = XlsxPaymentPlanExportService(payment_plan)
            service.export_per_fsp(user)
            payment_plan.status_date = timezone.now()
            payment_plan.status = PaymentPlan.Status.ACCEPTED
            payment_plan.save()

            service.send_email(service.get_context(user, per_fsp=True))

    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def import_payment_plan_payment_list_from_xlsx(payment_plan_id, file_id):
    try:
        from hct_mis_api.apps.core.models import FileTemp
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanImportService import XlsxPaymentPlanImportService

        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", payment_plan.business_area)

            try:
                file = FileTemp.objects.get(pk=file_id).file
            except FileTemp.DoesNotExist as e:
                logger.exception(f"Error import from xlsx, FileTemp object with ID {file_id} not found.", e)
                raise

            service = XlsxPaymentPlanImportService(payment_plan, file)
            service.open_workbook()
            try:
                with atomic():
                    service.import_payment_list()
                    payment_plan.xlsx_file_imported_date = timezone.now()
                    payment_plan.status_lock()
                    payment_plan.save()
                    payment_plan.update_money_fields()
            except Exception as e:
                logger.exception("Error import from xlsx", e)
                payment_plan.status_lock()
                payment_plan.save()
                payment_plan.update_money_fields()

    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def import_payment_plan_payment_list_per_fsp_from_xlsx(payment_plan_id, user_id, file):
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan

        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", payment_plan.business_area)

            service = XlsxPaymentPlanImportPerFspService(payment_plan, file)
            service.open_workbook()
            try:
                with atomic():
                    service.import_payment_list()
                    payment_plan.xlsx_file_imported_date = timezone.now()
                    # payment_plan.status_approved() # TODO
                    payment_plan.save()
            except Exception as e:
                print(e)
                traceback.print_exc()
                logger.exception("Error import from xlsx", e)
                # payment_plan.status_approved() # TODO
                payment_plan.save()

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
            for entry in payment_plan.all_active_payments:
                # TODO: not sure how will work steficon function payment_plan or payment need ??
                result = rule.execute({"household": entry.household, "payment_plan": payment_plan})
                entry.entitlement_quantity = result.value
                entry.entitlement_date = timezone.now()
                updates.append(entry)
            Payment.objects.bulk_update(updates, ["entitlement_quantity", "entitlement_date"])
        payment_plan.steficon_applied_date = timezone.now()
        payment_plan.status_lock()
        with disable_concurrency(payment_plan):
            payment_plan.save()
            payment_plan.update_money_fields()
    except Exception as e:
        logger.exception(e)
        payment_plan.steficon_applied_date = timezone.now()
        payment_plan.status = PaymentPlan.Status.STEFICON_ERROR
        payment_plan.save()
        raise


@app.task
@log_start_and_end
@sentry_tags
def remove_old_payment_plan_payment_list_xlsx(past_days=30):
    """Remove old Payment Plan Payment List XLSX files"""
    try:
        from hct_mis_api.apps.core.models import FileTemp
        from hct_mis_api.apps.payment.models import PaymentPlan

        days = datetime.datetime.now() - datetime.timedelta(days=past_days)
        file_qs = FileTemp.objects.filter(content_type=get_content_type_for_model(PaymentPlan), created__lte=days)
        if file_qs:
            for xlsx_obj in file_qs:
                xlsx_obj.file.delete(save=False)
                xlsx_obj.delete()

            logger.info(f"Removed old FileTemp: {file_qs.count()}")

    except Exception as e:
        logger.exception(e)
        raise
