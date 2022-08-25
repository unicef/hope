import logging
from contextlib import contextmanager

from concurrency.api import disable_concurrency
from django.core.cache import cache
from django.db import transaction
from django.db.transaction import atomic
from django.utils import timezone
from redis.exceptions import LockError
from sentry_sdk import configure_scope

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.sentry import sentry_tags
from ..household.models import Household
from ..targeting.models import HouseholdSelection, TargetPopulation

logger = logging.getLogger(__name__)


@contextmanager
def locked_cache(key, blocking_timeout=30, timeout=60 * 60 * 24):
    try:
        with cache.lock(key, blocking_timeout=blocking_timeout, timeout=timeout) as lock:
            yield
    except LockError as e:
        logger.exception(f"Couldn't lock cache for key '{key}'. Failed with: {e}")
    else:
        if lock.locked():
            lock.release()


@app.task(queue="priority")
@sentry_tags
def target_population_apply_steficon(target_population_id):
    from hct_mis_api.apps.steficon.models import RuleCommit

    try:
        target_population = TargetPopulation.objects.get(pk=target_population_id)
        with configure_scope() as scope:
            scope.set_tag("business_area", target_population.business_area)

            rule: RuleCommit = target_population.steficon_rule
            if not rule:
                raise Exception("TargetPopulation does not have a Steficon rule")
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
        with disable_concurrency(target_population):
            target_population.save()
    except Exception as e:
        logger.exception(e)
        target_population.steficon_applied_date = timezone.now()
        target_population.status = TargetPopulation.STATUS_STEFICON_ERROR
        target_population.save()
        raise


@app.task(queue="priority")
def target_population_rebuild_stats(target_population_id):
    with cache.lock(
        f"target_population_rebuild_stats_{target_population_id}", blocking_timeout=60 * 10, timeout=60 * 60 * 2
    ):
        target_population = TargetPopulation.objects.get(pk=target_population_id)
        target_population.build_status = TargetPopulation.BUILD_STATUS_BUILDING
        target_population.save()
        try:
            with transaction.atomic():
                target_population.refresh_stats()
                target_population.build_status = TargetPopulation.BUILD_STATUS_OK
                target_population.built_at = timezone.now()
                target_population.save()
        except Exception as e:
            logger.exception(e)
            target_population.refresh_from_db()
            target_population.build_status = TargetPopulation.BUILD_STATUS_FAILED
            target_population.save()


@app.task(queue="priority")
def target_population_full_rebuild(target_population_id):
    with cache.lock(
        f"target_population_full_rebuild_{target_population_id}", blocking_timeout=60 * 10, timeout=60 * 60 * 2
    ):
        target_population = TargetPopulation.objects.get(pk=target_population_id)
        target_population.build_status = TargetPopulation.BUILD_STATUS_BUILDING
        target_population.save()
        try:
            with transaction.atomic():
                if not target_population.is_open():
                    raise Exception('Target population is not in open status')
                target_population.full_rebuild()
                target_population.build_status = TargetPopulation.BUILD_STATUS_OK
                target_population.built_at = timezone.now()
                target_population.save()
        except Exception as e:
            logger.exception(e)
            target_population.refresh_from_db()
            target_population.build_status = TargetPopulation.BUILD_STATUS_FAILED
            target_population.save()
