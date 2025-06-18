from hct_mis_api.apps.household.models import Household, Individual


def replace_blank_with_null() -> None:
    BATCH_SIZE = 1000
    BLANK = ""
    NONE = "NONE"

    households_to_update = []

    for instance in Household.objects.iterator(chunk_size=BATCH_SIZE):
        update_fields = []

        if instance.consent_sharing:
            cleaned = [v for v in instance.consent_sharing if v != BLANK]
            if cleaned != instance.consent_sharing:
                instance.consent_sharing = cleaned if cleaned else None
                update_fields.append("consent_sharing")

        for field in ["org_enumerator", "registration_method", "residence_status"]:
            if getattr(instance, field) == "":
                setattr(instance, field, None)
                update_fields.append(field)

        if update_fields:
            households_to_update.append(instance)

    if households_to_update:
        Household.objects.bulk_update(
            households_to_update, ["consent_sharing", "org_enumerator", "registration_method", "residence_status"]
        )

    individuals_to_update = []

    for instance in Individual.objects.iterator(chunk_size=BATCH_SIZE):
        update_fields = []

        if instance.observed_disability:
            cleaned = [v for v in instance.observed_disability if v != NONE]
            if cleaned != instance.observed_disability:
                instance.observed_disability = cleaned if cleaned else None
                update_fields.append("observed_disability")

        fields = [
            "comms_disability",
            "hearing_disability",
            "marital_status",
            "memory_disability",
            "physical_disability",
            "seeing_disability",
            "selfcare_disability",
        ]
        for field in fields:
            if getattr(instance, field) == "":
                setattr(instance, field, None)
                update_fields.append(field)

        if update_fields:
            individuals_to_update.append(instance)

    if individuals_to_update:
        Individual.objects.bulk_update(
            individuals_to_update,
            [
                "observed_disability",
                "comms_disability",
                "hearing_disability",
                "marital_status",
                "memory_disability",
                "physical_disability",
                "seeing_disability",
                "selfcare_disability",
            ],
        )
