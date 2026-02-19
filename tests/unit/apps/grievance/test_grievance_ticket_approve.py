from datetime import date
from typing import Any, Callable

from django.core.files.base import ContentFile
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    TicketAddIndividualDetailsFactory,
    TicketDeleteHouseholdDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketPaymentVerificationDetailsFactory,
    UserFactory,
)
from extras.test_utils.factories.account import AdminAreaLimitedToFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_CHOICE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    SINGLE,
)
from hope.models import (
    Area,
    AreaType,
    BusinessArea,
    Country,
    DocumentType,
    Partner,
    PaymentVerification,
    PaymentVerificationPlan,
    Program,
    User,
)

pytestmark = pytest.mark.django_db()


@pytest.fixture
def afghanistan() -> BusinessArea:
    CountryFactory(name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004")
    CountryFactory(name="Poland", short_name="Poland", iso_code2="PL", iso_code3="POL", iso_num="0616")
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def document_types() -> None:
    identification_type_choice = tuple((doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE)
    document_types = []
    for doc_type, label in identification_type_choice:
        document_types.append(DocumentType(label=label, key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[doc_type]))
    DocumentType.objects.bulk_create(document_types, ignore_conflicts=True)


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def user2(partner: Partner) -> User:
    return UserFactory(first_name="SecondUser", partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    program = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )
    ProgramCycleFactory(program=program)
    return program


@pytest.fixture
def area_type(afghanistan: BusinessArea) -> AreaType:
    return AreaTypeFactory(
        name="Admin type one",
        country=Country.objects.get(name="Afghanistan"),
        area_level=2,
    )


@pytest.fixture
def area1(area_type: AreaType) -> Area:
    return AreaFactory(name="City Test", area_type=area_type, p_code="dffgh565556")


@pytest.fixture
def household_one(afghanistan: BusinessArea, program: Program, document_types: None) -> Any:
    first_individual = IndividualFactory(
        full_name="Benjamin Butler",
        given_name="Benjamin",
        family_name="Butler",
        phone_no="(953)682-4596",
        birth_date="1943-07-30",
        business_area=afghanistan,
        program=program,
        household=None,
    )

    household = HouseholdFactory(
        size=3,
        business_area=afghanistan,
        program=program,
        head_of_household=first_individual,
    )
    first_individual.household = household
    first_individual.save()

    second_individual = IndividualFactory(
        full_name="Robin Ford",
        given_name="Robin",
        family_name="Ford",
        phone_no="+18663567905",
        birth_date="1946-02-15",
        household=household,
        program=program,
    )

    national_id_type = DocumentType.objects.get(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID])
    birth_certificate_type = DocumentType.objects.get(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]
    )
    country_pol = Country.objects.get(iso_code2="PL")

    national_id = DocumentFactory(
        type=national_id_type,
        document_number="789-789-645",
        individual=first_individual,
        country=country_pol,
    )
    birth_certificate = DocumentFactory(
        type=birth_certificate_type,
        document_number="ITY8456",
        individual=first_individual,
        country=country_pol,
    )

    household.national_id = national_id
    household.birth_certificate = birth_certificate
    household.individuals_list = [first_individual, second_individual]

    return household


@pytest.fixture
def add_individual_ticket(
    afghanistan: BusinessArea, program: Program, area1: Area, household_one: Any
) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        admin2=area1,
        business_area=afghanistan,
    )
    ticket.programs.set([program])
    TicketAddIndividualDetailsFactory(
        ticket=ticket,
        household=household_one,
        individual_data={
            "given_name": "Test",
            "full_name": "Test Example",
            "family_name": "Example",
            "sex": "MALE",
            "birth_date": date(year=1980, month=2, day=1).isoformat(),
            "marital_status": SINGLE,
            "documents": [
                {
                    "country": "POL",
                    "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                    "number": "123-XYZ-321",
                },
                {
                    "country": "POL",
                    "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
                    "number": "QWE4567",
                },
            ],
        },
        approve_status=False,
    )
    return ticket


