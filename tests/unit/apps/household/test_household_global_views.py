from datetime import datetime
from typing import Any

from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentTypeFactory,
    GrievanceComplaintTicketWithoutExtrasFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramCycleFactory,
    ProgramFactory,
    SanctionListIndividualFactory,
    TicketDeleteHouseholdDetailsFactory,
    TicketDeleteIndividualDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketPaymentVerificationDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import RESIDENCE_STATUS_CHOICE, ROLE_PRIMARY
from hope.models import DocumentType, Household, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def household_global_context(api_client: Any) -> dict[str, Any]:
    global_url_name = "api:households:households-global-list"
    global_count_url = "api:households:households-global-count"

    afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    ukraine = BusinessAreaFactory(slug="ukraine", name="Ukraine")
    program_afghanistan1 = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )
    program_afghanistan2 = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 2",
    )
    program_ukraine = ProgramFactory(business_area=ukraine, status=Program.ACTIVE)

    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    country = CountryFactory()
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
    area3 = AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_2)
    area4 = AreaFactory(parent=area3, p_code="AF01010101", area_type=admin_type_2)

    household_afghanistan1 = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        admin3=area3,
        admin4=area4,
        country=country,
        country_origin=country,
        program=program_afghanistan1,
        business_area=afghanistan,
    )
    household_afghanistan1.created_at = timezone.make_aware(datetime(2025, 1, 1, 12, 0, 0))
    household_afghanistan1.save(update_fields=["created_at"])

    household_afghanistan2 = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        admin3=area3,
        admin4=area4,
        country=country,
        country_origin=country,
        program=program_afghanistan2,
        business_area=afghanistan,
    )
    household_afghanistan2.created_at = timezone.make_aware(datetime(2025, 1, 2, 12, 0, 0))
    household_afghanistan2.save(update_fields=["created_at"])

    household_ukraine = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        admin3=area3,
        admin4=area4,
        country=country,
        country_origin=country,
        program=program_ukraine,
        business_area=ukraine,
    )

    return {
        "global_url_name": global_url_name,
        "global_count_url": global_count_url,
        "afghanistan": afghanistan,
        "ukraine": ukraine,
        "program_afghanistan1": program_afghanistan1,
        "program_afghanistan2": program_afghanistan2,
        "program_ukraine": program_ukraine,
        "partner": partner,
        "user": user,
        "api_client": client,
        "country": country,
        "admin_type_1": admin_type_1,
        "area1": area1,
        "area2": area2,
        "area3": area3,
        "area4": area4,
        "household_afghanistan1": household_afghanistan1,
        "household_afghanistan2": household_afghanistan2,
        "household_ukraine": household_ukraine,
    }


