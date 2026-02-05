"""Tests for program copy API endpoint."""

import datetime
from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.old_factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    UserFactory,
)
from extras.test_utils.old_factories.core import (
    DataCollectingTypeFactory,
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
    create_ukraine,
)
from extras.test_utils.old_factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.old_factories.program import BeneficiaryGroupFactory, ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.models import (
    AdminAreaLimitedTo,
    Area,
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    FlexibleAttribute,
    Partner,
    PeriodicFieldData,
    Program,
    User,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return create_afghanistan()


@pytest.fixture
def ukraine(db: Any) -> BusinessArea:
    return create_ukraine()


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="Test Partner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def dct_original(db: Any) -> DataCollectingType:
    return DataCollectingTypeFactory(
        label="Original DCT",
        code="origdct",
        type=DataCollectingType.Type.STANDARD,
        active=True,
    )


@pytest.fixture
def dct_compatible(dct_original: Any) -> DataCollectingType:
    dct = DataCollectingTypeFactory(
        label="Compatible DCT",
        code="compdct",
        type=DataCollectingType.Type.STANDARD,
        active=True,
    )
    dct_original.compatible_types.add(dct)
    return dct


@pytest.fixture
def dct_incompatible(db: Any) -> DataCollectingType:
    return DataCollectingTypeFactory(
        label="Incompatible DCT",
        code="incompdct",
        type=DataCollectingType.Type.SOCIAL,
        active=True,
    )


@pytest.fixture
def bg_original(db: Any) -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="Original BG", master_detail=True)


@pytest.fixture
def program_to_copy(
    afghanistan: BusinessArea, dct_original: DataCollectingType, bg_original: BeneficiaryGroup
) -> Program:
    program = ProgramFactory(
        business_area=afghanistan,
        name="Test Program To Copy",
        description="Test Program To Copy Description",
        status=Program.ACTIVE,
        programme_code="ORIG",
        data_collecting_type=dct_original,
        beneficiary_group=bg_original,
        sector=Program.EDUCATION,
        start_date=datetime.date(2023, 1, 1),
        end_date=datetime.date(2023, 12, 31),
        partner_access=Program.NONE_PARTNERS_ACCESS,
        budget=100,
        population_goal=10,
        cash_plus=False,
        frequency_of_payments=Program.REGULAR,
        administrative_areas_of_implementation="Original areas impl.",
    )

    # Add PDU field
    pdu_data = PeriodicFieldDataFactory(subtype=PeriodicFieldData.STRING, number_of_rounds=1, rounds_names=["R1"])
    FlexibleAttributeForPDUFactory(program=program, label="Original PDU1", pdu_data=pdu_data)

    # Add household and individuals
    household = HouseholdFactory(program=program, business_area=afghanistan)
    IndividualFactory(household=household, program=program, business_area=afghanistan)

    return program


@pytest.fixture
def partner1_for_assign(afghanistan: Any) -> Partner:
    partner = PartnerFactory(name="Partner 1")
    partner.allowed_business_areas.set([afghanistan])
    return partner


@pytest.fixture
def partner2_for_assign(afghanistan: Any) -> Partner:
    partner = PartnerFactory(name="Partner 2")
    partner.allowed_business_areas.set([afghanistan])
    return partner


@pytest.fixture
def setup_partners_with_role_assignments(
    partner: Partner,
    partner1_for_assign: Partner,
    partner2_for_assign: Partner,
    afghanistan: BusinessArea,
) -> None:
    partner.allowed_business_areas.set([afghanistan])

    # TODO: Temporary solution - remove the below lines after proper solution is applied
    RoleAssignmentFactory(partner=partner, business_area=afghanistan, program=None)
    RoleAssignmentFactory(partner=partner1_for_assign, business_area=afghanistan, program=None)
    RoleAssignmentFactory(partner=partner2_for_assign, business_area=afghanistan, program=None)


@pytest.fixture
def area1(afghanistan: Any) -> Any:
    country = CountryFactory()
    country.business_areas.set([afghanistan])
    admin_type = AreaTypeFactory(country=country, area_level=1)
    return AreaFactory(parent=None, area_type=admin_type, p_code="AFCPY1", name="AreaCopy1")


