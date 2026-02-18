from typing import Any

from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.models import Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def household_members_context(api_client: Any) -> dict[str, Any]:
    members_url_name = "api:households:households-members"

    afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    household1 = HouseholdFactory(
        program=program,
        business_area=afghanistan,
        create_role=False,
        start=timezone.now(),
    )
    individuals1 = [household1.head_of_household]
    individuals1.append(
        IndividualFactory(
            household=household1,
            business_area=afghanistan,
            program=program,
            registration_data_import=household1.registration_data_import,
        )
    )

    household2 = HouseholdFactory(
        program=program,
        business_area=afghanistan,
        create_role=False,
        start=timezone.now(),
    )
    individuals2 = [household2.head_of_household]
    individuals2.append(
        IndividualFactory(
            household=household2,
            business_area=afghanistan,
            program=program,
            registration_data_import=household2.registration_data_import,
        )
    )

    IndividualRoleInHouseholdFactory(
        household=household1,
        individual=individuals1[0],
        role=ROLE_PRIMARY,
    )
    IndividualRoleInHouseholdFactory(
        household=household1,
        individual=individuals2[0],
        role=ROLE_ALTERNATE,
    )
    IndividualRoleInHouseholdFactory(
        household=household2,
        individual=individuals2[1],
        role=ROLE_PRIMARY,
    )
    IndividualRoleInHouseholdFactory(
        household=household2,
        individual=individuals1[0],
        role=ROLE_ALTERNATE,
    )

    return {
        "members_url_name": members_url_name,
        "afghanistan": afghanistan,
        "program": program,
        "partner": partner,
        "user": user,
        "api_client": client,
        "household1": household1,
        "household2": household2,
        "individuals1": individuals1,
        "individuals2": individuals2,
    }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS], status.HTTP_200_OK),
        ([Permissions.RDI_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_household_members_permissions(
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
    household_members_context: dict[str, Any],
) -> None:
    create_user_role_with_permissions(
        user=household_members_context["user"],
        permissions=permissions,
        business_area=household_members_context["afghanistan"],
        program=household_members_context["program"],
    )
    response = household_members_context["api_client"].get(
        reverse(
            household_members_context["members_url_name"],
            kwargs={
                "business_area_slug": household_members_context["afghanistan"].slug,
                "program_slug": household_members_context["program"].slug,
                "pk": str(household_members_context["household1"].id),
            },
        )
    )
    assert response.status_code == expected_status


def test_household_members(create_user_role_with_permissions: Any, household_members_context: dict[str, Any]) -> None:
    create_user_role_with_permissions(
        user=household_members_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=household_members_context["afghanistan"],
        program=household_members_context["program"],
    )
    response = household_members_context["api_client"].get(
        reverse(
            household_members_context["members_url_name"],
            kwargs={
                "business_area_slug": household_members_context["afghanistan"].slug,
                "program_slug": household_members_context["program"].slug,
                "pk": str(household_members_context["household1"].id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    response_results = response.json()["results"]
    assert len(response_results) == 3

    household1 = household_members_context["household1"]
    household2 = household_members_context["household2"]
    individual1_1, individual1_2 = household_members_context["individuals1"]
    individual2_1, individual2_2 = household_members_context["individuals2"]

    response_ids = [result["id"] for result in response_results]
    assert str(individual1_1.id) in response_ids
    assert str(individual1_2.id) in response_ids
    assert str(individual2_1.id) in response_ids
    assert str(individual2_2.id) not in response_ids
    assert response_results == [
        {
            "id": str(individual1_1.id),
            "unicef_id": individual1_1.unicef_id,
            "full_name": individual1_1.full_name,
            "role": "PRIMARY",
            "relationship": individual1_1.relationship,
            "status": individual1_1.status,
            "birth_date": f"{individual1_1.birth_date:%Y-%m-%d}",
            "sex": individual1_1.sex,
            "household": {
                "id": str(household1.id),
                "unicef_id": household1.unicef_id,
                "admin1": None,
                "admin2": None,
                "admin3": None,
                "admin4": None,
                "first_registration_date": f"{household1.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "last_registration_date": f"{household1.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "total_cash_received": None,
                "total_cash_received_usd": None,
                "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                "start": household1.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "zip_code": None,
                "residence_status": household1.get_residence_status_display(),
                "country_origin": "",
                "country": "",
                "address": household1.address,
                "village": household1.village,
                "geopoint": None,
                "import_id": household1.unicef_id,
                "program_slug": household_members_context["program"].slug,
            },
        },
        {
            "id": str(individual1_2.id),
            "unicef_id": individual1_2.unicef_id,
            "full_name": individual1_2.full_name,
            "role": None,
            "relationship": individual1_2.relationship,
            "status": individual1_2.status,
            "birth_date": f"{individual1_2.birth_date:%Y-%m-%d}",
            "sex": individual1_2.sex,
            "household": {
                "id": str(household1.id),
                "unicef_id": household1.unicef_id,
                "admin1": None,
                "admin2": None,
                "admin3": None,
                "admin4": None,
                "first_registration_date": f"{household1.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "last_registration_date": f"{household1.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "total_cash_received": None,
                "total_cash_received_usd": None,
                "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                "start": household1.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "zip_code": None,
                "residence_status": household1.get_residence_status_display(),
                "country_origin": "",
                "country": "",
                "address": household1.address,
                "village": household1.village,
                "geopoint": None,
                "import_id": household1.unicef_id,
                "program_slug": household_members_context["program"].slug,
            },
        },
        {
            "id": str(individual2_1.id),
            "unicef_id": individual2_1.unicef_id,
            "full_name": individual2_1.full_name,
            "role": "ALTERNATE",
            "relationship": individual2_1.relationship,
            "status": individual2_1.status,
            "birth_date": f"{individual2_1.birth_date:%Y-%m-%d}",
            "sex": individual2_1.sex,
            "household": {
                "id": str(household2.id),
                "unicef_id": household2.unicef_id,
                "admin1": None,
                "admin2": None,
                "admin3": None,
                "admin4": None,
                "first_registration_date": f"{household2.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "last_registration_date": f"{household2.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "total_cash_received": None,
                "total_cash_received_usd": None,
                "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                "start": household2.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "zip_code": None,
                "residence_status": household2.get_residence_status_display(),
                "country_origin": "",
                "country": "",
                "address": household2.address,
                "village": household2.village,
                "geopoint": None,
                "import_id": household2.unicef_id,
                "program_slug": household_members_context["program"].slug,
            },
        },
    ]
