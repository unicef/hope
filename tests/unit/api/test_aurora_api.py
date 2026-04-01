from types import SimpleNamespace

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories.account import RoleFactory, UserFactory
from extras.test_utils.factories.api import APITokenFactory
from extras.test_utils.factories.aurora import (
    OrganizationFactory,
    ProjectFactory,
    RegistrationFactory,
)
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.contrib.aurora.caches import (
    OrganizationListVersionsKeyBit,
    ProjectListVersionsKeyBit,
    RegistrationListVersionsKeyBit,
)
from hope.contrib.aurora.models import Organization, Project, Registration
from hope.models import APIToken
from hope.models.utils import Grant
from unit.api.conftest import token_grant_permission

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_token() -> APIToken:
    user = UserFactory()
    business_area = BusinessAreaFactory(name="Afghanistan")
    role = RoleFactory(name="test_role", permissions=[])
    user.role_assignments.create(role=role, business_area=business_area)

    token = APITokenFactory(user=user, grants=[])
    token.valid_for.set([business_area])
    return token


@pytest.fixture
def api_client(api_token: APIToken) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + api_token.key)
    return client


@pytest.fixture
def aurora_data(api_token: APIToken) -> SimpleNamespace:
    business_area = api_token.valid_for.first()
    program = ProgramFactory(name="Test Program 123")
    other_program = ProgramFactory(name="Other program")
    organization = OrganizationFactory(
        name="Test Organization",
        slug="test_organization",
        business_area=business_area,
        source_id=777,
    )
    organization_2 = OrganizationFactory(
        name="Test Organization 2",
        slug="slug123",
        business_area=business_area,
        source_id=111,
    )
    project_1 = ProjectFactory(
        name="Test Project 1",
        source_id=111,
        organization=organization,
        programme=program,
    )
    project_2 = ProjectFactory(
        name="Test Project 2",
        source_id=222,
        organization=organization_2,
        programme=other_program,
    )
    RegistrationFactory(project=project_1, source_id=111, name="Reg 1")
    RegistrationFactory(project=project_1, source_id=222, name="Reg 2")
    registration_3 = RegistrationFactory(project=project_2, source_id=333, name="Reg 3")

    return SimpleNamespace(
        business_area=business_area,
        program=program,
        other_program=other_program,
        organization=organization,
        organization_2=organization_2,
        project_1=project_1,
        project_2=project_2,
        registration_3=registration_3,
    )


