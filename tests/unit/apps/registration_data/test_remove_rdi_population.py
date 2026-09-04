from unittest.mock import PropertyMock, patch
import uuid

from django.db import OperationalError, connection, connections
from django.db.models.deletion import ProtectedError
from django.test import TestCase
import psycopg2
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.api.caches import get_or_create_cache_key
from hope.apps.core.celery_tasks import NonRetriableTaskError
from hope.apps.registration_data.celery_tasks import (
    remove_rdi_population_async_task,
    remove_rdi_population_async_task_action,
    remove_rdi_population_on_failure,
)
from hope.apps.registration_data.signals import invalidate_rdi_cache
from hope.apps.registration_data.tasks.rdi_removal_async import RdiPopulationRemoval
from hope.models import AsyncRetryJob, RegistrationDataImport

pytestmark = pytest.mark.django_db

CALLBACK_URL = "https://cw.example.com/api/rdi/callback/abc123"
SIGNED_TOKEN = "signed-token-abc123"


def _rdi_version_key(business_area_slug: str, program_code: str) -> str:
    ba_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    return f"{business_area_slug}:{ba_version}:{program_code}:registration_data_import_list"


@pytest.fixture
def program():
    return ProgramFactory(business_area=BusinessAreaFactory(name="Afghanistan"))


def test_wipe_enqueue_queues_wipe_with_config(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    queued = object()
    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.requeue", return_value=queued) as requeue:
        result = remove_rdi_population_async_task(rdi, callback_url=CALLBACK_URL, signed_token=SIGNED_TOKEN)

    assert result is queued
    config = requeue.call_args.kwargs["config"]
    assert config["registration_data_import_id"] == str(rdi.id)
    assert config["callback_url"] == CALLBACK_URL
    assert config["signed_token"] == SIGNED_TOKEN
    assert config["on_failure_action"] == "hope.apps.registration_data.celery_tasks.remove_rdi_population_on_failure"
    assert "country_workspace_id" not in config


def test_wipe_enqueue_skips_when_wipe_already_running(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue"):
        first = remove_rdi_population_async_task(rdi, callback_url=CALLBACK_URL, signed_token=SIGNED_TOKEN)
    assert first is not None
    jobs_before = AsyncRetryJob.objects.count()

    with patch.object(AsyncRetryJob, "task_status", new_callable=PropertyMock, return_value="STARTED"):
        second = remove_rdi_population_async_task(rdi, callback_url=CALLBACK_URL, signed_token=SIGNED_TOKEN)

    assert second is None
    assert AsyncRetryJob.objects.count() == jobs_before  # no second wipe job was queued alongside the live one


def test_wipe_action_calls_wipe_and_notifies(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(
        config={
            "registration_data_import_id": str(rdi.id),
            "callback_url": CALLBACK_URL,
            "signed_token": SIGNED_TOKEN,
            "program_id": str(program.id),
        }
    )

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population") as wipe,
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
    ):
        remove_rdi_population_async_task_action(job)

    wipe.assert_called_once()
    assert wipe.call_args.args[0].id == rdi.id
    assert wipe.call_args.kwargs == {"delete_rdi": True, "swallow_es_errors": True}
    notify.assert_called_once_with(CALLBACK_URL, SIGNED_TOKEN, program)


def test_wipe_action_keeps_scheduled_status_during_wipe(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(
        config={
            "registration_data_import_id": str(rdi.id),
            "callback_url": CALLBACK_URL,
            "signed_token": SIGNED_TOKEN,
            "program_id": str(program.id),
        }
    )
    seen = {}

    def capture_status(*args: object, **kwargs: object) -> None:
        seen["status"] = RegistrationDataImport.objects.get(id=rdi.id).status

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population", side_effect=capture_status),
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
    ):
        remove_rdi_population_async_task_action(job)

    assert seen.get("status") == RegistrationDataImport.DELETE_SCHEDULED  # no transient marker; row stays until gone
    notify.assert_called_once_with(CALLBACK_URL, SIGNED_TOKEN, program)


def test_wipe_action_idempotent_when_row_gone(program) -> None:
    job = AsyncRetryJob(
        config={
            "registration_data_import_id": "00000000-0000-0000-0000-000000000000",
            "callback_url": CALLBACK_URL,
            "signed_token": SIGNED_TOKEN,
            "program_id": str(program.id),
        }
    )

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population") as wipe,
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
    ):
        remove_rdi_population_async_task_action(job)

    wipe.assert_not_called()
    notify.assert_called_once_with(CALLBACK_URL, SIGNED_TOKEN, program)


def test_wipe_action_merged_under_lock_fails(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.MERGED
    )
    job = AsyncRetryJob(
        config={
            "registration_data_import_id": str(rdi.id),
            "callback_url": CALLBACK_URL,
            "signed_token": SIGNED_TOKEN,
            "program_id": str(program.id),
        }
    )

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population") as wipe,
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
        pytest.raises(NonRetriableTaskError),
    ):
        remove_rdi_population_async_task_action(job)

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.MERGED
    wipe.assert_not_called()
    notify.assert_not_called()


