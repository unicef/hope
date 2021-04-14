import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from openpyxl.writer.excel import save_virtual_workbook

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification
from hct_mis_api.apps.payment.xlsx.XlsxVerificationExportService import XlsxVerificationExportService

logger = logging.getLogger(__name__)


@login_required
def download_cash_plan_payment_verification(request, verification_id):
    cash_plan_payment_verification = get_object_or_404(
        CashPlanPaymentVerification, id=decode_id_string(verification_id)
    )
    if not request.user.has_permission(
        Permissions.PAYMENT_VERIFICATION_EXPORT.value, cash_plan_payment_verification.business_area
    ):
        logger.error("Permission Denied: User does not have correct permission.")
        raise PermissionDenied("Permission Denied: User does not have correct permission.")

    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = "payment_verification.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    service = XlsxVerificationExportService(cash_plan_payment_verification)
    response.write(save_virtual_workbook(service.generate_workbook()))

    return response
