import types
from typing import Any, Callable

from constance.test import override_config
from django.conf import settings
from elasticsearch import Elasticsearch
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.household.filters import IndividualFilter
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.models import BusinessArea, Program

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


@pytest.fixture
def john_smith(es_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        head_of_household__full_name="John Smith",
        head_of_household__unicef_id="IND-0000001",
    ).head_of_household


@pytest.fixture
def jane_doe(es_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        head_of_household__full_name="Jane Doe",
        head_of_household__unicef_id="IND-0000002",
    ).head_of_household


@pytest.fixture
def bob_wilson(es_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        head_of_household__full_name="Bob Wilson",
    ).head_of_household


@pytest.fixture
def maria_elena_gomez(es_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        head_of_household__full_name="Maria Elena Gomez",
    ).head_of_household


@pytest.fixture
def jon_baptiste(es_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        head_of_household__full_name="Jon Baptiste",
    ).head_of_household


@pytest.fixture
def alice_in_aleppo(es_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        unicef_id="HH-0000001",
        address="Main Street 5, Aleppo",
        head_of_household__full_name="Alice Aleppan",
    ).head_of_household


@pytest.fixture
def alice_wonderland(es_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        head_of_household__full_name="Alice Wonderland",
        head_of_household__unicef_id="IND-0000010",
    ).head_of_household


@pytest.fixture
def bob_builder(es_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        head_of_household__full_name="Bob Builder",
        head_of_household__unicef_id="IND-0000009",
    ).head_of_household


@pytest.fixture
def charlie_in_damascus(es_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        address="Damascus, Syria",
        head_of_household__full_name="Charlie Brown",
        head_of_household__unicef_id="IND-0000008",
    ).head_of_household


@pytest.fixture
def afghan_person(es_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=es_program,
        business_area=afghanistan,
        head_of_household__full_name="Afghan Person",
    ).head_of_household


@pytest.fixture
def ukraine() -> BusinessArea:
    return BusinessAreaFactory(name="Ukraine", slug="ukraine", code="0061")


@pytest.fixture
def ukraine_program(ukraine: BusinessArea) -> Program:
    program = ProgramFactory(business_area=ukraine, status=Program.DRAFT)
    program.status = Program.ACTIVE
    program.save()
    return program


@pytest.fixture
def ukrainian_person(ukraine_program: Program, ukraine: BusinessArea) -> Any:
    return HouseholdFactory(
        program=ukraine_program,
        business_area=ukraine,
        head_of_household__full_name="Ukrainian Person",
    ).head_of_household


@pytest.fixture
def other_program(afghanistan: BusinessArea) -> Program:
    program = ProgramFactory(business_area=afghanistan, status=Program.DRAFT)
    program.status = Program.ACTIVE
    program.save()
    return program


@pytest.fixture
def other_program_person(other_program: Program, afghanistan: BusinessArea) -> Any:
    return HouseholdFactory(
        program=other_program,
        business_area=afghanistan,
        head_of_household__full_name="Program Two Person",
    ).head_of_household


