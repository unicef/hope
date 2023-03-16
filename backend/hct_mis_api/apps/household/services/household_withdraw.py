from typing import Any, Iterable, Optional

from django.db import transaction

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household


class HouseholdWithdraw:
    def __init__(self, household: Household) -> None:
        self.household: Household = household
        self.individuals = None

    @transaction.atomic
    def withdraw(self, tag: Optional[Any] = None) -> None:
        self.household.withdraw(tag)

        self.individuals = self.household.individuals.select_for_update().filter(duplicate=False).order_by("pk")
        for individual in self.individuals:
            individual.withdraw()

    @transaction.atomic
    def unwithdraw(self) -> None:
        self.household.unwithdraw()

        self.individuals = self.household.individuals.select_for_update().filter(duplicate=False).order_by("pk")
        for individual in self.individuals:
            individual.unwithdraw()

    def change_tickets_status(self, tickets: Iterable) -> None:
        for ticket in tickets:
            if self.household.withdrawn:
                ticket.ticket.extras["status_before_withdrawn"] = ticket.ticket.status
                ticket.ticket.status = GrievanceTicket.STATUS_CLOSED
            elif ticket.ticket.extras.get("status_before_withdrawn"):
                ticket.ticket.status = ticket.ticket.extras["status_before_withdrawn"]
                ticket.ticket.extras["status_before_withdrawn"] = ""
            ticket.ticket.save()
