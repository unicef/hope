import datetime as dt
from decimal import Decimal
from functools import partial
import logging
from typing import Any, cast

from concurrency.api import disable_concurrency
from django.contrib.admin.options import get_content_type_for_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.core.celery import app
from hope.apps.core.services.rapid_pro.api import RapidProAPI
from hope.apps.core.utils import (
    send_email_notification,
    send_email_notification_on_commit,
)
from hope.apps.payment.flows import FollowUpInstructionFlow, PaymentListFlow
from hope.apps.payment.notifications import PaymentPlanReconciliationImportNotification
from hope.apps.payment.pdf.payment_plan_export_pdf_service import (
    FollowUpInstructionPDFExportService,
    PaymentPlanPDFExportService,
)
from hope.apps.payment.utils import (
    bulk_log_payment_changes,
    calculate_counts,
    from_received_to_status,
    generate_cache_key,
    get_owner_unore_exchange_rate,
    get_quantity_in_usd,
    log_follow_up_instruction_change,
    log_payment_list_change,
    log_payment_plan_change,
    normalize_score,
)
from hope.apps.payment.xlsx.xlsx_payment_list_delivery_export_service import (
    XlsxPaymentListDeliveryExportService,
)
from hope.apps.payment.xlsx.xlsx_payment_list_delivery_import_service import (
    NULL_DELIVERY_POLICY_OPTION,
    NULL_DELIVERY_POLICY_RESET,
    OVERRIDE_OPTION,
)
from hope.apps.payment.xlsx.xlsx_verification_export_service import (
    XlsxVerificationExportService,
)
from hope.apps.utils.phone import is_valid_phone_number
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import (
    AsyncJob,
    AsyncRetryJob,
    FileTemp,
    FollowUpInstruction,
    PaymentList,
    PaymentPlan,
    PaymentVerificationPlan,
    PeriodicAsyncRetryJob,
    Rule,
    User,
    WesternUnionPaymentListReport,
)

logger = logging.getLogger(__name__)


EXPORT_PAYMENT_PLAN_DELIVERY_XLSX_LOCK_PREFIX = "export_payment_plan_delivery_xlsx_"
PAYMENT_LIST_ORDER_NUMBERS_LOCK_PREFIX = "payment_list_generate_token_and_order_numbers_"
PAYMENT_LIST_REBUILD_STATS_LOCK_PREFIX = "payment_list_rebuild_stats_"
PAYMENT_LIST_FULL_REBUILD_LOCK_PREFIX = "payment_list_full_rebuild_"
SEND_WESTERN_UNION_REPORT_EMAIL_LOCK_PREFIX = "send_western_union_report_email_notifications_"
SEND_PAYMENT_LIST_RECONCILIATION_OVERDUE_EMAIL_LOCK_PREFIX = "send_payment_list_reconciliation_overdue_email_"


def get_sync_run_rapid_pro_async_task_action(job: AsyncRetryJob | None = None) -> None:
    CheckRapidProVerificationTask().execute()


@app.task()
def get_sync_run_rapid_pro_async_task() -> None:
    PeriodicAsyncRetryJob.queue_task(
        job_name=get_sync_run_rapid_pro_async_task.__name__,
        action="hope.apps.payment.celery_tasks.get_sync_run_rapid_pro_async_task_action",
        config={},
        group_key="payment",
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
        group_key="payment",
        description=f"Create payment verification plan xlsx for {payment_verification_plan_id}",
    )


def remove_old_cash_plan_payment_verification_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from django.contrib.contenttypes.models import ContentType

    from hope.models import FileTemp

    past_days = int(job.config.get("past_days", 30))
    days = dt.datetime.now() - dt.timedelta(days=past_days)
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
    PeriodicAsyncRetryJob.queue_task(
        job_name=remove_old_cash_plan_payment_verification_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.remove_old_cash_plan_payment_verification_xlsx_async_task_action",
        config=config,
        group_key="payment",
        description=f"Remove payment verification xlsx files older than {past_days} days",
    )


def create_payment_list_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.xlsx.xlsx_payment_list_export_service import (
        XlsxPaymentListExportService,
    )
    from hope.models import PaymentList, User

    user = User.objects.get(pk=job.config["user_id"])
    payment_list = PaymentList.objects.get(id=job.config["payment_list_id"])
    set_sentry_business_area_tag(payment_list.business_area.name)
    old_payment_list = cast("PaymentList", copy_model_object(payment_list))

    try:
        with transaction.atomic():
            service = XlsxPaymentListExportService(payment_list)
            service.save_xlsx_file(user)
            flow = PaymentListFlow(payment_list)
            flow.background_action_status_none()
            payment_list.save()
            log_payment_list_change(payment_list, old_payment_list, job.config["user_id"])

            if payment_list.business_area.enable_email_notification:
                send_email_notification_on_commit(service, user)
    except Exception:
        logger.exception("Create Payment List Generate XLSX Error")
        flow = PaymentListFlow(payment_list)
        flow.background_action_status_xlsx_export_error()
        payment_list.save(update_fields=["background_action_status", "updated_at"])
        raise


def create_payment_list_xlsx_async_task(payment_list: PaymentList, user_id: str) -> None:
    payment_list_id = str(payment_list.id)
    config = {
        "payment_list_id": payment_list_id,
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_list,
        job_name=create_payment_list_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.create_payment_list_xlsx_async_task_action",
        config=config,
        group_key="payment",
        description=f"Create payment list xlsx for {payment_list_id}",
    )


def create_follow_up_instruction_delivery_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.xlsx.xlsx_follow_up_instruction_delivery_export_service import (
        XlsxFollowUpInstructionDeliveryExportService,
    )
    from hope.models import FollowUpInstruction, User

    instruction_id = job.config["follow_up_instruction_id"]
    user = User.objects.get(pk=job.config["user_id"])
    instruction = FollowUpInstruction.objects.select_related("business_area", "program").get(id=instruction_id)

    try:
        with transaction.atomic():
            service = XlsxFollowUpInstructionDeliveryExportService(instruction)
            service.save_xlsx_file(user)
            flow = FollowUpInstructionFlow(instruction)
            flow.background_action_status_none()
            instruction.save(update_fields=["background_action_status", "updated_at"])
    except Exception:
        logger.exception("Create Follow Up Instruction Delivery XLSX Error")
        flow = FollowUpInstructionFlow(instruction)
        flow.background_action_status_xlsx_export_error()
        instruction.save(update_fields=["background_action_status", "updated_at"])
        raise


def create_follow_up_instruction_delivery_xlsx_async_task(
    instruction: FollowUpInstruction,
    user_id: str,
) -> None:
    instruction_id = str(instruction.id)
    config = {
        "follow_up_instruction_id": instruction_id,
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        instance=instruction,
        job_name=create_follow_up_instruction_delivery_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.create_follow_up_instruction_delivery_xlsx_async_task_action",
        config=config,
        group_key="payment",
        description=f"Create follow up instruction delivery xlsx for {instruction_id}",
    )


