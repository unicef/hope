import logging
from typing import Dict, List

from django.contrib.auth.models import AbstractUser

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.data_change.add_individual_service import (
    AddIndividualService,
)
from hct_mis_api.apps.grievance.services.data_change.data_change_service import (
    DataChangeService,
)
from hct_mis_api.apps.grievance.services.data_change.household_data_update_service import (
    HouseholdDataUpdateService,
)
from hct_mis_api.apps.grievance.services.data_change.household_delete_service import (
    HouseholdDeleteService,
)
from hct_mis_api.apps.grievance.services.data_change.individual_dalete_service import (
    IndividualDeleteService,
)
from hct_mis_api.apps.grievance.services.data_change.individual_data_update_service import (
    IndividualDataUpdateService,
)

logger = logging.getLogger(__name__)


class InvalidIssueTypeError(Exception):
    pass


def get_service(grievance_ticket: GrievanceTicket, extras: Dict) -> DataChangeService:
    issue_type = grievance_ticket.issue_type
    if issue_type == GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL:
        return AddIndividualService(grievance_ticket, extras)
    if issue_type == GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE:
        return IndividualDataUpdateService(grievance_ticket, extras)
    if issue_type == GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE:
        return HouseholdDataUpdateService(grievance_ticket, extras)
    if issue_type == GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL:
        return IndividualDeleteService(grievance_ticket, extras)
    if issue_type == GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD:
        return HouseholdDeleteService(grievance_ticket, extras)
    raise InvalidIssueTypeError("Invalid issue type")


def save_data_change_extras(grievance_ticket: GrievanceTicket, extras: Dict) -> List[GrievanceTicket]:
    service = get_service(grievance_ticket, extras)
    return service.save()


def update_data_change_extras(grievance_ticket: GrievanceTicket, extras: Dict, input_data: Dict) -> GrievanceTicket:
    service = get_service(grievance_ticket, extras)
    return service.update()


def close_data_change_ticket_service(grievance_ticket: GrievanceTicket, user: AbstractUser) -> None:
    service = get_service(grievance_ticket, {})
    service.close(user)
