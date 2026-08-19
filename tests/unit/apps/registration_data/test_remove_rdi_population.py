import threading
from unittest.mock import PropertyMock, patch

from django.core.cache import cache
from django.db import OperationalError, connection, connections
from django.db.models.deletion import ProtectedError
from django.test.utils import CaptureQueriesContext
import psycopg2
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.celery_tasks import NonRetriableTaskError
from hope.apps.registration_data.celery_tasks import (
    merge_registration_data_import_async_task_action,
    remove_rdi_population_async_task,
    remove_rdi_population_async_task_action,
    remove_rdi_population_on_failure,
)
from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask
from hope.apps.registration_data.tasks.rdi_removal_async import RdiPopulationRemoval
from hope.models import AsyncRetryJob, RegistrationDataImport


def _merge_key(rdi_id: object) -> str:
    return f"merge_registration_data_import_async_task-{rdi_id}"


pytestmark = pytest.mark.django_db

CALLBACK_URL = "https://cw.example.com/api/rdi/callback/abc123"


@pytest.fixture
def program():
    return ProgramFactory(business_area=BusinessAreaFactory(name="Afghanistan"))


def test_wipe_enqueue_queues_wipe_with_config(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    queued = object()
    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.requeue", return_value=queued) as requeue:
        result = remove_rdi_population_async_task(rdi, callback_url=CALLBACK_URL)

    assert result is queued
    config = requeue.call_args.kwargs["config"]
    assert config["registration_data_import_id"] == str(rdi.id)
    assert config["callback_url"] == CALLBACK_URL
    assert config["on_failure_action"] == "hope.apps.registration_data.celery_tasks.remove_rdi_population_on_failure"
    assert "country_workspace_id" not in config


def test_wipe_enqueue_skips_when_wipe_already_running(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue"):
        first = remove_rdi_population_async_task(rdi, callback_url=CALLBACK_URL)
    assert first is not None
    jobs_before = AsyncRetryJob.objects.count()

    # the first job is now live (STARTED) → requeue must not start a second one alongside it
    with patch.object(AsyncRetryJob, "task_status", new_callable=PropertyMock, return_value="STARTED"):
        second = remove_rdi_population_async_task(rdi, callback_url=CALLBACK_URL)

    assert second is None
    assert AsyncRetryJob.objects.count() == jobs_before  # no second wipe job was queued alongside the live one


def test_wipe_action_calls_wipe_and_notifies(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population") as wipe,
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
    ):
        remove_rdi_population_async_task_action(job)

    wipe.assert_called_once()
    assert wipe.call_args.args[0].id == rdi.id
    assert wipe.call_args.kwargs == {"delete_rdi": True, "swallow_es_errors": True}
    notify.assert_called_once_with(CALLBACK_URL)


def test_wipe_action_keeps_scheduled_status_during_wipe(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})
    seen = {}

    def capture_status(*args: object, **kwargs: object) -> None:
        seen["status"] = RegistrationDataImport.objects.get(id=rdi.id).status

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population", side_effect=capture_status),
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
    ):
        remove_rdi_population_async_task_action(job)

    assert seen.get("status") == RegistrationDataImport.DELETE_SCHEDULED  # no transient marker; row stays until gone
    notify.assert_called_once_with(CALLBACK_URL)


def test_wipe_action_idempotent_when_row_gone() -> None:
    job = AsyncRetryJob(
        config={"registration_data_import_id": "00000000-0000-0000-0000-000000000000", "callback_url": CALLBACK_URL}
    )

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population") as wipe,
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
    ):
        remove_rdi_population_async_task_action(job)

    wipe.assert_not_called()
    notify.assert_called_once_with(CALLBACK_URL)


def test_wipe_action_merged_under_lock_fails(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.MERGED
    )
    job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population") as wipe,
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
        pytest.raises(NonRetriableTaskError),
    ):
        remove_rdi_population_async_task_action(job)

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.MERGED  # terminal success, never clobbered
    wipe.assert_not_called()
    notify.assert_not_called()


def test_wipe_action_protected_error_sets_failed(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})

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
    job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})

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
    job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})

    with patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify:
        remove_rdi_population_on_failure(job, RuntimeError("retries exhausted"))

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DELETE_FAILED
    assert rdi.error_message == "retries exhausted"
    notify.assert_not_called()


