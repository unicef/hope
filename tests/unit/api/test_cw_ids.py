import pytest

from extras.test_utils.factories.household import IndividualFactory
from hope.api.endpoints.rdi.cw_ids import (
    collect_cw_ids,
    collect_member_cw_ids,
    collect_originating_ids,
    cw_id_error,
    duplicated_cw_ids,
    existing_cw_ids,
)
from hope.models import BusinessArea


def test_duplicated_cw_ids_returns_ids_seen_more_than_once() -> None:
    assert duplicated_cw_ids(["a", "a", "b", "c", "c", "c"]) == {"a", "c"}


def test_duplicated_cw_ids_returns_empty_when_every_id_is_unique() -> None:
    assert duplicated_cw_ids(["a", "b", "c"]) == set()


def test_collect_cw_ids_returns_ids_in_payload_order() -> None:
    request_data = [{"country_workspace_id": "2"}, {"country_workspace_id": "1"}]

    assert collect_cw_ids(request_data) == ["2", "1"]


def test_collect_cw_ids_casts_numeric_id_the_way_the_serializer_casts_it() -> None:
    request_data = [{"country_workspace_id": 7}, {"country_workspace_id": 0}]

    assert collect_cw_ids(request_data) == ["7", "0"]


@pytest.mark.parametrize(
    "row",
    [
        pytest.param("not-a-dict", id="non_dict_row"),
        pytest.param({"country_workspace_id": ""}, id="blank_cw_id"),
        pytest.param({"country_workspace_id": ["7"]}, id="composite_cw_id"),
        pytest.param({"country_workspace_id": None}, id="null_cw_id"),
        pytest.param({"full_name": "John Doe"}, id="cw_id_absent"),
    ],
)
def test_collect_cw_ids_skips_row_without_usable_cw_id(row: object) -> None:
    assert collect_cw_ids([row]) == []


def test_collect_originating_ids_returns_ids_of_replaced_rows() -> None:
    request_data = [{"originating_id": "XLS#1#1"}, {"originating_id": "KOB#321#123"}]

    assert collect_originating_ids(request_data) == {"XLS#1#1", "KOB#321#123"}


@pytest.mark.parametrize(
    "row",
    [
        pytest.param("not-a-dict", id="non_dict_row"),
        pytest.param({"originating_id": ""}, id="blank_originating_id"),
        pytest.param({"originating_id": None}, id="null_originating_id"),
        pytest.param({"full_name": "John Doe"}, id="originating_id_absent"),
    ],
)
def test_collect_originating_ids_skips_row_without_originating_id(row: object) -> None:
    assert collect_originating_ids([row]) == set()


def test_collect_member_cw_ids_returns_ids_across_every_household() -> None:
    request_data = [
        {"members": [{"country_workspace_id": "1"}, {"country_workspace_id": "2"}]},
        {"members": [{"country_workspace_id": "3"}]},
    ]

    assert collect_member_cw_ids(request_data) == ["1", "2", "3"]


def test_collect_member_cw_ids_casts_numeric_id_the_way_the_serializer_casts_it() -> None:
    request_data = [{"members": [{"country_workspace_id": 7}, {"country_workspace_id": 0}]}]

    assert collect_member_cw_ids(request_data) == ["7", "0"]


def test_collect_member_cw_ids_skips_non_dict_household() -> None:
    request_data = ["not-a-household", {"members": [{"country_workspace_id": "1"}]}]

    assert collect_member_cw_ids(request_data) == ["1"]


def test_collect_member_cw_ids_skips_non_dict_member() -> None:
    request_data = [{"members": ["not-a-member", {"country_workspace_id": "1"}]}]

    assert collect_member_cw_ids(request_data) == ["1"]


@pytest.mark.parametrize(
    "household",
    [
        pytest.param({}, id="members_absent"),
        pytest.param({"members": None}, id="members_null"),
        pytest.param({"members": []}, id="members_empty"),
    ],
)
def test_collect_member_cw_ids_returns_empty_for_household_without_members(household: dict) -> None:
    assert collect_member_cw_ids([household]) == []