@pytest.fixture
def area2(afghanistan: BusinessArea, area1: Any) -> Any:
    return AreaFactory(parent=None, area_type=area1.area_type, p_code="AFCPY2", name="AreaCopy2")


@pytest.fixture
def copy_url(afghanistan: BusinessArea, program_to_copy: Program) -> str:
    return reverse(
        "api:programs:programs-copy",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "slug": program_to_copy.slug,
        },
    )


@pytest.fixture
def base_copy_payload(dct_compatible: Any, area1: Any) -> dict:
    return {
        "name": "Copied Program Name",
        "programme_code": "COPY",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "sector": Program.HEALTH,
        "description": "Description for copied program.",
        "budget": 50000,
        "administrative_areas_of_implementation": "New areas impl.",
        "population_goal": 50,
        "cash_plus": True,
        "frequency_of_payments": Program.ONE_OFF,
        "data_collecting_type": dct_compatible.code,
        "partner_access": Program.NONE_PARTNERS_ACCESS,
        "partners": [],
        "pdu_fields": [
            {
                "label": "New PDU For Copy",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 1,
                    "rounds_names": ["R1C"],
                },
            }
        ],
    }


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_copy_program_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PROGRAMME_DUPLICATE], afghanistan, whole_business_area_access=True
    )
    response = authenticated_client.post(copy_url, base_copy_payload)
    assert response.status_code == status.HTTP_201_CREATED
    new_program = Program.objects.get(name="Copied Program Name", business_area=afghanistan)
    assert response.json() == {"message": f"Program copied successfully. New Program slug: {new_program.slug}"}


