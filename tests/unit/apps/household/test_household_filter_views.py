from typing import Any, Dict

from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.exceptions import SearchError
from hope.apps.household.const import HOST, REFUGEE, ROLE_PRIMARY
from hope.apps.household.filters import HouseholdFilter
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.models import Household, Program
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def household_filter_context(
    api_client: Any, create_user_role_with_permissions: Any, mock_elasticsearch: Any
) -> dict[str, Any]:
    afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)
    list_url = reverse(
        "api:households:households-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
        },
    )
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=afghanistan,
        program=program,
    )

    return {
        "afghanistan": afghanistan,
        "program": program,
        "list_url": list_url,
        "partner": partner,
        "user": user,
        "api_client": client,
    }


def test_filter_by_rdi_id(household_filter_context: dict[str, Any]) -> None:
    registration_data_import_household1 = RegistrationDataImportFactory(
        imported_by=household_filter_context["user"],
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
    )
    registration_data_import_household2 = RegistrationDataImportFactory(
        imported_by=household_filter_context["user"],
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
    )

    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        registration_data_import=registration_data_import_household1,
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        registration_data_import=registration_data_import_household2,
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"rdi_id": registration_data_import_household1.id},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


def test_filter_by_size(household_filter_context: dict[str, Any]) -> None:
    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        size=6,
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        size=4,
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"size_min": "5"},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


def test_filter_by_document_number(household_filter_context: dict[str, Any]) -> None:
    document_passport = DocumentTypeFactory(key="passport")
    document_id_card = DocumentTypeFactory(key="id_card")

    household_passport1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    passport1_hoh = household_passport1.head_of_household
    passport1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household_passport1, individual=passport1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household_passport1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household_passport1.registration_data_import,
    )

    household_passport2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    passport2_hoh = household_passport2.head_of_household
    passport2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household_passport2, individual=passport2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household_passport2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household_passport2.registration_data_import,
    )

    household_id_card = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    id_card_hoh = household_id_card.head_of_household
    id_card_hoh.save()
    IndividualRoleInHouseholdFactory(household=household_id_card, individual=id_card_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household_id_card,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household_id_card.registration_data_import,
    )

    DocumentFactory(
        individual=household_passport1.head_of_household,
        type=document_passport,
        document_number="123",
    )
    DocumentFactory(
        individual=household_passport2.head_of_household,
        type=document_passport,
        document_number="456",
    )
    DocumentFactory(
        individual=household_id_card.head_of_household,
        type=document_id_card,
        document_number="123",
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"document_number": "123", "document_type": "passport"},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household_passport1.id)


def test_filter_by_address(household_filter_context: dict[str, Any]) -> None:
    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        address="test address",
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        address="different address",
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"address": "test address"},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


def test_filter_by_head_of_household_full_name(household_filter_context: dict[str, Any]) -> None:
    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    household1_hoh = household1.head_of_household
    household1_hoh.full_name = "John Doe"
    household1_hoh.save(update_fields=["full_name"])
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    household2_hoh = household2.head_of_household
    household2_hoh.full_name = "Jane Doe"
    household2_hoh.save(update_fields=["full_name"])
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"head_of_household__full_name": "John"},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


def test_filter_by_head_of_household_phone_no_valid_true(household_filter_context: dict[str, Any]) -> None:
    invalid_phone_number = "12"
    valid_phone_number = "+48 609 456 789"

    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    household1_hoh = household1.head_of_household
    household1_hoh.phone_no = valid_phone_number
    household1_hoh.phone_no_alternative = valid_phone_number
    household1_hoh.phone_no_valid = True
    household1_hoh.phone_no_alternative_valid = True
    household1_hoh.save(
        update_fields=["phone_no", "phone_no_alternative", "phone_no_valid", "phone_no_alternative_valid"]
    )
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    household2_hoh = household2.head_of_household
    household2_hoh.phone_no = invalid_phone_number
    household2_hoh.phone_no_alternative = invalid_phone_number
    household2_hoh.phone_no_valid = False
    household2_hoh.phone_no_alternative_valid = False
    household2_hoh.save(
        update_fields=["phone_no", "phone_no_alternative", "phone_no_valid", "phone_no_alternative_valid"]
    )
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"head_of_household__phone_no_valid": True},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