@pytest.mark.parametrize(
    "url_name",
    [
        "api:organization-list",
        "api:project-list",
        "api:registration-list",
    ],
)
def test_list_requires_permission(api_client: APIClient, url_name: str) -> None:
    response = api_client.get(reverse(url_name))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_organization_list_returns_all_organizations(
    api_client: APIClient, api_token: APIToken, aurora_data: SimpleNamespace
) -> None:
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = api_client.get(reverse("api:organization-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    org = response.data["results"][0]
    assert org["name"] == "Test Organization"
    assert org["hope_id"] == str(aurora_data.business_area.pk)
    assert org["aurora_id"] == 777


def test_organization_list_caches_results(
    api_client: APIClient, api_token: APIToken, aurora_data: SimpleNamespace
) -> None:
    cache.clear()
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        with CaptureQueriesContext(connection) as queries:
            api_client.get(reverse("api:organization-list"))
    cache_key = (
        f"{OrganizationListVersionsKeyBit.specific_view_cache_key}:"
        f"{Organization.objects.latest('updated_at').updated_at}:"
        f"{Organization.objects.all().count()}"
    )
    assert cache.get(cache_key)
    assert len(queries) > 0
    with CaptureQueriesContext(connection) as queries2:
        resp_2 = api_client.get(reverse("api:organization-list"))
    assert resp_2.status_code == 200
    assert len(queries2) < len(queries)


def test_project_list_returns_all_projects(
    api_client: APIClient, api_token: APIToken, aurora_data: SimpleNamespace
) -> None:
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = api_client.get(reverse("api:project-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    project = response.data["results"][0]
    assert project["name"] == "Test Project 1"
    assert project["aurora_id"] == 111
    assert project["hope_id"] == str(aurora_data.program.pk)
    assert project["organization"] == "test_organization"


def test_project_list_caches_results(api_client: APIClient, api_token: APIToken, aurora_data: SimpleNamespace) -> None:
    cache.clear()
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        with CaptureQueriesContext(connection) as queries:
            api_client.get(reverse("api:project-list"))
    cache_key = (
        f"{ProjectListVersionsKeyBit.specific_view_cache_key}:"
        f"{Project.objects.latest('updated_at').updated_at}:"
        f"{Project.objects.all().count()}"
    )
    assert cache.get(cache_key) is not None
    assert len(queries) > 0
    with CaptureQueriesContext(connection) as queries2:
        resp_2 = api_client.get(reverse("api:project-list"))
    assert resp_2.status_code == 200
    assert len(queries2) < len(queries)


@pytest.mark.parametrize(
    ("filter_key", "filter_value_attr"),
    [
        ("org_slug", "slug"),
        ("org_pk", "pk"),
    ],
)
def test_project_list_filter_by_organization(
    api_client: APIClient,
    api_token: APIToken,
    aurora_data: SimpleNamespace,
    filter_key: str,
    filter_value_attr: str,
) -> None:
    filter_value = str(getattr(aurora_data.organization_2, filter_value_attr))
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = api_client.get(reverse("api:project-list"), {filter_key: filter_value})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    project = response.data["results"][0]
    assert project["name"] == aurora_data.project_2.name
    assert project["aurora_id"] == 222
    assert project["hope_id"] == str(aurora_data.other_program.pk)
    assert project["organization"] == aurora_data.organization_2.slug


def test_registration_list_returns_all_registrations(
    api_client: APIClient, api_token: APIToken, aurora_data: SimpleNamespace
) -> None:
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = api_client.get(reverse("api:registration-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3


def test_registration_list_caches_results(
    api_client: APIClient, api_token: APIToken, aurora_data: SimpleNamespace
) -> None:
    cache.clear()
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        with CaptureQueriesContext(connection) as queries:
            api_client.get(reverse("api:registration-list"))
    cache_key = (
        f"{RegistrationListVersionsKeyBit.specific_view_cache_key}:"
        f"{Registration.objects.latest('updated_at').updated_at}:{Registration.objects.all().count()}"
    )
    assert cache.get(cache_key) is not None
    assert len(queries) > 0
    with CaptureQueriesContext(connection) as queries2:
        resp_2 = api_client.get(reverse("api:registration-list"))
    assert resp_2.status_code == 200
    assert len(queries2) < len(queries)


@pytest.mark.parametrize(
    ("filter_key", "filter_value_attr"),
    [
        ("org_slug", "slug"),
        ("org_pk", "pk"),
    ],
)
def test_registration_list_filter_by_organization(
    api_client: APIClient,
    api_token: APIToken,
    aurora_data: SimpleNamespace,
    filter_key: str,
    filter_value_attr: str,
) -> None:
    filter_value = str(getattr(aurora_data.organization_2, filter_value_attr))
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = api_client.get(reverse("api:registration-list"), {filter_key: filter_value})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    reg = response.data["results"][0]
    assert reg["name"] == aurora_data.registration_3.name
    assert reg["aurora_id"] == aurora_data.registration_3.source_id
    assert reg["project"] == str(aurora_data.project_2.pk)
    assert reg["organization"] == aurora_data.organization_2.slug


def test_registration_list_filter_by_programme_pk(
    api_client: APIClient, api_token: APIToken, aurora_data: SimpleNamespace
) -> None:
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = api_client.get(
            reverse("api:registration-list"),
            {"programme_pk": str(aurora_data.other_program.pk)},
        )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    reg = response.data["results"][0]
    assert reg["name"] == aurora_data.registration_3.name
    assert reg["aurora_id"] == aurora_data.registration_3.source_id
    assert reg["project"] == str(aurora_data.project_2.pk)
    assert reg["organization"] == aurora_data.organization_2.slug
