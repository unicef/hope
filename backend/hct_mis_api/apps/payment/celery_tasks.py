import datetime
import logging
from typing import Any, Dict

from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from concurrency.api import disable_concurrency
from sentry_sdk import configure_scope

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.payment.models import PaymentVerificationPlan
from hct_mis_api.apps.payment.utils import get_quantity_in_usd
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_verification_export_service import (
    XlsxVerificationExportService,
)
from hct_mis_api.apps.registration_datahub.celery_tasks import locked_cache
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def get_sync_run_rapid_pro_task(self: Any) -> None:
    try:
        from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
            CheckRapidProVerificationTask,
        )

        CheckRapidProVerificationTask().execute()
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
def fsp_generate_xlsx_report_task(self: Any, fsp_id: str) -> None:
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
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def create_payment_verification_plan_xlsx(self: Any, payment_verification_plan_id: str, user_id: str) -> None:
    try:
        user = get_user_model().objects.get(pk=user_id)
        payment_verification_plan = PaymentVerificationPlan.objects.get(id=payment_verification_plan_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", payment_verification_plan.business_area)

            service = XlsxVerificationExportService(payment_verification_plan)
            # if no file will start creating it
            if not payment_verification_plan.has_xlsx_payment_verification_plan_file:
                service.save_xlsx_file(user)

            payment_verification_plan.xlsx_file_exporting = False
            payment_verification_plan.save()
            service.send_email(user)
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def remove_old_cash_plan_payment_verification_xls(self: Any, past_days: int = 30) -> None:
    """Remove old Payment Verification report XLSX files"""
    try:
        days = datetime.datetime.now() - datetime.timedelta(days=past_days)
        ct = ContentType.objects.get(app_label="payment", model="paymentverificationplan")
        files_qs = FileTemp.objects.filter(content_type=ct, created__lte=days)
        if files_qs:
            for obj in files_qs:
                obj.file.delete(save=False)
                obj.delete()

            logger.info(f"Removed old xlsx files for PaymentVerificationPlan: {files_qs.count()}")

    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def create_payment_plan_payment_list_xlsx(self: Any, payment_plan_id: str, user_id: str) -> None:
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_export_service import (
            XlsxPaymentPlanExportService,
        )

        user = get_user_model().objects.get(pk=user_id)
        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)

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

            except Exception as e:
                payment_plan.background_action_status_xlsx_export_error()
                payment_plan.save()
                logger.exception("Create Payment Plan Generate XLSX Error")
                raise self.retry(exc=e)

    except Exception as e:
        logger.exception("Create Payment Plan List XLSX Error")
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def create_payment_plan_payment_list_xlsx_per_fsp(self: Any, payment_plan_id: str, user_id: str) -> None:
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
            XlsxPaymentPlanExportPerFspService,
        )

        user = get_user_model().objects.get(pk=user_id)
        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)

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

            except Exception as e:
                payment_plan.background_action_status_xlsx_export_error()
                payment_plan.save()
                logger.exception("Create Payment Plan Generate XLSX Per FSP Error")
                raise self.retry(exc=e)

    except Exception as e:
        logger.exception("Create Payment Plan List XLSX Per FSP Error")
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def import_payment_plan_payment_list_from_xlsx(self: Any, payment_plan_id: str) -> None:
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_import_service import (
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
            except Exception as e:
                logger.exception("PaymentPlan Error import from xlsx")
                payment_plan.background_action_status_xlsx_import_error()
                payment_plan.save()
                raise self.retry(exc=e)

    except Exception as e:
        logger.exception("PaymentPlan Unexpected Error import from xlsx")
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def import_payment_plan_payment_list_per_fsp_from_xlsx(self: Any, payment_plan_id: str, file_pk: str) -> None:
    try:
        from hct_mis_api.apps.core.models import FileTemp
        from hct_mis_api.apps.payment.models import PaymentPlan

        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        try:
            with configure_scope() as scope:
                scope.set_tag("business_area", payment_plan.business_area)

                service = XlsxPaymentPlanImportPerFspService(payment_plan, FileTemp.objects.get(pk=file_pk).file)
                service.open_workbook()
                with transaction.atomic():
                    service.import_payment_list()
                    payment_plan.remove_export_file()
                    payment_plan.background_action_status_none()
                    payment_plan.update_money_fields()

                    if payment_plan.is_reconciled:
                        payment_plan.status_finished()

                    payment_plan.save()

        except Exception as e:
            logger.exception("Unexpected error during xlsx per fsp import")
            payment_plan.background_action_status_xlsx_import_error()
            payment_plan.save()
            raise self.retry(exc=e)

    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


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


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def payment_plan_apply_engine_rule(self: Any, payment_plan_id: str, engine_rule_id: str) -> None:
    from hct_mis_api.apps.payment.models import Payment, PaymentPlan
    from hct_mis_api.apps.steficon.models import Rule, RuleCommit

    payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
    engine_rule = Rule.objects.get(id=engine_rule_id)
    rule: RuleCommit = engine_rule.latest
    if rule.id != payment_plan.steficon_rule_id:
        payment_plan.steficon_rule = rule
        payment_plan.save()

    try:
        updates = []
        with transaction.atomic():
            payment: Payment
            for payment in payment_plan.eligible_payments:
                # TODO: not sure how will work engine function payment_plan or payment need ??
                result = rule.execute({"household": payment.household, "payment_plan": payment_plan})
                payment.entitlement_quantity = result.value
                payment.entitlement_quantity_usd = get_quantity_in_usd(
                    amount=result.value,
                    currency=payment_plan.currency,
                    exchange_rate=payment_plan.exchange_rate,
                    currency_exchange_date=payment_plan.currency_exchange_date,
                )
                payment.entitlement_date = timezone.now()
                updates.append(payment)
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

    except Exception as e:
        logger.exception("PaymentPlan Run Engine Rule Error")
        payment_plan.background_action_status_steficon_error()
        payment_plan.save()
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def remove_old_payment_plan_payment_list_xlsx(self: Any, past_days: int = 30) -> None:
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
        logger.exception("Remove old Payment Plan Payment List Error")
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def prepare_payment_plan_task(self: Any, payment_plan_id: str) -> bool:
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.services.payment_plan_services import (
            PaymentPlanService,
        )

        payment_plan = PaymentPlan.objects.select_related("target_population").get(id=payment_plan_id)

        PaymentPlanService.create_payments(payment_plan)
        payment_plan.refresh_from_db()
        payment_plan.update_population_count_fields()
        payment_plan.update_money_fields()
        payment_plan.status_open()
        payment_plan.save(update_fields=("status",))
    except Exception as e:
        logger.exception("Prepare Payment Plan Error")
        raise self.retry(exc=e) from e

    return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def prepare_follow_up_payment_plan_task(self: Any, payment_plan_id: str) -> bool:
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.services.payment_plan_services import (
            PaymentPlanService,
        )

        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        PaymentPlanService(payment_plan=payment_plan).create_follow_up_payments()
        payment_plan.refresh_from_db()
        payment_plan.update_population_count_fields()
        payment_plan.update_money_fields()
        payment_plan.status_open()
        payment_plan.status_lock()
        payment_plan.save(update_fields=("status",))
    except Exception as e:
        logger.exception("Prepare Follow Up Payment Plan Error")
        raise self.retry(exc=e) from e

    return True
