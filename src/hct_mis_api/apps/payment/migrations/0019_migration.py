# Generated by Django 3.2.25 on 2025-02-14 11:29

from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Subquery, OuterRef


def migrate_payments_to_parent_split(apps, schema_editor):  # pragma: no cover
    PaymentPlanSplitPayments = apps.get_model("payment", "PaymentPlanSplitPayments")
    Payment = apps.get_model("payment", "Payment")

    payments_to_update = []
    for split_payment in PaymentPlanSplitPayments.objects.select_related("payment"):
        split_payment.payment.parent_split_id = split_payment.payment_plan_split_id
        payments_to_update.append(split_payment.payment)

    if payments_to_update:
        Payment.objects.bulk_update(payments_to_update, ["parent_split"])


def migrate_payments_to_default_split(apps, schema_editor):  # pragma: no cover
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlanSplit = apps.get_model("payment", "PaymentPlanSplit")

    for payment_plan in PaymentPlan.objects.filter(splits__isnull=True).iterator():
        default_split = PaymentPlanSplit.objects.create(payment_plan=payment_plan)
        dm = getattr(payment_plan, "delivery_mechanism", None)
        if dm and dm.sent_to_payment_gateway:
            # store the old object's id in a variable
            old_obj_id = default_split.id
            # it creates a new object
            default_split.id = payment_plan.delivery_mechanism.id  # to match data stored in PG
            default_split.sent_to_payment_gateway = True
            default_split.save()
            # and delete the old object
            PaymentPlanSplit.objects.filter(id=old_obj_id).delete()
        payment_plan.payment_items.all().update(parent_split_id=default_split.id)


def migrate_dmppp_pp_fk(apps, schema_editor):  # pragma: no cover
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    DeliveryMechanismPerPaymentPlan = apps.get_model("payment", "DeliveryMechanismPerPaymentPlan")

    subquery_dm = DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=OuterRef("pk")).values(
        "delivery_mechanism"
    )[:1]

    subquery_fsp = DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=OuterRef("pk")).values(
        "financial_service_provider"
    )[:1]

    PaymentPlan.objects.filter(delivery_mechanism_per_payment_plan__isnull=False).update(
        delivery_mechanism=Subquery(subquery_dm), financial_service_provider=Subquery(subquery_fsp)
    )


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0018_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deliverymechanismperpaymentplan",
            name="payment_plan",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="delivery_mechanism_per_payment_plan",
                to="payment.paymentplan",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="delivery_mechanism",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="payment.deliverymechanism"
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="financial_service_provider",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="payment.financialserviceprovider",
            ),
        ),
        migrations.RunPython(migrate_dmppp_pp_fk, reverse_code=migrations.RunPython.noop),
        migrations.AddField(
            model_name="financialserviceprovider",
            name="required_fields",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=255), default=list, size=None
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="has_valid_wallet",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="deliverymechanism",
            name="payment_gateway_id",
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="financialserviceprovider",
            name="payment_gateway_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.RemoveField(
            model_name="deliverymechanismperpaymentplan",
            name="chosen_configuration",
        ),
        migrations.RemoveField(
            model_name="deliverymechanismperpaymentplan",
            name="created_by",
        ),
        migrations.RemoveField(
            model_name="deliverymechanismperpaymentplan",
            name="sent_by",
        ),
        migrations.RemoveField(
            model_name="deliverymechanismperpaymentplan",
            name="sent_date",
        ),
        migrations.RemoveField(
            model_name="deliverymechanismperpaymentplan",
            name="status",
        ),
        migrations.AddField(
            model_name="payment",
            name="parent_split",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="split_payment_items",
                to="payment.paymentplansplit",
            ),
        ),
        migrations.AlterField(
            model_name="deliverymechanismperpaymentplan",
            name="payment_plan",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, related_name="delivery_mechanism", to="payment.paymentplan"
            ),
        ),
        migrations.AlterField(
            model_name="paymentplansplit",
            name="split_type",
            field=models.CharField(
                choices=[
                    ("NO_SPLIT", "No Split"),
                    ("BY_RECORDS", "By Records"),
                    ("BY_COLLECTOR", "By Collector"),
                    ("BY_ADMIN_AREA1", "By Admin Area 1"),
                    ("BY_ADMIN_AREA2", "By Admin Area 2"),
                    ("BY_ADMIN_AREA3", "By Admin Area 3"),
                ],
                default="NO_SPLIT",
                max_length=24,
            ),
        ),
        migrations.RunPython(migrate_payments_to_parent_split, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(migrate_payments_to_default_split, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="paymentplansplit",
            name="payments",
        ),
    ]
