"""
This migration scans HouseholdSelection data and adds program_id values to Household/Individual objects.
When this migration is successfully applied, program_id field should be updated (remove null=True, blank=True)
"""

import logging

from django.db.models import Q

from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation

logger = logging.getLogger(__name__)


def migrate_program_psql_db(batch_size: int = 500) -> None:
    # Targeting should be at least in READY status
    q_target_population_status = Q(
        status__in=[
            TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE,
            TargetPopulation.STATUS_SENDING_TO_CASH_ASSIST,
            TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
        ]
    )

    # Program cannot be in status DRAFT or FINISHED
    active_programs = Program.objects.filter(status=Program.ACTIVE)

    for program in active_programs:
        all_program_targeting_ids = list(
            TargetPopulation.objects.filter(q_target_population_status & Q(program_id=program.id)).values_list(
                "id", flat=True
            )
        )
        all_household_ids = list(
            HouseholdSelection.objects.filter(target_population_id__in=all_program_targeting_ids).values_list(
                "household_id", flat=True
            )
        )

        i, pages = 0, len(all_household_ids) // batch_size + 1
        try:
            while i <= pages:
                logger.info(f"Processing {i}/{pages} page")
                household_batch_ids = all_household_ids[i * batch_size : (i + 1) * batch_size]

                Household.objects.filter(id__in=household_batch_ids).update(program=program)
                Individual.objects.filter(household_id__in=household_batch_ids).update(program=program)

                i += 1

        except Exception:
            logger.error("Adding program do population failed")
            raise
