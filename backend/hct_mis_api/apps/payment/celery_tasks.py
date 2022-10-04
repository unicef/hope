import datetime
import logging

from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from concurrency.api import disable_concurrency
from sentry_sdk import configure_scope

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.models import (
    PaymentVerificationPlan,
    XlsxPaymentVerificationPlanFile,
)
from hct_mis_api.apps.payment.utils import get_quantity_in_usd
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanPerFspImportService import (
    XlsxPaymentPlanImportPerFspService,
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
        from hct_mis_api.apps.payment.models import FinancialServiceProvider
        from hct_mis_api.apps.payment.services.generate_fsp_xlsx_service import (
            GenerateReportService,
        )

        fsp = FinancialServiceProvider.objects.get(id=fsp_id)
        service = GenerateReportService(fsp=fsp)
        service.generate_report()
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def create_payment_verification_plan_xlsx(cash_plan_payment_verification_id, user_id):
    try:
        user = get_user_model().objects.get(pk=user_id)
        payment_verification_plan = PaymentVerificationPlan.objects.get(id=cash_plan_payment_verification_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", payment_verification_plan.business_area)

            service = XlsxVerificationExportService(payment_verification_plan)
            # if no file will start creating it
            if not getattr(payment_verification_plan, "xlsx_verification_file", None):
                service.save_xlsx_file(user)

            payment_verification_plan.xlsx_file_exporting = False
            payment_verification_plan.save()
            service.send_email(service.get_email_context(user))
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
        files_qs = XlsxPaymentVerificationPlanFile.objects.filter(created_at__lte=days)
        if files_qs:
            for obj in files_qs:
                obj.file.delete(save=False)
                obj.delete()

            logger.info(f"Removed old XlsxPaymentVerificationPlanFile: {files_qs.count()}")

    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def create_payment_plan_payment_list_xlsx(payment_plan_id, user_id):
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportService import (
            XlsxPaymentPlanExportService,
        )

        user = get_user_model().objects.get(pk=user_id)
        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        payment_plan.background_action_status_xlsx_exporting()
        payment_plan.save()

        with configure_scope() as scope:
            scope.set_tag("business_area", payment_plan.business_area)

            try:
                with transaction.atomic():
                    # regenerate always xlsx
                    service = XlsxPaymentPlanExportService(payment_plan)
                    service.save_xlsx_file(user)
                    payment_plan.background_action_status_none()
                    payment_plan.save()

                    transaction.on_commit(lambda: service.send_email(service.get_email_context(user)))

            except Exception:
                payment_plan.background_action_status_xlsx_export_error()
                payment_plan.save()
                logger.exception("Create Payment Plan Generate XLSX Error")
                raise

    except Exception:
        logger.exception("Create Payment Plan List XLSX Error")
        raise


@app.task
@log_start_and_end
@sentry_tags
def create_payment_plan_payment_list_xlsx_per_fsp(payment_plan_id, user_id):
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportPerFspService import (
            XlsxPaymentPlanExportPerFspService,
        )

        user = get_user_model().objects.get(pk=user_id)
        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        payment_plan.background_action_status_xlsx_exporting()
        payment_plan.save()

        with configure_scope() as scope:
            scope.set_tag("business_area", payment_plan.business_area)

            try:
                with transaction.atomic():
                    # regenerate always xlsx
                    service = XlsxPaymentPlanExportPerFspService(payment_plan)
                    service.export_per_fsp(user)
                    payment_plan.background_action_status_none()
                    payment_plan.save()

                    transaction.on_commit(lambda: service.send_email(service.get_email_context(user)))

            except Exception:
                payment_plan.background_action_status_xlsx_export_error()
                payment_plan.save()
                logger.exception("Create Payment Plan Generate XLSX Per FSP Error")
                raise

    except Exception:
        logger.exception("Create Payment Plan List XLSX Per FSP Error")
        raise


@app.task
@log_start_and_end
@sentry_tags
def import_payment_plan_payment_list_from_xlsx(payment_plan_id):
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanImportService import (
            XlsxPaymentPlanImportService,
        )

        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", payment_plan.business_area)

            if not payment_plan.imported_file:
                raise Exception(
                    f"Error import from xlsx, file does not exist for Payment Plan ID {payment_plan.unicef_id}."
                )

            service = XlsxPaymentPlanImportService(payment_plan, payment_plan.imported_file.file)
            service.open_workbook()
            try:
                with transaction.atomic():
                    service.import_payment_list()
                    payment_plan.imported_file_date = timezone.now()
                    payment_plan.background_action_status_none()
                    payment_plan.remove_export_file()
                    payment_plan.save()
                    payment_plan.update_money_fields()
            except Exception:
                logger.exception("PaymentPlan Error import from xlsx")
                payment_plan.background_action_status_xlsx_import_error()
                payment_plan.save()

    except Exception:
        logger.exception("PaymentPlan Unexpected Error import from xlsx")
        raise


@app.task
@log_start_and_end
@sentry_tags
def import_payment_plan_payment_list_per_fsp_from_xlsx(payment_plan_id, user_id, file):
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan

        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        try:
            with configure_scope() as scope:
                scope.set_tag("business_area", payment_plan.business_area)

                service = XlsxPaymentPlanImportPerFspService(payment_plan, file)
                service.open_workbook()
                with transaction.atomic():
                    service.import_payment_list()
                    payment_plan.remove_export_file()
                    payment_plan.background_action_status_none()

                    if payment_plan.is_reconciled:
                        payment_plan.status_reconciled()

                    payment_plan.save()

        except Exception:
            logger.exception("Unexpected error during xlsx per fsp import")
            payment_plan.background_action_status_xlsx_import_error()
            payment_plan.save()

    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def payment_plan_apply_steficon(payment_plan_id, steficon_rule_id):
    from hct_mis_api.apps.payment.models import Payment, PaymentPlan
    from hct_mis_api.apps.steficon.models import Rule, RuleCommit

    payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
    steficon_rule = Rule.objects.get(id=decode_id_string(steficon_rule_id))
    rule: RuleCommit = steficon_rule.latest

    if rule.id != payment_plan.steficon_rule_id:
        payment_plan.steficon_rule = rule
    payment_plan.background_action_status_steficon_run()
    payment_plan.save()

    try:
        updates = []
        with transaction.atomic():
            entry: Payment
            for entry in payment_plan.not_excluded_payments:
                # TODO: not sure how will work steficon function payment_plan or payment need ??
                result = rule.execute({"household": entry.household, "payment_plan": payment_plan})
                entry.entitlement_quantity = result.value
                entry.entitlement_quantity_usd = get_quantity_in_usd(
                    amount=result.value,
                    currency=payment_plan.currency,
                    exchange_rate=payment_plan.exchange_rate,
                    currency_exchange_date=payment_plan.currency_exchange_date,
                )
                entry.entitlement_date = timezone.now()
                updates.append(entry)
            Payment.objects.bulk_update(
                updates, ["entitlement_quantity", "entitlement_date", "entitlement_quantity_usd"]
            )

            payment_plan.steficon_applied_date = timezone.now()
            payment_plan.background_action_status_none()
            with disable_concurrency(payment_plan):
                payment_plan.remove_export_file()
                payment_plan.remove_imported_file()
                payment_plan.save()
                payment_plan.update_money_fields()

    except Exception:
        logger.exception("PaymentPlan Steficon Error")
        payment_plan.background_action_status_steficon_error()
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

    except Exception:
        logger.exception("Remove old Payment Plan Payment List Error")
        raise
