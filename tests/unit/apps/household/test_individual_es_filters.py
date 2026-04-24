import types
from typing import Any

from constance.test import override_config
from django.conf import settings
from elasticsearch import Elasticsearch
import pytest
from rest_framework import status

from extras.test_utils.factories import BusinessAreaFactory, HouseholdFactory, ProgramFactory
from hope.apps.household.filters import IndividualFilter
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


# ── Phase 5: HOPE ID exact (term), address wildcard ──────────────────


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_hope_id_exact_match_case_insensitive_upper(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    ind = _create_individual(es_program, afghanistan, full_name="John Smith", unicef_id="IND-0000001")
    _create_individual(es_program, afghanistan, full_name="Jane Doe", unicef_id="IND-0000002")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "IND-0000001"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(ind.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_hope_id_exact_match_case_insensitive_lower(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    ind = _create_individual(es_program, afghanistan, full_name="John Smith", unicef_id="IND-0000001")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "ind-0000001"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(ind.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_hope_id_different_id_no_match(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    _create_individual(es_program, afghanistan, full_name="John Smith", unicef_id="IND-0000001")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "IND-0000002"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_hope_id_partial_input_does_not_match(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    _create_individual(es_program, afghanistan, full_name="John Smith", unicef_id="IND-0000001")
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "IND-00000"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_household_unicef_id_exact_match(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    ind = _create_individual(es_program, afghanistan, full_name="Alice Test")
    ind.household.unicef_id = "HH-0000001"
    ind.household.save(update_fields=["unicef_id"])
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "HH-0000001"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(ind.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_household_address_contains_match(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    ind = _create_individual(es_program, afghanistan, full_name="Alice Aleppan")
    ind.household.address = "Main Street 5, Aleppo"
    ind.household.save(update_fields=["address"])
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Aleppo"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(ind.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_household_address_contains_match_middle_token(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    ind = _create_individual(es_program, afghanistan, full_name="Alice Aleppan")
    ind.household.address = "Main Street 5, Aleppo"
    ind.household.save(update_fields=["address"])
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "street"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(ind.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_household_address_case_insensitive(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    ind = _create_individual(es_program, afghanistan, full_name="Alice Aleppan")
    ind.household.address = "Main Street 5, Aleppo"
    ind.household.save(update_fields=["address"])
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "ALEPPO"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(ind.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_household_address_no_match(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    ind = _create_individual(es_program, afghanistan, full_name="Alice Aleppan")
    ind.household.address = "Main Street 5, Aleppo"
    ind.household.save(update_fields=["address"])
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "xyz"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_main_search_box_combined_name_or_hope_id_or_address(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    alice = _create_individual(es_program, afghanistan, full_name="Alice Wonderland", unicef_id="IND-0000010")
    bob = _create_individual(es_program, afghanistan, full_name="Bob Builder", unicef_id="IND-0000009")
    charlie = _create_individual(es_program, afghanistan, full_name="Charlie Brown", unicef_id="IND-0000008")
    charlie.household.address = "Damascus, Syria"
    charlie.household.save(update_fields=["address"])

    rebuild_search_index()
    _refresh_es_index()

    # Search by name → only Alice
    response = es_client.get(individuals_list_url, {"search": "Alice Wonderland"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(alice.id)

    # Search by HOPE ID → only Bob
    response = es_client.get(individuals_list_url, {"search": "IND-0000009"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(bob.id)

    # Search by address → only Charlie
    response = es_client.get(individuals_list_url, {"search": "Damascus"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(charlie.id)


def test_es_query_shape_contains_expected_clauses(
    afghanistan: BusinessArea,
    es_program: Program,
) -> None:
    request = types.SimpleNamespace(parser_context={"kwargs": {"business_area_slug": afghanistan.slug}})
    f = IndividualFilter.__new__(IndividualFilter)
    f.request = request

    query = f._get_elasticsearch_query_for_individuals("test", es_program)
    should = query["query"]["bool"]["should"]

    clause_signatures = set()
    for clause in should:
        for query_type, body in clause.items():
            for field_name in body:
                clause_signatures.add((query_type, field_name))

    assert ("term", "unicef_id.keyword") in clause_signatures
    assert ("term", "household.unicef_id.keyword") in clause_signatures
    assert ("wildcard", "household.address.keyword") in clause_signatures
    assert ("match", "full_name") in clause_signatures


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_es_search_does_not_leak_across_business_areas(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    ind_afg = _create_individual(es_program, afghanistan, full_name="Afghan Person")

    ukraine = BusinessAreaFactory(name="Ukraine", slug="ukraine", code="0061")
    ukraine_program = ProgramFactory(business_area=ukraine, status=Program.DRAFT)
    ukraine_program.status = Program.ACTIVE
    ukraine_program.save()
    ind_ukr = _create_individual(ukraine_program, ukraine, full_name="Ukrainian Person")

    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Person"})
    assert response.status_code == status.HTTP_200_OK
    returned_ids = {r["id"] for r in response.json()["results"]}
    assert str(ind_afg.id) in returned_ids
    assert str(ind_ukr.id) not in returned_ids


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_es_search_does_not_leak_across_programs(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    ind_prog1 = _create_individual(es_program, afghanistan, full_name="Program One Person")

    other_program = ProgramFactory(business_area=afghanistan, status=Program.DRAFT)
    other_program.status = Program.ACTIVE
    other_program.save()
    ind_prog2 = _create_individual(other_program, afghanistan, full_name="Program Two Person")

    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Person"})
    assert response.status_code == status.HTTP_200_OK
    returned_ids = {r["id"] for r in response.json()["results"]}
    assert str(ind_prog1.id) in returned_ids
    assert str(ind_prog2.id) not in returned_ids