@pytest.fixture
def individual_data_change_ticket(
    afghanistan: BusinessArea,
    program: Program,
    area1: Area,
    household_one: Any,
) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        admin2=area1,
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_NEW,
    )
    ticket.programs.set([program])

    first_individual = household_one.individuals_list[0]

    TicketIndividualDataUpdateDetailsFactory(
        ticket=ticket,
        individual=first_individual,
        individual_data={
            "given_name": {"value": "Test", "approve_status": False},
            "full_name": {"value": "Test Example", "approve_status": False},
            "family_name": {"value": "Example", "approve_status": False},
            "sex": {"value": "MALE", "approve_status": False},
            "birth_date": {
                "value": date(year=1980, month=2, day=1).isoformat(),
                "approve_status": False,
            },
            "marital_status": {"value": SINGLE, "approve_status": False},
            "documents": [
                {
                    "value": {
                        "country": "POL",
                        "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                        "number": "999-888-777",
                    },
                    "approve_status": False,
                },
            ],
            "documents_to_edit": [
                {
                    "value": {
                        "id": str(household_one.national_id.id),
                        "country": None,
                        "type": None,
                        "number": "999-888-666",
                        "photo": "",
                    },
                    "previous_value": {
                        "id": str(household_one.national_id.id),
                        "country": "POL",
                        "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                        "number": "789-789-645",
                        "photo": "",
                    },
                    "approve_status": False,
                }
            ],
            "documents_to_remove": [
                {"value": str(household_one.national_id.id), "approve_status": False},
                {"value": str(household_one.birth_certificate.id), "approve_status": False},
            ],
            "flex_fields": {"flex_aaa": {"approve_status": True}},
        },
    )
    return ticket


@pytest.fixture
def household_data_change_ticket(
    afghanistan: BusinessArea,
    program: Program,
    area1: Area,
    household_one: Any,
) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        admin2=area1,
        business_area=afghanistan,
    )
    ticket.programs.set([program])
    TicketHouseholdDataUpdateDetailsFactory(
        ticket=ticket,
        household=household_one,
        household_data={
            "village": {"value": "Test Village"},
            "size": {"value": 19},
            "flex_fields": {},
            "roles": [
                {
                    "value": "PRIMARY",
                    "full_name": "Anthony Christine",
                    "individual_id": "9cac5264-7f50-4f39-8a5f-0b19bbe80ddf",
                    "approve_status": False,
                    "previous_value": None,
                },
                {
                    "value": "ALTERNATE",
                    "full_name": "Michael Catherine",
                    "individual_id": "15f93b1a-522e-42c1-a85e-8c329ea950f2",
                    "approve_status": False,
                    "previous_value": None,
                },
            ],
        },
    )
    return ticket


@pytest.fixture
def bulk_grievance_tickets(
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    user2: User,
) -> tuple:
    ticket1 = GrievanceTicketFactory(
        description="Test 1",
        assigned_to=user,
        priority=1,
        urgency=1,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        language="PL",
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        created_by=user2,
        business_area=afghanistan,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
    )
    ticket1.programs.set([program])

    ticket2 = GrievanceTicketFactory(
        description="Test 2",
        assigned_to=user,
        priority=1,
        urgency=1,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        language="PL",
        status=GrievanceTicket.STATUS_NEW,
        created_by=user2,
        business_area=afghanistan,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
    )
    ticket2.programs.set([program])

    return (ticket1, ticket2)


