import importlib
from typing import Any

from django.apps import apps as django_apps
import pytest

from hope.models import AsyncJob

migration_module = importlib.import_module("hope.apps.core.migrations.0034_migration")


@pytest.fixture
def legacy_payment_notification_job(db: Any) -> AsyncJob:
    return AsyncJob.objects.create(
        job_name="send_payment_notification_emails_async_task",
        config={"action_date_formatted": "3 September 2026"},
    )


@pytest.fixture
def legacy_pdu_notification_job(db: Any) -> AsyncJob:
    return AsyncJob.objects.create(
        job_name="send_pdu_online_edit_notification_emails_async_task",
        config={"action_date_formatted": "3 September 2026"},
    )


@pytest.fixture
def current_notification_job(db: Any) -> AsyncJob:
    return AsyncJob.objects.create(
        job_name="send_payment_notification_emails_async_task",
        config={
            "action_date": "2026-09-03T12:30:00+00:00",
            "action_date_formatted": "3 September 2026",
        },
    )


@pytest.fixture
def unrelated_legacy_job(db: Any) -> AsyncJob:
    return AsyncJob.objects.create(
        job_name="another_async_task",
        config={"action_date_formatted": "3 September 2026"},
    )


@pytest.mark.parametrize(
    "job_fixture_name",
    ["legacy_payment_notification_job", "legacy_pdu_notification_job"],
)
def test_backfill_uses_job_creation_datetime(
    job_fixture_name: str,
    request: pytest.FixtureRequest,
) -> None:
    job = request.getfixturevalue(job_fixture_name)

    migration_module.backfill_notification_action_dates(django_apps, None)
    job.refresh_from_db()

    assert job.config["action_date"] == job.datetime_created.isoformat()
    assert job.config["action_date_formatted"] == "3 September 2026"


def test_backfill_preserves_existing_action_date(current_notification_job: AsyncJob) -> None:
    migration_module.backfill_notification_action_dates(django_apps, None)
    current_notification_job.refresh_from_db()

    assert current_notification_job.config["action_date"] == "2026-09-03T12:30:00+00:00"


def test_backfill_ignores_other_job_types(unrelated_legacy_job: AsyncJob) -> None:
    migration_module.backfill_notification_action_dates(django_apps, None)
    unrelated_legacy_job.refresh_from_db()

    assert "action_date" not in unrelated_legacy_job.config
