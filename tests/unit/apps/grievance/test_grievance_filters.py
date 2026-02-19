"""Tests for grievance ticket filters."""

from datetime import datetime
from typing import Any, Callable

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
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketComplaintDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketPaymentVerificationDetailsFactory,
    TicketSensitiveDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
)
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory
from extras.test_utils.factories.sanction_list import SanctionListIndividualFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.constants import (
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    URGENCY_URGENT,
    URGENCY_VERY_URGENT,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.models import HEAD, BusinessArea, Partner, PaymentVerification, PaymentVerificationPlan, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="AFG")


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def program_afghanistan1(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )


@pytest.fixture
def program_afghanistan2(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.FINISHED,
        name="program afghanistan 2",
    )


@pytest.fixture
def user(partner: Partner, afghanistan: BusinessArea, create_user_role_with_permissions: Callable) -> User:
    user = UserFactory(partner=partner, id="45e3ffde-6a75-4799-a036-e2b00b93e94a")
    create_user_role_with_permissions(
        user=user,
        permissions=[
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
        ],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    return user


@pytest.fixture
def user2(partner: Partner) -> User:
    return UserFactory(partner=partner, id="a6f4652c-7ade-4b51-b1f2-0d28cfc08346")


@pytest.fixture
def areas() -> dict:
    country = CountryFactory()
    admin_type = AreaTypeFactory(country=country, area_level=1)
    area1 = AreaFactory(
        parent=None,
        p_code="AF01",
        area_type=admin_type,
        id="d19f0e24-a411-4f0e-9404-3d54b5a5c578",
    )
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type)
    area2_2 = AreaFactory(parent=None, p_code="AF010101", area_type=admin_type)
    area_other = AreaFactory(parent=None, p_code="AF02", area_type=admin_type)

    return {
        "country": country,
        "admin_type": admin_type,
        "area1": area1,
        "area2": area2,
        "area2_2": area2_2,
        "area_other": area_other,
    }


@pytest.fixture
def households_and_individuals(
    afghanistan: BusinessArea,
    program_afghanistan1: Program,
    areas: dict,
) -> dict:
    rdi = RegistrationDataImportFactory(business_area=afghanistan)

    individual1_1 = IndividualFactory(
        business_area=afghanistan,
        program=program_afghanistan1,
        registration_data_import=rdi,
        household=None,
        preferred_language="pl",
        full_name="Tom Smith",
        relationship=HEAD,
    )
    household1 = HouseholdFactory(
        business_area=afghanistan,
        program=program_afghanistan1,
        registration_data_import=rdi,
        head_of_household=individual1_1,
        admin1=areas["area1"],
        admin2=areas["area2"],
        country=areas["country"],
        country_origin=areas["country"],
    )
    household1.unicef_id = "HH-0001"
    household1.save()
    individual1_1.household = household1
    individual1_1.save()
    individual1_2 = IndividualFactory(
        business_area=afghanistan,
        program=program_afghanistan1,
        registration_data_import=rdi,
        household=household1,
        preferred_language="pl",
    )

    individual2_1 = IndividualFactory(
        id="b1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e6",
        business_area=afghanistan,
        program=program_afghanistan1,
        registration_data_import=rdi,
        household=None,
        preferred_language="en",
        relationship=HEAD,
    )
    household2 = HouseholdFactory(
        id="7e6a41c1-0fbd-4f91-98ba-2c6a7da8dbe1",
        business_area=afghanistan,
        program=program_afghanistan1,
        registration_data_import=rdi,
        head_of_household=individual2_1,
        admin1=areas["area1"],
        admin2=areas["area2_2"],
        country=areas["country"],
        country_origin=areas["country"],
    )
    individual2_1.household = household2
    individual2_1.unicef_id = "IND-0002"
    individual2_1.save()
    individual2_2 = IndividualFactory(
        business_area=afghanistan,
        program=program_afghanistan1,
        registration_data_import=rdi,
        household=household2,
        preferred_language="en",
    )

    # Create documents
    doc_type_birth = DocumentTypeFactory(key="birth_certificate")
    doc_type_drivers = DocumentTypeFactory(key="drivers_license")

    DocumentFactory(
        document_number="111222333",
        type=doc_type_birth,
        individual=individual1_1,
    )
    DocumentFactory(
        document_number="55555555",
        type=doc_type_drivers,
        individual=individual1_1,
    )
    DocumentFactory(
        document_number="55555555",
        type=doc_type_birth,
        individual=individual2_1,
    )
    DocumentFactory(
        document_number="111222333",
        type=doc_type_drivers,
        individual=individual2_1,
    )

    return {
        "household1": household1,
        "individuals1": [individual1_1, individual1_2],
        "household2": household2,
        "individuals2": [individual2_1, individual2_2],
    }


