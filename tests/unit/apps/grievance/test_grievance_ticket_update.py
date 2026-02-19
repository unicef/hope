from datetime import date
from typing import Any, Callable

from django.core.files.uploadedfile import SimpleUploadedFile
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
    TicketComplaintDetailsFactory,
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
from hope.apps.grievance.constants import (
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    URGENCY_NOT_URGENT,
)
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketNote,
)
from hope.apps.household.const import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_CHOICE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    ROLE_PRIMARY,
    SINGLE,
)
from hope.models import (
    Area,
    AreaType,
    BusinessArea,
    Country,
    DocumentType,
    IndividualRoleInHousehold,
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
    return AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")


@pytest.fixture
def area2(area_type: AreaType) -> Area:
    return AreaFactory(name="City Example", area_type=area_type, p_code="Afghnistan")


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


@pytest.fixture
def payment(afghanistan: BusinessArea, program: Program) -> Any:
    return PaymentFactory(
        parent__business_area=afghanistan,
        parent__program_cycle=program.cycles.first(),
    )


@pytest.fixture
def household_data_change_grievance_ticket(
    afghanistan: BusinessArea,
    program: Program,
    area1: Area,
    household_one: Any,
    user: User,
) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        admin2=area1,
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        created_by=user,
        assigned_to=user,
    )
    ticket.programs.set([program])

    TicketHouseholdDataUpdateDetailsFactory(
        ticket=ticket,
        household=household_one,
        household_data={
            "village": {"value": "Test Village", "approve_status": True},
            "size": {"value": 19, "approve_status": True},
            "country": "AFG",
        },
    )

    return ticket


@pytest.fixture
def complaint_ticket(
    afghanistan: BusinessArea,
    program: Program,
    area1: Area,
    household_one: Any,
    payment: Any,
    user: User,
) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        admin2=area1,
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_IN_PROGRESS,
        created_by=user,
        assigned_to=user,
        priority=PRIORITY_MEDIUM,
    )
    ticket.programs.set([program])

    TicketComplaintDetailsFactory(
        ticket=ticket,
        household=household_one,
        individual=household_one.individuals.first(),
        payment=payment,
    )

    return ticket


@pytest.fixture
def household_ticket_detail_url(
    afghanistan: BusinessArea, household_data_change_grievance_ticket: GrievanceTicket
) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(household_data_change_grievance_ticket.pk),
        },
    )


@pytest.fixture
def household_ticket_status_change_url(
    afghanistan: BusinessArea, household_data_change_grievance_ticket: GrievanceTicket
) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-status-change",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(household_data_change_grievance_ticket.pk),
        },
    )


@pytest.fixture
def complaint_ticket_detail_url(afghanistan: BusinessArea, complaint_ticket: GrievanceTicket) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(complaint_ticket.pk),
        },
    )


@pytest.fixture
def complaint_ticket_status_change_url(afghanistan: BusinessArea, complaint_ticket: GrievanceTicket) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-status-change",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(complaint_ticket.pk),
        },
    )


@pytest.fixture
def complaint_ticket_create_note_url(afghanistan: BusinessArea, complaint_ticket: GrievanceTicket) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-create-note",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(complaint_ticket.pk),
        },
    )


@pytest.mark.usefixtures("mock_elasticsearch")
def test_update_grievance_ticket_hh_update(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    household_data_change_grievance_ticket: GrievanceTicket,
    household_ticket_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
        ],
        afghanistan,
        program,
    )

    owner = UserFactory()
    data = {
        "assigned_to": str(owner.id),
        "admin": str(household_data_change_grievance_ticket.admin2.id),
        "language": household_data_change_grievance_ticket.language,
        "area": household_data_change_grievance_ticket.area,
        "extras": {
            "household_data_update_issue_type_extras": {
                "household_data": {
                    "village": "Test New",
                    "size": 33,
                    "country": "AFG",
                }
            }
        },
        "priority": PRIORITY_MEDIUM,
        "urgency": URGENCY_NOT_URGENT,
        "partner": str(PartnerFactory().id),
    }

    client = api_client(user)
    response = client.patch(household_ticket_detail_url, data, format="json")

    resp_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert resp_data["priority"] == PRIORITY_MEDIUM
    assert resp_data["urgency"] == URGENCY_NOT_URGENT
    assert resp_data["assigned_to"] == {
        "id": str(owner.id),
        "first_name": owner.first_name,
        "last_name": owner.last_name,
        "email": owner.email,
        "username": owner.username,
    }
    assert resp_data["ticket_details"]["household_data"]["village"]["value"] == "Test New"