def export_payment_plan_delivery_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.core.celery_tasks import NonRetriableTaskError
    from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_export_service import (
        UnexportablePaymentListsError,
        XlsxPaymentPlanDeliveryExportService,
    )
    from hope.models import PaymentPlan, User

    payment_plan_id = job.config["payment_plan_id"]
    with cache.lock(
        f"{EXPORT_PAYMENT_PLAN_DELIVERY_XLSX_LOCK_PREFIX}{payment_plan_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        payment_plan = PaymentPlan.objects.select_related("cycle__program__business_area").get(id=payment_plan_id)
        old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
        user = User.objects.get(pk=job.config["user_id"])
        fsp_xlsx_template_id = job.config.get("fsp_xlsx_template_id")
        try:
            service = XlsxPaymentPlanDeliveryExportService(payment_plan, fsp_xlsx_template_id=fsp_xlsx_template_id)
            if service.payment_lists and service.payment_generate_token_and_order_numbers:
                program = payment_plan.cycle.program
                with (
                    cache.lock(
                        f"{PAYMENT_LIST_ORDER_NUMBERS_LOCK_PREFIX}{str(program.id)}",
                        blocking_timeout=60 * 10,
                        timeout=60 * 20,
                    ),
                    transaction.atomic(),
                ):
                    service.generate_token_and_order_numbers(program)
            with transaction.atomic():
                service.save_xlsx_file(user)
                payment_plan.background_action_status = None
                payment_plan.save(update_fields=["background_action_status", "updated_at"])
                log_payment_plan_change(payment_plan, old_payment_plan, job.config["user_id"])
            if payment_plan.cycle.program.business_area.enable_email_notification:
                send_email_notification(service, user)
        except UnexportablePaymentListsError as exc:
            logger.warning(f"{exc} {' '.join(exc.skipped_reasons)}")
            payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_EXPORT_ERROR
            payment_plan.save(update_fields=["background_action_status", "updated_at"])
            log_payment_plan_change(payment_plan, old_payment_plan, job.config["user_id"])
            job.errors = {**job.errors, "export_skipped_payment_lists": exc.skipped_reasons}
            job.save(update_fields=["errors"])
            raise NonRetriableTaskError(str(exc)) from exc
        except Exception:
            logger.exception("Export Payment Plan Delivery XLSX Error")
            payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_EXPORT_ERROR
            payment_plan.save(update_fields=["background_action_status", "updated_at"])
            log_payment_plan_change(payment_plan, old_payment_plan, job.config["user_id"])
            raise


def export_payment_plan_delivery_xlsx_async_task(
    payment_plan: "PaymentPlan",
    user_id: str,
    fsp_xlsx_template_id: str | None = None,
) -> None:
    payment_plan_id = str(payment_plan.id)
    config: dict = {"payment_plan_id": payment_plan_id, "user_id": user_id}
    if fsp_xlsx_template_id is not None:
        config["fsp_xlsx_template_id"] = fsp_xlsx_template_id
    AsyncRetryJob.queue_task(
        program=payment_plan.cycle.program,
        job_name=export_payment_plan_delivery_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.export_payment_plan_delivery_xlsx_async_task_action",
        instance=payment_plan,
        config=config,
        group_key="payment",
        description=f"Export payment plan delivery xlsx for {payment_plan_id}",
    )


def send_payment_plan_delivery_xlsx_password_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import PaymentPlan, User

    payment_plan = PaymentPlan.objects.select_related("export_file_delivery").get(id=job.config["payment_plan_id"])
    user = User.objects.get(pk=job.config["user_id"])

    if payment_plan.export_file_delivery is None:
        raise Exception(f"No exported payment list file found for payment plan {payment_plan.id}.")
    label = f"Payment Plan {payment_plan.unicef_id} Payment List"
    XlsxPaymentListDeliveryExportService.send_delivery_passwords_for_file(
        user, payment_plan.export_file_delivery, label
    )


def send_payment_plan_delivery_xlsx_password_async_task(
    payment_plan: "PaymentPlan",
    user_id: str,
) -> None:
    config = {
        "payment_plan_id": str(payment_plan.id),
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        program=payment_plan.cycle.program,
        instance=payment_plan,
        job_name=send_payment_plan_delivery_xlsx_password_async_task.__name__,
        action="hope.apps.payment.celery_tasks.send_payment_plan_delivery_xlsx_password_async_task_action",
        config=config,
        group_key="payment",
        description=f"Send payment plan delivery xlsx password for payment plan {payment_plan.id}",
    )


def import_payment_list_from_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.xlsx.xlsx_payment_list_import_service import (
        XlsxPaymentListImportService,
    )
    from hope.models import PaymentList

    payment_list = PaymentList.objects.get(id=job.config["payment_list_id"])
    set_sentry_business_area_tag(payment_list.business_area.name)
    old_payment_list = cast("PaymentList", copy_model_object(payment_list))

    if not payment_list.imported_file:
        raise Exception(f"Error import from xlsx, file does not exist for Payment List ID {payment_list.unicef_id}.")

    service = XlsxPaymentListImportService(payment_list, payment_list.imported_file.file)
    service.open_workbook()
    try:
        with transaction.atomic():
            service.import_payment_list(job.config.get("user_id"))
            payment_list.imported_file_date = timezone.now()
            flow = PaymentListFlow(payment_list)
            flow.background_action_status_none()
            payment_list.remove_export_files()
            payment_list.save()
            payment_list.update_money_fields()

        payment_list.program_cycle.save()
        log_payment_list_change(payment_list, old_payment_list, job.config.get("user_id"))
    except Exception:
        logger.exception("PaymentList Error import from xlsx")
        flow = PaymentListFlow(payment_list)
        flow.background_action_status_xlsx_import_error()
        payment_list.save()
        raise


def import_payment_list_from_xlsx_async_task(payment_list: PaymentList, user_id: str | None = None) -> None:
    payment_list_id = str(payment_list.id)
    config = {"payment_list_id": payment_list_id, "user_id": user_id}
    AsyncRetryJob.queue_task(
        instance=payment_list,
        owner_id=user_id,
        job_name=import_payment_list_from_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.import_payment_list_from_xlsx_async_task_action",
        config=config,
        group_key="payment",
        description=f"Import payment list from xlsx for {payment_list_id}",
    )


def payment_list_set_entitlement_flat_amount_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import PaymentList

    payment_list = PaymentList.objects.get(id=job.config["payment_list_id"])
    set_sentry_business_area_tag(payment_list.business_area.name)

    try:
        with transaction.atomic():
            exchange_rate = payment_list.exchange_rate
            flat_amount_value = payment_list.flat_amount_value
            entitlement_quantity_usd = get_quantity_in_usd(
                amount=flat_amount_value,
                currency=payment_list.currency,
                exchange_rate=(Decimal(exchange_rate) if exchange_rate is not None else 1),
                currency_exchange_date=payment_list.currency_exchange_date,
            )
            payment_list.eligible_payments.update_and_log(
                {"entitlement_quantity": flat_amount_value},
                job.config.get("user_id"),
                extra_update={
                    "entitlement_quantity_usd": entitlement_quantity_usd,
                    "entitlement_date": timezone.now(),
                },
            )
            flow = PaymentListFlow(payment_list)
            flow.background_action_status_none()
            payment_list.remove_export_files()
            payment_list.save()
            payment_list.update_money_fields()
        # invalidate cache for program cycle list
        payment_list.program_cycle.save()
    except Exception:
        logger.exception("PaymentList Error set entitlement flat amount")
        flow = PaymentListFlow(payment_list)
        flow.background_action_status_xlsx_import_error()
        payment_list.save()
        raise


def payment_list_set_entitlement_flat_amount_async_task(payment_list: PaymentList, user_id: str | None = None) -> None:
    payment_list_id = str(payment_list.id)
    config = {"payment_list_id": payment_list_id, "user_id": user_id}
    AsyncRetryJob.queue_task(
        instance=payment_list,
        owner_id=user_id,
        job_name=payment_list_set_entitlement_flat_amount_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_list_set_entitlement_flat_amount_async_task_action",
        config=config,
        group_key="payment",
        description=f"Set payment list entitlement flat amount for {payment_list_id}",
    )


def import_payment_plan_fsp_extra_fields_from_xlsx_async_task_action(job: AsyncRetryJob) -> bool:
    from hope.apps.payment.xlsx.xlsx_payment_plan_fsp_extra_fields_import_service import (
        XlsxPaymentPlanFspExtraFieldsImportService,
    )

    payment_plan = PaymentPlan.objects.select_related("cycle__program__business_area").get(
        id=job.config["payment_plan_id"]
    )
    file_temp = FileTemp.objects.get(id=job.config["file_temp_id"])
    set_sentry_business_area_tag(payment_plan.cycle.program.business_area.name)
    old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))

    try:
        service = XlsxPaymentPlanFspExtraFieldsImportService(payment_plan, file_temp.file)
        service.open_workbook()
        with transaction.atomic():
            service.import_payment_list(job.config.get("user_id"))
            payment_plan.background_action_status = None
            payment_plan.save(update_fields=["background_action_status", "updated_at"])
            log_payment_plan_change(payment_plan, old_payment_plan, job.config.get("user_id"))
    except Exception:
        logger.exception("Unexpected error during Payment Plan FSP extra fields XLSX import")
        payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR
        payment_plan.save(update_fields=["background_action_status", "updated_at"])
        log_payment_plan_change(payment_plan, old_payment_plan, job.config.get("user_id"))
        raise

    return True


def import_payment_plan_fsp_extra_fields_from_xlsx_async_task(
    payment_plan: PaymentPlan,
    file_temp_id: str,
    user_id: str | None = None,
) -> None:
    payment_plan_id = str(payment_plan.id)
    config = {
        "payment_plan_id": payment_plan_id,
        "file_temp_id": file_temp_id,
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        owner_id=user_id,
        job_name=import_payment_plan_fsp_extra_fields_from_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.import_payment_plan_fsp_extra_fields_from_xlsx_async_task_action",
        config=config,
        group_key="payment",
        description=f"Import Payment Plan FSP extra fields xlsx for {payment_plan_id}",
    )


