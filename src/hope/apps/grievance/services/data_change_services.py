import logging

from django.contrib.auth.models import AbstractUser

from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.data_change.add_individual_service import (
    AddIndividualService,
)
from hope.apps.grievance.services.data_change.data_change_service import (
    DataChangeService,
)
from hope.apps.grievance.services.data_change.household_data_update_service import (
    HouseholdDataUpdateService,
)
from hope.apps.grievance.services.data_change.household_delete_service import (
    HouseholdDeleteService,
)
from hope.apps.grievance.services.data_change.individual_data_update_service import (
    IndividualDataUpdateService,
)
from hope.apps.grievance.services.data_change.individual_delete_service import (
    IndividualDeleteService,
)

logger = logging.getLogger(__name__)


class InvalidIssueTypeError(Exception):
    pass


ISSUE_TYPE_SERVICE_MAP: dict[int, type[DataChangeService]] = {
    GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL: AddIndividualService,
    GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE: IndividualDataUpdateService,
    GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE: HouseholdDataUpdateService,
    GrievanceTicket.ISSUE_TYPE_UPDATE_DELEGATE: HouseholdDataUpdateService,
    GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL: IndividualDeleteService,
    GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD: HouseholdDeleteService,
}


def get_service(grievance_ticket: GrievanceTicket, extras: dict) -> DataChangeService:
    service_class = ISSUE_TYPE_SERVICE_MAP.get(grievance_ticket.issue_type)
    if service_class is None:
        raise InvalidIssueTypeError("Invalid issue type")
    return service_class(grievance_ticket, extras)


def save_data_change_extras(grievance_ticket: GrievanceTicket, extras: dict) -> list[GrievanceTicket]:
    service = get_service(grievance_ticket, extras)
    return service.save()


def update_data_change_extras(grievance_ticket: GrievanceTicket, extras: dict, input_data: dict) -> GrievanceTicket:
    service = get_service(grievance_ticket, extras)
    return service.update()


def close_data_change_ticket_service(grievance_ticket: GrievanceTicket, user: AbstractUser) -> None:
    service = get_service(grievance_ticket, {})
    service.close(user)
