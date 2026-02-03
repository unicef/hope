from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.old_factories.account import (
    AdminAreaLimitedToFactory,
    PartnerFactory,
    UserFactory,
)
from extras.test_utils.old_factories.core import (
    FlexibleAttributeForPDUFactory,
    create_afghanistan,
)
from extras.test_utils.old_factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.old_factories.payment import PaymentPlanFactory
from extras.test_utils.old_factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.old_factories.registration_data import RegistrationDataImportFactory
from hope.apps.account.permissions import Permissions
from hope.models import (
    Area,
    BusinessArea,
    FlexibleAttribute,
    Partner,
    PaymentPlan,
    Program,
    RegistrationDataImport,
    User,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return create_afghanistan()


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        partner_access=Program.SELECTED_PARTNERS_ACCESS,
    )


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def pdu_field1(program: Program) -> FlexibleAttribute:
    return FlexibleAttributeForPDUFactory(program=program)


@pytest.fixture
def pdu_field2(program: Program) -> FlexibleAttribute:
    return FlexibleAttributeForPDUFactory(program=program)


@pytest.fixture
def partner_with_all_area_access(
    afghanistan: BusinessArea,
    program: Program,
    create_partner_role_with_permissions: Callable,
) -> Partner:
    partner = PartnerFactory(name="PartnerWithAllAreaAccess")
    create_partner_role_with_permissions(
        partner,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program,
    )
    return partner


@pytest.fixture
def area1(afghanistan: BusinessArea) -> Area:
    country = CountryFactory()
    country.business_areas.set([afghanistan])
    admin_type = AreaTypeFactory(country=country, area_level=1)
    return AreaFactory(parent=None, p_code="AF01", area_type=admin_type, name="Area1")


@pytest.fixture
def area2(afghanistan: BusinessArea) -> Area:
    country = CountryFactory()
    country.business_areas.set([afghanistan])
    admin_type = AreaTypeFactory(country=country, area_level=1)
    return AreaFactory(parent=None, p_code="AF0101", area_type=admin_type, name="Area2")


@pytest.fixture
def partner_with_area_limits(
    afghanistan: BusinessArea,
    program: Program,
    area1: Area,
    create_partner_role_with_permissions: Callable,
) -> Partner:
    partner = PartnerFactory(name="PartnerWithAreaLimits")
    create_partner_role_with_permissions(
        partner,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program,
    )
    admin_area_limits = AdminAreaLimitedToFactory(partner=partner, program=program)
    admin_area_limits.areas.set([area1])
    return partner


@pytest.fixture
def partner_without_access(db: Any) -> Partner:
    return PartnerFactory(name="PartnerWithoutAccess")


@pytest.fixture
def rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(program=program)


@pytest.fixture
def payment_plan(program: Program) -> PaymentPlan:
    program_cycle = ProgramCycleFactory(program=program)
    return PaymentPlanFactory(program_cycle=program_cycle)


@pytest.fixture
def detail_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:programs:programs-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "slug": program.slug,
        },
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_program_detail_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    detail_url: str,
    create_user_role_with_permissions: Callable,
    partner_with_all_area_access: Partner,
    partner_with_area_limits: Partner,
    partner_without_access: Partner,
    rdi: RegistrationDataImport,
    payment_plan: PaymentPlan,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], afghanistan, program)
    response = authenticated_client.get(detail_url)
    assert response.status_code == status.HTTP_200_OK


