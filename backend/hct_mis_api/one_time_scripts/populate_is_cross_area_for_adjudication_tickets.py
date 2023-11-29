from hct_mis_api.apps.grievance.models import TicketNeedsAdjudicationDetails


def populate_is_cross_area_for_adjudication_tickets() -> None:
    for ticket in TicketNeedsAdjudicationDetails.objects.all():
        ticket.populate_cross_area_flag()
