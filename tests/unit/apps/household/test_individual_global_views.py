from typing import Any, Callable

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
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramCycleFactory,
    ProgramFactory,
    SanctionListIndividualFactory,
    TicketDeleteIndividualDetailsFactory,
    TicketPaymentVerificationDetailsFactory,
    TicketSensitiveDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import to_choice_object
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.apps.household.const import (
    AGENCY_TYPE_CHOICES,
    DEDUPLICATION_BATCH_STATUS_CHOICE,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    INDIVIDUAL_FLAGS_CHOICES,
    INDIVIDUAL_STATUS_CHOICES,
    MARITAL_STATUS_CHOICE,
    OBSERVED_DISABILITY_CHOICE,
    RELATIONSHIP_CHOICE,
    ROLE_CHOICE,
    SEVERITY_OF_DISABILITY_CHOICES,
    SEX_CHOICE,
    WORK_STATUS_CHOICE,
)
from hope.models import AccountType, BusinessArea, DocumentType, FinancialInstitution, Individual, Program

pytestmark = pytest.mark.django_db


def _create_household_with_individuals(
    program: Program, business_area: BusinessArea, count: int = 2, **hh_kwargs: Any
) -> tuple[Any, list[Individual]]:
    hh = HouseholdFactory(program=program, business_area=business_area, **hh_kwargs)
    individuals = [hh.head_of_household]
    individuals.extend(
        IndividualFactory(
            household=hh,
            program=program,
            business_area=business_area,
            registration_data_import=hh.registration_data_import,
        )
        for _ in range(count - 1)
    )
    return hh, individuals


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def partner() -> Any:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Any) -> Any:
    return UserFactory(partner=partner)


@pytest.fixture
def client(api_client: Callable, user: Any) -> Any:
    return api_client(user)


@pytest.fixture
def documents() -> None:
    DocumentTypeFactory(key="passport", label="Passport")
    DocumentTypeFactory(key="id_card", label="ID Card")
    DocumentTypeFactory(key="birth_certificate", label="Birth Certificate")


def test_get_choices(
    documents: None,
    client: Any,
    user: Any,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user, permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], business_area=afghanistan
    )
    response = client.get(
        reverse("api:households:individuals-global-choices", kwargs={"business_area_slug": afghanistan.slug})
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "document_type_choices": [
            {"name": str(dt.label), "value": dt.key} for dt in DocumentType.objects.order_by("key")
        ],
        "sex_choices": to_choice_object(SEX_CHOICE),
        "flag_choices": to_choice_object(INDIVIDUAL_FLAGS_CHOICES),
        "status_choices": to_choice_object(INDIVIDUAL_STATUS_CHOICES),
        "deduplication_batch_status_choices": to_choice_object(DEDUPLICATION_BATCH_STATUS_CHOICE),
        "deduplication_golden_record_status_choices": to_choice_object(DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE),
        "relationship_choices": to_choice_object(RELATIONSHIP_CHOICE),
        "role_choices": to_choice_object(ROLE_CHOICE),
        "role_choices_for_grievance": [
            {"name": "Alternate collector", "value": "ALTERNATE"},
            {"name": "Primary collector", "value": "PRIMARY"},
            {"name": "No role", "value": "NO_ROLE"},
        ],
        "marital_status_choices": to_choice_object(MARITAL_STATUS_CHOICE),
        "identity_type_choices": to_choice_object(AGENCY_TYPE_CHOICES),
        "observed_disability_choices": to_choice_object(OBSERVED_DISABILITY_CHOICE),
        "severity_of_disability_choices": to_choice_object(SEVERITY_OF_DISABILITY_CHOICES),
        "work_status_choices": to_choice_object(WORK_STATUS_CHOICE),
        "account_type_choices": [{"name": x.label, "value": x.key} for x in AccountType.objects.all()],
        "account_financial_institution_choices": [
            {"name": x.name, "value": x.id} for x in FinancialInstitution.objects.all()
        ],
    }


