from django.db import migrations

STANDARD = "STANDARD"
SOCIAL = "SOCIAL"


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
    PayeeType.objects.get_or_create(name="Organization", defaults={"gl_code": "7700430", "weight": 10, "active": False})

    DataCollectingType.objects.filter(payee_type__isnull=True, type=STANDARD).update(payee_type=household)
    DataCollectingType.objects.filter(payee_type__isnull=True, type=SOCIAL).update(payee_type=incentive_payee)
    BeneficiaryGroup.objects.filter(payee_type__isnull=True, master_detail=True).update(payee_type=household)
    BeneficiaryGroup.objects.filter(payee_type__isnull=True, master_detail=False).update(payee_type=incentive_payee)

    household.default_data_collecting_type = _default_dct(DataCollectingType, household, "full_collection")
    household.save(update_fields=["default_data_collecting_type"])
    incentive_payee.default_data_collecting_type = _default_dct(
        DataCollectingType, incentive_payee, "frontline_worker_humanitarian"
    )
    incentive_payee.save(update_fields=["default_data_collecting_type"])

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
    BeneficiaryGroup.objects.filter(payee_type__data_collecting_types__type=SOCIAL).update(master_detail=False)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0042_migration"),
        ("program", "0024_migration"),
    ]

    operations = [
        migrations.RunPython(create_payee_types_and_backfill, restore_master_detail),
    ]