@pytest.fixture
def tickets(
    afghanistan: BusinessArea,
    program_afghanistan1: Program,
    program_afghanistan2: Program,
    households_and_individuals: dict,
    areas: dict,
    user: User,
    user2: User,
) -> dict:
    data = households_and_individuals

    user_modified = timezone.make_aware(datetime(year=2021, month=8, day=22))

    # Ticket 0: Needs Adjudication ticket, not cross area, program1
    ticket0 = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=areas["area2"],
        language="Polish",
        consent=True,
        description="Needs Adjudication ticket, not cross area, program1",
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        status=GrievanceTicket.STATUS_NEW,
        created_by=user,
        assigned_to=user,
        user_modified=user_modified,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        priority=PRIORITY_HIGH,
        urgency=URGENCY_URGENT,
    )
    ticket0.unicef_id = "GRV-0001"
    ticket0.save()
    ticket0.programs.add(program_afghanistan1)

    # Ticket 1: Needs Adjudication ticket, cross area, program1
    ticket1 = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=areas["area2_2"],
        language="Polish",
        consent=True,
        description="Needs Adjudication ticket, cross area, program1",
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        status=GrievanceTicket.STATUS_CLOSED,
        created_by=user,
        assigned_to=user,
        user_modified=user_modified,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        priority=PRIORITY_MEDIUM,
        urgency=URGENCY_URGENT,
    )
    ticket1.programs.add(program_afghanistan1)

    # Ticket 2: Payment Verification ticket, program1
    ticket2 = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=None,
        language="Polish, English",
        consent=True,
        description="Payment Verification ticket, program1",
        category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        status=GrievanceTicket.STATUS_IN_PROGRESS,
        created_by=user,
        assigned_to=user,
        user_modified=user_modified,
        issue_type=None,
    )
    ticket2.programs.add(program_afghanistan1)

    # Ticket 3: Payment Verification ticket, program2
    ticket3 = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=None,
        language="Polish, English",
        consent=True,
        description="Payment Verification ticket, program2",
        category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        status=GrievanceTicket.STATUS_IN_PROGRESS,
        created_by=user,
        assigned_to=user,
        user_modified=user_modified,
        issue_type=None,
    )
    ticket3.programs.add(program_afghanistan2)

    # Ticket 4: Complaint ticket, program1
    ticket4 = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=None,
        language="Polish, English",
        consent=True,
        description="Complaint ticket, program1",
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        status=GrievanceTicket.STATUS_IN_PROGRESS,
        created_by=user,
        assigned_to=user,
        user_modified=user_modified,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
    )
    ticket4.programs.add(program_afghanistan1)

    # Ticket 5: Data Change ticket, program2
    ticket5 = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=areas["area2"],
        language="Polish",
        consent=True,
        description="Data Change ticket, program2",
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        status=GrievanceTicket.STATUS_NEW,
        created_by=user2,
        assigned_to=user,
        user_modified=user_modified,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        urgency=URGENCY_VERY_URGENT,
    )
    ticket5.programs.add(program_afghanistan2)

    # Ticket 6: Sensitive ticket, program1
    ticket6 = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=areas["area2"],
        language="English",
        consent=True,
        description="Sensitive ticket, program1",
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        status=GrievanceTicket.STATUS_ON_HOLD,
        created_by=user,
        assigned_to=user,
        user_modified=user_modified,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )
    ticket6.programs.add(program_afghanistan1)

    # Ticket 7: Sensitive ticket, program2
    ticket7 = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=areas["area2"],
        language="Polish, English",
        consent=True,
        description="Sensitive ticket, program2",
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        status=GrievanceTicket.STATUS_IN_PROGRESS,
        created_by=user,
        assigned_to=user2,
        user_modified=user_modified,
        issue_type=GrievanceTicket.ISSUE_TYPE_HARASSMENT,
        priority=PRIORITY_MEDIUM,
    )
    ticket7.programs.add(program_afghanistan2)

    # Ticket 8: System Flagging ticket, program1
    ticket8 = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=areas["area1"],
        language="Polish, English",
        consent=True,
        description="System Flagging ticket, program1",
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        status=GrievanceTicket.STATUS_CLOSED,
        created_by=user,
        assigned_to=user,
        user_modified=user_modified,
        issue_type=None,
    )
    ticket8.programs.add(program_afghanistan1)

    created_at_dates = [
        timezone.make_aware(datetime(year=2020, month=3, day=12)),
        timezone.make_aware(datetime(year=2020, month=3, day=13)),
        timezone.make_aware(datetime(year=2020, month=3, day=14)),
        timezone.make_aware(datetime(year=2020, month=7, day=12)),
        timezone.make_aware(datetime(year=2020, month=8, day=22)),
        timezone.make_aware(datetime(year=2020, month=8, day=23)),
        timezone.make_aware(datetime(year=2020, month=8, day=24)),
        timezone.make_aware(datetime(year=2020, month=8, day=25)),
        timezone.make_aware(datetime(year=2020, month=8, day=26)),
    ]
    for ticket, date in zip(
        [ticket0, ticket1, ticket2, ticket3, ticket4, ticket5, ticket6, ticket7, ticket8], created_at_dates, strict=True
    ):
        ticket.created_at = date
        ticket.save(update_fields=["created_at"])

    # Create ticket details
    needs_adjudication_details_0 = TicketNeedsAdjudicationDetailsFactory(
        ticket=ticket0,
        golden_records_individual=data["individuals1"][0],
        possible_duplicate=data["individuals1"][1],
        score_min=100,
        score_max=200,
        extra_data={
            "golden_records": [
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(data["individuals1"][0].pk),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": 1.2,
                    "duplicate": False,
                    "distinct": True,
                }
            ],
            "possible_duplicate": [
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(data["individuals1"][1].pk),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": 2.0,
                    "duplicate": True,
                    "distinct": False,
                }
            ],
        },
    )
    needs_adjudication_details_0.possible_duplicates.set([data["individuals1"][1]])
    needs_adjudication_details_0.populate_cross_area_flag()

    needs_adjudication_details_1 = TicketNeedsAdjudicationDetailsFactory(
        ticket=ticket1,
        golden_records_individual=data["individuals1"][0],
        possible_duplicate=data["individuals2"][0],
        score_min=50,
        score_max=150,
        extra_data={
            "golden_records": [
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(data["individuals1"][0].pk),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": 1.2,
                    "duplicate": False,
                    "distinct": True,
                }
            ],
            "possible_duplicate": [
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(data["individuals2"][0].pk),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": 2.0,
                    "duplicate": True,
                    "distinct": False,
                }
            ],
        },
    )
    needs_adjudication_details_1.possible_duplicates.set([data["individuals2"][0]])
    needs_adjudication_details_1.populate_cross_area_flag()

    # Create payment related objects
    program_cycle = ProgramCycleFactory(program=program_afghanistan1)
    payment_plan = PaymentPlanFactory(
        id="689ba2ea-8ffb-4787-98e4-ae12797ee4da",
        name="TEST",
        business_area=afghanistan,
        program_cycle=program_cycle,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    payment_verification_plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        status=PaymentVerificationPlan.STATUS_ACTIVE,
    )
    financial_service_provider1 = FinancialServiceProviderFactory(name="Filter Value")
    payment1 = PaymentFactory(
        parent=payment_plan,
        household=data["household1"],
        currency="PLN",
        head_of_household=data["individuals1"][0],
        financial_service_provider=financial_service_provider1,
        program=program_afghanistan1,
        collector=data["individuals1"][0],
    )
    payment_verification1 = PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment1,
        status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        received_amount=10,
    )
    payment_verification_details_1 = TicketPaymentVerificationDetailsFactory(
        ticket=ticket2,
        approve_status=True,
        new_status=PaymentVerification.STATUS_RECEIVED,
        old_received_amount=0,
        new_received_amount=20,
        payment_verification_status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        payment_verification=payment_verification1,
    )

    payment_plan2 = PaymentPlanFactory(
        name="TEST2",
        business_area=afghanistan,
        program_cycle=program_cycle,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan2)
    payment_verification_plan2 = PaymentVerificationPlanFactory(
        payment_plan=payment_plan2,
        status=PaymentVerificationPlan.STATUS_ACTIVE,
    )
    financial_service_provider2 = FinancialServiceProviderFactory(name="Value")
    payment2 = PaymentFactory(
        id="f1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e6",
        parent=payment_plan,
        household=data["household2"],
        head_of_household=data["individuals2"][0],
        currency="PLN",
        program=program_afghanistan1,
        collector=data["individuals2"][0],
    )
    payment_verification2 = PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan2,
        payment=payment2,
        status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        received_amount=10,
    )
    payment_verification_details_2 = TicketPaymentVerificationDetailsFactory(
        ticket=ticket3,
        approve_status=True,
        new_status=PaymentVerification.STATUS_RECEIVED,
        old_received_amount=0,
        new_received_amount=20,
        payment_verification_status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        payment_verification=payment_verification2,
    )

    complaint_details = TicketComplaintDetailsFactory(
        ticket=ticket4,
        household=data["household2"],
        individual=data["individuals2"][0],
        payment=payment2,
    )

    individual_data_update_details = TicketIndividualDataUpdateDetailsFactory(
        ticket=ticket5,
        individual=data["individuals2"][0],
    )

    sensitive_details_1 = TicketSensitiveDetailsFactory(
        ticket=ticket6,
        household=data["household1"],
        individual=data["individuals1"][0],
    )

    sensitive_details_2 = TicketSensitiveDetailsFactory(
        ticket=ticket7,
        household=data["household2"],
        individual=data["individuals2"][0],
    )

    sanction_list_individual = SanctionListIndividualFactory(full_name="Sanction Individual")
    system_flagging_details = TicketSystemFlaggingDetailsFactory(
        ticket=ticket8,
        golden_records_individual=data["individuals2"][0],
        sanction_list_individual=sanction_list_individual,
    )

    for ticket in [ticket0, ticket1, ticket2, ticket3, ticket4, ticket5, ticket6, ticket7, ticket8]:
        ticket.refresh_from_db()

    return {
        "tickets": [ticket0, ticket1, ticket2, ticket3, ticket4, ticket5, ticket6, ticket7, ticket8],
        "needs_adjudication_details_0": needs_adjudication_details_0,
        "needs_adjudication_details_1": needs_adjudication_details_1,
        "payment_verification_details_1": payment_verification_details_1,
        "payment_verification_details_2": payment_verification_details_2,
        "complaint_details": complaint_details,
        "individual_data_update_details": individual_data_update_details,
        "sensitive_details_1": sensitive_details_1,
        "sensitive_details_2": sensitive_details_2,
        "system_flagging_details": system_flagging_details,
        "financial_service_provider1": financial_service_provider1,
        "financial_service_provider2": financial_service_provider2,
        "payment1": payment1,
        "payment2": payment2,
        "payment_plan": payment_plan,
    }