def test_program_detail_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    detail_url: str,
    create_user_role_with_permissions: Callable,
    partner_with_all_area_access: Partner,
    partner_with_area_limits: Partner,
    partner_without_access: Partner,
    rdi: RegistrationDataImport,
    payment_plan: PaymentPlan,
) -> None:
    create_user_role_with_permissions(user, [], afghanistan, program)
    response = authenticated_client.get(detail_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_program_detail(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    detail_url: str,
    pdu_field1: FlexibleAttribute,
    pdu_field2: FlexibleAttribute,
    partner_with_all_area_access: Partner,
    partner_with_area_limits: Partner,
    area1: Area,
    create_user_role_with_permissions: Callable,
    partner_without_access: Partner,
    rdi: RegistrationDataImport,
    payment_plan: PaymentPlan,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program,
    )

    response = authenticated_client.get(detail_url)
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    partner_unicef_hq = Partner.objects.get(name="UNICEF HQ")
    partner_unicef_in_afg = Partner.objects.get(name="UNICEF Partner for afghanistan")

    assert response_data["id"] == str(program.id)
    assert response_data["version"] == program.version
    assert response_data["programme_code"] == program.programme_code
    assert response_data["slug"] == program.slug
    assert response_data["name"] == program.name
    assert response_data["start_date"] == program.start_date.strftime("%Y-%m-%d")
    assert response_data["end_date"] == program.end_date.strftime("%Y-%m-%d")
    assert response_data["budget"] == str(program.budget)
    assert response_data["frequency_of_payments"] == program.frequency_of_payments
    assert response_data["sector"] == program.sector
    assert response_data["cash_plus"] == program.cash_plus
    assert response_data["population_goal"] == program.population_goal
    assert response_data["screen_beneficiary"] == program.screen_beneficiary
    assert response_data["data_collecting_type"] == {
        "id": program.data_collecting_type.id,
        "label": program.data_collecting_type.label,
        "code": program.data_collecting_type.code,
        "type": program.data_collecting_type.type,
        "type_display": program.data_collecting_type.get_type_display(),
        "household_filters_available": program.data_collecting_type.household_filters_available,
        "individual_filters_available": program.data_collecting_type.individual_filters_available,
    }
    assert response_data["beneficiary_group"] == {
        "id": str(program.beneficiary_group.id),
        "name": program.beneficiary_group.name,
        "group_label": program.beneficiary_group.group_label,
        "group_label_plural": program.beneficiary_group.group_label_plural,
        "member_label": program.beneficiary_group.member_label,
        "member_label_plural": program.beneficiary_group.member_label_plural,
        "master_detail": program.beneficiary_group.master_detail,
    }
    assert response_data["status"] == program.status
    assert response_data["pdu_fields"] == [
        {
            "id": str(pdu_field1.id),
            "label": pdu_field1.label["English(EN)"],
            "name": pdu_field1.name,
            "pdu_data": {
                "subtype": pdu_field1.pdu_data.subtype,
                "number_of_rounds": pdu_field1.pdu_data.number_of_rounds,
                "rounds_names": pdu_field1.pdu_data.rounds_names,
            },
        },
        {
            "id": str(pdu_field2.id),
            "label": pdu_field2.label["English(EN)"],
            "name": pdu_field2.name,
            "pdu_data": {
                "subtype": pdu_field2.pdu_data.subtype,
                "number_of_rounds": pdu_field2.pdu_data.number_of_rounds,
                "rounds_names": pdu_field2.pdu_data.rounds_names,
            },
        },
    ]
    assert response_data["household_count"] == program.household_count

    assert response_data["description"] == program.description
    assert response_data["administrative_areas_of_implementation"] == program.administrative_areas_of_implementation
    assert response_data["version"] == program.version
    assert response_data["partners"] == [
        {
            "id": partner_with_all_area_access.id,
            "name": partner_with_all_area_access.name,
            "area_access": "BUSINESS_AREA",
            "areas": None,
        },
        {
            "id": partner_with_area_limits.id,
            "name": partner_with_area_limits.name,
            "area_access": "ADMIN_AREA",
            "areas": [
                {
                    "id": str(area1.id),
                    "level": area1.area_type.level,
                }
            ],
        },
        {
            "id": partner_unicef_hq.id,
            "name": partner_unicef_hq.name,
            "area_access": "BUSINESS_AREA",
            "areas": None,
        },
        {
            "id": partner_unicef_in_afg.id,
            "name": partner_unicef_in_afg.name,
            "area_access": "BUSINESS_AREA",
            "areas": None,
        },
    ]
    assert response_data["partner_access"] == program.partner_access
    assert response_data["can_import_rdi"] is True
    assert response_data["registration_imports_total_count"] == program.registration_imports.count()
    assert (
        response_data["target_populations_count"] == PaymentPlan.objects.filter(program_cycle__program=program).count()
    )
    assert response_data["population_goal"] == program.population_goal


def test_program_detail_can_import_rdi(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        program,
    )
    program.biometric_deduplication_enabled = True
    program.save()

    # No registration data imports
    response = authenticated_client.get(detail_url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["can_import_rdi"] is True

    # Deduplicated RDI in review
    rdi = RegistrationDataImportFactory(
        program=program,
        business_area=afghanistan,
        status=RegistrationDataImport.IN_REVIEW,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
    )

    response = authenticated_client.get(detail_url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["can_import_rdi"] is False

    # Deduplicated RDI merged
    rdi.status = RegistrationDataImport.MERGED
    rdi.save()
    response = authenticated_client.get(detail_url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["can_import_rdi"] is True
