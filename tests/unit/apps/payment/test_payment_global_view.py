from decimal import Decimal
from typing import Any, List

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory, TicketSensitiveDetailsFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def partner():
    return PartnerFactory(name="unittest")


@pytest.fixture
def user(partner):
    return UserFactory(partner=partner)


@pytest.fixture
def api_client_user(api_client: Any, user):
    return api_client(user)


@pytest.fixture
def program_active(business_area):
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def program_cycle(program_active):
    return ProgramCycleFactory(program=program_active)


@pytest.fixture
def payment_plan(user, business_area, program_cycle):
    return PaymentPlanFactory(
        name="Payment Plan",
        business_area=business_area,
        program_cycle=program_cycle,
        status=PaymentPlan.Status.OPEN,
        created_by=user,
        created_at="2022-02-24",
    )


@pytest.fixture
def base_household(business_area, program_active):
    return HouseholdFactory(business_area=business_area, program=program_active)


@pytest.fixture
def base_payment(payment_plan, base_household, program_active):
    head = base_household.head_of_household
    return PaymentFactory(
        parent=payment_plan,
        household=base_household,
        head_of_household=head,
        collector=head,
        program=program_active,
        status=Payment.STATUS_SUCCESS,
        delivered_quantity=Decimal("999.00"),
        entitlement_quantity=Decimal("112.00"),
    )


@pytest.fixture
def global_urls(business_area):
    return {
        "list": reverse(
            "api:payments:payments-global-list",
            kwargs={"business_area_slug": business_area.slug},
        ),
        "choices": reverse(
            "api:payments:payments-global-choices",
            kwargs={"business_area_slug": business_area.slug},
        ),
        "count": reverse(
            "api:payments:payments-global-count",
            kwargs={"business_area_slug": business_area.slug},
        ),
    }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_global_list(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    user,
    business_area,
    program_active,
    api_client_user,
    global_urls,
    base_payment,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = api_client_user.get(global_urls["list"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert len(resp_data["results"]) == 1
        payment = resp_data["results"][0]
        assert payment["delivered_quantity"] == "999.00"
        assert payment["status"] == "Transaction Successful"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_global_choices(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    user,
    business_area,
    program_active,
    api_client_user,
    global_urls,
    base_payment,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = api_client_user.get(global_urls["choices"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        data = response.json()
        assert "status_choices" in data
        assert isinstance(data["status_choices"], list)
        assert any(x.get("value") == Payment.STATUS_SUCCESS for x in data["status_choices"])


def test_count_endpoint(
    create_user_role_with_permissions: Any,
    user,
    business_area,
    program_active,
    api_client_user,
    global_urls,
    payment_plan,
    base_payment,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_DETAILS],
        business_area,
        program_active,
    )
    PaymentFactory(
        parent=payment_plan,
        program=program_active,
        status=Payment.STATUS_PENDING,
    )

    response = api_client_user.get(global_urls["count"])

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 2


def test_ordering(
    create_user_role_with_permissions: Any,
    user,
    business_area,
    program_active,
    api_client_user,
    global_urls,
    payment_plan,
    base_payment,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_DETAILS],
        business_area,
        program_active,
    )
    PaymentFactory(
        parent=payment_plan,
        program=program_active,
        delivered_quantity=Decimal("100.00"),
        status=Payment.STATUS_SUCCESS,
    )
    PaymentFactory(
        parent=payment_plan,
        program=program_active,
        delivered_quantity=Decimal("500.00"),
        status=Payment.STATUS_SUCCESS,
    )

    response = api_client_user.get(f"{global_urls['list']}?ordering=delivered_quantity")
    results = response.json()["results"]
    assert len(results) == 3
    quantities = [float(r["delivered_quantity"]) for r in results]
    assert quantities == sorted(quantities)

    response = api_client_user.get(f"{global_urls['list']}?ordering=-delivered_quantity")
    results = response.json()["results"]
    quantities = [float(r["delivered_quantity"]) for r in results]
    assert quantities == sorted(quantities, reverse=True)


def test_excludes_pre_payment_statuses(
    create_user_role_with_permissions: Any,
    user,
    business_area,
    program_active,
    api_client_user,
    global_urls,
    base_payment,
    program_cycle,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_DETAILS],
        business_area,
        program_active,
    )

    pp_tp_open = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=program_cycle,
        status=PaymentPlan.Status.TP_OPEN,
    )
    PaymentFactory(
        parent=pp_tp_open,
        program=program_active,
    )

    response = api_client_user.get(global_urls["list"])
    results = response.json()["results"]
    assert len(results) == 1
    assert str(results[0]["id"]) == str(base_payment.id)


def test_program_filtering(
    create_user_role_with_permissions: Any,
    user,
    business_area,
    program_active,
    api_client_user,
    global_urls,
    base_payment,
) -> None:
    program_no_access = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle_no_access = ProgramCycleFactory(program=program_no_access)

    pp_no_access = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle_no_access,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentFactory(
        parent=pp_no_access,
        program=program_no_access,
    )

    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_DETAILS],
        business_area,
        program_active,
    )

    response = api_client_user.get(global_urls["list"])
    results = response.json()["results"]

    assert len(results) == 1
    assert str(results[0]["id"]) == str(base_payment.id)


