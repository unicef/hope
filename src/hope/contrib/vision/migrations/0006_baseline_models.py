from django.db import migrations, models
import django.db.models.deletion

import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("vision", "0001_migration"),
        ("vision", "0002_migration"),
        ("vision", "0003_migration"),
        ("vision", "0004_migration"),
        ("vision", "0005_migration"),
    ]

    dependencies = [
        ("core", "0044_baseline_models"),
        ("payment", "0084_baseline_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="DownPayment",
            fields=[
                (
                    "rec_serial_number",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                ("business_area", models.CharField(max_length=4)),
                ("down_payment_reference", models.CharField(max_length=20)),
                ("document_type", models.CharField(max_length=10)),
                ("consumed_fc_number", models.CharField(max_length=10)),
                (
                    "consumed_fc_item_number",
                    models.CharField(blank=True, max_length=3, null=True),
                ),
                (
                    "currency_code",
                    models.CharField(blank=True, max_length=5, null=True),
                ),
                ("posting_date", models.DateField(blank=True, null=True)),
                ("doc_year", models.IntegerField(blank=True, null=True)),
                ("doc_number", models.CharField(blank=True, max_length=10, null=True)),
                ("doc_item_number", models.CharField(max_length=3, null=True)),
                (
                    "total_down_payment_amount_local",
                    models.DecimalField(decimal_places=2, max_digits=15),
                ),
                (
                    "total_down_payment_amount_usd",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                ("create_date", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "created_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                ("update_date", models.DateTimeField(blank=True, null=True)),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "office",
                    models.ForeignKey(
                        blank=True,
                        help_text="This can be a business office or a business area",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.businessarea",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FundsCommitmentHeader",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "funds_commitment_number",
                    models.CharField(max_length=10, unique=True),
                ),
                ("vendor_id", models.CharField(blank=True, max_length=10, null=True)),
                ("posting_date", models.DateField(blank=True, null=True)),
                (
                    "document_reference",
                    models.CharField(blank=True, max_length=16, null=True),
                ),
                ("fc_status", models.CharField(blank=True, max_length=1, null=True)),
                ("currency", models.CharField(blank=True, max_length=5, null=True)),
                (
                    "payment_plans",
                    models.ManyToManyField(
                        blank=True,
                        related_name="funds_commitment_headers",
                        to="payment.paymentplan",
                    ),
                ),
            ],
            options={
                "verbose_name": "Funds Commitment Header",
                "verbose_name_plural": "Funds Commitment Headers",
            },
        ),
        migrations.CreateModel(
            name="FundsCommitment",
            fields=[
                (
                    "rec_serial_number",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                (
                    "funds_commitment_number",
                    models.CharField(blank=True, max_length=10, null=True),
                ),
                ("vendor_id", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "business_area",
                    models.CharField(blank=True, max_length=4, null=True),
                ),
                ("posting_date", models.DateField(blank=True, null=True)),
                (
                    "vision_approval",
                    models.CharField(blank=True, max_length=1, null=True),
                ),
                ("document_reference", models.CharField(max_length=16, null=True)),
                ("fc_status", models.CharField(blank=True, max_length=1, null=True)),
                (
                    "funds_commitment_item",
                    models.CharField(blank=True, default="", max_length=3, null=True),
                ),
                (
                    "wbs_element",
                    models.CharField(blank=True, default="", max_length=24, null=True),
                ),
                (
                    "grant_number",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "document_type",
                    models.CharField(blank=True, max_length=2, null=True),
                ),
                (
                    "document_text",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "currency_code",
                    models.CharField(blank=True, max_length=5, null=True),
                ),
                ("gl_account", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "commitment_amount_local",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "commitment_amount_usd",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "total_open_amount_local",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "total_open_amount_usd",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "sponsor",
                    models.CharField(blank=True, default="", max_length=10, null=True),
                ),
                (
                    "sponsor_name",
                    models.CharField(blank=True, default="", max_length=100, null=True),
                ),
                (
                    "fund",
                    models.CharField(blank=True, default="", max_length=10, null=True),
                ),
                (
                    "funds_center",
                    models.CharField(blank=True, default="", max_length=16, null=True),
                ),
                (
                    "percentage",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
                ),
                ("create_date", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "created_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                ("update_date", models.DateTimeField(blank=True, null=True)),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "office",
                    models.ForeignKey(
                        blank=True,
                        help_text="This can be a business office or a business area",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.businessarea",
                    ),
                ),
            ],
            options={
                "indexes": [
                    hope.models.utils.LongNameIndex(
                        fields=["funds_commitment_number"],
                        name="vision_fundscommitment_funds_commitment_number_7eeae3be",
                    ),
                    hope.models.utils.LongNameIndex(
                        fields=["funds_commitment_number"],
                        name="vision_fundscommitment_funds_commitment_number_7eeae3be_like",
                        opclasses=["varchar_pattern_ops"],
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="FundsCommitmentItem",
            fields=[
                ("funds_commitment_item", models.CharField(max_length=3)),
                (
                    "rec_serial_number",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                ("vendor_id", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "business_area",
                    models.CharField(blank=True, max_length=4, null=True),
                ),
                ("posting_date", models.DateField(blank=True, null=True)),
                (
                    "vision_approval",
                    models.CharField(blank=True, max_length=1, null=True),
                ),
                ("document_reference", models.CharField(max_length=16, null=True)),
                ("fc_status", models.CharField(blank=True, max_length=1, null=True)),
                (
                    "wbs_element",
                    models.CharField(blank=True, default="", max_length=24, null=True),
                ),
                (
                    "grant_number",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "document_type",
                    models.CharField(blank=True, max_length=2, null=True),
                ),
                (
                    "document_text",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "currency_code",
                    models.CharField(blank=True, max_length=5, null=True),
                ),
                ("gl_account", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "commitment_amount_local",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "commitment_amount_usd",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "total_open_amount_local",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "total_open_amount_usd",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "sponsor",
                    models.CharField(blank=True, default="", max_length=10, null=True),
                ),
                (
                    "sponsor_name",
                    models.CharField(blank=True, default="", max_length=100, null=True),
                ),
                (
                    "fund",
                    models.CharField(blank=True, default="", max_length=10, null=True),
                ),
                (
                    "funds_center",
                    models.CharField(blank=True, default="", max_length=16, null=True),
                ),
                (
                    "percentage",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
                ),
                ("create_date", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "created_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                ("update_date", models.DateTimeField(blank=True, null=True)),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "funds_commitment_header",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="funds_commitment_items",
                        to="vision.fundscommitmentheader",
                    ),
                ),
                (
                    "office",
                    models.ForeignKey(
                        blank=True,
                        help_text="This can be a business office or a business area",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.businessarea",
                    ),
                ),
            ],
            options={
                "indexes": [
                    hope.models.utils.LongNameIndex(
                        fields=["funds_commitment_item"],
                        name="vision_fundscommitmentitem_funds_commitment_item_ab1d46fb",
                    ),
                    hope.models.utils.LongNameIndex(
                        fields=["funds_commitment_item"],
                        name="vision_fundscommitmentitem_funds_commitment_item_ab1d46fb_like",
                        opclasses=["varchar_pattern_ops"],
                    ),
                ],
            },
        ),
    ]
