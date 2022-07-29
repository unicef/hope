from django.core.management import BaseCommand

from hct_mis_api.apps.household.models import DISABLED, NOT_DISABLED
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.core.models import BusinessArea


# for copying & pasting into the terminal purposes
# there's this business_area filter
# additional kwargs go to GrievanceTicket filter
def fix_disability_fields(business_area=None, **kwargs):
    def _logic(ba):
        print(f"Fixing disability fields for {ba}")
        tickets = GrievanceTicket.objects.filter(business_area=ba, **kwargs)
        for ticket in tickets:
            details = ticket.individual_data_update_ticket_details
            if not details:
                continue
            data = details.individual_data
            if not data:
                continue
            disability = data.get("disability", None)
            if not disability:
                continue
            disability_value = disability.get("value", None)
            if disability_value is not None:
                new_disability_value = None
                if disability_value is True:
                    new_disability_value = DISABLED
                elif disability_value is False:
                    new_disability_value = NOT_DISABLED
                if new_disability_value is not None:
                    print(
                        f"Found ticket (id={ticket.id}) with disability: '{disability_value}'. Changing to '{new_disability_value}'"
                    )
                    ticket.individual_data_update_ticket_details.individual_data["disability"][
                        "value"
                    ] = new_disability_value
                    ticket.save()

    if business_area:
        return _logic(business_area)

    for _business_area in BusinessArea.objects.all():
        _logic(_business_area)


class Command(BaseCommand):
    help = "Go through all grievance tickets, look for wrongly formatted data and fix it"

    def handle(self, *args, **options):
        print("Fixing grievance tickets")

        fix_disability_fields()  # PR #1608
