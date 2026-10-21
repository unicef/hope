from django.db import migrations
from django.db.models import Q

STANDARD = "STANDARD"
SOCIAL = "SOCIAL"
HOUSEHOLD_DCT_CODES_WITHOUT_TYPE = ("unknown",)
INCENTIVE_PAYEE_DCT_CODES_WITHOUT_TYPE = ("delegate",)
INCENTIVE_PAYEE_MASTER_DETAIL_PAYEE_LABELS = ("Education Workers", "Community worker", "Facility Workers")
# (name, singular) pairs; the singular fills group_label and member_label, the name both plurals
INCENTIVE_PAYEE_NEW_PAYEE_LABELS = (
    ("Child Protection Workers", "Child Protection Worker"),
    ("Health Workers", "Health Worker"),
    ("Social Protection Workers", "Social Protection Worker"),
    ("WASH Workers", "WASH Worker"),
)
# (name, singular) pairs; the singular fills group_label, member_label is the organization's representative
ORGANIZATION_NEW_PAYEE_LABELS = (
    ("Schools", "School"),
    ("Healthcare Facilities", "Healthcare Facility"),
)
ORGANIZATION_MEMBER_LABEL = ("Representative", "Representatives")
ORGANIZATION_DCT_CODE = "head_of_facility"
ORGANIZATION_DCT_DEFAULTS = {
    "label": "Head of Facility",
    "description": "Head of Facility / Authorized Representative",
    "type": STANDARD,
    "active": True,
}


def _payee_labels_named(beneficiary_group_model, names):
    query = Q()
    for name in names:
        query |= Q(name__iexact=name)
    return beneficiary_group_model.objects.filter(query)


def _create_payee_labels(beneficiary_group_model, payee_type, payee_labels, member_label=None):
    for name, singular in payee_labels:
        member_singular, member_plural = member_label or (singular, name)
        beneficiary_group_model.objects.get_or_create(
            name=name,
            defaults={
                "group_label": singular,
                "group_label_plural": name,
                "member_label": member_singular,
                "member_label_plural": member_plural,
                "payee_type": payee_type,
            },
        )


def _default_dct(data_collecting_type_model, payee_type, preferred_code):
    candidates = data_collecting_type_model.objects.filter(payee_type=payee_type)
    return candidates.filter(code=preferred_code).first() or candidates.filter(active=True).order_by("pk").first()


def create_payee_types_and_backfill(apps, schema_editor):
    PayeeType = apps.get_model("core", "PayeeType")
    DataCollectingType = apps.get_model("core", "DataCollectingType")
    BeneficiaryGroup = apps.get_model("program", "BeneficiaryGroup")
    Program = apps.get_model("program", "Program")

    household, _ = PayeeType.objects.get_or_create(name="Household", defaults={"gl_code": "7700410", "weight": 30})
    incentive_payee, _ = PayeeType.objects.get_or_create(
        name="Incentive Payee", defaults={"gl_code": "7700430", "weight": 20}
    )
    organization, _ = PayeeType.objects.get_or_create(
        name="Organization", defaults={"gl_code": "7700430", "weight": 10}
    )

    DataCollectingType.objects.get_or_create(
        code=ORGANIZATION_DCT_CODE, defaults={**ORGANIZATION_DCT_DEFAULTS, "payee_type": organization}
    )
    DataCollectingType.objects.filter(payee_type__isnull=True, type=STANDARD).update(payee_type=household)
    DataCollectingType.objects.filter(payee_type__isnull=True, type=SOCIAL).update(payee_type=incentive_payee)
    DataCollectingType.objects.filter(payee_type__isnull=True, code__in=HOUSEHOLD_DCT_CODES_WITHOUT_TYPE).update(
        payee_type=household
    )
    DataCollectingType.objects.filter(payee_type__isnull=True, code__in=INCENTIVE_PAYEE_DCT_CODES_WITHOUT_TYPE).update(
        payee_type=incentive_payee
    )

    _create_payee_labels(BeneficiaryGroup, incentive_payee, INCENTIVE_PAYEE_NEW_PAYEE_LABELS)
    _create_payee_labels(BeneficiaryGroup, organization, ORGANIZATION_NEW_PAYEE_LABELS, ORGANIZATION_MEMBER_LABEL)
    payee_label_names_for_incentive_payee = INCENTIVE_PAYEE_MASTER_DETAIL_PAYEE_LABELS + tuple(
        name for name, _ in INCENTIVE_PAYEE_NEW_PAYEE_LABELS
    )
    _payee_labels_named(BeneficiaryGroup, payee_label_names_for_incentive_payee).filter(payee_type__isnull=True).update(
        payee_type=incentive_payee
    )
    _payee_labels_named(BeneficiaryGroup, [name for name, _ in ORGANIZATION_NEW_PAYEE_LABELS]).filter(
        payee_type__isnull=True
    ).update(payee_type=organization)
    BeneficiaryGroup.objects.filter(payee_type__isnull=True, master_detail=True).update(payee_type=household)
    BeneficiaryGroup.objects.filter(payee_type__isnull=True, master_detail=False).update(payee_type=incentive_payee)

    household.default_data_collecting_type = _default_dct(DataCollectingType, household, "full_collection")
    household.save(update_fields=["default_data_collecting_type"])
    incentive_payee.default_data_collecting_type = _default_dct(
        DataCollectingType, incentive_payee, "frontline_worker_humanitarian"
    )
    incentive_payee.save(update_fields=["default_data_collecting_type"])
    organization.default_data_collecting_type = _default_dct(DataCollectingType, organization, ORGANIZATION_DCT_CODE)
    organization.save(update_fields=["default_data_collecting_type"])

    unmapped_dcts_with_programs = DataCollectingType.objects.filter(
        payee_type__isnull=True, pk__in=Program.objects.values("data_collecting_type_id")
    )
    if unmapped_dcts_with_programs.exists():
        legacy, _ = PayeeType.objects.get_or_create(
            name="Legacy",
            defaults={"active": False, "description": "Data Collecting Types without type used by programs"},
        )
        unmapped_dcts_with_programs.update(payee_type=legacy)


def restore_master_detail(apps, schema_editor):
    BeneficiaryGroup = apps.get_model("program", "BeneficiaryGroup")
    payee_labels_with_master_detail = _payee_labels_named(BeneficiaryGroup, INCENTIVE_PAYEE_MASTER_DETAIL_PAYEE_LABELS)
    BeneficiaryGroup.objects.filter(payee_type__data_collecting_types__type=SOCIAL).exclude(
        pk__in=payee_labels_with_master_detail.values("pk")
    ).update(master_detail=False)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0042_migration"),
        ("program", "0024_migration"),
    ]

    operations = [
        migrations.RunPython(create_payee_types_and_backfill, restore_master_detail),
    ]