def _refresh_es_index() -> None:
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    es.indices.refresh(index="_all")


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_fuzzy_name_match_tolerates_single_typo(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
    bob_wilson: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Jonh"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_smith.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_fuzzy_name_match_by_surname(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
    jane_doe: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Smith"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_smith.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_fuzzy_name_match_by_middle_token(
    es_client: Any,
    individuals_list_url: str,
    maria_elena_gomez: Any,
    jane_doe: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Elena"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(maria_elena_gomez.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_fuzzy_name_match_is_case_insensitive(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "john"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_smith.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_fuzzy_name_no_match_beyond_edit_distance(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Zxcvb"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_fuzzy_name_preserves_phonetic_behavior(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
    jon_baptiste: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Jon"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    returned_ids = {r["id"] for r in results}
    assert str(jon_baptiste.id) in returned_ids
    assert str(john_smith.id) in returned_ids


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_fuzzy_name_operator_and_matches_when_all_terms_present(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "John Smith"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_smith.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_fuzzy_name_operator_and_no_match_when_one_term_missing(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "John Zxcvb"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_fuzzy_name_matches_tokens_out_of_order(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
    bob_wilson: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Smith John"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_smith.id)


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_search_db_fallback_name_still_works_when_es_disabled(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
    jane_doe: Any,
    django_assert_num_queries: Any,
) -> None:
    with django_assert_num_queries(19):
        response = es_client.get(individuals_list_url, {"search": "John"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_smith.id)


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_search_db_fallback_unicef_id_case_insensitive(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
    jane_doe: Any,
) -> None:
    response = es_client.get(individuals_list_url, {"search": "ind-0000001"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_smith.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_hope_id_exact_match_case_insensitive_upper(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
    jane_doe: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "IND-0000001"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_smith.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_hope_id_exact_match_case_insensitive_lower(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "ind-0000001"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(john_smith.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_hope_id_different_id_no_match(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "IND-0000002"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_hope_id_partial_input_does_not_match(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "IND-00000"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_household_unicef_id_exact_match(
    es_client: Any,
    individuals_list_url: str,
    alice_in_aleppo: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "HH-0000001"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(alice_in_aleppo.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_household_address_contains_match(
    es_client: Any,
    individuals_list_url: str,
    alice_in_aleppo: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Aleppo"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(alice_in_aleppo.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_household_address_contains_match_middle_token(
    es_client: Any,
    individuals_list_url: str,
    alice_in_aleppo: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "street"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(alice_in_aleppo.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_household_address_case_insensitive(
    es_client: Any,
    individuals_list_url: str,
    alice_in_aleppo: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "ALEPPO"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(alice_in_aleppo.id)


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_household_address_no_match(
    es_client: Any,
    individuals_list_url: str,
    alice_in_aleppo: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "xyz"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@pytest.mark.parametrize(
    "search",
    ["*", "?", "street*aleppo", "main?street"],
    ids=["lone_star", "lone_question_mark", "star_inside_term", "question_mark_inside_term"],
)
@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_household_address_treats_wildcard_characters_literally(
    es_client: Any,
    individuals_list_url: str,
    alice_in_aleppo: Any,
    search: str,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": search})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 0


@pytest.mark.parametrize(
    ("search", "expected_individual"),
    [
        ("Alice Wonderland", "alice_wonderland"),
        ("IND-0000009", "bob_builder"),
        ("Damascus", "charlie_in_damascus"),
    ],
    ids=["name", "hope_id", "address"],
)
@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_main_search_box_matches_name_or_hope_id_or_address(
    es_client: Any,
    individuals_list_url: str,
    alice_wonderland: Any,
    bob_builder: Any,
    charlie_in_damascus: Any,
    request: pytest.FixtureRequest,
    search: str,
    expected_individual: str,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": search})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(request.getfixturevalue(expected_individual).id)


def _clause_signatures(afghanistan: BusinessArea, es_program: Program) -> set[tuple[str, str]]:
    request = types.SimpleNamespace(parser_context={"kwargs": {"business_area_slug": afghanistan.slug}})
    f = IndividualFilter.__new__(IndividualFilter)
    f.request = request

    query = f._get_elasticsearch_query_for_individuals("test", es_program)
    should = query["query"]["bool"]["should"]

    signatures = set()
    for clause in should:
        for query_type, body in clause.items():
            for field_name in body:
                signatures.add((query_type, field_name))
    return signatures


@override_config(ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_es_query_shape_contains_expected_clauses(
    afghanistan: BusinessArea,
    es_program: Program,
) -> None:
    clause_signatures = _clause_signatures(afghanistan, es_program)

    assert ("term", "unicef_id.keyword") in clause_signatures
    assert ("term", "household.unicef_id.keyword") in clause_signatures
    assert ("wildcard", "household.address") in clause_signatures
    assert ("match", "full_name") in clause_signatures


@override_config(ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=False)
def test_es_query_shape_flag_off_uses_match_phrase_prefix(
    afghanistan: BusinessArea,
    es_program: Program,
) -> None:
    clause_signatures = _clause_signatures(afghanistan, es_program)

    assert ("match_phrase_prefix", "unicef_id") in clause_signatures
    assert ("match_phrase_prefix", "household.unicef_id") in clause_signatures
    assert ("match_phrase_prefix", "full_name") in clause_signatures
    assert ("term", "unicef_id.keyword") not in clause_signatures
    assert ("term", "household.unicef_id.keyword") not in clause_signatures
    assert ("wildcard", "household.address") not in clause_signatures


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=False)
def test_hope_id_prefix_search_still_works_before_fleet_reindex(
    es_client: Any,
    individuals_list_url: str,
    john_smith: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "IND-00000"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_es_search_does_not_leak_across_business_areas(
    es_client: Any,
    individuals_list_url: str,
    afghan_person: Any,
    ukrainian_person: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Person"})
    assert response.status_code == status.HTTP_200_OK
    returned_ids = {r["id"] for r in response.json()["results"]}
    assert str(afghan_person.id) in returned_ids
    assert str(ukrainian_person.id) not in returned_ids


@override_config(IS_ELASTICSEARCH_ENABLED=True, ES_USE_EXACT_ID_AND_ADDRESS_SEARCH=True)
def test_es_search_does_not_leak_across_programs(
    es_client: Any,
    individuals_list_url: str,
    afghan_person: Any,
    other_program_person: Any,
) -> None:
    rebuild_search_index()
    _refresh_es_index()

    response = es_client.get(individuals_list_url, {"search": "Person"})
    assert response.status_code == status.HTTP_200_OK
    returned_ids = {r["id"] for r in response.json()["results"]}
    assert str(afghan_person.id) in returned_ids
    assert str(other_program_person.id) not in returned_ids
