from django.contrib.auth.models import AbstractUser

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.reassign_roles_services import (
    reassign_roles_on_disable_individual_service,
)
from hct_mis_api.apps.household.models import Individual


def close_system_flagging_ticket_service(grievance_ticket: GrievanceTicket, user: AbstractUser) -> None:
    ticket_details = grievance_ticket.ticket_details

    if not ticket_details:
        return

    individual = ticket_details.golden_records_individual
    old_individual = copy_model_object(individual)

    if ticket_details.approve_status is False:
        individual.sanction_list_possible_match = False
        individual.save()
    else:
        individual.sanction_list_confirmed_match = True
        individual.save()
        reassign_roles_on_disable_individual_service(
            individual, ticket_details.role_reassign_data, user, grievance_ticket.programme
        )
    log_create(
        Individual.ACTIVITY_LOG_MAPPING,
        "business_area",
        user,
        getattr(grievance_ticket.programme, "pk", None),
        old_individual,
        individual,
    )