def import_follow_up_instruction_reconciliation_from_xlsx_async_task_action(job: AsyncRetryJob) -> bool:
    from hope.apps.payment.services.payment_list_services import PaymentListService
    from hope.apps.payment.xlsx.xlsx_follow_up_instruction_reconciliation_import_service import (
        XlsxFollowUpInstructionReconciliationImportService,
    )
    from hope.models import FollowUpInstruction

    def _remove_stale_export_file(instruction_id: str, export_file_id: str | None) -> None:
        if export_file_id is None:
            return
        refreshed_instruction = FollowUpInstruction.objects.select_related("export_file").get(id=instruction_id)
        if str(refreshed_instruction.export_file_id) != export_file_id:
            return
        refreshed_instruction.remove_export_file()
        refreshed_instruction.save(update_fields=["export_file", "updated_at"])

    instruction = FollowUpInstruction.objects.select_related(
        "business_area",
        "reconciliation_import_file",
    ).get(id=job.config["follow_up_instruction_id"])
    set_sentry_business_area_tag(instruction.business_area.name)
    export_file_id = str(instruction.export_file_id) if instruction.export_file_id else None

    try:
        file_xlsx = instruction.reconciliation_import_file.file
        service = XlsxFollowUpInstructionReconciliationImportService(instruction, file_xlsx)
        service.open_workbook()
        service.validate()
        if service.errors:
            raise ValidationError([error.message for error in service.errors])
        with transaction.atomic():
            service.import_payment_list(job.config.get("user_id"))
            flow = FollowUpInstructionFlow(instruction)
            flow.background_action_status_none()
            instruction.save(update_fields=["background_action_status", "updated_at"])
            for payment_list in service.payment_lists_to_update.values():
                PaymentListService(payment_list).recalculate_signatures_in_batch()
            transaction.on_commit(lambda: _remove_stale_export_file(str(instruction.id), export_file_id))
    except Exception:
        logger.exception("Unexpected error during Follow Up Instruction reconciliation import")
        flow = FollowUpInstructionFlow(instruction)
        flow.background_action_status_xlsx_import_error()
        instruction.save(update_fields=["background_action_status", "updated_at"])
        raise

    return True


def import_follow_up_instruction_reconciliation_from_xlsx_async_task(
    instruction: FollowUpInstruction,
    user_id: str | None = None,
) -> bool | None:
    instruction_id = str(instruction.id)
    config = {"follow_up_instruction_id": instruction_id, "user_id": user_id}
    AsyncRetryJob.queue_task(
        instance=instruction,
        owner_id=user_id,
        job_name=import_follow_up_instruction_reconciliation_from_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.import_follow_up_instruction_reconciliation_from_xlsx_async_task_action",
        config=config,
        group_key="payment",
        description=f"Import follow up instruction reconciliation from xlsx for {instruction_id}",
    )
    return None


def import_payment_plan_delivery_from_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.core.celery_tasks import NonRetriableTaskError
    from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_import_service import (
        XlsxPaymentPlanDeliveryImportError,
        XlsxPaymentPlanDeliveryImportService,
    )

    payment_plan = PaymentPlan.objects.select_related("cycle__program__business_area").get(
        id=job.config["payment_plan_id"]
    )
    old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
    delivery_import_file_id = job.config.get("delivery_import_file_id") or (payment_plan.delivery_import_file_id)
    delivery_import_file = (
        FileTemp.objects.select_related("created_by").filter(pk=delivery_import_file_id).first()
        if delivery_import_file_id
        else None
    )
    if delivery_import_file is None:
        payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR
        payment_plan.save(update_fields=["background_action_status", "updated_at"])
        log_payment_plan_change(payment_plan, old_payment_plan, job.config.get("user_id"))
        raise NonRetriableTaskError("The reconciliation import file no longer exists.")
    if str(delivery_import_file.object_id) != str(payment_plan.pk):
        raise NonRetriableTaskError("The reconciliation import file does not belong to this Payment Plan.")
    if payment_plan.delivery_import_file_id != delivery_import_file.pk:
        raise NonRetriableTaskError("The reconciliation import was superseded by a newer upload.")
    notification = None

    try:
        notification_user_id = job.config.get("notification_user_id") or delivery_import_file.created_by_id
        notification_user = User.objects.filter(pk=notification_user_id).first()
        notification = (
            PaymentPlanReconciliationImportNotification(
                payment_plan,
                notification_user,
                delivery_import_file.file.name or "reconciliation.xlsx",
            )
            if notification_user
            else None
        )
        file_xlsx = delivery_import_file.file
        saved_options = delivery_import_file.extras
        service = XlsxPaymentPlanDeliveryImportService(
            payment_plan,
            file_xlsx,
            override=job.config.get(OVERRIDE_OPTION, saved_options.get(OVERRIDE_OPTION, False)),
            null_delivery_policy=job.config.get(
                NULL_DELIVERY_POLICY_OPTION,
                saved_options.get(NULL_DELIVERY_POLICY_OPTION, NULL_DELIVERY_POLICY_RESET),
            ),
        )
        service.open_workbook()
        service.import_payment_list(job.config.get("user_id"))
        payment_plan.background_action_status = None
        payment_plan.save(update_fields=["background_action_status", "updated_at"])
        log_payment_plan_change(payment_plan, old_payment_plan, job.config.get("user_id"))
        if notification:
            transaction.on_commit(partial(notification.send_success, **service.get_result_counts()))
    except XlsxPaymentPlanDeliveryImportError as exc:
        payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR
        payment_plan.save(update_fields=["background_action_status", "updated_at"])
        log_payment_plan_change(payment_plan, old_payment_plan, job.config.get("user_id"))
        job.errors = {
            **job.errors,
            "xlsx_errors": [
                {"sheet": error.sheet, "coordinates": error.coordinates, "message": error.message}
                for error in exc.errors
            ],
        }
        job.save(update_fields=["errors"])
        if notification:
            transaction.on_commit(partial(notification.send_background_failure, exc.errors))
        raise NonRetriableTaskError(str(exc)) from exc
    except Exception:
        logger.exception("Import Payment Plan Delivery XLSX Error")
        payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR
        payment_plan.save(update_fields=["background_action_status", "updated_at"])
        log_payment_plan_change(payment_plan, old_payment_plan, job.config.get("user_id"))
        raise


def notify_payment_plan_reconciliation_import_failure(job: AsyncRetryJob, _exception: Exception) -> None:
    payment_plan = PaymentPlan.objects.select_related("cycle__program__business_area").get(
        id=job.config["payment_plan_id"]
    )
    delivery_import_file_id = job.config.get("delivery_import_file_id") or (payment_plan.delivery_import_file_id)
    delivery_import_file = (
        FileTemp.objects.select_related("created_by").filter(pk=delivery_import_file_id).first()
        if delivery_import_file_id
        else None
    )
    notification_user_id = job.config.get("notification_user_id")
    if notification_user_id is None:
        notification_user_id = delivery_import_file.created_by_id if delivery_import_file else job.owner_id
    notification_user = User.objects.filter(pk=notification_user_id).first()
    if notification_user:
        file_name = delivery_import_file.file.name if delivery_import_file else None
        PaymentPlanReconciliationImportNotification(
            payment_plan,
            notification_user,
            file_name or "reconciliation.xlsx",
        ).send_processing_failure()


def import_payment_plan_delivery_from_xlsx_async_task(
    payment_plan: PaymentPlan,
    user_id: str | None = None,
    override: bool = False,
    null_delivery_policy: str = NULL_DELIVERY_POLICY_RESET,
    notification_user_id: str | None = None,
) -> None:
    payment_plan_id = str(payment_plan.id)
    if payment_plan.delivery_import_file_id is None:
        raise ValueError("Payment Plan reconciliation import file is required.")
    config = {
        "payment_plan_id": payment_plan_id,
        "delivery_import_file_id": str(payment_plan.delivery_import_file_id),
        "user_id": user_id,
        "notification_user_id": notification_user_id or user_id,
        OVERRIDE_OPTION: override,
        NULL_DELIVERY_POLICY_OPTION: null_delivery_policy,
        "on_failure_action": ("hope.apps.payment.celery_tasks.notify_payment_plan_reconciliation_import_failure"),
    }
    AsyncRetryJob.queue_task(
        program=payment_plan.cycle.program,
        owner_id=user_id,
        job_name=import_payment_plan_delivery_from_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.import_payment_plan_delivery_from_xlsx_async_task_action",
        instance=payment_plan,
        config=config,
        group_key="payment",
        description=f"Import payment plan delivery from xlsx for {payment_plan_id}",
    )


