from itertools import islice

from django.db import migrations

BATCH_SIZE = 2000


def _bulk_create_in_batches(model, objects_iter, ignore_conflicts=False):
    while batch := list(islice(objects_iter, BATCH_SIZE)):
        model.objects.bulk_create(batch, ignore_conflicts=ignore_conflicts)


def migrate_plan_type(apps, schema_editor):
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlan.objects.filter(is_follow_up=True).update(plan_type="FOLLOW_UP")


def create_default_purpose_and_backfill(apps, schema_editor):
    PaymentPlanPurpose = apps.get_model("payment", "PaymentPlanPurpose")  # noqa: N806
    Program = apps.get_model("program", "Program")  # noqa: N806
    PaymentPlan = apps.get_model("payment", "PaymentPlan")  # noqa: N806
    PaymentPlanGroup = apps.get_model("payment", "PaymentPlanGroup")  # noqa: N806

    ProgramThrough = Program.payment_plan_purposes.through  # noqa: N806
    PlanThrough = PaymentPlan.payment_plan_purposes.through  # noqa: N806

    default_purpose, _ = PaymentPlanPurpose.objects.get_or_create(
        name="Default Purpose",
        defaults={"description": "Default payment plan purpose"},
    )

    program_ids_with_purpose = ProgramThrough.objects.values_list("program_id", flat=True)
    _bulk_create_in_batches(
        ProgramThrough,
        (
            ProgramThrough(program_id=pk, paymentplanpurpose_id=default_purpose.id)
            for pk in Program.objects.exclude(id__in=program_ids_with_purpose).values_list("id", flat=True)
        ),
        ignore_conflicts=True,
    )

    plan_ids_with_purpose = PlanThrough.objects.values_list("paymentplan_id", flat=True)
    _bulk_create_in_batches(
        PlanThrough,
        (
            PlanThrough(paymentplan_id=pk, paymentplanpurpose_id=default_purpose.id)
            for pk in PaymentPlan.objects.exclude(id__in=plan_ids_with_purpose).values_list("id", flat=True)
        ),
        ignore_conflicts=True,
    )

    ungrouped_pps = list(
        PaymentPlan.objects.filter(payment_plan_group__isnull=True, is_removed=False).values_list(
            "id", "name", "program_cycle_id"
        )
    )
    _bulk_create_in_batches(
        PaymentPlanGroup,
        (PaymentPlanGroup(cycle_id=cycle_id, name=f"{pp_name} Group") for _, pp_name, cycle_id in ungrouped_pps),
        ignore_conflicts=True,
    )
    cycle_ids = {cycle_id for _, _, cycle_id in ungrouped_pps}
    group_lookup = {
        (g.cycle_id, g.name): g.id
        for g in PaymentPlanGroup.objects.filter(cycle_id__in=cycle_ids).only("id", "cycle_id", "name")
    }
    pps_to_update = [
        PaymentPlan(id=pp_id, payment_plan_group_id=group_lookup[cycle_id, f"{pp_name} Group"])
        for pp_id, pp_name, cycle_id in ungrouped_pps
        if (cycle_id, f"{pp_name} Group") in group_lookup
    ]
    PaymentPlan.objects.bulk_update(pps_to_update, ["payment_plan_group_id"], batch_size=BATCH_SIZE)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("payment", "0068_migration"),
    ]

    operations = [
        migrations.RunPython(migrate_plan_type, migrations.RunPython.noop),
        migrations.RunPython(create_default_purpose_and_backfill, migrations.RunPython.noop),
    ]
