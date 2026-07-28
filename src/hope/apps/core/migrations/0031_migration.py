from django.db import migrations, models


def set_collects_individual_data(apps, schema_editor):
    DataCollectingType = apps.get_model("core", "DataCollectingType")
    DataCollectingType.objects.filter(recalculate_composition=True).update(collects_individual_data=True)


def reverse_set_collects_individual_data(apps, schema_editor):
    DataCollectingType = apps.get_model("core", "DataCollectingType")
    DataCollectingType.objects.update(collects_individual_data=False)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0030_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="datacollectingtype",
            name="recalculate_composition",
            field=models.BooleanField(
                default=False,
                help_text="When enabled, household composition counters (age/gender disaggregation, size, "
                "children counts) are automatically recalculated from linked individuals data",
            ),
        ),
        migrations.AlterField(
            model_name="datacollectingtype",
            name="weight",
            field=models.PositiveSmallIntegerField(
                default=0, help_text="Ordering weight: types with a higher weight are listed first"
            ),
        ),
        migrations.AddField(
            model_name="datacollectingtype",
            name="collects_individual_data",
            field=models.BooleanField(
                default=False,
                help_text="Whether this data collecting type registers individual members data; "
                "when enabled, known affected beneficiaries may be derived by counting linked individuals",
            ),
        ),
        migrations.RunPython(set_collects_individual_data, reverse_set_collects_individual_data),
    ]
