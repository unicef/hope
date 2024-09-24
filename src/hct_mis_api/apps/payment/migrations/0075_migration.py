# Generated by Django 3.2.15 on 2022-09-23 18:56

from django.db import migrations
from django.db.models import OuterRef, Subquery


def update_payment_verification_fk(apps, schema_editor):
    PaymentVerificationPlan = apps.get_model("payment", "PaymentVerificationPlan")
    PaymentVerificationSummary = apps.get_model("payment", "PaymentVerificationSummary")
    CashPlan = apps.get_model("payment", "CashPlan")
    ContentType = apps.get_model("contenttypes", "ContentType")

    content_type_for_cash_plan = ContentType.objects.get_for_model(CashPlan)

    subquery_pvp = Subquery(
        PaymentVerificationPlan.objects
        .filter(pk=OuterRef("pk"))
        .values("cash_plan_id")[:1]
    )
    subquery_summary = Subquery(
        PaymentVerificationSummary.objects
        .filter(pk=OuterRef("pk"))
        .values("cash_plan_id")[:1]
    )

    PaymentVerificationPlan.objects.all().update(
        payment_plan_content_type_id=content_type_for_cash_plan.id,
        payment_plan_object_id=subquery_pvp,
    )
    PaymentVerificationSummary.objects.all().update(
        payment_plan_content_type_id=content_type_for_cash_plan.id,
        payment_plan_object_id=subquery_summary,
    )


def update_payment_record_fk(apps, schema_editor):
    PaymentVerification = apps.get_model("payment", "PaymentVerification")
    PaymentRecord = apps.get_model("payment", "PaymentRecord")
    ContentType = apps.get_model("contenttypes", "ContentType")

    content_type_for_payment_record = ContentType.objects.get_for_model(PaymentRecord)

    subquery_pv = Subquery(
        PaymentVerification.objects
        .filter(pk=OuterRef("pk"))
        .values("payment_record_id")[:1]
    )

    PaymentVerification.objects.all().update(
        payment_content_type_id=content_type_for_payment_record.id,
        payment_object_id=subquery_pv,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("payment", "0073_migration_squashed_0074_migration"),
    ]

    operations = [
        migrations.RunPython(update_payment_verification_fk, migrations.RunPython.noop),
        migrations.RunPython(update_payment_record_fk, migrations.RunPython.noop),
    ]