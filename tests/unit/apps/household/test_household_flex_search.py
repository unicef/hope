from datetime import timedelta
from typing import Any

from constance.test import override_config
from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import HouseholdFactory, ProgramFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.apps.household.filters import HouseholdFilter
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.models import BusinessArea, Household, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def client(api_client: Any, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def list_permission(
    create_user_role_with_permissions: Any, user: User, afghanistan: BusinessArea, program: Program
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )


@pytest.fixture
def list_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:households:households-list",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code},
    )


@pytest.fixture
def count_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:households:households-count",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code},
    )


@pytest.fixture
def global_list_url(afghanistan: BusinessArea) -> str:
    return reverse("api:households:households-global-list", kwargs={"business_area_slug": afghanistan.slug})


@pytest.fixture
def household_without_facility_name(afghanistan: BusinessArea, program: Program) -> Household:
    # Oldest in the program: the key is picked up from a later household of the sample.
    household = HouseholdFactory(business_area=afghanistan, program=program)
    Household.objects.filter(pk=household.pk).update(created_at=timezone.now() - timedelta(days=1))
    return household


@pytest.fixture
def facility_household(afghanistan: BusinessArea, program: Program) -> Household:
    return HouseholdFactory(
        business_area=afghanistan,
        program=program,
        flex_fields={"facility_name_h_f": "Al Thawra General Hospital"},
    )


@pytest.fixture
def withdrawn_facility_household(afghanistan: BusinessArea, program: Program) -> Household:
    return HouseholdFactory(
        business_area=afghanistan,
        program=program,
        withdrawn=True,
        flex_fields={"facility_name_h_f": "Al Thawra Maternity Hospital"},
    )


@pytest.fixture
def household_with_matching_head_name(afghanistan: BusinessArea, program: Program) -> Household:
    return HouseholdFactory(
        business_area=afghanistan,
        program=program,
        head_of_household__full_name="Thawra Saleh",
    )


@pytest.fixture
def sample_of_one_household(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("hope.apps.household.filters._FLEX_KEYS_SAMPLE_SIZE", 1)


def test_search_returns_403_without_permission(client: Any, list_url: str, facility_household: Household) -> None:
    response = client.get(list_url, {"search": "Thawra"})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize("search", ["Al Thawra", "Thawra Gen", "thawra general HOSPITAL"])
def test_search_db_matches_facility_name_fragment_case_insensitively(
    search: str,
    client: Any,
    list_permission: None,
    list_url: str,
    household_without_facility_name: Household,
    facility_household: Household,
    django_assert_num_queries: Any,
) -> None:
    with django_assert_num_queries(18):
        response = client.get(list_url, {"search": search})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.json()["results"]] == [str(facility_household.id)]


