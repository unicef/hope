from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import HouseholdFactory, PartnerFactory, ProgramFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Program

pytestmark = pytest.mark.django_db


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


def _create_individual(es_program: Program, afghanistan: BusinessArea, **kwargs: Any) -> Any:
    hh = HouseholdFactory(program=es_program, business_area=afghanistan)
    ind = hh.head_of_household
    for field, value in kwargs.items():
        setattr(ind, field, value)
    ind.save()
    return ind


def test_phone_filter_matches_substring(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    target = _create_individual(es_program, afghanistan, phone_no="+48123456789")
    _create_individual(es_program, afghanistan, phone_no="+19998887777")

    response = es_client.get(individuals_list_url, {"phone": "3456"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(target.id)


def test_phone_filter_matches_on_alternative(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    target = _create_individual(
        es_program,
        afghanistan,
        phone_no="",
        phone_no_alternative="+48999000111",
    )
    _create_individual(es_program, afghanistan, phone_no="+19998887777")

    response = es_client.get(individuals_list_url, {"phone": "999000"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(target.id)


def test_phone_filter_matches_by_country_code(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    pl1 = _create_individual(es_program, afghanistan, phone_no="+4812123456789")
    pl2 = _create_individual(es_program, afghanistan, phone_no="+4812111222333")
    _create_individual(es_program, afghanistan, phone_no="+19998887777")

    response = es_client.get(individuals_list_url, {"phone": "+4812"})
    assert response.status_code == status.HTTP_200_OK
    returned_ids = {r["id"] for r in response.json()["results"]}
    assert str(pl1.id) in returned_ids
    assert str(pl2.id) in returned_ids
    assert len(returned_ids) == 2


def test_phone_filter_accepts_exactly_4_digits(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    _create_individual(es_program, afghanistan, phone_no="+48123456789")

    response = es_client.get(individuals_list_url, {"phone": "1234"})
    assert response.status_code == status.HTTP_200_OK


def test_phone_filter_ignores_non_digit_formatting(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    target = _create_individual(es_program, afghanistan, phone_no="+48123456789")

    response = es_client.get(individuals_list_url, {"phone": "+48 123 456"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(target.id)


def test_phone_filter_rejects_input_under_4_digits(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    response = es_client.get(individuals_list_url, {"phone": "123"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_phone_filter_rejects_input_of_3_digits_with_spaces(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    response = es_client.get(individuals_list_url, {"phone": " 1 2 3 "})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_phone_filter_empty_value_ignored(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    _create_individual(es_program, afghanistan, phone_no="+48123456789")
    _create_individual(es_program, afghanistan, phone_no="+19998887777")

    response = es_client.get(individuals_list_url, {"phone": ""})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 2


def test_phone_filter_query_param_name_is_phone(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
) -> None:
    _create_individual(es_program, afghanistan, phone_no="+48123456789")
    _create_individual(es_program, afghanistan, phone_no="+19998887777")

    wrong_name = es_client.get(individuals_list_url, {"phone_number": "1234"})
    assert wrong_name.status_code == status.HTTP_200_OK
    assert len(wrong_name.json()["results"]) == 2

    correct_name = es_client.get(individuals_list_url, {"phone": "3456"})
    assert correct_name.status_code == status.HTTP_200_OK
    assert len(correct_name.json()["results"]) == 1


def test_phone_filter_query_count(
    es_client: Any,
    individuals_list_url: str,
    es_program: Program,
    afghanistan: BusinessArea,
    django_assert_num_queries: Any,
) -> None:
    _create_individual(es_program, afghanistan, phone_no="+48123456789")

    with django_assert_num_queries(18):
        response = es_client.get(individuals_list_url, {"phone": "1234"})
    assert response.status_code == status.HTTP_200_OK
