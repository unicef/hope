from datetime import timedelta
from unittest.mock import PropertyMock, patch

from django.contrib import admin, messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone
import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from hope.admin.async_job import AsyncJobAdmin, is_missing
from hope.admin.grievance import GrievanceTicketAdmin
from hope.admin.household import HouseholdAdmin
from hope.apps.core.celery_tasks import (
    DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MAX_AGE_SECONDS,
    DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.models import AsyncJob, Household, PeriodicAsyncJob, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="root",
        email="root@root.com",
        password="password",
    )


@pytest.fixture
def client_logged(client, admin_user):
    client.login(username="root", password="password")
    return client


@pytest.fixture
def staff_user_without_recover_permission() -> User:
    user = User.objects.create_user(
        username="staff-no-recover",
        email="staff-no-recover@example.com",
        password="password",
        is_staff=True,
        is_superuser=False,
    )
    content_type = ContentType.objects.get_for_model(AsyncJob)
    user.user_permissions.set(
        Permission.objects.filter(
            content_type=content_type,
            codename__in=["view_asyncjob", "change_asyncjob"],
        )
    )
    return user


@pytest.fixture
def staff_client_without_recover_permission(client, staff_user_without_recover_permission):
    client.force_login(staff_user_without_recover_permission, backend="django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def business_area():
    return BusinessAreaFactory(code="0060", slug="afghanistan", name="Afghanistan", active=True)


@pytest.fixture
def program(business_area) -> Program:
    return ProgramFactory(
        name="Test Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )


def test_async_job_admin_changelist_loads(client_logged, program) -> None:
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="async_job_task",
    )

    url = reverse("admin:core_asyncjob_changelist")
    response = client_logged.get(url)

    assert response.status_code == 200
    assert "async_job_task" in response.content.decode()


def test_async_job_admin_change_page_loads(client_logged, program) -> None:
    job = AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="async_job_task",
    )

    url = reverse("admin:core_asyncjob_change", args=(job.pk,))
    response = client_logged.get(url)

    assert response.status_code == 200
    assert "Task status" in response.content.decode()


# ── AutocompleteForeignKeyMixin ──────────────────────────────────────────


def test_fk_fields_included_in_autocomplete():
    model_admin = HouseholdAdmin(Household, admin.site)
    request = HttpRequest()
    request.user = type("User", (), {"is_superuser": True, "has_perm": lambda *a: True})()
    fields = model_admin.get_autocomplete_fields(request)
    assert "program" in fields
    assert "business_area" in fields
    assert "head_of_household" in fields


def test_filter_horizontal_excluded_from_autocomplete():
    model_admin = GrievanceTicketAdmin(GrievanceTicket, admin.site)
    request = HttpRequest()
    request.user = type("User", (), {"is_superuser": True, "has_perm": lambda *a: True})()
    fields = model_admin.get_autocomplete_fields(request)
    assert "programs" not in fields


def test_async_job_recover_button_is_enabled_only_for_missing_jobs(program) -> None:
    missing_job = AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="missing_job",
    )
    started_job = AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="started_job",
    )

    missing_button = type("Button", (), {"original": missing_job})()
    started_button = type("Button", (), {"original": started_job})()

    with patch.object(
        AsyncJob,
        "task_status",
        new=property(lambda self: self.MISSING if self.pk == missing_job.pk else self.STARTED),
    ):
        assert is_missing(missing_button) is True
        assert is_missing(started_button) is False


def test_async_job_declares_recover_missing_permission() -> None:
    assert ("recover_missing_async_job", "Can recover missing async jobs") in AsyncJob._meta.permissions


def test_async_job_recover_missing_button_uses_recover_missing_permission() -> None:
    assert AsyncJobAdmin.recover_missing.permission == "core.recover_missing_async_job"


