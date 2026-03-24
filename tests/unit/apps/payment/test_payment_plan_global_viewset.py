from typing import Any

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.models import PaymentPlan, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_areas():
    afghanistan = BusinessAreaFactory(slug="afghanistan")
    ukraine = BusinessAreaFactory(slug="ukraine")
    return {"afghanistan": afghanistan, "ukraine": ukraine}


@pytest.fixture
def programs_and_cycles(business_areas):
    afghanistan = business_areas["afghanistan"]
    ukraine = business_areas["ukraine"]

    program_afghanistan1 = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="Program Afghanistan 1",
    )
    program_afghanistan2 = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="Program Afghanistan 2",
    )
    program_ukraine = ProgramFactory(
        business_area=ukraine,
        status=Program.ACTIVE,
        name="Program Ukraine",
    )

    program_cycle_afghanistan1 = ProgramCycleFactory(program=program_afghanistan1)
    program_cycle_afghanistan2 = ProgramCycleFactory(program=program_afghanistan2)
    program_cycle_ukraine = ProgramCycleFactory(program=program_ukraine)

    return {
        "program_afghanistan1": program_afghanistan1,
        "program_afghanistan2": program_afghanistan2,
        "program_ukraine": program_ukraine,
        "program_cycle_afghanistan1": program_cycle_afghanistan1,
        "program_cycle_afghanistan2": program_cycle_afghanistan2,
        "program_cycle_ukraine": program_cycle_ukraine,
    }


@pytest.fixture
def user_client(api_client: Any):
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    return {"user": user, "client": api_client(user)}


@pytest.fixture
def payment_plans_data(business_areas, programs_and_cycles):
    payment_plan_afghanistan1 = PaymentPlanFactory(
        business_area=business_areas["afghanistan"],
        program_cycle=programs_and_cycles["program_cycle_afghanistan1"],
        status=PaymentPlan.Status.ACCEPTED,
    )
    payment_plan_afghanistan2 = PaymentPlanFactory(
        business_area=business_areas["afghanistan"],
        program_cycle=programs_and_cycles["program_cycle_afghanistan2"],
        status=PaymentPlan.Status.ACCEPTED,
    )
    payment_plan_ukraine = PaymentPlanFactory(
        business_area=business_areas["ukraine"],
        program_cycle=programs_and_cycles["program_cycle_ukraine"],
        status=PaymentPlan.Status.ACCEPTED,
    )

    household_afghanistan1 = HouseholdFactory(
        business_area=business_areas["afghanistan"],
        program=programs_and_cycles["program_afghanistan1"],
    )
    household_afghanistan2 = HouseholdFactory(
        business_area=business_areas["afghanistan"],
        program=programs_and_cycles["program_afghanistan2"],
    )
    household_ukraine = HouseholdFactory(
        business_area=business_areas["ukraine"],
        program=programs_and_cycles["program_ukraine"],
    )

    individuals_afghanistan1 = [household_afghanistan1.head_of_household]
    individuals_afghanistan1.append(
        IndividualFactory(
            household=household_afghanistan1,
            business_area=business_areas["afghanistan"],
            program=programs_and_cycles["program_afghanistan1"],
            registration_data_import=household_afghanistan1.registration_data_import,
        )
    )
    individuals_afghanistan2 = [household_afghanistan2.head_of_household]
    individuals_afghanistan2.append(
        IndividualFactory(
            household=household_afghanistan2,
            business_area=business_areas["afghanistan"],
            program=programs_and_cycles["program_afghanistan2"],
            registration_data_import=household_afghanistan2.registration_data_import,
        )
    )
    individuals_ukraine = [household_ukraine.head_of_household]
    individuals_ukraine.append(
        IndividualFactory(
            household=household_ukraine,
            business_area=business_areas["ukraine"],
            program=programs_and_cycles["program_ukraine"],
            registration_data_import=household_ukraine.registration_data_import,
        )
    )

    payment_afghanistan1 = PaymentFactory(
        business_area=business_areas["afghanistan"],
        parent=payment_plan_afghanistan1,
        household=household_afghanistan1,
        head_of_household=individuals_afghanistan1[0],
        collector=individuals_afghanistan1[0],
        program=programs_and_cycles["program_afghanistan1"],
    )
    payment_afghanistan2 = PaymentFactory(
        business_area=business_areas["afghanistan"],
        parent=payment_plan_afghanistan2,
        household=household_afghanistan2,
        head_of_household=individuals_afghanistan2[0],
        collector=individuals_afghanistan2[0],
        program=programs_and_cycles["program_afghanistan2"],
    )
    payment_ukraine = PaymentFactory(
        business_area=business_areas["ukraine"],
        parent=payment_plan_ukraine,
        household=household_ukraine,
        head_of_household=individuals_ukraine[0],
        collector=individuals_ukraine[0],
        program=programs_and_cycles["program_ukraine"],
    )

    return {
        "payment_plan_afghanistan1": payment_plan_afghanistan1,
        "payment_plan_afghanistan2": payment_plan_afghanistan2,
        "payment_plan_ukraine": payment_plan_ukraine,
        "payment_afghanistan1": payment_afghanistan1,
        "payment_afghanistan2": payment_afghanistan2,
        "payment_ukraine": payment_ukraine,
    }