def test_search_db_returns_nothing_when_no_facility_name_matches(
    client: Any,
    list_permission: None,
    list_url: str,
    household_without_facility_name: Household,
    facility_household: Household,
) -> None:
    response = client.get(list_url, {"search": "Clinic"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"] == []


def test_search_db_in_program_without_facility_name_matches_other_fields_only(
    client: Any,
    list_permission: None,
    list_url: str,
    household_without_facility_name: Household,
    household_with_matching_head_name: Household,
) -> None:
    response = client.get(list_url, {"search": "Thawra"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.json()["results"]] == [str(household_with_matching_head_name.id)]


def test_search_db_misses_facility_name_carried_only_outside_sample(
    client: Any,
    list_permission: None,
    list_url: str,
    sample_of_one_household: None,
    household_without_facility_name: Household,
    facility_household: Household,
) -> None:
    # Pins the accepted false negative: a key no sampled household carries is not searched.
    response = client.get(list_url, {"search": "Thawra"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"] == []


def test_search_db_by_facility_name_combines_with_other_filter(
    client: Any,
    list_permission: None,
    list_url: str,
    facility_household: Household,
    withdrawn_facility_household: Household,
) -> None:
    response = client.get(list_url, {"search": "Thawra", "withdrawn": True})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.json()["results"]] == [str(withdrawn_facility_household.id)]


def test_count_db_counts_facility_name_matches(
    client: Any,
    list_permission: None,
    count_url: str,
    household_without_facility_name: Household,
    facility_household: Household,
    django_assert_num_queries: Any,
) -> None:
    with django_assert_num_queries(15):
        response = client.get(count_url, {"search": "Thawra"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"count": 1}


def test_global_search_matches_head_name_but_not_facility_name(
    client: Any,
    list_permission: None,
    global_list_url: str,
    facility_household: Household,
    household_with_matching_head_name: Household,
) -> None:
    response = client.get(global_list_url, {"search": "Thawra"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.json()["results"]] == [str(household_with_matching_head_name.id)]


def test_flex_search_q_samples_program_in_one_query(
    program: Program, facility_household: Household, django_assert_num_queries: Any
) -> None:
    with django_assert_num_queries(1):
        flex_q = HouseholdFilter._flex_search_q(program, "Thawra")

    assert list(Household.objects.filter(flex_q)) == [facility_household]


def test_flex_search_q_without_program_runs_no_query(
    facility_household: Household, django_assert_num_queries: Any
) -> None:
    with django_assert_num_queries(0):
        flex_q = HouseholdFilter._flex_search_q(None, "Thawra")

    assert not flex_q


@pytest.mark.xdist_group(name="elasticsearch")
@pytest.mark.parametrize("search", ["Al Thawra", "Thawra Gen", "thawra general HOSPITAL"])
@override_config(IS_ELASTICSEARCH_ENABLED=True)
@pytest.mark.elasticsearch
@pytest.mark.usefixtures("django_elasticsearch_setup")
def test_search_es_matches_facility_name_fragment_case_insensitively(
    search: str,
    client: Any,
    list_permission: None,
    list_url: str,
    household_without_facility_name: Household,
    facility_household: Household,
    django_assert_num_queries: Any,
) -> None:
    rebuild_search_index()

    with django_assert_num_queries(20):
        response = client.get(list_url, {"search": search})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.json()["results"]] == [str(facility_household.id)]


@pytest.mark.xdist_group(name="elasticsearch")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
@pytest.mark.elasticsearch
@pytest.mark.usefixtures("django_elasticsearch_setup")
def test_search_es_returns_index_hits_together_with_facility_name_matches(
    client: Any,
    list_permission: None,
    list_url: str,
    household_without_facility_name: Household,
    household_with_matching_head_name: Household,
    facility_household: Household,
) -> None:
    rebuild_search_index()

    response = client.get(list_url, {"search": "Thawra"})

    assert response.status_code == status.HTTP_200_OK
    assert {result["id"] for result in response.json()["results"]} == {
        str(household_with_matching_head_name.id),
        str(facility_household.id),
    }


@pytest.mark.xdist_group(name="elasticsearch")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
@pytest.mark.elasticsearch
@pytest.mark.usefixtures("django_elasticsearch_setup")
def test_search_es_returns_nothing_when_no_facility_name_matches(
    client: Any,
    list_permission: None,
    list_url: str,
    household_without_facility_name: Household,
    facility_household: Household,
) -> None:
    rebuild_search_index()

    response = client.get(list_url, {"search": "Clinic"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"] == []


@pytest.mark.xdist_group(name="elasticsearch")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
@pytest.mark.elasticsearch
@pytest.mark.usefixtures("django_elasticsearch_setup")
def test_search_es_by_facility_name_combines_with_other_filter(
    client: Any,
    list_permission: None,
    list_url: str,
    facility_household: Household,
    withdrawn_facility_household: Household,
) -> None:
    rebuild_search_index()

    response = client.get(list_url, {"search": "Thawra", "withdrawn": True})

    assert response.status_code == status.HTTP_200_OK
    assert [result["id"] for result in response.json()["results"]] == [str(withdrawn_facility_household.id)]


@pytest.mark.xdist_group(name="elasticsearch")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
@pytest.mark.elasticsearch
@pytest.mark.usefixtures("django_elasticsearch_setup")
def test_count_es_counts_facility_name_matches(
    client: Any,
    list_permission: None,
    count_url: str,
    household_without_facility_name: Household,
    facility_household: Household,
    django_assert_num_queries: Any,
) -> None:
    rebuild_search_index()

    with django_assert_num_queries(17):
        response = client.get(count_url, {"search": "Thawra"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"count": 1}
