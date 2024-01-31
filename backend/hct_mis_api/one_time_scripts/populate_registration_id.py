import logging
import math

from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.aurora.models import Record

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


def populate_registration_ids() -> None:
    registration_ids = Record.objects.values_list("registration", flat=True).distinct()
    logger.info(f"Populating Registration ID (Aurora) {list(registration_ids)}")
    logger.info(f"Page size {BATCH_SIZE}")
    for registration_id in registration_ids:
        populate_registration_id(registration_id)


def populate_registration_id(registration_id: int) -> None:
    logger.info(f"Start populate id: {registration_id}")
    qs = Record.objects.filter(registration=registration_id).order_by("timestamp").values_list("source_id", flat=True)

    i = 0
    page_numbers = math.ceil(qs.count() / BATCH_SIZE)
    while source_ids := qs[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]:
        logger.info(f"Populating page {i+1} of {page_numbers}")
        Household.objects.filter(
            registration_data_import__data_source=RegistrationDataImport.FLEX_REGISTRATION,
            kobo_asset_id__in=list(source_ids),
        ).update(registration_id=registration_id)
        Individual.objects.filter(
            registration_data_import__data_source=RegistrationDataImport.FLEX_REGISTRATION,
            kobo_asset_id__in=list(source_ids),
        ).update(registration_id=registration_id)
        i += 1

    logger.info(f"Finish populate id: {registration_id}")