@pytest.mark.usefixtures("mock_elasticsearch")
def test_update_grievance_ticket_with_no_area_access(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    area2: Area,
    household_data_change_grievance_ticket: GrievanceTicket,
    household_ticket_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
        ],
        afghanistan,
        program,
    )

    # Limit user access to area2, but ticket is in area1
    AdminAreaLimitedToFactory(
        program=program,
        partner=user.partner,
        areas=[area2],
    )

    input_data = {"priority": PRIORITY_LOW}

    client = api_client(user)
    response = client.patch(household_ticket_detail_url, input_data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "No GrievanceTicket matches the given query."


@pytest.mark.usefixtures("mock_elasticsearch")
def test_update_grievance_ticket_as_creator(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    household_data_change_grievance_ticket: GrievanceTicket,
    household_ticket_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    assert household_data_change_grievance_ticket.created_by == user

    data = {
        "priority": PRIORITY_LOW,
        "extras": {
            "household_data_update_issue_type_extras": {
                "household_data": {
                    "village": "Test V",
                    "size": 33,
                    "country": "AFG",
                }
            }
        },
    }

    client = api_client(user)
    response = client.patch(household_ticket_detail_url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # add permission to update as creator -> should be able to update ticket but extras not updated
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_UPDATE_AS_CREATOR],
        afghanistan,
        program,
    )
    response = client.patch(household_ticket_detail_url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    resp_data = response.json()
    assert resp_data["priority"] == PRIORITY_LOW
    assert resp_data["ticket_details"]["household_data"]["village"]["value"] == "Test Village"

    # add permission to update extras
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR],
        afghanistan,
        program,
    )
    response = client.patch(household_ticket_detail_url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert resp_data["ticket_details"]["household_data"]["village"]["value"] == "Test V"


@pytest.mark.usefixtures("mock_elasticsearch")
def test_update_grievance_ticket_as_owner(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    household_data_change_grievance_ticket: GrievanceTicket,
    household_ticket_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    assert household_data_change_grievance_ticket.assigned_to == user

    data = {
        "priority": PRIORITY_LOW,
        "assigned_to": str(user.id),  # not changing value; but is expected in input
        "extras": {
            "household_data_update_issue_type_extras": {
                "household_data": {
                    "village": "Test New One",
                    "size": 22,
                    "country": "AFG",
                }
            }
        },
    }

    client = api_client(user)
    response = client.patch(household_ticket_detail_url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # add permission to update as owner -> should be able to update ticket but extras not updated
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_UPDATE_AS_OWNER],
        afghanistan,
        program,
    )
    response = client.patch(household_ticket_detail_url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    resp_data = response.json()
    assert resp_data["priority"] == PRIORITY_LOW
    assert resp_data["ticket_details"]["household_data"]["village"]["value"] == "Test Village"

    household_data_change_grievance_ticket.refresh_from_db()

    # add permission to update extras
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER],
        afghanistan,
        program,
    )
    response = client.patch(household_ticket_detail_url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert resp_data["ticket_details"]["household_data"]["village"]["value"] == "Test New One"


@pytest.mark.usefixtures("mock_elasticsearch")
def test_update_payment_verification_ticket_with_new_received_amount_extras(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)

    household = HouseholdFactory(business_area=afghanistan, program=program)

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
        household=household,
        currency="PLN",
        program=program,
        collector=household.head_of_household,
    )
    payment_verification = PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        received_amount=10.00,
    )

    ticket = TicketPaymentVerificationDetailsFactory(
        payment_verification=payment_verification,
        ticket__status=GrievanceTicket.STATUS_IN_PROGRESS,
        ticket__business_area=afghanistan,
    )
    ticket.ticket.programs.set([program])

    data = {
        "priority": PRIORITY_LOW,
        "extras": {
            "ticket_payment_verification_details_extras": {
                "new_received_amount": 1234.99,
                "new_status": PaymentVerification.STATUS_RECEIVED,
            }
        },
    }

    client = api_client(user)
    response = client.patch(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-detail",
            kwargs={"business_area_slug": afghanistan.slug, "pk": str(ticket.ticket.pk)},
        ),
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert resp_data["ticket_details"]["new_received_amount"] == "1234.99"
    assert resp_data["ticket_details"]["new_status"] == PaymentVerification.STATUS_RECEIVED
    assert resp_data["ticket_details"]["payment_verification"]["received_amount"] == "10.00"
    assert (
        resp_data["ticket_details"]["payment_verification"]["status"] == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
    )


