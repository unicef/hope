from importlib import import_module

from django.apps import apps as django_apps
from django.db import connection
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import pytest

from hope.apps.core.tasks_schedules import TASKS_SCHEDULES

pytestmark = pytest.mark.django_db

migration = import_module("hope.apps.payment.migrations.0088_migration")


@pytest.fixture
def overdue_emails_row_before_the_rename() -> PeriodicTask:
    return PeriodicTask.objects.create(
        name="periodic_send_payment_plan_reconciliation_overdue_emails_async_task",
        task="hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task",
        crontab=CrontabSchedule.objects.create(minute="0", hour="2"),
    )


@pytest.fixture
def overdue_emails_row_after_the_rename() -> PeriodicTask:
    return PeriodicTask.objects.create(
        name="periodic_send_payment_list_reconciliation_overdue_emails_async_task",
        task="hope.apps.payment.celery_tasks.periodic_send_payment_list_reconciliation_overdue_emails_async_task",
        crontab=CrontabSchedule.objects.create(minute="0", hour="2"),
    )


def test_forwards_renames_the_periodic_task_row_to_the_schedule_key_beat_looks_it_up_by(
    overdue_emails_row_before_the_rename: PeriodicTask,
) -> None:
    migration.forwards(django_apps, connection.schema_editor())

    overdue_emails_row_before_the_rename.refresh_from_db()
    assert (
        overdue_emails_row_before_the_rename.name
        == "periodic_send_payment_list_reconciliation_overdue_emails_async_task"
    )
    assert (
        overdue_emails_row_before_the_rename.task
        == TASKS_SCHEDULES["periodic_send_payment_list_reconciliation_overdue_emails_async_task"]["task"]
    )


def test_backwards_gives_the_periodic_task_row_its_old_name_and_task(
    overdue_emails_row_after_the_rename: PeriodicTask,
) -> None:
    migration.backwards(django_apps, connection.schema_editor())

    overdue_emails_row_after_the_rename.refresh_from_db()
    assert (
        overdue_emails_row_after_the_rename.name
        == "periodic_send_payment_plan_reconciliation_overdue_emails_async_task"
    )
    assert (
        overdue_emails_row_after_the_rename.task
        == "hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task"
    )