@pytest.fixture
def global_context(client: Any, user: Any, partner: Any, afghanistan: BusinessArea) -> dict[str, Any]:
    ukraine = BusinessAreaFactory(name="Ukraine", slug="ukraine", code="4410")

    program_afghanistan1 = ProgramFactory(
        business_area=afghanistan, status=Program.ACTIVE, name="program afghanistan 1"
    )
    program_afghanistan2 = ProgramFactory(
        business_area=afghanistan, status=Program.ACTIVE, name="program afghanistan 2"
    )
    program_ukraine = ProgramFactory(business_area=ukraine, status=Program.ACTIVE)

    country = CountryFactory()
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
    area3 = AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_2)
    area4 = AreaFactory(parent=area3, p_code="AF01010101", area_type=admin_type_2)

    hh_af1, (ind_af1_1, ind_af1_2) = _create_household_with_individuals(
        program_afghanistan1, afghanistan, admin1=area1, admin2=area2, admin3=area3, admin4=area4
    )
    hh_af2, (ind_af2_1, ind_af2_2) = _create_household_with_individuals(
        program_afghanistan2, afghanistan, admin1=area1, admin2=area2, admin3=area3, admin4=area4
    )
    hh_ua, (ind_ua_1, ind_ua_2) = _create_household_with_individuals(
        program_ukraine, ukraine, admin1=area1, admin2=area2, admin3=area3, admin4=area4
    )

    return {
        "afghanistan": afghanistan,
        "ukraine": ukraine,
        "program_afghanistan1": program_afghanistan1,
        "program_afghanistan2": program_afghanistan2,
        "program_ukraine": program_ukraine,
        "partner": partner,
        "user": user,
        "client": client,
        "area1": area1,
        "area2": area2,
        "admin_type_1": admin_type_1,
        "hh_af1": hh_af1,
        "hh_af2": hh_af2,
        "hh_ua": hh_ua,
        "ind_af1_1": ind_af1_1,
        "ind_af1_2": ind_af1_2,
        "ind_af2_1": ind_af2_1,
        "ind_af2_2": ind_af2_2,
        "ind_ua_1": ind_ua_1,
        "ind_ua_2": ind_ua_2,
    }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
        ([Permissions.RDI_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
        ([Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], status.HTTP_403_FORBIDDEN),
    ],
)
def test_individual_global_list_permissions(
    global_context: dict,
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Callable,
) -> None:
    ctx = global_context
    create_user_role_with_permissions(
        user=ctx["user"], permissions=permissions, business_area=ctx["afghanistan"], whole_business_area_access=True
    )
    response = ctx["client"].get(
        reverse("api:households:individuals-global-list", kwargs={"business_area_slug": ctx["afghanistan"].slug})
    )
    assert response.status_code == expected_status


def test_individual_global_list(global_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = global_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        whole_business_area_access=True,
    )

    response = ctx["client"].get(
        reverse("api:households:individuals-global-list", kwargs={"business_area_slug": ctx["afghanistan"].slug})
    )
    assert response.status_code == status.HTTP_200_OK
    results = response.data["results"]
    assert len(results) == 4

    response_count = ctx["client"].get(
        reverse("api:households:individuals-global-count", kwargs={"business_area_slug": ctx["afghanistan"].slug})
    )
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 4

    result_ids = [r["id"] for r in results]
    assert str(ctx["ind_af1_1"].id) in result_ids
    assert str(ctx["ind_af1_2"].id) in result_ids
    assert str(ctx["ind_af2_1"].id) in result_ids
    assert str(ctx["ind_af2_2"].id) in result_ids
    assert str(ctx["ind_ua_1"].id) not in result_ids
    assert str(ctx["ind_ua_2"].id) not in result_ids

    for i, individual in enumerate([ctx["ind_af1_1"], ctx["ind_af1_2"], ctx["ind_af2_1"], ctx["ind_af2_2"]]):
        individual_result = results[i]
        assert individual_result["unicef_id"] == individual.unicef_id
        assert individual_result["full_name"] == individual.full_name
        assert individual_result["status"] == individual.status
        assert individual_result["relationship"] == individual.relationship
        assert individual_result["age"] == individual.age
        assert individual_result["sex"] == individual.sex
        assert individual_result["household"] == {
            "id": str(individual.household.id),
            "unicef_id": individual.household.unicef_id,
            "admin2": {"id": str(individual.household.admin2.id), "name": individual.household.admin2.name},
        }
        assert individual_result["program"] == {
            "id": str(individual.program.id),
            "name": individual.program.name,
            "code": individual.program.code,
        }
        assert individual_result["last_registration_date"] == f"{individual.last_registration_date:%Y-%m-%d}"


