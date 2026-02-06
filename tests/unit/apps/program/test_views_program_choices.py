"""Tests for program choices API endpoints."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import to_choice_object
from hope.models import BusinessArea, DataCollectingType, Partner, PeriodicFieldData, Program, ProgramCycle, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def ukraine(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Ukraine", slug="ukraine")


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def dct_1(db: Any) -> DataCollectingType:
    """DCT1: Active, not deprecated, not limited to any business area"""
    return DataCollectingType.objects.create(
        label="DCT 1",
        code="dct_1",
        description="Description for DCT 1",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=False,
    )


@pytest.fixture
def dct_2(afghanistan: Any) -> DataCollectingType:
    """DCT2: Active, not deprecated, limited to afghanistan"""
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
def dct_3(ukraine: Any) -> DataCollectingType:
    """DCT3: Active, not deprecated, limited to ukraine"""
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
def dct_4(db: Any) -> DataCollectingType:
    """DCT4: Inactive"""
    return DataCollectingType.objects.create(
        label="DCT 4 (Inactive)",
        code="dct_4",
        description="Description for DCT 4",
        type=DataCollectingType.Type.STANDARD,
        active=False,
        deprecated=False,
    )


@pytest.fixture
def dct_5(db: Any) -> DataCollectingType:
    """DCT5: Deprecated"""
    return DataCollectingType.objects.create(
        label="DCT 5 (Deprecated)",
        code="dct_5",
        description="Description for DCT 5",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=True,
    )


@pytest.fixture
def dct_6(db: Any) -> DataCollectingType:
    """DCT6: code 'unknown'"""
    return DataCollectingType.objects.create(
        label="DCT 6 (Unknown Code)",
        code="unknown",
        description="Description for DCT 6",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=False,
    )


@pytest.fixture
def choices_url() -> str:
    return "api:programs:programs-choices"


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_get_choices(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    choices_url: str,
    dct_1: DataCollectingType,
    dct_2: DataCollectingType,
    dct_3: DataCollectingType,
    dct_4: DataCollectingType,
    dct_5: DataCollectingType,
    dct_6: DataCollectingType,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(reverse(choices_url, kwargs={"business_area_slug": afghanistan.slug}))
    assert response.status_code == status.HTTP_200_OK

    assert response.data == {
        "status_choices": to_choice_object(Program.STATUS_CHOICE),
        "frequency_of_payments_choices": to_choice_object(Program.FREQUENCY_OF_PAYMENTS_CHOICE),
        "sector_choices": to_choice_object(Program.SECTOR_CHOICE),
        "scope_choices": to_choice_object(Program.SCOPE_CHOICE),
        "data_collecting_type_choices": [
            {
                "value": dct_1.code,
                "name": dct_1.label,
                "description": dct_1.description,
                "type": dct_1.type,
            },
            {
                "value": dct_2.code,
                "name": dct_2.label,
                "description": dct_2.description,
                "type": dct_2.type,
            },
        ],
        "partner_access_choices": to_choice_object(Program.PARTNER_ACCESS_CHOICE),
        "pdu_subtype_choices": to_choice_object(PeriodicFieldData.TYPE_CHOICES),
        "program_cycle_status_choices": to_choice_object(ProgramCycle.STATUS_CHOICE),
    }
