"""Tests for program list API endpoint."""

import datetime
from enum import Enum
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.old_factories.account import PartnerFactory, UserFactory
from extras.test_utils.old_factories.core import (
    DataCollectingTypeFactory,
    FlexibleAttributeForPDUFactory,
    create_afghanistan,
    create_ukraine,
)
from extras.test_utils.old_factories.household import (
    HouseholdFactory,
)
from extras.test_utils.old_factories.program import (
    BeneficiaryGroupFactory,
    ProgramFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import (
    BusinessArea,
    FlexibleAttribute,
    Partner,
    Program,
    User,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return create_afghanistan()


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def pdu_field1(program: Program) -> FlexibleAttribute:
    return FlexibleAttributeForPDUFactory(program=program)


@pytest.fixture
def pdu_field2(program: Program) -> FlexibleAttribute:
    return FlexibleAttributeForPDUFactory(program=program)


@pytest.fixture
def pdu_field_other(db: Any) -> FlexibleAttribute:
    return FlexibleAttributeForPDUFactory()


@pytest.fixture
def ukraine(db: Any) -> BusinessArea:
    return create_ukraine()


@pytest.fixture
def program_in_ukraine(ukraine: BusinessArea) -> Program:
    """Program in Ukraine should NOT be on the list"""
    return ProgramFactory(business_area=ukraine)


@pytest.fixture
def program_with_dct_deprecated(afghanistan: BusinessArea) -> Program:
    """Program with deprecated DCT should NOT be on the list"""
    deprecated_dct = DataCollectingTypeFactory(deprecated=True)
    return ProgramFactory(
        business_area=afghanistan,
        name="Deprecated DCT Program",
        data_collecting_type=deprecated_dct,
    )


@pytest.fixture
def program_with_unknown_dct(afghanistan: BusinessArea) -> Program:
    """Program with unknown DCT should NOT be on the list"""
    unknown_dct = DataCollectingTypeFactory(code="unknown")
    return ProgramFactory(
        business_area=afghanistan,
        name="Unknown DCT Program",
        data_collecting_type=unknown_dct,
    )


@pytest.fixture
def program_not_allowed(afghanistan: BusinessArea) -> Program:
    """Program not in allowed_programs should NOT be on the list"""
    return ProgramFactory(business_area=afghanistan, name="Not Allowed Program")


@pytest.fixture
def list_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:programs:programs-list",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.fixture
def count_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:programs:programs-count",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    cache.clear()


@pytest.mark.parametrize(
    "permissions",
    [
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        [Permissions.GRIEVANCES_CREATE],
        [Permissions.GRIEVANCES_UPDATE],
        [Permissions.GRIEVANCES_UPDATE_AS_CREATOR],
        [Permissions.GRIEVANCES_UPDATE_AS_OWNER],
        [Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE],
        [Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR],
        [Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER],
    ],
)
def test_program_list_with_permissions(
    permissions: list,
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    program_in_ukraine: Program,
    program_with_dct_deprecated: Program,
    program_with_unknown_dct: Program,
    program_not_allowed: Program,
    pdu_field1: FlexibleAttribute,
    pdu_field2: FlexibleAttribute,
    pdu_field_other: FlexibleAttribute,
    list_url: str,
    count_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    for prog in [
        program,
        program_in_ukraine,
        program_with_dct_deprecated,
        program_with_unknown_dct,
    ]:
        create_user_role_with_permissions(
            user,
            permissions,
            afghanistan,
            prog,
        )
    response = authenticated_client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1

    response_count = authenticated_client.get(count_url)
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 1

    program_ids = [prog["id"] for prog in response_data]
    assert str(program.id) in program_ids
    assert str(program_in_ukraine.id) not in program_ids
    assert str(program_with_dct_deprecated.id) not in program_ids
    assert str(program_with_unknown_dct.id) not in program_ids
    assert str(program_not_allowed.id) not in program_ids

    program_data1 = response_data[0]
    assert program_data1["id"] == str(program.id)
    assert program_data1["programme_code"] == program.programme_code
    assert program_data1["slug"] == program.slug
    assert program_data1["name"] == program.name
    assert program_data1["start_date"] == program.start_date.strftime("%Y-%m-%d")
    assert program_data1["end_date"] == program.end_date.strftime("%Y-%m-%d")
    assert program_data1["budget"] == str(program.budget)
    assert program_data1["frequency_of_payments"] == program.frequency_of_payments
    assert program_data1["sector"] == program.sector
    assert program_data1["cash_plus"] == program.cash_plus
    assert program_data1["population_goal"] == program.population_goal
    assert program_data1["status"] == program.status
    assert program_data1["household_count"] == program.household_count

    data_collecting_type_program_data1 = program_data1["data_collecting_type"]
    assert data_collecting_type_program_data1["id"] == program.data_collecting_type.id
    assert data_collecting_type_program_data1["label"] == program.data_collecting_type.label
    assert data_collecting_type_program_data1["code"] == program.data_collecting_type.code
    assert data_collecting_type_program_data1["type"] == program.data_collecting_type.type
    assert (
        data_collecting_type_program_data1["household_filters_available"]
        == program.data_collecting_type.household_filters_available
    )
    assert (
        data_collecting_type_program_data1["individual_filters_available"]
        == program.data_collecting_type.individual_filters_available
    )

    beneficiary_group_program_data1 = program_data1["beneficiary_group"]
    assert beneficiary_group_program_data1["id"] == str(program.beneficiary_group.id)
    assert beneficiary_group_program_data1["name"] == program.beneficiary_group.name
    assert beneficiary_group_program_data1["group_label"] == program.beneficiary_group.group_label
    assert beneficiary_group_program_data1["group_label_plural"] == program.beneficiary_group.group_label_plural
    assert beneficiary_group_program_data1["member_label"] == program.beneficiary_group.member_label
    assert beneficiary_group_program_data1["member_label_plural"] == program.beneficiary_group.member_label_plural
    assert beneficiary_group_program_data1["master_detail"] == program.beneficiary_group.master_detail

    assert str(pdu_field1.id) in program_data1["pdu_fields"]
    assert str(pdu_field2.id) in program_data1["pdu_fields"]
    assert len(program_data1["pdu_fields"]) == 2


@pytest.mark.parametrize(
    "permissions",
    [
        [],
        [Permissions.PM_SEND_XLSX_PASSWORD],
    ],
)
def test_program_list_without_permissions(
    permissions: Enum,
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        program,
    )
    response = authenticated_client.get(list_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_program_list_ordering(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program_finished = ProgramFactory(business_area=afghanistan, status=Program.FINISHED)
    program_draft_first = ProgramFactory(
        business_area=afghanistan,
        status=Program.DRAFT,
        start_date=datetime.datetime(2000, 1, 1),
    )
    program_draft_second = ProgramFactory(
        business_area=afghanistan,
        status=Program.DRAFT,
        start_date=datetime.datetime(2001, 1, 1),
    )
    for prog in [
        program,
        program_finished,
        program_draft_first,
        program_draft_second,
    ]:
        create_user_role_with_permissions(
            user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            afghanistan,
            prog,
        )
    response = authenticated_client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 4

    assert response_data[0]["id"] == str(program_draft_first.id)
    assert response_data[1]["id"] == str(program_draft_second.id)
    assert response_data[2]["id"] == str(program.id)
    assert response_data[3]["id"] == str(program_finished.id)


def test_program_list_caching(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    program_in_ukraine: Program,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    no_queries_not_cached_no_permissions = 11
    no_queries_not_cached_with_permissions = 7
    no_queries_cached = 5

    program_afghanistan2 = ProgramFactory(business_area=afghanistan)
    for prog in [
        program,
        program_in_ukraine,
    ]:
        create_user_role_with_permissions(
            user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            afghanistan,
            prog,
        )

    def _test_response_len_and_queries(response_len: int, queries_len: int) -> None:
        with CaptureQueriesContext(connection) as queries:
            response = authenticated_client.get(list_url)
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()["results"]
            assert len(response_data) == response_len
            assert len(queries) == queries_len

    _test_response_len_and_queries(1, no_queries_not_cached_no_permissions)
    # second request should be cached
    _test_response_len_and_queries(1, no_queries_cached)  # on CI we have 7 here instead of 5 #FIXME
    # caching data should invalidate cache, -4 queries because of cached permissions
    program.name = "New Name"
    program.save()
    _test_response_len_and_queries(1, no_queries_not_cached_with_permissions)
    # changing programs from other business area should not invalidate cache
    program_in_ukraine.name = "New Name"
    program_in_ukraine.save()
    _test_response_len_and_queries(1, 5)  # on CI we have 7 here instead of 5 #FIXME
    # changing user permissions should invalidate cache
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program_afghanistan2,
    )
    _test_response_len_and_queries(2, no_queries_not_cached_no_permissions)
    # cached data with another call
    _test_response_len_and_queries(2, no_queries_cached)


def test_program_count_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    count_url: str,
    program: Program,
    program_with_dct_deprecated: Program,
    program_with_unknown_dct: Program,
    program_not_allowed: Program,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(count_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 2  # program_not_allowed is included because whole_business_area_access


def test_program_count_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    count_url: str,
    program: Program,
    program_with_dct_deprecated: Program,
    program_with_unknown_dct: Program,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(count_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_filter_by_status(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program1 = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)
    program2 = ProgramFactory(business_area=afghanistan, status=Program.FINISHED)
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    response = authenticated_client.get(list_url, {"status": Program.ACTIVE})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(program1.id)
    assert response_data[0]["status"] == Program.ACTIVE


def test_filter_by_sector(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program1 = ProgramFactory(business_area=afghanistan, sector=Program.HEALTH)
    program2 = ProgramFactory(business_area=afghanistan, sector=Program.EDUCATION)
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    response = authenticated_client.get(list_url, {"sector": Program.HEALTH})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(program1.id)
    assert response_data[0]["sector"] == Program.HEALTH


def test_filter_by_budget(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program1 = ProgramFactory(business_area=afghanistan, budget=2000)
    program2 = ProgramFactory(business_area=afghanistan, budget=1000)
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    response = authenticated_client.get(list_url, {"budget_min": 1500})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(program1.id)
    assert response_data[0]["budget"] == "2000.00"


def test_filter_by_start_date(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program1 = ProgramFactory(business_area=afghanistan, start_date=datetime.datetime(2023, 1, 1))
    program2 = ProgramFactory(business_area=afghanistan, start_date=datetime.datetime(2022, 1, 1))
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    response = authenticated_client.get(list_url, {"start_date": "2022-12-31"})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(program1.id)
    assert response_data[0]["start_date"] == "2023-01-01"


def test_filter_by_end_date(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program1 = ProgramFactory(
        business_area=afghanistan,
        start_date=datetime.datetime(2020, 1, 1),
        end_date=datetime.datetime(2022, 1, 1),
    )
    program2 = ProgramFactory(
        business_area=afghanistan,
        start_date=datetime.datetime(2020, 1, 1),
        end_date=datetime.datetime(2023, 1, 1),
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    response = authenticated_client.get(list_url, {"end_date": "2022-12-31"})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(program1.id)
    assert response_data[0]["end_date"] == "2022-01-01"


def test_filter_by_name(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program1 = ProgramFactory(business_area=afghanistan, name="Health Program")
    program2 = ProgramFactory(business_area=afghanistan, name="Education Program")
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    response = authenticated_client.get(list_url, {"name": "Health"})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(program1.id)


def test_filter_by_compatible_dct(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    dct1 = DataCollectingTypeFactory(code="type1")
    dct2 = DataCollectingTypeFactory(code="type2")
    dct2.compatible_types.add(dct1)
    program1 = ProgramFactory(business_area=afghanistan, data_collecting_type=dct1)
    program2 = ProgramFactory(business_area=afghanistan, data_collecting_type=dct2)
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    response = authenticated_client.get(list_url, {"compatible_dct": program1.slug})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(program2.id)


def test_filter_by_beneficiary_group_match(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    beneficiary_group1 = BeneficiaryGroupFactory(name="Group1")
    beneficiary_group2 = BeneficiaryGroupFactory(name="Group2")
    program1 = ProgramFactory(business_area=afghanistan, beneficiary_group=beneficiary_group1)
    program2 = ProgramFactory(business_area=afghanistan, beneficiary_group=beneficiary_group2)
    program3 = ProgramFactory(business_area=afghanistan, beneficiary_group=beneficiary_group1)
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    # additional check to test filter doesn't break allowed_programs constraints
    response = authenticated_client.get(list_url, {"beneficiary_group_match": program1.slug})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 0

    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program3,
    )
    response = authenticated_client.get(list_url, {"beneficiary_group_match": program1.slug})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(program3.id)


def test_filter_by_search(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program1 = ProgramFactory(business_area=afghanistan, name="Health Program")
    program2 = ProgramFactory(business_area=afghanistan, name="Education Program")
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    response = authenticated_client.get(list_url, {"search": "Health"})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(program1.id)


def test_filter_number_of_households(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    program1 = ProgramFactory(business_area=afghanistan)
    program2 = ProgramFactory(business_area=afghanistan)
    HouseholdFactory.create_batch(5, business_area=afghanistan, program=program1)
    HouseholdFactory.create_batch(3, business_area=afghanistan, program=program2)
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program1,
    )
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program2,
    )

    response_min = authenticated_client.get(list_url, {"number_of_households_min": 4})
    assert response_min.status_code == status.HTTP_200_OK
    response_data_min = response_min.json()["results"]
    assert len(response_data_min) == 1
    assert response_data_min[0]["id"] == str(program1.id)

    response_max = authenticated_client.get(list_url, {"number_of_households_max": 4})
    assert response_max.status_code == status.HTTP_200_OK
    response_data_max = response_max.json()["results"]
    assert len(response_data_max) == 1
    assert response_data_max[0]["id"] == str(program2.id)
