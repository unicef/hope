from typing import List

from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketDeleteIndividualDetails,
)
from hct_mis_api.apps.grievance.services.data_change.data_change_service import (
    DataChangeService,
)
from hct_mis_api.apps.grievance.services.reassign_roles_services import (
    reassign_roles_on_disable_individual_service,
)
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.household.services.household_recalculate_data import (
    recalculate_data,
)


class IndividualDeleteService(DataChangeService):
    def save(self) -> List[GrievanceTicket]:
        data_change_extras = self.extras.get("issue_type")
        individual_data_update_issue_type_extras = data_change_extras.get("individual_delete_issue_type_extras")
        individual_encoded_id = individual_data_update_issue_type_extras.get("individual")
        individual_id = decode_id_string(individual_encoded_id)
        individual = get_object_or_404(Individual, id=individual_id)
        ticket_individual_data_update_details = TicketDeleteIndividualDetails(
            individual=individual,
            ticket=self.grievance_ticket,
        )
        ticket_individual_data_update_details.save()
        self.grievance_ticket.refresh_from_db()
        return [self.grievance_ticket]

    def update(self) -> GrievanceTicket:
        return self.grievance_ticket

    def close(self, user: AbstractUser) -> None:
        ticket_details = self.grievance_ticket.ticket_details

        if not ticket_details or ticket_details.approve_status is False:
            return
        household = None
        details = self.grievance_ticket.ticket_details
        individual_to_remove = details.individual
        if individual_to_remove.household:
            household = individual_to_remove.household
        individual_to_remove = Individual.objects.select_for_update().get(id=individual_to_remove.id)
        old_individual_to_remove = Individual.objects.get(id=individual_to_remove.id)
        household_to_remove = reassign_roles_on_disable_individual_service(
            individual_to_remove, details.role_reassign_data, user
        )
        individual_to_remove.withdraw()
        log_create(
            Individual.ACTIVITY_LOG_MAPPING, "business_area", user, old_individual_to_remove, individual_to_remove
        )
        household_to_remove.refresh_from_db()
        if household_to_remove.active_individuals.count() == 0:
            household_to_remove.withdraw()
        if household:
            recalculate_data(household)