@pytest.fixture
def office_search_setup(api_client: Any, business_area, global_urls):
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program)

    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    payment_plan1 = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.ACCEPTED,
    )
    household1 = HouseholdFactory(business_area=business_area, program=program)
    individuals1 = [household1.head_of_household]
    individuals1.append(
        IndividualFactory(
            household=household1,
            business_area=business_area,
            program=program,
            registration_data_import=household1.registration_data_import,
        )
    )

    household1_2 = HouseholdFactory(business_area=business_area, program=program)
    individuals1_2 = [household1_2.head_of_household]

    payment_plan2 = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.ACCEPTED,
    )
    household2 = HouseholdFactory(business_area=business_area, program=program)
    individuals2 = [household2.head_of_household]
    individuals2.append(
        IndividualFactory(
            household=household2,
            business_area=business_area,
            program=program,
            registration_data_import=household2.registration_data_import,
        )
    )

    payment_plan3 = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.ACCEPTED,
    )
    household3 = HouseholdFactory(business_area=business_area, program=program)
    individuals3 = [household3.head_of_household]
    individuals3.append(
        IndividualFactory(
            household=household3,
            business_area=business_area,
            program=program,
            registration_data_import=household3.registration_data_import,
        )
    )

    payment1 = PaymentFactory(
        parent=payment_plan1,
        household=household1,
        head_of_household=individuals1[0],
        collector=individuals1[0],
        program=program,
        status=Payment.STATUS_SUCCESS,
    )
    payment1_second = PaymentFactory(
        parent=payment_plan1,
        household=household1_2,
        head_of_household=individuals1_2[0],
        collector=individuals1_2[0],
        program=program,
        status=Payment.STATUS_SUCCESS,
    )
    payment2 = PaymentFactory(
        parent=payment_plan2,
        household=household2,
        head_of_household=individuals2[0],
        collector=individuals2[0],
        program=program,
        status=Payment.STATUS_PENDING,
    )
    payment3 = PaymentFactory(
        parent=payment_plan3,
        household=household3,
        head_of_household=individuals3[0],
        collector=individuals3[0],
        program=program,
        status=Payment.STATUS_SUCCESS,
    )

    return {
        "global_url": global_urls["list"],
        "business_area": business_area,
        "program": program,
        "cycle": cycle,
        "user": user,
        "client": client,
        "payment_plan1": payment_plan1,
        "payment_plan2": payment_plan2,
        "payment_plan3": payment_plan3,
        "household1": household1,
        "household1_2": household1_2,
        "household2": household2,
        "household3": household3,
        "individuals1": individuals1,
        "individuals1_2": individuals1_2,
        "individuals2": individuals2,
        "individuals3": individuals3,
        "payment1": payment1,
        "payment1_second": payment1_second,
        "payment2": payment2,
        "payment3": payment3,
    }


