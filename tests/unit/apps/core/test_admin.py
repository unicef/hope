from django.urls import reverse
import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
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
