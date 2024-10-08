from django.db import migrations, models
import django.db.models.deletion


def migrate_needs_adjudication_tickets_issue_type(apps, schema_editor):
    GrievanceTicket = apps.get_model("grievance", "GrievanceTicket")

    CATEGORY_NEEDS_ADJUDICATION = 8
    ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY = 24

    GrievanceTicket.objects.filter(category=CATEGORY_NEEDS_ADJUDICATION).update(
        issue_type=ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY
    )


class Migration(migrations.Migration):

    dependencies = [
        ("registration_data", "0038_migration"),
        ("grievance", "0071_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketneedsadjudicationdetails",
            name="dedup_engine_similarity_pair",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="registration_data.deduplicationenginesimilaritypair",
            ),
        ),
        migrations.RunPython(migrate_needs_adjudication_tickets_issue_type, migrations.RunPython.noop),
    ]