def test_async_job_admin_changelist_excludes_periodic_jobs(client_logged, program) -> None:
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="default_queue_job",
    )
    PeriodicAsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="periodic_queue_job",
    )

    url = reverse("admin:core_asyncjob_changelist")
    response = client_logged.get(url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "default_queue_job" in content
    assert "periodic_queue_job" not in content


def test_periodic_async_job_admin_changelist_shows_only_periodic_jobs(client_logged, program) -> None:
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="default_queue_job",
    )
    PeriodicAsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="periodic_queue_job",
    )

    url = reverse("admin:core_periodicasyncjob_changelist")
    response = client_logged.get(url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "periodic_queue_job" in content
    assert "default_queue_job" not in content


@pytest.mark.parametrize(
    ("filter_value", "included_age_delta", "excluded_age_delta"),
    [
        (
            "recoverable",
            timedelta(
                seconds=(
                    DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS
                    + DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MAX_AGE_SECONDS
                )
                // 2
            ),
            timedelta(seconds=DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS - 60),
        ),
        ("12_24", timedelta(hours=18), timedelta(hours=30)),
        ("24_72", timedelta(hours=30), timedelta(hours=6)),
    ],
)
def test_async_job_admin_missing_filter_by_age_bucket(
    client_logged,
    program,
    filter_value: str,
    included_age_delta: timedelta,
    excluded_age_delta: timedelta,
) -> None:
    included_job = AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name=f"included_job_{filter_value}",
        curr_async_result_id=f"included-{filter_value}",
    )
    excluded_job = AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name=f"excluded_job_{filter_value}",
        curr_async_result_id=f"excluded-{filter_value}",
    )
    AsyncJob.objects.filter(pk=included_job.pk).update(
        datetime_queued=timezone.now() - included_age_delta,
    )
    AsyncJob.objects.filter(pk=excluded_job.pk).update(
        datetime_queued=timezone.now() - excluded_age_delta,
    )

    url = reverse("admin:core_asyncjob_changelist")
    with patch.object(
        AsyncJob,
        "task_status",
        new=property(lambda self: self.MISSING if self.pk == included_job.pk else self.SUCCESS),
    ):
        response = client_logged.get(url, {"missing_age": filter_value})
        content = response.content.decode()

    assert response.status_code == 200
    assert included_job.job_name in content
    assert excluded_job.job_name not in content


def test_async_job_admin_recover_missing_button_forbidden_without_permission(
    staff_client_without_recover_permission,
    program,
) -> None:
    job = AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="missing_job",
    )

    url = reverse("admin:core_asyncjob_recover_missing", args=[job.pk])
    response = staff_client_without_recover_permission.post(url)

    assert response.status_code == 403


def test_async_job_admin_recover_missing_button_requeues_missing_job(client_logged, program) -> None:
    job = AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="missing_job",
    )

    url = reverse("admin:core_asyncjob_recover_missing", args=[job.pk])
    with (
        patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=job.MISSING),
        patch.object(AsyncJob, "queue", autospec=True, return_value="new-task-id") as mock_queue,
    ):
        response = client_logged.post(url)

    assert response.status_code == 302
    mock_queue.assert_called_once()
    assert list(messages.get_messages(response.wsgi_request))[0].message == "Async job was requeued"


def test_async_job_admin_recover_missing_button_skips_non_missing_job(client_logged, program) -> None:
    job = AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="started_job",
    )

    url = reverse("admin:core_asyncjob_recover_missing", args=[job.pk])
    with (
        patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=job.STARTED),
        patch.object(AsyncJob, "queue", autospec=True, return_value="new-task-id") as mock_queue,
    ):
        response = client_logged.post(url)

    assert response.status_code == 302
    mock_queue.assert_not_called()
    assert [message.message for message in messages.get_messages(response.wsgi_request)] == [
        "Async job is not missing. Current status: STARTED",
    ]


def test_async_job_admin_recover_missing_button_skips_non_repeatable_job(client_logged, program) -> None:
    job = AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=False,
        job_name="missing_job",
    )

    url = reverse("admin:core_asyncjob_recover_missing", args=[job.pk])
    with (
        patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=job.MISSING),
        patch.object(AsyncJob, "queue", autospec=True, return_value="new-task-id") as mock_queue,
    ):
        response = client_logged.post(url)

    assert response.status_code == 302
    mock_queue.assert_not_called()
    assert [message.message for message in messages.get_messages(response.wsgi_request)] == [
        "Async job is not repeatable and cannot be requeued",
    ]


def test_periodic_async_job_admin_requires_own_permissions(
    staff_client_without_recover_permission,
    program,
) -> None:
    PeriodicAsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="periodic_queue_job",
    )

    url = reverse("admin:core_periodicasyncjob_changelist")
    response = staff_client_without_recover_permission.get(url)

    assert response.status_code == 403
