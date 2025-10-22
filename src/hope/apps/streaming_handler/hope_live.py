from streaming.manager import manager
from streaming.utils import make_event


class HopeLiveService:
    ACTION_RDI_MERGED = "rdi.imported"
    ACTION_PAYMENT_RECONCILED = "payment.reconciled"
    ACTION_PAYMENT_PLAN_APPROVED = "payment_plan.approved"
    ACTION_PROGRAM_OPENED = "program.opened"
    ACTION_PROGRAM_CLOSED = "program.closed"

    def notify(self, event_name: str, data_dict: dict):
        manager.notify(event_name, make_event(data_dict))
