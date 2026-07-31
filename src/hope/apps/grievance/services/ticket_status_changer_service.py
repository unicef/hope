from functools import partial
from typing import TYPE_CHECKING, cast
from uuid import UUID

from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.dispatch import Signal

from hope.apps.grievance.events import (
    grievance_assignment_changed,
    grievance_sent_back_to_in_progress,
    grievance_sent_to_approval,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification, send_grievance_notification_event
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
        old_status = self.ticket.status
        old_assigned_to_id = self.ticket.assigned_to_id

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
        self._emit_events(old_status, old_assigned_to_id)

    def _emit_events(self, old_status: int, old_assigned_to_id: UUID | None) -> None:
        if self.ticket.status == GrievanceTicket.STATUS_ASSIGNED and self.ticket.assigned_to_id != old_assigned_to_id:
            self._emit_event(grievance_assignment_changed, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)
        if self.ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL:
            self._emit_event(grievance_sent_to_approval, GrievanceNotification.ACTION_SEND_TO_APPROVAL)
        if (
            old_status == GrievanceTicket.STATUS_FOR_APPROVAL
            and self.ticket.status == GrievanceTicket.STATUS_IN_PROGRESS
        ):
            self._emit_event(
                grievance_sent_back_to_in_progress,
                GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS,
                approver=self.user,
            )

    def _emit_event(self, event: Signal, action: object, **kwargs: object) -> None:
        transaction.on_commit(
            partial(
                send_grievance_notification_event,
                event,
                self.ticket,
                action,
                **kwargs,
            )
        )

    def _can_change_status(self, status: int) -> None:
        if not self.ticket.can_change_status(status):
            log_and_raise("New status is incorrect")

    def _change_status_assigned(self) -> None:
        if not self.ticket.assigned_to:
            self.ticket.assigned_to = cast("User", self.user)
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
