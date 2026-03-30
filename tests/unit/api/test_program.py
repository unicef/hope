from datetime import timedelta

from django.utils import timezone
import pytest
from rest_framework.test import APIClient

from hope.models import APIToken, BusinessArea, Program
from hope.models.grant import Grant
from unit.api.conftest import token_grant_permission

pytestmark = pytest.mark.django_db


# --- Program create (BA-scoped) ---


def test_create_program_returns_403_without_permission(
    token_api_client: APIClient,
    program_create_url: str,
    program_create_payload: dict,
) -> None:
    response = token_api_client.post(program_create_url, program_create_payload, format="json")
    assert response.status_code == 403


def test_create_program_returns_403_with_read_only_grant(
    token_api_client: APIClient,
    api_token: APIToken,
    program_create_url: str,
    program_create_payload: dict,
) -> None:
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = token_api_client.post(program_create_url, program_create_payload, format="json")
    assert response.status_code == 403


def test_create_program_succeeds_with_create_permission(
    token_api_client: APIClient,
    api_token: APIToken,
    program_create_url: str,
    program_create_payload: dict,
    business_area: BusinessArea,
) -> None:
    with (
        token_grant_permission(api_token, Grant.API_READ_ONLY),
        token_grant_permission(api_token, Grant.API_PROGRAM_CREATE),
    ):
        response = token_api_client.post(program_create_url, program_create_payload, format="json")

    assert response.status_code == 201, response.json()
    data = response.json()

    program = Program.objects.get(name="Program #1")
    assert data == {
        "budget": "10000.00",
        "cash_plus": True,
        "end_date": "2022-09-27",
        "frequency_of_payments": "ONE_OFF",
        "id": str(program.id),
        "name": "Program #1",
        "population_goal": 101,
        "sector": "CHILD_PROTECTION",
        "start_date": "2022-09-27",
        "data_collecting_type": program.data_collecting_type_id,
        "beneficiary_group": str(program.beneficiary_group_id),
    }
    assert program.business_area == business_area


# --- Program list (BA-scoped) ---


def test_list_programs_returns_403_without_permission(
    token_api_client: APIClient,
    program_list_url: str,
) -> None:
    response = token_api_client.get(program_list_url)
    assert response.status_code == 403


def test_list_programs_returns_only_own_business_area(
    token_api_client: APIClient,
    api_token: APIToken,
    program_list_url: str,
    ba_scoped_programs: tuple[Program, Program],
) -> None:
    program1, program2 = ba_scoped_programs

    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = token_api_client.get(program_list_url)

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert _ba_expected(program1) in results
    assert _ba_expected(program2) in results


def _ba_expected(p: Program) -> dict:
    return {
        "budget": str(p.budget),
        "cash_plus": p.cash_plus,
        "end_date": p.end_date.strftime("%Y-%m-%d"),
        "frequency_of_payments": p.frequency_of_payments,
        "id": str(p.id),
        "name": p.name,
        "population_goal": p.population_goal,
        "sector": p.sector,
        "start_date": p.start_date.strftime("%Y-%m-%d"),
        "data_collecting_type": p.data_collecting_type_id,
        "beneficiary_group": str(p.beneficiary_group_id),
    }


# --- Global program list ---


def _global_expected(p: Program) -> dict:
    return {
        "budget": str(p.budget),
        "business_area_code": p.business_area.code,
        "cash_plus": p.cash_plus,
        "end_date": p.end_date.strftime("%Y-%m-%d"),
        "frequency_of_payments": p.frequency_of_payments,
        "id": str(p.id),
        "name": p.name,
        "population_goal": p.population_goal,
        "code": p.code,
        "scope": p.scope,
        "sector": p.sector,
        "status": p.status,
        "start_date": p.start_date.strftime("%Y-%m-%d"),
        "beneficiary_group": str(p.beneficiary_group.id),
        "biometric_deduplication_enabled": p.biometric_deduplication_enabled,
    }


def test_global_list_returns_403_without_permission(
    token_api_client: APIClient,
    program_global_list_url: str,
) -> None:
    response = token_api_client.get(program_global_list_url)
    assert response.status_code == 403


def test_global_list_returns_all_programs(
    token_api_client: APIClient,
    api_token: APIToken,
    program_global_list_url: str,
    three_programs: tuple[Program, Program, Program],
) -> None:
    program_active, program_draft, program_other_ba = three_programs

    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = token_api_client.get(program_global_list_url)

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 3
    assert _global_expected(program_active) in results
    assert _global_expected(program_draft) in results
    assert _global_expected(program_other_ba) in results


def test_global_list_filter_business_area(
    token_api_client: APIClient,
    api_token: APIToken,
    program_global_list_url: str,
    three_programs: tuple[Program, Program, Program],
) -> None:
    _program_active, _program_draft, program_other_ba = three_programs

    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = token_api_client.get(program_global_list_url, {"business_area": "afghanistan"})

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 2
    assert _global_expected(program_other_ba) not in results


@pytest.mark.parametrize(("active_value", "expected_count"), [("true", 2), ("false", 1)])
def test_global_list_filter_active(
    token_api_client: APIClient,
    api_token: APIToken,
    program_global_list_url: str,
    three_programs: tuple[Program, Program, Program],
    active_value: str,
    expected_count: int,
) -> None:
    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = token_api_client.get(program_global_list_url, {"active": active_value})

    assert response.status_code == 200
    assert len(response.json()["results"]) == expected_count


def test_global_list_filter_status(
    token_api_client: APIClient,
    api_token: APIToken,
    program_global_list_url: str,
    three_programs: tuple[Program, Program, Program],
) -> None:
    _program_active, program_draft, _program_other_ba = three_programs

    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = token_api_client.get(program_global_list_url, {"status": Program.DRAFT})

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert _global_expected(program_draft) in results


@pytest.mark.parametrize(
    ("filter_key", "days_offset", "expected_count"),
    [
        ("updated_at_before", 1, 3),
        ("updated_at_after", 1, 0),
        ("updated_at_before", -1, 0),
        ("updated_at_after", -1, 3),
    ],
)
def test_global_list_filter_updated_at(
    token_api_client: APIClient,
    api_token: APIToken,
    program_global_list_url: str,
    three_programs: tuple[Program, Program, Program],
    filter_key: str,
    days_offset: int,
    expected_count: int,
) -> None:
    filter_date = (timezone.now() + timedelta(days=days_offset)).date().strftime("%Y-%m-%d")

    with token_grant_permission(api_token, Grant.API_READ_ONLY):
        response = token_api_client.get(program_global_list_url, {filter_key: filter_date})

    assert response.status_code == 200
    assert len(response.json()["results"]) == expected_count