def test_filter_by_head_of_household_phone_no_valid_false(household_filter_context: dict[str, Any]) -> None:
    invalid_phone_number = "12"
    valid_phone_number = "+48 609 456 789"

    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    household1_hoh = household1.head_of_household
    household1_hoh.phone_no = invalid_phone_number
    household1_hoh.phone_no_alternative = invalid_phone_number
    household1_hoh.phone_no_valid = False
    household1_hoh.phone_no_alternative_valid = False
    household1_hoh.save(
        update_fields=["phone_no", "phone_no_alternative", "phone_no_valid", "phone_no_alternative_valid"]
    )
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    household2_hoh = household2.head_of_household
    household2_hoh.phone_no = invalid_phone_number
    household2_hoh.phone_no_alternative = valid_phone_number
    household2_hoh.phone_no_valid = True
    household2_hoh.phone_no_alternative_valid = True
    household2_hoh.save(
        update_fields=["phone_no", "phone_no_alternative", "phone_no_valid", "phone_no_alternative_valid"]
    )
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"head_of_household__phone_no_valid": False},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


def test_filter_by_withdrawn(household_filter_context: dict[str, Any]) -> None:
    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        withdrawn=True,
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        withdrawn=False,
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"withdrawn": True},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


def test_filter_by_country_origin(household_filter_context: dict[str, Any]) -> None:
    afghanistan = CountryFactory()
    ukraine = CountryFactory(name="Ukraine", iso_code3="UKR", iso_code2="UK", iso_num="050")

    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        country_origin=afghanistan,
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        country_origin=ukraine,
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"country_origin": afghanistan.iso_code3},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


@pytest.mark.parametrize(
    ("program_status", "filter_value", "expected_results"),
    [
        (Program.ACTIVE, True, 2),
        (Program.FINISHED, True, 0),
        (Program.ACTIVE, False, 0),
        (Program.FINISHED, False, 2),
    ],
)
def test_filter_by_is_active_program(
    program_status: str, filter_value: bool, expected_results: int, household_filter_context: dict[str, Any]
) -> None:
    program = household_filter_context["program"]
    program.status = program_status
    program.save(update_fields=["status"])

    household1 = HouseholdFactory(
        program=program,
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=program,
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=program,
        business_area=household_filter_context["afghanistan"],
        create_role=False,
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=program,
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"], {"is_active_program": filter_value}
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == expected_results


def test_filter_by_rdi_merge_status(household_filter_context: dict[str, Any]) -> None:
    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        rdi_merge_status=MergeStatusModel.PENDING,
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"rdi_merge_status": MergeStatusModel.PENDING},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


@pytest.mark.parametrize(
    "filter_by_field",
    [
        "admin1",
        "admin2",
    ],
)
def test_filter_by_area(filter_by_field: str, household_filter_context: dict[str, Any]) -> None:
    country = CountryFactory()
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)

    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        **{filter_by_field: area1},
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        **{filter_by_field: area2},
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {filter_by_field: str(area1.id)},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


@pytest.mark.parametrize(
    "area",
    [
        "admin1",
        "admin2",
    ],
)
def test_filter_by_admin_area(area: str, household_filter_context: dict[str, Any]) -> None:
    country = CountryFactory()
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)

    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        **{area: area1},
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        **{area: area2},
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"admin_area": str(area1.id)},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


def test_filter_by_residence_status(household_filter_context: dict[str, Any]) -> None:
    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        residence_status=REFUGEE,
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        residence_status=HOST,
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"residence_status": REFUGEE},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


