"""Tests for program choices API endpoints."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import to_choice_object
from hope.models import Partner, PeriodicFieldData, Program, ProgramCycle, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_get_choices_returns_every_program_choice_list(authenticated_client: Any) -> None:
    response = authenticated_client.get(reverse("api:choices-programs"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "status_choices": to_choice_object(Program.STATUS_CHOICE),
        "frequency_of_payments_choices": to_choice_object(Program.FREQUENCY_OF_PAYMENTS_CHOICE),
        "sector_choices": to_choice_object(Program.SECTOR_CHOICE),
        "scope_choices": to_choice_object(Program.SCOPE_CHOICE),
        "partner_access_choices": to_choice_object(Program.PARTNER_ACCESS_CHOICE),
        "pdu_subtype_choices": to_choice_object(PeriodicFieldData.TYPE_CHOICES),
        "program_cycle_status_choices": to_choice_object(ProgramCycle.STATUS_CHOICE),
    }


def test_get_choices_allows_authenticated_user_without_any_role(authenticated_client: Any) -> None:
    response = authenticated_client.get(reverse("api:choices-programs"))

    assert response.status_code == status.HTTP_200_OK
    assert "data_collecting_type_choices" not in response.data


def test_get_choices_denies_anonymous_access() -> None:
    response = APIClient().get(reverse("api:choices-programs"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_program_viewset_choices_returns_choices_for_user_with_role(
    authenticated_client: Any,
    create_user_role_with_permissions: Any,
    user: User,
) -> None:
    afghanistan = BusinessAreaFactory(slug="afghanistan")
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
    )
    response = authenticated_client.get(
        reverse("api:programs:programs-choices", kwargs={"business_area_slug": afghanistan.slug})
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "status_choices": to_choice_object(Program.STATUS_CHOICE),
        "frequency_of_payments_choices": to_choice_object(Program.FREQUENCY_OF_PAYMENTS_CHOICE),
        "sector_choices": to_choice_object(Program.SECTOR_CHOICE),
        "scope_choices": to_choice_object(Program.SCOPE_CHOICE),
        "partner_access_choices": to_choice_object(Program.PARTNER_ACCESS_CHOICE),
        "pdu_subtype_choices": to_choice_object(PeriodicFieldData.TYPE_CHOICES),
        "program_cycle_status_choices": to_choice_object(ProgramCycle.STATUS_CHOICE),
    }