def test_individual_global_list_with_permissions_in_one_program(
    global_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = global_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program_afghanistan1"],
    )

    response = ctx["client"].get(
        reverse("api:households:individuals-global-list", kwargs={"business_area_slug": ctx["afghanistan"].slug})
    )
    assert response.status_code == status.HTTP_200_OK
    result_ids = [r["id"] for r in response.data["results"]]
    assert len(result_ids) == 2
    assert str(ctx["ind_af1_1"].id) in result_ids
    assert str(ctx["ind_af1_2"].id) in result_ids
    assert str(ctx["ind_af2_1"].id) not in result_ids
    assert str(ctx["ind_af2_2"].id) not in result_ids
    assert str(ctx["ind_ua_1"].id) not in result_ids
    assert str(ctx["ind_ua_2"].id) not in result_ids


def test_individual_global_list_area_limits(
    global_context: dict, create_user_role_with_permissions: Callable, set_admin_area_limits_in_program: Callable
) -> None:
    ctx = global_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        whole_business_area_access=True,
    )
    set_admin_area_limits_in_program(ctx["partner"], ctx["program_afghanistan2"], [ctx["area1"], ctx["area2"]])

    (
        household_afghanistan_without_areas,
        (individual_afghanistan_without_areas1, individual_afghanistan_without_areas2),
    ) = _create_household_with_individuals(ctx["program_afghanistan2"], ctx["afghanistan"])

    area_different = AreaFactory(parent=None, p_code="AF05", area_type=ctx["admin_type_1"])
    (
        household_afghanistan_different_areas,
        (individual_afghanistan_different_areas1, individual_afghanistan_different_areas2),
    ) = _create_household_with_individuals(
        ctx["program_afghanistan2"],
        ctx["afghanistan"],
        admin1=area_different,
        admin2=area_different,
        admin3=area_different,
        admin4=area_different,
    )

    response = ctx["client"].get(
        reverse("api:households:individuals-global-list", kwargs={"business_area_slug": ctx["afghanistan"].slug})
    )
    assert response.status_code == status.HTTP_200_OK
    result_ids = [r["id"] for r in response.data["results"]]
    assert len(result_ids) == 6
    assert str(ctx["ind_af1_1"].id) in result_ids
    assert str(ctx["ind_af1_2"].id) in result_ids
    assert str(ctx["ind_af2_1"].id) in result_ids
    assert str(ctx["ind_af2_2"].id) in result_ids
    assert str(individual_afghanistan_without_areas1.id) in result_ids
    assert str(individual_afghanistan_without_areas2.id) in result_ids
    assert str(individual_afghanistan_different_areas1.id) not in result_ids
    assert str(individual_afghanistan_different_areas2.id) not in result_ids
    assert str(ctx["ind_ua_1"].id) not in result_ids
    assert str(ctx["ind_ua_2"].id) not in result_ids