@pytest.mark.usefixtures("mock_elasticsearch")
def test_update_grievance_ticket_complaint(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    household_one: Any,
    document_types: None,
    payment: Any,
    complaint_ticket: GrievanceTicket,
    complaint_ticket_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
        ],
        afghanistan,
        program,
    )

    household_two = HouseholdFactory(business_area=afghanistan, program=program)
    individual = IndividualFactory(household=household_two, program=program, business_area=afghanistan)

    data = {
        "priority": PRIORITY_LOW,
        "assigned_to": str(user.id),
        "extras": {
            "category": {
                "grievance_complaint_ticket_extras": {
                    "household": str(household_two.pk),
                    "individual": str(individual.pk),
                    "payment_record": [str(payment.pk)],
                }
            }
        },
    }

    client = api_client(user)
    response = client.patch(complaint_ticket_detail_url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["priority"] == PRIORITY_LOW


@pytest.mark.usefixtures("mock_elasticsearch")
def test_update_grievance_ticket_validation_error(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    household_data_change_grievance_ticket: GrievanceTicket,
    household_ticket_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
        ],
        afghanistan,
        program,
    )

    data = {
        "extras": {
            "household_data_update_issue_type_extras": {
                "household_data": {
                    "village": "Test New",
                }
            }
        },
    }
    household_data_change_grievance_ticket.status = GrievanceTicket.STATUS_CLOSED
    household_data_change_grievance_ticket.save()

    client = api_client(user)
    response = client.patch(household_ticket_detail_url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Grievance Ticket in status Closed is not editable" in response.json()


@pytest.mark.usefixtures("mock_elasticsearch")
def test_grievance_status_change(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    complaint_ticket: GrievanceTicket,
    complaint_ticket_status_change_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.GRIEVANCES_SET_ON_HOLD, Permissions.GRIEVANCES_UPDATE], afghanistan, program
    )

    input_data = {
        "status": GrievanceTicket.STATUS_ON_HOLD,
    }

    client = api_client(user)
    response = client.post(complaint_ticket_status_change_url, input_data, format="json")

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["status"] == GrievanceTicket.STATUS_ON_HOLD


@pytest.mark.usefixtures("mock_elasticsearch")
def test_grievance_status_change_invalid_status(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    complaint_ticket: GrievanceTicket,
    complaint_ticket_status_change_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)

    input_data = {"status": 22}

    client = api_client(user)
    response = client.post(complaint_ticket_status_change_url, input_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "New status is incorrect" in response.json()


@pytest.mark.usefixtures("mock_elasticsearch")
def test_grievance_status_change_invalid_status_flow(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        afghanistan,
        program,
    )

    household = HouseholdFactory(business_area=afghanistan, program=program)
    ticket = TicketHouseholdDataUpdateDetailsFactory(
        ticket__business_area=afghanistan,
        ticket__status=GrievanceTicket.STATUS_NEW,
        household=household,
    )
    ticket.ticket.programs.set([program])

    # Try to move from NEW directly to CLOSED (invalid flow)
    input_data = {
        "status": GrievanceTicket.STATUS_CLOSED,
    }

    client = api_client(user)
    response = client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-status-change",
            kwargs={"business_area_slug": afghanistan.slug, "pk": str(ticket.ticket.pk)},
        ),
        input_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "New status is incorrect" in response.json()


