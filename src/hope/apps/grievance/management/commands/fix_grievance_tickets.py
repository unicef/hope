import logging
from typing import Any

from django.core.management import BaseCommand
from django.db import transaction

from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import DISABLED, NOT_DISABLED
from hope.models import BusinessArea, Individual


def _map_disability_value(value: Any) -> str | None:
    if value is True:
        return DISABLED
    if value is False:
        return NOT_DISABLED
    return None


def _fix_disability_fields_for_ba(ba: BusinessArea, **kwargs: Any) -> None:
    logging.info(f"Fixing disability fields for {ba}")
    tickets = GrievanceTicket.objects.filter(
        business_area=ba,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type__in=[
            GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        ],
        **kwargs,
    )
    for ticket in tickets:
        try:
            details = ticket.individual_data_update_ticket_details
        except GrievanceTicket.individual_data_update_ticket_details.RelatedObjectDoesNotExist:
            continue
        data = details.individual_data
        if not data:
            continue
        disability = data.get("disability", None)
        if not disability:
            continue
        disability_value = disability.get("value", None)
        if disability_value is None:
            continue
        new_disability_value = _map_disability_value(disability_value)
        if new_disability_value is not None:
            logging.info(
                f"Found ticket (id={ticket.id}) with disability: '{disability_value}'. "
                f"Changing to '{new_disability_value}'"
            )
            ticket.individual_data_update_ticket_details.individual_data["disability"]["value"] = new_disability_value
            ticket.individual_data_update_ticket_details.save()


# for copying & pasting into the terminal purposes
# there's this business_area filter
# additional kwargs go to GrievanceTicket filter
@transaction.atomic
def fix_disability_fields(business_area: BusinessArea | None = None, **kwargs: Any) -> None:
    if business_area:
        return _fix_disability_fields_for_ba(business_area, **kwargs)

    for _business_area in BusinessArea.objects.all():
        _fix_disability_fields_for_ba(_business_area, **kwargs)

    Individual.objects.filter(disability="False").update(disability=NOT_DISABLED)
    Individual.objects.filter(disability="True").update(disability=DISABLED)
    return None


class Command(BaseCommand):
    help = "Go through all grievance tickets, look for wrongly formatted data and fix it"

    def handle(self, *args: Any, **options: Any) -> None:
        fix_disability_fields()  # PR #1608
