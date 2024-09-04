from django.core.paginator import Paginator
from django.db import migrations, models
import django.db.models.deletion


def migrate_needs_adjudication_tickets_issue_type(apps, schema_editor):
    GrievanceTicket = apps.get_model("grievance", "GrievanceTicket")
    TicketNeedsAdjudicationDetails = apps.get_model("grievance", "TicketNeedsAdjudicationDetails")

    ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY = 24

    qs_tickets = (
        TicketNeedsAdjudicationDetails.objects.filter(ticket__issue_type__isnull=True)
        .select_related("ticket")
        .order_by("id")
    )
    gt_to_update = []

    paginator = Paginator(qs_tickets, 500)
    for page in paginator.page_range:
        for ticket in paginator.page(page).object_list:
            issue_type = ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY
            gt = ticket.ticket
            gt.issue_type = issue_type
            gt_to_update.append(gt)

        GrievanceTicket.objects.bulk_update(gt_to_update, ["issue_type"])
        gt_to_update = []


class Migration(migrations.Migration):

    dependencies = [
        ("registration_data", "0038_migration"),
        ("grievance", "0071_migration"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(migrate_needs_adjudication_tickets_issue_type, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="ticketneedsadjudicationdetails",
                    name="dedup_engine_similarity_pair",
                    field=models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="registration_data.deduplicationenginesimilaritypair",
                    ),
                ),
            ],
        ),
    ]
