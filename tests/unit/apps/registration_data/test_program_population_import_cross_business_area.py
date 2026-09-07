from typing import Any
from unittest.mock import Mock, patch

from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Household, Program, RegistrationDataImport, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def attacker_business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def victim_business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="ukraine")


@pytest.fixture
def victim_program(victim_business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=victim_business_area, status=Program.ACTIVE)


@pytest.fixture
def attacker_program(attacker_business_area: BusinessArea, victim_program: Program) -> Program:
    return ProgramFactory(
        business_area=attacker_business_area,
        status=Program.ACTIVE,
        beneficiary_group=victim_program.beneficiary_group,
        data_collecting_type=victim_program.data_collecting_type,
    )


@pytest.fixture
def victim_household(victim_program: Program) -> Household:
    head_of_household = IndividualFactory(
        household=None,
        program=victim_program,
        business_area=victim_program.business_area,
    )
    household = HouseholdFactory(
        program=victim_program,
        business_area=victim_program.business_area,
        head_of_household=head_of_household,
    )
    head_of_household.household = household
    head_of_household.save()
    return household


@pytest.fixture
def attacker(
    attacker_business_area: BusinessArea,
    attacker_program: Program,
    create_user_role_with_permissions: Any,
) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.RDI_IMPORT_DATA],
        attacker_business_area,
        program=attacker_program,
    )
    return user


@pytest.fixture
def api_client(attacker: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=attacker)
    return client


@patch("hope.apps.registration_data.api.views.registration_program_population_import_async_task", new=Mock())
def test_import_population_from_program_in_other_business_area_is_denied(
    api_client: APIClient,
    attacker_business_area: BusinessArea,
    attacker_program: Program,
    victim_program: Program,
    victim_household: Household,
) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-list",
        kwargs={"business_area_slug": attacker_business_area.slug, "program_code": attacker_program.code},
    )

    response = api_client.post(
        url,
        {
            "import_from_program_id": str(victim_program.id),
            "import_from_ids": victim_household.unicef_id,
            "name": "cross business area import",
            "screen_beneficiary": False,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.status_code
    assert not RegistrationDataImport.objects.filter(name="cross business area import").exists()
