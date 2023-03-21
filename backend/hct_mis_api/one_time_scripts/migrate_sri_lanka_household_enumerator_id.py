from django.db import transaction
from django.db.models import Q

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.registration_datahub.models import ImportedHousehold


@transaction.atomic()
def migrate_imported_household_admin_area() -> None:
    queryset = Household.objects.filter(
        ~Q(flex_fields__has_key="id_enumerator"),
        business_area__slug="sri-lanka",
    ).order_by("pk")

    for hh in queryset:
        imported_individual_id = hh.head_of_household.imported_individual_id
        imported_household = ImportedHousehold.objects.filter(individuals=imported_individual_id).first()

        if not imported_household:
            print(f"No imported_household for {imported_individual_id}")
            continue

        record = imported_household.flex_registrations_record

        if id_enumerator := record.get_data().get("id_enumerator"):
            hh.flex_fields["id_enumerator"] = id_enumerator
            hh.save(update_fields=["flex_fields"])
