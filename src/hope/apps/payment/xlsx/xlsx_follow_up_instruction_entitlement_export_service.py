from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hope.apps.payment.xlsx.xlsx_follow_up_instruction_base_export_service import (
    XlsxFollowUpInstructionBaseExportService,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_export_service import XlsxPaymentPlanExportService

if TYPE_CHECKING:
    from hope.models import FollowUpInstruction, Payment


class XlsxFollowUpInstructionEntitlementExportService(XlsxFollowUpInstructionBaseExportService):
    def __init__(self, instruction: "FollowUpInstruction") -> None:
        self.payment_plan_export_service: XlsxPaymentPlanExportService | None = None
        super().__init__(instruction)

    @property
    def filename_prefix(self) -> str:
        return "follow_up_instruction_entitlement_payment_list"

    def get_source_headers(self) -> list[str]:
        self.payment_plan_export_service = XlsxPaymentPlanExportService(self.payment_plan)
        return list(self.payment_plan_export_service.headers)

    def get_payment_row_data(self, payment: Payment) -> dict[str, Any]:
        if self.payment_plan_export_service is None:
            raise ValueError("Payment Plan entitlement export service is not initialized.")
        return dict(
            zip(
                self.payment_plan_export_service.headers,
                self.payment_plan_export_service.get_payment_row(payment),
                strict=True,
            )
        )
