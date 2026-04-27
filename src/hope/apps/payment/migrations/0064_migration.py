from itertools import islice

from django.db import migrations, models
import django.db.models.deletion

BATCH_SIZE = 2000


def _bulk_create_in_batches(model, objects_iter, ignore_conflicts=False):
    while batch := list(islice(objects_iter, BATCH_SIZE)):
        model.objects.bulk_create(batch, ignore_conflicts=ignore_conflicts)


def create_default_purpose_and_backfill(apps, schema_editor):
    PaymentPlanPurpose = apps.get_model("core", "PaymentPlanPurpose")
    Program = apps.get_model("program", "Program")
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    ProgramCycle = apps.get_model("program", "ProgramCycle")
    PaymentPlanGroup = apps.get_model("payment", "PaymentPlanGroup")

    default_purpose, _ = PaymentPlanPurpose.objects.get_or_create(name="Default Purpose")

    # Programs without any purpose
    ProgramThrough = Program.payment_plan_purposes.through  # noqa: N806
    program_ids_with_purpose = ProgramThrough.objects.values_list("program_id", flat=True)
    _bulk_create_in_batches(
        ProgramThrough,
        (
            ProgramThrough(program_id=pk, paymentplanpurpose_id=default_purpose.id)
            for pk in Program.objects.exclude(id__in=program_ids_with_purpose).values_list("id", flat=True)
        ),
        ignore_conflicts=True,
    )

    # Plans without any purpose
    PlanThrough = PaymentPlan.payment_plan_purposes.through  # noqa: N806
    plan_ids_with_purpose = PlanThrough.objects.values_list("paymentplan_id", flat=True)
    _bulk_create_in_batches(
        PlanThrough,
        (
            PlanThrough(paymentplan_id=pk, paymentplanpurpose_id=default_purpose.id)
            for pk in PaymentPlan.objects.exclude(id__in=plan_ids_with_purpose).values_list("id", flat=True)
        ),
        ignore_conflicts=True,
    )

    # Cycles without a Default Group
    cycle_ids_with_group = PaymentPlanGroup.objects.filter(name="Default Group").values_list("cycle_id", flat=True)
    _bulk_create_in_batches(
        PaymentPlanGroup,
        (
            PaymentPlanGroup(cycle_id=pk, name="Default Group")
            for pk in ProgramCycle.objects.exclude(id__in=cycle_ids_with_group).values_list("id", flat=True)
        ),
    )

    # Ungrouped plans relation to their cycle's Default Group
    default_groups = {
        g.cycle_id: g.id for g in PaymentPlanGroup.objects.filter(name="Default Group").only("id", "cycle_id")
    }
    for cycle_id, group_id in default_groups.items():
        PaymentPlan.objects.filter(program_cycle_id=cycle_id, payment_plan_group__isnull=True).update(
            payment_plan_group_id=group_id
        )


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("core", "0024_migration"),
        ("payment", "0063_migration"),
        ("program", "0019_migration"),
    ]

    operations = [
        migrations.RunPython(
            create_default_purpose_and_backfill,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="paymentplan",
            name="payment_plan_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_plans",
                to="payment.paymentplangroup",
            ),
        ),
    ]
