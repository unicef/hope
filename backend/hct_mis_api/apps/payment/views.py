import logging
from typing import TYPE_CHECKING, Union

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect

from graphql import GraphQLError

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.models import PaymentPlan, PaymentVerificationPlan
from hct_mis_api.apps.utils.exceptions import log_and_raise

if TYPE_CHECKING:
    from django.http import (
        HttpRequest,
        HttpResponsePermanentRedirect,
        HttpResponseRedirect,
    )

logger = logging.getLogger(__name__)


@login_required
def download_payment_verification_plan(  # type: ignore
    request: "HttpRequest", verification_id: str
) -> Union[
    "HttpResponseRedirect", "HttpResponseRedirect", "HttpResponsePermanentRedirect", "HttpResponsePermanentRedirect"
]:
    payment_verification_plan_id = decode_id_string(verification_id)
    payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=payment_verification_plan_id)
    if not request.user.has_permission(
        Permissions.PAYMENT_VERIFICATION_EXPORT.value, payment_verification_plan.business_area
    ):
        raise PermissionDenied("Permission Denied: User does not have correct permission.")
    if payment_verification_plan.verification_channel != PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX:
        raise GraphQLError("You can only download verification file when XLSX channel is selected")

    if payment_verification_plan.has_xlsx_payment_verification_plan_file:
        if not payment_verification_plan.xlsx_payment_verification_plan_file_was_downloaded:
            xlsx_file = payment_verification_plan.get_xlsx_verification_file
            xlsx_file.was_downloaded = True
            xlsx_file.save()
        return redirect(payment_verification_plan.xlsx_payment_verification_plan_file_link)  # type: ignore # FIXME
    log_and_raise(f"XLSX File not found. PaymentVerificationPlan ID: {payment_verification_plan.unicef_id}")


@login_required
def download_payment_plan_payment_list(  # type: ignore # missing return
    request: "HttpRequest", payment_plan_id: str
) -> Union[
    "HttpResponseRedirect", "HttpResponseRedirect", "HttpResponsePermanentRedirect", "HttpResponsePermanentRedirect"
]:
    payment_plan_id_str = decode_id_string(payment_plan_id)
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id_str)

    if not request.user.has_permission(Permissions.PM_VIEW_LIST.value, payment_plan.business_area):
        raise PermissionDenied("Permission Denied: User does not have correct permission.")

    if payment_plan.status not in (PaymentPlan.Status.LOCKED, PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED):
        raise GraphQLError("Export XLSX is possible only for Payment Plan within status LOCK, ACCEPTED or FINISHED.")

    if payment_plan.has_export_file:
        return redirect(payment_plan.payment_list_export_file_link)  # type: ignore # FIXME

    log_and_raise(f"XLSX File not found. PaymentPlan ID: {payment_plan.unicef_id}")


@login_required
def download_payment_plan_summary_pdf(  # type: ignore # missing return
    request: "HttpRequest", payment_plan_id: str
) -> Union[
    "HttpResponseRedirect", "HttpResponseRedirect", "HttpResponsePermanentRedirect", "HttpResponsePermanentRedirect"
]:
    payment_plan_id_str = decode_id_string(payment_plan_id)
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id_str)

    if not request.user.has_permission(Permissions.PM_VIEW_LIST.value, payment_plan.business_area):
        raise PermissionDenied("Permission Denied: User does not have correct permission.")

    if payment_plan.export_pdf_file_summary and payment_plan.export_pdf_file_summary.file:
        return redirect(payment_plan.export_pdf_file_summary.file.url)

    log_and_raise(f"PDF file not found. PaymentPlan ID: {payment_plan.unicef_id}")
