from django.utils import timezone

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household, Individual


class HouseholdWithdraw:
    def execute(self, household: Household, tickets):
        withdrawn = not household.withdrawn
        household.withdrawn_date = timezone.now() if withdrawn else None
        household.withdrawn = withdrawn

        individuals_ids = list(household.individuals.values_list("id", flat=True))

        individuals = []

        for individual in Individual.objects.filter(id__in=individuals_ids, duplicate=False):
            individual.withdrawn = withdrawn
            individual.save()
            individuals.append(individual)

        for ticket in tickets:
            if withdrawn:
                ticket.ticket.extras["status_before_withdrawn"] = ticket.ticket.status
                ticket.ticket.status = GrievanceTicket.STATUS_CLOSED
            elif ticket.ticket.extras.get("status_before_withdrawn"):
                ticket.ticket.status = ticket.ticket.extras["status_before_withdrawn"]
                ticket.ticket.extras["status_before_withdrawn"] = ""
            ticket.ticket.save()

        household.save()

        return household, individuals
