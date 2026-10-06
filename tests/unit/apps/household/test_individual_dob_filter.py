from datetime import date
from typing import Any, Callable

from constance.test import override_config
from django.conf import settings
from elasticsearch import Elasticsearch
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import HouseholdFactory, PartnerFactory, ProgramFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.models import BusinessArea, Individual, Program

pytestmark = [
    pytest.mark.usefixtures("django_elasticsearch_setup"),
    pytest.mark.elasticsearch,
    pytest.mark.xdist_group(name="elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def es_program(afghanistan: BusinessArea) -> Program:
    program = ProgramFactory(business_area=afghanistan, status=Program.DRAFT)
    program.status = Program.ACTIVE
    program.save()
    return program


@pytest.fixture
def es_user(afghanistan: BusinessArea, create_user_role_with_permissions: Callable) -> Any:
    partner = PartnerFactory(name="ESSearchPartner")
    user = UserFactory(partner=partner)
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    return user


@pytest.fixture
def es_client(api_client: Callable, es_user: Any) -> Any:
    return api_client(es_user)


@pytest.fixture
def individuals_list_url(afghanistan: BusinessArea, es_program: Program) -> str:
    return reverse(
        "api:households:individuals-list",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": es_program.code},
    )


def _refresh_es_index() -> None:
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    es.indices.refresh(index="_all")


@pytest.fixture
def john_born_1990_05_12(es_program: Program, afghanistan: BusinessArea) -> Individual:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        head_of_household__full_name="John Smith",
        head_of_household__birth_date=date(1990, 5, 12),
    ).head_of_household


@pytest.fixture
def john_born_1991_01_01(es_program: Program, afghanistan: BusinessArea) -> Individual:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        head_of_household__full_name="John Smith",
        head_of_household__birth_date=date(1991, 1, 1),
    ).head_of_household


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_dob_filter_exact_match(
    es_client: Any,
    individuals_list_url: str,
    john_born_1990_05_12: Individual,
    john_born_1991_01_01: Individual,
    django_assert_num_queries: Any,
) -> None:
    with django_assert_num_queries(18):
        response = es_client.get(individuals_list_url, {"birth_date": "1990-05-12"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_born_1990_05_12.id)


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_dob_filter_no_match_different_day(
    es_client: Any,
    individuals_list_url: str,
    john_born_1990_05_12: Individual,
) -> None:
    response = es_client.get(individuals_list_url, {"birth_date": "1990-05-13"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"] == []


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_dob_filter_no_match_different_year(
    es_client: Any,
    individuals_list_url: str,
    john_born_1990_05_12: Individual,
) -> None:
    response = es_client.get(individuals_list_url, {"birth_date": "1991-05-12"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"] == []


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_dob_filter_invalid_format_returns_validation_error(
    es_client: Any,
    individuals_list_url: str,
) -> None:
    response = es_client.get(individuals_list_url, {"birth_date": "not-a-date"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_dob_filter_empty_value_ignored(
    es_client: Any,
    individuals_list_url: str,
    john_born_1990_05_12: Individual,
    john_born_1991_01_01: Individual,
) -> None:
    response = es_client.get(individuals_list_url, {"birth_date": ""})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 2


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_dob_filter_combines_with_name_search_via_es(
    es_client: Any,
    individuals_list_url: str,
    john_born_1990_05_12: Individual,
    john_born_1991_01_01: Individual,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(
        individuals_list_url,
        {"search": "John", "birth_date": "1990-05-12"},
    )
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_born_1990_05_12.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_dob_filter_alone_does_not_route_through_es(
    es_client: Any,
    individuals_list_url: str,
    john_born_1990_05_12: Individual,
) -> None:
    # ES is enabled but the doc index is intentionally NOT rebuilt. If the DOB
    # filter incorrectly routed through ES (e.g. reused search_filter), the
    # target individual would not be returned because ES has no documents for
    # it. A Postgres-only DOB path returns the row regardless.
    response = es_client.get(individuals_list_url, {"birth_date": "1990-05-12"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_born_1990_05_12.id)
