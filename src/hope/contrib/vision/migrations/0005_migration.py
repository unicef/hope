from django.db import migrations, models


def migrate_group_assignments(apps, schema_editor):
    database_alias = schema_editor.connection.alias
    header_model = apps.get_model("vision", "FundsCommitmentHeader")
    old_through = header_model.payment_plans.through
    new_through = header_model.payment_plan_groups.through

    assignments = old_through.objects.using(database_alias)

    group_assignments = assignments.values_list(
        "fundscommitmentheader_id", "paymentplan__payment_plan_group_id"
    ).distinct()
    batch = []
    for header_id, group_id in group_assignments.iterator(chunk_size=1000):
        batch.append(new_through(fundscommitmentheader_id=header_id, paymentplangroup_id=group_id))
        if len(batch) == 1000:
            new_through.objects.using(database_alias).bulk_create(batch, batch_size=1000)
            batch.clear()
    if batch:
        new_through.objects.using(database_alias).bulk_create(batch, batch_size=1000)


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0088_migration"),
        ("vision", "0004_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="fundscommitmentheader",
            name="payment_plan_groups",
            field=models.ManyToManyField(
                blank=True,
                related_name="funds_commitment_headers",
                to="payment.paymentplangroup",
            ),
        ),
        migrations.RunPython(migrate_group_assignments),
        migrations.RemoveField(model_name="fundscommitmentheader", name="payment_plans"),
    ]
