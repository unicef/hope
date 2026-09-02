import pytest

from hope.api.utils import humanize_errors


@pytest.fixture
def top_level_error() -> dict:
    return {"program": ["This field is required."]}


@pytest.fixture
def household_error() -> dict:
    return {"country": ["This field is required."]}


@pytest.fixture
def member_error() -> dict:
    return {"full_name": ["This field is required."]}


def test_empty_dict() -> None:
    assert humanize_errors({}) == {}


def test_top_level_errors_only(top_level_error: dict) -> None:
    result = humanize_errors({**top_level_error})

    assert result == top_level_error


def test_households_string_error() -> None:
    errors = {"households": ["This field is required."]}
    result = humanize_errors(errors)

    assert result == {"households": ["This field is required."]}


def test_single_household_error(household_error: dict) -> None:
    errors = {"households": [household_error]}
    result = humanize_errors(errors)

    assert result == {"households": [{"Household #1": [{"country": ["This field is required."]}]}]}


def test_empty_household_skipped() -> None:
    errors = {"households": [{}]}
    result = humanize_errors(errors)

    assert result == {}


def test_multiple_households_only_errors_labeled(household_error: dict) -> None:
    errors = {"households": [{}, {}, household_error]}
    result = humanize_errors(errors)

    assert result == {"households": [{"Household #3": [{"country": ["This field is required."]}]}]}


def test_members_string_error(household_error: dict) -> None:
    errors = {"households": [{**household_error, "members": ["This field is required."]}]}
    result = humanize_errors(errors)

    assert result["households"][0]["Household #1"][0]["members"] == ["This field is required."]


def test_single_member_error(household_error: dict, member_error: dict) -> None:
    errors = {"households": [{**household_error, "members": [member_error]}]}
    result = humanize_errors(errors)

    hh = result["households"][0]["Household #1"][0]
    assert hh["members"] == {"Member #1": [{"full_name": ["This field is required."]}]}


def test_empty_member_skipped(household_error: dict, member_error: dict) -> None:
    errors = {"households": [{**household_error, "members": [{}, member_error]}]}
    result = humanize_errors(errors)

    hh = result["households"][0]["Household #1"][0]
    assert hh["members"] == {"Member #2": [{"full_name": ["This field is required."]}]}


def test_household_and_top_level_errors(top_level_error: dict, household_error: dict) -> None:
    errors = {**top_level_error, "households": [household_error]}
    result = humanize_errors(errors)

    assert result["program"] == ["This field is required."]
    assert "households" in result


def test_no_members_key_in_household() -> None:
    errors = {"households": [{"size": ["This field is required."]}]}
    result = humanize_errors(errors)

    assert result == {"households": [{"Household #1": [{"size": ["This field is required."]}]}]}


def test_empty_members_list(household_error: dict) -> None:
    errors = {"households": [{**household_error, "members": []}]}
    result = humanize_errors(errors)

    hh = result["households"][0]["Household #1"][0]
    assert "members" not in hh


def test_households_dict_single_error(household_error: dict) -> None:
    errors = {"households": {"0": household_error}}
    result = humanize_errors(errors)

    assert result == {"households": {"Household #0": [{"country": ["This field is required."]}]}}


def test_households_dict_keyed_by_index(household_error: dict) -> None:
    errors = {"households": {"1": household_error}}
    result = humanize_errors(errors)

    assert result == {"households": {"Household #1": [{"country": ["This field is required."]}]}}


def test_households_dict_only_failing_indices_included(household_error: dict) -> None:
    errors = {"households": {"0": {}, "2": household_error}}
    result = humanize_errors(errors)

    assert result == {"households": {"Household #2": [{"country": ["This field is required."]}]}}


def test_households_dict_string_error() -> None:
    errors = {"households": "This field is required."}
    result = humanize_errors(errors)

    assert result == {"households": ["This field is required."]}


def test_households_dict_members_dict(household_error: dict, member_error: dict) -> None:
    errors = {"households": {"0": {**household_error, "members": {"1": member_error}}}}
    result = humanize_errors(errors)

    hh = result["households"]["Household #0"][0]
    assert hh["members"] == {"Member #1": [{"full_name": ["This field is required."]}]}


def test_households_dict_members_only_failing_indices_included(household_error: dict, member_error: dict) -> None:
    errors = {"households": {"0": {**household_error, "members": {"0": {}, "2": member_error}}}}
    result = humanize_errors(errors)

    hh = result["households"]["Household #0"][0]
    assert hh["members"] == {"Member #2": [{"full_name": ["This field is required."]}]}
