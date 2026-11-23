from django.db import migrations

# (name, group label, group label plural, member label, member label plural, payee type)
BENEFICIARY_GROUPS = [
    ("Household", "Household", "Households", "Individual", "Individuals", "Household"),
    ("Social Workers", "Household", "Households", "Individual", "Individuals", "Incentive Payee"),
    (
        "Child Protection Workers",
        "Child Protection Worker",
        "Child Protection Workers",
        "Child Protection Worker",
        "Child Protection Workers",
        "Incentive Payee",
    ),
    ("Health Workers", "Health Worker", "Health Workers", "Health Worker", "Health Workers", "Incentive Payee"),
    (
        "Social Protection Workers",
        "Social Protection Worker",
        "Social Protection Workers",
        "Social Protection Worker",
        "Social Protection Workers",
        "Incentive Payee",
    ),
    ("WASH Workers", "WASH Worker", "WASH Workers", "WASH Worker", "WASH Workers", "Incentive Payee"),
    ("Schools", "School", "Schools", "Representative", "Representatives", "Organization"),
    (
        "Healthcare Facilities",
        "Healthcare Facility",
        "Healthcare Facilities",
        "Representative",
        "Representatives",
        "Organization",
    ),
    (
        "Child Protection Facilities",
        "Child Protection Facility",
        "Child Protection Facilities",
        "Representative",
        "Representatives",
        "Organization",
    ),
    (
        "Social Protection Facilities",
        "Social Protection Facility",
        "Social Protection Facilities",
        "Representative",
        "Representatives",
        "Organization",
    ),
    ("WASH Facilities", "WASH Facility", "WASH Facilities", "Representative", "Representatives", "Organization"),
    ("Mosques", "Mosque", "Mosques", "Representative", "Representatives", "Organization"),
    (
        "Other Service Delivery Organizations",
        "Other Service Delivery Organization",
        "Other Service Delivery Organizations",
        "Representative",
        "Representatives",
        "Organization",
    ),
]


def seed_reference_data(apps, schema_editor):
    """Create the beneficiary groups of a new database; core seeds their payee types."""
    BeneficiaryGroup = apps.get_model("program", "BeneficiaryGroup")
    PayeeType = apps.get_model("core", "PayeeType")
    Constance = apps.get_model("constance", "Constance")

    payee_types = {payee_type.name: payee_type for payee_type in PayeeType.objects.all()}
    for name, group_label, group_label_plural, member_label, member_label_plural, payee_type in BENEFICIARY_GROUPS:
        BeneficiaryGroup.objects.get_or_create(
            name=name,
            defaults={
                "group_label": group_label,
                "group_label_plural": group_label_plural,
                "member_label": member_label,
                "member_label_plural": member_label_plural,
                "payee_type": payee_types[payee_type],
            },
        )
    # The replaced history read this setting through constance, which stores the default on first read.
    Constance.objects.get_or_create(
        key="DEFAULT_BENEFICIARY_GROUP_NAME", defaults={"value": '{"__type__": "default", "__value__": "Household"}'}
    )


class Migration(migrations.Migration):
    replaces = [
        ("program", "0001_migration"),
    ]

    dependencies = [
        ("constance", "0003_drop_pickle"),
        ("core", "0045_baseline_relations"),
        ("program", "0027_baseline_models"),
    ]

    operations = [
        migrations.RunPython(seed_reference_data, migrations.RunPython.noop),
    ]
