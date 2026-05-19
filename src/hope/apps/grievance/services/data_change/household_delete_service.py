from django.contrib.auth.models import AbstractUser
from rest_framework.exceptions import ValidationError

from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketDeleteHouseholdDetails,
)
from hope.apps.grievance.services.data_change.data_change_service import (
    DataChangeService,
)
from hope.apps.household.services.bulk_withdraw import HouseholdBulkWithdrawService
from hope.models import Household, IndividualRoleInHousehold


class HouseholdDeleteService(DataChangeService):
    def save(self) -> list[GrievanceTicket]:
        data_change_extras = self.extras.get("issue_type")
        household_data_update_issue_type_extras = data_change_extras.get("household_delete_issue_type_extras")
        household = household_data_update_issue_type_extras.get("household")
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

        has_external_collectors = (
            IndividualRoleInHousehold.objects.filter(individual__id__in=individuals)
            .exclude(household=household)
            .exists()
        )
        if has_external_collectors:
            raise ValidationError(
                "One of the Household member is an external collector. This household cannot be withdrawn."
            )

        HouseholdBulkWithdrawService(household.program).withdraw(
            Household.objects.filter(pk=household.pk),
            processed_ticket_id=self.grievance_ticket.id,
        )