def test_filter_by_last_registration_date(household_filter_context: dict[str, Any]) -> None:
    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        last_registration_date=timezone.make_aware(timezone.datetime(2023, 1, 1)),
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        last_registration_date=timezone.make_aware(timezone.datetime(2021, 1, 1)),
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"last_registration_date_after": "2022-12-31"},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


def test_filter_by_first_registration_date(household_filter_context: dict[str, Any]) -> None:
    household1 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        first_registration_date=timezone.make_aware(timezone.datetime(2022, 12, 31)),
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_context["program"],
        business_area=household_filter_context["afghanistan"],
        create_role=False,
        first_registration_date=timezone.make_aware(timezone.datetime(2022, 12, 30)),
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_context["afghanistan"],
        program=household_filter_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    response = household_filter_context["api_client"].get(
        household_filter_context["list_url"],
        {"first_registration_date": "2022-12-31 00:00:00"},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(household1.id)


@pytest.fixture
def household_filter_search_context(
    api_client: Any, create_user_role_with_permissions: Any, django_elasticsearch_setup: Any
) -> dict[str, Any]:
    _ = django_elasticsearch_setup
    afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)
    list_url = reverse(
        "api:households:households-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
        },
    )
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    return {
        "afghanistan": afghanistan,
        "program": program,
        "list_url": list_url,
        "partner": partner,
        "user": user,
        "api_client": client,
    }


parametrize_search_context = (
    ("filters", "household1_data", "household2_data", "hoh_1_data", "hoh_2_data"),
    [
        (
            {"search": "HH-123"},
            {"unicef_id": "HH-123"},
            {"unicef_id": "HH-321"},
            {},
            {},
        ),
        (
            {"search": "John"},
            {},
            {},
            {"full_name": "John Doe"},
            {"full_name": "Jane Doe"},
        ),
        (
            {"search": "IND-123"},
            {},
            {},
            {"unicef_id": "IND-123"},
            {"unicef_id": "IND-321"},
        ),
        (
            {"search": "123456789"},
            {},
            {},
            {"phone_no": "123456789"},
            {"phone_no": "987654321"},
        ),
        (
            {"search": "123456789"},
            {},
            {},
            {"phone_no_alternative": "123 456 789"},
            {"phone_no_alternative": "987 654 321"},
        ),
        (
            {"search": "HOPE-123"},
            {"detail_id": "HOPE-123"},
            {"detail_id": "HOPE-321"},
            {},
            {},
        ),
        (
            {"search": "456"},
            {"program_registration_id": "456"},
            {"program_registration_id": "123"},
            {},
            {},
        ),
    ],
)


def _test_search(
    filters: Dict,
    household1_data: Dict,
    household2_data: Dict,
    hoh_1_data: Dict,
    hoh_2_data: Dict,
    household_filter_search_context: dict[str, Any],
) -> tuple[Any, list[Any]]:
    afghanistan = household_filter_search_context["afghanistan"]
    program2 = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)

    program1 = household_filter_search_context["program"]
    expected_results = []
    for program in (program1, program2):
        household1 = HouseholdFactory(
            program=program,
            business_area=household_filter_search_context["afghanistan"],
            create_role=False,
            **household1_data,
        )
        expected_results.append(household1)
        household1_hoh = household1.head_of_household
        for field, value in hoh_1_data.items():
            setattr(household1_hoh, field, value)
        household1_hoh.save()
        IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
        IndividualFactory(
            household=household1,
            business_area=household_filter_search_context["afghanistan"],
            program=program,
            registration_data_import=household1.registration_data_import,
        )

        household2 = HouseholdFactory(
            program=program,
            business_area=household_filter_search_context["afghanistan"],
            create_role=False,
            **household2_data,
        )
        household2_hoh = household2.head_of_household
        for field, value in hoh_2_data.items():
            setattr(household2_hoh, field, value)
        household2_hoh.save()
        IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
        IndividualFactory(
            household=household2,
            business_area=household_filter_search_context["afghanistan"],
            program=program,
            registration_data_import=household2.registration_data_import,
        )

    rebuild_search_index()
    response = household_filter_search_context["api_client"].get(household_filter_search_context["list_url"], filters)
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    return response_data, expected_results