def payment_list_apply_engine_rule_async_task_action(job: AsyncRetryJob) -> None:  # noqa: PLR0915
    from hope.models import Payment, PaymentList, Rule, RuleCommit, User

    payment_list = get_object_or_404(PaymentList, id=job.config["payment_list_id"])
    set_sentry_business_area_tag(payment_list.business_area.name)
    old_payment_list = cast("PaymentList", copy_model_object(payment_list))
    engine_rule = get_object_or_404(Rule, id=job.config["engine_rule_id"])
    rule: RuleCommit | None = engine_rule.latest
    bulk_size = 1000

    if not rule:
        logger.error("PaymentList Run Engine Rule Error no RuleCommit")
        flow = PaymentListFlow(payment_list)
        flow.background_action_status_steficon_error()
        payment_list.save(update_fields=["background_action_status"])
        return

    if rule.id != payment_list.steficon_rule_id:
        payment_list.steficon_rule = rule
        payment_list.save(update_fields=["steficon_rule"])

    try:
        now = timezone.now()
        qs = payment_list.eligible_payments.select_related(
            "household",
            "household_snapshot",
            "delivery_type",
            "currency",
        )

        pp_currency = payment_list.currency
        pp_exchange_rate = payment_list.exchange_rate
        pp_currency_exchange_date = payment_list.currency_exchange_date

        steficon_user_id = job.config.get("user_id")
        steficon_user = User.objects.filter(pk=steficon_user_id).first() if steficon_user_id else None
        updates_buffer = []
        log_pairs_buffer: list = []
        with transaction.atomic():
            for payment in qs.iterator(chunk_size=bulk_size):
                old_payment = cast("Payment", copy_model_object(payment))
                result = rule.execute({"household": payment.household, "payment_list": payment_list})

                payment.entitlement_quantity = result.value
                payment.entitlement_quantity_usd = get_quantity_in_usd(
                    amount=result.value,
                    currency=pp_currency,
                    exchange_rate=pp_exchange_rate,
                    currency_exchange_date=pp_currency_exchange_date,
                )
                payment.entitlement_date = now
                updates_buffer.append(payment)
                log_pairs_buffer.append((old_payment, payment))

                if len(updates_buffer) >= bulk_size:  # pragma: no cover
                    Payment.signature_manager.bulk_update_with_signature(
                        updates_buffer,
                        ["entitlement_quantity", "entitlement_date", "entitlement_quantity_usd"],
                    )
                    bulk_log_payment_changes(log_pairs_buffer, user=steficon_user)
                    updates_buffer.clear()
                    log_pairs_buffer.clear()

            if updates_buffer:
                Payment.signature_manager.bulk_update_with_signature(
                    updates_buffer,
                    ["entitlement_quantity", "entitlement_date", "entitlement_quantity_usd"],
                )
                bulk_log_payment_changes(log_pairs_buffer, user=steficon_user)

            payment_list.steficon_applied_date = now
            flow = PaymentListFlow(payment_list)
            flow.background_action_status_none()
            with disable_concurrency(payment_list):
                payment_list.remove_export_files()
                payment_list.remove_imported_file()
                payment_list.save()
                payment_list.update_money_fields()
        # invalidate cache for program cycle list
        payment_list.program_cycle.save()
        log_payment_list_change(payment_list, old_payment_list, job.config.get("user_id"))
    except Exception:
        logger.exception("PaymentList Run Engine Rule Error")
        flow = PaymentListFlow(payment_list)
        flow.background_action_status_steficon_error()
        payment_list.save()
        raise


def payment_list_apply_engine_rule_async_task(
    payment_list: PaymentList, engine_rule: Rule, user_id: str | None = None
) -> None:
    payment_list_id = str(payment_list.id)
    engine_rule_id = str(engine_rule.id)
    config = {
        "payment_list_id": payment_list_id,
        "engine_rule_id": engine_rule_id,
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_list,
        owner_id=user_id,
        job_name=payment_list_apply_engine_rule_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_list_apply_engine_rule_async_task_action",
        config=config,
        group_key="payment",
        description=f"Apply engine rule {engine_rule_id} for payment list {payment_list_id}",
    )


def _run_owner_exchange_rate_recalculation(
    job: AsyncRetryJob, owner_model: type[PaymentPlan] | type[FollowUpInstruction]
) -> None:
    from hope.apps.core.celery_tasks import NonRetriableTaskError
    from hope.models import Payment

    with transaction.atomic():
        owner = owner_model.objects.select_for_update(of=("self",)).select_related("currency").get(pk=job.object_id)
        if owner.background_action_status != owner.BackgroundActionStatus.RECALCULATING:
            raise NonRetriableTaskError("The owner recalculation was superseded by another background action")
        plans = list(
            owner.payment_lists.select_related("program_cycle", "payment_plan", "follow_up_instruction").order_by(
                "created_at"
            )
        )
        if not plans:
            owner.background_action_status = None
            owner.save(update_fields=["background_action_status", "updated_at"])
            return
        set_sentry_business_area_tag(owner.business_area.name)
        exchange_date = owner.currency_exchange_date
        rate = owner.exchange_rate
        if job.config["fetch_unore_rate"] and not owner.custom_exchange_rate:
            unore_rate = get_owner_unore_exchange_rate(owner, exchange_date)
            rate = Decimal(str(unore_rate)) if unore_rate is not None else None
        # The exchange-rate feed returns None when it has no rate for this date.
        if rate is None or rate <= 0:
            raise ValueError("A positive exchange rate is required to recalculate owner payments")
        if owner.exchange_rate != rate:
            old_owner = copy_model_object(owner)
            owner.exchange_rate = rate
            owner.save(update_fields=["exchange_rate", "updated_at"])
            owner.refresh_from_db(fields=["exchange_rate"])
            if isinstance(owner, PaymentPlan):
                log_payment_plan_change(owner, cast("PaymentPlan", old_owner), job.config.get("user_id"))
            else:
                log_follow_up_instruction_change(
                    owner, cast("FollowUpInstruction", old_owner), job.config.get("user_id")
                )
        rate = owner.exchange_rate

        bulk_size = 1000
        cycles = {}
        usd_fields = ["entitlement_quantity_usd", "delivered_quantity_usd"]
        for plan in plans:
            updates = []
            for payment in plan.eligible_payments.only("id", "entitlement_quantity", "delivered_quantity").iterator(
                chunk_size=bulk_size
            ):
                payment.entitlement_quantity_usd = get_quantity_in_usd(
                    amount=payment.entitlement_quantity,
                    currency=owner.currency,
                    exchange_rate=rate,
                    currency_exchange_date=exchange_date,
                )
                payment.delivered_quantity_usd = get_quantity_in_usd(
                    amount=payment.delivered_quantity,
                    currency=owner.currency,
                    exchange_rate=rate,
                    currency_exchange_date=exchange_date,
                )
                updates.append(payment)
                if len(updates) >= bulk_size:
                    Payment.objects.bulk_update(updates, usd_fields, batch_size=bulk_size)
                    updates.clear()
            Payment.objects.bulk_update(updates, usd_fields, batch_size=bulk_size)
            plan.update_money_fields()
            cycles[plan.program_cycle_id] = plan.program_cycle
        for cycle in cycles.values():
            cycle.save()
        owner.background_action_status = None
        owner.save(update_fields=["background_action_status", "updated_at"])


def recalculate_owner_exchange_rate_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.core.celery_tasks import NonRetriableTaskError

    owner_model = cast("type[PaymentPlan] | type[FollowUpInstruction]", job.content_type.model_class())
    try:
        _run_owner_exchange_rate_recalculation(job, owner_model)
    except NonRetriableTaskError:
        raise
    except Exception as error:
        with transaction.atomic():
            owner = owner_model.objects.select_for_update().get(pk=job.object_id)
            if owner.background_action_status == owner.BackgroundActionStatus.RECALCULATING:
                owner.background_action_status = owner.BackgroundActionStatus.RECALCULATING_ERROR
                owner.save(update_fields=["background_action_status", "updated_at"])
        raise NonRetriableTaskError(str(error)) from error


def recalculate_owner_exchange_rate_async_task(
    owner: PaymentPlan | FollowUpInstruction, user_id: str | None = None, *, fetch_unore_rate: bool = True
) -> PaymentPlan | FollowUpInstruction:
    config = {
        "user_id": user_id,
        "fetch_unore_rate": fetch_unore_rate,
    }
    with transaction.atomic():
        locked_owner = type(owner).objects.select_for_update().get(pk=owner.pk)
        if locked_owner.background_action_status not in (None, *locked_owner.BACKGROUND_ACTION_ERROR_STATES):
            raise ValidationError("Another owner background action is in progress")
        locked_owner.background_action_status = locked_owner.BackgroundActionStatus.RECALCULATING
        locked_owner.save(update_fields=["background_action_status", "updated_at"])
        AsyncRetryJob.queue_task(
            instance=locked_owner,
            owner_id=user_id,
            job_name=recalculate_owner_exchange_rate_async_task.__name__,
            action="hope.apps.payment.celery_tasks.recalculate_owner_exchange_rate_async_task_action",
            config=config,
            group_key="payment",
            description=f"Recalculate Payment List data for {owner._meta.verbose_name} {owner.pk}",
        )
    return locked_owner


def remove_old_payment_list_xlsx_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import FileTemp, PaymentList

    past_days = int(job.config.get("past_days", 30))
    days = dt.datetime.now() - dt.timedelta(days=past_days)
    file_qs = FileTemp.objects.filter(content_type=get_content_type_for_model(PaymentList), created__lte=days)
    removed_count = file_qs.count()
    if not removed_count:
        return

    for xlsx_obj in file_qs.iterator(chunk_size=1000):
        xlsx_obj.file.delete(save=False)
        xlsx_obj.delete()

    logger.info(f"Removed old FileTemp: {removed_count}")


