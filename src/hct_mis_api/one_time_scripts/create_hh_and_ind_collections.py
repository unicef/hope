import logging

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import (
    Household,
    HouseholdCollection,
    Individual,
    IndividualCollection,
)

logger = logging.getLogger(__name__)


def create_hh_and_ind_collections(business_area: BusinessArea | None = None) -> None:
    # Create representation collection for every household and individual already present in db
    business_area_name = business_area.name if business_area else None
    _create_collections(Household, HouseholdCollection, "household_collection", business_area_name)
    _create_collections(Individual, IndividualCollection, "individual_collection", business_area_name)


def _create_collections(
    representation_model: type[Household] | type[Individual],
    collection_model: type[HouseholdCollection] | type[IndividualCollection],
    related_name: str,
    business_area_name: str | None = None,
) -> None:
    batch_size = 500
    business_areas = (
        BusinessArea.objects.filter(name=business_area_name) if business_area_name else BusinessArea.objects.all()
    )
    for business_area in business_areas:
        logger.info(
            f"Starting batch collection creation for {representation_model} in business area: {business_area.name}"
        )
        all_objects_ids = list(
            representation_model.objects.filter(
                business_area=business_area,
                **{f"{related_name}__isnull": True},
            )
            .order_by("id")
            .values_list("id", flat=True)
        )
        all_objects_count = len(all_objects_ids)

        for batch_start in range(0, all_objects_count, batch_size):
            batch_end = batch_start + batch_size
            logging.info(
                f"{business_area.name}: {representation_model} batch {batch_start}-{batch_end}/{all_objects_count}"
            )
            batched_ids = all_objects_ids[batch_start:batch_end]
            representations = list(representation_model.objects.filter(id__in=batched_ids))
            _batch_create_collections(representation_model, collection_model, related_name, representations)
        logger.info(
            f"Finished batch collection creation for {representation_model} in business area: {business_area.name}"
        )


def _batch_create_collections(
    representation_model: type[Household] | type[Individual],
    collection_model: type[HouseholdCollection] | type[IndividualCollection],
    related_name: str,
    representations: list[Household | Individual],
) -> None:
    # Create HouseholdCollection/IndividualCollection objects for every Household/Individual object
    collections = collection_model.objects.bulk_create([collection_model() for _ in representations])

    # Prepare a list of Household/Individual objects with corresponding HouseholdCollection/IndividualCollection objects
    representations_with_collection = [
        representation_model(**{"id": representation.id, related_name: collection})
        for representation, collection in zip(representations, collections)
    ]
    representation_model.objects.bulk_update(representations_with_collection, [related_name])
