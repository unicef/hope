"""Tests for user choices API views."""

from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import to_choice_object
from hope.models import USER_STATUS_CHOICES, Partner, Role, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any):
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        slug="afghanistan",
        active=True,
    )


@pytest.fixture
def partner(db: Any):
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner):
    return UserFactory(partner=partner)


@pytest.fixture
def roles_setup(db: Any):
    RoleFactory(name="TestRole")
    RoleFactory(name="TestRole2")
    RoleFactory(name="TestRole3")


@pytest.fixture
def unicef_partners(db: Any):
    unicef_hq = PartnerFactory(name="UNICEF HQ")
    unicef_partner_for_afghanistan = PartnerFactory(name="UNICEF Partner for afghanistan")
    return {
        "unicef_hq": unicef_hq,
        "unicef_partner_for_afghanistan": unicef_partner_for_afghanistan,
    }


@pytest.fixture
def choices_url(afghanistan):
    return reverse("api:accounts:users-choices", kwargs={"business_area_slug": afghanistan.slug})


@pytest.fixture
def authenticated_client(api_client: Any, user: User):
    return api_client(user)


def test_get_choices(
    authenticated_client: Any,
    user: User,
    partner: Partner,
    afghanistan,
    choices_url: str,
    roles_setup: None,
    unicef_partners: dict,
    create_user_role_with_permissions: Any,
):
    partner.allowed_business_areas.add(afghanistan)

    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
        business_area=afghanistan,
    )

    unicef_hq = unicef_partners["unicef_hq"]
    unicef_partner_in_afghanistan = unicef_partners["unicef_partner_for_afghanistan"]

    response = authenticated_client.get(choices_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "role_choices": [
            {"name": role.name, "value": role.id, "subsystem": role.subsystem} for role in Role.objects.order_by("name")
        ],
        "status_choices": to_choice_object(USER_STATUS_CHOICES),
        "partner_choices": [
            {"name": partner.name, "value": partner.id}
            for partner in [
                partner,
                unicef_hq,
                unicef_partner_in_afghanistan,
            ]
        ],
        # TODO: below assert can be removed after temporary solution is removed for partners
        "partner_choices_temp": [
            {"name": partner.name, "value": partner.id} for partner in [unicef_hq, unicef_partner_in_afghanistan]
        ],
    }
