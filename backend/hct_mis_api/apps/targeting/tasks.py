import logging

from django.db.transaction import atomic
from django.utils import timezone

from hct_mis_api.apps.core.celery import app

from ..targeting.models import HouseholdSelection, TargetPopulation

logger = logging.getLogger(__name__)


@app.task()
def target_population_apply_steficon(target_population_id):
    from hct_mis_api.apps.steficon.models import RuleCommit

    try:
        target_population = TargetPopulation.objects.get(pk=target_population_id)
        rule: RuleCommit = target_population.steficon_rule
    except Exception as e:
        logger.exception(e)
        raise
    try:
        target_population.status = TargetPopulation.STATUS_STEFICON_RUN
        target_population.steficon_applied_date = timezone.now()
        target_population.save()
        updates = []
        with atomic():
            entry: HouseholdSelection
            for entry in target_population.selections.all():
                result = rule.execute({"household": entry.household, "target_population": target_population})
                entry.vulnerability_score = result.value
                updates.append(entry)
            HouseholdSelection.objects.bulk_update(updates, ["vulnerability_score"])
        target_population.status = TargetPopulation.STATUS_STEFICON_COMPLETED
        target_population.steficon_applied_date = timezone.now()
    except Exception as e:
        logger.exception(e)
        target_population.steficon_applied_date = timezone.now()
        target_population.status = TargetPopulation.STATUS_STEFICON_ERROR
    finally:
        target_population.save()
