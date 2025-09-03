import datetime
import logging
from typing import Any, List, Optional

from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from concurrency.api import disable_concurrency

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.core.utils import (
    send_email_notification,
    send_email_notification_on_commit,
)
from hct_mis_api.apps.payment.models import PaymentPlan, PaymentVerificationPlan
from hct_mis_api.apps.payment.pdf.payment_plan_export_pdf_service import (
    PaymentPlanPDFExportService,
)
from hct_mis_api.apps.payment.utils import generate_cache_key, get_quantity_in_usd
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_verification_export_service import (
    XlsxVerificationExportService,
)
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

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
@sentry_tags
def create_payment_verification_plan_xlsx(self: Any, payment_verification_plan_id: str, user_id: str) -> None:
    try:
        user = get_user_model().objects.get(pk=user_id)
        payment_verification_plan = PaymentVerificationPlan.objects.get(id=payment_verification_plan_id)

        set_sentry_business_area_tag(payment_verification_plan.business_area.name)

        service = XlsxVerificationExportService(payment_verification_plan)
        # if no file will start creating it
        if not payment_verification_plan.has_xlsx_payment_verification_plan_file:
            service.save_xlsx_file(user)

        payment_verification_plan.xlsx_file_exporting = False
        payment_verification_plan.save()

        if payment_verification_plan.business_area.enable_email_notification:
            send_email_notification(service, user)

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
        set_sentry_business_area_tag(payment_plan.business_area.name)
        try:
            with transaction.atomic():
                # regenerate always xlsx
                service = XlsxPaymentPlanExportService(payment_plan)
                service.save_xlsx_file(user)
                payment_plan.background_action_status_none()
                payment_plan.save()

                if payment_plan.business_area.enable_email_notification:
                    send_email_notification_on_commit(service, user)

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
def create_payment_plan_payment_list_xlsx_per_fsp(
    self: Any,
    payment_plan_id: str,
    user_id: str,
    fsp_xlsx_template_id: Optional[str] = None,
) -> None:
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
            XlsxPaymentPlanExportPerFspService,
        )

        user = get_user_model().objects.get(pk=user_id)
        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        try:
            with transaction.atomic():
                # regenerate always xlsx
                service = XlsxPaymentPlanExportPerFspService(payment_plan, fsp_xlsx_template_id)
                service.export_per_fsp(user)
                payment_plan.background_action_status_none()
                payment_plan.save()

                if payment_plan.business_area.enable_email_notification:
                    send_email_notification_on_commit(service, user)
                    if fsp_xlsx_template_id:
                        service.send_email_with_passwords(user, payment_plan)

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
def send_payment_plan_payment_list_xlsx_per_fsp_password(
    self: Any,
    payment_plan_id: str,
    user_id: str,
) -> None:
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
            XlsxPaymentPlanExportPerFspService,
        )

        user: User = get_user_model().objects.get(pk=user_id)
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        XlsxPaymentPlanExportPerFspService.send_email_with_passwords(user, payment_plan)

    except Exception as e:
        logger.exception("Send Payment Plan List XLSX Per FSP Password Error")
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
        set_sentry_business_area_tag(payment_plan.business_area.name)

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
                payment_plan.remove_export_files()
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
def import_payment_plan_payment_list_per_fsp_from_xlsx(self: Any, payment_plan_id: str) -> bool:
    try:
        from hct_mis_api.apps.payment.models import PaymentPlan
        from hct_mis_api.apps.payment.services.payment_plan_services import (
            PaymentPlanService,
        )

        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        try:
            file_xlsx = payment_plan.reconciliation_import_file.file
            service = XlsxPaymentPlanImportPerFspService(payment_plan, file_xlsx)
            service.open_workbook()
            with transaction.atomic():
                service.import_payment_list()
                payment_plan.remove_export_files()
                payment_plan.background_action_status_none()
                payment_plan.update_money_fields()

                if payment_plan.is_reconciled:
                    payment_plan.status_finished()

                payment_plan.save()

                logger.info(f"Scheduled update payments signature for payment plan {payment_plan_id}")

                # started update signature for payments sync because we want to be sure that this is atomic
                PaymentPlanService(payment_plan).recalculate_signatures_in_batch()

        except Exception as e:
            logger.exception("Unexpected error during xlsx per fsp import")
            payment_plan.background_action_status_xlsx_import_error()
            payment_plan.save()
            raise self.retry(exc=e)

    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)
    return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def payment_plan_apply_engine_rule(self: Any, payment_plan_id: str, engine_rule_id: str) -> None:
    from hct_mis_api.apps.payment.models import Payment, PaymentPlan
    from hct_mis_api.apps.steficon.models import Rule, RuleCommit

    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
    set_sentry_business_area_tag(payment_plan.business_area.name)
    engine_rule = get_object_or_404(Rule, id=engine_rule_id)
    rule: Optional["RuleCommit"] = engine_rule.latest
    if rule.id != payment_plan.steficon_rule_id:
        payment_plan.steficon_rule = rule
        payment_plan.save()

    try:
        updates = []
        with transaction.atomic():
            payment: Payment
            for payment in payment_plan.eligible_payments:
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
            Payment.signature_manager.bulk_update_with_signature(
                updates,
                [
                    "entitlement_quantity",
                    "entitlement_date",
                    "entitlement_quantity_usd",
                ],
            )

            payment_plan.steficon_applied_date = timezone.now()
            payment_plan.background_action_status_none()
            with disable_concurrency(payment_plan):
                payment_plan.remove_export_files()
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
def update_exchange_rate_on_release_payments(self: Any, payment_plan_id: str) -> None:
    from hct_mis_api.apps.payment.models import Payment, PaymentPlan
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
    set_sentry_business_area_tag(payment_plan.business_area.name)

    payment_plan.exchange_rate = payment_plan.get_exchange_rate()
    payment_plan.save(update_fields=["exchange_rate"])
    payment_plan.refresh_from_db(fields=["exchange_rate"])
    try:
        updates = []
        with transaction.atomic():
            for payment in payment_plan.eligible_payments:
                payment.entitlement_quantity_usd = get_quantity_in_usd(
                    amount=payment.entitlement_quantity,
                    currency=payment_plan.currency,
                    exchange_rate=payment_plan.exchange_rate,
                    currency_exchange_date=payment_plan.currency_exchange_date,
                )
                updates.append(payment)
            Payment.objects.bulk_update(updates, ["entitlement_quantity_usd"])
            payment_plan.update_money_fields()

    except Exception as e:
        logger.exception("PaymentPlan Update Exchange Rate On Release Payments Error")
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
    from hct_mis_api.apps.payment.models import PaymentPlan
    from hct_mis_api.apps.payment.services.payment_plan_services import (
        PaymentPlanService,
    )

    cache_key = generate_cache_key(
        {
            "task_name": "prepare_payment_plan_task",
            "payment_plan_id": payment_plan_id,
        }
    )
    if cache.get(cache_key):
        logger.info(f"Task prepare_payment_plan_task with payment_plan_id {payment_plan_id} already running.")
        return False

    # 10 hours timeout
    cache.set(cache_key, True, timeout=60 * 60 * 10)
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)

    try:
        # double check Payment Plan status
        if payment_plan.status != PaymentPlan.Status.TP_OPEN:
            logger.info(f"The Payment Plan must have the status {PaymentPlan.Status.TP_OPEN}.")
            return False
        with transaction.atomic():
            payment_plan.build_status_building()
            payment_plan.save(update_fields=("build_status", "built_at"))
            set_sentry_business_area_tag(payment_plan.business_area.name)

            PaymentPlanService.create_payments(payment_plan)
            payment_plan.update_population_count_fields()
            payment_plan.build_status_ok()
            payment_plan.save(update_fields=("build_status", "built_at"))
    except Exception as e:
        payment_plan.build_status_failed()
        payment_plan.save(update_fields=("build_status", "built_at"))
        logger.exception("Prepare Payment Plan Error")
        raise self.retry(exc=e) from e

    finally:
        cache.delete(cache_key)

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
        set_sentry_business_area_tag(payment_plan.business_area.name)

        PaymentPlanService(payment_plan=payment_plan).create_follow_up_payments()
        payment_plan.refresh_from_db()
        payment_plan.update_population_count_fields()
        payment_plan.update_money_fields()
    except Exception as e:
        logger.exception("Prepare Follow Up Payment Plan Error")
        raise self.retry(exc=e) from e

    return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def payment_plan_exclude_beneficiaries(
    self: Any,
    payment_plan_id: str,
    excluding_hh_or_ind_ids: List[Optional[str]],
    exclusion_reason: Optional[str] = "",
) -> None:
    try:
        from django.db.models import Q

        from hct_mis_api.apps.payment.models import Payment, PaymentPlan

        payment_plan = PaymentPlan.objects.select_related("program_cycle__program").get(id=payment_plan_id)
        # for social worker program exclude Individual unicef_id
        is_social_worker_program = payment_plan.program_cycle.program.is_social_worker_program
        set_sentry_business_area_tag(payment_plan.business_area.name)
        pp_payment_items = payment_plan.payment_items.select_related("household")
        payment_plan_title = "Follow-up Payment Plan" if payment_plan.is_follow_up else "Payment Plan"
        error_msg, info_msg = [], []
        filter_key = "household__individuals__unicef_id" if is_social_worker_program else "household__unicef_id"

        try:
            for unicef_id in excluding_hh_or_ind_ids:
                if not pp_payment_items.filter(**{f"{filter_key}": unicef_id}).exists():
                    # add only notice for user and ignore this id
                    info_msg.append(f"Beneficiary with ID {unicef_id} is not part of this {payment_plan_title}.")
                    # remove wrong ID from the list because later will compare number of HHs with .eligible_payments()
                    excluding_hh_or_ind_ids.remove(unicef_id)

            if payment_plan.status == PaymentPlan.Status.LOCKED:
                # for Locked PaymentPlan we check if all HHs are not removed from PP
                if len(excluding_hh_or_ind_ids) >= pp_payment_items.count():
                    error_msg.append(f"Households cannot be entirely excluded from the {payment_plan_title}.")

            payments_for_undo_exclude = pp_payment_items.filter(excluded=True).exclude(
                **{f"{filter_key}__in": excluding_hh_or_ind_ids}
            )
            undo_exclude_hh_ids = payments_for_undo_exclude.values_list(filter_key, flat=True)

            # check if hard conflicts exists in other Payments for undo exclude HH
            for unicef_id in undo_exclude_hh_ids:
                if (
                    Payment.objects.exclude(parent__id=payment_plan.pk)
                    .filter(
                        parent__program_cycle_id=payment_plan.program_cycle_id
                    )  # check only Payments in the same program cycle
                    .filter(
                        Q(parent__program_cycle__start_date__lte=payment_plan.program_cycle.end_date)
                        & Q(parent__program_cycle__end_date__gte=payment_plan.program_cycle.start_date),
                        ~Q(parent__status=PaymentPlan.Status.OPEN),
                        Q(**{filter_key: unicef_id}) & Q(conflicted=False),
                    )
                    .exists()
                ):
                    error_msg.append(
                        f"It is not possible to undo exclude Beneficiary with ID {unicef_id} because of hard conflict(s) with other {payment_plan_title}(s)."
                    )

            payment_plan.exclusion_reason = exclusion_reason

            if error_msg:
                payment_plan.background_action_status_exclude_beneficiaries_error()
                payment_plan.exclude_household_error = str([*error_msg, *info_msg])
                payment_plan.save(
                    update_fields=[
                        "exclusion_reason",
                        "exclude_household_error",
                        "background_action_status",
                    ]
                )
                raise ValidationError("Payment Plan Exclude Beneficiaries Validation Error with Beneficiaries List")

            payments_for_exclude = payment_plan.eligible_payments.filter(
                **{f"{filter_key}__in": excluding_hh_or_ind_ids}
            )

            payments_for_exclude.update(excluded=True)
            payments_for_undo_exclude.update(excluded=False)

            payment_plan.update_population_count_fields()
            payment_plan.update_money_fields()

            payment_plan.background_action_status_none()
            payment_plan.exclude_household_error = str(info_msg or "")
            payment_plan.save(
                update_fields=[
                    "exclusion_reason",
                    "background_action_status",
                    "exclude_household_error",
                ]
            )
        except Exception as e:
            logger.exception("Payment Plan Exclude Beneficiaries Error with excluding method. \n" + str(e))
            payment_plan.background_action_status_exclude_beneficiaries_error()

            if error_msg:
                payment_plan.exclude_household_error = str([*error_msg, *info_msg])
            payment_plan.save(
                update_fields=[
                    "exclusion_reason",
                    "background_action_status",
                    "exclude_household_error",
                ]
            )

    except Exception as e:
        logger.exception("Payment Plan Excluding Beneficiaries Error with celery task. \n" + str(e))
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def export_pdf_payment_plan_summary(self: Any, payment_plan_id: str, user_id: str) -> None:
    """create PDF file with summary and sent an enail to request user"""
    try:
        from hct_mis_api.apps.core.models import FileTemp
        from hct_mis_api.apps.payment.models import PaymentPlan

        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        user = get_user_model().objects.get(pk=user_id)

        with transaction.atomic():
            # regenerate PDF always
            # remove old export_pdf_file_summary
            if payment_plan.export_pdf_file_summary:
                payment_plan.export_pdf_file_summary.file.delete()
                payment_plan.export_pdf_file_summary.delete()
                payment_plan.export_pdf_file_summary = None

            service = PaymentPlanPDFExportService(payment_plan)
            pdf, filename = service.generate_pdf_summary()

            file_pdf_obj = FileTemp(
                object_id=payment_plan.pk,
                content_type=get_content_type_for_model(payment_plan),
                created_by=user,
            )
            file_pdf_obj.file.save(filename, ContentFile(pdf))

            payment_plan.export_pdf_file_summary = file_pdf_obj
            payment_plan.save()

            if payment_plan.business_area.enable_email_notification:
                send_email_notification_on_commit(service, user)

    except Exception as e:
        logger.exception("Export PDF Payment Plan Summary Error")
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def periodic_sync_payment_gateway_fsp(self: Any) -> None:  # pragma: no cover
    from hct_mis_api.apps.payment.services.payment_gateway import PaymentGatewayAPI

    try:
        from hct_mis_api.apps.payment.services.payment_gateway import (
            PaymentGatewayService,
        )

        PaymentGatewayService().sync_fsps()
    except PaymentGatewayAPI.PaymentGatewayMissingAPICredentialsException:
        return
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def periodic_sync_payment_gateway_account_types(self: Any) -> None:  # pragma: no cover
    from hct_mis_api.apps.payment.services.payment_gateway import PaymentGatewayAPI

    try:
        from hct_mis_api.apps.payment.services.payment_gateway import (
            PaymentGatewayService,
        )

        PaymentGatewayService().sync_account_types()
    except PaymentGatewayAPI.PaymentGatewayMissingAPICredentialsException:
        return
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True)
@log_start_and_end
@sentry_tags
def send_to_payment_gateway(self: Any, payment_plan_id: str, user_id: str) -> None:
    from hct_mis_api.apps.payment.services.payment_gateway import PaymentGatewayService

    try:
        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        user = get_user_model().objects.get(pk=user_id)

        payment_plan.background_action_status_send_to_payment_gateway()
        payment_plan.save(update_fields=["background_action_status"])

        PaymentGatewayService().create_payment_instructions(payment_plan, user.email)
        PaymentGatewayService().add_records_to_payment_instructions(payment_plan)

        payment_plan.background_action_status_none()
        payment_plan.save(update_fields=["background_action_status"])
    except Exception:
        msg = "Error while sending to Payment Gateway"
        logger.exception(msg)
        payment_plan.background_action_status_send_to_payment_gateway_error()
        payment_plan.save(update_fields=["background_action_status"])


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def periodic_sync_payment_gateway_records(self: Any) -> None:
    from hct_mis_api.apps.payment.services.payment_gateway import PaymentGatewayAPI

    try:
        from hct_mis_api.apps.payment.services.payment_gateway import (
            PaymentGatewayService,
        )

        PaymentGatewayService().sync_records()
    except PaymentGatewayAPI.PaymentGatewayMissingAPICredentialsException:
        return
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True)
@log_start_and_end
@sentry_tags
def send_payment_notification_emails(
    self: Any,
    payment_plan_id: str,
    action: str,
    action_user_id: str,
    action_date_formatted: str,
) -> None:
    from hct_mis_api.apps.payment.notifications import PaymentNotification

    try:
        payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        action_user = User.objects.get(id=action_user_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        PaymentNotification(payment_plan, action, action_user, action_date_formatted).send_email_notification()
    except Exception as e:
        logger.exception(e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def periodic_sync_payment_gateway_delivery_mechanisms(self: Any) -> None:
    from hct_mis_api.apps.payment.services.payment_gateway import PaymentGatewayAPI

    try:
        from hct_mis_api.apps.payment.services.payment_gateway import (
            PaymentGatewayService,
        )

        PaymentGatewayService().sync_delivery_mechanisms()
    except PaymentGatewayAPI.PaymentGatewayMissingAPICredentialsException:
        return
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def payment_plan_apply_steficon_hh_selection(self: Any, payment_plan_id: str, engine_rule_id: str) -> None:
    from hct_mis_api.apps.payment.models import Payment, PaymentPlan
    from hct_mis_api.apps.steficon.models import Rule, RuleCommit

    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
    set_sentry_business_area_tag(payment_plan.business_area.name)
    engine_rule = get_object_or_404(Rule, id=engine_rule_id)
    rule: Optional["RuleCommit"] = engine_rule.latest
    if rule and rule.id != payment_plan.steficon_rule_targeting_id:
        payment_plan.steficon_rule_targeting = rule
        payment_plan.save(update_fields=["steficon_rule_targeting"])
    try:
        payment_plan.status = PaymentPlan.Status.TP_STEFICON_RUN
        payment_plan.steficon_targeting_applied_date = timezone.now()
        payment_plan.save(update_fields=["status", "steficon_targeting_applied_date"])
        updates = []
        with transaction.atomic():
            payment: Payment
            for payment in payment_plan.payment_items.all():
                result = rule.execute(
                    {
                        "household": payment.household,
                        "payment_plan": payment_plan,
                    }
                )
                payment.vulnerability_score = result.value
                updates.append(payment)
            Payment.objects.bulk_update(updates, ["vulnerability_score"])
        payment_plan.status = PaymentPlan.Status.TP_STEFICON_COMPLETED
        payment_plan.steficon_targeting_applied_date = timezone.now()
        with disable_concurrency(payment_plan):
            payment_plan.save(update_fields=["status", "steficon_targeting_applied_date"])
    except Exception as e:
        logger.exception(e)
        payment_plan.steficon_targeting_applied_date = timezone.now()
        payment_plan.status = PaymentPlan.Status.TP_STEFICON_ERROR
        payment_plan.save(update_fields=["status", "steficon_targeting_applied_date"])
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def payment_plan_rebuild_stats(self: Any, payment_plan_id: str) -> None:
    with cache.lock(
        f"payment_plan_rebuild_stats_{payment_plan_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        payment_plan.build_status_building()
        payment_plan.save(update_fields=("build_status", "built_at"))
        try:
            with transaction.atomic():
                payment_plan.update_population_count_fields()
                payment_plan.update_money_fields()
                payment_plan.build_status_ok()
                payment_plan.save(update_fields=("build_status", "built_at"))
        except Exception as e:
            logger.exception(e)
            raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def payment_plan_full_rebuild(self: Any, payment_plan_id: str) -> None:
    from hct_mis_api.apps.payment.services.payment_plan_services import (
        PaymentPlanService,
    )

    with cache.lock(
        f"payment_plan_full_rebuild_{payment_plan_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        payment_plan.build_status_building()
        payment_plan.save(update_fields=("build_status", "built_at"))
        try:
            with transaction.atomic():
                PaymentPlanService(payment_plan).full_rebuild()
                payment_plan.build_status_ok()
                payment_plan.save(update_fields=("build_status", "built_at"))
        except Exception as e:
            logger.exception(e)
            payment_plan.build_status_failed()
            payment_plan.save(update_fields=("build_status", "built_at"))
            raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def periodic_sync_payment_plan_invoices_western_union_ftp(self: Any) -> None:
    from datetime import datetime, timedelta

    from hct_mis_api.apps.payment.services.qcf_reports_service import QCFReportsService

    try:
        service = QCFReportsService()
        service.process_files_since(datetime.now() - timedelta(hours=24))

    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def send_qcf_report_email_notifications(self: Any, qcf_report_id: str) -> None:
    from hct_mis_api.apps.payment.models.payment import WesternUnionPaymentPlanReport
    from hct_mis_api.apps.payment.services.qcf_reports_service import QCFReportsService

    with cache.lock(
        f"send_qcf_email_notifications_{qcf_report_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        qcf_report = WesternUnionPaymentPlanReport.objects.get(id=qcf_report_id)
        try:
            set_sentry_business_area_tag(qcf_report.payment_plan.business_area.name)

            service = QCFReportsService()
            service.send_notification_emails(qcf_report)
            qcf_report.sent = True
            qcf_report.save()

        except Exception as e:
            logger.exception(f"Failed to send QCF report emails for {qcf_report}")
            raise self.retry(exc=e)
