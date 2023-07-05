import abc
from typing import Dict, List, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404
from django.utils import timezone

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import (
    decode_and_get_object,
    decode_id_string,
    decode_id_string_required,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketSensitiveDetails,
)
from hct_mis_api.apps.grievance.notifications import GrievanceNotification
from hct_mis_api.apps.grievance.services.data_change_services import (
    save_data_change_extras,
)
from hct_mis_api.apps.grievance.services.payment_verification_services import (
    update_payment_verification_service,
)
from hct_mis_api.apps.grievance.services.referral_services import save_referral_service
from hct_mis_api.apps.grievance.services.ticket_based_on_payment_record_services import (
    create_tickets_based_on_payment_records_service,
)
from hct_mis_api.apps.grievance.utils import create_grievance_documents
from hct_mis_api.apps.grievance.validators import validate_grievance_documents_size
from hct_mis_api.apps.program.models import Program


class TicketDetailsCreator(abc.ABC):
    @abc.abstractmethod
    def create(self, grievance_ticket: GrievanceTicket, extras: Dict) -> List[GrievanceTicket]:
        pass


class PaymentVerificationTicketDetailsCreator(TicketDetailsCreator):
    def create(self, grievance_ticket: GrievanceTicket, extras: Dict) -> List[GrievanceTicket]:
        return update_payment_verification_service(grievance_ticket)


class DataChangeTicketDetailsCreator(TicketDetailsCreator):
    def create(self, grievance_ticket: GrievanceTicket, extras: Dict) -> List[GrievanceTicket]:
        return save_data_change_extras(grievance_ticket, extras)


class GrievanceComplaintTicketDetailsCreator(TicketDetailsCreator):
    def create(self, grievance_ticket: GrievanceTicket, extras: Dict) -> List[GrievanceTicket]:
        details = extras.get("category", {}).get("grievance_complaint_ticket_extras", {})
        return create_tickets_based_on_payment_records_service(grievance_ticket, details, TicketComplaintDetails)


class SensitiveGrievanceTicketDetailsCreator(TicketDetailsCreator):
    def create(self, grievance_ticket: GrievanceTicket, extras: Dict) -> List[GrievanceTicket]:
        details = extras.get("category", {}).get("sensitive_grievance_ticket_extras", {})
        return create_tickets_based_on_payment_records_service(grievance_ticket, details, TicketSensitiveDetails)


class ReferralTicketDetailsCreator(TicketDetailsCreator):
    def create(self, grievance_ticket: GrievanceTicket, extras: Dict) -> List[GrievanceTicket]:
        return save_referral_service(grievance_ticket, extras)


class InvalidCategoryError(Exception):
    pass


class TicketDetailsCreatorFactory:
    @staticmethod
    def get_for_category(category: Optional[int]) -> TicketDetailsCreator:
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

    def create(self, user: AbstractUser, business_area: BusinessArea, input_data: Dict) -> List[GrievanceTicket]:
        documents = input_data.pop("documentation", None)
        extras = input_data.pop("extras", {})
        linked_tickets = [decode_id_string_required(encoded_id) for encoded_id in input_data.pop("linked_tickets", [])]
        linked_feedback_id = input_data.pop("linked_feedback_id", None)

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

    def _create_details(self, extras: Dict, grievance_ticket: GrievanceTicket) -> List[GrievanceTicket]:
        return self._details_creator.create(grievance_ticket, extras)

    def _create_documents(self, documents: List[Dict], grievance_ticket: GrievanceTicket, user: AbstractUser) -> None:
        if not documents:
            return
        validate_grievance_documents_size(grievance_ticket.id, documents)
        create_grievance_documents(user, grievance_ticket, documents)

    def _assign_linked_tickets(self, grievance_ticket: GrievanceTicket, linked_tickets: List[str]) -> None:
        grievance_ticket.linked_tickets.set(linked_tickets)

    def _assign_to_feedback(self, grievance_ticket: GrievanceTicket, linked_feedback_id: str) -> None:
        if not linked_feedback_id:
            return
        linked_feedback = Feedback.objects.get(id=linked_feedback_id)
        linked_feedback.linked_grievance = grievance_ticket
        linked_feedback.save()

    def _create_ticket(self, business_area: BusinessArea, input_data: Dict, user: AbstractUser) -> GrievanceTicket:
        partner = decode_and_get_object(input_data.pop("partner", None), Partner, False)
        assigned_to = decode_and_get_object(input_data.pop("assigned_to", None), get_user_model(), False)
        admin = input_data.pop("admin", None)
        program = input_data.pop("program", None)

        if admin:
            admin = get_object_or_404(Area, p_code=admin)

        if program:
            program = get_object_or_404(Program, pk=decode_id_string(program))

        new_ticket = GrievanceTicket.objects.create(
            **input_data,
            admin2=admin,
            business_area=business_area,
            created_by=user,
            user_modified=timezone.now(),
            assigned_to=assigned_to,
            status=GrievanceTicket.STATUS_ASSIGNED,
            partner=partner,
        )
        new_ticket.programs.add(program)

        return new_ticket
