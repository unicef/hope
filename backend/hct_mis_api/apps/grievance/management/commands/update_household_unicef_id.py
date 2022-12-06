from django.core.management import BaseCommand
from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Coalesce

from hct_mis_api.apps.grievance.models import GrievanceTicket


def update_household_unicef_id() -> int:
    subquery = Subquery(
        GrievanceTicket.objects.annotate(
            hh_unicef_id=Coalesce(
                "complaint_ticket_details__household__unicef_id",
                "sensitive_ticket_details__household__unicef_id",
                "positive_feedback_ticket_details__household__unicef_id",
                "negative_feedback_ticket_details__household__unicef_id",
                "referral_ticket_details__household__unicef_id",
                "individual_data_update_ticket_details__individual__household__unicef_id",
                "add_individual_ticket_details__household__unicef_id",
                "household_data_update_ticket_details__household__unicef_id",
                "delete_individual_ticket_details__individual__household__unicef_id",
                "delete_household_ticket_details__household__unicef_id",
                "system_flagging_ticket_details__golden_records_individual__household__unicef_id",
                "needs_adjudication_ticket_details__golden_records_individual__household__unicef_id",
                "payment_verification_ticket_details__payment_verification__payment_record__household__unicef_id",
                Value(""),
            )
        )
        .filter(pk=OuterRef("pk"))
        .values("hh_unicef_id")[:1]
    )

    updated = 0
    while current_ids := GrievanceTicket.objects.filter(household_unicef_id__isnull=True).values_list("pk", flat=True)[
        :2000
    ]:
        updated += GrievanceTicket.objects.filter(pk__in=current_ids).update(household_unicef_id=subquery)
    return updated


class Command(BaseCommand):
    help = "Update household unicef id"

    def handle(self, *args, **options):
        print("Updating household unicef id")
        updated = update_household_unicef_id()
        print(f"Done - updated {updated}")