@pytest.mark.usefixtures("mock_elasticsearch")
@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.GRIEVANCES_APPROVE_DATA_CHANGE], status.HTTP_202_ACCEPTED),
        ([Permissions.GRIEVANCES_UPDATE], status.HTTP_403_FORBIDDEN),
    ],
)
def test_approve_individual_data_change(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    individual_data_change_ticket: GrievanceTicket,
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, permissions, afghanistan, program)

    data = {
        "individual_approve_data": {
            "given_name": True,
            "full_name": True,
            "family_name": True,
        },
        "approved_documents_to_create": [0],
        "approved_documents_to_edit": [0],
        "approved_documents_to_remove": [0],
        "approved_identities_to_create": [],
        "approved_identities_to_edit": [],
        "approved_identities_to_remove": [],
        "approved_accounts_to_create": [],
        "approved_accounts_to_edit": [],
        "flex_fields_approve_data": {"flex_aaa": False},
    }

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-approve-individual-data-change",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(individual_data_change_ticket.pk),
        },
    )

    client = api_client(user)
    response = client.post(url, data, format="json")

    resp_data = response.json()
    assert response.status_code == expected_status

    if expected_status == status.HTTP_202_ACCEPTED:
        assert "id" in resp_data
        assert resp_data["ticket_details"]["individual_data"]["given_name"] == {
            "value": "Test",
            "approve_status": True,
        }
        assert resp_data["ticket_details"]["individual_data"]["full_name"] == {
            "value": "Test Example",
            "approve_status": True,
        }
        assert resp_data["ticket_details"]["individual_data"]["family_name"] == {
            "value": "Example",
            "approve_status": True,
        }
        assert resp_data["ticket_details"]["individual_data"]["sex"] == {
            "value": "MALE",
            "approve_status": False,
        }
        assert resp_data["ticket_details"]["individual_data"]["birth_date"] == {
            "value": date(year=1980, month=2, day=1).isoformat(),
            "approve_status": False,
        }
        assert resp_data["ticket_details"]["individual_data"]["marital_status"] == {
            "value": SINGLE,
            "approve_status": False,
        }
        assert resp_data["ticket_details"]["individual_data"]["documents"] == [
            {
                "value": {
                    "country": "POL",
                    "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                    "number": "999-888-777",
                },
                "approve_status": True,
            },
        ]


@pytest.mark.usefixtures("mock_elasticsearch")
@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.GRIEVANCES_APPROVE_DATA_CHANGE], status.HTTP_202_ACCEPTED),
        ([Permissions.GRIEVANCES_UPDATE], status.HTTP_403_FORBIDDEN),
    ],
)
def test_approve_household_data_change(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    household_data_change_ticket: GrievanceTicket,
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, permissions, afghanistan, program)

    data = {
        "household_approve_data": {
            "village": True,
            "roles": [
                {
                    "individual_id": "9cac5264-7f50-4f39-8a5f-0b19bbe80ddf",
                    "approve_status": "True",
                },
                {
                    "individual_id": "15f93b1a-522e-42c1-a85e-8c329ea950f2",
                    "approve_status": "true",
                },
            ],
        },
        "flex_fields_approve_data": {},
    }

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-approve-household-data-change",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(household_data_change_ticket.pk),
        },
    )

    client = api_client(user)
    response = client.post(url, data, format="json")

    resp_data = response.json()
    assert response.status_code == expected_status

    if expected_status == status.HTTP_202_ACCEPTED:
        assert "id" in resp_data
        assert resp_data["ticket_details"]["household_data"]["village"] == {
            "value": "Test Village",
            "approve_status": True,
        }
        assert resp_data["ticket_details"]["household_data"]["size"] == {
            "value": 19,
            "approve_status": False,
        }
        assert resp_data["ticket_details"]["household_data"]["flex_fields"] == {}
        for role in resp_data["ticket_details"]["household_data"]["roles"]:
            assert role["approve_status"] is True


@pytest.mark.usefixtures("mock_elasticsearch")
def test_approve_add_individual(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    add_individual_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
        ],
        afghanistan,
        program,
    )

    data = {
        "approve_status": True,
        "version": add_individual_ticket.version,
    }

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-approve-status-update",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(add_individual_ticket.pk),
        },
    )

    client = api_client(user)
    response = client.post(url, data, format="json")

    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in resp_data


@pytest.mark.usefixtures("mock_elasticsearch")
def test_approve_delete_household(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    household_one: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_DATA_CHANGE],
        afghanistan,
        program,
    )

    reason_household = HouseholdFactory(
        program=program,
        business_area=afghanistan,
    )

    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
    )
    ticket.programs.set([program])

    details = TicketDeleteHouseholdDetailsFactory(
        ticket=ticket,
        household=household_one,
        approve_status=False,
    )

    data = {
        "approve_status": True,
        "reason_hh_id": reason_household.unicef_id,
        "version": ticket.version,
    }

    client = api_client(user)
    response = client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-delete-household",
            kwargs={"business_area_slug": afghanistan.slug, "pk": str(ticket.pk)},
        ),
        data,
        format="json",
    )

    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in resp_data
    details.refresh_from_db()
    assert details.approve_status is True
    assert details.reason_household == reason_household