@pytest.mark.usefixtures("mock_elasticsearch")
def test_grievance_status_change_other_statuses(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    complaint_ticket: GrievanceTicket,
    complaint_ticket_status_change_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_SET_ON_HOLD,
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_SEND_BACK,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        afghanistan,
        program,
    )

    client = api_client(user)

    # Test moving to FOR_APPROVAL
    response = client.post(
        complaint_ticket_status_change_url,
        {"status": GrievanceTicket.STATUS_FOR_APPROVAL},
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["status"] == GrievanceTicket.STATUS_FOR_APPROVAL

    # Test moving to IN_PROGRESS
    response = client.post(
        complaint_ticket_status_change_url,
        {"status": GrievanceTicket.STATUS_IN_PROGRESS},
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["status"] == GrievanceTicket.STATUS_IN_PROGRESS

    # Test moving to FOR_APPROVAL again
    response = client.post(
        complaint_ticket_status_change_url,
        {"status": GrievanceTicket.STATUS_FOR_APPROVAL},
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED

    # Test moving to CLOSED
    response = client.post(
        complaint_ticket_status_change_url,
        {"status": GrievanceTicket.STATUS_CLOSED},
        format="json",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["status"] == GrievanceTicket.STATUS_CLOSED


@pytest.mark.usefixtures("mock_elasticsearch")
def test_grievance_status_change_assigned_to(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_UPDATE, Permissions.GRIEVANCE_ASSIGN],
        afghanistan,
        program,
    )

    household = HouseholdFactory(business_area=afghanistan, program=program)

    ticket = TicketHouseholdDataUpdateDetailsFactory(
        ticket__business_area=afghanistan,
        ticket__category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        ticket__issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        ticket__status=GrievanceTicket.STATUS_NEW,
        ticket__assigned_to=None,
        household=household,
        household_data={},
    )
    ticket.ticket.programs.set([program])

    input_data = {
        "status": GrievanceTicket.STATUS_ASSIGNED,
    }

    client = api_client(user)
    response = client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-status-change",
            kwargs={"business_area_slug": afghanistan.slug, "pk": str(ticket.ticket.pk)},
        ),
        input_data,
        format="json",
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["status"] == GrievanceTicket.STATUS_ASSIGNED
    assert response.json()["assigned_to"]["id"] == str(user.id)


@pytest.mark.usefixtures("mock_elasticsearch")
def test_grievance_status_change_close_na_without_access(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    area1: Area,
    area2: Area,
    create_user_role_with_permissions: Callable,
) -> None:
    program_2 = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)

    household_one = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        admin2=area1,
    )
    household_2 = HouseholdFactory(
        business_area=afghanistan,
        program=program_2,
        admin2=area2,
    )
    first_individual = IndividualFactory(
        household=household_one,
        program=program,
        business_area=afghanistan,
    )
    second_individual = IndividualFactory(
        household=household_2,
        program=program_2,
        business_area=afghanistan,
    )

    household_one.head_of_household = first_individual
    household_one.save()
    household_2.head_of_household = second_individual
    household_2.save()

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
        golden_records_individual=first_individual,
        possible_duplicate=second_individual,
        selected_individual=second_individual,
    )
    ticket_details.selected_distinct.add(first_individual)
    ticket_details.possible_duplicates.add(second_individual)
    ticket_details.selected_individuals.add(second_individual, first_individual)

    AdminAreaLimitedToFactory(
        partner=user.partner,
        program=program_2,
        areas=[area1],
    )

    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        afghanistan,
        program,
    )

    input_data = {
        "status": GrievanceTicket.STATUS_CLOSED,
    }

    client = api_client(user)
    response = client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-status-change",
            kwargs={"business_area_slug": afghanistan.slug, "pk": str(na_grv.pk)},
        ),
        input_data,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("mock_elasticsearch")
def test_create_ticket_note(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    complaint_ticket: GrievanceTicket,
    document_types: None,
    complaint_ticket_create_note_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_ADD_NOTE], afghanistan, program)

    input_data = {"version": complaint_ticket.version, "description": "test new note"}

    client = api_client(user)
    response = client.post(complaint_ticket_create_note_url, input_data, format="json")

    resp_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in resp_data
    assert resp_data["description"] == "test new note"


