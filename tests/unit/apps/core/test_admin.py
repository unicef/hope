from datetime import timedelta
from typing import Any
from unittest.mock import PropertyMock, patch

from django.contrib import admin, messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone
import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from hope.admin.async_job import (
    AsyncJobAdmin,
    UsedContentTypeListFilter,
    UsedJobNameListFilter,
    is_missing,
)
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


def build_async_job_admin_filter(
    filter_cls: type,
    params: dict[str, str] | None = None,
) -> tuple[Any, HttpRequest, AsyncJobAdmin]:
    request = RequestFactory().get("/", data=params or {})
    model_admin = AsyncJobAdmin(AsyncJob, admin.site)
    return filter_cls(request, request.GET.copy(), AsyncJob, model_admin), request, model_admin


def get_changelist_job_names(response: Any) -> list[str]:
    return [job.job_name for job in response.context["cl"].result_list]


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


def test_async_job_admin_program_autocomplete_only_returns_used_programs(client_logged, program, business_area) -> None:
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="used_program_job",
    )
    unused_program = ProgramFactory(
        name="Unused Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )
    periodic_only_program = ProgramFactory(
        name="Periodic Only Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )
    PeriodicAsyncJob.objects.create(
        program=periodic_only_program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="periodic_only_program_job",
    )

    url = reverse("admin:core_asyncjob_used_program_autocomplete")
    response = client_logged.get(url, {"term": "Program"})
    data = response.json()
    results = {entry["id"]: entry["text"] for entry in data["results"]}

    assert response.status_code == 200
    assert str(program.pk) in results
    assert results[str(program.pk)] == str(program)
    assert str(unused_program.pk) not in results
    assert str(periodic_only_program.pk) not in results


def test_async_job_admin_business_area_autocomplete_only_returns_used_business_areas(
    client_logged,
    program,
    business_area,
) -> None:
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="used_business_area_job",
    )
    unused_business_area = BusinessAreaFactory(
        code="0061",
        slug="ukraine",
        name="Ukraine",
        active=True,
    )
    periodic_only_business_area = BusinessAreaFactory(
        code="0062",
        slug="poland",
        name="Poland",
        active=True,
    )
    periodic_only_program = ProgramFactory(
        name="Periodic Only Program",
        status=Program.ACTIVE,
        business_area=periodic_only_business_area,
    )
    PeriodicAsyncJob.objects.create(
        program=periodic_only_program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="periodic_only_business_area_job",
    )

    url = reverse("admin:core_asyncjob_used_business_area_autocomplete")
    response = client_logged.get(url, {"term": "a"})
    data = response.json()
    results = {entry["id"]: entry["text"] for entry in data["results"]}

    assert response.status_code == 200
    assert str(business_area.pk) in results
    assert results[str(business_area.pk)] == str(business_area)
    assert str(unused_business_area.pk) not in results
    assert str(periodic_only_business_area.pk) not in results


def test_async_job_admin_program_autocomplete_respects_business_area_parent(
    client_logged,
    business_area,
) -> None:
    included_program = ProgramFactory(
        name="Included Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )
    excluded_business_area = BusinessAreaFactory(
        code="0064",
        slug="moldova",
        name="Moldova",
        active=True,
    )
    excluded_program = ProgramFactory(
        name="Excluded Program",
        status=Program.ACTIVE,
        business_area=excluded_business_area,
    )
    AsyncJob.objects.create(
        program=included_program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="included_parent_program_job",
    )
    AsyncJob.objects.create(
        program=excluded_program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="excluded_parent_program_job",
    )

    url = reverse("admin:core_asyncjob_used_program_autocomplete")
    response = client_logged.get(url, {"business_area": str(business_area.pk), "term": "Program"})
    data = response.json()
    results = {entry["id"]: entry["text"] for entry in data["results"]}

    assert response.status_code == 200
    assert str(included_program.pk) in results
    assert str(excluded_program.pk) not in results


def test_async_job_admin_job_name_filter_lookups_only_used_async_job_names(program) -> None:
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="used_job_name",
    )
    PeriodicAsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="periodic_only_job_name",
    )

    job_name_filter, request, model_admin = build_async_job_admin_filter(UsedJobNameListFilter)
    lookups = dict(job_name_filter.lookups(request, model_admin))

    assert "used_job_name" in lookups
    assert "periodic_only_job_name" not in lookups


