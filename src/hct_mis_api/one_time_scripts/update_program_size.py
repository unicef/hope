import logging

from django.db.models import F, Func, OuterRef, Subquery

from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program

logger = logging.getLogger(__name__)


def update_program_size() -> None:
    logger.info("Updating programs")

    updated = Program.objects.all().update(
        household_count=Subquery(
            Household.objects.filter(program_id=OuterRef("pk"))
            .annotate(count=Func(F("id"), function="Count"))
            .values("count")
        ),
        individual_count=Subquery(
            Individual.objects.filter(program_id=OuterRef("pk"))
            .annotate(count=Func(F("id"), function="Count"))
            .values("count")
        ),
    )

    logger.info(f"Updated {updated} programs")
