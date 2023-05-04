import logging
from typing import Any, Dict
from uuid import UUID

from django.core.cache import cache
from django.db import transaction
from django.db.transaction import atomic
from django.utils import timezone

from celery.exceptions import TaskError
from concurrency.api import disable_concurrency
from sentry_sdk import configure_scope

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.household.forms import CreateTargetPopulationTextForm
from hct_mis_api.apps.registration_datahub.celery_tasks import locked_cache
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation
from hct_mis_api.apps.utils.sentry import sentry_tags

from .services.targeting_stats_refresher import full_rebuild, refresh_stats

logger = logging.getLogger(__name__)


@app.task(bind=True, queue="priority", default_retry_delay=60, max_retries=3)
@sentry_tags
def target_population_apply_steficon(self: Any, target_population_id: UUID) -> None:
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
        raise self.retry(exc=e)
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
        raise self.retry(exc=e)


@app.task(bind=True, queue="priority", default_retry_delay=60, max_retries=3)
def target_population_rebuild_stats(self: Any, target_population_id: UUID) -> None:
    with cache.lock(
        f"target_population_rebuild_stats_{target_population_id}", blocking_timeout=60 * 10, timeout=60 * 60 * 2
    ):
        target_population = TargetPopulation.objects.get(pk=target_population_id)
        target_population.build_status = TargetPopulation.BUILD_STATUS_BUILDING
        target_population.save()
        try:
            with transaction.atomic():
                target_population = refresh_stats(target_population)
                target_population.save()
        except Exception as e:
            logger.exception(e)
            target_population.refresh_from_db()
            target_population.build_status = TargetPopulation.BUILD_STATUS_FAILED
            target_population.save()
            raise self.retry(exc=e)


@app.task(bind=True, queue="priority", default_retry_delay=60, max_retries=3)
def target_population_full_rebuild(self: Any, target_population_id: UUID) -> None:
    with cache.lock(
        f"target_population_full_rebuild_{target_population_id}", blocking_timeout=60 * 10, timeout=60 * 60 * 2
    ):
        target_population = TargetPopulation.objects.get(pk=target_population_id)
        target_population.build_status = TargetPopulation.BUILD_STATUS_BUILDING
        target_population.save()
        try:
            with transaction.atomic():
                if not target_population.is_open():
                    raise Exception("Target population is not in open status")
                target_population = full_rebuild(target_population)
                target_population.save()
        except Exception as e:
            logger.exception(e)
            target_population.refresh_from_db()
            target_population.build_status = TargetPopulation.BUILD_STATUS_FAILED
            target_population.save()
            raise self.retry(exc=e)


@app.task
@sentry_tags
def check_send_tp_periodic_task() -> bool:
    from hct_mis_api.apps.utils.celery_manager import send_tp_celery_manager

    with locked_cache(key="celery_manager_periodic_task") as locked:
        if not locked:
            return True
        send_tp_celery_manager.execute()
    return True


@app.task()
@sentry_tags
def create_tp_from_list(form_data: Dict[str, str], user_id: str) -> None:
    form = CreateTargetPopulationTextForm(form_data)
    if form.is_valid():
        ba = form.cleaned_data["business_area"]
        population = form.cleaned_data["criteria"]
        try:
            with atomic():
                tp = TargetPopulation.objects.create(
                    targeting_criteria=form.cleaned_data["targeting_criteria"],
                    created_by=User.objects.get(pk=user_id),
                    name=form.cleaned_data["name"],
                    business_area=ba,
                )
                tp.households.set(population)
                refresh_stats(tp)
                tp.save()
        except Exception as e:
            logger.exception(e)
    else:
        error_message = f"Form validation failed: {form.errors}."
        logger.error(error_message)
        raise TaskError(error_message)
