from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import BusinessAreaFactory, PartnerFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(code="0060", name="Afghanistan", slug="afghanistan", active=True)


@pytest.fixture
def ukraine(db: Any) -> BusinessArea:
    return BusinessAreaFactory(code="4410", name="Ukraine", slug="ukraine", active=True)


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def unicef_partners(db: Any) -> list[Partner]:
    return [
        PartnerFactory(name="UNICEF HQ"),
        PartnerFactory(name="UNICEF Partner for afghanistan"),
    ]


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Any, user: User) -> Any:
    return api_client(user)


def _choices_url(business_area_slug: str) -> str:
    return reverse("api:accounts:partners-choices", kwargs={"business_area_slug": business_area_slug})


def test_get_choices_returns_the_partners_of_the_business_area(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    partner: Partner,
    unicef_partners: list[Partner],
    create_user_role_with_permissions: Any,
) -> None:
    partner.allowed_business_areas.add(afghanistan)
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "partner_choices": [{"name": choice.name, "value": choice.id} for choice in [partner, *unicef_partners]],
        # TODO: below assert can be removed after temporary solution is removed for partners
        "partner_choices_temp": [{"name": choice.name, "value": choice.id} for choice in unicef_partners],
    }


def test_get_choices_returns_a_different_list_per_business_area(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ukraine: BusinessArea,
    partner: Partner,
    create_user_role_with_permissions: Any,
) -> None:
    partner.allowed_business_areas.add(afghanistan)
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=ukraine,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_choices_url(ukraine.slug))

    assert response.status_code == status.HTTP_200_OK
    assert partner.id not in [choice["value"] for choice in response.data["partner_choices"]]


def test_get_choices_allows_a_user_holding_a_grievance_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    partner: Partner,
    create_user_role_with_permissions: Any,
) -> None:
    partner.allowed_business_areas.add(afghanistan)
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.GRIEVANCES_CREATE],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert partner.id in [choice["value"] for choice in response.data["partner_choices"]]


def test_get_choices_denies_a_user_without_the_permission_in_the_business_area(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ukraine: BusinessArea,
    partner: Partner,
    create_user_role_with_permissions: Any,
) -> None:
    partner.allowed_business_areas.add(afghanistan)
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=ukraine,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_choices_denies_a_user_without_any_role(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    partner: Partner,
) -> None:
    partner.allowed_business_areas.add(afghanistan)

    response = authenticated_client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_choices_denies_anonymous_access(afghanistan: BusinessArea) -> None:
    response = APIClient().get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_403_FORBIDDEN
