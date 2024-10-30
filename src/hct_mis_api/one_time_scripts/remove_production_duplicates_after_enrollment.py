import logging

from django.db.models import Count

from hct_mis_api.apps.household.models import Household

logger = logging.getLogger(__name__)


def remove_production_duplicates_after_enrollment():
    # Exceptions from the further rules
    for household in Household.objects.filter(
        id__in=[
            "8b9bf768-4837-49aa-a598-5ad3c5822ca8",
            "33a7bdf0-650d-49b4-b333-c49a7eb05356",
        ]
    ):
        household.delete(soft=False)

    households_with_duplicates = (
        Household.objects.values("unicef_id", "program")
        .annotate(household_count=Count("id"))
        .filter(household_count__gt=1)
        .order_by("copied_from__registration_data_import")
    )
    logger.info(f"Found {households_with_duplicates.count()} households with duplicates")

    for i, entry in enumerate(households_with_duplicates, 1):
        unicef_id = entry["unicef_id"]
        program = entry["program"]

        households = Household.objects.filter(unicef_id=unicef_id, program=program).order_by("created_at")

        # Keep the first household and delete the duplicates
        first = True
        households_to_remove = []
        for household in households:
            if first:
                first = False
                continue
            if household.payment_set.exists():
                logger.info(f"Skipping {household.id} because it has payments")
                continue
            else:
                households_to_remove.append(household)
        for duplicate in households_to_remove:
            duplicate.delete(soft=False)

        if i % 100 == 0:
            logger.info(f"Processed {i}/{households_with_duplicates.count()} households")
