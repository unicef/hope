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
        target_population__status__in=[
            TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE,
            TargetPopulation.STATUS_SENDING_TO_CASH_ASSIST,
            TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
        ]
    )

    # Program cannot be DRAFT or FINISHED
    q_program_status = Q(target_population__program__status=Program.ACTIVE)

    qs = list(
        HouseholdSelection.objects.select_related("target_population", "target_population__program")
        .filter(q_target_population_status & q_program_status)
        .values_list("household_id", "target_population__program__id")
    )

    households_to_update = []
    individuals_to_update = []

    i, pages = 0, len(qs) // batch_size + 1
    try:
        while i <= pages:
            logger.info(f"Processing {i}/{pages} page")

            for household_id, program_id in qs:
                household = Household.objects.get(id=household_id)
                household.program_id = program_id
                households_to_update.append(household)

                individuals = Individual.objects.filter(household_id=household_id)
                for individual in individuals:
                    individual.program_id = program_id
                    individuals_to_update.append(individual)

                if i % batch_size == 0:
                    Household.objects.bulk_update(households_to_update, ["program_id"])
                    Individual.objects.bulk_update(individuals_to_update, ["program_id"])
                    households_to_update = []
                    individuals_to_update = []

            i += 1
    except Exception:
        logger.error("Adding program do population failed")
        raise
