from django.db import migrations, models
import django.db.models.deletion


def assign_targeting_criteria_for_all_payment_plans(apps, schema_editor):
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    TargetingCriteria = apps.get_model("targeting", "TargetingCriteria")
    payment_plan_qs = PaymentPlan.objects.filter(targeting_criteria__isnull=True)
    for payment_plan in payment_plan_qs:
        payment_plan.targeting_criteria = TargetingCriteria.objects.create()
        payment_plan.save()

class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0012_migration'),
    ]

    operations = [
        migrations.RunPython(assign_targeting_criteria_for_all_payment_plans, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='paymentplan',
            name='target_population',
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='targeting_criteria',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='payment_plan',
                                       to='targeting.targetingcriteria'),
        ),
    ]
