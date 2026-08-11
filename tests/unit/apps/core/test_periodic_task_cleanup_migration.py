from importlib import import_module

from django.apps import apps as django_apps
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import pytest

from hope.apps.core.tasks_schedules import TASKS_SCHEDULES

migration = import_module("hope.apps.core.migrations.0032_migration")


@pytest.fixture
def crontab() -> CrontabSchedule:
    return CrontabSchedule.objects.create(minute="0", hour="0")


@pytest.fixture
def already_cleaned_rows(crontab: CrontabSchedule) -> list[PeriodicTask]:
    return PeriodicTask.objects.bulk_create(
        [
            PeriodicTask(
                name="cleanup_inactive_program_indexes_task",
                task="hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_async_task",
                crontab=crontab,
                total_run_count=17,
            ),
            PeriodicTask(
                name="update_dashboard_figures_async_task",
                task="hope.apps.dashboard.celery_tasks.update_dashboard_figures",
                crontab=crontab,
                total_run_count=4,
            ),
            PeriodicTask(
                name="some leftover row pointing at live code",
                task="hope.apps.core.celery_tasks.recover_missing_async_jobs_async_task",
                crontab=crontab,
                total_run_count=99,
            ),
        ]
    )


def test_retired_paths_never_overlap_current_schedule() -> None:
    current_paths = {entry["task"] for entry in TASKS_SCHEDULES.values()}

    assert migration.RETIRED_TASK_PATHS & current_paths == set()


@pytest.mark.django_db
def test_row_with_live_name_and_stale_task_is_repointed(crontab: CrontabSchedule) -> None:
    PeriodicTask.objects.create(
        name="cleanup_inactive_program_indexes_task",
        task="hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_task",
        crontab=crontab,
    )

    migration.repoint_and_drop_stale_periodic_tasks(django_apps, None)

    assert (
        PeriodicTask.objects.get(name="cleanup_inactive_program_indexes_task").task
        == "hope.apps.household.celery_tasks.cleanup_indexes_in_inactive_programs_async_task"
    )


@pytest.mark.django_db
def test_row_pointing_at_retired_task_is_deleted(crontab: CrontabSchedule) -> None:
    PeriodicTask.objects.create(
        name="periodic_sync_payment_gateway_fsp",
        task="hope.apps.payment.celery_tasks.periodic_sync_payment_gateway_fsp",
        crontab=crontab,
    )

    migration.repoint_and_drop_stale_periodic_tasks(django_apps, None)

    assert not PeriodicTask.objects.filter(name="periodic_sync_payment_gateway_fsp").exists()


@pytest.mark.django_db
def test_row_pointing_at_live_task_is_untouched(crontab: CrontabSchedule) -> None:
    PeriodicTask.objects.create(
        name="aurora extract for org X",
        task="hope.contrib.aurora.celery_tasks.extract_records_async_task",
        crontab=crontab,
    )

    migration.repoint_and_drop_stale_periodic_tasks(django_apps, None)

    assert PeriodicTask.objects.filter(name="aurora extract for org X").exists()


@pytest.mark.django_db
def test_live_dashboard_row_and_its_duplicate_are_resolved(crontab: CrontabSchedule) -> None:
    live = PeriodicTask.objects.create(
        name="update_dashboard_figures_async_task",
        task="hope.apps.dashboard.celery_tasks.update_dashboard_figures_async_task",
        crontab=crontab,
        total_run_count=8,
    )
    PeriodicTask.objects.create(
        name="update_dashboard_figures_task",
        task="hope.apps.dashboard.celery_tasks.update_dashboard_figures",
        crontab=crontab,
    )

    migration.repoint_and_drop_stale_periodic_tasks(django_apps, None)

    reloaded = PeriodicTask.objects.get(pk=live.pk)
    assert reloaded.task == "hope.apps.dashboard.celery_tasks.update_dashboard_figures"
    assert reloaded.total_run_count == 8
    assert not PeriodicTask.objects.filter(name="update_dashboard_figures_task").exists()


@pytest.mark.django_db
def test_already_cleaned_database_is_left_untouched(already_cleaned_rows: list[PeriodicTask]) -> None:
    before = list(PeriodicTask.objects.order_by("name").values("name", "task", "total_run_count"))

    migration.repoint_and_drop_stale_periodic_tasks(django_apps, None)

    assert list(PeriodicTask.objects.order_by("name").values("name", "task", "total_run_count")) == before


@pytest.mark.django_db
def test_edited_duplicate_dashboard_row_is_kept(crontab: CrontabSchedule) -> None:
    PeriodicTask.objects.create(
        name="update_dashboard_figures_task",
        task="hope.apps.core.celery_tasks.recover_missing_async_jobs_async_task",
        crontab=crontab,
    )

    migration.repoint_and_drop_stale_periodic_tasks(django_apps, None)

    assert PeriodicTask.objects.filter(name="update_dashboard_figures_task").exists()
