from typing import Any

from constance.test import override_config
from django.conf import settings
from elasticsearch import Elasticsearch
import pytest
from rest_framework import status

from extras.test_utils.factories import HouseholdFactory
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.models import BusinessArea, Program

pytestmark = [
    pytest.mark.usefixtures("django_elasticsearch_setup"),
    pytest.mark.elasticsearch,
    pytest.mark.xdist_group(name="elasticsearch"),
    pytest.mark.django_db,
]


def _refresh_es_index() -> None:
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    es.indices.refresh(index="_all")


def _create_individual(es_program: Program, afghanistan: BusinessArea, **kwargs: Any) -> Any:
    hh = HouseholdFactory(program=es_program, business_area=afghanistan)
    ind = hh.head_of_household
    for field, value in kwargs.items():
        setattr(ind, field, value)
    ind.save()
    return ind


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_fuzzy_name_match_tolerates_single_typo(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    john = _create_individual(es_program, afghanistan, full_name="John Smith")
    _create_individual(es_program, afghanistan, full_name="Bob Wilson")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Jonh"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_fuzzy_name_match_by_surname(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    john = _create_individual(es_program, afghanistan, full_name="John Smith")
    _create_individual(es_program, afghanistan, full_name="Jane Doe")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Smith"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_fuzzy_name_match_by_middle_token(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    maria = _create_individual(es_program, afghanistan, full_name="Maria Elena Gomez")
    _create_individual(es_program, afghanistan, full_name="Jane Doe")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Elena"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(maria.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_fuzzy_name_match_is_case_insensitive(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    john = _create_individual(es_program, afghanistan, full_name="John Smith")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "john"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_fuzzy_name_no_match_beyond_edit_distance(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    _create_individual(es_program, afghanistan, full_name="John Smith")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Zxcvb"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_fuzzy_name_preserves_phonetic_behavior(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    john = _create_individual(es_program, afghanistan, full_name="John Smith")
    jon = _create_individual(es_program, afghanistan, full_name="Jon Baptiste")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Jon"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    returned_ids = {r["id"] for r in results}
    assert str(jon.id) in returned_ids
    assert str(john.id) in returned_ids


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_fuzzy_name_operator_and_requires_all_terms(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    john = _create_individual(es_program, afghanistan, full_name="John Smith")
    rebuild_search_index()
    _refresh_es_index()

    # Both terms present — should match
    response = es_client.get(individuals_list_url, {"search": "John Smith"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john.id)

    # One real term + one nonsense term — should not match
    response = es_client.get(individuals_list_url, {"search": "John Zxcvb"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_fuzzy_name_matches_tokens_out_of_order(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    john = _create_individual(es_program, afghanistan, full_name="John Smith")
    _create_individual(es_program, afghanistan, full_name="Bob Wilson")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Smith John"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john.id)


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_search_db_fallback_name_still_works_when_es_disabled(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
    django_assert_num_queries: Any,
) -> None:
    john = _create_individual(es_program, afghanistan, full_name="John Smith")
    _create_individual(es_program, afghanistan, full_name="Jane Doe")

    with django_assert_num_queries(19):
        response = es_client.get(individuals_list_url, {"search": "John"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john.id)
