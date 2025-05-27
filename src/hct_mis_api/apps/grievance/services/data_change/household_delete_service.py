from typing import List

from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.shortcuts import get_object_or_404

from graphql import GraphQLError

from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketDeleteHouseholdDetails,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.grievance.services.data_change.data_change_service import (
    DataChangeService,
)
from hct_mis_api.apps.household.models import Household, IndividualRoleInHousehold
from hct_mis_api.apps.household.services.household_withdraw import HouseholdWithdraw


class HouseholdDeleteService(DataChangeService):
    def save(self) -> List[GrievanceTicket]:
        data_change_extras = self.extras.get("issue_type")
        household_data_update_issue_type_extras = data_change_extras.get("household_delete_issue_type_extras")
        household_encoded_id = household_data_update_issue_type_extras.get("household")
        household_id = decode_id_string(household_encoded_id)
        household = get_object_or_404(Household, id=household_id)
        ticket_household_data_update_details = TicketDeleteHouseholdDetails(
            household=household,
            ticket=self.grievance_ticket,
        )
        ticket_household_data_update_details.save()
        self.grievance_ticket.refresh_from_db()
        return [self.grievance_ticket]

    def update(self) -> GrievanceTicket:
        return self.grievance_ticket

    def close(self, user: AbstractUser) -> None:
        ticket_details = self.grievance_ticket.ticket_details
        if not ticket_details or ticket_details.approve_status is False:
            return

        household = Household.objects.select_for_update().get(id=ticket_details.household.id)
        individuals = household.individuals.values_list("id", flat=True)

        external_collectors_count = (
            IndividualRoleInHousehold.objects.filter(individual__id__in=individuals)
            .exclude(household=household)
            .count()
        )
        if external_collectors_count:
            raise GraphQLError(
                "One of the Household member is an external collector. This household cannot be withdrawn."
            )

        tickets = TicketNeedsAdjudicationDetails.objects.filter(
            Q(selected_individual__in=individuals) | Q(golden_records_individual__in=individuals)
        ).exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)

        service = HouseholdWithdraw(household)
        service.withdraw()
        service.change_tickets_status(tickets)