@pytest.mark.usefixtures("mock_elasticsearch")
def test_approve_delete_household_validation_errors(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    household_one: Any,
    document_types: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_DATA_CHANGE],
        afghanistan,
        program,
    )

    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
    )
    ticket.programs.set([program])

    ticket_details = TicketDeleteHouseholdDetailsFactory(
        ticket=ticket,
        household=household_one,
        approve_status=False,
    )

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-approve-delete-household",
        kwargs={"business_area_slug": afghanistan.slug, "pk": str(ticket.pk)},
    )

    client = api_client(user)

    # Test 1: Same household as reason (should fail)
    response = client.post(
        url,
        {
            "approve_status": True,
            "reason_hh_id": household_one.unicef_id,
            "version": ticket.version,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        f"The provided household {household_one.unicef_id} is the same as the one being withdrawn." in response.json()
    )
    assert ticket_details.reason_household is None

    # Test 2: Withdrawn household as reason (should fail)
    household_one.withdrawn = True
    household_one.save()

    response = client.post(
        url,
        {
            "approve_status": True,
            "reason_hh_id": household_one.unicef_id,
            "version": ticket.version,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert f"The provided household {household_one.unicef_id} has to be active." in response.json()
    assert ticket_details.reason_household is None

    # Test 3: Invalid ID (should fail)
    response = client.post(
        url,
        {
            "approve_status": True,
            "reason_hh_id": "invalid_id",
            "version": ticket.version,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert ticket_details.reason_household is None

    # Test 4: Empty reason_hh_id (should pass)
    household_one.withdrawn = False
    household_one.save()

    response = client.post(
        url,
        {
            "approve_status": True,
            "reason_hh_id": "",
            "version": ticket.version,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in response.json()
    assert ticket_details.reason_household is None


@pytest.mark.usefixtures("mock_elasticsearch")
def test_approve_needs_adjudication(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        afghanistan,
        program,
    )

    household = HouseholdFactory(business_area=afghanistan, program=program)

    individuals_data = [
        {
            "full_name": "Benjamin Butler",
            "unicef_id": "IND-123-123",
            "photo": ContentFile(b"111", name="foo1.png"),
        },
        {
            "full_name": "Robin Ford",
            "unicef_id": "IND-222-222",
            "photo": ContentFile(b"222", name="foo2.png"),
        },
    ]

    individuals = [
        IndividualFactory(household=household, program=program, business_area=afghanistan, **individual)
        for individual in individuals_data
    ]

    na_grv = GrievanceTicketFactory(
        description="needs_adjudication_grievance_ticket",
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY,
    )
    na_grv.programs.set([program])

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=na_grv,
        golden_records_individual=individuals[0],
        possible_duplicate=individuals[1],
        selected_individual=None,
    )
    ticket_details.possible_duplicates.add(individuals[0], individuals[1])

    assert ticket_details.selected_individuals.all().count() == 0

    data = {
        "duplicate_individual_ids": [str(individuals[1].id)],
        "version": na_grv.version,
    }

    client = api_client(user)
    response = client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
            kwargs={"business_area_slug": afghanistan.slug, "pk": str(na_grv.pk)},
        ),
        data,
        format="json",
    )

    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in resp_data

    ticket_details.refresh_from_db()
    assert ticket_details.selected_individuals.all().count() == 1
    assert individuals[1] in ticket_details.selected_individuals.all()


@pytest.mark.usefixtures("mock_elasticsearch")
def test_approve_needs_adjudication_more(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        afghanistan,
        program,
    )

    household = HouseholdFactory(business_area=afghanistan, program=program)

    individuals_data = [
        {
            "full_name": "Benjamin Butler",
            "unicef_id": "IND-123-123",
            "photo": ContentFile(b"111", name="foo1.png"),
        },
        {
            "full_name": "Robin Ford",
            "unicef_id": "IND-222-222",
            "photo": ContentFile(b"222", name="foo2.png"),
        },
    ]

    individuals = [
        IndividualFactory(household=household, program=program, business_area=afghanistan, **individual)
        for individual in individuals_data
    ]

    na_grv = GrievanceTicketFactory(
        description="needs_adjudication_grievance_ticket",
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY,
    )
    na_grv.programs.set([program])

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=na_grv,
        golden_records_individual=individuals[0],
        possible_duplicate=individuals[1],
        selected_individual=None,
    )
    ticket_details.possible_duplicates.add(individuals[0], individuals[1])

    assert ticket_details.selected_individuals.all().count() == 0

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
        kwargs={"business_area_slug": afghanistan.slug, "pk": str(na_grv.pk)},
    )

    client = api_client(user)

    # Test clear_individual_ids
    response = client.post(
        url,
        {
            "clear_individual_ids": [str(individuals[1].id)],
            "version": na_grv.version,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in response.json()

    # Test selected_individual_id
    response = client.post(
        url,
        {"selected_individual_id": str(individuals[1].id)},
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in response.json()

    # Test distinct_individual_ids
    response = client.post(
        url,
        {"distinct_individual_ids": [str(individuals[1].id)]},
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in response.json()


@pytest.mark.usefixtures("mock_elasticsearch")
def test_approve_needs_adjudication_partner_with_area_limit(
    api_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program: Program,
    area1: Area,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        afghanistan,
        program,
    )

    another_area = AreaFactory(
        name="Another Area",
        area_type=area1.area_type,
        p_code="another-area-code",
    )

    AdminAreaLimitedToFactory(partner=partner, program=program, areas=[another_area])

    household = HouseholdFactory(business_area=afghanistan, program=program)
    individuals_data = [
        {
            "full_name": "Benjamin Butler",
            "unicef_id": "IND-123-123",
            "photo": ContentFile(b"111", name="foo1.png"),
        },
        {
            "full_name": "Robin Ford",
            "unicef_id": "IND-222-222",
            "photo": ContentFile(b"222", name="foo2.png"),
        },
    ]

    individuals = [
        IndividualFactory(household=household, program=program, business_area=afghanistan, **individual)
        for individual in individuals_data
    ]

    na_grv = GrievanceTicketFactory(
        description="needs_adjudication_grievance_ticket",
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        admin2=area1,
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY,
    )
    na_grv.programs.set([program])

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=na_grv,
        golden_records_individual=individuals[0],
        possible_duplicate=individuals[1],
        selected_individual=None,
    )
    ticket_details.possible_duplicates.add(individuals[0], individuals[1])

    data = {
        "duplicate_individual_ids": [str(individuals[1].id)],
        "version": na_grv.version,
    }

    client = api_client(user)
    response = client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
            kwargs={"business_area_slug": afghanistan.slug, "pk": str(na_grv.pk)},
        ),
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("mock_elasticsearch")
@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION],
            status.HTTP_202_ACCEPTED,
        ),
        ([Permissions.GRIEVANCES_UPDATE], status.HTTP_403_FORBIDDEN),
    ],
)
def test_approve_payment_details(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    household_one: Any,
    document_types: None,
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, permissions, afghanistan, program)

    payment_plan = PaymentPlanFactory(
        name="TEST",
        program_cycle=program.cycles.first(),
        business_area=afghanistan,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    payment_verification_plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        status=PaymentVerificationPlan.STATUS_ACTIVE,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        household=household_one,
        currency="PLN",
        collector=household_one.head_of_household,
    )
    payment_verification = PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
    )

    ticket_details = TicketPaymentVerificationDetailsFactory(payment_verification=payment_verification)
    ticket_details.ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
    ticket_details.ticket.business_area = afghanistan
    ticket_details.ticket.programs.set([program])
    ticket_details.ticket.save()

    data = {
        "approve_status": True,
        "version": ticket_details.ticket.version,
    }

    client = api_client(user)
    response = client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-payment-details",
            kwargs={"business_area_slug": afghanistan.slug, "pk": str(ticket_details.ticket.pk)},
        ),
        data,
        format="json",
    )

    resp_data = response.json()
    assert response.status_code == expected_status

    if expected_status == status.HTTP_202_ACCEPTED:
        assert "id" in resp_data
        ticket_details.refresh_from_db()
        assert ticket_details.approve_status is True