@pytest.mark.parametrize(
    "permissions",
    [
        (Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,),
        (Permissions.RDI_VIEW_DETAILS,),
    ],
)
def test_household_global_list_with_permissions(
    permissions: list, create_user_role_with_permissions: Any, household_global_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_global_context["user"],
        permissions=permissions,
        business_area=household_global_context["afghanistan"],
        whole_business_area_access=True,
    )

    response = household_global_context["api_client"].get(
        reverse(
            household_global_context["global_url_name"],
            kwargs={"business_area_slug": household_global_context["afghanistan"].slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 2

    response_count = household_global_context["api_client"].get(
        reverse(
            household_global_context["global_count_url"],
            kwargs={"business_area_slug": household_global_context["afghanistan"].slug},
        )
    )
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 2

    result_ids = [result["id"] for result in response_results]
    assert str(household_global_context["household_afghanistan1"].id) in result_ids
    assert str(household_global_context["household_afghanistan2"].id) in result_ids
    assert str(household_global_context["household_ukraine"].id) not in result_ids

    for i, household in enumerate(
        [household_global_context["household_afghanistan1"], household_global_context["household_afghanistan2"]]
    ):
        household_result_first = response_results[i]
        assert household_result_first["id"] == str(household.id)
        assert household_result_first["unicef_id"] == household.unicef_id
        assert household_result_first["head_of_household"] == household.head_of_household.full_name
        assert household_result_first["admin1"] == {
            "id": str(household.admin1.id),
            "name": household.admin1.name,
        }
        assert household_result_first["admin2"] == {
            "id": str(household.admin2.id),
            "name": household.admin2.name,
        }
        assert household_result_first["program_id"] == household.program.id
        assert household_result_first["program_name"] == household.program.name
        assert household_result_first["status"] == household.status
        assert household_result_first["size"] == household.size
        assert household_result_first["residence_status"] == household.get_residence_status_display()
        assert household_result_first["total_cash_received"] == household.total_cash_received
        assert household_result_first["total_cash_received_usd"] == household.total_cash_received_usd
        assert (
            household_result_first["last_registration_date"] == f"{household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
        )


def test_household_global_list_with_permissions_in_one_program(
    create_user_role_with_permissions: Any, household_global_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_global_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_global_context["afghanistan"],
        program=household_global_context["program_afghanistan1"],
    )

    response = household_global_context["api_client"].get(
        reverse(
            household_global_context["global_url_name"],
            kwargs={"business_area_slug": household_global_context["afghanistan"].slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 1

    result_ids = [result["id"] for result in response_results]
    assert str(household_global_context["household_afghanistan1"].id) in result_ids
    assert str(household_global_context["household_afghanistan2"].id) not in result_ids
    assert str(household_global_context["household_ukraine"].id) not in result_ids


@pytest.mark.parametrize(
    "permissions",
    [
        [],
        (Permissions.PROGRAMME_ACTIVATE,),
    ],
)
def test_household_global_list_without_permissions(
    permissions: list, create_user_role_with_permissions: Any, household_global_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_global_context["user"],
        permissions=permissions,
        business_area=household_global_context["afghanistan"],
        whole_business_area_access=True,
    )

    response = household_global_context["api_client"].get(
        reverse(
            household_global_context["global_url_name"],
            kwargs={"business_area_slug": household_global_context["afghanistan"].slug},
        )
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_household_global_list_area_limits(
    create_user_role_with_permissions: Any,
    set_admin_area_limits_in_program: Any,
    household_global_context: dict[str, Any],
) -> None:
    create_user_role_with_permissions(
        user=household_global_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_global_context["afghanistan"],
        whole_business_area_access=True,
    )
    set_admin_area_limits_in_program(
        household_global_context["partner"],
        household_global_context["program_afghanistan2"],
        [household_global_context["area1"], household_global_context["area2"]],
    )
    household_afghanistan_without_areas = HouseholdFactory(
        country=household_global_context["country"],
        country_origin=household_global_context["country"],
        program=household_global_context["program_afghanistan2"],
        business_area=household_global_context["afghanistan"],
    )
    area_different = AreaFactory(parent=None, p_code="AF05", area_type=household_global_context["admin_type_1"])
    household_afghanistan_different_areas = HouseholdFactory(
        admin1=area_different,
        admin2=area_different,
        admin3=area_different,
        admin4=area_different,
        country=household_global_context["country"],
        country_origin=household_global_context["country"],
        program=household_global_context["program_afghanistan2"],
        business_area=household_global_context["afghanistan"],
    )

    response = household_global_context["api_client"].get(
        reverse(
            household_global_context["global_url_name"],
            kwargs={"business_area_slug": household_global_context["afghanistan"].slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 3

    result_ids = [result["id"] for result in response_results]
    assert str(household_global_context["household_afghanistan1"].id) in result_ids
    assert str(household_global_context["household_afghanistan2"].id) in result_ids
    assert str(household_afghanistan_without_areas.id) in result_ids
    assert str(household_global_context["household_ukraine"].id) not in result_ids
    assert str(household_afghanistan_different_areas.id) not in result_ids


@pytest.fixture
def household_office_search_context(api_client: Any) -> dict[str, Any]:
    global_url_name = "api:households:households-global-list"
    afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)

    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    def create_household_with_individuals(count: int) -> tuple[Household, list[Any]]:
        household = HouseholdFactory(program=program, business_area=afghanistan, create_role=False)
        individuals = [household.head_of_household]
        individuals.extend(
            IndividualFactory(
                household=household,
                business_area=afghanistan,
                program=program,
                registration_data_import=household.registration_data_import,
            )
            for _ in range(count - 1)
        )
        IndividualRoleInHouseholdFactory(household=household, individual=household.head_of_household, role=ROLE_PRIMARY)
        return household, individuals

    household1, individuals1 = create_household_with_individuals(2)
    household2, individuals2 = create_household_with_individuals(2)
    household3, individuals3 = create_household_with_individuals(2)
    household4, individuals4 = create_household_with_individuals(1)

    program_cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(
        business_area=afghanistan,
        program_cycle=program_cycle,
    )
    payment1 = PaymentFactory(
        parent=payment_plan,
        household=household1,
        head_of_household=individuals1[0],
        program=program,
    )
    payment2 = PaymentFactory(
        parent=payment_plan,
        household=household2,
        head_of_household=individuals2[0],
        program=program,
    )

    grievance_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
    )
    GrievanceComplaintTicketWithoutExtrasFactory(
        ticket=grievance_ticket,
        household=household3,
        individual=individuals3[0],
        payment=None,
    )

    delete_household_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
    )
    TicketDeleteHouseholdDetailsFactory(
        ticket=delete_household_ticket,
        household=household1,
        reason_household=household4,
    )

    household5, individuals5 = create_household_with_individuals(2)
    needs_adjudication_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
    )
    needs_adjudication_ticket.programs.add(program)
    TicketNeedsAdjudicationDetailsFactory(
        ticket=needs_adjudication_ticket,
        golden_records_individual=individuals5[0],
    )

    household6, individuals6 = create_household_with_individuals(1)
    sanction_list_individual = SanctionListIndividualFactory()
    system_flagging_ticket = GrievanceTicketFactory(
        business_area=afghanistan, category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING, issue_type=None
    )
    system_flagging_ticket.programs.add(program)
    TicketSystemFlaggingDetailsFactory(
        ticket=system_flagging_ticket,
        golden_records_individual=individuals6[0],
        sanction_list_individual=sanction_list_individual,
    )

    household8, individuals8 = create_household_with_individuals(1)
    delete_individual_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
    )
    delete_individual_ticket.programs.add(program)
    TicketDeleteIndividualDetailsFactory(
        ticket=delete_individual_ticket,
        individual=individuals8[0],
    )

    household7, individuals7 = create_household_with_individuals(1)
    payment3 = PaymentFactory(
        parent=payment_plan,
        household=household7,
        head_of_household=individuals7[0],
        program=program,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    payment_verification_plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
    )
    payment_verification = PaymentVerificationFactory(
        payment=payment3,
        payment_verification_plan=payment_verification_plan,
    )
    payment_verification_ticket = GrievanceTicketFactory(
        business_area=afghanistan, category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION, issue_type=None
    )
    payment_verification_ticket.programs.add(program)
    TicketPaymentVerificationDetailsFactory(
        ticket=payment_verification_ticket,
        payment_verification=payment_verification,
    )

    return {
        "global_url_name": global_url_name,
        "afghanistan": afghanistan,
        "program": program,
        "partner": partner,
        "user": user,
        "api_client": client,
        "household1": household1,
        "individuals1": individuals1,
        "household2": household2,
        "individuals2": individuals2,
        "household3": household3,
        "individuals3": individuals3,
        "household4": household4,
        "individuals4": individuals4,
        "household5": household5,
        "individuals5": individuals5,
        "household6": household6,
        "individuals6": individuals6,
        "household7": household7,
        "individuals7": individuals7,
        "household8": household8,
        "individuals8": individuals8,
        "payment1": payment1,
        "payment2": payment2,
        "payment_plan": payment_plan,
        "grievance_ticket": grievance_ticket,
        "delete_household_ticket": delete_household_ticket,
        "needs_adjudication_ticket": needs_adjudication_ticket,
        "system_flagging_ticket": system_flagging_ticket,
        "delete_individual_ticket": delete_individual_ticket,
        "payment_verification_ticket": payment_verification_ticket,
    }


def test_search_by_household_unicef_id(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": household_office_search_context["household1"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household1"].id)


def test_search_by_individual_unicef_id(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": household_office_search_context["individuals2"][0].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household2"].id)


def test_search_by_payment_unicef_id(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": household_office_search_context["payment1"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household1"].id)


def test_search_by_payment_plan_unicef_id(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["payment_plan"].refresh_from_db()
    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": household_office_search_context["payment_plan"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(household_office_search_context["household1"].id) in result_ids
    assert str(household_office_search_context["household2"].id) in result_ids
    assert str(household_office_search_context["household7"].id) in result_ids
    assert str(household_office_search_context["household3"].id) not in result_ids


def test_search_by_grievance_unicef_id(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["grievance_ticket"].refresh_from_db()
    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": household_office_search_context["grievance_ticket"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household3"].id)


def test_search_by_grievance_unicef_id_delete_household_ticket(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["delete_household_ticket"].refresh_from_db()
    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": household_office_search_context["delete_household_ticket"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(household_office_search_context["household1"].id) in result_ids
    assert str(household_office_search_context["household4"].id) in result_ids


def test_search_by_grievance_unicef_id_not_found(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": "GRV-DOESNOTEXIST"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 0


def test_search_by_needs_adjudication_household(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["needs_adjudication_ticket"].refresh_from_db()
    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": household_office_search_context["needs_adjudication_ticket"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household5"].id)


def test_search_by_system_flagging_household(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["system_flagging_ticket"].refresh_from_db()
    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": household_office_search_context["system_flagging_ticket"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household6"].id)


def test_search_by_delete_individual_household(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["delete_individual_ticket"].refresh_from_db()
    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": household_office_search_context["delete_individual_ticket"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household8"].id)


def test_search_by_payment_verification_household(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["payment_verification_ticket"].refresh_from_db()
    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": household_office_search_context["payment_verification_ticket"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household7"].id)