def remove_old_payment_list_xlsx_async_task(past_days: int = 30) -> None:
    config = {"past_days": past_days}
    AsyncRetryJob.queue_task(
        job_name=remove_old_payment_list_xlsx_async_task.__name__,
        action="hope.apps.payment.celery_tasks.remove_old_payment_list_xlsx_async_task_action",
        config=config,
        group_key="payment",
        description=f"Remove payment list xlsx files older than {past_days} days",
    )


def prepare_payment_list_async_task_action(job: AsyncRetryJob) -> bool:
    from hope.apps.payment.services.payment_list_services import PaymentListService
    from hope.models import PaymentList

    payment_list_id = job.config["payment_list_id"]
    cache_key = generate_cache_key(
        {
            "task_name": "prepare_payment_list_async_task",
            "payment_list_id": payment_list_id,
        }
    )
    if cache.get(cache_key):
        logger.info(f"Task prepare_payment_list_async_task with payment_list_id {payment_list_id} already running.")
        return False

    # 10 hours timeout
    cache.set(cache_key, True, timeout=60 * 60 * 10)
    payment_list = get_object_or_404(PaymentList, id=payment_list_id)

    try:
        if payment_list.status != PaymentList.Status.TP_OPEN:
            logger.info(f"The Payment List must have the status {PaymentList.Status.TP_OPEN}.")
            return False

        with transaction.atomic():
            flow = PaymentListFlow(payment_list)
            flow.build_status_building()
            payment_list.save(update_fields=("build_status", "built_at"))
            set_sentry_business_area_tag(payment_list.business_area.name)

            PaymentListService.create_payments(payment_list)
            payment_list.update_population_count_fields()
            flow.build_status_ok()
            payment_list.save(update_fields=("build_status", "built_at"))
    except Exception:
        flow = PaymentListFlow(payment_list)
        flow.build_status_failed()
        payment_list.save(update_fields=("build_status", "built_at"))
        logger.exception("Prepare Payment List Error")
        raise
    finally:
        cache.delete(cache_key)

    return True


def prepare_payment_list_async_task(payment_list: PaymentList) -> bool | None:
    payment_list_id = str(payment_list.id)
    config = {"payment_list_id": payment_list_id}
    AsyncRetryJob.queue_task(
        instance=payment_list,
        job_name=prepare_payment_list_async_task.__name__,
        action="hope.apps.payment.celery_tasks.prepare_payment_list_async_task_action",
        config=config,
        group_key="payment",
        description=f"Prepare payment list {payment_list_id}",
    )
    return None


def prepare_child_payment_list_async_task_action(job: AsyncRetryJob) -> bool:
    from hope.apps.payment.services.payment_list_services import PaymentListService
    from hope.models import PaymentList

    with transaction.atomic():
        payment_list = PaymentList.all_objects.get(id=job.config["payment_list_id"])
        set_sentry_business_area_tag(payment_list.business_area.name)

        # Lock the source plan so concurrent child-plan copies from the same source
        # run serially — each one then computes its eligible payments on a consistent
        # state instead of racing for the "one child per beneficiary" pool.
        # PaymentListService.delete() takes the same lock, so a concurrent delete of
        # this plan cannot interleave with the copy below.
        if payment_list.source_payment_list_id:
            PaymentList.objects.select_for_update().get(id=payment_list.source_payment_list_id)
            payment_list.refresh_from_db()
        if payment_list.is_removed:
            logger.warning(f"Child payment list {payment_list.id} was deleted before its payments were copied.")
            return True

        fixed_amount = job.config.get("fixed_amount")
        amounts = job.config.get("amounts")
        PaymentListService(payment_list=payment_list).create_child_plan_payments(
            amounts={unicef_id: Decimal(amount) for unicef_id, amount in amounts.items()} if amounts else None,
            fixed_amount=Decimal(fixed_amount) if fixed_amount else None,
        )
        payment_list.refresh_from_db()
        payment_list.update_population_count_fields()
        payment_list.update_money_fields()
        # invalidate cache for program cycle list
        payment_list.program_cycle.save()

        if not payment_list.payment_items.exists():
            # The eligible set was emptied between request-time validation and this
            # copy (e.g. a sibling child plan consumed the same households). Surface
            # the empty plan as failed instead of leaving it silently OPEN.
            payment_list.build_status = PaymentList.BuildStatus.BUILD_STATUS_FAILED
            payment_list.save(update_fields=["build_status", "updated_at"])
            logger.warning(f"Child payment list {payment_list.id} copied zero payments; marked build_status FAILED.")
    return True


def prepare_child_payment_list_async_task(
    payment_list: PaymentList, extra_config: dict[str, Any] | None = None
) -> bool | None:
    """Queue copying of payments for a child plan (follow-up / top-up / top-up amendment).

    ``extra_config`` carries the Top-Up entitlement decision made at creation time: either
    ``{"fixed_amount": "50.00"}`` or ``{"amounts": {payment unicef_id: "50.00", ...}}``.
    """
    payment_list_id = str(payment_list.id)
    config = {"payment_list_id": payment_list_id, **(extra_config or {})}
    AsyncRetryJob.queue_task(
        instance=payment_list,
        job_name=prepare_child_payment_list_async_task.__name__,
        action="hope.apps.payment.celery_tasks.prepare_child_payment_list_async_task_action",
        config=config,
        group_key="payment",
        description=f"Prepare child payment list {payment_list_id}",
    )
    return None


def payment_list_exclude_beneficiaries_async_task_action(job: AsyncRetryJob) -> None:  # noqa: PLR0915
    from django.db.models import Q

    from hope.apps.core.celery_tasks import NonRetriableTaskError
    from hope.models import Payment, PaymentList

    payment_list = PaymentList.objects.select_related("program_cycle__program").get(id=job.config["payment_list_id"])
    excluding_hh_or_ind_ids = list(job.config["excluding_hh_or_ind_ids"])
    exclusion_reason = job.config.get("exclusion_reason", "")
    # for social worker program exclude Individual unicef_id
    is_social_worker_program = payment_list.program_cycle.program.is_social_worker_program
    set_sentry_business_area_tag(payment_list.business_area.name)
    old_payment_list = cast("PaymentList", copy_model_object(payment_list))
    pp_payment_items = payment_list.payment_items.select_related("household")
    error_msg, info_msg = [], []
    filter_key = "household__individuals__unicef_id" if is_social_worker_program else "household__unicef_id"

    try:
        payment_item_ids = set(pp_payment_items.values_list(filter_key, flat=True).distinct())
        missing_ids = [unicef_id for unicef_id in excluding_hh_or_ind_ids if unicef_id not in payment_item_ids]
        info_msg.extend(
            f"Beneficiary with ID {unicef_id} is not part of this Payment List." for unicef_id in missing_ids
        )
        excluding_hh_or_ind_ids = [unicef_id for unicef_id in excluding_hh_or_ind_ids if unicef_id in payment_item_ids]

        # for Locked PaymentList we check if all HHs are not removed from PP
        if (
            payment_list.status == PaymentList.Status.LOCKED
            and len(excluding_hh_or_ind_ids) >= pp_payment_items.count()
        ):
            error_msg.append("Households cannot be entirely excluded from the Payment List.")

        payments_for_undo_exclude = pp_payment_items.filter(excluded=True).exclude(
            **{f"{filter_key}__in": excluding_hh_or_ind_ids}
        )
        undo_exclude_hh_ids = list(payments_for_undo_exclude.values_list(filter_key, flat=True).distinct())

        # check if hard conflicts exists in other Payments for undo exclude HH
        conflicting_undo_ids = set()
        if undo_exclude_hh_ids:
            conflicting_undo_ids = set(
                Payment.objects.exclude(parent__id=payment_list.pk)
                .filter(parent__program_cycle_id=payment_list.program_cycle_id)
                .filter(
                    ~Q(parent__status=PaymentList.Status.OPEN),
                    Q(**{f"{filter_key}__in": undo_exclude_hh_ids}) & Q(conflicted=False),
                )
                .values_list(filter_key, flat=True)
                .distinct()
            )
        error_msg += [
            (
                f"It is not possible to undo exclude Beneficiary with ID {unicef_id} because of hard conflict(s) "
                f"with other Payment List(s)."
            )
            for unicef_id in undo_exclude_hh_ids
            if unicef_id in conflicting_undo_ids
        ]

        payment_list.exclusion_reason = exclusion_reason

        if error_msg:
            flow = PaymentListFlow(payment_list)
            flow.background_action_status_exclude_beneficiaries_error()
            payment_list.exclude_household_error = str([*error_msg, *info_msg])
            payment_list.save(
                update_fields=[
                    "exclusion_reason",
                    "exclude_household_error",
                    "background_action_status",
                ]
            )
            raise ValidationError("Payment List Exclude Beneficiaries Validation Error with Beneficiaries List")

        payments_for_exclude = payment_list.eligible_payments.filter(
            **{f"{filter_key}__in": excluding_hh_or_ind_ids}
        ).distinct()
        restorable_payments = payments_for_undo_exclude.filter(
            status=Payment.STATUS_NOT_ELIGIBLE,
            conflicted=False,
            has_valid_wallet=True,
        )
        user_id = job.config.get("user_id")
        payments_for_exclude.update_and_log(
            {
                "excluded": True,
                "status": Payment.STATUS_NOT_ELIGIBLE,
                "status_date": timezone.now(),
            },
            user_id,
        )
        restorable_payments.update_and_log(
            {
                "excluded": False,
                "status": Payment.STATUS_PENDING,
                "status_date": timezone.now(),
            },
            user_id,
        )
        payments_for_undo_exclude.update_and_log({"excluded": False}, user_id)

        payment_list.update_population_count_fields()
        payment_list.update_money_fields()

        flow = PaymentListFlow(payment_list)
        flow.background_action_status_none()
        payment_list.exclude_household_error = str(info_msg or "")
        payment_list.save(
            update_fields=[
                "exclusion_reason",
                "background_action_status",
                "exclude_household_error",
            ]
        )
        # invalidate cache for program cycle list
        payment_list.program_cycle.save()
        log_payment_list_change(payment_list, old_payment_list, job.config.get("user_id"))
    except Exception as exc:
        logger.exception("Payment List Exclude Beneficiaries Error with excluding method. \n" + str(exc))
        flow = PaymentListFlow(payment_list)
        flow.background_action_status_exclude_beneficiaries_error()

        if error_msg:
            payment_list.exclude_household_error = str([*error_msg, *info_msg])
        else:
            payment_list.exclude_household_error = str([*info_msg, "Exclusion failed due to an unexpected error."])
        payment_list.save(
            update_fields=[
                "exclusion_reason",
                "background_action_status",
                "exclude_household_error",
            ]
        )
        if error_msg:
            return
        raise NonRetriableTaskError(str(exc)) from exc


