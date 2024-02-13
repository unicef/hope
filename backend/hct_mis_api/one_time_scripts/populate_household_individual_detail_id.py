import logging
from typing import Optional

from django.core.paginator import Paginator

from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
)

logger = logging.getLogger(__name__)


def update_detail_id(
    model_to_update: [Household, ImportedHousehold, Individual, ImportedIndividual], batch_size: Optional = 1000
) -> None:
    qs_with_kobo_asset_id = model_to_update.objects.exclude(kobo_asset_id="")
    qs_with_row_id = model_to_update.objects.exclude(row_id__isnull=True)

    for qs, field_name in [(qs_with_kobo_asset_id, "kobo_asset_id"), (qs_with_row_id, "row_id")]:
        paginator = Paginator(qs.order_by("id"), batch_size)
        for page_n in paginator.page_range:
            obj_list = []
            for obj in paginator.page(page_n).object_list:
                detail_id = getattr(obj, field_name, None)
                if detail_id:
                    obj.detail_id = detail_id
                    obj_list.append(obj)
            model_to_update.objects.bulk_update(obj_list, ["detail_id"])


def populate_household_individual_detail_id(batch_size: Optional[int] = 1000) -> None:
    for model in [Household, ImportedHousehold, Individual, ImportedIndividual]:
        logger.info(f"Updating {model}")
        update_detail_id(model, batch_size)

    logger.info("Finished updating detail_id")