@pytest.fixture
def office_search_context(client: Any, user: Any, afghanistan: BusinessArea) -> dict[str, Any]:
    program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)

    hh1, individuals1 = _create_household_with_individuals(program, afghanistan)
    hh2, individuals2 = _create_household_with_individuals(program, afghanistan)
    hh3, individuals3 = _create_household_with_individuals(program, afghanistan)
    hh4, individuals4 = _create_household_with_individuals(program, afghanistan, count=1)

    program_cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(business_area=afghanistan, program_cycle=program_cycle)
    payment1 = PaymentFactory(
        parent=payment_plan,
        household=hh1,
        head_of_household=individuals1[0],
        collector=individuals1[0],
        program=program,
    )
    payment2 = PaymentFactory(
        parent=payment_plan,
        household=hh2,
        head_of_household=individuals2[0],
        collector=individuals2[0],
        program=program,
    )

    complaint_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
    )
    GrievanceComplaintTicketWithoutExtrasFactory(
        ticket=complaint_ticket, household=hh1, individual=individuals1[0], payment=None
    )

    sensitive_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )
    TicketSensitiveDetailsFactory(ticket=sensitive_ticket, household=hh2, individual=individuals2[0], payment=None)

    needs_adjudication_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
    )
    needs_adjudication_ticket.programs.add(program)
    needs_adjudication_details = TicketNeedsAdjudicationDetails.objects.create(
        ticket=needs_adjudication_ticket, golden_records_individual=individuals3[0]
    )
    needs_adjudication_details.possible_duplicates.add(individuals3[1])

    sanction_list_individual = SanctionListIndividualFactory()
    system_flagging_ticket = GrievanceTicketFactory(
        business_area=afghanistan, category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING, issue_type=None
    )
    system_flagging_ticket.programs.add(program)
    TicketSystemFlaggingDetailsFactory(
        ticket=system_flagging_ticket,
        golden_records_individual=individuals4[0],
        sanction_list_individual=sanction_list_individual,
    )

    delete_individual_ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
    )
    delete_individual_ticket.programs.add(program)
    TicketDeleteIndividualDetailsFactory(ticket=delete_individual_ticket, individual=individuals2[1])

    hh5, individuals5 = _create_household_with_individuals(program, afghanistan, count=1)
    payment3 = PaymentFactory(
        parent=payment_plan,
        household=hh5,
        head_of_household=individuals5[0],
        collector=individuals5[0],
        program=program,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    payment_verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)
    payment_verification = PaymentVerificationFactory(
        payment=payment3, payment_verification_plan=payment_verification_plan
    )
    payment_verification_ticket = GrievanceTicketFactory(
        business_area=afghanistan, category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION, issue_type=None
    )
    payment_verification_ticket.programs.add(program)
    TicketPaymentVerificationDetailsFactory(
        ticket=payment_verification_ticket, payment_verification=payment_verification
    )

    return {
        "afghanistan": afghanistan,
        "program": program,
        "user": user,
        "client": client,
        "hh1": hh1,
        "hh2": hh2,
        "hh3": hh3,
        "hh4": hh4,
        "hh5": hh5,
        "individuals1": individuals1,
        "individuals2": individuals2,
        "individuals3": individuals3,
        "individuals4": individuals4,
        "individuals5": individuals5,
        "payment_plan": payment_plan,
        "payment1": payment1,
        "payment2": payment2,
        "payment3": payment3,
        "complaint_ticket": complaint_ticket,
        "sensitive_ticket": sensitive_ticket,
        "needs_adjudication_ticket": needs_adjudication_ticket,
        "system_flagging_ticket": system_flagging_ticket,
        "delete_individual_ticket": delete_individual_ticket,
        "payment_verification_ticket": payment_verification_ticket,
    }


def _global_url(afghanistan: BusinessArea) -> str:
    return reverse("api:households:individuals-global-list", kwargs={"business_area_slug": afghanistan.slug})


def test_search_by_individual_unicef_id(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": ctx["individuals1"][0].unicef_id})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals1"][0].id)


def test_search_by_household_unicef_id(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": ctx["hh2"].unicef_id})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [r["id"] for r in response.data["results"]]
    assert str(ctx["individuals2"][0].id) in result_ids
    assert str(ctx["individuals2"][1].id) in result_ids


def test_search_by_payment_unicef_id(office_search_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": ctx["payment1"].unicef_id})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals1"][0].id)


def test_search_by_payment_plan_unicef_id(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["payment_plan"].refresh_from_db()
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": ctx["payment_plan"].unicef_id})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3
    result_ids = [r["id"] for r in response.data["results"]]
    assert str(ctx["individuals1"][0].id) in result_ids
    assert str(ctx["individuals2"][0].id) in result_ids
    assert str(ctx["individuals5"][0].id) in result_ids


def test_search_by_complaint_ticket_individual(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["complaint_ticket"].refresh_from_db()
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": ctx["complaint_ticket"].unicef_id})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals1"][0].id)