def payment_list_exclude_beneficiaries_async_task(
    payment_list: PaymentList,
    excluding_hh_or_ind_ids: list[str | None],
    exclusion_reason: str | None = "",
    user_id: str | None = None,
) -> None:
    payment_list_id = str(payment_list.id)
    config = {
        "payment_list_id": payment_list_id,
        "excluding_hh_or_ind_ids": excluding_hh_or_ind_ids,
        "exclusion_reason": exclusion_reason or "",
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_list,
        owner_id=user_id,
        job_name=payment_list_exclude_beneficiaries_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_list_exclude_beneficiaries_async_task_action",
        config=config,
        group_key="payment",
        description=f"Exclude beneficiaries from payment list {payment_list_id}",
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
        payment_plan.save(update_fields=["export_pdf_file_summary", "updated_at"])

        if payment_plan.business_area.enable_email_notification:
            send_email_notification_on_commit(service, user)


def export_pdf_payment_plan_summary_async_task(payment_plan: PaymentPlan, user_id: str) -> None:
    payment_plan_id = str(payment_plan.id)
    AsyncRetryJob.queue_task(
        instance=payment_plan,
        owner_id=user_id,
        job_name=export_pdf_payment_plan_summary_async_task.__name__,
        action="hope.apps.payment.celery_tasks.export_pdf_payment_plan_summary_async_task_action",
        config={"payment_plan_id": payment_plan_id, "user_id": user_id},
        group_key="payment",
        description=f"Export payment plan summary pdf for {payment_plan_id}",
    )


def export_pdf_follow_up_instruction_summary_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import FileTemp, FollowUpInstruction, User

    instruction = FollowUpInstruction.objects.get(id=job.config["follow_up_instruction_id"])
    set_sentry_business_area_tag(instruction.business_area.name)
    user = User.objects.get(pk=job.config["user_id"])

    with transaction.atomic():
        if instruction.export_pdf_file_summary:
            instruction.export_pdf_file_summary.file.delete()
            instruction.export_pdf_file_summary.delete()
            instruction.export_pdf_file_summary = None

        service = FollowUpInstructionPDFExportService(instruction)
        pdf, filename = service.generate_pdf_summary()

        file_pdf_obj = FileTemp(
            object_id=instruction.pk,
            content_type=get_content_type_for_model(instruction),
            created_by=user,
        )
        file_pdf_obj.file.save(filename, ContentFile(pdf))

        instruction.export_pdf_file_summary = file_pdf_obj
        instruction.save(update_fields=["export_pdf_file_summary", "updated_at"])

        if instruction.business_area.enable_email_notification:
            send_email_notification_on_commit(service, user)


def export_pdf_follow_up_instruction_summary_async_task(instruction: FollowUpInstruction, user_id: str) -> None:
    instruction_id = str(instruction.id)
    AsyncRetryJob.queue_task(
        instance=instruction,
        owner_id=user_id,
        job_name=export_pdf_follow_up_instruction_summary_async_task.__name__,
        action="hope.apps.payment.celery_tasks.export_pdf_follow_up_instruction_summary_async_task_action",
        config={"follow_up_instruction_id": instruction_id, "user_id": user_id},
        group_key="payment",
        description=f"Export follow-up instruction summary pdf for {instruction_id}",
    )


def periodic_sync_payment_gateway_fsp_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from hope.apps.payment.services.payment_gateway import PaymentGatewayAPI, PaymentGatewayService

    try:
        PaymentGatewayService().sync_fsps()
    except PaymentGatewayAPI.API_MISSING_CREDENTIALS_EXCEPTION_CLASS:
        return


@app.task()
def periodic_sync_payment_gateway_fsp_async_task() -> None:
    PeriodicAsyncRetryJob.queue_task(
        job_name=periodic_sync_payment_gateway_fsp_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_fsp_async_task_action",
        config={},
        group_key="payment",
        description="Periodic sync payment gateway fsps",
    )


def periodic_sync_payment_gateway_account_types_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from hope.apps.payment.services.payment_gateway import PaymentGatewayAPI, PaymentGatewayService

    try:
        PaymentGatewayService().sync_account_types()
    except PaymentGatewayAPI.API_MISSING_CREDENTIALS_EXCEPTION_CLASS:
        return


@app.task()
def periodic_sync_payment_gateway_account_types_async_task() -> None:
    PeriodicAsyncRetryJob.queue_task(
        job_name=periodic_sync_payment_gateway_account_types_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_account_types_async_task_action",
        config={},
        group_key="payment",
        description="Periodic sync payment gateway account types",
    )


def send_to_payment_gateway_async_task_action(job: AsyncJob) -> None:
    from hope.apps.payment.services.payment_gateway import PaymentGatewayService
    from hope.models import PaymentList, User

    payment_list = PaymentList.objects.get(id=job.config["payment_list_id"])
    user = User.objects.get(pk=job.config["user_id"])

    if payment_list.background_action_status != PaymentList.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY:
        return

    try:
        set_sentry_business_area_tag(payment_list.business_area.name)

        pg_service = PaymentGatewayService(user_id=job.config["user_id"])
        pg_service.create_payment_instructions(payment_list, user.email)
        pg_service.add_records_to_payment_instructions(payment_list)

        flow = PaymentListFlow(payment_list)
        flow.background_action_status_none()
        payment_list.save(update_fields=["background_action_status"])
    except Exception:
        flow = PaymentListFlow(payment_list)
        flow.background_action_status_send_to_payment_gateway_error()
        payment_list.save(update_fields=["background_action_status"])
        raise


def send_to_payment_gateway_async_task(payment_list: PaymentList, user_id: str) -> None:
    payment_list_id = str(payment_list.id)
    config = {
        "payment_list_id": payment_list_id,
        "user_id": user_id,
    }
    AsyncJob.queue_task(
        instance=payment_list,
        owner_id=user_id,
        job_name=send_to_payment_gateway_async_task.__name__,
        action="hope.apps.payment.celery_tasks.send_to_payment_gateway_async_task_action",
        config=config,
        group_key="payment",
        description=f"Send payment list {payment_list_id} to payment gateway",
    )


def periodic_sync_payment_gateway_records_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from hope.apps.payment.services.payment_gateway import PaymentGatewayAPI, PaymentGatewayService

    try:
        PaymentGatewayService().sync_records()
    except PaymentGatewayAPI.API_MISSING_CREDENTIALS_EXCEPTION_CLASS:
        return


@app.task()
def periodic_sync_payment_gateway_records_async_task() -> None:
    PeriodicAsyncRetryJob.queue_task(
        job_name=periodic_sync_payment_gateway_records_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_records_async_task_action",
        config={},
        group_key="payment",
        description="Periodic sync payment gateway records",
    )


def send_payment_notification_emails_async_task_action(job: AsyncJob) -> None:
    from hope.apps.payment.notifications import PaymentNotification
    from hope.models import PaymentList, User

    payment_list = PaymentList.objects.get(id=job.config["payment_list_id"])
    action_user = User.objects.get(id=job.config["action_user_id"])
    set_sentry_business_area_tag(payment_list.business_area.name)
    PaymentNotification(
        payment_list,
        job.config["action"],
        action_user,
        dt.datetime.fromisoformat(job.config["action_date"]),
    ).send_email_notification()


def send_payment_plan_notification_emails_async_task_action(job: AsyncJob) -> None:
    from hope.apps.payment.notifications import PaymentNotification
    from hope.models import PaymentPlan, User

    payment_plan = PaymentPlan.objects.get(id=job.config["payment_plan_id"])
    action_user = User.objects.get(id=job.config["action_user_id"])
    set_sentry_business_area_tag(payment_plan.business_area.name)
    PaymentNotification(
        payment_plan,
        job.config["action"],
        action_user,
        dt.datetime.fromisoformat(job.config["action_date"]),
    ).send_email_notification()


def send_payment_plan_notification_emails_async_task(
    payment_plan: PaymentPlan,
    action: str,
    action_user_id: str,
    action_date: str,
) -> None:
    payment_plan_id = str(payment_plan.id)
    AsyncJob.queue_task(
        instance=payment_plan,
        owner_id=action_user_id,
        job_name=send_payment_plan_notification_emails_async_task.__name__,
        action="hope.apps.payment.celery_tasks.send_payment_plan_notification_emails_async_task_action",
        config={
            "payment_plan_id": payment_plan_id,
            "action": action,
            "action_user_id": action_user_id,
            "action_date": action_date,
        },
        group_key="payment",
        description=f"Send payment notification emails for payment plan {payment_plan_id}",
    )


def send_follow_up_instruction_notification_emails_async_task_action(job: AsyncJob) -> None:
    from hope.apps.payment.notifications import PaymentNotification
    from hope.models import FollowUpInstruction, User

    instruction = FollowUpInstruction.objects.get(id=job.config["follow_up_instruction_id"])
    action_user = User.objects.get(id=job.config["action_user_id"])
    set_sentry_business_area_tag(instruction.business_area.name)
    PaymentNotification(
        instruction,
        job.config["action"],
        action_user,
        dt.datetime.fromisoformat(job.config["action_date"]),
    ).send_email_notification()


def send_follow_up_instruction_notification_emails_async_task(
    instruction: FollowUpInstruction,
    action: str,
    action_user_id: str,
    action_date: str,
) -> None:
    instruction_id = str(instruction.id)
    AsyncJob.queue_task(
        instance=instruction,
        owner_id=action_user_id,
        job_name=send_follow_up_instruction_notification_emails_async_task.__name__,
        action="hope.apps.payment.celery_tasks.send_follow_up_instruction_notification_emails_async_task_action",
        config={
            "follow_up_instruction_id": instruction_id,
            "action": action,
            "action_user_id": action_user_id,
            "action_date": action_date,
        },
        group_key="payment",
        description=f"Send payment notification emails for follow-up instruction {instruction_id}",
    )


def send_payment_notification_emails_async_task(
    payment_list: PaymentList,
    action: str,
    action_user_id: str,
    action_date: str,
) -> None:
    payment_list_id = str(payment_list.id)
    config = {
        "payment_list_id": payment_list_id,
        "action": action,
        "action_user_id": action_user_id,
        "action_date": action_date,
    }
    AsyncJob.queue_task(
        instance=payment_list,
        owner_id=action_user_id,
        job_name=send_payment_notification_emails_async_task.__name__,
        action="hope.apps.payment.celery_tasks.send_payment_notification_emails_async_task_action",
        config=config,
        group_key="payment",
        description=f"Send payment notification emails for {payment_list_id}",
    )


def periodic_sync_payment_gateway_delivery_mechanisms_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from hope.apps.payment.services.payment_gateway import PaymentGatewayAPI, PaymentGatewayService

    try:
        PaymentGatewayService().sync_delivery_mechanisms()
    except PaymentGatewayAPI.API_MISSING_CREDENTIALS_EXCEPTION_CLASS:
        return


@app.task()
def periodic_sync_payment_gateway_delivery_mechanisms_async_task() -> None:
    PeriodicAsyncRetryJob.queue_task(
        job_name=periodic_sync_payment_gateway_delivery_mechanisms_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_delivery_mechanisms_async_task_action",
        config={},
        group_key="payment",
        description="Periodic sync payment gateway delivery mechanisms",
    )


def payment_list_apply_steficon_hh_selection_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import Payment, PaymentList, Rule, RuleCommit

    payment_list = get_object_or_404(PaymentList, id=job.config["payment_list_id"])
    set_sentry_business_area_tag(payment_list.business_area.name)
    old_payment_list = cast("PaymentList", copy_model_object(payment_list))
    engine_rule = get_object_or_404(Rule, id=job.config["engine_rule_id"])
    rule: RuleCommit | None = engine_rule.latest
    if not rule:
        logger.error("PaymentList Run Engine Rule Error no RuleCommit")
        flow = PaymentListFlow(payment_list)
        flow.background_action_status_steficon_error()
        payment_list.save(update_fields=["background_action_status"])
        return

    if rule.id != payment_list.steficon_rule_targeting_id:
        payment_list.steficon_rule_targeting = rule
        payment_list.save(update_fields=["steficon_rule_targeting"])

    try:
        payment_list.status = PaymentList.Status.TP_STEFICON_RUN
        payment_list.steficon_targeting_applied_date = timezone.now()
        payment_list.save(update_fields=["status", "steficon_targeting_applied_date"])
        bulk_size = 1000
        updates = []

        with transaction.atomic():
            for payment in payment_list.payment_items.select_related("household").iterator(chunk_size=bulk_size):
                result = rule.execute({"household": payment.household, "payment_list": payment_list})
                payment.vulnerability_score = normalize_score(result.value)
                updates.append(payment)
                if len(updates) >= bulk_size:
                    Payment.objects.bulk_update(updates, ["vulnerability_score"], batch_size=bulk_size)
                    updates.clear()

            if updates:
                Payment.objects.bulk_update(updates, ["vulnerability_score"], batch_size=bulk_size)

        if payment_list.vulnerability_score_min is not None or payment_list.vulnerability_score_max is not None:
            params = {}
            if payment_list.vulnerability_score_max is not None:
                params["vulnerability_score__lte"] = payment_list.vulnerability_score_max
            if payment_list.vulnerability_score_min is not None:
                params["vulnerability_score__gte"] = payment_list.vulnerability_score_min
            payment_list.payment_items(manager="all_objects").filter(**params).update(is_removed=False)
            payment_list.payment_items(manager="all_objects").exclude(**params).update(is_removed=True)
            payment_list.update_population_count_fields()
            payment_list.update_money_fields()

        payment_list.status = PaymentList.Status.TP_STEFICON_COMPLETED
        payment_list.steficon_targeting_applied_date = timezone.now()
        with disable_concurrency(payment_list):
            payment_list.save(update_fields=["status", "steficon_targeting_applied_date"])
        log_payment_list_change(payment_list, old_payment_list, job.config.get("user_id"))
    except Exception:
        logger.exception("Payment List Apply Steficon HH Selection Error")
        payment_list.steficon_targeting_applied_date = timezone.now()
        payment_list.status = PaymentList.Status.TP_STEFICON_ERROR
        payment_list.save(update_fields=["status", "steficon_targeting_applied_date"])
        raise


def payment_list_apply_steficon_hh_selection_async_task(
    payment_list: PaymentList, engine_rule_id: str, user_id: str | None = None
) -> None:
    payment_list_id = str(payment_list.id)
    config = {
        "payment_list_id": payment_list_id,
        "engine_rule_id": engine_rule_id,
        "user_id": user_id,
    }
    AsyncRetryJob.queue_task(
        instance=payment_list,
        owner_id=user_id,
        job_name=payment_list_apply_steficon_hh_selection_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_list_apply_steficon_hh_selection_async_task_action",
        config=config,
        group_key="payment",
        description=f"Apply steficon hh selection {engine_rule_id} for payment list {payment_list_id}",
    )


def payment_list_rebuild_stats_async_task_action(job: AsyncRetryJob) -> None:
    from hope.models import PaymentList

    payment_list_id = job.config["payment_list_id"]
    with cache.lock(
        f"{PAYMENT_LIST_REBUILD_STATS_LOCK_PREFIX}{payment_list_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        payment_list = get_object_or_404(PaymentList, id=payment_list_id)
        set_sentry_business_area_tag(payment_list.business_area.name)
        flow = PaymentListFlow(payment_list)
        flow.build_status_building()
        payment_list.save(update_fields=("build_status", "built_at"))
        with transaction.atomic():
            payment_list.update_population_count_fields()
            payment_list.update_money_fields()
            flow = PaymentListFlow(payment_list)
            flow.build_status_ok()
            payment_list.save(update_fields=("build_status", "built_at"))


def payment_list_rebuild_stats_async_task(payment_list: PaymentList) -> None:
    payment_list_id = str(payment_list.id)
    config = {"payment_list_id": payment_list_id}
    AsyncRetryJob.queue_task(
        instance=payment_list,
        job_name=payment_list_rebuild_stats_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_list_rebuild_stats_async_task_action",
        config=config,
        group_key="payment",
        description=f"Rebuild payment list stats for {payment_list_id}",
    )


def payment_list_full_rebuild_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.services.payment_list_services import PaymentListService
    from hope.models import PaymentList

    payment_list_id = job.config["payment_list_id"]
    update_money_fields = bool(job.config.get("update_money_fields", False))

    with cache.lock(
        f"{PAYMENT_LIST_FULL_REBUILD_LOCK_PREFIX}{payment_list_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        payment_list = get_object_or_404(PaymentList, id=payment_list_id)
        set_sentry_business_area_tag(payment_list.business_area.name)
        flow = PaymentListFlow(payment_list)
        flow.build_status_building()
        payment_list.save(update_fields=("build_status", "built_at"))
        try:
            with transaction.atomic():
                PaymentListService(payment_list).full_rebuild()
                flow = PaymentListFlow(payment_list)
                flow.build_status_ok()
                payment_list.save(update_fields=("build_status", "built_at"))
                if update_money_fields:
                    payment_list.update_money_fields()
        except Exception:
            logger.exception("Payment list full rebuild failed")
            flow = PaymentListFlow(payment_list)
            flow.build_status_failed()
            payment_list.save(update_fields=("build_status", "built_at"))
            raise


def payment_list_full_rebuild_async_task(payment_list: PaymentList, update_money_fields: bool = False) -> None:
    payment_list_id = str(payment_list.id)
    config = {
        "payment_list_id": payment_list_id,
        "update_money_fields": update_money_fields,
    }
    AsyncRetryJob.queue_task(
        instance=payment_list,
        job_name=payment_list_full_rebuild_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_list_full_rebuild_async_task_action",
        config=config,
        group_key="payment",
        description=f"Full rebuild payment list {payment_list_id}",
    )


def payment_list_refresh_payees_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.services.payment_list_services import PaymentListService
    from hope.apps.payment.services.payment_plan_services import PaymentPlanService
    from hope.models import PaymentList

    payment_list_id = job.config["payment_list_id"]

    with cache.lock(
        f"{PAYMENT_LIST_FULL_REBUILD_LOCK_PREFIX}{payment_list_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        payment_list = get_object_or_404(PaymentList, id=payment_list_id)
        set_sentry_business_area_tag(payment_list.business_area.name)
        if payment_list.status != PaymentList.Status.ABORTED:
            logger.warning(f"Payment list {payment_list_id} is no longer aborted, skipping the payees refresh.")
            return
        old_payment_list = cast("PaymentList", copy_model_object(payment_list))
        flow = PaymentListFlow(payment_list)
        flow.build_status_building()
        payment_list.save(update_fields=("build_status", "built_at"))
        try:
            with transaction.atomic():
                PaymentListService(payment_list).refresh_payees()
                flow = PaymentListFlow(payment_list)
                flow.build_status_ok()
                flow.status_reactivate_abort()
                flow.background_action_status_none()
                payment_list.save(
                    update_fields=(
                        "build_status",
                        "built_at",
                        "status",
                        "status_date",
                        "background_action_status",
                        "updated_at",
                    )
                )
                log_payment_list_change(payment_list, old_payment_list, job.config.get("user_id"))
                if payment_list.payment_plan_id:
                    PaymentPlanService.open_after_payees_refresh(
                        payment_list.payment_plan_id, job.config.get("user_id")
                    )
        except Exception:
            logger.exception("Payment list payees refresh failed")
            flow = PaymentListFlow(payment_list)
            flow.build_status_failed()
            payment_list.save(update_fields=("build_status", "built_at"))
            raise


def mark_payment_list_rebuild_error(job: AsyncRetryJob, _exception: Exception) -> None:
    from hope.apps.payment.services.payment_plan_services import PaymentPlanService
    from hope.models import PaymentList

    payment_list = PaymentList.objects.get(id=job.config["payment_list_id"])
    old_payment_list = cast("PaymentList", copy_model_object(payment_list))
    flow = PaymentListFlow(payment_list)
    flow.background_action_status_rebuild_error()
    payment_list.save(update_fields=("background_action_status", "updated_at"))
    log_payment_list_change(payment_list, old_payment_list, job.config.get("user_id"))
    if payment_list.payment_plan_id:
        PaymentPlanService.mark_rebuild_error(payment_list.payment_plan_id, job.config.get("user_id"))


def payment_list_refresh_payees_async_task(payment_list: PaymentList, user_id: str | None = None) -> None:
    payment_list_id = str(payment_list.id)
    AsyncRetryJob.queue_task(
        instance=payment_list,
        job_name=payment_list_refresh_payees_async_task.__name__,
        action="hope.apps.payment.celery_tasks.payment_list_refresh_payees_async_task_action",
        config={
            "payment_list_id": payment_list_id,
            "user_id": user_id,
            "on_failure_action": "hope.apps.payment.celery_tasks.mark_payment_list_rebuild_error",
        },
        group_key="payment",
        description=f"Refresh payees of reactivated payment list {payment_list_id}",
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
        business_area = payment_verification_plan.payment_list.business_area
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


def periodic_sync_payment_list_invoices_western_union_ftp_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from datetime import datetime, timedelta

    from constance import config

    from hope.apps.payment.services.western_union_reports_service import WesternUnionReportsService

    service = WesternUnionReportsService()
    service.process_files_since(datetime.now() - timedelta(days=config.WU_FTP_SYNC_LOOKBACK_DAYS))


@app.task()
def periodic_sync_payment_list_invoices_western_union_ftp_async_task() -> None:
    PeriodicAsyncRetryJob.queue_task(
        job_name=periodic_sync_payment_list_invoices_western_union_ftp_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_sync_payment_list_invoices_western_union_ftp_async_task_action",
        config={},
        group_key="payment",
        description="Periodic sync payment list invoices western union ftp",
    )


def send_western_union_report_email_notifications_async_task_action(job: AsyncRetryJob) -> None:
    from flags.state import flag_state

    if not bool(flag_state("WU_PAYMENT_LIST_INVOICES_NOTIFICATIONS_ENABLED")):
        return

    from hope.apps.payment.services.western_union_reports_service import WesternUnionReportsService
    from hope.models import WesternUnionPaymentListReport

    report_id = job.config["western_union_report_id"]
    with cache.lock(
        f"{SEND_WESTERN_UNION_REPORT_EMAIL_LOCK_PREFIX}{report_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        report = WesternUnionPaymentListReport.objects.get(id=report_id)
        set_sentry_business_area_tag(report.payment_list.business_area.name)

        service = WesternUnionReportsService()
        service.send_notification_emails(report)
        report.sent = True
        report.save()


def send_western_union_report_email_notifications_async_task(report_id: str) -> None:
    config = {"western_union_report_id": report_id}
    AsyncRetryJob.queue_task(
        job_name=send_western_union_report_email_notifications_async_task.__name__,
        program=WesternUnionPaymentListReport.objects.get(id=report_id).payment_list.program,
        action="hope.apps.payment.celery_tasks.send_western_union_report_email_notifications_async_task_action",
        config=config,
        group_key="payment",
        description=f"Send Western Union report email notifications for {report_id}",
    )


def periodic_send_payment_list_reconciliation_overdue_emails_async_task_action(
    job: AsyncRetryJob | None = None,
) -> None:
    from hope.apps.payment.services.payment_list_services import PaymentListService

    PaymentListService.send_reconciliation_overdue_emails()


@app.task()
def periodic_send_payment_list_reconciliation_overdue_emails_async_task() -> None:
    PeriodicAsyncRetryJob.queue_task(
        job_name=periodic_send_payment_list_reconciliation_overdue_emails_async_task.__name__,
        action="hope.apps.payment.celery_tasks.periodic_send_payment_list_reconciliation_overdue_emails_async_task_action",
        config={},
        group_key="payment",
        description="Periodic send payment list reconciliation overdue emails",
    )


def send_payment_list_reconciliation_overdue_email_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.payment.services.payment_list_services import PaymentListService
    from hope.models import PaymentList

    payment_list_id = job.config["payment_list_id"]
    with cache.lock(
        f"{SEND_PAYMENT_LIST_RECONCILIATION_OVERDUE_EMAIL_LOCK_PREFIX}{payment_list_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        payment_list = get_object_or_404(PaymentList, id=payment_list_id)
        set_sentry_business_area_tag(payment_list.business_area.name)
        service = PaymentListService(payment_list)
        service.send_reconciliation_overdue_email_for_pp()


def send_payment_list_reconciliation_overdue_email_async_task(payment_list: PaymentList) -> None:
    payment_list_id = str(payment_list.id)
    config = {"payment_list_id": payment_list_id}
    AsyncRetryJob.queue_task(
        instance=payment_list,
        job_name=send_payment_list_reconciliation_overdue_email_async_task.__name__,
        action="hope.apps.payment.celery_tasks.send_payment_list_reconciliation_overdue_email_async_task_action",
        config=config,
        group_key="payment",
        description=f"Send payment list reconciliation overdue email for {payment_list_id}",
    )