def test_wipe_action_protected_error_sets_failed(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(
        config={
            "registration_data_import_id": str(rdi.id),
            "callback_url": CALLBACK_URL,
            "signed_token": SIGNED_TOKEN,
            "program_id": str(program.id),
        }
    )

    with (
        patch(
            "hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population",
            side_effect=ProtectedError("rdi_has_dependents", set()),
        ),
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
        pytest.raises(NonRetriableTaskError),
    ):
        remove_rdi_population_async_task_action(job)

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DELETE_FAILED
    assert rdi.error_message
    notify.assert_not_called()


def test_wipe_action_transient_error_retries(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(
        config={
            "registration_data_import_id": str(rdi.id),
            "callback_url": CALLBACK_URL,
            "signed_token": SIGNED_TOKEN,
            "program_id": str(program.id),
        }
    )

    with (
        patch(
            "hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population",
            side_effect=RuntimeError("transient db hiccup"),
        ),
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
        pytest.raises(RuntimeError, match="transient db hiccup"),
    ):
        remove_rdi_population_async_task_action(job)

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DELETE_SCHEDULED  # untouched on a transient failure → retried
    notify.assert_not_called()


def test_wipe_on_failure_hook_sets_failed(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(
        config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL, "signed_token": SIGNED_TOKEN}
    )

    with patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify:
        remove_rdi_population_on_failure(job, RuntimeError("retries exhausted"))

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DELETE_FAILED
    assert rdi.error_message == "retries exhausted"
    notify.assert_not_called()


def test_fail_marks_status_and_invalidates_cache(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    version_key = _rdi_version_key(program.business_area.slug, program.code)
    initial_version = get_or_create_cache_key(version_key, 0)

    with (
        TestCase.captureOnCommitCallbacks(execute=True),
        patch(
            "hope.apps.registration_data.tasks.rdi_removal_async.invalidate_rdi_cache",
            wraps=invalidate_rdi_cache,
        ) as invalidate,
    ):
        RdiPopulationRemoval.mark_failed(str(rdi.id), reason="boom")

    invalidate.assert_called_once_with(program.business_area.slug, program.code)

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DELETE_FAILED
    assert rdi.error_message == "boom"

    new_version = get_or_create_cache_key(version_key, 0)
    assert new_version == initial_version + 1


def test_fail_on_missing_rdi_is_a_noop(program) -> None:
    missing_id = str(uuid.uuid4())

    with patch("hope.apps.registration_data.tasks.rdi_removal_async.invalidate_rdi_cache") as invalidate:
        result = RdiPopulationRemoval.mark_failed(missing_id, reason="boom")

    assert result is None
    invalidate.assert_not_called()
    assert not RegistrationDataImport.objects.filter(id=missing_id).exists()


@pytest.mark.django_db(transaction=True)
def test_wipe_blocks_on_a_held_row_lock() -> None:
    ba = BusinessAreaFactory(name="Afghanistan")
    program = ProgramFactory(business_area=ba)
    rdi = RegistrationDataImportFactory(
        business_area=ba, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(
        config={
            "registration_data_import_id": str(rdi.id),
            "callback_url": CALLBACK_URL,
            "signed_token": SIGNED_TOKEN,
            "program_id": str(program.id),
        }
    )

    db = connections["default"].settings_dict
    locker = psycopg2.connect(
        dbname=db["NAME"], user=db["USER"], password=db["PASSWORD"], host=db["HOST"], port=db["PORT"]
    )
    try:
        with locker.cursor() as cur:
            cur.execute(
                f"SELECT id FROM {RegistrationDataImport._meta.db_table} WHERE id = %s FOR UPDATE",
                [str(rdi.id)],
            )
            with connection.cursor() as c:
                c.execute("SET lock_timeout = '750ms'")
            with (
                patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task"),
                pytest.raises(OperationalError),  # blocking select_for_update hits the held lock
            ):
                remove_rdi_population_async_task_action(job)
    finally:
        with connection.cursor() as c:
            c.execute("SET lock_timeout = DEFAULT")
        locker.rollback()
        locker.close()

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DELETE_SCHEDULED  # never advanced past the blocked lock
