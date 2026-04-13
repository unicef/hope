import datetime
from decimal import Decimal
import logging
from typing import Any

from concurrency.api import disable_concurrency
from django.contrib.admin.options import get_content_type_for_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from hope.apps.core.celery import app
from hope.apps.core.services.rapid_pro.api import RapidProAPI
from hope.apps.core.utils import (
    send_email_notification,
    send_email_notification_on_commit,
)
from hope.apps.payment.flows import PaymentPlanFlow
from hope.apps.payment.pdf.payment_plan_export_pdf_service import (
    PaymentPlanPDFExportService,
)
from hope.apps.payment.utils import (
    calculate_counts,
    from_received_to_status,
    generate_cache_key,
    get_quantity_in_usd,
    normalize_score,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)
from hope.apps.payment.xlsx.xlsx_verification_export_service import (
    XlsxVerificationExportService,
)
from hope.apps.utils.phone import is_valid_phone_number
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import (
    AsyncJob,
    AsyncRetryJob,
    PaymentPlan,
    PaymentVerificationPlan,
    Rule,
    WesternUnionPaymentPlanReport,
)

logger = logging.getLogger(__name__)


def get_sync_run_rapid_pro_async_task_action(job: AsyncRetryJob | None = None) -> None:
    CheckRapidProVerificationTask().execute()


@app.task()
def get_sync_run_rapid_pro_async_task() -> None:
    AsyncRetryJob.queue_task(
        job_name=get_sync_run_rapid_pro_async_task.__name__,
        action="hope.apps.payment.celery_tasks.get_sync_run_rapid_pro_async_task_action",
        config={},
        group_key="get_sync_run_rapid_pro_async_task",
        description="Sync RapidPro verification runs",
    )


def create_payment_verification_plan_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import PaymentVerificationPlan, User

    user = User.objects.get(pk=job.config["user_id"])
    payment_verification_plan = PaymentVerificationPlan.objects.get(id=job.config["payment_verification_plan_id"])

    set_sentry_business_area_tag(payment_verification_plan.business_area.name)

    service = XlsxVerificationExportService(payment_verification_plan)
    if not payment_verification_plan.has_xlsx_payment_verification_plan_file:
        service.save_xlsx_file(user)

    payment_verification_plan.xlsx_file_exporting = False
    payment_verification_plan.save()

    if payment_verification_plan.business_area.enable_email_notification:
        send_email_notification(service, user)


def create_payment_verification_plan_xlsx_async_task(
    payment_verification_plan: PaymentVerificationPlan, user_id: str
) -> None:
    payment_verification_plan_id = str(payment_verification_plan.id)
    config = {
        "payment_verification_plan_id": payment_verification_plan_id,
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        job_name=create_payment_verification_plan_xlsx_async_task.__name__,
        program=payment_verification_plan.get_program,
        action="hope.apps.payment.celery_tasks.create_payment_verification_plan_xlsx_async_task_action",
        config=config,
        group_key=f"create_payment_verification_plan_xlsx_async_task:{payment_verification_plan_id}:{user_id}",
        description=f"Create payment verification plan xlsx for {payment_verification_plan_id}",
    )


def remove_old_cash_plan_payment_verification_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from django.contrib.contenttypes.models import ContentType

    from hope.models import FileTemp

    past_days = int(job.config.get("past_days", 30))
    days = datetime.datetime.now() - datetime.timedelta(days=past_days)
    ct = ContentType.objects.get(app_label="payment", model="paymentverificationplan")
    files_qs = FileTemp.objects.filter(content_type=ct, created__lte=days)
    removed_count = files_qs.count()

    if not removed_count:
        return

    for obj in files_qs.iterator(chunk_size=1000):
        obj.file.delete(save=False)
        obj.delete()

    logger.info(f"Removed old xlsx files for PaymentVerificationPlan: {removed_count}")


@app.task()
def remove_old_cash_plan_payment_verification_xlsx_async_task(past_days: int = 30) -> None:
    config = {"past_days": past_days}
    AsyncRetryJob.queue_task(
        job_name=remove_old_cash_plan_payment_verification_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.remove_old_cash_plan_payment_verification_xlsx_async_task_action",
        config=config,
        group_key=f"remove_old_cash_plan_payment_verification_xlsx_async_task:{past_days}",
        description=f"Remove payment verification xlsx files older than {past_days} days",
    )


def create_payment_plan_payment_list_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.xlsx.xlsx_payment_plan_export_service import (
        XlsxPaymentPlanExportService,
    )
    from hope.models import PaymentPlan, User

    user = User.objects.get(pk=job.config["user_id"])
    payment_plan = PaymentPlan.objects.get(id=job.config["payment_plan_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)

    try:
        with transaction.atomic():
            service = XlsxPaymentPlanExportService(payment_plan)
            service.save_xlsx_file(user)
            flow = PaymentPlanFlow(payment_plan)
            flow.background_action_status_none()
            payment_plan.save()

            if payment_plan.business_area.enable_email_notification:
                send_email_notification_on_commit(service, user)
    except Exception:
        logger.exception("Create Payment Plan Generate XLSX Error")
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_xlsx_export_error()
        payment_plan.save(update_fields=["background_action_status", "updated_at"])
        raise


def create_payment_plan_payment_list_xlsx_async_task(payment_plan: PaymentPlan, user_id: str) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=create_payment_plan_payment_list_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.create_payment_plan_payment_list_xlsx_async_task_action",
        config=config,
        group_key=f"create_payment_plan_payment_list_xlsx_async_task:{payment_plan_id}:{user_id}",
        description=f"Create payment plan payment list xlsx for {payment_plan_id}",
    )


def create_payment_plan_payment_list_xlsx_per_fsp_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
        XlsxPaymentPlanExportPerFspService,
    )
    from hope.models import PaymentPlan, User

    payment_plan_id = job.config["payment_plan_id"]
    user = User.objects.get(pk=job.config["user_id"])
    fsp_xlsx_template_id = job.config.get("fsp_xlsx_template_id")
    payment_plan = PaymentPlan.objects.select_related("program_cycle__program", "business_area").get(id=payment_plan_id)
    set_sentry_business_area_tag(payment_plan.business_area.name)

    with cache.lock(
        f"create_payment_plan_payment_list_xlsx_per_fsp_{payment_plan_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        try:
            service = XlsxPaymentPlanExportPerFspService(payment_plan, fsp_xlsx_template_id)

            if service.payment_generate_token_and_order_numbers:
                with (
                    cache.lock(
                        f"payment_plan_generate_token_and_order_numbers_{str(payment_plan.program.id)}",
                        blocking_timeout=60 * 10,
                        timeout=60 * 20,
                    ),
                    transaction.atomic(),
                ):
                    service.generate_token_and_order_numbers(payment_plan.eligible_payments.all(), payment_plan.program)

            service.export_per_fsp(user)

            if payment_plan.business_area.enable_email_notification:
                send_email_notification(service, user)
                if fsp_xlsx_template_id:
                    service.send_email_with_passwords(user, payment_plan)
        except Exception:
            logger.exception("Create Payment Plan Generate XLSX Per FSP Error")
            flow = PaymentPlanFlow(payment_plan)
            flow.background_action_status_xlsx_export_error()
            payment_plan.save(update_fields=["background_action_status", "updated_at"])
            raise


def create_payment_plan_payment_list_xlsx_per_fsp_async_task(
    payment_plan: PaymentPlan,
    user_id: str,
    fsp_xlsx_template_id: str | None = None,
) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "user_id": user_id,
        "fsp_xlsx_template_id": fsp_xlsx_template_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=create_payment_plan_payment_list_xlsx_per_fsp_async_task.__name__,
        action="hope.apps.payment.celery_tasks.create_payment_plan_payment_list_xlsx_per_fsp_async_task_action",
        config=config,
        group_key=f"create_payment_plan_payment_list_xlsx_per_fsp_async_task:{payment_plan_id}:{fsp_xlsx_template_id}",
        description=f"Create payment plan payment list xlsx per fsp for {payment_plan_id}",
    )