def test_async_job_admin_gfk_filters_only_include_used_async_job_targets(
    admin_user,
    business_area,
    program,
) -> None:
    program_content_type = ContentType.objects.get_for_model(program)
    business_area_content_type = ContentType.objects.get_for_model(business_area)
    user_content_type = ContentType.objects.get_for_model(admin_user)

    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="program_target_job",
        content_type=program_content_type,
        object_id=str(program.pk),
    )
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="business_area_target_job",
        content_type=business_area_content_type,
        object_id=str(business_area.pk),
    )
    PeriodicAsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="periodic_user_target_job",
        content_type=user_content_type,
        object_id=str(admin_user.pk),
    )

    content_type_filter, request, model_admin = build_async_job_admin_filter(UsedContentTypeListFilter)
    content_type_lookups = dict(content_type_filter.lookups(request, model_admin))
    assert str(program_content_type.pk) in content_type_lookups
    assert str(business_area_content_type.pk) in content_type_lookups
    assert str(user_content_type.pk) not in content_type_lookups


def test_async_job_admin_filters_by_business_area(client_logged, business_area) -> None:
    included_program = ProgramFactory(
        name="Included Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )
    excluded_business_area = BusinessAreaFactory(
        code="0063",
        slug="romania",
        name="Romania",
        active=True,
    )
    excluded_program = ProgramFactory(
        name="Excluded Program",
        status=Program.ACTIVE,
        business_area=excluded_business_area,
    )

    AsyncJob.objects.create(
        program=included_program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="included_business_area_job",
    )
    AsyncJob.objects.create(
        program=excluded_program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="excluded_business_area_job",
    )

    url = reverse("admin:core_asyncjob_changelist")
    response = client_logged.get(
        url,
        {"program__business_area__exact": str(business_area.pk)},
    )
    job_names = get_changelist_job_names(response)

    assert response.status_code == 200
    assert "included_business_area_job" in job_names
    assert "excluded_business_area_job" not in job_names


def test_async_job_admin_filters_by_program(client_logged, business_area) -> None:
    included_program = ProgramFactory(
        name="Included Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )
    excluded_program = ProgramFactory(
        name="Excluded Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )

    AsyncJob.objects.create(
        program=included_program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="included_program_job",
    )
    AsyncJob.objects.create(
        program=excluded_program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="excluded_program_job",
    )

    url = reverse("admin:core_asyncjob_changelist")
    response = client_logged.get(
        url,
        {"program__exact": str(included_program.pk)},
    )
    job_names = get_changelist_job_names(response)

    assert response.status_code == 200
    assert "included_program_job" in job_names
    assert "excluded_program_job" not in job_names


def test_async_job_admin_searches_by_program_name(client_logged, business_area) -> None:
    included_program = ProgramFactory(
        name="Included Program Search",
        status=Program.ACTIVE,
        business_area=business_area,
    )
    excluded_program = ProgramFactory(
        name="Excluded Program Search",
        status=Program.ACTIVE,
        business_area=business_area,
    )

    AsyncJob.objects.create(
        program=included_program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="included_program_search_job",
    )
    AsyncJob.objects.create(
        program=excluded_program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="excluded_program_search_job",
    )

    url = reverse("admin:core_asyncjob_changelist")
    response = client_logged.get(url, {"q": "Included Program Search"})
    job_names = get_changelist_job_names(response)

    assert response.status_code == 200
    assert "included_program_search_job" in job_names
    assert "excluded_program_search_job" not in job_names


def test_async_job_admin_filters_by_job_name(client_logged, program) -> None:
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="included_job_name",
    )
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="excluded_job_name",
    )

    url = reverse("admin:core_asyncjob_changelist")
    response = client_logged.get(
        url,
        {UsedJobNameListFilter.parameter_name: "included_job_name"},
    )
    job_names = get_changelist_job_names(response)

    assert response.status_code == 200
    assert "included_job_name" in job_names
    assert "excluded_job_name" not in job_names


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
        job_names = get_changelist_job_names(response)

    assert response.status_code == 200
    assert included_job.job_name in job_names
    assert excluded_job.job_name not in job_names


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