@pytest.fixture
def global_urls(business_areas):
    return {
        "list_afghanistan": reverse(
            "api:payments:payment-plans-global-list",
            kwargs={"business_area_slug": business_areas["afghanistan"].slug},
        ),
        "list_ukraine": reverse(
            "api:payments:payment-plans-global-list",
            kwargs={"business_area_slug": business_areas["ukraine"].slug},
        ),
        "count_afghanistan": reverse(
            "api:payments:payment-plans-global-count",
            kwargs={"business_area_slug": business_areas["afghanistan"].slug},
        ),
    }


def test_payment_plan_global_list_with_whole_business_area_access(
    create_user_role_with_permissions: Any,
    user_client: dict,
    business_areas: dict,
    global_urls: dict,
    payment_plans_data: dict,
) -> None:
    create_user_role_with_permissions(
        user=user_client["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=business_areas["afghanistan"],
        whole_business_area_access=True,
    )

    response = user_client["client"].get(global_urls["list_afghanistan"])
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 2

    response_count = user_client["client"].get(global_urls["count_afghanistan"])
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 2

    result_ids = [result["id"] for result in response_results]
    assert str(payment_plans_data["payment_plan_afghanistan1"].id) in result_ids
    assert str(payment_plans_data["payment_plan_afghanistan2"].id) in result_ids
    assert str(payment_plans_data["payment_plan_ukraine"].id) not in result_ids


def test_payment_plan_global_list_with_permissions_in_one_program(
    create_user_role_with_permissions: Any,
    user_client: dict,
    business_areas: dict,
    programs_and_cycles: dict,
    global_urls: dict,
    payment_plans_data: dict,
) -> None:
    create_user_role_with_permissions(
        user=user_client["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=business_areas["afghanistan"],
        program=programs_and_cycles["program_afghanistan1"],
    )

    response = user_client["client"].get(global_urls["list_afghanistan"])
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 1

    result_ids = [result["id"] for result in response_results]
    assert str(payment_plans_data["payment_plan_afghanistan1"].id) in result_ids
    assert str(payment_plans_data["payment_plan_afghanistan2"].id) not in result_ids
    assert str(payment_plans_data["payment_plan_ukraine"].id) not in result_ids


def test_payment_plan_global_list_with_permissions_in_multiple_programs(
    create_user_role_with_permissions: Any,
    user_client: dict,
    business_areas: dict,
    programs_and_cycles: dict,
    global_urls: dict,
    payment_plans_data: dict,
) -> None:
    create_user_role_with_permissions(
        user=user_client["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=business_areas["afghanistan"],
        program=programs_and_cycles["program_afghanistan1"],
    )
    create_user_role_with_permissions(
        user=user_client["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=business_areas["afghanistan"],
        program=programs_and_cycles["program_afghanistan2"],
    )

    response = user_client["client"].get(global_urls["list_afghanistan"])
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 2

    result_ids = [result["id"] for result in response_results]
    assert str(payment_plans_data["payment_plan_afghanistan1"].id) in result_ids
    assert str(payment_plans_data["payment_plan_afghanistan2"].id) in result_ids
    assert str(payment_plans_data["payment_plan_ukraine"].id) not in result_ids


@pytest.mark.parametrize(
    "permissions",
    [
        [],
        (Permissions.PROGRAMME_ACTIVATE,),
    ],
)
def test_payment_plan_global_list_without_permissions(
    permissions: list,
    create_user_role_with_permissions: Any,
    user_client: dict,
    business_areas: dict,
    global_urls: dict,
) -> None:
    create_user_role_with_permissions(
        user=user_client["user"],
        permissions=permissions,
        business_area=business_areas["afghanistan"],
        whole_business_area_access=True,
    )

    response = user_client["client"].get(global_urls["list_afghanistan"])
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_payment_plan_global_count_endpoint(
    create_user_role_with_permissions: Any,
    user_client: dict,
    business_areas: dict,
    global_urls: dict,
    payment_plans_data: dict,
) -> None:
    create_user_role_with_permissions(
        user=user_client["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=business_areas["afghanistan"],
        whole_business_area_access=True,
    )

    response = user_client["client"].get(global_urls["count_afghanistan"])
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 2


def test_payment_plan_global_list_ukraine(
    create_user_role_with_permissions: Any,
    user_client: dict,
    business_areas: dict,
    global_urls: dict,
    payment_plans_data: dict,
) -> None:
    create_user_role_with_permissions(
        user=user_client["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=business_areas["ukraine"],
        whole_business_area_access=True,
    )

    response = user_client["client"].get(global_urls["list_ukraine"])
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 1

    result_ids = [result["id"] for result in response_results]
    assert str(payment_plans_data["payment_plan_ukraine"].id) in result_ids
    assert str(payment_plans_data["payment_plan_afghanistan1"].id) not in result_ids
    assert str(payment_plans_data["payment_plan_afghanistan2"].id) not in result_ids


@pytest.fixture
def office_search_setup(api_client: Any):
    business_area = BusinessAreaFactory(slug="afghanistan")
    global_url = reverse(
        "api:payments:payment-plans-global-list",
        kwargs={"business_area_slug": business_area.slug},
    )
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    program_cycle = ProgramCycleFactory(program=program)

    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

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

    payment_plan1 = PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
    )
    payment_plan2 = PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
    )
    payment_plan3 = PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
    )

    payment1 = PaymentFactory(
        parent=payment_plan1,
        household=household1,
        head_of_household=individuals1[0],
        collector=individuals1[0],
        program=program,
    )
    payment2 = PaymentFactory(
        parent=payment_plan2,
        household=household2,
        head_of_household=individuals2[0],
        collector=individuals2[0],
        program=program,
    )
    payment3 = PaymentFactory(
        parent=payment_plan3,
        household=household3,
        head_of_household=individuals3[0],
        collector=individuals3[0],
        program=program,
    )

    return {
        "global_url": global_url,
        "business_area": business_area,
        "program": program,
        "user": user,
        "client": client,
        "payment_plan1": payment_plan1,
        "payment_plan2": payment_plan2,
        "payment_plan3": payment_plan3,
        "household1": household1,
        "household2": household2,
        "household3": household3,
        "individuals1": individuals1,
        "individuals2": individuals2,
        "individuals3": individuals3,
        "payment1": payment1,
        "payment2": payment2,
        "payment3": payment3,
    }


def test_search_by_payment_plan_unicef_id(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=office_search_setup["business_area"],
        whole_business_area_access=True,
    )

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": office_search_setup["payment_plan1"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment_plan1"].id)


def test_search_by_household_unicef_id(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=office_search_setup["business_area"],
        whole_business_area_access=True,
    )

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": office_search_setup["household2"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment_plan2"].id)