def send_payment_plan_payment_list_xlsx_per_fsp_password_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
        XlsxPaymentPlanExportPerFspService,
    )
    from hope.models import PaymentPlan, User

    user: User = User.objects.get(pk=job.config["user_id"])
    payment_plan = get_object_or_404(PaymentPlan, id=job.config["payment_plan_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)
    XlsxPaymentPlanExportPerFspService.send_email_with_passwords(user, payment_plan)


def send_payment_plan_payment_list_xlsx_per_fsp_password_async_task(
    payment_plan: PaymentPlan,
    user_id: str,
) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=send_payment_plan_payment_list_xlsx_per_fsp_password_async_task.__name__,
        action="hope.apps.payment.celery_tasks.send_payment_plan_payment_list_xlsx_per_fsp_password_async_task_action",
        config=config,
        group_key=f"send_payment_plan_payment_list_xlsx_per_fsp_password_async_task:{payment_plan_id}:{user_id}",
        description=f"Send payment plan xlsx per fsp password for {payment_plan_id}",
    )


def import_payment_plan_payment_list_from_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.xlsx.xlsx_payment_plan_import_service import (
        XlsxPaymentPlanImportService,
    )
    from hope.models import PaymentPlan

    payment_plan = PaymentPlan.objects.get(id=job.config["payment_plan_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)

    if not payment_plan.imported_file:
        raise Exception(f"Error import from xlsx, file does not exist for Payment Plan ID {payment_plan.unicef_id}.")

    service = XlsxPaymentPlanImportService(payment_plan, payment_plan.imported_file.file)
    service.open_workbook()
    try:
        with transaction.atomic():
            service.import_payment_list()
            payment_plan.imported_file_date = timezone.now()
            flow = PaymentPlanFlow(payment_plan)
            flow.background_action_status_none()
            payment_plan.remove_export_files()
            payment_plan.save()
            payment_plan.update_money_fields()

        payment_plan.program_cycle.save()
    except Exception:
        logger.exception("PaymentPlan Error import from xlsx")
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_xlsx_import_error()
        payment_plan.save()
        raise


def import_payment_plan_payment_list_from_xlsx_async_task(payment_plan: PaymentPlan) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {"payment_plan_id": payment_plan_id}
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=import_payment_plan_payment_list_from_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.import_payment_plan_payment_list_from_xlsx_async_task_action",
        config=config,
        group_key=f"import_payment_plan_payment_list_from_xlsx_async_task:{payment_plan_id}",
        description=f"Import payment plan payment list from xlsx for {payment_plan_id}",
    )


def payment_plan_set_entitlement_flat_amount_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import PaymentPlan

    payment_plan = PaymentPlan.objects.get(id=job.config["payment_plan_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)

    try:
        with transaction.atomic():
            exchange_rate = payment_plan.exchange_rate
            flat_amount_value = payment_plan.flat_amount_value
            entitlement_quantity_usd = get_quantity_in_usd(
                amount=flat_amount_value,
                currency=payment_plan.currency,
                exchange_rate=(Decimal(exchange_rate) if exchange_rate is not None else 1),
                currency_exchange_date=payment_plan.currency_exchange_date,
            )
            payment_plan.eligible_payments.update(
                entitlement_quantity=flat_amount_value,
                entitlement_quantity_usd=entitlement_quantity_usd,
                entitlement_date=timezone.now(),
            )
            flow = PaymentPlanFlow(payment_plan)
            flow.background_action_status_none()
            payment_plan.remove_export_files()
            payment_plan.save()
            payment_plan.update_money_fields()
        # invalidate cache for program cycle list
        payment_plan.program_cycle.save()
    except Exception:
        logger.exception("PaymentPlan Error set entitlement flat amount")
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_xlsx_import_error()
        payment_plan.save()
        raise


def payment_plan_set_entitlement_flat_amount_async_task(payment_plan: PaymentPlan) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {"payment_plan_id": payment_plan_id}
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=payment_plan_set_entitlement_flat_amount_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_plan_set_entitlement_flat_amount_async_task_action",
        config=config,
        group_key=f"payment_plan_set_entitlement_flat_amount_async_task:{payment_plan_id}",
        description=f"Set payment plan entitlement flat amount for {payment_plan_id}",
    )


def payment_plan_apply_custom_exchange_rate_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import Payment, PaymentPlan

    payment_plan = get_object_or_404(PaymentPlan, id=job.config["payment_plan_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)

    try:
        bulk_size = 1000
        updates = []
        with transaction.atomic():
            for payment in payment_plan.eligible_payments.only(
                "id",
                "entitlement_quantity",
                "delivered_quantity",
            ).iterator(chunk_size=bulk_size):
                payment.entitlement_quantity_usd = get_quantity_in_usd(
                    amount=payment.entitlement_quantity,
                    currency=payment_plan.currency,
                    exchange_rate=payment_plan.exchange_rate,
                    currency_exchange_date=payment_plan.currency_exchange_date,
                )
                payment.delivered_quantity_usd = get_quantity_in_usd(
                    amount=payment.delivered_quantity,
                    currency=payment_plan.currency,
                    exchange_rate=payment_plan.exchange_rate,
                    currency_exchange_date=payment_plan.currency_exchange_date,
                )
                updates.append(payment)

                if len(updates) >= bulk_size:
                    Payment.objects.bulk_update(
                        updates,
                        ["entitlement_quantity_usd", "delivered_quantity_usd"],
                        batch_size=bulk_size,
                    )
                    updates.clear()

            if updates:
                Payment.objects.bulk_update(
                    updates,
                    ["entitlement_quantity_usd", "delivered_quantity_usd"],
                    batch_size=bulk_size,
                )
            flow = PaymentPlanFlow(payment_plan)
            flow.background_action_status_none()
            payment_plan.save(update_fields=["background_action_status", "updated_at"])
            payment_plan.update_money_fields()
            # invalidate cache for program cycle list
            payment_plan.program_cycle.save()
    except Exception:
        logger.exception("PaymentPlan Apply Custom Exchange Rate Error")
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_applying_custom_exchange_rate_error()
        payment_plan.save(update_fields=["background_action_status", "updated_at"])
        raise


def payment_plan_apply_custom_exchange_rate_async_task(payment_plan: PaymentPlan) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {"payment_plan_id": payment_plan_id}
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=payment_plan_apply_custom_exchange_rate_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_plan_apply_custom_exchange_rate_async_task_action",
        config=config,
        group_key=f"payment_plan_apply_custom_exchange_rate_async_task:{payment_plan_id}",
        description=f"Apply custom exchange rate for payment plan {payment_plan_id}",
    )


def import_payment_plan_payment_list_per_fsp_from_xlsx_async_task_action(job: AsyncRetryJob) -> bool:
    from hope.apps.payment.services.payment_plan_services import PaymentPlanService
    from hope.models import PaymentPlan

    payment_plan = PaymentPlan.objects.select_related("business_area", "reconciliation_import_file").get(
        id=job.config["payment_plan_id"]
    )
    set_sentry_business_area_tag(payment_plan.business_area.name)

    try:
        file_xlsx = payment_plan.reconciliation_import_file.file
        service = XlsxPaymentPlanImportPerFspService(payment_plan, file_xlsx)
        service.open_workbook()
        with transaction.atomic():
            service.import_payment_list()
            payment_plan.remove_export_files()
            flow = PaymentPlanFlow(payment_plan)
            flow.background_action_status_none()
            payment_plan.update_money_fields()

            if payment_plan.is_reconciled and payment_plan.status == PaymentPlan.Status.ACCEPTED:
                flow.status_finished()

            payment_plan.save()
            # invalidate cache for program cycle list
            payment_plan.program_cycle.save()

            logger.info(f"Scheduled update payments signature for payment plan {job.config['payment_plan_id']}")
            PaymentPlanService(payment_plan).recalculate_signatures_in_batch()
    except Exception:
        logger.exception("Unexpected error during xlsx per fsp import")
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_xlsx_import_error()
        payment_plan.save()
        raise

    return True


def import_payment_plan_payment_list_per_fsp_from_xlsx_async_task(payment_plan: PaymentPlan) -> bool | None:
    payment_plan_id = str(payment_plan.id)
    config = {"payment_plan_id": payment_plan_id}
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=import_payment_plan_payment_list_per_fsp_from_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.import_payment_plan_payment_list_per_fsp_from_xlsx_async_task_action",
        config=config,
        group_key=f"import_payment_plan_payment_list_per_fsp_from_xlsx_async_task:{payment_plan_id}",
        description=f"Import payment plan payment list per fsp from xlsx for {payment_plan_id}",
    )
    return None


def payment_plan_apply_engine_rule_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import Payment, PaymentPlan, Rule, RuleCommit

    payment_plan = get_object_or_404(PaymentPlan, id=job.config["payment_plan_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)
    engine_rule = get_object_or_404(Rule, id=job.config["engine_rule_id"])
    rule: RuleCommit | None = engine_rule.latest
    bulk_size = 1000

    if not rule:
        logger.error("PaymentPlan Run Engine Rule Error no RuleCommit")
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_steficon_error()
        payment_plan.save(update_fields=["background_action_status"])
        return

    if rule.id != payment_plan.steficon_rule_id:
        payment_plan.steficon_rule = rule
        payment_plan.save(update_fields=["steficon_rule"])

    try:
        now = timezone.now()
        qs = payment_plan.eligible_payments.select_related("household").only(
            "id",
            "household",  # for rule.execute input
            "entitlement_quantity",
            "entitlement_quantity_usd",
            "entitlement_date",
        )

        pp_currency = payment_plan.currency
        pp_exchange_rate = payment_plan.exchange_rate
        pp_currency_exchange_date = payment_plan.currency_exchange_date

        updates_buffer = []
        with transaction.atomic():
            for payment in qs.iterator(chunk_size=bulk_size):
                result = rule.execute({"household": payment.household, "payment_plan": payment_plan})

                payment.entitlement_quantity = result.value
                payment.entitlement_quantity_usd = get_quantity_in_usd(
                    amount=result.value,
                    currency=pp_currency,
                    exchange_rate=pp_exchange_rate,
                    currency_exchange_date=pp_currency_exchange_date,
                )
                payment.entitlement_date = now
                updates_buffer.append(payment)

                if len(updates_buffer) >= bulk_size:  # pragma: no cover
                    Payment.signature_manager.bulk_update_with_signature(
                        updates_buffer,
                        ["entitlement_quantity", "entitlement_date", "entitlement_quantity_usd"],
                    )
                    updates_buffer.clear()

            if updates_buffer:
                Payment.signature_manager.bulk_update_with_signature(
                    updates_buffer,
                    ["entitlement_quantity", "entitlement_date", "entitlement_quantity_usd"],
                )

            payment_plan.steficon_applied_date = now
            flow = PaymentPlanFlow(payment_plan)
            flow.background_action_status_none()
            with disable_concurrency(payment_plan):
                payment_plan.remove_export_files()
                payment_plan.remove_imported_file()
                payment_plan.save()
                payment_plan.update_money_fields()
        # invalidate cache for program cycle list
        payment_plan.program_cycle.save()
    except Exception:
        logger.exception("PaymentPlan Run Engine Rule Error")
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_steficon_error()
        payment_plan.save()
        raise


def payment_plan_apply_engine_rule_async_task(payment_plan: PaymentPlan, engine_rule: Rule) -> None:
    payment_plan_id = str(payment_plan.id)
    engine_rule_id = str(engine_rule.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "engine_rule_id": engine_rule_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=payment_plan_apply_engine_rule_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_plan_apply_engine_rule_async_task_action",
        config=config,
        group_key=f"payment_plan_apply_engine_rule_async_task:{payment_plan_id}:{engine_rule_id}",
        description=f"Apply engine rule {engine_rule_id} for payment plan {payment_plan_id}",
    )


def update_exchange_rate_on_release_payments_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import Payment, PaymentPlan

    payment_plan = get_object_or_404(PaymentPlan, id=job.config["payment_plan_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)

    payment_plan.exchange_rate = payment_plan.get_exchange_rate()
    payment_plan.save(update_fields=["exchange_rate"])
    payment_plan.refresh_from_db(fields=["exchange_rate"])
    bulk_size = 1000
    updates = []
    currency_exchange_date = payment_plan.currency_exchange_date

    with transaction.atomic():
        for payment in payment_plan.eligible_payments.only(
            "id",
            "entitlement_quantity",
        ).iterator(chunk_size=bulk_size):
            payment.entitlement_quantity_usd = get_quantity_in_usd(
                amount=payment.entitlement_quantity,
                currency=payment_plan.currency,
                exchange_rate=payment_plan.exchange_rate,
                currency_exchange_date=currency_exchange_date,
            )
            updates.append(payment)
            if len(updates) >= bulk_size:
                Payment.objects.bulk_update(updates, ["entitlement_quantity_usd"], batch_size=bulk_size)
                updates.clear()

        if updates:
            Payment.objects.bulk_update(updates, ["entitlement_quantity_usd"], batch_size=bulk_size)
        payment_plan.update_money_fields()
        payment_plan.program_cycle.save()


def update_exchange_rate_on_release_payments_async_task(payment_plan: PaymentPlan) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {"payment_plan_id": payment_plan_id}
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=update_exchange_rate_on_release_payments_async_task.__name__,
        action="hope.apps.payment.celery_tasks.update_exchange_rate_on_release_payments_async_task_action",
        config=config,
        group_key=f"update_exchange_rate_on_release_payments_async_task:{payment_plan_id}",
        description=f"Update exchange rate on release payments for {payment_plan_id}",
    )


def remove_old_payment_plan_payment_list_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import FileTemp, PaymentPlan

    past_days = int(job.config.get("past_days", 30))
    days = datetime.datetime.now() - datetime.timedelta(days=past_days)
    file_qs = FileTemp.objects.filter(content_type=get_content_type_for_model(PaymentPlan), created__lte=days)
    removed_count = file_qs.count()
    if not removed_count:
        return

    for xlsx_obj in file_qs.iterator(chunk_size=1000):
        xlsx_obj.file.delete(save=False)
        xlsx_obj.delete()

    logger.info(f"Removed old FileTemp: {removed_count}")


def remove_old_payment_plan_payment_list_xlsx_async_task(past_days: int = 30) -> None:
    config = {"past_days": past_days}
    AsyncRetryJob.queue_task(
        job_name=remove_old_payment_plan_payment_list_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.remove_old_payment_plan_payment_list_xlsx_async_task_action",
        config=config,
        group_key=f"remove_old_payment_plan_payment_list_xlsx_async_task:{past_days}",
        description=f"Remove payment plan xlsx files older than {past_days} days",
    )


def prepare_payment_plan_async_task_action(job: AsyncRetryJob) -> bool:
    from hope.apps.payment.services.payment_plan_services import PaymentPlanService
    from hope.models import PaymentPlan

    payment_plan_id = job.config["payment_plan_id"]
    cache_key = generate_cache_key(
        {
            "task_name": "prepare_payment_plan_async_task",
            "payment_plan_id": payment_plan_id,
        }
    )
    if cache.get(cache_key):
        logger.info(f"Task prepare_payment_plan_async_task with payment_plan_id {payment_plan_id} already running.")
        return False

    # 10 hours timeout
    cache.set(cache_key, True, timeout=60 * 60 * 10)
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)

    try:
        if payment_plan.status != PaymentPlan.Status.TP_OPEN:
            logger.info(f"The Payment Plan must have the status {PaymentPlan.Status.TP_OPEN}.")
            return False

        with transaction.atomic():
            flow = PaymentPlanFlow(payment_plan)
            flow.build_status_building()
            payment_plan.save(update_fields=("build_status", "built_at"))
            set_sentry_business_area_tag(payment_plan.business_area.name)

            PaymentPlanService.create_payments(payment_plan)
            payment_plan.update_population_count_fields()
            flow.build_status_ok()
            payment_plan.save(update_fields=("build_status", "built_at"))
    except Exception:
        flow = PaymentPlanFlow(payment_plan)
        flow.build_status_failed()
        payment_plan.save(update_fields=("build_status", "built_at"))
        logger.exception("Prepare Payment Plan Error")
        raise
    finally:
        cache.delete(cache_key)

    return True


def prepare_payment_plan_async_task(payment_plan: PaymentPlan) -> bool | None:
    payment_plan_id = str(payment_plan.id)
    config = {"payment_plan_id": payment_plan_id}
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=prepare_payment_plan_async_task.__name__,
        action="hope.apps.payment.celery_tasks.prepare_payment_plan_async_task_action",
        config=config,
        group_key=f"prepare_payment_plan_async_task:{payment_plan_id}",
        description=f"Prepare payment plan {payment_plan_id}",
    )
    return None


def prepare_follow_up_payment_plan_async_task_action(job: AsyncRetryJob) -> bool:
    from hope.apps.payment.services.payment_plan_services import PaymentPlanService
    from hope.models import PaymentPlan

    payment_plan = PaymentPlan.objects.get(id=job.config["payment_plan_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)

    PaymentPlanService(payment_plan=payment_plan).create_follow_up_payments()
    payment_plan.refresh_from_db()
    payment_plan.update_population_count_fields()
    payment_plan.update_money_fields()
    # invalidate cache for program cycle list
    payment_plan.program_cycle.save()
    return True


def prepare_follow_up_payment_plan_async_task(payment_plan: PaymentPlan) -> bool | None:
    payment_plan_id = str(payment_plan.id)
    config = {"payment_plan_id": payment_plan_id}
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=prepare_follow_up_payment_plan_async_task.__name__,
        action="hope.apps.payment.celery_tasks.prepare_follow_up_payment_plan_async_task_action",
        config=config,
        group_key=f"prepare_follow_up_payment_plan_async_task:{payment_plan_id}",
        description=f"Prepare follow up payment plan {payment_plan_id}",
    )
    return None


def payment_plan_exclude_beneficiaries_async_task_action(job: AsyncRetryJob) -> None:
    from django.db.models import Q

    from hope.models import Payment, PaymentPlan

    payment_plan = PaymentPlan.objects.select_related("program_cycle__program").get(id=job.config["payment_plan_id"])
    excluding_hh_or_ind_ids = list(job.config["excluding_hh_or_ind_ids"])
    exclusion_reason = job.config.get("exclusion_reason", "")
    # for social worker program exclude Individual unicef_id
    is_social_worker_program = payment_plan.program_cycle.program.is_social_worker_program
    set_sentry_business_area_tag(payment_plan.business_area.name)
    pp_payment_items = payment_plan.payment_items.select_related("household")
    error_msg, info_msg = [], []
    filter_key = "household__individuals__unicef_id" if is_social_worker_program else "household__unicef_id"

    try:
        payment_item_ids = set(pp_payment_items.values_list(filter_key, flat=True).distinct())
        missing_ids = [unicef_id for unicef_id in excluding_hh_or_ind_ids if unicef_id not in payment_item_ids]
        info_msg.extend(
            f"Beneficiary with ID {unicef_id} is not part of this Payment Plan." for unicef_id in missing_ids
        )
        excluding_hh_or_ind_ids = [unicef_id for unicef_id in excluding_hh_or_ind_ids if unicef_id in payment_item_ids]

        # for Locked PaymentPlan we check if all HHs are not removed from PP
        if (
            payment_plan.status == PaymentPlan.Status.LOCKED
            and len(excluding_hh_or_ind_ids) >= pp_payment_items.count()
        ):
            error_msg.append("Households cannot be entirely excluded from the Payment Plan.")

        payments_for_undo_exclude = pp_payment_items.filter(excluded=True).exclude(
            **{f"{filter_key}__in": excluding_hh_or_ind_ids}
        )
        undo_exclude_hh_ids = list(payments_for_undo_exclude.values_list(filter_key, flat=True).distinct())

        # check if hard conflicts exists in other Payments for undo exclude HH
        conflicting_undo_ids = set()
        if undo_exclude_hh_ids:
            conflicting_undo_ids = set(
                Payment.objects.exclude(parent__id=payment_plan.pk)
                .filter(parent__program_cycle_id=payment_plan.program_cycle_id)
                .filter(
                    Q(parent__program_cycle__start_date__lte=payment_plan.program_cycle.end_date)
                    & Q(parent__program_cycle__end_date__gte=payment_plan.program_cycle.start_date),
                    ~Q(parent__status=PaymentPlan.Status.OPEN),
                    Q(**{f"{filter_key}__in": undo_exclude_hh_ids}) & Q(conflicted=False),
                )
                .values_list(filter_key, flat=True)
                .distinct()
            )
        error_msg += [
            (
                f"It is not possible to undo exclude Beneficiary with ID {unicef_id} because of hard conflict(s) "
                f"with other Payment Plan(s)."
            )
            for unicef_id in undo_exclude_hh_ids
            if unicef_id in conflicting_undo_ids
        ]

        payment_plan.exclusion_reason = exclusion_reason

        if error_msg:
            flow = PaymentPlanFlow(payment_plan)
            flow.background_action_status_exclude_beneficiaries_error()
            payment_plan.exclude_household_error = str([*error_msg, *info_msg])
            payment_plan.save(
                update_fields=[
                    "exclusion_reason",
                    "exclude_household_error",
                    "background_action_status",
                ]
            )
            raise ValidationError("Payment Plan Exclude Beneficiaries Validation Error with Beneficiaries List")

        payments_for_exclude = payment_plan.eligible_payments.filter(**{f"{filter_key}__in": excluding_hh_or_ind_ids})

        payments_for_exclude.update(excluded=True)
        payments_for_undo_exclude.update(excluded=False)

        payment_plan.update_population_count_fields()
        payment_plan.update_money_fields()

        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_none()
        payment_plan.exclude_household_error = str(info_msg or "")
        payment_plan.save(
            update_fields=[
                "exclusion_reason",
                "background_action_status",
                "exclude_household_error",
            ]
        )
        # invalidate cache for program cycle list
        payment_plan.program_cycle.save()
    except Exception as exc:
        logger.exception("Payment Plan Exclude Beneficiaries Error with excluding method. \n" + str(exc))
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_exclude_beneficiaries_error()

        if error_msg:
            payment_plan.exclude_household_error = str([*error_msg, *info_msg])
        payment_plan.save(
            update_fields=[
                "exclusion_reason",
                "background_action_status",
                "exclude_household_error",
            ]
        )
        if error_msg:
            return
        raise


def payment_plan_exclude_beneficiaries_async_task(
    payment_plan: PaymentPlan,
    excluding_hh_or_ind_ids: list[str | None],
    exclusion_reason: str | None = "",
) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "excluding_hh_or_ind_ids": excluding_hh_or_ind_ids,
        "exclusion_reason": exclusion_reason or "",
    }
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=payment_plan_exclude_beneficiaries_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_plan_exclude_beneficiaries_async_task_action",
        config=config,
        group_key=f"payment_plan_exclude_beneficiaries_async_task:{payment_plan_id}",
        description=f"Exclude beneficiaries from payment plan {payment_plan_id}",
    )


def export_pdf_payment_plan_summary_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import FileTemp, PaymentPlan, User

    payment_plan = PaymentPlan.objects.get(id=job.config["payment_plan_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)
    user = User.objects.get(pk=job.config["user_id"])

    with transaction.atomic():
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


def export_pdf_payment_plan_summary_async_task(payment_plan: PaymentPlan, user_id: str) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        owner_id=user_id,
        job_name=export_pdf_payment_plan_summary_async_task.__name__,
        action="hope.apps.payment.celery_tasks.export_pdf_payment_plan_summary_async_task_action",
        config=config,
        group_key=f"export_pdf_payment_plan_summary_async_task:{payment_plan_id}:{user_id}",
        description=f"Export payment plan summary pdf for {payment_plan_id}",
    )


def periodic_sync_payment_gateway_fsp_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from hope.apps.payment.services.payment_gateway import PaymentGatewayAPI, PaymentGatewayService

    try:
        PaymentGatewayService().sync_fsps()
    except PaymentGatewayAPI.PaymentGatewayMissingAPICredentialsError:
        return


@app.task()
def periodic_sync_payment_gateway_fsp_async_task() -> None:
    AsyncRetryJob.queue_task(
        job_name=periodic_sync_payment_gateway_fsp_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_fsp_async_task_action",
        config={},
        group_key="periodic_sync_payment_gateway_fsp_async_task",
        description="Periodic sync payment gateway fsps",
    )


def periodic_sync_payment_gateway_account_types_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from hope.apps.payment.services.payment_gateway import PaymentGatewayAPI, PaymentGatewayService

    try:
        PaymentGatewayService().sync_account_types()
    except PaymentGatewayAPI.PaymentGatewayMissingAPICredentialsError:
        return


@app.task()
def periodic_sync_payment_gateway_account_types_async_task() -> None:
    AsyncRetryJob.queue_task(
        job_name=periodic_sync_payment_gateway_account_types_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_account_types_async_task_action",
        config={},
        group_key="periodic_sync_payment_gateway_account_types_async_task",
        description="Periodic sync payment gateway account types",
    )


def send_to_payment_gateway_async_task_action(job: AsyncJob) -> None:
    from hope.apps.payment.services.payment_gateway import PaymentGatewayService
    from hope.models import PaymentPlan, User

    payment_plan = PaymentPlan.objects.get(id=job.config["payment_plan_id"])
    user = User.objects.get(pk=job.config["user_id"])

    try:
        set_sentry_business_area_tag(payment_plan.business_area.name)
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_send_to_payment_gateway()
        payment_plan.save(update_fields=["background_action_status"])

        PaymentGatewayService().create_payment_instructions(payment_plan, user.email)
        PaymentGatewayService().add_records_to_payment_instructions(payment_plan)

        flow.background_action_status_none()
        payment_plan.save(update_fields=["background_action_status"])
    except Exception:
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_send_to_payment_gateway_error()
        payment_plan.save(update_fields=["background_action_status"])
        raise


def send_to_payment_gateway_async_task(payment_plan: PaymentPlan, user_id: str) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "user_id": user_id,
    }
    AsyncJob.queue_task(
        instance=payment_plan,
        owner_id=user_id,
        job_name=send_to_payment_gateway_async_task.__name__,
        action="hope.apps.payment.celery_tasks.send_to_payment_gateway_async_task_action",
        config=config,
        group_key=f"send_to_payment_gateway_async_task:{payment_plan_id}:{user_id}",
        description=f"Send payment plan {payment_plan_id} to payment gateway",
    )


def periodic_sync_payment_gateway_records_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from hope.apps.payment.services.payment_gateway import PaymentGatewayAPI, PaymentGatewayService

    try:
        PaymentGatewayService().sync_records()
    except PaymentGatewayAPI.PaymentGatewayMissingAPICredentialsError:
        return


@app.task()
def periodic_sync_payment_gateway_records_async_task() -> None:
    AsyncRetryJob.queue_task(
        job_name=periodic_sync_payment_gateway_records_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_records_async_task_action",
        config={},
        group_key="periodic_sync_payment_gateway_records_async_task",
        description="Periodic sync payment gateway records",
    )


def send_payment_notification_emails_async_task_action(job: AsyncJob) -> None:
    from hope.apps.payment.notifications import PaymentNotification
    from hope.models import PaymentPlan, User

    payment_plan = PaymentPlan.objects.get(id=job.config["payment_plan_id"])
    action_user = User.objects.get(id=job.config["action_user_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)
    PaymentNotification(
        payment_plan,
        job.config["action"],
        action_user,
        job.config["action_date_formatted"],
    ).send_email_notification()


def send_payment_notification_emails_async_task(
    payment_plan: PaymentPlan,
    action: str,
    action_user_id: str,
    action_date_formatted: str,
) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "action": action,
        "action_user_id": action_user_id,
        "action_date_formatted": action_date_formatted,
    }
    AsyncJob.queue_task(
        instance=payment_plan,
        owner_id=action_user_id,
        job_name=send_payment_notification_emails_async_task.__name__,
        action="hope.apps.payment.celery_tasks.send_payment_notification_emails_async_task_action",
        config=config,
        group_key=f"send_payment_notification_emails_async_task:{payment_plan_id}:{action}",
        description=f"Send payment notification emails for {payment_plan_id}",
    )


def periodic_sync_payment_gateway_delivery_mechanisms_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from hope.apps.payment.services.payment_gateway import PaymentGatewayAPI, PaymentGatewayService

    try:
        PaymentGatewayService().sync_delivery_mechanisms()
    except PaymentGatewayAPI.PaymentGatewayMissingAPICredentialsError:
        return


@app.task()
def periodic_sync_payment_gateway_delivery_mechanisms_async_task() -> None:
    AsyncRetryJob.queue_task(
        job_name=periodic_sync_payment_gateway_delivery_mechanisms_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_delivery_mechanisms_async_task_action",
        config={},
        group_key="periodic_sync_payment_gateway_delivery_mechanisms_async_task",
        description="Periodic sync payment gateway delivery mechanisms",
    )


def payment_plan_apply_steficon_hh_selection_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import Payment, PaymentPlan, Rule, RuleCommit

    payment_plan = get_object_or_404(PaymentPlan, id=job.config["payment_plan_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)
    engine_rule = get_object_or_404(Rule, id=job.config["engine_rule_id"])
    rule: RuleCommit | None = engine_rule.latest
    if not rule:
        logger.error("PaymentPlan Run Engine Rule Error no RuleCommit")
        flow = PaymentPlanFlow(payment_plan)
        flow.background_action_status_steficon_error()
        payment_plan.save(update_fields=["background_action_status"])
        return

    if rule.id != payment_plan.steficon_rule_targeting_id:
        payment_plan.steficon_rule_targeting = rule
        payment_plan.save(update_fields=["steficon_rule_targeting"])

    try:
        payment_plan.status = PaymentPlan.Status.TP_STEFICON_RUN
        payment_plan.steficon_targeting_applied_date = timezone.now()
        payment_plan.save(update_fields=["status", "steficon_targeting_applied_date"])
        bulk_size = 1000
        updates = []

        with transaction.atomic():
            for payment in payment_plan.payment_items.select_related("household").iterator(chunk_size=bulk_size):
                result = rule.execute(
                    {
                        "household": payment.household,
                        "payment_plan": payment_plan,
                    }
                )
                payment.vulnerability_score = normalize_score(result.value)
                updates.append(payment)
                if len(updates) >= bulk_size:
                    Payment.objects.bulk_update(updates, ["vulnerability_score"], batch_size=bulk_size)
                    updates.clear()

            if updates:
                Payment.objects.bulk_update(updates, ["vulnerability_score"], batch_size=bulk_size)

        if payment_plan.vulnerability_score_min is not None or payment_plan.vulnerability_score_max is not None:
            params = {}
            if payment_plan.vulnerability_score_max is not None:
                params["vulnerability_score__lte"] = payment_plan.vulnerability_score_max
            if payment_plan.vulnerability_score_min is not None:
                params["vulnerability_score__gte"] = payment_plan.vulnerability_score_min
            payment_plan.payment_items(manager="all_objects").filter(**params).update(is_removed=False)
            payment_plan.payment_items(manager="all_objects").exclude(**params).update(is_removed=True)
            payment_plan.update_population_count_fields()
            payment_plan.update_money_fields()

        payment_plan.status = PaymentPlan.Status.TP_STEFICON_COMPLETED
        payment_plan.steficon_targeting_applied_date = timezone.now()
        with disable_concurrency(payment_plan):
            payment_plan.save(update_fields=["status", "steficon_targeting_applied_date"])
    except Exception:
        logger.exception("Payment Plan Apply Steficon HH Selection Error")
        payment_plan.steficon_targeting_applied_date = timezone.now()
        payment_plan.status = PaymentPlan.Status.TP_STEFICON_ERROR
        payment_plan.save(update_fields=["status", "steficon_targeting_applied_date"])
        raise


def payment_plan_apply_steficon_hh_selection_async_task(payment_plan: PaymentPlan, engine_rule_id: str) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "engine_rule_id": engine_rule_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=payment_plan_apply_steficon_hh_selection_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_plan_apply_steficon_hh_selection_async_task_action",
        config=config,
        group_key=f"payment_plan_apply_steficon_hh_selection_async_task:{payment_plan_id}:{engine_rule_id}",
        description=f"Apply steficon hh selection {engine_rule_id} for payment plan {payment_plan_id}",
    )


def payment_plan_rebuild_stats_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import PaymentPlan

    payment_plan_id = job.config["payment_plan_id"]
    with cache.lock(
        f"payment_plan_rebuild_stats_{payment_plan_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        flow = PaymentPlanFlow(payment_plan)
        flow.build_status_building()
        payment_plan.save(update_fields=("build_status", "built_at"))
        with transaction.atomic():
            payment_plan.update_population_count_fields()
            payment_plan.update_money_fields()
            flow = PaymentPlanFlow(payment_plan)
            flow.build_status_ok()
            payment_plan.save(update_fields=("build_status", "built_at"))


def payment_plan_rebuild_stats_async_task(payment_plan: PaymentPlan) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {"payment_plan_id": payment_plan_id}
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=payment_plan_rebuild_stats_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_plan_rebuild_stats_async_task_action",
        config=config,
        group_key=f"payment_plan_rebuild_stats_async_task:{payment_plan_id}",
        description=f"Rebuild payment plan stats for {payment_plan_id}",
    )


def payment_plan_full_rebuild_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.services.payment_plan_services import PaymentPlanService
    from hope.models import PaymentPlan

    payment_plan_id = job.config["payment_plan_id"]
    update_money_fields = bool(job.config.get("update_money_fields", False))

    with cache.lock(
        f"payment_plan_full_rebuild_{payment_plan_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        flow = PaymentPlanFlow(payment_plan)
        flow.build_status_building()
        payment_plan.save(update_fields=("build_status", "built_at"))
        try:
            with transaction.atomic():
                PaymentPlanService(payment_plan).full_rebuild()
                flow = PaymentPlanFlow(payment_plan)
                flow.build_status_ok()
                payment_plan.save(update_fields=("build_status", "built_at"))
                if update_money_fields:
                    payment_plan.update_money_fields()
        except Exception:
            logger.exception("Payment plan full rebuild failed")
            flow = PaymentPlanFlow(payment_plan)
            flow.build_status_failed()
            payment_plan.save(update_fields=("build_status", "built_at"))
            raise


def payment_plan_full_rebuild_async_task(payment_plan: PaymentPlan, update_money_fields: bool = False) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "update_money_fields": update_money_fields,
    }
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=payment_plan_full_rebuild_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_plan_full_rebuild_async_task_action",
        config=config,
        group_key=f"payment_plan_full_rebuild_async_task:{payment_plan_id}:{int(update_money_fields)}",
        description=f"Full rebuild payment plan {payment_plan_id}",
    )


class CheckRapidProVerificationTask:
    def execute(self) -> None:
        from hope.models import PaymentVerificationPlan

        active_rapidpro_verifications = PaymentVerificationPlan.objects.filter(
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
            status=PaymentVerificationPlan.STATUS_ACTIVE,
        )
        for payment_verification_plan in active_rapidpro_verifications:
            try:
                self._verify_cashplan_payment_verification(payment_verification_plan)
            except Exception as e:
                logger.exception(e)

    def _verify_cashplan_payment_verification(self, payment_verification_plan: Any) -> None:
        from hope.models import PaymentVerification

        payment_record_verifications = payment_verification_plan.payment_record_verifications.select_related(
            "payment__head_of_household"
        )
        business_area = payment_verification_plan.payment_plan.business_area
        payment_record_verifications_phone_number_dict = {
            str(payment_verification.payment.head_of_household.phone_no): payment_verification
            for payment_verification in payment_record_verifications
            if payment_verification.payment.head_of_household is not None
        }
        api = RapidProAPI(business_area.slug, RapidProAPI.MODE_VERIFICATION)
        rapid_pro_results = api.get_mapped_flow_runs(payment_verification_plan.rapid_pro_flow_start_uuids)
        payment_record_verification_to_update = self._get_payment_record_verification_to_update(
            rapid_pro_results, payment_record_verifications_phone_number_dict
        )
        PaymentVerification.objects.bulk_update(payment_record_verification_to_update, ("status", "received_amount"))
        calculate_counts(payment_verification_plan)
        payment_verification_plan.save()

    def _get_payment_record_verification_to_update(self, results: Any, phone_numbers: dict) -> list:
        output = []
        for rapid_pro_result in results:
            payment_record_verification = self._rapid_pro_results_to_payment_record_verification(
                phone_numbers, rapid_pro_result
            )
            if payment_record_verification:
                output.append(payment_record_verification)
        return output

    def _rapid_pro_results_to_payment_record_verification(
        self, payment_record_verifications_phone_number_dict: Any, rapid_pro_result: Any
    ) -> Any | None:
        received = rapid_pro_result.get("received")
        received_amount = rapid_pro_result.get("received_amount")
        phone_number = rapid_pro_result.get("phone_number")
        if not phone_number or not is_valid_phone_number(phone_number):
            return None
        payment_record_verification = payment_record_verifications_phone_number_dict.get(phone_number)
        if not payment_record_verification:
            return None
        delivered_amount = payment_record_verification.payment.delivered_quantity
        payment_record_verification.status = from_received_to_status(received, received_amount, delivered_amount)
        payment_record_verification.received_amount = received_amount
        return payment_record_verification


def periodic_sync_payment_plan_invoices_western_union_ftp_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from datetime import datetime, timedelta

    from hope.apps.payment.services.qcf_reports_service import QCFReportsService

    service = QCFReportsService()
    service.process_files_since(datetime.now() - timedelta(hours=24))


@app.task()
def periodic_sync_payment_plan_invoices_western_union_ftp_async_task() -> None:
    AsyncRetryJob.queue_task(
        job_name=periodic_sync_payment_plan_invoices_western_union_ftp_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_sync_payment_plan_invoices_western_union_ftp_async_task_action",
        config={},
        group_key="periodic_sync_payment_plan_invoices_western_union_ftp_async_task",
        description="Periodic sync payment plan invoices western union ftp",
    )


def send_qcf_report_email_notifications_async_task_action(job: AsyncRetryJob) -> None:
    from flags.state import flag_state

    if not bool(flag_state("WU_PAYMENT_PLAN_INVOICES_NOTIFICATIONS_ENABLED")):
        return

    from hope.apps.payment.services.qcf_reports_service import QCFReportsService
    from hope.models import WesternUnionPaymentPlanReport

    qcf_report_id = job.config["qcf_report_id"]
    with cache.lock(
        f"send_qcf_email_notifications_{qcf_report_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        qcf_report = WesternUnionPaymentPlanReport.objects.get(id=qcf_report_id)
        set_sentry_business_area_tag(qcf_report.payment_plan.business_area.name)

        service = QCFReportsService()
        service.send_notification_emails(qcf_report)
        qcf_report.sent = True
        qcf_report.save()


def send_qcf_report_email_notifications_async_task(qcf_report_id: str) -> None:
    config = {"qcf_report_id": qcf_report_id}
    AsyncRetryJob.queue_task(
        job_name=send_qcf_report_email_notifications_async_task.__name__,
        program=WesternUnionPaymentPlanReport.objects.get(id=qcf_report_id).payment_plan.program,
        action="hope.apps.payment.celery_tasks.send_qcf_report_email_notifications_async_task_action",
        config=config,
        group_key=f"send_qcf_report_email_notifications_async_task:{qcf_report_id}",
        description=f"Send qcf report email notifications for {qcf_report_id}",
    )


def periodic_send_payment_plan_reconciliation_overdue_emails_async_task_action(
    job: AsyncRetryJob | None = None,
) -> None:
    from hope.apps.payment.services.payment_plan_services import PaymentPlanService

    PaymentPlanService.send_reconciliation_overdue_emails()


@app.task()
def periodic_send_payment_plan_reconciliation_overdue_emails_async_task() -> None:
    AsyncRetryJob.queue_task(
        job_name=periodic_send_payment_plan_reconciliation_overdue_emails_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task_action",
        config={},
        group_key="periodic_send_payment_plan_reconciliation_overdue_emails_async_task",
        description="Periodic send payment plan reconciliation overdue emails",
    )


def send_payment_plan_reconciliation_overdue_email_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.services.payment_plan_services import PaymentPlanService
    from hope.models import PaymentPlan

    payment_plan_id = job.config["payment_plan_id"]
    with cache.lock(
        f"send_payment_plan_reconciliation_overdue_email_{payment_plan_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        set_sentry_business_area_tag(payment_plan.business_area.name)
        service = PaymentPlanService(payment_plan)
        service.send_reconciliation_overdue_email_for_pp()


def send_payment_plan_reconciliation_overdue_email_async_task(payment_plan: PaymentPlan) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {"payment_plan_id": payment_plan_id}
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        job_name=send_payment_plan_reconciliation_overdue_email_async_task.__name__,
        action="hope.apps.payment.celery_tasks.send_payment_plan_reconciliation_overdue_email_async_task_action",
        config=config,
        group_key=f"send_payment_plan_reconciliation_overdue_email_async_task:{payment_plan_id}",
        description=f"Send payment plan reconciliation overdue email for {payment_plan_id}",
    )
