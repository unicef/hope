from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import BusinessAreaFactory, UserFactory
from hope.models import BusinessArea, DataCollectingType, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def ukraine(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Ukraine", slug="ukraine")


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory()


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def unlimited_dct(db: Any) -> DataCollectingType:
    """Active, not deprecated, not limited to any business area."""
    return DataCollectingType.objects.create(
        label="DCT 1",
        code="dct_1",
        description="Description for DCT 1",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=False,
    )


@pytest.fixture
def afghanistan_dct(afghanistan: BusinessArea) -> DataCollectingType:
    """Active, not deprecated, limited to Afghanistan."""
    dct = DataCollectingType.objects.create(
        label="DCT 2",
        code="dct_2",
        description="Description for DCT 2",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=False,
    )
    dct.limit_to.add(afghanistan)
    return dct


@pytest.fixture
def ukraine_dct(ukraine: BusinessArea) -> DataCollectingType:
    """Active, not deprecated, limited to Ukraine."""
    dct = DataCollectingType.objects.create(
        label="DCT 3",
        code="dct_3",
        description="Description for DCT 3",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=False,
    )
    dct.limit_to.add(ukraine)
    return dct


@pytest.fixture
def inactive_dct(db: Any) -> DataCollectingType:
    return DataCollectingType.objects.create(
        label="DCT 4 (Inactive)",
        code="dct_4",
        description="Description for DCT 4",
        type=DataCollectingType.Type.STANDARD,
        active=False,
        deprecated=False,
    )


@pytest.fixture
def deprecated_dct(db: Any) -> DataCollectingType:
    return DataCollectingType.objects.create(
        label="DCT 5 (Deprecated)",
        code="dct_5",
        description="Description for DCT 5",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=True,
    )


@pytest.fixture
def unknown_dct(db: Any) -> DataCollectingType:
    return DataCollectingType.objects.create(
        label="DCT 6 (Unknown Code)",
        code="unknown",
        description="Description for DCT 6",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=False,
    )


def _choices_url(business_area_slug: str) -> str:
    return reverse(
        "api:core:data-collecting-types-choices",
        kwargs={"business_area_slug": business_area_slug},
    )


def test_choices_returns_unlimited_and_business_area_types_only(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    unlimited_dct: DataCollectingType,
    afghanistan_dct: DataCollectingType,
    ukraine_dct: DataCollectingType,
    inactive_dct: DataCollectingType,
    deprecated_dct: DataCollectingType,
    unknown_dct: DataCollectingType,
) -> None:
    response = authenticated_client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "name": unlimited_dct.label,
            "value": unlimited_dct.code,
            "description": unlimited_dct.description,
            "type": unlimited_dct.type,
        },
        {
            "name": afghanistan_dct.label,
            "value": afghanistan_dct.code,
            "description": afghanistan_dct.description,
            "type": afghanistan_dct.type,
        },
    ]


def test_choices_returns_a_different_list_per_business_area(
    authenticated_client: Any,
    ukraine: BusinessArea,
    unlimited_dct: DataCollectingType,
    afghanistan_dct: DataCollectingType,
    ukraine_dct: DataCollectingType,
) -> None:
    response = authenticated_client.get(_choices_url(ukraine.slug))

    assert response.status_code == status.HTTP_200_OK
    assert [row["value"] for row in response.json()] == [unlimited_dct.code, ukraine_dct.code]


def test_choices_allows_authenticated_user_without_any_role(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    unlimited_dct: DataCollectingType,
) -> None:
    response = authenticated_client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert [row["value"] for row in response.json()] == [unlimited_dct.code]


def test_choices_denies_anonymous_access(afghanistan: BusinessArea, unlimited_dct: DataCollectingType) -> None:
    response = APIClient().get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_403_FORBIDDEN
