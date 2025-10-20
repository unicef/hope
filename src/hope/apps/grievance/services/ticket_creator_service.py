import abc

from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from hope.apps.accountability.models import Feedback
from hope.apps.activity_log.models import log_create
from hope.apps.core.models import BusinessArea
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketSensitiveDetails,
)
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.grievance.services.data_change_services import save_data_change_extras
from hope.apps.grievance.services.payment_verification_services import (
    update_payment_verification_service,
)
from hope.apps.grievance.services.referral_services import save_referral_service
from hope.apps.grievance.services.ticket_based_on_payment_record_services import (
    create_tickets_based_on_payment_records_service,
)
from hope.apps.grievance.utils import create_grievance_documents
from hope.apps.grievance.validators import validate_grievance_documents_size


class TicketDetailsCreator(abc.ABC):
    @abc.abstractmethod
    def create(self, grievance_ticket: GrievanceTicket, extras: dict) -> list[GrievanceTicket]:
        pass


class PaymentVerificationTicketDetailsCreator(TicketDetailsCreator):
    def create(self, grievance_ticket: GrievanceTicket, extras: dict) -> list[GrievanceTicket]:
        return update_payment_verification_service(grievance_ticket)


class DataChangeTicketDetailsCreator(TicketDetailsCreator):
    def create(self, grievance_ticket: GrievanceTicket, extras: dict) -> list[GrievanceTicket]:
        return save_data_change_extras(grievance_ticket, extras)


class GrievanceComplaintTicketDetailsCreator(TicketDetailsCreator):
    def create(self, grievance_ticket: GrievanceTicket, extras: dict) -> list[GrievanceTicket]:
        details = extras.get("category", {}).get("grievance_complaint_ticket_extras", {})
        return create_tickets_based_on_payment_records_service(grievance_ticket, details, TicketComplaintDetails)


class SensitiveGrievanceTicketDetailsCreator(TicketDetailsCreator):
    def create(self, grievance_ticket: GrievanceTicket, extras: dict) -> list[GrievanceTicket]:
        details = extras.get("category", {}).get("sensitive_grievance_ticket_extras", {})
        return create_tickets_based_on_payment_records_service(grievance_ticket, details, TicketSensitiveDetails)


class ReferralTicketDetailsCreator(TicketDetailsCreator):
    def create(self, grievance_ticket: GrievanceTicket, extras: dict) -> list[GrievanceTicket]:
        return save_referral_service(grievance_ticket, extras)


class InvalidCategoryError(Exception):
    pass


class TicketDetailsCreatorFactory:
    @staticmethod
    def get_for_category(category: int | None) -> TicketDetailsCreator:
        if category == GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION:
            return PaymentVerificationTicketDetailsCreator()
        if category == GrievanceTicket.CATEGORY_DATA_CHANGE:
            return DataChangeTicketDetailsCreator()
        if category == GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT:
            return GrievanceComplaintTicketDetailsCreator()
        if category == GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE:
            return SensitiveGrievanceTicketDetailsCreator()
        if category == GrievanceTicket.CATEGORY_REFERRAL:
            return ReferralTicketDetailsCreator()
        raise InvalidCategoryError("Invalid category")


class TicketCreatorService:
    def __init__(self, details_creator: TicketDetailsCreator):
        self._details_creator = details_creator

    def create(self, user: AbstractUser, business_area: BusinessArea, input_data: dict) -> list[GrievanceTicket]:
        documents = input_data.pop("documentation", None)
        extras = input_data.pop("extras", {})
        linked_tickets = input_data.pop("linked_tickets", [])
        linked_feedback = input_data.pop("linked_feedback_id", None)
        linked_feedback_id = None
        if linked_feedback:
            linked_feedback_id = linked_feedback.id
        grievance_ticket = self._create_ticket(business_area, input_data, user)

        self._assign_to_feedback(grievance_ticket, linked_feedback_id)
        self._assign_linked_tickets(grievance_ticket, linked_tickets)
        self._create_documents(documents, grievance_ticket, user)

        grievances = self._create_details(extras, grievance_ticket)

        GrievanceNotification.send_all_notifications(
            GrievanceNotification.prepare_notification_for_ticket_creation(grievance_ticket)
        )

        for grievance in grievances:
            log_create(
                GrievanceTicket.ACTIVITY_LOG_MAPPING,
                "business_area",
                user,
                grievance_ticket.programs.all(),
                None,
                grievance,
            )
        return grievances

    def _create_details(self, extras: dict, grievance_ticket: GrievanceTicket) -> list[GrievanceTicket]:
        return self._details_creator.create(grievance_ticket, extras)

    def _create_documents(
        self,
        documents: list[dict],
        grievance_ticket: GrievanceTicket,
        user: AbstractUser,
    ) -> None:
        if not documents:
            return
        validate_grievance_documents_size(grievance_ticket.id, documents)
        create_grievance_documents(user, grievance_ticket, documents)

    def _assign_linked_tickets(self, grievance_ticket: GrievanceTicket, linked_tickets: list[str]) -> None:
        grievance_ticket.linked_tickets.set(linked_tickets)

    def _assign_to_feedback(self, grievance_ticket: GrievanceTicket, linked_feedback_id: str) -> None:
        if not linked_feedback_id:
            return
        linked_feedback = Feedback.objects.get(id=linked_feedback_id)
        linked_feedback.linked_grievance = grievance_ticket
        linked_feedback.save()

    def _create_ticket(self, business_area: BusinessArea, input_data: dict, user: AbstractUser) -> GrievanceTicket:
        partner = input_data.pop("partner", None)
        assigned_to = input_data.pop("assigned_to", None)
        admin = input_data.pop("admin", None)
        program = input_data.pop("program", None)

        new_ticket = GrievanceTicket.objects.create(
            **input_data,
            admin2=admin,
            business_area=business_area,
            created_by=user,
            user_modified=timezone.now(),
            assigned_to=assigned_to,
            status=GrievanceTicket.STATUS_ASSIGNED if assigned_to else GrievanceTicket.STATUS_NEW,
            partner=partner,
        )
        if program:
            new_ticket.programs.add(program)

        return new_ticket
