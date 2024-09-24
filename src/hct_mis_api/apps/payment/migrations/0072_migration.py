# Generated by Django 3.2.15 on 2022-11-02 09:23

from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q

from hct_mis_api.apps.account.fields import ChoiceArrayField
import model_utils.fields
import uuid
import multiselectfield.db.fields


def populate_delivery_mechanisms(apps, schema_editor):
    DeliveryMechanism = apps.get_model("payment", "DeliveryMechanism")

    DeliveryMechanism.objects.get_or_create(
        delivery_mechanism="Cash",
        defaults=dict(global_core_fields=["given_name", "family_name"], payment_channel_fields=[]),
    )


def fix_fsp_communication_channels(apps, schema_editor):
    FinancialServiceProvider = apps.get_model("payment", "FinancialServiceProvider")

    FinancialServiceProvider.objects.filter(
        Q(communication_channel__isnull=True) | Q(communication_channel__exact="")
    ).update(communication_channel="XLSX")


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0052_migration_squashed_0071_migration"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryMechanism",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "delivery_mechanism",
                    models.CharField(
                        choices=[
                            ("Cardless cash withdrawal", "Cardless cash withdrawal"),
                            ("Cash", "Cash"),
                            ("Cash by FSP", "Cash by FSP"),
                            ("Cheque", "Cheque"),
                            ("Deposit to Card", "Deposit to Card"),
                            ("In Kind", "In Kind"),
                            ("Mobile Money", "Mobile Money"),
                            ("Other", "Other"),
                            ("Pre-paid card", "Pre-paid card"),
                            ("Referral", "Referral"),
                            ("Transfer", "Transfer"),
                            ("Transfer to Account", "Transfer to Account"),
                            ("Voucher", "Voucher"),
                        ],
                        max_length=255,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "global_core_fields",
                    ChoiceArrayField(
                        base_field=models.CharField(
                            blank=True,
                            choices=[
                                ("Age (calculated)", "age"),
                                ("Residence status", "residence_status"),
                                ("Do you consent?", "consent"),
                                ("Do you consent?", "consent_sign"),
                                ("Country of Origin", "country_origin"),
                                ("Country of registration", "country"),
                                ("Address", "address"),
                                ("Household resides in which ${admin1_h_c}?", "admin1"),
                                ("Household resides in which ${admin2_h_c}?", "admin2"),
                                ("Geolocation", "geopoint"),
                                ("UNHCR Case ID", "unhcr_id"),
                                ("Is this a returnee household?", "returnee"),
                                ("What is the household size?", "size"),
                                ("Child is female and head of household", "fchild_hoh"),
                                ("Child is/ head of household", "child_hoh"),
                                ("Relationship to head of household", "relationship"),
                                ("Full name", "full_name"),
                                ("Given name", "given_name"),
                                ("Middle name(s)", "middle_name"),
                                ("Family name", "family_name"),
                                ("Gender", "sex"),
                                ("Birth date", "birth_date"),
                                ("Estimated birth date?", "estimated_birth_date"),
                                ("Individual's photo", "photo"),
                                ("Marital status", "marital_status"),
                                ("Phone number", "phone_no"),
                                ("Who answers this phone?", "who_answers_phone"),
                                ("Alternative phone number", "phone_no_alternative"),
                                ("Who answers this phone?", "who_answers_alt_phone"),
                                ("Method of collection (e.g. HH survey, Community, etc.)", "registration_method"),
                                ("Will you be collecting all member Individuals' data?", "collect_individual_data"),
                                ("Which currency will be used for financial questions?", "currency"),
                                ("Birth certificate number", "birth_certificate_no"),
                                ("Issuing country of birth certificate", "birth_certificate_issuer"),
                                ("Birth certificate photo", "birth_certificate_photo"),
                                ("Driver's license number", "drivers_license_no"),
                                ("Issuing country of driver's license", "drivers_license_issuer"),
                                ("Driver's license photo", "drivers_license_photo"),
                                ("Electoral card number", "electoral_card_no"),
                                ("Issuing country of electoral card", "electoral_card_issuer"),
                                ("Electoral card photo", "electoral_card_photo"),
                                ("UNHCR ID number", "unhcr_id_no"),
                                ("Issuing entity of UNHCR ID", "unhcr_id_issuer"),
                                ("UNHCR ID photo", "unhcr_id_photo"),
                                ("National passport number", "national_passport"),
                                ("Issuing country of national passport", "national_passport_issuer"),
                                ("National passport photo", "national_passport_photo"),
                                ("National ID number", "national_id_no"),
                                ("Issuing country of national ID", "national_id_issuer"),
                                ("National ID photo", "national_id_photo"),
                                ("WFP Scope ID number", "scope_id_no"),
                                ("Issuing entity of SCOPE ID", "scope_id_issuer"),
                                ("WFP Scope ID photo", "scope_id_photo"),
                                ("If other type of ID, specify the type", "other_id_type"),
                                ("Other ID number", "other_id_no"),
                                ("Issuing country of other ID", "other_id_issuer"),
                                ("ID photo", "other_id_photo"),
                                ("Females Age 0 - 5", "female_age_group_0_5_count"),
                                ("Females Age 6 - 11", "female_age_group_6_11_count"),
                                ("Females Age 12 - 17", "female_age_group_12_17_count"),
                                ("Females Age 18 - 59", "female_age_group_18_59_count"),
                                ("Females Age 60 +", "female_age_group_60_count"),
                                ("Pregnant count", "pregnant_count"),
                                ("Males Age 0 - 5", "male_age_group_0_5_count"),
                                ("Males Age 6 - 11", "male_age_group_6_11_count"),
                                ("Males Age 12 - 17", "male_age_group_12_17_count"),
                                ("Males Age 18 - 59", "male_age_group_18_59_count"),
                                ("Males Age 60 +", "male_age_group_60_count"),
                                ("Females age 0 - 5 with disability", "female_age_group_0_5_disabled_count"),
                                ("Females age 6 - 11 with disability", "female_age_group_6_11_disabled_count"),
                                ("Females age 12 - 17 with disability", "female_age_group_12_17_disabled_count"),
                                ("Females Age 18 - 59 with disability", "female_age_group_18_59_disabled_count"),
                                ("Female members with Disability age 60 +", "female_age_group_60_disabled_count"),
                                ("Males age 0 - 5 with disability", "male_age_group_0_5_disabled_count"),
                                ("Males age 6 - 11 with disability", "male_age_group_6_11_disabled_count"),
                                ("Males age 12 - 17 with disability", "male_age_group_12_17_disabled_count"),
                                ("Males Age 18 - 59 with disability", "male_age_group_18_59_disabled_count"),
                                ("Male members with Disability age 60 +", "male_age_group_60_disabled_count"),
                                ("Is the individual pregnant?", "pregnant"),
                                ("Does the individual have paid employment in the current month?", "work_status"),
                                ("Does the individual have disability?", "observed_disability"),
                                ("If the individual has difficulty seeing, what is the severity?", "seeing_disability"),
                                (
                                    "If the individual has difficulty hearing, what is the severity?",
                                    "hearing_disability",
                                ),
                                (
                                    "If the individual has difficulty walking or climbing steps, what is the severity?",
                                    "physical_disability",
                                ),
                                (
                                    "If the individual has difficulty remembering or concentrating, what is the severity?",
                                    "memory_disability",
                                ),
                                (
                                    "Do you have difficulty (with self-care such as) washing all over or dressing",
                                    "selfcare_disability",
                                ),
                                (
                                    "If the individual has difficulty communicating, what is the severity?",
                                    "comms_disability",
                                ),
                                ("Female child headed household", "fchild_hoh"),
                                ("Child headed household", "child_hoh"),
                                ("Village", "village"),
                                ("Device ID", "deviceid"),
                                ("Name of the enumerator", "name_enumerator"),
                                ("Organization of the enumerator", "org_enumerator"),
                                ("Which organizations may we share your information with?", "consent_sharing"),
                                ("Name of partner organization", "org_name_enumerator"),
                                ("Individual is disabled?", "disability"),
                            ],
                            max_length=255,
                        ),
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "payment_channel_fields",
                    ChoiceArrayField(
                        base_field=models.CharField(
                            blank=True,
                            choices=[
                                ("Bank name", "bank_name"),
                                ("Bank account number", "bank_account_number"),
                                ("Debit Card Issuer", "debit_card_issuer"),
                                ("Debit card number", "debit_card_number"),
                            ],
                            max_length=255,
                        ),
                        default=list,
                        size=None,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterField(
            model_name="cashplanpaymentverification",
            name="status",
            field=models.CharField(
                choices=[
                    ("ACTIVE", "Active"),
                    ("FINISHED", "Finished"),
                    ("PENDING", "Pending"),
                    ("INVALID", "Invalid"),
                    ("RAPID_PRO_ERROR", "RapidPro Error"),
                ],
                db_index=True,
                default="PENDING",
                max_length=50,
            ),
        ),
        # WUUUUT
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.CharField(
                choices=[
                    ("Distribution Successful", "Distribution Successful"),
                    ("Not Distributed", "Not Distributed"),
                    ("Transaction Successful", "Transaction Successful"),
                    ("Transaction Erroneous", "Transaction Erroneous"),
                    ("Force failed", "Force failed"),
                ],
                max_length=255,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="deliverymechanismperpaymentplan",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="paymentchannel",
            constraint=models.UniqueConstraint(
                fields=("individual", "delivery_mechanism"), name="unique individual_delivery_mechanism"
            ),
        ),
        migrations.AlterField(
            model_name="paymentchannel",
            name="delivery_mechanism",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="payment_channels",
                to="payment.deliverymechanism",
            ),
        ),
        migrations.AlterField(
            model_name="deliverymechanism",
            name="delivery_mechanism",
            field=models.CharField(
                choices=[
                    ("Cardless cash withdrawal", "Cardless cash withdrawal"),
                    ("Cash", "Cash"),
                    ("Cash by FSP", "Cash by FSP"),
                    ("Cheque", "Cheque"),
                    ("Deposit to Card", "Deposit to Card"),
                    ("In Kind", "In Kind"),
                    ("Mobile Money", "Mobile Money"),
                    ("Other", "Other"),
                    ("Pre-paid card", "Pre-paid card"),
                    ("Referral", "Referral"),
                    ("Transfer", "Transfer"),
                    ("Transfer to Account", "Transfer to Account"),
                    ("Voucher", "Voucher"),
                ],
                max_length=255,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="financialserviceproviderxlsxtemplate",
            name="columns",
            field=multiselectfield.db.fields.MultiSelectField(
                choices=[
                    ("payment_id", "Payment ID"),
                    ("household_id", "Household ID"),
                    ("household_size", "Household Size"),
                    ("admin_level_2", "Admin Level 2"),
                    ("collector_name", "Collector Name"),
                    ("payment_channel", "Payment Channel (Delivery mechanism)"),
                    ("fsp_name", "FSP Name"),
                    ("currency", "Currency"),
                    ("entitlement_quantity", "Entitlement Quantity"),
                    ("entitlement_quantity_usd", "Entitlement Quantity USD"),
                    ("delivered_quantity", "Delivered Quantity"),
                ],
                default=[
                    "payment_id",
                    "household_id",
                    "household_size",
                    "admin_level_2",
                    "collector_name",
                    "payment_channel",
                    "fsp_name",
                    "currency",
                    "entitlement_quantity",
                    "entitlement_quantity_usd",
                    "delivered_quantity",
                ],
                help_text="Select the columns to include in the report",
                max_length=166,
                verbose_name="Columns",
            ),
        ),
        migrations.RunPython(populate_delivery_mechanisms, migrations.RunPython.noop),
        migrations.RunPython(fix_fsp_communication_channels, migrations.RunPython.noop),
    ]