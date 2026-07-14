from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hope.apps.payment.xlsx.xlsx_follow_up_instruction_base_export_service import (
    XlsxFollowUpInstructionBaseExportService,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_export_service import (
    XlsxPaymentPlanDeliveryExportService,
)

if TYPE_CHECKING:
    from hope.models import FollowUpInstruction, Payment


class XlsxFollowUpInstructionDeliveryExportService(XlsxFollowUpInstructionBaseExportService):
    def __init__(self, instruction: "FollowUpInstruction") -> None:
        self.payment_plan_delivery_export_service: XlsxPaymentPlanDeliveryExportService | None = None
        super().__init__(instruction)

    @property
    def filename_prefix(self) -> str:
        return "follow_up_instruction_delivery_payment_list"

    def get_source_headers(self) -> list[str]:
        self.payment_plan_delivery_export_service = XlsxPaymentPlanDeliveryExportService(self.payment_plan, None)
        fsp = self.payment_plan.financial_service_provider
        delivery_mechanism = self.payment_plan.delivery_mechanism
        if fsp is None or delivery_mechanism is None:
            raise ValueError("Child Payment Plans must define Financial Service Provider and Delivery Mechanism.")
        fsp_xlsx_template = self.payment_plan_delivery_export_service.get_template(fsp, delivery_mechanism)
        if fsp_xlsx_template is None:
            raise ValueError("FSP XLSX template not found for child Payment Plan delivery export.")
        return self.payment_plan_delivery_export_service.prepare_headers(fsp_xlsx_template)

    def get_payment_row_data(self, payment: Payment) -> dict[str, Any]:
        if self.payment_plan_delivery_export_service is None:
            raise ValueError("Payment Plan delivery export service is not initialized.")
        return dict(
            zip(
                self.payment_plan_delivery_export_service.header_list,
                self.payment_plan_delivery_export_service.get_payment_row(payment),
                strict=True,
            )
        )