@pytest.mark.usefixtures("mock_elasticsearch")
def test_reassign_role(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)
    household = HouseholdFactory(business_area=afghanistan, program=program)

    individual_1 = IndividualFactory(
        full_name="Benjamin Butler",
        household=None,
        program=program,
        business_area=afghanistan,
    )

    individual_2 = IndividualFactory(
        full_name="Andrew Jackson",
        household=None,
        program=program,
        business_area=afghanistan,
    )

    IndividualFactory(
        full_name="Ulysses Grant",
        household=None,
        program=program,
        business_area=afghanistan,
    )

    household.head_of_household = individual_1
    household.save()

    individual_1.household = household
    individual_2.household = household
    individual_1.save()
    individual_2.save()

    household.refresh_from_db()
    individual_1.refresh_from_db()
    individual_2.refresh_from_db()

    primary_role = IndividualRoleInHousehold.objects.get(
        household=household,
        role=ROLE_PRIMARY,
    )
    primary_role.individual = individual_1
    primary_role.save()

    grievance_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        business_area=afghanistan,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY,
    )
    grievance_ticket.programs.set([program])

    TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance_ticket,
        golden_records_individual=individual_1,
        possible_duplicate=individual_2,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )

    data = {
        "household_id": str(household.id),
        "individual_id": str(individual_1.id),
        "new_individual_id": str(individual_2.id),
        "role": "HEAD",
        "version": grievance_ticket.version,
    }

    client = api_client(user)
    response = client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-reassign-role",
            kwargs={"business_area_slug": afghanistan.slug, "pk": str(grievance_ticket.pk)},
        ),
        data,
        format="json",
    )

    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in resp_data


@pytest.mark.usefixtures("mock_elasticsearch")
@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.PROGRAMME_UPDATE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            ],
            status.HTTP_403_FORBIDDEN,
        ),
        (
            [
                Permissions.GRIEVANCES_UPDATE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            ],
            status.HTTP_202_ACCEPTED,
        ),
    ],
)
def test_bulk_update_grievance_assignee(
    api_client: Any,
    user: User,
    user2: User,
    afghanistan: BusinessArea,
    program: Program,
    bulk_grievance_tickets: tuple,
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, permissions, afghanistan, program=program)

    ticket1, ticket2 = bulk_grievance_tickets

    url_list = reverse(
        "api:grievance:grievance-tickets-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
        },
    )

    client = api_client(user)

    response_list_before = client.get(url_list, {"category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT})
    assert response_list_before.status_code == status.HTTP_200_OK
    assert len(response_list_before.json()["results"]) == 2
    for ticket in response_list_before.json()["results"]:
        assert ticket["assigned_to"]["id"] == str(user.id)

    # Bulk update assignee
    data = {
        "assigned_to": str(user2.id),
        "grievance_ticket_ids": [
            str(ticket1.id),
            str(ticket2.id),
        ],
    }

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-bulk-update-assignee",
        kwargs={"business_area_slug": afghanistan.slug},
    )

    response = client.post(url, data, format="json")

    resp_data = response.json()
    assert response.status_code == expected_status

    if expected_status == status.HTTP_202_ACCEPTED:
        assert len(resp_data) == 2
        assert resp_data[0]["assigned_to"]["first_name"] == "SecondUser"
        assert resp_data[1]["assigned_to"]["first_name"] == "SecondUser"

    # Check list after bulk update
    response_list_after = client.get(url_list, {"category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT})
    assert response_list_after.status_code == status.HTTP_200_OK
    assert len(response_list_after.json()["results"]) == 2

    if expected_status == status.HTTP_202_ACCEPTED:
        for ticket in response_list_after.json()["results"]:
            assert ticket["assigned_to"]["id"] == str(user2.id)
    else:
        for ticket in response_list_after.json()["results"]:
            assert ticket["assigned_to"]["id"] == str(user.id)


@pytest.mark.usefixtures("mock_elasticsearch")
def test_bulk_update_grievance_priority(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    bulk_grievance_tickets: tuple,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)

    ticket1, ticket2 = bulk_grievance_tickets

    data = {
        "priority": 3,
        "grievance_ticket_ids": [
            str(ticket1.id),
            str(ticket2.id),
        ],
    }

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-bulk-update-priority",
        kwargs={"business_area_slug": afghanistan.slug},
    )

    client = api_client(user)
    response = client.post(url, data, format="json")

    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert len(resp_data) == 2
    assert resp_data[0]["priority"] == 3
    assert resp_data[1]["priority"] == 3


@pytest.mark.usefixtures("mock_elasticsearch")
def test_bulk_update_grievance_urgency(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    bulk_grievance_tickets: tuple,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)

    ticket1, ticket2 = bulk_grievance_tickets

    data = {
        "urgency": 2,
        "grievance_ticket_ids": [
            str(ticket1.id),
            str(ticket2.id),
        ],
    }

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-bulk-update-urgency",
        kwargs={"business_area_slug": afghanistan.slug},
    )

    client = api_client(user)
    response = client.post(url, data, format="json")

    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert len(resp_data) == 2
    assert resp_data[0]["urgency"] == 2
    assert resp_data[1]["urgency"] == 2


@pytest.mark.usefixtures("mock_elasticsearch")
def test_bulk_add_note(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    bulk_grievance_tickets: tuple,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_UPDATE], afghanistan, program)

    ticket1, ticket2 = bulk_grievance_tickets

    data = {
        "note": "New Note bulk create",
        "grievance_ticket_ids": [
            str(ticket1.id),
            str(ticket2.id),
        ],
    }

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-bulk-add-note",
        kwargs={"business_area_slug": afghanistan.slug},
    )

    client = api_client(user)
    response = client.post(url, data, format="json")

    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert TicketNote.objects.count() == 2
    assert len(resp_data) == 2
    assert resp_data[0]["ticket_notes"][0]["description"] == "New Note bulk create"
    assert resp_data[1]["ticket_notes"][0]["description"] == "New Note bulk create"


