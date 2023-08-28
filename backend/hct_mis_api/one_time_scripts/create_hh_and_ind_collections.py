import logging
from typing import Type, Union

from django.db.models import QuerySet

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import (
    Household,
    HouseholdCollection,
    Individual,
    IndividualCollection,
)

logger = logging.getLogger(__name__)


def create_hh_and_ind_collections() -> None:
    # Create representation collection for every household and individual already present in db
    _create_collections(Household, HouseholdCollection, "household_collection")
    _create_collections(Individual, IndividualCollection, "individual_collection")


def _create_collections(
    representation_model: Union[Type[Household], Type[Individual]],
    collection_model: Union[Type[HouseholdCollection], Type[IndividualCollection]],
    related_name: str,
) -> None:
    batch_size = 500
    for business_area in BusinessArea.objects.all():
        logger.info(
            f"Starting batch collection creation for {representation_model} in business area: {business_area.name}"
        )
        total_representations = representation_model.objects.filter(
            business_area=business_area,
            **{f"{related_name}__isnull": True},
        ).count()
        all_representations = representation_model.objects.filter(
            business_area=business_area,
            **{f"{related_name}__isnull": True},
        ).all()

        for batch_start in range(0, total_representations, batch_size):
            batch_end = batch_start + batch_size
            logging.info(
                f"{business_area.name}: {representation_model} batch {batch_start}-{batch_end}/{total_representations}"
            )
            representations = all_representations[batch_start:batch_end]
            _batch_create_collections(representation_model, collection_model, related_name, representations)
        logger.info(
            f"Finished batch collection creation for {representation_model} in business area: {business_area.name}"
        )


def _batch_create_collections(
    representation_model: Union[Type[Household], Type[Individual]],
    collection_model: Union[Type[HouseholdCollection], Type[IndividualCollection]],
    related_name: str,
    representations: QuerySet,
) -> None:
    # Create HouseholdCollection/IndividualCollection objects for every Household/Individual object
    collections = collection_model.objects.bulk_create([collection_model() for _ in representations])

    # Prepare a list of Household/Individual objects with corresponding HouseholdCollection/IndividualCollection objects
    representations_with_collection = [
        representation_model(**{"id": representation.id, related_name: collection})
        for representation, collection in zip(representations, collections)
    ]
    representation_model.objects.bulk_update(representations_with_collection, [related_name])
