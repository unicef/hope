from collections.abc import Iterable
import logging

from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_export_base_service import XlsxPaymentPlanExportBaseService
from hope.models import PaymentPlan

logger = logging.getLogger(__name__)


class XlsxPaymentPlanExportService(XlsxPaymentPlanExportBaseService, XlsxExportBaseService):
    FILENAME_PREFIX = "payment_plan_payment_list"
    EXPORT_FILE_FIELD = "export_file_entitlement"

    def __init__(self, payment_plan: PaymentPlan):
        self.payment_plan = payment_plan
        super().__init__()

    @property
    def is_social_worker_program(self) -> bool:
        return self.payment_plan.is_social_worker_program

    def _payment_plans(self) -> Iterable[PaymentPlan]:
        return [self.payment_plan]

    def _export_instance(self) -> PaymentPlan:
        return self.payment_plan
