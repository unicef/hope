from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

from hope.apps.core.migration_operations import RunSQLAfterDeferred
import hope.models.utils


def seed_reference_data(apps, schema_editor):
    """Create the two account types and the default payment plan purpose of a new database."""
    AccountType = apps.get_model("payment", "AccountType")
    PaymentPlanPurpose = apps.get_model("payment", "PaymentPlanPurpose")

    AccountType.objects.get_or_create(key="mobile", defaults={"label": "Mobile", "unique_fields": ["number"]})
    AccountType.objects.get_or_create(key="bank", defaults={"label": "Bank", "unique_fields": ["number"]})
    # unicef_id is filled by the create_ppp_unicef_id trigger created above.
    PaymentPlanPurpose.objects.get_or_create(
        name="Default Purpose", defaults={"description": "Default payment plan purpose"}
    )


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("payment", "0001_migration"),
    ]

    dependencies = [
        ("core", "0041_baseline_models"),
        ("household", "0052_baseline_relations"),
        ("payment", "0081_baseline_models"),
        ("program", "0023_baseline_models"),
        ("steficon", "0008_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="followupinstruction",
            name="program",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="follow_up_instructions",
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="reconciliation_import_file",
            field=models.ForeignKey(
                blank=True,
                help_text="Reconciliation Import File",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="fspnamemapping",
            name="fsp",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="names_mappings",
                to="payment.financialserviceprovider",
            ),
        ),
        migrations.AddField(
            model_name="fspxlsxtemplateperdeliverymechanism",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="created_fsp_xlsx_template_per_delivery_mechanisms",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created by",
            ),
        ),
        migrations.AddField(
            model_name="fspxlsxtemplateperdeliverymechanism",
            name="delivery_mechanism",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="payment.deliverymechanism",
            ),
        ),
        migrations.AddField(
            model_name="fspxlsxtemplateperdeliverymechanism",
            name="financial_service_provider",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="fsp_xlsx_template_per_delivery_mechanisms",
                to="payment.financialserviceprovider",
            ),
        ),
        migrations.AddField(
            model_name="fspxlsxtemplateperdeliverymechanism",
            name="xlsx_template",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="fsp_xlsx_template_per_delivery_mechanisms",
                to="payment.financialserviceproviderxlsxtemplate",
            ),
        ),
        migrations.AddField(
            model_name="financialserviceprovider",
            name="xlsx_templates",
            field=models.ManyToManyField(
                related_name="financial_service_providers",
                through="payment.FspXlsxTemplatePerDeliveryMechanism",
                to="payment.financialserviceproviderxlsxtemplate",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="business_area",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.businessarea"),
        ),
        migrations.AddField(
            model_name="payment",
            name="collector",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="collector_payments",
                to="household.individual",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                help_text="Currency",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="payments",
                to="core.currency",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="delivery_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="payment.deliverymechanism",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="financial_service_provider",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="payment.financialserviceprovider",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="head_of_household",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="household.individual",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="household",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="household.household"),
        ),
        migrations.AddField(
            model_name="payment",
            name="program",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="program.program"),
        ),
        migrations.AddField(
            model_name="payment",
            name="source_payment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="follow_ups",
                to="payment.payment",
            ),
        ),
        migrations.AddField(
            model_name="paymenthouseholdsnapshot",
            name="payment",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="household_snapshot",
                to="payment.payment",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="business_area",
            field=models.ForeignKey(
                help_text="Business Area",
                on_delete=django.db.models.deletion.PROTECT,
                to="core.businessarea",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="closed_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who closed the payment plan",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="closed_payment_plans",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="created_by",
            field=models.ForeignKey(
                help_text="Created by user",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="created_payment_plans",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                help_text="Currency",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="payment_plans",
                to="core.currency",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
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
            model_name="paymentplan",
            name="delivery_mechanism",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="payment.deliverymechanism",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="export_file_delivery",
            field=models.ForeignKey(
                blank=True,
                help_text="Export File Delivery",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="export_file_entitlement",
            field=models.ForeignKey(
                blank=True,
                help_text="Export File Entitlement",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="export_pdf_file_summary",
            field=models.ForeignKey(
                blank=True,
                help_text="Export PDF File Summary",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
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
        migrations.AddField(
            model_name="paymentplan",
            name="follow_up_instruction",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_plans",
                to="payment.followupinstruction",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="imported_file",
            field=models.ForeignKey(
                blank=True,
                help_text="Imported File",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="program_cycle",
            field=models.ForeignKey(
                help_text="Program Cycle",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_plans",
                to="program.programcycle",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="reconciliation_import_file",
            field=models.ForeignKey(
                blank=True,
                help_text="Reconciliation Import File",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="source_payment_plan",
            field=models.ForeignKey(
                blank=True,
                help_text="Source Payment Plan (applicable for follow-up and top-up Payment Plans)",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="child_plans",
                to="payment.paymentplan",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="steficon_rule",
            field=models.ForeignKey(
                blank=True,
                help_text="Engine Formula for calculation entitlement value",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_plans",
                to="steficon.rulecommit",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="steficon_rule_targeting",
            field=models.ForeignKey(
                blank=True,
                help_text="Engine Formula for calculation vulnerability score value",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_plans_target",
                to="steficon.rulecommit",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="storage_file",
            field=models.OneToOneField(
                blank=True,
                help_text="Storage File",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.storagefile",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="parent",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_items",
                to="payment.paymentplan",
            ),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="payment_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="approval_process",
                to="payment.paymentplan",
            ),
        ),
        migrations.CreateModel(
            name="TargetPopulation",
            fields=[],
            options={
                "verbose_name": "Target Population",
                "verbose_name_plural": "Target Populations",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("payment.paymentplan",),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="cycle",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_plan_groups",
                to="program.programcycle",
                verbose_name="Programme Cycle",
            ),
        ),
        migrations.AddField(
            model_name="paymentplangroup",
            name="delivery_import_file",
            field=models.ForeignKey(
                blank=True,
                help_text="Uploaded reconciliation XLSX [sys]",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="payment_plan_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payment_plans",
                to="payment.paymentplangroup",
            ),
        ),
        migrations.AddField(
            model_name="paymentplanpurpose",
            name="limit_to",
            field=models.ManyToManyField(blank=True, related_name="payment_plan_purposes", to="core.businessarea"),
        ),
        migrations.AddField(
            model_name="paymentplan",
            name="payment_plan_purposes",
            field=models.ManyToManyField(
                blank=True,
                help_text="Payment plan purposes",
                related_name="payment_plans",
                to="payment.paymentplanpurpose",
            ),
        ),
        migrations.AddField(
            model_name="paymentplansplit",
            name="payment_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="splits",
                to="payment.paymentplan",
            ),
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
        migrations.AddField(
            model_name="paymentplansplitpayments",
            name="payment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_plan_split_payment",
                to="payment.payment",
            ),
        ),
        migrations.AddField(
            model_name="paymentplansplitpayments",
            name="payment_plan_split",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_plan_split",
                to="payment.paymentplansplit",
            ),
        ),
        migrations.AddField(
            model_name="paymentplansupportingdocument",
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
            model_name="paymentplansupportingdocument",
            name="payment_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="payment.paymentplan",
            ),
        ),
        migrations.AddField(
            model_name="paymentverification",
            name="payment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_verifications",
                to="payment.payment",
            ),
        ),
        migrations.AddField(
            model_name="paymentverificationplan",
            name="payment_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_verification_plans",
                to="payment.paymentplan",
            ),
        ),
        migrations.AddField(
            model_name="paymentverification",
            name="payment_verification_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_record_verifications",
                to="payment.paymentverificationplan",
            ),
        ),
        migrations.AddField(
            model_name="paymentverificationsummary",
            name="payment_plan",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment_verification_summary",
                to="payment.paymentplan",
            ),
        ),
        migrations.AddField(
            model_name="westernuniondata",
            name="file",
            field=models.ForeignKey(
                help_text="Western Union data file",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="westernunioninvoice",
            name="file",
            field=models.ForeignKey(
                help_text="Western Union invoice file",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddField(
            model_name="westernunioninvoice",
            name="matched_data",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="matched_invoices",
                to="payment.westernuniondata",
            ),
        ),
        migrations.AddField(
            model_name="westernunioninvoicepayment",
            name="payment",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="payment.payment"),
        ),
        migrations.AddField(
            model_name="westernunioninvoicepayment",
            name="western_union_invoice",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="payment.westernunioninvoice",
            ),
        ),
        migrations.AddField(
            model_name="westernunioninvoice",
            name="payments",
            field=models.ManyToManyField(
                related_name="invoices",
                through="payment.WesternUnionInvoicePayment",
                to="payment.payment",
            ),
        ),
        migrations.AddField(
            model_name="westernunionpaymentplanreport",
            name="invoice",
            field=models.ForeignKey(
                help_text="Western Union invoice",
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="reports",
                to="payment.westernunioninvoice",
            ),
        ),
        migrations.AddField(
            model_name="westernunionpaymentplanreport",
            name="payment_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="western_union_reports",
                to="payment.paymentplan",
            ),
        ),
        migrations.AddField(
            model_name="westernunionpaymentplanreport",
            name="report_file",
            field=models.ForeignKey(
                help_text="Western Union report file",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddIndex(
            model_name="acceptanceprocessthreshold",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_acceptanceprocessthreshold_created_at_bbe69353",
            ),
        ),
        migrations.AddIndex(
            model_name="acceptanceprocessthreshold",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_acceptanceprocessthreshold_updated_at_a8013a3d",
            ),
        ),
        migrations.AddIndex(
            model_name="approval",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="payment_approval_created_at_e97382ec"),
        ),
        migrations.AddIndex(
            model_name="approval",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="payment_approval_updated_at_b0fc5def"),
        ),
        migrations.AddIndex(
            model_name="deliverymechanism",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_deliverymechanism_created_at_784397b0",
            ),
        ),
        migrations.AddIndex(
            model_name="deliverymechanism",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_deliverymechanism_updated_at_ed583b15",
            ),
        ),
        migrations.AddIndex(
            model_name="financialinstitution",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_financialinstitution_created_at_c2d484cd",
            ),
        ),
        migrations.AddIndex(
            model_name="financialinstitution",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_financialinstitution_updated_at_fb0812ed",
            ),
        ),
        migrations.AddIndex(
            model_name="account",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="payment_account_created_at_06eee052"),
        ),
        migrations.AddIndex(
            model_name="account",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="payment_account_updated_at_cd04ae57"),
        ),
        migrations.AddIndex(
            model_name="account",
            index=hope.models.utils.LongNameIndex(fields=["number"], name="payment_account_number_ab8231a5"),
        ),
        migrations.AddIndex(
            model_name="account",
            index=hope.models.utils.LongNameIndex(
                fields=["number"],
                name="payment_account_number_ab8231a5_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="account",
            index=hope.models.utils.LongNameIndex(fields=["is_unique"], name="payment_account_is_unique_183d0bc1"),
        ),
        migrations.AddIndex(
            model_name="account",
            index=hope.models.utils.LongNameIndex(fields=["active"], name="payment_account_active_3b740582"),
        ),
        migrations.AddConstraint(
            model_name="account",
            constraint=models.UniqueConstraint(
                condition=models.Q(("active", True), ("unique_key__isnull", False), ("is_unique", True)),
                fields=("unique_key", "active", "is_unique"),
                name="unique_active_wallet",
            ),
        ),
        migrations.AddIndex(
            model_name="financialinstitutionmapping",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_financialinstitutionmapping_created_at_f136c2dc",
            ),
        ),
        migrations.AddIndex(
            model_name="financialinstitutionmapping",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_financialinstitutionmapping_updated_at_e681b3d7",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="financialinstitutionmapping",
            unique_together={("financial_service_provider", "financial_institution")},
        ),
        migrations.AddIndex(
            model_name="financialserviceproviderxlsxtemplate",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_financialservicepr_created_at_5fa42339",
            ),
        ),
        migrations.AddIndex(
            model_name="financialserviceproviderxlsxtemplate",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_financialservicepr_updated_at_eb878d36",
            ),
        ),
        migrations.AddIndex(
            model_name="followupinstruction",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_followupinstruction_created_at_5807ab3f",
            ),
        ),
        migrations.AddIndex(
            model_name="followupinstruction",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_followupinstruction_updated_at_197e3019",
            ),
        ),
        migrations.AddIndex(
            model_name="followupinstruction",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="payment_followupinstruction_unicef_id_8793ca7b",
            ),
        ),
        migrations.AddIndex(
            model_name="followupinstruction",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="payment_followupinstruction_unicef_id_8793ca7b_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="fspxlsxtemplateperdeliverymechanism",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_fspxlsxtemplateperdeliverymechanism_created_at_aa00fa2f",
            ),
        ),
        migrations.AddIndex(
            model_name="fspxlsxtemplateperdeliverymechanism",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_fspxlsxtemplateperdeliverymechanism_updated_at_d262f049",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="fspxlsxtemplateperdeliverymechanism",
            unique_together={("financial_service_provider", "delivery_mechanism")},
        ),
        migrations.AddIndex(
            model_name="financialserviceprovider",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_financialserviceprovider_created_at_7ca1152c",
            ),
        ),
        migrations.AddIndex(
            model_name="financialserviceprovider",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_financialserviceprovider_updated_at_89400a76",
            ),
        ),
        migrations.AddIndex(
            model_name="financialserviceprovider",
            index=hope.models.utils.LongNameIndex(
                fields=["distribution_limit"],
                name="payment_financialserviceprovider_distribution_limit_d7a089a1",
            ),
        ),
        migrations.AddIndex(
            model_name="financialserviceprovider",
            index=hope.models.utils.LongNameIndex(
                fields=["communication_channel"],
                name="payment_financialserviceprovider_communication_channel_67d4a550",
            ),
        ),
        migrations.AddIndex(
            model_name="financialserviceprovider",
            index=hope.models.utils.LongNameIndex(
                fields=["communication_channel"],
                name="payment_financialservice_communication_channel_67d4a550_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="paymenthouseholdsnapshot",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_paymenthouseholdsnapshot_created_at_dbec5131",
            ),
        ),
        migrations.AddIndex(
            model_name="paymenthouseholdsnapshot",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_paymenthouseholdsnapshot_updated_at_8f771f31",
            ),
        ),
        migrations.AddIndex(
            model_name="approvalprocess",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_approvalprocess_created_at_6a9c5d12",
            ),
        ),
        migrations.AddIndex(
            model_name="approvalprocess",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_approvalprocess_updated_at_1ff18c46",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplangroup",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_paymentplangroup_created_at_14a802c0",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplangroup",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_paymentplangroup_updated_at_b23558fe",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplangroup",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"], name="payment_paymentplangroup_unicef_id_3fb17c90"
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplangroup",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="payment_paymentplangroup_unicef_id_3fb17c90_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplangroup",
            index=hope.models.utils.LongNameIndex(
                fields=["background_action_status"],
                name="payment_paymentplangroup_background_action_status_2aeaeb44",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplangroup",
            index=hope.models.utils.LongNameIndex(
                fields=["background_action_status"],
                name="payment_paymentplangroup_background_action_status_2aeaeb44_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AlterUniqueTogether(
            name="paymentplangroup",
            unique_together={("cycle", "name")},
        ),
        migrations.AddIndex(
            model_name="paymentplanpurpose",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_paymentplanpurpose_created_at_d7aea5fa",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplanpurpose",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_paymentplanpurpose_updated_at_8d7cd301",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplanpurpose",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="payment_paymentplanpurpose_unicef_id_62d4c073",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplanpurpose",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="payment_paymentplanpurpose_unicef_id_62d4c073_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="payment_paymentplan_created_at_029b4d04"
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="payment_paymentplan_updated_at_4f87ddb1"
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(fields=["unicef_id"], name="payment_paymentplan_unicef_id_ba96bd54"),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["start_date"], name="payment_paymentplan_start_date_2c9849e2"
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(fields=["end_date"], name="payment_paymentplan_end_date_04e45bb0"),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(fields=["status"], name="payment_paymentplan_status_864b68ea"),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="payment_paymentplan_status_864b68ea_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["background_action_status"],
                name="payment_paymentplan_background_action_status_0334335b",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["background_action_status"],
                name="payment_paymentplan_background_action_status_0334335b_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["build_status"],
                name="payment_paymentplan_build_status_d3880ed4",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["build_status"],
                name="payment_paymentplan_build_status_d3880ed4_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["total_entitled_quantity"],
                name="payment_paymentplan_total_entitled_quantity_4edacc55",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["total_entitled_quantity_revised"],
                name="payment_paymentplan_total_entitled_quantity_revised_be7a6766",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["total_delivered_quantity"],
                name="payment_paymentplan_total_delivered_quantity_fd076625",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["total_undelivered_quantity"],
                name="payment_paymentplan_total_undelivered_quantity_2652642a",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(fields=["plan_type"], name="payment_paymentplan_plan_type_b827c7b8"),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["plan_type"],
                name="payment_paymentplan_plan_type_b827c7b8_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplan",
            index=hope.models.utils.LongNameIndex(
                fields=["export_tag"], name="payment_paymentplan_export_tag_ff34093c"
            ),
        ),
        migrations.AddConstraint(
            model_name="paymentplan",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("is_removed", True),
                    ("payment_plan_group__isnull", False),
                    _connector="OR",
                ),
                name="payment_plan_group_required_unless_removed",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplansplit",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_paymentplansplit_created_at_47485ac7",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplansplit",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_paymentplansplit_updated_at_5f13380d",
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="payment_payment_created_at_537eadaf"),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="payment_payment_updated_at_89699d7d"),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=hope.models.utils.LongNameIndex(fields=["unicef_id"], name="payment_payment_unicef_id_07f610de"),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=hope.models.utils.LongNameIndex(
                fields=["vulnerability_score"],
                name="payment_payment_vulnerability_score_e91d7c15",
            ),
        ),
        migrations.AddConstraint(
            model_name="payment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False), ("is_cash_assist", False)),
                fields=("parent", "household"),
                name="payment_plan_and_household",
            ),
        ),
        migrations.AddConstraint(
            model_name="payment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False)),
                fields=("program_id", "order_number"),
                name="order_number_unique_per_program",
            ),
        ),
        migrations.AddConstraint(
            model_name="payment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False)),
                fields=("program_id", "token_number"),
                name="token_number_unique_per_program",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplansplitpayments",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_paymentplansplitpayments_created_at_e95fd4c6",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentplansplitpayments",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_paymentplansplitpayments_updated_at_ced8e717",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="paymentplansplitpayments",
            unique_together={("payment_plan_split", "payment")},
        ),
        migrations.AddIndex(
            model_name="paymentverificationplan",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_paymentverificationplan_created_at_ccfa9990",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverificationplan",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_paymentverificationplan_updated_at_eece3840",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverificationplan",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="payment_paymentverificationplan_unicef_id_87e4384b",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverificationplan",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="payment_paymentverificationplan_unicef_id_87e4384b_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverificationplan",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="payment_paymentverificationplan_status_d41cb725",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverificationplan",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="payment_paymentverificationplan_status_d41cb725_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverification",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_paymentverification_created_at_aeebbe97",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverification",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_paymentverification_updated_at_4f0cb4e9",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverificationsummary",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="payment_paymentverificationsummary_created_at_290679bf",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverificationsummary",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="payment_paymentverificationsummary_updated_at_92a7bfc0",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverificationsummary",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="payment_paymentverificationsummary_status_245e2017",
            ),
        ),
        migrations.AddIndex(
            model_name="paymentverificationsummary",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="payment_paymentverificationsummary_status_245e2017_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="westernuniondata",
            index=hope.models.utils.LongNameIndex(fields=["status"], name="payment_westernuniondata_status_986d9c0a"),
        ),
        migrations.AddIndex(
            model_name="westernuniondata",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="payment_westernuniondata_status_986d9c0a_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="westernunioninvoice",
            index=hope.models.utils.LongNameIndex(
                fields=["status"], name="payment_westernunioninvoice_status_f3104712"
            ),
        ),
        migrations.AddIndex(
            model_name="westernunioninvoice",
            index=hope.models.utils.LongNameIndex(
                fields=["status"],
                name="payment_westernunioninvoice_status_f3104712_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        # payment_paymentplangroup.unicef_id comes from a serial column that is not on the model and a trigger that formats it.
        migrations.RunSQL(
            sql=[
                "ALTER TABLE payment_paymentplangroup ADD unicef_id_index SERIAL",
                """CREATE OR REPLACE FUNCTION create_ppg_unicef_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
            BEGIN
                NEW.unicef_id := format('PPG-%s', NEW.unicef_id_index);
                return NEW;
            END
            $function$""",
                "CREATE TRIGGER create_ppg_unicef_id BEFORE INSERT ON payment_paymentplangroup FOR EACH ROW EXECUTE FUNCTION create_ppg_unicef_id()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # payment_paymentplanpurpose.unicef_id comes from a serial column that is not on the model and a trigger that formats it.
        migrations.RunSQL(
            sql=[
                "ALTER TABLE payment_paymentplanpurpose ADD unicef_id_index SERIAL",
                """CREATE OR REPLACE FUNCTION create_ppp_unicef_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
                BEGIN
                    NEW.unicef_id := format('PPP-%s', NEW.unicef_id_index);
                return NEW;
                END
                $function$""",
                "CREATE TRIGGER create_ppp_unicef_id BEFORE INSERT ON payment_paymentplanpurpose FOR EACH ROW EXECUTE FUNCTION create_ppp_unicef_id()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # payment_paymentverificationplan.unicef_id comes from a serial column that is not on the model and a trigger that formats it.
        migrations.RunSQL(
            sql=[
                "ALTER TABLE payment_paymentverificationplan ADD unicef_id_index SERIAL",
                """CREATE OR REPLACE FUNCTION create_pvp_unicef_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
        BEGIN
            NEW.unicef_id := format('PVP-%s', NEW.unicef_id_index);
            return NEW;
        END
        $function$""",
                "CREATE TRIGGER create_pvp_unicef_id BEFORE INSERT ON payment_paymentverificationplan FOR EACH ROW EXECUTE FUNCTION create_pvp_unicef_id()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Each new business area also gets a sequence for follow-up instructions.
        migrations.RunSQL(
            sql=[
                """CREATE OR REPLACE FUNCTION follow_up_instruction_business_area_seq()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
            begin
                execute format(
                    'create sequence if not exists follow_up_instruction_business_area_seq_%s',
                    translate(NEW.id::text, '-','_')
                );
                return NEW;
            end
            $function$""",
                "CREATE TRIGGER follow_up_instruction_business_area_seq AFTER INSERT ON core_businessarea FOR EACH ROW EXECUTE FUNCTION follow_up_instruction_business_area_seq()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # unicef_id of payment plans, payments and follow-up instructions, numbered per business area.
        migrations.RunSQL(
            sql=[
                """CREATE OR REPLACE FUNCTION payment_plan_fill_unicef_id_per_business_area_seq()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
                DECLARE businessAreaID varchar;
                DECLARE businessAreaCode varchar;
            begin
                SELECT INTO businessAreaID translate(ba.id::text, '-','_') FROM core_businessarea ba WHERE ba.id=NEW.business_area_id;
                SELECT INTO businessAreaCode ba.code FROM core_businessarea ba WHERE ba.id=NEW.business_area_id;

                NEW.unicef_id := format('PP-%s-%s-%s', trim(businessAreaCode), to_char(NEW.created_at, 'yy'), trim(replace(to_char(nextval('payment_plan_business_area_seq_' || businessAreaID),'00000000'),',','.')));
                RETURN NEW;
            end
            $function$""",
                "CREATE TRIGGER payment_plan_fill_unicef_id_per_business_area_seq BEFORE INSERT ON payment_paymentplan FOR EACH ROW EXECUTE FUNCTION payment_plan_fill_unicef_id_per_business_area_seq()",
                """CREATE OR REPLACE FUNCTION payment_fill_unicef_id_per_business_area_seq()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
                DECLARE businessAreaID varchar;
                DECLARE businessAreaCode varchar;
            begin
                SELECT INTO businessAreaID translate(ba.id::text, '-','_') FROM core_businessarea ba WHERE ba.id=NEW.business_area_id;
                SELECT INTO businessAreaCode ba.code FROM core_businessarea ba WHERE ba.id=NEW.business_area_id;

                NEW.unicef_id := format('RCPT-%s-%s-%s', trim(businessAreaCode), to_char(NEW.created_at, 'yy'), trim(replace(to_char(nextval('payment_business_area_seq_' || businessAreaID),'0,000,000'),',','.')));
                RETURN NEW;
            end
            $function$""",
                "CREATE TRIGGER payment_fill_unicef_id_per_business_area_seq BEFORE INSERT ON payment_payment FOR EACH ROW EXECUTE FUNCTION payment_fill_unicef_id_per_business_area_seq()",
                """CREATE OR REPLACE FUNCTION follow_up_instruction_fill_unicef_id_per_business_area_seq()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
                DECLARE businessAreaID varchar;
                DECLARE businessAreaCode varchar;
            begin
                SELECT INTO businessAreaID translate(ba.id::text, '-','_') FROM core_businessarea ba WHERE ba.id=NEW.business_area_id;
                SELECT INTO businessAreaCode ba.code FROM core_businessarea ba WHERE ba.id=NEW.business_area_id;

                NEW.unicef_id := format(
                    'FUI-%s-%s-%s',
                    trim(businessAreaCode),
                    to_char(NEW.created_at, 'yy'),
                    trim(replace(to_char(nextval('follow_up_instruction_business_area_seq_' || businessAreaID), '00000000'), ',', '.'))
                );
                RETURN NEW;
            end
            $function$""",
                "CREATE TRIGGER follow_up_instruction_fill_unicef_id_per_business_area_seq BEFORE INSERT ON payment_followupinstruction FOR EACH ROW EXECUTE FUNCTION follow_up_instruction_fill_unicef_id_per_business_area_seq()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Left behind when unique_key stopped being unique; no model declares it, but every existing database has it.
        migrations.RunSQL(
            sql=[
                "CREATE INDEX IF NOT EXISTS payment_deliverymechanismdata_unique_key_4132f7bb_like ON payment_account USING btree (unique_key varchar_pattern_ops)",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Names that RenameModel and RenameField left behind in the replaced history. Every existing database
        # has them, so a new one gets them too. Renaming the index of a primary key or unique constraint
        # renames the constraint with it.
        RunSQLAfterDeferred(
            sql=[
                "ALTER INDEX IF EXISTS payment_account_account_type_id_cd162acd RENAME TO payment_deliverymechanismdata_account_type_id_d2bd1fea",
                "ALTER INDEX IF EXISTS payment_account_individual_id_b000f72b RENAME TO payment_deliverymechanismdata_individual_id_34989bba",
                "ALTER INDEX IF EXISTS payment_account_pkey RENAME TO payment_deliverymechanismdata_pkey",
                "ALTER INDEX IF EXISTS payment_paymentplan_export_file_delivery_id_809d0f7f RENAME TO payment_paymentplan_export_file_per_fsp_id_32703ed1",
                "ALTER INDEX IF EXISTS payment_westernunionpaymentplanreport_invoice_id_4ba96a99 RENAME TO payment_westernunionpaymentplanreport_qcf_file_id_dc17e149",
                """DO $$
DECLARE
    renames text[][] := ARRAY[
        ['payment_account', 'payment_account_individual_id_b000f72b_fk_household', 'payment_deliverymech_individual_id_34989bba_fk_household']
    ];
    r text[];
BEGIN
    FOREACH r SLICE 1 IN ARRAY renames LOOP
        IF EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid = r[1]::regclass AND conname = r[2]) THEN
            EXECUTE format('ALTER TABLE %I RENAME CONSTRAINT %I TO %I', r[1], r[2], r[3]);
        END IF;
    END LOOP;
END $$""",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunPython(seed_reference_data, migrations.RunPython.noop),
    ]