def test_copy_program_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [], afghanistan, whole_business_area_access=True)
    response = authenticated_client.post(copy_url, base_copy_payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_copy_program(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    program_to_copy: Program,
    dct_original: DataCollectingType,
    dct_compatible: DataCollectingType,
    bg_original: BeneficiaryGroup,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.post(copy_url, base_copy_payload)
    assert response.status_code == status.HTTP_201_CREATED

    new_program_slug = response.json()["message"].split(": ")[-1]
    new_program = Program.objects.get(slug=new_program_slug, business_area=afghanistan)

    # Check copied fields
    assert new_program.name == "Copied Program Name"
    assert new_program.programme_code == "COPY"
    assert new_program.slug == "copy"
    assert new_program.start_date == datetime.date(2024, 1, 1)
    assert new_program.end_date == datetime.date(2024, 12, 31)
    assert new_program.sector == Program.HEALTH
    assert new_program.description == "Description for copied program."
    assert new_program.budget == 50000
    assert new_program.administrative_areas_of_implementation == "New areas impl."
    assert new_program.population_goal == 50
    assert new_program.cash_plus is True
    assert new_program.frequency_of_payments == Program.ONE_OFF
    assert new_program.data_collecting_type.code == dct_compatible.code
    assert str(new_program.beneficiary_group.id) == str(bg_original.id)
    assert new_program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert new_program.status == Program.DRAFT  # New program should be in DRAFT status

    # Check PDU fields
    pdu_fields = FlexibleAttribute.objects.filter(program=new_program)
    assert pdu_fields.count() == 1
    pdu_field = pdu_fields.first()
    assert pdu_field.label["English(EN)"] == "New PDU For Copy"
    assert pdu_field.pdu_data.subtype == PeriodicFieldData.BOOL
    assert pdu_field.pdu_data.number_of_rounds == 1
    assert pdu_field.pdu_data.rounds_names == ["R1C"]

    # Check that the original program's data is not modified
    original_program = Program.objects.get(id=program_to_copy.id)
    assert original_program.name == "Test Program To Copy"
    assert original_program.programme_code == "ORIG"
    assert original_program.slug == "orig"
    assert original_program.start_date == datetime.date(2023, 1, 1)
    assert original_program.end_date == datetime.date(2023, 12, 31)
    assert original_program.description == "Test Program To Copy Description"
    assert original_program.budget == 100
    assert original_program.population_goal == 10
    assert original_program.administrative_areas_of_implementation == "Original areas impl."
    assert original_program.cash_plus is False
    assert original_program.frequency_of_payments == Program.REGULAR
    assert original_program.sector == Program.EDUCATION
    assert original_program.data_collecting_type.code == dct_original.code
    assert str(original_program.beneficiary_group.id) == str(bg_original.id)
    assert original_program.partner_access == Program.NONE_PARTNERS_ACCESS
    assert original_program.status == Program.ACTIVE
    pdu_fields_original = FlexibleAttribute.objects.filter(program=program_to_copy)
    assert pdu_fields_original.count() == 1
    pdu_field_original = pdu_fields_original.first()
    assert pdu_field_original.label["English(EN)"] == "Original PDU1"
    assert pdu_field_original.pdu_data.subtype == PeriodicFieldData.STRING
    assert pdu_field_original.pdu_data.number_of_rounds == 1
    assert pdu_field_original.pdu_data.rounds_names == ["R1"]


def test_copy_program_new_programme_code_generation(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    program_to_copy: Program,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_copy_payload,
        "programme_code": None,
    }
    response = authenticated_client.post(copy_url, payload)
    assert response.status_code == status.HTTP_201_CREATED

    new_program_slug = response.json()["message"].split(": ")[-1]
    new_program = Program.objects.get(slug=new_program_slug, business_area=afghanistan)
    assert new_program.programme_code != program_to_copy.programme_code
    assert new_program.slug != program_to_copy.slug


def test_copy_program_existing_programme_code(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    program_to_copy: Program,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_copy_payload,
        "programme_code": program_to_copy.programme_code,
    }
    response = authenticated_client.post(copy_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "programme_code" in response.json()
    assert response.json()["programme_code"][0] == "Programme code is already used."


def test_copy_program_invalid_programme_code(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_copy_payload,
        "programme_code": "T#ST",
    }
    response = authenticated_client.post(copy_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "programme_code" in response.json()
    assert (
        "Programme code should be exactly 4 characters long and may only contain letters, digits and character: -"
        in response.json()["programme_code"][0]
    )


def test_copy_program_with_invalid_dates(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_copy_payload,
        "start_date": "2024-12-31",
        "end_date": "2024-01-01",
    }
    response = authenticated_client.post(copy_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "end_date" in response.json()
    assert "End date cannot be earlier than the start date." in response.json()["end_date"][0]


def test_copy_program_incompatible_dct(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    dct_incompatible: DataCollectingType,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_copy_payload,
        "data_collecting_type": dct_incompatible.code,
    }

    response = authenticated_client.post(copy_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response.json()
    assert (
        "Data Collecting Type must be compatible with the original Program."
        in response.json()["data_collecting_type"][0]
    )


def test_copy_program_dct_invalid(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ukraine: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    dct_compatible: DataCollectingType,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )
    payload = {
        **base_copy_payload,
        "data_collecting_type": dct_compatible.code,
    }

    # DCT inactive
    dct_compatible.active = False
    dct_compatible.save()
    response_for_inactive = authenticated_client.post(copy_url, payload)
    assert response_for_inactive.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response_for_inactive.json()
    assert (
        response_for_inactive.json()["data_collecting_type"][0]
        == "Only active Data Collecting Type can be used in Program."
    )

    # DCT deprecated
    dct_compatible.active = True
    dct_compatible.deprecated = True
    dct_compatible.save()
    response_for_deprecated = authenticated_client.post(copy_url, payload)
    assert response_for_deprecated.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response_for_deprecated.json()
    assert (
        response_for_deprecated.json()["data_collecting_type"][0]
        == "Deprecated Data Collecting Type cannot be used in Program."
    )

    # DCT limited to another BA
    dct_compatible.deprecated = False
    dct_compatible.save()
    dct_compatible.limit_to.add(ukraine)
    response_for_limited = authenticated_client.post(copy_url, payload)
    assert response_for_limited.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response_for_limited.json()
    assert (
        response_for_limited.json()["data_collecting_type"][0]
        == "This Data Collecting Type is not available for this Business Area."
    )


def test_copy_program_all_partners_access(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    partner: Partner,
    partner1_for_assign: Partner,
    partner2_for_assign: Partner,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_copy_payload,
        "partner_access": Program.ALL_PARTNERS_ACCESS,
    }

    response = authenticated_client.post(copy_url, payload)
    assert response.status_code == status.HTTP_201_CREATED

    new_program_slug = response.json()["message"].split(": ")[-1]
    new_program = Program.objects.get(slug=new_program_slug, business_area=afghanistan)
    assert new_program.partner_access == Program.ALL_PARTNERS_ACCESS
    assert new_program.role_assignments.count() == 3
    assert set(new_program.role_assignments.values_list("partner", flat=True)) == {
        partner.id,
        partner1_for_assign.id,
        partner2_for_assign.id,
    }


def test_copy_program_all_partners_access_with_partners_data(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    partner: Partner,
    partner2_for_assign: Partner,
    area1: Area,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_copy_payload,
        "partner_access": Program.ALL_PARTNERS_ACCESS,
        "partners": [
            {"partner": str(partner.id), "areas": [str(area1.id)]},
            {"partner": str(partner2_for_assign.id), "areas": []},
        ],
    }

    response = authenticated_client.post(copy_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "partners" in response.json()
    assert "You cannot specify partners for the chosen access type." in response.json()["partners"][0]


def test_copy_program_none_partners_access_with_partners_data(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    partner: Partner,
    partner2_for_assign: Partner,
    area1: Area,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_copy_payload,
        "partner_access": Program.NONE_PARTNERS_ACCESS,
        "partners": [
            {"partner": str(partner.id), "areas": [str(area1.id)]},
            {"partner": str(partner2_for_assign.id), "areas": []},
        ],
    }

    response = authenticated_client.post(copy_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "partners" in response.json()
    assert "You cannot specify partners for the chosen access type." in response.json()["partners"][0]


def test_copy_program_selected_access(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    partner: Partner,
    partner2_for_assign: Partner,
    area1: Area,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_copy_payload,
        "partner_access": Program.SELECTED_PARTNERS_ACCESS,
        "partners": [
            {"partner": str(partner.id), "areas": [str(area1.id)]},
            {"partner": str(partner2_for_assign.id), "areas": []},
        ],
    }
    response = authenticated_client.post(copy_url, payload)
    assert response.status_code == status.HTTP_201_CREATED

    new_program_slug = response.json()["message"].split(": ")[-1]
    new_program = Program.objects.get(slug=new_program_slug, business_area=afghanistan)
    assert new_program.partner_access == Program.SELECTED_PARTNERS_ACCESS
    assert new_program.role_assignments.count() == 2
    assert set(new_program.role_assignments.values_list("partner", flat=True)) == {
        partner.id,
        partner2_for_assign.id,
    }
    assert AdminAreaLimitedTo.objects.filter(program=new_program).count() == 1
    assert (
        AdminAreaLimitedTo.objects.filter(
            program=new_program,
            partner=partner,
        ).count()
        == 1
    )
    assert (
        AdminAreaLimitedTo.objects.filter(
            program=new_program,
            partner=partner2_for_assign,
        ).count()
        == 0
    )


def test_copy_program_selected_access_without_partner(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    copy_url: str,
    base_copy_payload: dict,
    partner1_for_assign: Partner,
    partner2_for_assign: Partner,
    area1: Area,
    setup_partners_with_role_assignments: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_DUPLICATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_copy_payload,
        "partner_access": Program.SELECTED_PARTNERS_ACCESS,
        "partners": [
            {
                "partner": str(partner1_for_assign.id),
                "areas": [str(area1.id)],
            },
            {"partner": str(partner2_for_assign.id), "areas": []},
        ],
    }
    response = authenticated_client.post(copy_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "partners" in response.json()
    assert "Please assign access to your partner before saving the Program." in response.json()["partners"][0]
