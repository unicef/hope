# Generated manually

from django.db import migrations, models


def transfer_targeting_criteria_data(apps, schema_editor):  # pragma no cover
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    for plan in PaymentPlan.objects.filter(targeting_criteria__isnull=False):
        criteria = plan.targeting_criteria
        plan.flag_exclude_if_active_adjudication_ticket = criteria.flag_exclude_if_active_adjudication_ticket
        plan.flag_exclude_if_on_sanction_list = criteria.flag_exclude_if_on_sanction_list
        plan.save()

    # Update ForeignKey relationships from rules to payment plans
    TargetingCriteriaRule = apps.get_model("targeting", "TargetingCriteriaRule")
    for rule in TargetingCriteriaRule.objects.all():
        if hasattr(rule.targeting_criteria, "payment_plan"):
            rule.payment_plan = rule.targeting_criteria.payment_plan
            rule.save()


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0037_migration"),
        ("targeting", "0005_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentplan",
            name="flag_exclude_if_active_adjudication_ticket",
            field=models.BooleanField(
                default=False,
                help_text="Exclude households with individuals (members or collectors) that have active adjudication ticket(s).",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="flag_exclude_if_on_sanction_list",
            field=models.BooleanField(
                default=False,
                help_text="Exclude households with individuals (members or collectors) on sanction list.",
            ),
        ),
        migrations.RunPython(transfer_targeting_criteria_data, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="paymentplan",
            name="targeting_criteria",
        ),
    ]
