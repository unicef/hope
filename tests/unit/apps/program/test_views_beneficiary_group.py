"""Tests for beneficiary group views and models."""

from typing import Any, Callable

from django.core.cache import cache
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    UserFactory,
)
from hope.models import BeneficiaryGroup, BusinessArea, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory()


@pytest.fixture
def beneficiary_group1(db: Any) -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="Household")


@pytest.fixture
def beneficiary_group2(db: Any) -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="Social Workers")


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
        "master_detail": beneficiary_group1.master_detail,
    } in response.json()["results"]
    assert {
        "id": str(beneficiary_group2.id),
        "name": "Social Workers",
        "group_label": beneficiary_group2.group_label,
        "group_label_plural": beneficiary_group2.group_label_plural,
        "member_label": beneficiary_group2.member_label,
        "member_label_plural": beneficiary_group2.member_label_plural,
        "master_detail": beneficiary_group2.master_detail,
    } in response.json()["results"]


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

    beneficiary_group1.group_label = "new_group_label"
    beneficiary_group1.save()
    response = authenticated_client.get(list_url, HTTP_IF_NONE_MATCH=etag)
    assert response.status_code == status.HTTP_200_OK
    after_edit_etag = response.headers["ETAG"]
    assert etag_after_cache != after_edit_etag

    beneficiary_group3 = BeneficiaryGroupFactory(name="Other `BG")
    response = authenticated_client.get(list_url, HTTP_IF_NONE_MATCH=after_edit_etag)
    assert response.status_code == status.HTTP_200_OK
    after_create_etag = response.headers["ETAG"]
    assert after_edit_etag != after_create_etag

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
