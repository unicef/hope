import concurrency.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import hope.models.utils

PLAN_TYPE_CHOICES = [
    ("REGULAR", "Regular"),
    ("TOP_UP", "Top Up"),
    ("FOLLOW_UP", "Follow Up"),
    ("TOP_UP_AMENDMENT", "Top Up Amendment"),
]


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0041_migration"),
        ("payment", "0082_migration"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Follow-Up Instruction children leave their groups in 0084; 0085 adds the constraint that replaces this one.
        migrations.RemoveConstraint(
            model_name="paymentplan",
            name="payment_plan_group_required_unless_removed",
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="status",
            field=models.CharField(
                choices=[
                    ("OPEN", "Open"),
                    ("LOCKED", "Locked"),
                    ("IN_APPROVAL", "In Approval"),
                    ("IN_AUTHORIZATION", "In Authorization"),
                    ("IN_REVIEW", "In Review"),
                    ("ACCEPTED", "Accepted"),
                    ("ABORTED", "Aborted"),
                    ("FINISHED", "Finished"),
                    ("READY_FOR_CLOSURE", "Ready for Closure"),
                    ("CLOSED", "Closed"),
                ],
                default="OPEN",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="status_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="plan_type",
            field=models.CharField(
                choices=PLAN_TYPE_CHOICES,
                default="REGULAR",
                help_text="Type of the Payment Plans the group runs; a Follow-Up / Top-Up / Amendment group is linked [sys]",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="source_group",
            field=models.ForeignKey(
                blank=True,
                help_text="The group this Follow-Up / Top-Up / Amendment group was created from [sys]",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="linked_groups",
                to="payment.paymentplangroup",
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_plan_groups",
                to="core.currency",
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="financial_service_provider",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_plan_groups",
                to="payment.financialserviceprovider",
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="use_payment_gateway",
            field=models.BooleanField(
                default=False,
                help_text="Send the payment plans through the payment gateway regardless of the FSP communication channel",
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="dispersion_start_date",
            field=models.DateField(blank=True, help_text="Dispersion Start Date", null=True),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="dispersion_end_date",
            field=models.DateField(blank=True, help_text="Dispersion End Date", null=True),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="exchange_rate",
            field=models.DecimalField(
                blank=True, decimal_places=8, help_text="Exchange Rate [sys]", max_digits=15, null=True
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="custom_exchange_rate",
            field=models.BooleanField(default=False, help_text="Custom Exchange Rate flag [sys]"),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="custom_exchange_rate_set_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who set the custom exchange rate [sys]",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="abort_comment",
            field=models.CharField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="closure_comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="closed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="export_pdf_file_summary",
            field=models.ForeignKey(
                blank=True,
                help_text="Generated summary PDF [sys]",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="export_file_delivery",
            field=models.ForeignKey(
                blank=True,
                help_text="Generated payment list XLSX for the FSP [sys]",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="internal_data",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="version",
            field=concurrency.fields.IntegerVersionField(default=0, help_text="record revision number"),
        ),
        migrations.AlterField(
            model_name="paymentplangroup",
            name="background_action_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("RECALCULATING", "Recalculating Payment Plan data"),
                    ("RECALCULATING_ERROR", "Payment Plan recalculation error"),
                    ("XLSX_EXPORTING", "Exporting XLSX file"),
                    ("XLSX_EXPORT_ERROR", "Export XLSX file Error"),
                    ("XLSX_IMPORTING_RECONCILIATION", "Importing Reconciliation XLSX file"),
                    ("XLSX_IMPORTING_FSP_EXTRA_FIELDS", "Importing FSP Extra Fields XLSX file"),
                    ("XLSX_IMPORT_ERROR", "Import XLSX file Error"),
                    ("REBUILDING", "Rebuilding"),
                    ("REBUILD_ERROR", "Rebuild Error"),
                ],
                default=None,
                help_text="Background Action Status for asynchronous group tasks [sys]",
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplangroup",
            index=hope.models.utils.LongNameIndex(fields=["status"], name="payment_paymentplangroup_status_c68e4ae6"),
        ),
        migrations.AddIndex(
            model_name="paymentplangroup",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="payment_paymentplangroup_status_c68e4ae6_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplangroup",
            index=hope.models.utils.LongNameIndex(
                fields=["plan_type"], name="payment_paymentplangroup_plan_type_1e21f341"
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplangroup",
            index=hope.models.utils.LongNameIndex(
                fields=["plan_type"],
                name="payment_paymentplangroup_plan_type_1e21f341_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="follow_up_instructions",
                to="core.currency",
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="financial_service_provider",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="follow_up_instructions",
                to="payment.financialserviceprovider",
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="use_payment_gateway",
            field=models.BooleanField(
                default=False,
                help_text="Send the payment plans through the payment gateway regardless of the FSP communication channel",
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="dispersion_start_date",
            field=models.DateField(blank=True, help_text="Dispersion Start Date", null=True),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="dispersion_end_date",
            field=models.DateField(blank=True, help_text="Dispersion End Date", null=True),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="exchange_rate",
            field=models.DecimalField(
                blank=True, decimal_places=8, help_text="Exchange Rate [sys]", max_digits=15, null=True
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="custom_exchange_rate",
            field=models.BooleanField(default=False, help_text="Custom Exchange Rate flag [sys]"),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="custom_exchange_rate_set_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who set the custom exchange rate [sys]",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="abort_comment",
            field=models.CharField(blank=True, default="", max_length=2000),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="closure_comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="closed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="export_pdf_file_summary",
            field=models.ForeignKey(
                blank=True,
                help_text="Generated summary PDF",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="version",
            field=concurrency.fields.IntegerVersionField(default=0, help_text="record revision number"),
        ),
        migrations.AlterField(
            model_name="followupinstruction",
            name="background_action_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("RECALCULATING", "Recalculating Payment Plan data"),
                    ("RECALCULATING_ERROR", "Payment Plan recalculation error"),
                    ("XLSX_EXPORTING", "Exporting XLSX"),
                    ("XLSX_IMPORTING_RECONCILIATION", "Importing Reconciliation from XLSX"),
                    ("XLSX_EXPORT_ERROR", "Error while exporting XLSX"),
                    ("XLSX_IMPORT_ERROR", "Error while importing XLSX"),
                ],
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="approvalprocess",
            name="payment_plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="approval_process",
                to="payment.paymentplan",
            ),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="payment_plan_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="approval_process",
                to="payment.paymentplangroup",
            ),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="follow_up_instruction",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="approval_process",
                to="payment.followupinstruction",
            ),
        ),
        migrations.AddField(
            model_name="paymentplansupportingdocument",
            name="payment_plan_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="payment.paymentplangroup",
            ),
        ),
        migrations.AddField(
            model_name="paymentplansupportingdocument",
            name="follow_up_instruction",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="payment.followupinstruction",
            ),
        ),
    ]