@pytest.mark.parametrize(
    "member",
    [
        pytest.param({"country_workspace_id": ""}, id="blank_cw_id"),
        pytest.param({"country_workspace_id": ["7"]}, id="composite_cw_id"),
        pytest.param({"country_workspace_id": None}, id="null_cw_id"),
        pytest.param({"full_name": "John Doe"}, id="cw_id_absent"),
    ],
)
def test_collect_member_cw_ids_skips_member_without_usable_cw_id(member: dict) -> None:
    assert collect_member_cw_ids([{"members": [member]}]) == []


def test_cw_id_error_reports_id_already_taken_in_business_area() -> None:
    error = cw_id_error("1", existing={"1"}, duplicated=set())

    assert error == {
        "country_workspace_id": ["Individual with country_workspace_id '1' already exists in this business area."]
    }


def test_cw_id_error_reports_id_duplicated_within_payload() -> None:
    error = cw_id_error("1", existing=set(), duplicated={"1"})

    assert error == {"country_workspace_id": ["country_workspace_id '1' is duplicated within this payload."]}


def test_cw_id_error_prefers_already_taken_over_duplicated_within_payload() -> None:
    error = cw_id_error("1", existing={"1"}, duplicated={"1"})

    assert error == {
        "country_workspace_id": ["Individual with country_workspace_id '1' already exists in this business area."]
    }


def test_cw_id_error_matches_numeric_id_against_the_cast_ids_in_the_payload_checks() -> None:
    error = cw_id_error(7, existing={"7"}, duplicated=set())

    assert error == {
        "country_workspace_id": ["Individual with country_workspace_id '7' already exists in this business area."]
    }


def test_cw_id_error_returns_none_when_id_is_free() -> None:
    assert cw_id_error("1", existing=set(), duplicated=set()) is None


@pytest.mark.django_db
def test_existing_cw_ids_returns_empty_without_querying_when_payload_has_no_ids(
    business_area: BusinessArea, django_assert_num_queries: object
) -> None:
    with django_assert_num_queries(0):
        assert existing_cw_ids(business_area, []) == set()


@pytest.mark.django_db
def test_existing_cw_ids_returns_only_ids_held_by_a_live_individual(business_area: BusinessArea) -> None:
    IndividualFactory(business_area=business_area, country_workspace_id="1")

    assert existing_cw_ids(business_area, ["1", "2"]) == {"1"}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "released",
    [
        pytest.param({"withdrawn": True}, id="withdrawn"),
        pytest.param({"is_removed": True}, id="soft_deleted"),
    ],
)
def test_existing_cw_ids_ignores_individual_that_released_its_id(business_area: BusinessArea, released: dict) -> None:
    IndividualFactory(business_area=business_area, country_workspace_id="1", **released)

    assert existing_cw_ids(business_area, ["1"]) == set()


@pytest.mark.django_db
def test_existing_cw_ids_ignores_individual_in_another_business_area(business_area: BusinessArea) -> None:
    IndividualFactory(country_workspace_id="1")

    assert existing_cw_ids(business_area, ["1"]) == set()


@pytest.mark.django_db
def test_existing_cw_ids_excludes_rows_the_re_push_replaces(business_area: BusinessArea) -> None:
    IndividualFactory(business_area=business_area, country_workspace_id="1", originating_id="XLS#1#1")

    assert existing_cw_ids(business_area, ["1"], exclude_originating_ids=["XLS#1#1"]) == set()


@pytest.mark.django_db
def test_existing_cw_ids_keeps_rows_the_re_push_does_not_replace(business_area: BusinessArea) -> None:
    IndividualFactory(business_area=business_area, country_workspace_id="1", originating_id="XLS#1#1")

    assert existing_cw_ids(business_area, ["1"], exclude_originating_ids=["XLS#9#9"]) == {"1"}
