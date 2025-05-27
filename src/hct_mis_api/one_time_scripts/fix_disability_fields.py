import logging

from django.db.models import Q

from hct_mis_api.apps.household.models import (
    CANNOT_DO,
    DISABLED,
    LOT_DIFFICULTY,
    NOT_DISABLED,
    Individual,
)

logger = logging.getLogger(__name__)

disability_fields = [
    "seeing_disability",
    "hearing_disability",
    "physical_disability",
    "memory_disability",
    "selfcare_disability",
    "comms_disability",
]


def fix_disability_fields() -> None:
    logger.info("Fixing disability fields")

    params = Q()
    for field in disability_fields:
        params |= Q(**{field: CANNOT_DO})
        params |= Q(**{field: LOT_DIFFICULTY})

    updated = Individual.objects.filter(Q(params) & Q(disability=NOT_DISABLED)).update(disability=DISABLED)

    logger.info(f"Updated {updated} individuals")
