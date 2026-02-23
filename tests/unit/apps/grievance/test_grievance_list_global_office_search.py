"""Tests for grievance ticket global list - office search functionality."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketComplaintDetailsFactory,
    TicketDeleteHouseholdDetailsFactory,
    TicketDeleteIndividualDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketPaymentVerificationDetailsFactory,
    TicketSensitiveDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
)
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory
from extras.test_utils.factories.sanction_list import (
    SanctionListIndividualFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, Partner, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="AFG")


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
    )


@pytest.fixture
def households_and_individuals(
    afghanistan: BusinessArea,
    program: Program,
) -> dict:
    rdi = RegistrationDataImportFactory(business_area=afghanistan)

    individual1_1 = IndividualFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    household1 = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        head_of_household=individual1_1,
    )
    individual1_1.household = household1
    individual1_1.save()
    individual1_2 = IndividualFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        household=household1,
    )

    individual2_1 = IndividualFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    household2 = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        head_of_household=individual2_1,
    )
    individual2_1.household = household2
    individual2_1.save()
    individual2_2 = IndividualFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        household=household2,
    )

    individual3_1 = IndividualFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    household3 = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        head_of_household=individual3_1,
    )
    individual3_1.household = household3
    individual3_1.save()
    individual3_2 = IndividualFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        household=household3,
    )

    individual4_1 = IndividualFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    household4 = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        head_of_household=individual4_1,
    )
    individual4_1.household = household4
    individual4_1.save()

    individual5_1 = IndividualFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    household5 = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        head_of_household=individual5_1,
    )
    individual5_1.household = household5
    individual5_1.save()

    return {
        "household1": household1,
        "individuals1": [individual1_1, individual1_2],
        "household2": household2,
        "individuals2": [individual2_1, individual2_2],
        "household3": household3,
        "individuals3": [individual3_1, individual3_2],
        "household4": household4,
        "individuals4": [individual4_1],
        "household5": household5,
        "individuals5": [individual5_1],
    }


@pytest.fixture
def tickets(
    afghanistan: BusinessArea,
    program: Program,
    households_and_individuals: dict,
) -> dict:
    data = households_and_individuals

    program_cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(
        business_area=afghanistan,
        program_cycle=program_cycle,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        household=data["household1"],
        head_of_household=data["individuals1"][0],
        program=program,
        collector=data["individuals1"][0],
    )

    complaint_ticket1 = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
    )
    TicketComplaintDetailsFactory(
        ticket=complaint_ticket1,
        household=data["household1"],
        individual=data["individuals1"][0],
        payment=None,
    )
    complaint_ticket1.programs.add(program)

    sensitive_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )
    TicketSensitiveDetailsFactory(
        ticket=sensitive_ticket,
        household=data["household2"],
        individual=data["individuals2"][0],
        payment=None,
    )
    sensitive_ticket.programs.add(program)

    complaint_ticket2 = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
    )
    TicketComplaintDetailsFactory(
        ticket=complaint_ticket2,
        household=data["household3"],
        individual=data["individuals3"][0],
        payment=payment,
    )
    complaint_ticket2.programs.add(program)

    needs_adjudication_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
    )
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=needs_adjudication_ticket,
        golden_records_individual=data["individuals1"][0],
    )
    ticket_details.possible_duplicates.add(data["individuals2"][1])
    needs_adjudication_ticket.programs.add(program)

    delete_individual_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
    )
    TicketDeleteIndividualDetailsFactory(
        ticket=delete_individual_ticket,
        individual=data["individuals3"][1],
    )
    delete_individual_ticket.programs.add(program)

    delete_household_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
    )
    TicketDeleteHouseholdDetailsFactory(
        ticket=delete_household_ticket,
        household=data["household4"],
    )
    delete_household_ticket.programs.add(program)

    sanction_list_individual = SanctionListIndividualFactory()
    system_flagging_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
    )
    TicketSystemFlaggingDetailsFactory(
        ticket=system_flagging_ticket,
        golden_records_individual=data["individuals1"][1],
        sanction_list_individual=sanction_list_individual,
    )
    system_flagging_ticket.programs.add(program)

    payment_plan2 = PaymentPlanFactory(
        business_area=afghanistan,
        program_cycle=program_cycle,
    )
    payment2 = PaymentFactory(
        parent=payment_plan2,
        household=data["household5"],
        head_of_household=data["individuals5"][0],
        program=program,
        collector=data["individuals5"][0],
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan2)
    payment_verification_plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan2,
    )
    payment_verification = PaymentVerificationFactory(
        payment=payment2,
        payment_verification_plan=payment_verification_plan,
    )
    payment_verification_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        issue_type=None,
    )
    TicketPaymentVerificationDetailsFactory(
        ticket=payment_verification_ticket,
        payment_verification=payment_verification,
    )
    payment_verification_ticket.programs.add(program)

    return {
        "complaint_ticket1": complaint_ticket1,
        "sensitive_ticket": sensitive_ticket,
        "complaint_ticket2": complaint_ticket2,
        "needs_adjudication_ticket": needs_adjudication_ticket,
        "delete_individual_ticket": delete_individual_ticket,
        "delete_household_ticket": delete_household_ticket,
        "system_flagging_ticket": system_flagging_ticket,
        "payment_verification_ticket": payment_verification_ticket,
        "payment": payment,
    }


def test_search_by_grievance_ticket_unicef_id(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    complaint_ticket1 = tickets["complaint_ticket1"]
    complaint_ticket1.refresh_from_db()
    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": complaint_ticket1.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(complaint_ticket1.id)


def test_search_by_household_unicef_id_complaint_ticket(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    household1 = households_and_individuals["household1"]
    complaint_ticket1 = tickets["complaint_ticket1"]

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": household1.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK

    result_ids = [result["id"] for result in response.data["results"]]
    assert str(complaint_ticket1.id) in result_ids


def test_search_by_household_unicef_id_sensitive_ticket(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
        afghanistan,
        program=program,
    )

    household2 = households_and_individuals["household2"]
    sensitive_ticket = tickets["sensitive_ticket"]
    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": household2.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(sensitive_ticket.id)


def test_search_by_individual_unicef_id_sensitive_ticket(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
        afghanistan,
        program=program,
    )

    individuals2 = households_and_individuals["individuals2"]
    sensitive_ticket = tickets["sensitive_ticket"]
    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": individuals2[0].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(sensitive_ticket.id)


def test_search_by_delete_individual_ticket_details(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    individuals3 = households_and_individuals["individuals3"]
    delete_individual_ticket = tickets["delete_individual_ticket"]
    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": individuals3[1].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(delete_individual_ticket.id)


def test_search_by_delete_individual_household(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    household3 = households_and_individuals["household3"]
    delete_individual_ticket = tickets["delete_individual_ticket"]

    client = api_client(user)
    # Search by household of the individual being deleted
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": household3.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(delete_individual_ticket.id) in result_ids


def test_search_by_payment_verification_household(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    household5 = households_and_individuals["household5"]
    payment_verification_ticket = tickets["payment_verification_ticket"]

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": household5.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(payment_verification_ticket.id)


def test_search_by_payment_verification_individual(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    individuals5 = households_and_individuals["individuals5"]
    payment_verification_ticket = tickets["payment_verification_ticket"]
    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": individuals5[0].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(payment_verification_ticket.id)


def test_search_by_household_unicef_id_multiple_tickets(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    household1 = households_and_individuals["household1"]
    complaint_ticket1 = tickets["complaint_ticket1"]
    needs_adjudication_ticket = tickets["needs_adjudication_ticket"]
    system_flagging_ticket = tickets["system_flagging_ticket"]

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": household1.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(complaint_ticket1.id) in result_ids
    assert str(needs_adjudication_ticket.id) in result_ids
    assert str(system_flagging_ticket.id) in result_ids


def test_search_by_individual_unicef_id_multiple_tickets(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    individuals1 = households_and_individuals["individuals1"]
    complaint_ticket1 = tickets["complaint_ticket1"]
    needs_adjudication_ticket = tickets["needs_adjudication_ticket"]

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": individuals1[0].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(needs_adjudication_ticket.id) in result_ids
    assert str(complaint_ticket1.id) in result_ids


def test_search_by_possible_duplicates_individual(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    individuals2 = households_and_individuals["individuals2"]
    needs_adjudication_ticket = tickets["needs_adjudication_ticket"]

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": individuals2[1].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(needs_adjudication_ticket.id)


def test_search_by_needs_adjudication_household(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    household1 = households_and_individuals["household1"]
    needs_adjudication_ticket = tickets["needs_adjudication_ticket"]

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": household1.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(needs_adjudication_ticket.id) in result_ids


def test_search_by_payment_unicef_id(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    complaint_ticket2 = tickets["complaint_ticket2"]
    payment = tickets["payment"]
    complaint_ticket2.refresh_from_db()

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": payment.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(complaint_ticket2.id)


def test_search_by_system_flagging_individual(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    individuals1 = households_and_individuals["individuals1"]
    system_flagging_ticket = tickets["system_flagging_ticket"]

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": individuals1[1].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(system_flagging_ticket.id)


def test_search_by_system_flagging_household(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    household1 = households_and_individuals["household1"]
    system_flagging_ticket = tickets["system_flagging_ticket"]
    complaint_ticket1 = tickets["complaint_ticket1"]

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": household1.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(system_flagging_ticket.id) in result_ids
    assert str(complaint_ticket1.id) in result_ids


def test_search_by_delete_household_ticket(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    household4 = households_and_individuals["household4"]
    delete_household_ticket = tickets["delete_household_ticket"]

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": household4.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(delete_household_ticket.id)


def test_search_by_phone_number(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    individuals1 = households_and_individuals["individuals1"]
    complaint_ticket1 = tickets["complaint_ticket1"]
    needs_adjudication_ticket = tickets["needs_adjudication_ticket"]

    # Update individual with phone number
    individuals1[0].phone_no = "+1234567890"
    individuals1[0].save()

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": "+1234567890"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(complaint_ticket1.id) in result_ids
    assert str(needs_adjudication_ticket.id) in result_ids


def test_search_by_phone_number_alternative(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
        afghanistan,
        program=program,
    )

    individuals2 = households_and_individuals["individuals2"]
    sensitive_ticket = tickets["sensitive_ticket"]

    # Update individual with alternative phone number
    individuals2[0].phone_no_alternative = "+9876543210"
    individuals2[0].save()

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": "+9876543210"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(sensitive_ticket.id)


def test_search_by_individual_name(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        program=program,
    )

    individuals3 = households_and_individuals["individuals3"]
    complaint_ticket2 = tickets["complaint_ticket2"]

    # Update individual with specific name
    individuals3[0].full_name = "UniqueGrievanceName"
    individuals3[0].save()

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": "UniqueGrievanceName"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(complaint_ticket2.id)


def test_search_with_active_programs_filter(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    tickets: dict,
    households_and_individuals: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )

    individuals1 = households_and_individuals["individuals1"]
    complaint_ticket1 = tickets["complaint_ticket1"]
    needs_adjudication_ticket = tickets["needs_adjudication_ticket"]

    finished_program = ProgramFactory(business_area=afghanistan, status=Program.FINISHED)
    rdi = RegistrationDataImportFactory(business_area=afghanistan)

    finished_individual = IndividualFactory(
        business_area=afghanistan,
        program=finished_program,
        registration_data_import=rdi,
        household=None,
    )
    finished_household = HouseholdFactory(
        program=finished_program,
        business_area=afghanistan,
        registration_data_import=rdi,
        head_of_household=finished_individual,
    )
    finished_individual.household = finished_household
    finished_individual.save()

    finished_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
    )
    finished_ticket.programs.add(finished_program)
    TicketComplaintDetailsFactory(
        ticket=finished_ticket,
        household=finished_household,
        individual=finished_individual,
        payment=None,
    )

    # Set same phone number for both active and finished program individuals
    individuals1[0].phone_no = "+5557778888"
    individuals1[0].save()

    finished_individual.phone_no = "+5557778888"
    finished_individual.save()

    # First, search WITHOUT active_programs filter - should return 3 grievances (2 active, 1 finished)
    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": "+5557778888", "active_programs_only": "false"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(complaint_ticket1.id) in result_ids
    assert str(needs_adjudication_ticket.id) in result_ids
    assert str(finished_ticket.id) in result_ids

    # Now search WITH active_programs_only filter - should only return active program grievances
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        ),
        {"office_search": "+5557778888", "active_programs_only": "true"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(complaint_ticket1.id) in result_ids
    assert str(needs_adjudication_ticket.id) in result_ids
