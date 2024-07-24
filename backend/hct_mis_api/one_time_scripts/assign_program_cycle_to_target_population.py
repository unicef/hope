import logging

from hct_mis_api.apps.program.models import ProgramCycle
from hct_mis_api.apps.targeting.models import TargetPopulation

logger = logging.getLogger(__name__)


def assign_program_cycle_to_target_population() -> None:
    BATCH_SIZE = 1000
    target_population = TargetPopulation.objects.all().only("id")
    target_population_count = target_population.count()
    target_population_ids = list(target_population.values_list("id", flat=True))

    for batch_start in range(0, target_population_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logger.info(f"Handling {batch_start} - {batch_end}/{target_population_count} Target Populations")

        processing_ids = target_population_ids[batch_start:batch_end]
        for tp_id in processing_ids:
            tp = TargetPopulation.objects.select_related("program").get(id=tp_id)

            program_cycle = ProgramCycle.objects.filter(program=tp.program).order_by("created_at").first()
            if not program_cycle:
                logger.error(f"Nof found ProgramCycle for Target Population {tp_id}")
                continue

            TargetPopulation.objects.filter(pk=tp_id).update(program_cycle=program_cycle)
