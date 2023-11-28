from hct_mis_api.apps.grievance.models import TicketNeedsAdjudicationDetails

for ticket in TicketNeedsAdjudicationDetails.objects.all():
    ticket.save()