def test_search_by_sensitive_ticket_individual(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["sensitive_ticket"].refresh_from_db()
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": ctx["sensitive_ticket"].unicef_id})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals2"][0].id)


def test_search_by_needs_adjudication_multiple_individuals(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["needs_adjudication_ticket"].refresh_from_db()
    response = ctx["client"].get(
        _global_url(ctx["afghanistan"]), {"office_search": ctx["needs_adjudication_ticket"].unicef_id}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [r["id"] for r in response.data["results"]]
    assert str(ctx["individuals3"][0].id) in result_ids
    assert str(ctx["individuals3"][1].id) in result_ids


def test_search_by_grievance_unicef_id_not_found(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": "GRV-DOESNOTEXIST"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 0


def test_office_search_no_matching_prefix(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": "UNKNOWN-12345"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 0


def test_search_by_system_flagging_ticket(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["system_flagging_ticket"].refresh_from_db()
    response = ctx["client"].get(
        _global_url(ctx["afghanistan"]), {"office_search": ctx["system_flagging_ticket"].unicef_id}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals4"][0].id)


def test_search_by_delete_individual_ticket(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["delete_individual_ticket"].refresh_from_db()
    response = ctx["client"].get(
        _global_url(ctx["afghanistan"]), {"office_search": ctx["delete_individual_ticket"].unicef_id}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals2"][1].id)


def test_search_by_payment_verification_ticket(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["payment_verification_ticket"].refresh_from_db()
    response = ctx["client"].get(
        _global_url(ctx["afghanistan"]), {"office_search": ctx["payment_verification_ticket"].unicef_id}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals5"][0].id)


def test_search_by_phone_number(office_search_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["individuals1"][0].phone_no = "+1234567890"
    ctx["individuals1"][0].save()
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": "+1234567890"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals1"][0].id)


def test_search_by_phone_number_alternative(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["individuals2"][0].phone_no_alternative = "+9876543210"
    ctx["individuals2"][0].save()
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": "+9876543210"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals2"][0].id)


def test_search_by_full_name(office_search_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["individuals1"][0].full_name = "John Smith Doe"
    ctx["individuals1"][0].save()
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": "John Smith Doe"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals1"][0].id)


def test_search_by_given_name(office_search_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["individuals2"][0].given_name = "UniqueAlice"
    ctx["individuals2"][0].save()
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": "UniqueAlice"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals2"][0].id)


def test_search_by_family_name(office_search_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    ctx["individuals3"][0].family_name = "UniqueWilliams"
    ctx["individuals3"][0].save()
    response = ctx["client"].get(_global_url(ctx["afghanistan"]), {"office_search": "UniqueWilliams"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals3"][0].id)


def test_search_with_active_programs_filter(
    office_search_context: dict, create_user_role_with_permissions: Callable
) -> None:
    ctx = office_search_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        whole_business_area_access=True,
    )

    finished_program = ProgramFactory(business_area=ctx["afghanistan"], status=Program.FINISHED)
    finished_household, (finished_individual,) = _create_household_with_individuals(
        finished_program, ctx["afghanistan"], count=1
    )

    # Set same phone number for both active and finished program individuals
    ctx["individuals1"][0].phone_no = "+5551112222"
    ctx["individuals1"][0].save()
    finished_individual.phone_no = "+5551112222"
    finished_individual.save()

    # First, search WITHOUT active_programs filter - should return both individuals
    response = ctx["client"].get(
        _global_url(ctx["afghanistan"]), {"office_search": "+5551112222", "active_programs_only": "false"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    result_ids = [r["id"] for r in response.data["results"]]
    assert str(ctx["individuals1"][0].id) in result_ids
    assert str(finished_individual.id) in result_ids

    # Now search WITH active_programs_only filter - should only return active program individual
    response = ctx["client"].get(
        _global_url(ctx["afghanistan"]), {"office_search": "+5551112222", "active_programs_only": "true"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(ctx["individuals1"][0].id)
