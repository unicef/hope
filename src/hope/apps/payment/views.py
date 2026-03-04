import logging
from typing import TYPE_CHECKING, Union

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from rest_framework.exceptions import ValidationError

from hope.apps.account.permissions import Permissions
from hope.apps.utils.exceptions import log_and_raise
from hope.models import PaymentPlan, PaymentVerificationPlan, WesternUnionPaymentPlanReport

if TYPE_CHECKING:  # pragma: no cover
    from django.http import (
        HttpRequest,
        HttpResponse,
        HttpResponsePermanentRedirect,
        HttpResponseRedirect,
    )

logger = logging.getLogger(__name__)


@login_required
def download_payment_verification_plan(  # type: ignore
    request: "HttpRequest", verification_id: str
) -> Union[
    "HttpResponseRedirect",
    "HttpResponsePermanentRedirect",
]:
    payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=verification_id)
    if not request.user.has_perm(
        Permissions.PAYMENT_VERIFICATION_EXPORT.value,
        payment_verification_plan.business_area,
    ):
        raise PermissionDenied({"required_permissions": [Permissions.PAYMENT_VERIFICATION_EXPORT.value]})
    if payment_verification_plan.verification_channel != PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX:
        raise ValidationError("You can only download verification file when XLSX channel is selected")

    if payment_verification_plan.has_xlsx_payment_verification_plan_file:
        if not payment_verification_plan.xlsx_payment_verification_plan_file_was_downloaded:
            xlsx_file = payment_verification_plan.get_xlsx_verification_file
            xlsx_file.was_downloaded = True
            xlsx_file.save()
        return redirect(payment_verification_plan.xlsx_payment_verification_plan_file_link)  # type: ignore # FIXME
    log_and_raise(
        f"XLSX File not found. PaymentVerificationPlan ID: {payment_verification_plan.unicef_id}",
        error_type=FileNotFoundError,
    )
    return None


@login_required
def download_payment_plan_payment_list(  # type: ignore # missing return
    request: "HttpRequest", payment_plan_id: str
) -> Union[
    "HttpResponseRedirect",
    "HttpResponseRedirect",
    "HttpResponsePermanentRedirect",
    "HttpResponsePermanentRedirect",
]:
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)

    if not request.user.has_perm(Permissions.PM_VIEW_LIST.value, payment_plan.business_area):
        raise PermissionDenied({"required_permissions": [Permissions.PM_VIEW_LIST.value]})

    if payment_plan.status not in (
        PaymentPlan.Status.LOCKED,
        PaymentPlan.Status.ACCEPTED,
        PaymentPlan.Status.FINISHED,
    ):
        raise ValidationError("Export XLSX is possible only for Payment Plan within status LOCK, ACCEPTED or FINISHED.")

    if payment_plan.has_export_file:
        return redirect(payment_plan.payment_list_export_file_link)

    log_and_raise(
        f"XLSX File not found. PaymentPlan ID: {payment_plan.unicef_id}",
        error_type=FileNotFoundError,
    )
    return None


@login_required
def download_payment_plan_summary_pdf(  # type: ignore # missing return
    request: "HttpRequest", payment_plan_id: str
) -> Union[
    "HttpResponseRedirect",
    "HttpResponseRedirect",
    "HttpResponsePermanentRedirect",
    "HttpResponsePermanentRedirect",
]:
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)

    if not request.user.has_perm(Permissions.PM_EXPORT_PDF_SUMMARY.value, payment_plan.business_area):
        raise PermissionDenied({"required_permissions": [Permissions.PM_EXPORT_PDF_SUMMARY.value]})

    if payment_plan.status not in (
        PaymentPlan.Status.IN_REVIEW,
        PaymentPlan.Status.ACCEPTED,
        PaymentPlan.Status.FINISHED,
    ):  # pragma: no cover
        raise ValidationError("Export PDF is possible only for Payment Plan within status IN_REVIEW/ACCEPTED/FINISHED.")

    if payment_plan.export_pdf_file_summary and payment_plan.export_pdf_file_summary.file:
        return redirect(payment_plan.export_pdf_file_summary.file.url)

    log_and_raise(
        f"PDF file not found. PaymentPlan ID: {payment_plan.unicef_id}",
        error_type=FileNotFoundError,
    )
    return None


@login_required
def download_payment_plan_invoice_report_pdf(request: "HttpRequest", report_id: str) -> "HttpResponse":
    report = WesternUnionPaymentPlanReport.objects.get(id=report_id)
    payment_plan = report.payment_plan

    if not request.user.has_perm(Permissions.RECEIVE_PARSED_WU_QCF.value, payment_plan.program):
        raise PermissionDenied({"required_permissions": [Permissions.RECEIVE_PARSED_WU_QCF.value]})

    return redirect(report.report_file.file.url)