@pytest.mark.parametrize(*parametrize_search_context)
def test_search(
    filters: Dict,
    household1_data: Dict,
    household2_data: Dict,
    hoh_1_data: Dict,
    hoh_2_data: Dict,
    household_filter_search_context: dict[str, Any],
) -> None:
    response_data, expected_results = _test_search(
        filters=filters,
        household1_data=household1_data,
        household2_data=household2_data,
        hoh_1_data=hoh_1_data,
        hoh_2_data=hoh_2_data,
        household_filter_search_context=household_filter_search_context,
    )
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(expected_results[0].id)


@pytest.mark.parametrize(*parametrize_search_context)
def test_search_db(
    filters: Dict,
    household1_data: Dict,
    household2_data: Dict,
    hoh_1_data: Dict,
    hoh_2_data: Dict,
    household_filter_search_context: dict[str, Any],
) -> None:
    program = household_filter_search_context["program"]
    program.status = Program.FINISHED
    program.save()

    response_data, expected_results = _test_search(
        filters=filters,
        household1_data=household1_data,
        household2_data=household2_data,
        hoh_1_data=hoh_1_data,
        hoh_2_data=hoh_2_data,
        household_filter_search_context=household_filter_search_context,
    )
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(expected_results[0].id)


@pytest.mark.parametrize(*parametrize_search_context)
def test_search_db_no_program_filter(
    filters: Dict,
    household1_data: Dict,
    household2_data: Dict,
    hoh_1_data: Dict,
    hoh_2_data: Dict,
    household_filter_search_context: dict[str, Any],
) -> None:
    household_filter_search_context["list_url"] = reverse(
        "api:households:households-global-list",
        kwargs={
            "business_area_slug": household_filter_search_context["afghanistan"].slug,
        },
    )
    response_data, expected_results = _test_search(
        filters=filters,
        household1_data=household1_data,
        household2_data=household2_data,
        hoh_1_data=hoh_1_data,
        hoh_2_data=hoh_2_data,
        household_filter_search_context=household_filter_search_context,
    )
    assert len(response_data) == 2
    result_ids = [result["id"] for result in response_data]
    assert str(expected_results[0].id) in result_ids
    assert str(expected_results[1].id) in result_ids


def test_filter_detail_id_requires_numeric(household_filter_search_context: dict[str, Any]) -> None:
    household_filter = HouseholdFilter(data={}, queryset=Household.objects.all(), request=None)

    with pytest.raises(SearchError):
        household_filter._filter_detail_id(Household.objects.all(), "abc123")


def test_filter_detail_id_filters_queryset(household_filter_search_context: dict[str, Any]) -> None:
    household1 = HouseholdFactory(
        program=household_filter_search_context["program"],
        business_area=household_filter_search_context["afghanistan"],
        create_role=False,
        detail_id="12345",
    )
    household1_hoh = household1.head_of_household
    household1_hoh.save()
    IndividualRoleInHouseholdFactory(household=household1, individual=household1_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household1,
        business_area=household_filter_search_context["afghanistan"],
        program=household_filter_search_context["program"],
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        program=household_filter_search_context["program"],
        business_area=household_filter_search_context["afghanistan"],
        create_role=False,
        detail_id="67890",
    )
    household2_hoh = household2.head_of_household
    household2_hoh.save()
    IndividualRoleInHouseholdFactory(household=household2, individual=household2_hoh, role=ROLE_PRIMARY)
    IndividualFactory(
        household=household2,
        business_area=household_filter_search_context["afghanistan"],
        program=household_filter_search_context["program"],
        registration_data_import=household2.registration_data_import,
    )

    household_filter = HouseholdFilter(data={}, queryset=Household.objects.all(), request=None)

    result_qs = household_filter._filter_detail_id(Household.objects.all(), "123")

    assert list(result_qs.values_list("id", flat=True)) == [household1.id]
