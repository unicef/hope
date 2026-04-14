from django.urls import reverse
import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from hope.apps.core.celery_queues import CELERY_QUEUE_DEFAULT, CELERY_QUEUE_PERIODIC
from hope.models import AsyncJob, Program, User

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


def test_async_job_admin_changelist_excludes_periodic_jobs(client_logged, program) -> None:
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="default_queue_job",
        queue_name=CELERY_QUEUE_DEFAULT,
    )
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="periodic_queue_job",
        queue_name=CELERY_QUEUE_PERIODIC,
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
        queue_name=CELERY_QUEUE_DEFAULT,
    )
    AsyncJob.objects.create(
        program=program,
        type="JOB_TASK",
        action="hope.apps.core.celery_tasks.async_job_task",
        config={},
        repeatable=True,
        job_name="periodic_queue_job",
        queue_name=CELERY_QUEUE_PERIODIC,
    )

    url = reverse("admin:core_periodicasyncjob_changelist")
    response = client_logged.get(url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "periodic_queue_job" in content
    assert "default_queue_job" not in content
