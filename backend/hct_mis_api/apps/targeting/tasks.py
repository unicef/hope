import logging

from django.db.transaction import atomic
from django.utils import timezone

from hct_mis_api.apps.core.celery import app

from ..targeting.models import HouseholdSelection, TargetPopulation

logger = logging.getLogger(__name__)


@app.task()
def target_population_apply_steficon(target_population_id):
    try:
        from steficon.models import RuleCommit

        target_population = TargetPopulation.objects.get(pk=target_population_id)
        rule: RuleCommit = target_population.steficon_rule
        try:
            target_population.status = TargetPopulation.STATUS_STEFICON_RUN
            target_population.steficon_applied_date = timezone.now()
            target_population.save()
            with atomic():
                entry: HouseholdSelection
                for entry in target_population.selections.all():
                    result = rule.execute({"household": entry.household})
                    entry.vulnerability_score = result.value
                    entry.save()
            target_population.status = TargetPopulation.STATUS_STEFICON_COMPLETED
        except Exception as e:
            target_population.status = TargetPopulation.STATUS_STEFICON_ERROR
        finally:
            target_population.save()
    except Exception as e:
        logger.exception(e)
