from typing import Any, Callable

from constance import config
from streaming.manager import manager
from streaming.utils import make_event

from hope.apps.payment.models import Payment, PaymentPlan
from hope.apps.program.models import Program
from hope.apps.registration_data.models import RegistrationDataImport


class HopeLiveService:
    ACTION_RDI_MERGED = "rdi.imported"
    ACTION_PAYMENT_RECONCILED = "payment.reconciled"
    ACTION_PAYMENT_PLAN_APPROVED = "payment_plan.approved"
    ACTION_PROGRAM_OPENED = "program.opened"
    ACTION_PROGRAM_CLOSED = "program.closed"

    @property
    def payload_builders(self) -> dict[str, Callable[[Any], dict]]:
        return {
            self.ACTION_RDI_MERGED: self._payload_rdi_merged,
            self.ACTION_PAYMENT_RECONCILED: self._payload_payment_reconciled,
            self.ACTION_PAYMENT_PLAN_APPROVED: self._payload_payment_plan_approved,
            self.ACTION_PROGRAM_OPENED: self._payload_program_opened,
            self.ACTION_PROGRAM_CLOSED: self._payload_program_closed,
        }

    def _payload_rdi_merged(self, instance: RegistrationDataImport) -> dict:
        return {
            "business_area": instance.business_area.slug,
            "program": instance.program.name,
            "number_of_hh": instance.number_of_households,
            "number_of_beneficiaries": instance.number_of_individuals,
        }

    def _payload_payment_reconciled(self, instance: Payment) -> dict:
        return {
            "business_area": instance.business_area.slug,
            "program": instance.program.name,
            "amount": instance.delivered_quantity_usd,
            "household_admin_area": instance.household.admin_area.name,
        }

    def _payload_payment_plan_approved(self, instance: PaymentPlan) -> dict:
        return {
            "business_area": instance.business_area.slug,
            "program": instance.program.name,
            "amount": instance.total_entitled_quantity_usd,
            # "household_admin_area": "", TODO bulk send all payments?
        }

    def _payload_program_opened(self, instance: Program) -> dict:
        return {
            "business_area": instance.business_area.slug,
            "program": instance.name,
        }

    def _payload_program_closed(self, instance: Program) -> dict:
        return {
            "business_area": instance.business_area.slug,
            "program": instance.name,
            "number_of_beneficiaries": instance.individual_count,
            "total_amount_paid": instance.get_total_amount_paid()["delivered_quantity_usd"],
        }

    def get_payload(self, event_name: str, obj: Any) -> dict[str, Any]:
        try:
            builder = self.payload_builders[event_name]
        except KeyError:
            raise ValueError(f"Unsupported event: {event_name}")
        return builder(obj)

    def notify(self, event_name: str, obj: Any) -> None:
        if config.STREAMING_HANDLER_ENABLED:
            manager.notify(event_name, make_event(self.get_payload(event_name, obj)))