@pytest.fixture
def list_url(afghanistan: BusinessArea, program_afghanistan1: Program) -> str:
    return reverse(
        "api:grievance:grievance-tickets-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program_afghanistan1.slug,
        },
    )


@pytest.fixture
def list_global_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-list",
        kwargs={"business_area_slug": afghanistan.slug},
    )


def _test_filter(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    filter_name: str,
    filter_value: Any,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    client = api_client(user)
    response_for_global = client.get(list_global_url, {filter_name: filter_value})
    response_for_program = client.get(list_url, {filter_name: filter_value})
    for response, expected_count in [
        (response_for_program, expected_count_for_program),
        (response_for_global, expected_count_for_global),
    ]:
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_count


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("Filter", 1, 1),
        ("Not", 0, 0),
        ("", 6, 9),
    ],
)
def test_filter_by_fsp(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "fsp",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("pl", 3, 3),
        ("en", 2, 4),
        ("", 6, 9),
    ],
)
def test_filter_by_preferred_language(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "preferred_language",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("system", 4, 5),
        ("user", 2, 4),
        ("", 6, 9),
    ],
)
def test_filter_by_grievance_type(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "grievance_type",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("active", 4, 7),
        ("", 6, 9),
    ],
)
def test_filter_by_grievance_status(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "grievance_status",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value1", "filter_value2", "expected_count_for_program", "expected_count_for_global"),
    [
        ("drivers_license", "111222333", 2, 5),
        ("birth_certificate", "55555555", 2, 5),
        ("birth_certificate", "111222333", 4, 4),
        ("drivers_license", "55555555", 4, 4),
        ("", "111222333", 0, 0),
    ],
)
def test_filter_by_document_number_and_document_type(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value1: str,
    filter_value2: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    client = api_client(user)
    response_for_global = client.get(
        list_global_url,
        {"document_type": filter_value1, "document_number": filter_value2},
    )
    response_for_program = client.get(
        list_url,
        {"document_type": filter_value1, "document_number": filter_value2},
    )
    for response, expected_count in [
        (response_for_program, expected_count_for_program),
        (response_for_global, expected_count_for_global),
    ]:
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_count


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        (0, 4, 6),
        (1, 1, 1),
        (2, 1, 2),
        (3, 0, 0),
    ],
)
def test_filter_by_priority(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: int,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "priority",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        (0, 4, 6),
        (1, 0, 1),
        (2, 2, 2),
        (3, 0, 0),
    ],
)
def test_filter_by_urgency(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: int,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "urgency",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("HH-0001", 4, 4),
        ("HH-990808", 0, 0),
    ],
)
def test_filter_by_household_unicef_id(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    households_and_individuals: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "household",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("7e6a41c1-0fbd-4f91-98ba-2c6a7da8dbe1", 2, 5),
        ("7e6a41c1-0fbd-4f91-98ba-2c6a7da8dbe2", 0, 0),
    ],
)
def test_filter_by_household_id(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    households_and_individuals: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "household_id",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("b1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e6", 1, 4),
        ("b1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e8", 0, 0),
    ],
)
def test_filter_by_individual_id(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    households_and_individuals: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "individual_id",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        (
            "f1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e6,f1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e0",
            1,
            1,
        ),
        ("f1c2d3e4-f5a6-7b8c-9d0e-f1a2b3c4d5e0", 0, 0),
    ],
)
def test_filter_by_payment_record_ids(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "payment_record_ids",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [(8, 2, 2), (3, 1, 2)],
)
def test_filter_by_category(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: int,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "category",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [(24, 2, 2), (1, 1, 1)],
)
def test_filter_by_issue_type(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: int,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "issue_type",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        (3, 2, 4),
        (6, 2, 2),
        ([3, 6], 4, 6),
    ],
)
def test_filter_by_status(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: int,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "status",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        (50, 2, 2),
        (80, 1, 1),
    ],
)
def test_filter_by_score_min(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: int,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "score_min",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        (200, 2, 2),
        (180, 1, 1),
    ],
)
def test_filter_by_score_max(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: int,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "score_max",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("d19f0e24-a411-4f0e-9404-3d54b5a5c578", 2, 4),
        ("d19f0e24-a411-4f0e-9404-3d54b5a5c579", 0, 0),
    ],
)
def test_filter_by_admin1(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "admin1",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("45e3ffde-6a75-4799-a036-e2b00b93e94a", 6, 8),
        ("a6f4652c-7ade-4b51-b1f2-0d28cfc08346", 0, 1),
    ],
)
def test_filter_by_assigned_to(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "assigned_to",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("689ba2ea-8ffb-4787-98e4-ae12797ee4da", 1, 1),
        ("689ba2ea-8ffb-4787-98e4-ae12797ee4d1", 0, 0),
    ],
)
def test_filter_by_cash_plan(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        "cash_plan",
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    (
        "filter_expression",
        "filter_value",
        "expected_count_for_program",
        "expected_count_for_global",
    ),
    [
        ("created_at_after", "2020-07-15", 3, 5),
        ("created_at_before", "2020-07-15", 3, 4),
    ],
)
def test_filter_by_created_at(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_expression: str,
    filter_value: int,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    _test_filter(
        api_client,
        user,
        list_url,
        list_global_url,
        filter_expression,
        filter_value,
        expected_count_for_program,
        expected_count_for_global,
    )


@pytest.mark.parametrize(
    ("is_filtered", "expected_count"),
    [
        (True, 6),
        (False, 9),
    ],
)
def test_filter_by_program(
    api_client: Any,
    user: User,
    list_global_url: str,
    tickets: dict,
    program_afghanistan1: Program,
    is_filtered: bool,
    expected_count: int,
) -> None:
    filter_value = program_afghanistan1.slug if is_filtered else ""
    client = api_client(user)
    response = client.get(list_global_url, {"program": filter_value})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == expected_count


@pytest.mark.parametrize(
    ("filter_value", "expected_count"),
    [
        (True, 6),
        (False, 3),
    ],
)
def test_filter_by_program_status(
    api_client: Any,
    user: User,
    list_global_url: str,
    tickets: dict,
    filter_value: bool,
    expected_count: int,
) -> None:
    client = api_client(user)
    response = client.get(list_global_url, {"is_active_program": filter_value})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == expected_count


@pytest.mark.parametrize(
    (
        "has_cross_area_filter_permission",
        "has_full_area_access",
        "filter_value",
        "is_filtered_for_program",
        "is_filtered_for_global",
    ),
    [
        (False, False, False, False, False),
        (False, False, True, False, False),
        (False, True, True, False, False),
        (True, False, False, False, False),
        (True, False, True, False, True),
        (True, True, True, True, True),
    ],
)
def test_filter_by_cross_area(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    areas: dict,
    partner: Partner,
    program_afghanistan1: Program,
    afghanistan: BusinessArea,
    has_cross_area_filter_permission: bool,
    has_full_area_access: bool,
    filter_value: bool,
    is_filtered_for_program: bool,
    is_filtered_for_global: bool,
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    if has_cross_area_filter_permission:
        create_user_role_with_permissions(
            user=user,
            permissions=[Permissions.GRIEVANCES_CROSS_AREA_FILTER],
            business_area=afghanistan,
            whole_business_area_access=True,
        )
    if not has_full_area_access:
        set_admin_area_limits_in_program(
            partner,
            program_afghanistan1,
            [areas["area1"], areas["area2"], areas["area2_2"]],
        )

    client = api_client(user)
    response_for_program = client.get(
        list_url,
        {
            "is_cross_area": filter_value,
            "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        },
    )
    response_for_global = client.get(
        list_global_url,
        {
            "is_cross_area": filter_value,
            "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        },
    )

    for response, is_filtered in [
        (response_for_program, is_filtered_for_program),
        (response_for_global, is_filtered_for_global),
    ]:
        assert response.status_code == status.HTTP_200_OK
        if is_filtered:
            response_results = response.data["results"]
            assert len(response_results) == 1
            assert response_results[0]["id"] == str(tickets["tickets"][1].id)
        else:
            response_results = response.data["results"]
            assert len(response_results) == 2
            result_ids = [result["id"] for result in response_results]
            assert str(tickets["tickets"][0].id) in result_ids
            assert str(tickets["tickets"][1].id) in result_ids


@pytest.mark.parametrize(
    ("filter_value", "expected_count_for_program", "expected_count_for_global"),
    [
        ("GRV-0001", 1, 1),
        ("HH-0001", 4, 4),
        ("IND-0002", 2, 5),
        ("Tom", 4, 4),
        ("GRV-9918515", 0, 0),
        ("", 6, 9),
    ],
)
def test_search(
    api_client: Any,
    user: User,
    list_url: str,
    list_global_url: str,
    tickets: dict,
    filter_value: str,
    expected_count_for_program: int,
    expected_count_for_global: int,
) -> None:
    client = api_client(user)
    response_for_global = client.get(list_global_url, {"search": filter_value})
    response_for_program = client.get(list_url, {"search": filter_value})
    for response, expected_count in [
        (response_for_program, expected_count_for_program),
        (response_for_global, expected_count_for_global),
    ]:
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_count