def test_search_by_payment_unicef_id(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_DETAILS],
        business_area=office_search_setup["business_area"],
        program=office_search_setup["program"],
    )

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": office_search_setup["payment1"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment1"].id)


def test_search_by_household_unicef_id(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_DETAILS],
        business_area=office_search_setup["business_area"],
        program=office_search_setup["program"],
    )

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": office_search_setup["household2"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment2"].id)


def test_search_by_individual_unicef_id(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_DETAILS],
        business_area=office_search_setup["business_area"],
        program=office_search_setup["program"],
    )

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": office_search_setup["individuals3"][0].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment3"].id)


def test_search_by_payment_plan_unicef_id(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_DETAILS],
        business_area=office_search_setup["business_area"],
        program=office_search_setup["program"],
    )

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": office_search_setup["payment_plan1"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(office_search_setup["payment1"].id) in result_ids
    assert str(office_search_setup["payment1_second"].id) in result_ids


def test_search_by_grievance_unicef_id(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_DETAILS],
        business_area=office_search_setup["business_area"],
        program=office_search_setup["program"],
    )

    ticket = GrievanceTicketFactory(
        business_area=office_search_setup["business_area"],
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )

    TicketSensitiveDetailsFactory(
        ticket=ticket,
        payment=office_search_setup["payment2"],
    )

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": ticket.unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment2"].id)


def test_search_by_phone_number(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_DETAILS],
        business_area=office_search_setup["business_area"],
        program=office_search_setup["program"],
    )

    office_search_setup["individuals1"][0].phone_no = "+1234567890"
    office_search_setup["individuals1"][0].save()

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": "+1234567890"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment1"].id)


def test_search_by_phone_number_alternative(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_DETAILS],
        business_area=office_search_setup["business_area"],
        program=office_search_setup["program"],
    )

    office_search_setup["individuals2"][0].phone_no_alternative = "+9876543210"
    office_search_setup["individuals2"][0].save()

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": "+9876543210"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment2"].id)


def test_search_by_individual_name(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_DETAILS],
        business_area=office_search_setup["business_area"],
        program=office_search_setup["program"],
    )

    office_search_setup["individuals3"][0].full_name = "UniqueCharliePay"
    office_search_setup["individuals3"][0].save()

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": "UniqueCharliePay"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment3"].id)


def test_search_with_active_programs_filter(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_DETAILS],
        business_area=office_search_setup["business_area"],
        whole_business_area_access=True,
    )

    finished_program = ProgramFactory(business_area=office_search_setup["business_area"], status=Program.FINISHED)
    finished_cycle = ProgramCycleFactory(program=finished_program)
    finished_payment_plan = PaymentPlanFactory(
        business_area=office_search_setup["business_area"],
        program_cycle=finished_cycle,
        status=PaymentPlan.Status.ACCEPTED,
    )
    finished_household = HouseholdFactory(
        business_area=office_search_setup["business_area"],
        program=finished_program,
    )
    finished_individuals = [finished_household.head_of_household]
    payment_finished = PaymentFactory(
        parent=finished_payment_plan,
        household=finished_household,
        head_of_household=finished_individuals[0],
        collector=finished_individuals[0],
        program=finished_program,
        status=Payment.STATUS_SUCCESS,
    )

    office_search_setup["individuals1"][0].phone_no = "+5555556666"
    office_search_setup["individuals1"][0].save()

    finished_individuals[0].phone_no = "+5555556666"
    finished_individuals[0].save()

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": "+5555556666", "active_programs_only": "false"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(office_search_setup["payment1"].id) in result_ids
    assert str(payment_finished.id) in result_ids

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": "+5555556666", "active_programs_only": "true"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment1"].id)
