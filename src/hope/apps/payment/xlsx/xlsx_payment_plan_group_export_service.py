from collections.abc import Iterable
import logging
from typing import TYPE_CHECKING

from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_export_base_service import XlsxPaymentPlanExportBaseService
from hope.models import PaymentPlan

if TYPE_CHECKING:
    from hope.models import PaymentPlanGroup

logger = logging.getLogger(__name__)


class XlsxPaymentPlanGroupExportService(XlsxPaymentPlanExportBaseService, XlsxExportBaseService):
    TITLE = "Payment Plan Group - Payment List"
    FILENAME_PREFIX = "payment_plan_group"
    EXPORT_FILE_FIELD = "export_file"

    def __init__(self, payment_plan_group: "PaymentPlanGroup") -> None:
        self.payment_plan_group = payment_plan_group
        self.payment_plans = list(
            payment_plan_group.payment_plans.filter(status=PaymentPlan.Status.LOCKED).order_by("unicef_id")
        )
        super().__init__()

    @property
    def is_social_worker_program(self) -> bool:
        return self.payment_plan_group.cycle.program.is_social_worker_program

    def _payment_plans(self) -> Iterable[PaymentPlan]:
        return self.payment_plans

    def _export_instance(self) -> "PaymentPlanGroup":
        return self.payment_plan_group
