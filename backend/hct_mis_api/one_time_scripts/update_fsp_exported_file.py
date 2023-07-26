from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
    XlsxPaymentPlanExportPerFspService,
)


def update_fsp_exported_file() -> None:
    payment_plans = PaymentPlan.objects.filter(
        status__in=(PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED), export_file_per_fsp__isnull=False
    ).select_related("export_file_per_fsp", "export_file_per_fsp__created_by")
    for payment_plan in payment_plans:
        user = payment_plan.export_file_per_fsp.created_by
        service = XlsxPaymentPlanExportPerFspService(payment_plan)
        service.export_per_fsp(user)