@pytest.mark.usefixtures("mock_elasticsearch")
def test_update_grievance_ticket_individual_data_with_photo(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    individual_data_change_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
            Permissions.GRIEVANCE_DOCUMENTS_UPLOAD,
        ],
        afghanistan,
        program=program,
    )

    fake_photo = SimpleUploadedFile(
        "photo.png",
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82",
        content_type="image/png",
    )

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(individual_data_change_ticket.pk),
        },
    )

    data = {
        "extras.individual_data_update_issue_type_extras.individual_data.photo": fake_photo,
    }

    client = api_client(user)
    response = client.patch(url, data, format="multipart")

    assert response.status_code == status.HTTP_200_OK

    individual_data_change_ticket.refresh_from_db()
    ticket_details = individual_data_change_ticket.individual_data_update_ticket_details
    assert "photo" in ticket_details.individual_data
    assert ticket_details.individual_data["photo"]["value"]


@pytest.mark.usefixtures("mock_elasticsearch")
def test_update_grievance_ticket_add_individual_with_photo(
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
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
            Permissions.GRIEVANCE_DOCUMENTS_UPLOAD,
        ],
        afghanistan,
        program=program,
    )

    fake_photo = SimpleUploadedFile(
        "photo.png",
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82",
        content_type="image/png",
    )

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(add_individual_ticket.pk),
        },
    )

    data = {
        "extras.add_individual_issue_type_extras.individual_data.photo": fake_photo,
    }

    client = api_client(user)
    response = client.patch(url, data, format="multipart")

    assert response.status_code == status.HTTP_200_OK

    add_individual_ticket.refresh_from_db()
    ticket_details = add_individual_ticket.add_individual_ticket_details
    assert "photo" in ticket_details.individual_data
    assert ticket_details.individual_data["photo"]


@pytest.mark.usefixtures("mock_elasticsearch")
def test_update_grievance_ticket_individual_data_clear_photo(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    individual_data_change_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
        ],
        afghanistan,
        program=program,
    )

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "pk": str(individual_data_change_ticket.pk),
        },
    )

    data = {
        "extras": {
            "individual_data_update_issue_type_extras": {
                "individual_data": {
                    "photo": None,
                }
            }
        }
    }

    client = api_client(user)
    response = client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK

    individual_data_change_ticket.refresh_from_db()
    ticket_details = individual_data_change_ticket.individual_data_update_ticket_details
    assert "photo" in ticket_details.individual_data
    assert ticket_details.individual_data["photo"]["value"] == ""