def test_fail_marks_status_keyed_on_id_without_a_select(program) -> None:
    # keyed UPDATE from rdi_id alone, no fetch — so it fires even when the wipe's SELECT/lock raised
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )

    with CaptureQueriesContext(connection) as ctx:
        RdiPopulationRemoval.mark_failed(str(rdi.id), reason="boom")

    queries = ctx.captured_queries
    assert len(queries) == 3  # SAVEPOINT, keyed UPDATE, RELEASE — no SELECT fetches the row first
    assert queries[1]["sql"].upper().startswith("UPDATE")

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DELETE_FAILED
    assert rdi.error_message == "boom"


@pytest.mark.django_db(transaction=True)
def test_wipe_blocks_on_a_held_row_lock() -> None:
    ba = BusinessAreaFactory(name="Afghanistan")
    program = ProgramFactory(business_area=ba)
    rdi = RegistrationDataImportFactory(
        business_area=ba, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})

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


def test_wipe_action_skips_when_merge_holds_lock(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})
    cache.set(_merge_key(rdi.id), "held")  # simulate a merge holding the shared lock for this RDI

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population") as wipe,
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
        pytest.raises(RuntimeError, match="rdi_merge_in_progress"),  # transient → retried, not DELETE_FAILED
    ):
        remove_rdi_population_async_task_action(job)

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DELETE_SCHEDULED  # untouched — never wiped under a merge
    wipe.assert_not_called()
    notify.assert_not_called()


def test_wipe_action_holds_merge_lock_during_wipe(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})
    seen = {}

    def capture_lock(*args: object, **kwargs: object) -> None:
        seen["held"] = cache.get(_merge_key(rdi.id)) is not None

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population", side_effect=capture_lock),
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task"),
    ):
        remove_rdi_population_async_task_action(job)

    assert seen.get("held") is True  # a concurrent merge is locked out for the whole wipe


def test_wipe_action_releases_merge_lock_after_success(program) -> None:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})

    with (
        patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population"),
        patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task"),
    ):
        remove_rdi_population_async_task_action(job)

    assert cache.get(_merge_key(rdi.id)) is None  # released → a later merge can acquire it


@pytest.mark.django_db(transaction=True)
def test_wipe_backs_off_while_a_real_merge_holds_the_lock() -> None:
    ba = BusinessAreaFactory(name="Afghanistan")
    program = ProgramFactory(business_area=ba)
    rdi = RegistrationDataImportFactory(
        business_area=ba, program=program, status=RegistrationDataImport.DELETE_SCHEDULED
    )
    wipe_job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id), "callback_url": CALLBACK_URL})
    merge_job = AsyncRetryJob(config={"registration_data_import_id": str(rdi.id)})

    merge_holding = threading.Event()  # set once the real merge has acquired the cache lock
    release_merge = threading.Event()  # set by the main thread once the wipe has tried

    def blocking_execute(_self: object, _rdi_id: str) -> None:
        # stand in for the real merge body: signal we hold the lock, then hold it until released
        merge_holding.set()
        release_merge.wait(timeout=5)

    def run_merge() -> None:
        # a failure here leaves merge_holding unset → the wait() assert below fails loudly
        try:
            with patch.object(RdiMergeTask, "execute", blocking_execute):
                merge_registration_data_import_async_task_action(merge_job)
        finally:
            connections.close_all()

    merge_thread = threading.Thread(target=run_merge)
    merge_thread.start()
    try:
        assert merge_holding.wait(timeout=5), "merge never acquired the cache lock"
        with (
            patch("hope.apps.registration_data.tasks.rdi_removal_async.remove_rdi_population") as wipe,
            patch("hope.apps.registration_data.celery_tasks.notify_rdi_deleted_async_task") as notify,
            pytest.raises(RuntimeError, match="rdi_merge_in_progress"),
        ):
            remove_rdi_population_async_task_action(wipe_job)
        wipe.assert_not_called()  # the real merge's lock excluded the wipe
        notify.assert_not_called()
    finally:
        release_merge.set()
        merge_thread.join(timeout=5)

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.MERGING  # merge advanced; the wipe never ran under its lock