def test_search_by_individual_unicef_id(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=office_search_setup["business_area"],
        whole_business_area_access=True,
    )

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": office_search_setup["individuals3"][0].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment_plan3"].id)


def test_search_by_payment_unicef_id(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=office_search_setup["business_area"],
        whole_business_area_access=True,
    )

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": office_search_setup["payment1"].unicef_id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment_plan1"].id)


def test_search_by_phone_number(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=office_search_setup["business_area"],
        whole_business_area_access=True,
    )

    office_search_setup["individuals1"][0].phone_no = "+1234567890"
    office_search_setup["individuals1"][0].save()

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": "+1234567890"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment_plan1"].id)


def test_search_by_phone_number_alternative(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=office_search_setup["business_area"],
        whole_business_area_access=True,
    )

    office_search_setup["individuals2"][0].phone_no_alternative = "+9876543210"
    office_search_setup["individuals2"][0].save()

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": "+9876543210"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment_plan2"].id)


def test_search_by_individual_name(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=office_search_setup["business_area"],
        whole_business_area_access=True,
    )

    office_search_setup["individuals3"][0].full_name = "UniqueAlicePlan"
    office_search_setup["individuals3"][0].save()

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": "UniqueAlicePlan"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment_plan3"].id)


def test_search_with_active_programs_filter(
    create_user_role_with_permissions: Any,
    office_search_setup: dict,
) -> None:
    create_user_role_with_permissions(
        user=office_search_setup["user"],
        permissions=[Permissions.PM_VIEW_LIST],
        business_area=office_search_setup["business_area"],
        whole_business_area_access=True,
    )

    finished_program = ProgramFactory(business_area=office_search_setup["business_area"], status=Program.FINISHED)
    finished_program_cycle = ProgramCycleFactory(program=finished_program)
    finished_payment_plan = PaymentPlanFactory(
        program_cycle=finished_program_cycle,
        status=PaymentPlan.Status.ACCEPTED,
        business_area=office_search_setup["business_area"],
    )
    finished_household = HouseholdFactory(
        business_area=office_search_setup["business_area"],
        program=finished_program,
    )
    finished_individuals = [finished_household.head_of_household]
    PaymentFactory(
        parent=finished_payment_plan,
        household=finished_household,
        head_of_household=finished_individuals[0],
        collector=finished_individuals[0],
        program=finished_program,
    )

    office_search_setup["individuals1"][0].phone_no = "+5553334444"
    office_search_setup["individuals1"][0].save()

    finished_individuals[0].phone_no = "+5553334444"
    finished_individuals[0].save()

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": "+5553334444", "active_programs_only": "false"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [result["id"] for result in response.data["results"]]
    assert str(office_search_setup["payment_plan1"].id) in result_ids
    assert str(finished_payment_plan.id) in result_ids

    response = office_search_setup["client"].get(
        office_search_setup["global_url"],
        {"office_search": "+5553334444", "active_programs_only": "true"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(office_search_setup["payment_plan1"].id)
