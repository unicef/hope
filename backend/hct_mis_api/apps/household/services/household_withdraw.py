from django.db.models import QuerySet

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Document, Household, Individual


class HouseholdWithdraw:
    def __init__(self, household: Household):
        self.household: Household = household
        self.individuals: QuerySet[Individual] = self.household.individuals.filter(duplicate=False)
        self.documents = None

    def withdraw(self):
        should_withdraw = not self.household.withdrawn
        self._withdraw_household(should_withdraw)
        self._withdraw_individuals(should_withdraw)
        self._withdraw_documents(should_withdraw)

        self.household.save()
        Individual.objects.bulk_update(
            self.individuals,
            (
                "withdrawn",
                "withdrawn_date",
            ),
        )
        Document.objects.bulk_update(self.documents, ("status",))

    def change_tickets_status(self, tickets):
        for ticket in tickets:
            if self.household.withdrawn:
                ticket.ticket.extras["status_before_withdrawn"] = ticket.ticket.status
                ticket.ticket.status = GrievanceTicket.STATUS_CLOSED
            elif ticket.ticket.extras.get("status_before_withdrawn"):
                ticket.ticket.status = ticket.ticket.extras["status_before_withdrawn"]
                ticket.ticket.extras["status_before_withdrawn"] = ""
            ticket.ticket.save()

    def _withdraw_household(self, should_withdraw):
        if should_withdraw:
            self.household.withdraw(False)
        else:
            self.household.unwithdraw(False)

    def _withdraw_individuals(self, should_withdraw):
        for individual in self.individuals:
            if should_withdraw:
                individual.withdraw(False)
            else:
                individual.unwithdraw(False)

    def _withdraw_documents(self, should_withdraw):
        self.documents = Document.objects.filter(individual__household=self.household)
        if should_withdraw:
            self.documents = self.documents.filter(status=Document.STATUS_VALID)
            for document in self.documents:
                document.mark_as_need_investigation()
        else:
            self.documents = self.documents.filter(status=Document.STATUS_NEED_INVESTIGATION)
            for document in self.documents:
                document.mark_as_valid()
