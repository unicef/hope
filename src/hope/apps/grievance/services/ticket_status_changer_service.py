from typing import TYPE_CHECKING, cast

from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.data_change_services import (
    close_data_change_ticket_service,
)
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    close_needs_adjudication_ticket_service,
)
from hope.apps.grievance.services.payment_verification_services import (
    update_payment_verification_service,
)
from hope.apps.grievance.services.system_ticket_service import (
    close_system_flagging_ticket_service,
)
from hope.apps.utils.exceptions import log_and_raise

if TYPE_CHECKING:
    from hope.models import User


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
            self.ticket.assigned_to = cast("User", self.user)
            self.ticket.assigned_at = timezone.now()
            self.ticket.assigned_by = cast("User", self.user)
        self.ticket.status = GrievanceTicket.STATUS_ASSIGNED

    def _change_status_in_progress(self) -> None:
        self.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS

    def _change_status_on_hold(self) -> None:
        self.ticket.status = GrievanceTicket.STATUS_ON_HOLD

    def _change_status_for_approval(self) -> None:
        self._validate_biometrics_photo_assigned()
        self.ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL

    def _validate_biometrics_photo_assigned(self) -> None:
        # A rerouted biometric photo-fix ticket is created with an empty photo value; the
        # operator must upload a valid photo before the ticket can proceed to approval.
        if self.ticket.issue_type != GrievanceTicket.ISSUE_TYPE_BIOMETRICS_PHOTO:
            return
        details = self.ticket.individual_data_update_ticket_details
        photo = (details.individual_data or {}).get("photo", {})
        if not photo.get("value"):
            log_and_raise("A valid photo must be uploaded before this ticket can be sent for approval")

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
