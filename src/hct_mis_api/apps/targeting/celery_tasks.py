import logging
from typing import Any, Dict
from uuid import UUID

from django.core.cache import cache
from django.db import transaction
from django.db.transaction import atomic
from django.utils import timezone

from celery.exceptions import TaskError
from concurrency.api import disable_concurrency

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.household.forms import CreateTargetPopulationTextForm
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation
from hct_mis_api.apps.targeting.services.targeting_stats_refresher import (
    full_rebuild,
    refresh_stats,
)
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


@app.task(bind=True, queue="priority", default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def target_population_apply_steficon(self: Any, target_population_id: UUID) -> None:
    from hct_mis_api.apps.steficon.models import RuleCommit

    try:
        target_population = TargetPopulation.objects.get(pk=target_population_id)
        set_sentry_business_area_tag(target_population.business_area.name)

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
                result = rule.execute(
                    {
                        "household": entry.household,
                        "target_population": target_population,
                    }
                )
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
@log_start_and_end
@sentry_tags
def target_population_rebuild_stats(self: Any, target_population_id: UUID) -> None:
    with cache.lock(
        f"target_population_rebuild_stats_{target_population_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        target_population = TargetPopulation.objects.get(pk=target_population_id)
        set_sentry_business_area_tag(target_population.business_area.name)
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
@log_start_and_end
@sentry_tags
def target_population_full_rebuild(self: Any, target_population_id: UUID) -> None:
    with cache.lock(
        f"target_population_full_rebuild_{target_population_id}",
        blocking_timeout=60 * 10,
        timeout=60 * 60 * 2,
    ):
        target_population = TargetPopulation.objects.get(pk=target_population_id)
        set_sentry_business_area_tag(target_population.business_area.name)
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


@app.task()
@log_start_and_end
@sentry_tags
def create_tp_from_list(form_data: Dict[str, str], user_id: str, program_pk: str) -> None:
    program = Program.objects.get(pk=program_pk)
    form = CreateTargetPopulationTextForm(form_data, program=program)
    if form.is_valid():
        population = form.cleaned_data["criteria"]
        set_sentry_business_area_tag(program.business_area.name)
        try:
            with atomic():
                tp = TargetPopulation.objects.create(
                    targeting_criteria=form.cleaned_data["targeting_criteria"],
                    created_by=User.objects.get(pk=user_id),
                    name=form.cleaned_data["name"],
                    business_area=program.business_area,
                    program=program,
                    program_cycle=form.cleaned_data["program_cycle"],
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