def test_search_by_phone_number(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["individuals1"][0].phone_no = "+1234567890"
    household_office_search_context["individuals1"][0].save(update_fields=["phone_no"])

    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": "+1234567890"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household1"].id)


def test_search_by_phone_number_alternative(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["individuals2"][0].phone_no_alternative = "+9876543210"
    household_office_search_context["individuals2"][0].save(update_fields=["phone_no_alternative"])

    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": "+9876543210"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household2"].id)


def test_search_by_member_name(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["individuals3"][0].full_name = "UniqueJohnDoe"
    household_office_search_context["individuals3"][0].save(update_fields=["full_name"])

    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": "UniqueJohnDoe"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household3"].id)


def test_search_by_member_given_name(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        program=household_office_search_context["program"],
    )

    household_office_search_context["individuals4"][0].given_name = "UniqueBob"
    household_office_search_context["individuals4"][0].save(update_fields=["given_name"])

    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": "UniqueBob"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household4"].id)


def test_search_with_active_programs_filter(
    create_user_role_with_permissions: Any, household_office_search_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_office_search_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_office_search_context["afghanistan"],
        whole_business_area_access=True,
    )

    finished_program = ProgramFactory(
        business_area=household_office_search_context["afghanistan"],
        status=Program.FINISHED,
    )
    finished_household = HouseholdFactory(
        program=finished_program,
        business_area=household_office_search_context["afghanistan"],
        create_role=False,
    )
    finished_individual = finished_household.head_of_household
    IndividualRoleInHouseholdFactory(
        household=finished_household,
        individual=finished_individual,
        role=ROLE_PRIMARY,
    )

    household_office_search_context["individuals1"][0].phone_no = "+5551234567"
    household_office_search_context["individuals1"][0].save(update_fields=["phone_no"])
    finished_individual.phone_no = "+5551234567"
    finished_individual.save(update_fields=["phone_no"])

    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": "+5551234567", "active_programs_only": "false"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(household_office_search_context["household1"].id) in result_ids
    assert str(finished_household.id) in result_ids

    response = household_office_search_context["api_client"].get(
        reverse(
            household_office_search_context["global_url_name"],
            kwargs={"business_area_slug": household_office_search_context["afghanistan"].slug},
        ),
        {"office_search": "+5551234567", "active_programs_only": "true"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(household_office_search_context["household1"].id)


@pytest.fixture
def household_choices_context(api_client: Any) -> dict[str, Any]:
    choices_url = "api:households:households-global-choices"
    afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    DocumentTypeFactory(key="passport", label="Passport")
    DocumentTypeFactory(key="id_card", label="ID Card")
    DocumentTypeFactory(key="birth_certificate", label="Birth Certificate")

    return {
        "choices_url": choices_url,
        "afghanistan": afghanistan,
        "partner": partner,
        "user": user,
        "api_client": client,
    }


def test_get_choices(create_user_role_with_permissions: Any, household_choices_context: dict[str, Any]) -> None:
    create_user_role_with_permissions(
        user=household_choices_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_choices_context["afghanistan"],
    )
    response = household_choices_context["api_client"].get(
        reverse(
            household_choices_context["choices_url"],
            kwargs={"business_area_slug": household_choices_context["afghanistan"].slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "document_type_choices": [
            {"name": str(document_type.label), "value": document_type.key}
            for document_type in DocumentType.objects.order_by("key")
        ],
        "residence_status_choices": sorted(
            [{"name": name, "value": value} for value, name in RESIDENCE_STATUS_CHOICE],
            key=lambda choice: choice["name"],
        ),
    }
