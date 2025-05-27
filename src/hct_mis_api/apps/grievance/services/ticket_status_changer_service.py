from django.contrib.auth.models import AbstractUser

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.data_change_services import (
    close_data_change_ticket_service,
)
from hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services import (
    close_needs_adjudication_ticket_service,
)
from hct_mis_api.apps.grievance.services.payment_verification_services import (
    update_payment_verification_service,
)
from hct_mis_api.apps.grievance.services.system_ticket_service import (
    close_system_flagging_ticket_service,
)
from hct_mis_api.apps.utils.exceptions import log_and_raise


class TicketStatusChangerService:
    def __init__(self, ticket: GrievanceTicket, user: AbstractUser) -> None:
        self.ticket = ticket
        self.user = user

    def change_status(self, status: int) -> None:
        self._can_change_status(status)

        if status == GrievanceTicket.STATUS_ASSIGNED:
            self._change_status_assigned()
        elif status == GrievanceTicket.STATUS_IN_PROGRESS:
            self._change_status_in_progress()
        elif status == GrievanceTicket.STATUS_ON_HOLD:
            self._change_status_on_hold()
        elif status == GrievanceTicket.STATUS_FOR_APPROVAL:
            self._change_status_for_approval()
        elif status == GrievanceTicket.STATUS_CLOSED:
            self._change_status_closed()
        self.ticket.save()

    def _can_change_status(self, status: int) -> None:
        if not self.ticket.can_change_status(status):
            log_and_raise("New status is incorrect")

    def _change_status_assigned(self) -> None:
        if not self.ticket.assigned_to:
            self.ticket.assigned_to = self.user
        self.ticket.status = GrievanceTicket.STATUS_ASSIGNED

    def _change_status_in_progress(self) -> None:
        self.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS

    def _change_status_on_hold(self) -> None:
        self.ticket.status = GrievanceTicket.STATUS_ON_HOLD

    def _change_status_for_approval(self) -> None:
        self.ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL

    def _change_status_closed(self) -> None:
        self.ticket.status = GrievanceTicket.STATUS_CLOSED

        if self.ticket.category == GrievanceTicket.CATEGORY_DATA_CHANGE:
            close_data_change_ticket_service(self.ticket, self.user)
        elif self.ticket.category == GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION:
            update_payment_verification_service(self.ticket, self.user)
        elif self.ticket.category == GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION:
            close_needs_adjudication_ticket_service(self.ticket, self.user)
        elif self.ticket.category == GrievanceTicket.CATEGORY_SYSTEM_FLAGGING:
            close_system_flagging_ticket_service(self.ticket, self.user)
