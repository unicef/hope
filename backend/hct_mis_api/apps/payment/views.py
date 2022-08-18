import logging

from graphql import GraphQLError
from openpyxl.writer.excel import save_virtual_workbook

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportService import XlsxPaymentPlanExportService
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification, PaymentPlan

logger = logging.getLogger(__name__)


@login_required
def download_cash_plan_payment_verification(request, verification_id):
    cash_plan_payment_verification_id = decode_id_string(verification_id)
    cash_plan_payment_verification = get_object_or_404(
        CashPlanPaymentVerification, id=cash_plan_payment_verification_id
    )
    if not request.user.has_permission(
        Permissions.PAYMENT_VERIFICATION_EXPORT.value, cash_plan_payment_verification.business_area
    ):
        logger.error("Permission Denied: User does not have correct permission.")
        raise PermissionDenied("Permission Denied: User does not have correct permission.")
    if cash_plan_payment_verification.verification_channel != CashPlanPaymentVerification.VERIFICATION_CHANNEL_XLSX:
        raise GraphQLError("You can only download verification file when XLSX channel is selected")

    if cash_plan_payment_verification.has_xlsx_cash_plan_payment_verification_file:
        if not cash_plan_payment_verification.xlsx_cashplan_payment_verification_file.was_downloaded:
            cash_plan_payment_verification.xlsx_cashplan_payment_verification_file.was_downloaded = True
            cash_plan_payment_verification.xlsx_cashplan_payment_verification_file.save()
        return redirect(cash_plan_payment_verification.xlsx_cash_plan_payment_verification_file_link)
    else:
        logger.error(f"File not found. CashPlanPaymentVerification ID: {verification_id}")
        raise GraphQLError("File not found")


@login_required
def download_payment_plan_payment_list(request, payment_plan_id):
    payment_plan_id = decode_id_string(payment_plan_id)
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)

    if not request.user.has_permission(
            Permissions.PAYMENT_MODULE_VIEW_LIST.value, payment_plan.business_area
    ):
        logger.error("Permission Denied: User does not have correct permission.")
        raise PermissionDenied("Permission Denied: User does not have correct permission.")

    if payment_plan.has_payment_plan_payment_list_xlsx_file:
        return redirect(payment_plan.xlsx_payment_plan_payment_list_file_link)
    else:
        logger.error(f"File not found. CashPlanPaymentVerification ID: {payment_plan_id}")
        raise GraphQLError("File not found")


@login_required
def download_payment_plan_payment_list_per_fsp(request, payment_plan_id):
    payment_plan_id = decode_id_string(payment_plan_id)
    payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)

    if not request.user.has_permission(
        Permissions.PAYMENT_MODULE_VIEW_LIST.value, payment_plan.business_area
    ):
        logger.error("Permission Denied: User does not have correct permission.")
        raise PermissionDenied("Permission Denied: User does not have correct permission.")

    if payment_plan.status != PaymentPlan.Status.ACCEPTED:
        logger.error("Export XLSX is possible only for Payment Plan within status ACCEPTED.")
        raise GraphQLError("Export XLSX is possible only for Payment Plan within status ACCEPTED.")

    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"payment_plan_payment_list_{payment_plan.unicef_id}.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    service = XlsxPaymentPlanExportService(payment_plan)
    response.write(save_virtual_workbook(service.export_per_fsp()))

    return response
