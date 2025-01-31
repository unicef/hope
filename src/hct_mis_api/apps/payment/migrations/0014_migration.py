from django.db import migrations, models
import django.db.models.deletion
import django_fsm


def assign_targeting_criteria_for_all_payment_plans(apps, schema_editor):
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    TargetingCriteria = apps.get_model("targeting", "TargetingCriteria")
    payment_plan_qs = PaymentPlan.objects.filter(targeting_criteria__isnull=True)
    for payment_plan in payment_plan_qs:
        payment_plan.targeting_criteria = TargetingCriteria.objects.create()
        payment_plan.save()

class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0013_migration'),
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
        migrations.AlterField(
            model_name='paymentplan',
            name='status',
            field=django_fsm.FSMField(
                choices=[('TP_OPEN', 'Open'), ('TP_LOCKED', 'Locked'), ('PROCESSING', 'Processing'),
                         ('STEFICON_WAIT', 'Steficon Wait'), ('STEFICON_RUN', 'Steficon Run'),
                         ('STEFICON_COMPLETED', 'Steficon Completed'), ('STEFICON_ERROR', 'Steficon Error'),
                         ('DRAFT', 'Draft'), ('PREPARING', 'Preparing'), ('OPEN', 'Open'), ('LOCKED', 'Locked'),
                         ('LOCKED_FSP', 'Locked FSP'), ('IN_APPROVAL', 'In Approval'),
                         ('IN_AUTHORIZATION', 'In Authorization'), ('IN_REVIEW', 'In Review'), ('ACCEPTED', 'Accepted'),
                         ('FINISHED', 'Finished')], db_index=True, default='TP_OPEN', max_length=50),
        ),
    ]