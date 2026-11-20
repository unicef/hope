import logging
from typing import TYPE_CHECKING, Union

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from rest_framework.exceptions import ValidationError

from hope.apps.account.permissions import Permissions
from hope.apps.utils.exceptions import log_and_raise
from hope.models import (
    FollowUpInstruction,
    PaymentList,
    PaymentPlan,
    PaymentVerificationPlan,
    WesternUnionPaymentListReport,
)

if TYPE_CHECKING:  # pragma: no cover
    from django.http import (
        HttpRequest,
        HttpResponse,
        HttpResponsePermanentRedirect,
        HttpResponseRedirect,
    )

logger = logging.getLogger(__name__)


@login_required
def download_payment_verification_plan(
    request: "HttpRequest", verification_id: str
) -> Union[
    "HttpResponseRedirect",
    "HttpResponsePermanentRedirect",
]:
    payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=verification_id)
    if not request.user.has_perm(
        Permissions.PAYMENT_VERIFICATION_EXPORT.value,
        payment_verification_plan.payment_list.program,
    ):
        raise PermissionDenied({"required_permissions": [Permissions.PAYMENT_VERIFICATION_EXPORT.value]})
    if payment_verification_plan.verification_channel != PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX:
        raise ValidationError("You can only download verification file when XLSX channel is selected")

    if not payment_verification_plan.has_xlsx_payment_verification_plan_file:
        log_and_raise(
            f"XLSX File not found. PaymentVerificationPlan ID: {payment_verification_plan.unicef_id}",
            error_type=FileNotFoundError,
        )
    if not payment_verification_plan.xlsx_payment_verification_plan_file_was_downloaded:
        xlsx_file = payment_verification_plan.get_xlsx_verification_file
        xlsx_file.was_downloaded = True
        xlsx_file.save()
    link = payment_verification_plan.xlsx_payment_verification_plan_file_link
    if link is None:
        raise ValueError("Payment verification plan XLSX file link must not be None")
    return redirect(link)


@login_required
def download_payment_list(
    request: "HttpRequest", payment_list_id: str
) -> Union[
    "HttpResponseRedirect",
    "HttpResponseRedirect",
    "HttpResponsePermanentRedirect",
    "HttpResponsePermanentRedirect",
]:
    payment_list = get_object_or_404(PaymentList, id=payment_list_id)

    if not request.user.has_perm(Permissions.PM_VIEW_LIST.value, payment_list.program):
        raise PermissionDenied({"required_permissions": [Permissions.PM_VIEW_LIST.value]})

    if payment_list.status != PaymentList.Status.LOCKED:
        raise ValidationError("Export XLSX is possible only for Payment List within status LOCK.")

    if not payment_list.has_entitlement_file:
        log_and_raise(
            f"XLSX File not found. PaymentList ID: {payment_list.unicef_id}",
            error_type=FileNotFoundError,
        )
    link = payment_list.entitlement_export_file_link
    if link is None:
        raise ValueError("Payment list entitlement export file link must not be None")
    return redirect(link)


@login_required
def download_payment_plan_xlsx(
    request: "HttpRequest", payment_plan_id: str
) -> Union[
    "HttpResponseRedirect",
    "HttpResponsePermanentRedirect",
]:
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)

    if not request.user.has_perm(
        Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX.value,
        payment_plan.cycle.program,
    ):
        raise PermissionDenied({"required_permissions": [Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX.value]})

    link = payment_plan.export_file_link
    if link is None:
        log_and_raise(
            f"XLSX File not found. PaymentPlan ID: {payment_plan.unicef_id}",
            error_type=FileNotFoundError,
        )
    return redirect(link)


@login_required
def download_payment_plan_summary_pdf(request: "HttpRequest", payment_plan_id: str) -> "HttpResponse":
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)

    if not request.user.has_perm(Permissions.PM_EXPORT_PDF_SUMMARY.value, payment_plan.cycle.program):
        raise PermissionDenied({"required_permissions": [Permissions.PM_EXPORT_PDF_SUMMARY.value]})

    export_pdf_file_summary = payment_plan.export_pdf_file_summary
    if not (export_pdf_file_summary and export_pdf_file_summary.file):
        log_and_raise(
            f"PDF file not found. PaymentPlan ID: {payment_plan.unicef_id}",
            error_type=FileNotFoundError,
        )
    return redirect(export_pdf_file_summary.file.url)


@login_required
def download_follow_up_instruction_summary_pdf(request: "HttpRequest", instruction_id: str) -> "HttpResponse":
    instruction = get_object_or_404(FollowUpInstruction, id=instruction_id)

    if not request.user.has_perm(Permissions.PM_EXPORT_PDF_SUMMARY.value, instruction.program):
        raise PermissionDenied({"required_permissions": [Permissions.PM_EXPORT_PDF_SUMMARY.value]})

    export_pdf_file_summary = instruction.export_pdf_file_summary
    if not (export_pdf_file_summary and export_pdf_file_summary.file):
        log_and_raise(
            f"PDF file not found. FollowUpInstruction ID: {instruction.unicef_id}",
            error_type=FileNotFoundError,
        )
    return redirect(export_pdf_file_summary.file.url)


@login_required
def download_follow_up_instruction_xlsx(
    request: "HttpRequest", instruction_id: str
) -> Union[
    "HttpResponseRedirect",
    "HttpResponsePermanentRedirect",
]:
    instruction = get_object_or_404(FollowUpInstruction, id=instruction_id)

    if not request.user.has_perm(Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX.value, instruction.program):
        raise PermissionDenied({"required_permissions": [Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX.value]})

    link = instruction.export_file_link
    if link is None:
        log_and_raise(
            f"XLSX File not found. FollowUpInstruction ID: {instruction.unicef_id}",
            error_type=FileNotFoundError,
        )
    return redirect(link)


@login_required
def download_payment_list_invoice_report_pdf(request: "HttpRequest", report_id: str) -> "HttpResponse":
    report = WesternUnionPaymentListReport.objects.get(id=report_id)
    payment_list = report.payment_list

    if not request.user.has_perm(Permissions.RECEIVE_PARSED_WU_QCF.value, payment_list.program):
        raise PermissionDenied({"required_permissions": [Permissions.RECEIVE_PARSED_WU_QCF.value]})

    return redirect(report.report_file.file.url)
