# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from openpyxl.writer.excel import save_virtual_workbook

from payment.xlsx.XlsxVerificationExportService import XlsxVerificationExportService
from payment.models import CashPlanPaymentVerification


@login_required
def download_cash_plan_payment_verification(request, verification_id):
    mimetype = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = "payment_verification.xlsx"
    response = HttpResponse(content_type=mimetype)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    service = XlsxVerificationExportService(
        get_object_or_404(CashPlanPaymentVerification, id=verification_id)
    )
    response.write(
        save_virtual_workbook(service.generate_workbook())
    )

    return response
