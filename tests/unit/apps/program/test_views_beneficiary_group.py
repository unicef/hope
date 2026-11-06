"""Tests for beneficiary group views and models."""

from typing import Any, Callable

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    PayeeTypeFactory,
    UserFactory,
)
from hope.models import BeneficiaryGroup, BusinessArea, DataCollectingType, PayeeType, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory()


@pytest.fixture
def household_payee_type(db: Any) -> PayeeType:
    return PayeeTypeFactory(name="Household", gl_code="7700410")


@pytest.fixture
def incentive_payee_type(db: Any) -> PayeeType:
    return PayeeTypeFactory(name="Incentive Payee", gl_code="7700430")


@pytest.fixture
def frontline_worker_education(incentive_payee_type: PayeeType) -> DataCollectingType:
    return DataCollectingTypeFactory(
        code="frontline_worker_education",
        type=DataCollectingType.Type.SOCIAL,
        payee_type=incentive_payee_type,
    )


@pytest.fixture
def beneficiary_group1(household_payee_type: PayeeType) -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="Household", payee_type=household_payee_type)


@pytest.fixture
def beneficiary_group2(
    incentive_payee_type: PayeeType, frontline_worker_education: DataCollectingType
) -> BeneficiaryGroup:
    beneficiary_group = BeneficiaryGroupFactory(name="Education workers", payee_type=incentive_payee_type)
    beneficiary_group.data_collecting_types.add(frontline_worker_education)
    return beneficiary_group


@pytest.fixture
def inactive_beneficiary_group(household_payee_type: PayeeType) -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="Retired", payee_type=household_payee_type, active=False)


@pytest.fixture
def list_url() -> str:
    return reverse("api:programs:beneficiary-groups-list")


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_list_beneficiary_group(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    beneficiary_group1: BeneficiaryGroup,
    beneficiary_group2: BeneficiaryGroup,
    list_url: str,
) -> None:
    cache.clear()
    response = authenticated_client.get(list_url)
    beneficiary_group1.refresh_from_db()
    beneficiary_group2.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert {
        "id": str(beneficiary_group1.id),
        "name": "Household",
        "group_label": beneficiary_group1.group_label,
        "group_label_plural": beneficiary_group1.group_label_plural,
        "member_label": beneficiary_group1.member_label,
        "member_label_plural": beneficiary_group1.member_label_plural,
        "payee_type": str(beneficiary_group1.payee_type_id),
        "data_collecting_types": [],
        "active": True,
    } in response.json()["results"]
    assert {
        "id": str(beneficiary_group2.id),
        "name": "Education workers",
        "group_label": beneficiary_group2.group_label,
        "group_label_plural": beneficiary_group2.group_label_plural,
        "member_label": beneficiary_group2.member_label,
        "member_label_plural": beneficiary_group2.member_label_plural,
        "payee_type": str(beneficiary_group2.payee_type_id),
        "data_collecting_types": ["frontline_worker_education"],
        "active": True,
    } in response.json()["results"]


def test_list_beneficiary_group_filtered_by_active_returns_only_active(
    authenticated_client: Any,
    beneficiary_group1: BeneficiaryGroup,
    inactive_beneficiary_group: BeneficiaryGroup,
    list_url: str,
) -> None:
    cache.clear()

    response = authenticated_client.get(list_url, {"active": "true"})

    assert response.status_code == status.HTTP_200_OK
    assert [result["name"] for result in response.json()["results"]] == ["Household"]


def test_list_beneficiary_group_cache_invalidated_when_data_collecting_types_change(
    authenticated_client: Any,
    beneficiary_group1: BeneficiaryGroup,
    frontline_worker_education: DataCollectingType,
    list_url: str,
) -> None:
    response = authenticated_client.get(list_url)
    etag = response.headers["ETAG"]

    with TestCase.captureOnCommitCallbacks(execute=True):
        beneficiary_group1.data_collecting_types.add(frontline_worker_education)
    response = authenticated_client.get(list_url, HTTP_IF_NONE_MATCH=etag)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"][0]["data_collecting_types"] == ["frontline_worker_education"]


def test_list_beneficiary_group_caching(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    beneficiary_group1: BeneficiaryGroup,
    beneficiary_group2: BeneficiaryGroup,
    list_url: str,
) -> None:
    response = authenticated_client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
    etag = response.headers["ETAG"]

    response = authenticated_client.get(list_url, HTTP_IF_NONE_MATCH=etag)
    assert response.status_code == status.HTTP_304_NOT_MODIFIED
    etag_after_cache = response.headers["ETAG"]

    with TestCase.captureOnCommitCallbacks(execute=True):
        beneficiary_group1.group_label = "new_group_label"
        beneficiary_group1.save()
    response = authenticated_client.get(list_url, HTTP_IF_NONE_MATCH=etag)
    assert response.status_code == status.HTTP_200_OK
    after_edit_etag = response.headers["ETAG"]
    assert etag_after_cache != after_edit_etag

    with TestCase.captureOnCommitCallbacks(execute=True):
        beneficiary_group3 = BeneficiaryGroupFactory(name="Other `BG")
    response = authenticated_client.get(list_url, HTTP_IF_NONE_MATCH=after_edit_etag)
    assert response.status_code == status.HTTP_200_OK
    after_create_etag = response.headers["ETAG"]
    assert after_edit_etag != after_create_etag

    with TestCase.captureOnCommitCallbacks(execute=True):
        beneficiary_group3.delete()
    response = authenticated_client.get(list_url, HTTP_IF_NONE_MATCH=after_create_etag)
    assert response.status_code == status.HTTP_200_OK
    after_delete_etag = response.headers["ETAG"]
    assert after_create_etag != after_delete_etag

    response = authenticated_client.get(list_url, HTTP_IF_NONE_MATCH=after_delete_etag)
    assert response.status_code == status.HTTP_304_NOT_MODIFIED
    etag_after_cache_2 = response.headers["ETAG"]
    assert etag_after_cache_2 == after_delete_etag


def test_beneficiary_group_str() -> None:
    bg = BeneficiaryGroup(name="Test Group")
    assert str(bg) == "Test Group"
