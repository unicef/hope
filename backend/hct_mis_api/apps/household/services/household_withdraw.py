from django.db import transaction

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household


class HouseholdWithdraw:
    def __init__(self, household: Household) -> None:
        self.household: Household = household
        self.documents = None

    @transaction.atomic
    def withdraw(self, tag=None) -> None:
        self.household.withdraw(tag)

        for individual in self.household.individuals.select_for_update().filter(duplicate=False):
            individual.withdraw()

    @transaction.atomic
    def unwithdraw(self) -> None:
        self.household.unwithdraw()

        for individual in self.household.individuals.select_for_update().filter(duplicate=False):
            individual.unwithdraw()

    def change_tickets_status(self, tickets) -> None:
        for ticket in tickets:
            if self.household.withdrawn:
                ticket.ticket.extras["status_before_withdrawn"] = ticket.ticket.status
                ticket.ticket.status = GrievanceTicket.STATUS_CLOSED
            elif ticket.ticket.extras.get("status_before_withdrawn"):
                ticket.ticket.status = ticket.ticket.extras["status_before_withdrawn"]
                ticket.ticket.extras["status_before_withdrawn"] = ""
            ticket.ticket.save()
