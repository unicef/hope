import logging

from django.db.transaction import atomic

from hct_mis_api.apps.core.celery import app

from ..targeting.models import HouseholdSelection, TargetPopulation
from .models import RuleCommit

logger = logging.getLogger(__name__)


@app.task()
def queue(rule_commit_id, target_population_id):
    try:
        rule = RuleCommit.objects.get(pk=rule_commit_id)
        target_population = TargetPopulation.objects.get(pk=target_population_id)

        with atomic():
            notify_to = [target_population.created_by.email]
            entry: HouseholdSelection
            for entry in target_population.selections.all():
                result = rule.execute({"context": entry})
                if ["vulnerability_score"] in pts:
                    entry.vulnerability_score

    except Exception as e:
        logger.exception(e)
