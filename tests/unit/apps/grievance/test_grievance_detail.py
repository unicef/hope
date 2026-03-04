from datetime import date, datetime
from typing import Any, Callable

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.core.files.base import ContentFile
from django.utils import timezone
from freezegun import freeze_time
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.grievance import (
    GrievanceDocumentFactory,
    GrievanceTicketFactory,
    TicketAddIndividualDetailsFactory,
    TicketDeleteHouseholdDetailsFactory,
    TicketDeleteIndividualDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketNoteFactory,
    TicketPaymentVerificationDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
)
from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
)
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.registration_data import DeduplicationEngineSimilarityPairFactory
from extras.test_utils.factories.sanction_list import (
    SanctionListIndividualDateOfBirthFactory,
    SanctionListIndividualDocumentFactory,
    SanctionListIndividualFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import (
    DUPLICATE,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SINGLE,
)
from hope.models import (
    Area,
    BusinessArea,
    Country,
    Household,
    Individual,
    IndividualRoleInHousehold,
    Partner,
    PaymentVerification,
    PaymentVerificationPlan,
    Program,
    User,
)

pytestmark = pytest.mark.django_db


def assign_ticket_data(
    grievance_ticket: GrievanceTicket,
    ticket_note: Any,
    grievance_document: Any,
    program: Program,
    linked_ticket: GrievanceTicket,
) -> None:
    ticket_note.ticket = grievance_ticket
    ticket_note.save()
    grievance_document.grievance_ticket = grievance_ticket
    grievance_document.save()
    grievance_ticket.programs.add(program)
    grievance_ticket.linked_tickets.add(linked_ticket)


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="AFG")


@pytest.fixture
def ukraine() -> BusinessArea:
    return BusinessAreaFactory(name="Ukraine", slug="ukraine", code="UKR")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def user2(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def country() -> Country:
    return CountryFactory()


@pytest.fixture
def admin_type(country: Country) -> Any:
    return AreaTypeFactory(country=country, area_level=1)


@pytest.fixture
def area1(admin_type: Any) -> Area:
    return AreaFactory(parent=None, p_code="AF01", area_type=admin_type)


@pytest.fixture
def area2(admin_type: Any) -> Area:
    return AreaFactory(parent=None, p_code="AF0101", area_type=admin_type)


@pytest.fixture
def grievance_ticket_base_data(afghanistan: BusinessArea, area1: Area, user: User, user2: User) -> dict:
    return {
        "business_area": afghanistan,
        "admin2": area1,
        "language": "Polish",
        "consent": True,
        "description": "Test Description",
        "status": GrievanceTicket.STATUS_NEW,
        "created_by": user,
        "assigned_to": user2,
        "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
    }


@pytest.fixture
def ticket_note(user: User) -> Any:
    return TicketNoteFactory(
        description="Test Note",
        created_by=user,
        created_at=timezone.make_aware(datetime(year=2021, month=8, day=22)),
        updated_at=timezone.make_aware(datetime(year=2021, month=8, day=24)),
    )


@pytest.fixture
def grievance_document(user: User) -> Any:
    return GrievanceDocumentFactory(
        name="Test Document",
        created_by=user,
        created_at=timezone.make_aware(datetime(year=2022, month=8, day=22)),
        updated_at=timezone.make_aware(datetime(year=2022, month=8, day=24)),
    )


@pytest.fixture
def household1(area1: Area, area2: Area, country: Country, program: Program, afghanistan: BusinessArea) -> Household:
    individual1 = IndividualFactory(business_area=afghanistan, program=program, household=None)
    household = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        country=country,
        country_origin=country,
        program=program,
        business_area=afghanistan,
        head_of_household=individual1,
        start=timezone.now(),
    )
    IndividualFactory(business_area=afghanistan, program=program, household=household)
    individual1.household = household
    individual1.save()
    return household


@pytest.fixture
def individuals1(household1: Household) -> list[Individual]:
    return list(household1.individuals.all())


@pytest.fixture
def household2(area1: Area, area2: Area, country: Country, program: Program, afghanistan: BusinessArea) -> Household:
    individual1 = IndividualFactory(business_area=afghanistan, program=program, household=None)
    household = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        country=country,
        country_origin=country,
        program=program,
        business_area=afghanistan,
        head_of_household=individual1,
        start=timezone.now(),
    )
    IndividualFactory(business_area=afghanistan, program=program, household=household)
    individual1.household = household
    individual1.save()
    return household


@pytest.fixture
def individuals2(household2: Household) -> list[Individual]:
    return list(household2.individuals.all())


@pytest.fixture
def linked_ticket(ukraine: BusinessArea, area1: Area, user2: User) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        business_area=ukraine,
        admin2=area1,
        language="Polish",
        consent=True,
        description="Linked Ticket",
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
        status=GrievanceTicket.STATUS_NEW,
        created_by=user2,
        assigned_to=user2,
    )
    ticket.created_at = timezone.make_aware(datetime(year=2021, month=8, day=22))
    ticket.save()
    return ticket


@pytest.fixture
def existing_ticket(ukraine: BusinessArea, area1: Area, user2: User, household1: Household) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        business_area=ukraine,
        admin2=area1,
        language="Polish",
        consent=True,
        description="Linked Ticket",
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
        status=GrievanceTicket.STATUS_NEW,
        created_by=user2,
        assigned_to=user2,
        household_unicef_id=household1.unicef_id,
    )
    ticket.created_at = timezone.make_aware(datetime(year=2021, month=8, day=23))
    ticket.save()
    return ticket


@pytest.fixture
def configured_grievance_ticket(
    grievance_ticket_base_data: dict,
    program: Program,
    household1: Household,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
) -> GrievanceTicket:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        household_unicef_id=household1.unicef_id,
    )
    grievance_ticket.created_at = timezone.make_aware(datetime(year=2024, month=8, day=25, hour=12))
    grievance_ticket.save()
    assign_ticket_data(grievance_ticket, ticket_note, grievance_document, program, linked_ticket)
    return grievance_ticket


@pytest.fixture
def detail_url_name() -> str:
    return "api:grievance:grievance-tickets-global-detail"


def assert_base_grievance_data(
    data: dict,
    grievance_ticket: GrievanceTicket,
    linked_ticket: Any,
    existing_ticket: Any,
    delivered_quantities: list | None = None,
) -> None:
    """Assert base grievance ticket data for detail responses."""
    program = grievance_ticket.programs.first()
    afghanistan = grievance_ticket.business_area
    ticket_note = grievance_ticket.ticket_notes.first()
    grievance_document = grievance_ticket.support_documents.first()
    user = ticket_note.created_by

    assert data["id"] == str(grievance_ticket.id)
    assert data["unicef_id"] == grievance_ticket.unicef_id
    assert data["status"] == grievance_ticket.status
    assert data["programs"] == [
        {
            "id": str(program.id),
            "programme_code": program.programme_code,
            "slug": program.slug,
            "name": program.name,
            "status": program.status,
            "screen_beneficiary": program.screen_beneficiary,
        }
    ]

    # Household data
    household = getattr(getattr(grievance_ticket, "ticket_details", None), "household", None)
    expected_household = (
        {
            "id": str(household.id),
            "unicef_id": household.unicef_id,
            "unhcr_id": household.unhcr_id,
            "village": household.village,
            "address": household.address,
            "admin1": {
                "id": str(household.admin1.id),
                "name": household.admin1.name,
            },
            "admin2": {
                "id": str(household.admin2.id),
                "name": household.admin2.name,
            },
            "country": household.country.name,
            "country_origin": household.country_origin.name,
            "geopoint": household.geopoint,
            "size": household.size,
            "residence_status": household.get_residence_status_display(),
            "program_slug": household.program.slug,
            "head_of_household": {
                "id": str(household.head_of_household.id),
                "full_name": household.head_of_household.full_name,
            },
            "active_individuals_count": household.active_individuals.count(),
        }
        if household
        else None
    )
    assert data["household"] == expected_household

    # Admin data
    assert data["admin"] == (grievance_ticket.admin2.name if grievance_ticket.admin2 else "")
    expected_admin2 = (
        {
            "id": str(grievance_ticket.admin2.id),
            "name": grievance_ticket.admin2.name,
            "p_code": grievance_ticket.admin2.p_code,
            "area_type": grievance_ticket.admin2.area_type.id,
            "updated_at": f"{grievance_ticket.admin2.updated_at:%Y-%m-%dT%H:%M:%SZ}",
        }
        if grievance_ticket.admin2
        else None
    )
    assert data["admin2"] == expected_admin2

    # User data
    assert data["assigned_to"] == {
        "id": str(grievance_ticket.assigned_to.id),
        "first_name": grievance_ticket.assigned_to.first_name,
        "last_name": grievance_ticket.assigned_to.last_name,
        "email": grievance_ticket.assigned_to.email,
        "username": grievance_ticket.assigned_to.username,
    }
    assert data["created_by"] == {
        "id": str(grievance_ticket.created_by.id),
        "first_name": grievance_ticket.created_by.first_name,
        "last_name": grievance_ticket.created_by.last_name,
        "email": grievance_ticket.created_by.email,
        "username": grievance_ticket.created_by.username,
    }

    assert data["user_modified"] == f"{grievance_ticket.user_modified:%Y-%m-%dT%H:%M:%SZ}"
    assert data["category"] == grievance_ticket.category
    assert data["issue_type"] == grievance_ticket.issue_type
    assert data["priority"] == grievance_ticket.priority
    assert data["urgency"] == grievance_ticket.urgency
    assert data["created_at"] == f"{grievance_ticket.created_at:%Y-%m-%dT%H:%M:%SZ}"
    assert data["updated_at"] == f"{grievance_ticket.updated_at:%Y-%m-%dT%H:%M:%SZ}"

    # Total days
    if grievance_ticket.status == GrievanceTicket.STATUS_CLOSED:
        delta = grievance_ticket.updated_at - grievance_ticket.created_at
    else:
        delta = timezone.now() - grievance_ticket.created_at
    expected_total_days = delta.days
    assert data["total_days"] == expected_total_days

    assert data["target_id"] == grievance_ticket.target_id
    assert data["partner"] == (
        {
            "id": str(grievance_ticket.partner.id),
            "name": grievance_ticket.partner.name,
        }
        if grievance_ticket.partner
        else None
    )
    assert data["postpone_deduplication"] == afghanistan.postpone_deduplication

    # Individual data
    individual = getattr(getattr(grievance_ticket, "ticket_details", None), "individual", None)
    expected_role = (
        (individual.households_and_roles(manager="all_objects").filter(household=individual.household).first())
        if individual
        else None
    )
    expected_individual = (
        {
            "id": str(individual.id),
            "unicef_id": individual.unicef_id,
            "full_name": individual.full_name,
            "program_slug": individual.program.slug,
            "household": {
                "id": str(individual.household.id),
                "unicef_id": individual.household.unicef_id,
                "admin1": {
                    "id": str(individual.household.admin1.id),
                    "name": individual.household.admin1.name,
                },
                "admin2": {
                    "id": str(individual.household.admin2.id),
                    "name": individual.household.admin2.name,
                },
                "program_slug": individual.program.slug,
                "admin3": None,
                "admin4": None,
                "first_registration_date": f"{individual.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "last_registration_date": f"{individual.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "total_cash_received": None,
                "total_cash_received_usd": None,
                "delivered_quantities": delivered_quantities
                or [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                "start": individual.household.start.strftime("%Y-%m-%dT%H:%M:%SZ")
                if individual.household.start
                else None,
                "zip_code": None,
                "residence_status": individual.household.get_residence_status_display(),
                "country_origin": individual.household.country_origin.name,
                "country": individual.household.country.name,
                "address": individual.household.address,
                "village": individual.household.village,
                "geopoint": None,
                "import_id": individual.household.unicef_id,
            },
            "roles_in_households": [
                {
                    "id": str(role.id),
                    "role": role.role,
                    "household": {
                        "id": str(role.household.id),
                        "unicef_id": role.household.unicef_id,
                        "admin1": {
                            "id": str(role.household.admin1.id),
                            "name": role.household.admin1.name,
                        },
                        "admin2": {
                            "id": str(role.household.admin2.id),
                            "name": role.household.admin2.name,
                        },
                        "admin3": None,
                        "admin4": None,
                        "country": role.household.country.name,
                        "country_origin": role.household.country_origin.name,
                        "address": role.household.address,
                        "village": role.household.village,
                        "geopoint": role.household.geopoint,
                        "first_registration_date": f"{role.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                        "last_registration_date": f"{role.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                        "total_cash_received": role.household.total_cash_received,
                        "total_cash_received_usd": role.household.total_cash_received_usd,
                        "delivered_quantities": delivered_quantities
                        or [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                        "start": f"{role.household.start:%Y-%m-%dT%H:%M:%SZ}" if role.household.start else None,
                        "zip_code": role.household.zip_code,
                        "residence_status": role.household.get_residence_status_display(),
                        "import_id": role.household.unicef_id,
                        "program_slug": program.slug,
                    },
                }
                for role in individual.households_and_roles(manager="all_merge_status_objects").all()
            ],
            "relationship": individual.relationship,
            "role": (expected_role.get_role_display() if expected_role else "-"),
            "documents": [
                {
                    "id": str(document.id),
                    "type": {
                        "id": str(document.type.id),
                        "label": document.type.label,
                        "key": document.type.key,
                    },
                    "country": {
                        "id": str(document.country.id),
                        "name": document.country.name,
                        "iso_code3": document.country.iso_code3,
                    },
                    "document_number": document.document_number,
                    "photo": document.photo.url if document.photo else None,
                }
                for document in individual.documents.all()
            ],
        }
        if individual
        else None
    )
    assert data["individual"] == expected_individual

    # Related tickets
    related_tickets = data["related_tickets"]
    assert {
        "id": str(existing_ticket.id),
        "unicef_id": existing_ticket.unicef_id,
    } in related_tickets
    assert {
        "id": str(linked_ticket.id),
        "unicef_id": linked_ticket.unicef_id,
    } in related_tickets

    assert data["linked_tickets"] == [
        {
            "id": str(linked_ticket.id),
            "unicef_id": linked_ticket.unicef_id,
        },
    ]
    assert data["existing_tickets"] == [
        {
            "id": str(existing_ticket.id),
            "unicef_id": existing_ticket.unicef_id,
        },
    ]

    # Ticket notes
    assert data["ticket_notes"] == [
        {
            "id": str(ticket_note.id),
            "description": ticket_note.description,
            "created_by": {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "username": user.username,
            },
            "created_at": f"{ticket_note.created_at:%Y-%m-%dT%H:%M:%SZ}",
            "updated_at": f"{ticket_note.updated_at:%Y-%m-%dT%H:%M:%SZ}",
        }
    ]

    # Documentation
    assert data["documentation"] == [
        {
            "id": str(grievance_document.id),
            "name": grievance_document.name,
            "file_path": grievance_document.file_path,
            "file_name": grievance_document.file_name,
            "content_type": grievance_document.content_type,
            "file_size": grievance_document.file_size,
            "created_by": {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "username": user.username,
            },
            "created_at": f"{grievance_document.created_at:%Y-%m-%dT%H:%M:%SZ}",
            "updated_at": f"{grievance_document.updated_at:%Y-%m-%dT%H:%M:%SZ}",
        }
    ]


@freeze_time("2024-08-25 12:00:00")
def test_grievance_detail_with_all_permissions(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    configured_grievance_ticket: GrievanceTicket,
    detail_url_name: str,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
    existing_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
        ],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(configured_grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK

    assert_base_grievance_data(
        data=response.data,
        grievance_ticket=configured_grievance_ticket,
        linked_ticket=linked_ticket,
        existing_ticket=existing_ticket,
    )


@pytest.mark.parametrize(
    "permissions",
    [
        [],
        [Permissions.PROGRAMME_ACTIVATE],
    ],
)
def test_grievance_detail_without_permissions(
    permissions: list,
    authenticated_client: Any,
    afghanistan: BusinessArea,
    user: User,
    configured_grievance_ticket: GrievanceTicket,
    detail_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(configured_grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_grievance_detail_area_limits(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    partner: Partner,
    area1: Area,
    area2: Area,
    configured_grievance_ticket: GrievanceTicket,
    detail_url_name: str,
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
        ],
        afghanistan,
        whole_business_area_access=True,
    )
    set_admin_area_limits_in_program(partner, program, [area2])

    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(configured_grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_grievance_detail_with_permissions_in_program(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    configured_grievance_ticket: GrievanceTicket,
    detail_url_name: str,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
    existing_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
        ],
        afghanistan,
        program=program,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(configured_grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    ("permissions", "area_limit", "expected_status_1", "expected_status_2"),
    [
        (
            [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            False,
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ),
        (
            [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR],
            False,
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ),
        (
            [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER],
            False,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_404_NOT_FOUND,
        ),
        (
            [Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE],
            False,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_200_OK,
        ),
        (
            [Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR],
            False,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_404_NOT_FOUND,
        ),
        (
            [Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER],
            False,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_200_OK,
        ),
        (
            [
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
            ],
            False,
            status.HTTP_200_OK,
            status.HTTP_200_OK,
        ),
        (
            [
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
            ],
            True,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_200_OK,
        ),
    ],
)
def test_grievance_ticket_detail_access_based_on_permissions(
    permissions: list,
    area_limit: bool,
    expected_status_1: int,
    expected_status_2: int,
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    user2: User,
    partner: Partner,
    area1: Area,
    area2: Area,
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        program=program,
    )
    grievance_ticket_non_sensitive_with_creator = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
    )
    grievance_ticket_non_sensitive_with_creator.programs.add(program)
    grievance_ticket_sensitive_with_owner = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE,
    )
    grievance_ticket_sensitive_with_owner.created_by = user2
    grievance_ticket_sensitive_with_owner.assigned_to = user
    grievance_ticket_sensitive_with_owner.admin2 = None
    grievance_ticket_sensitive_with_owner.save()
    grievance_ticket_sensitive_with_owner.programs.add(program)
    if area_limit:
        set_admin_area_limits_in_program(partner, program, [area2])

    response_1 = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket_non_sensitive_with_creator.id),
            },
        )
    )
    assert response_1.status_code == expected_status_1

    response_2 = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket_sensitive_with_owner.id),
            },
        )
    )
    assert response_2.status_code == expected_status_2


def test_grievance_detail_household_data_update(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
    existing_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        household_unicef_id=household1.unicef_id,
    )
    ticket_details = TicketHouseholdDataUpdateDetailsFactory(
        ticket=grievance_ticket,
        household=household1,
        household_data={"village": {"value": "Test Village", "approve_status": True}},
    )
    assign_ticket_data(grievance_ticket, ticket_note, grievance_document, program, linked_ticket)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    assert_base_grievance_data(
        data=data,
        grievance_ticket=grievance_ticket,
        linked_ticket=linked_ticket,
        existing_ticket=existing_ticket,
    )
    assert data["payment_record"] is None

    assert data["ticket_details"] == {
        "id": str(ticket_details.id),
        "household_data": ticket_details.household_data,
    }


def test_grievance_detail_individual_data_update(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    individuals1: list[Individual],
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
    existing_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        household_unicef_id=household1.unicef_id,
    )
    ticket_details = TicketIndividualDataUpdateDetailsFactory(
        ticket=grievance_ticket,
        individual=individuals1[0],
        individual_data={"role": {"value": ROLE_ALTERNATE, "approve_status": True}},
    )
    assign_ticket_data(grievance_ticket, ticket_note, grievance_document, program, linked_ticket)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    assert_base_grievance_data(
        data=data,
        grievance_ticket=grievance_ticket,
        linked_ticket=linked_ticket,
        existing_ticket=existing_ticket,
    )
    assert data["payment_record"] is None

    assert data["ticket_details"] == {
        "id": str(ticket_details.id),
        "individual_data": ticket_details.individual_data,
        "role_reassign_data": ticket_details.role_reassign_data,
    }


def test_grievance_detail_add_individual(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
    existing_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        household_unicef_id=household1.unicef_id,
    )
    ticket_details = TicketAddIndividualDetailsFactory(
        ticket=grievance_ticket,
        household=household1,
        approve_status=True,
        individual_data={
            "given_name": "Test",
            "full_name": "Test Example",
            "family_name": "Example",
            "sex": "MALE",
            "birth_date": date(year=1980, month=2, day=1).isoformat(),
            "marital_status": SINGLE,
            "documents": [],
        },
    )
    assign_ticket_data(grievance_ticket, ticket_note, grievance_document, program, linked_ticket)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    assert_base_grievance_data(
        data=data,
        grievance_ticket=grievance_ticket,
        linked_ticket=linked_ticket,
        existing_ticket=existing_ticket,
    )
    assert data["payment_record"] is None

    assert data["ticket_details"] == {
        "id": str(ticket_details.id),
        "individual_data": ticket_details.individual_data,
        "approve_status": ticket_details.approve_status,
    }


def test_grievance_detail_delete_individual(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    individuals1: list[Individual],
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
    existing_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
        household_unicef_id=household1.unicef_id,
    )
    role_primary = IndividualRoleInHousehold.objects.get(
        role=ROLE_PRIMARY,
        household=household1,
    )
    role_primary.individual = individuals1[0]
    role_primary.save()
    ticket_details = TicketDeleteIndividualDetailsFactory(
        ticket=grievance_ticket,
        individual=individuals1[0],
        approve_status=True,
        role_reassign_data={
            str(role_primary.id): {
                "role": ROLE_PRIMARY,
                "household": str(household1.id),
                "individual": str(individuals1[1].id),
            }
        },
    )
    assign_ticket_data(grievance_ticket, ticket_note, grievance_document, program, linked_ticket)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    assert_base_grievance_data(
        data=data,
        grievance_ticket=grievance_ticket,
        linked_ticket=linked_ticket,
        existing_ticket=existing_ticket,
    )
    assert data["payment_record"] is None

    assert data["ticket_details"] == {
        "id": str(ticket_details.id),
        "role_reassign_data": ticket_details.role_reassign_data,
        "approve_status": ticket_details.approve_status,
    }


def test_grievance_detail_delete_household(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    household2: Household,
    individuals1: list[Individual],
    individuals2: list[Individual],
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
    existing_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
        household_unicef_id=household1.unicef_id,
    )
    role_primary = IndividualRoleInHousehold.objects.get(
        role=ROLE_PRIMARY,
        household=household1,
    )
    ticket_details = TicketDeleteHouseholdDetailsFactory(
        ticket=grievance_ticket,
        household=household1,
        approve_status=True,
        reason_household=household2,
        role_reassign_data={
            str(role_primary.id): {
                "role": ROLE_PRIMARY,
                "household": str(household2.id),
                "individual": str(individuals2[0].id),
            }
        },
    )
    assign_ticket_data(grievance_ticket, ticket_note, grievance_document, program, linked_ticket)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    assert_base_grievance_data(
        data=data,
        grievance_ticket=grievance_ticket,
        linked_ticket=linked_ticket,
        existing_ticket=existing_ticket,
    )
    assert data["payment_record"] is None

    assert data["ticket_details"] == {
        "id": str(ticket_details.id),
        "approve_status": ticket_details.approve_status,
        "role_reassign_data": ticket_details.role_reassign_data,
        "reason_household": {
            "id": str(ticket_details.reason_household.id),
            "unicef_id": ticket_details.reason_household.unicef_id,
            "admin1": {
                "id": str(ticket_details.reason_household.admin1.id),
                "name": ticket_details.reason_household.admin1.name,
            },
            "admin2": {
                "id": str(ticket_details.reason_household.admin2.id),
                "name": ticket_details.reason_household.admin2.name,
            },
            "admin3": None,
            "admin4": None,
            "first_registration_date": ticket_details.reason_household.first_registration_date.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "last_registration_date": ticket_details.reason_household.last_registration_date.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "total_cash_received": None,
            "total_cash_received_usd": None,
            "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
            "start": ticket_details.reason_household.start.strftime("%Y-%m-%dT%H:%M:%SZ")
            if ticket_details.reason_household.start
            else None,
            "zip_code": None,
            "residence_status": ticket_details.reason_household.get_residence_status_display(),
            "country_origin": ticket_details.reason_household.country_origin.name,
            "country": ticket_details.reason_household.country.name,
            "address": ticket_details.reason_household.address,
            "village": ticket_details.reason_household.village,
            "geopoint": None,
            "import_id": ticket_details.reason_household.unicef_id,
            "program_slug": program.slug,
        },
    }


def test_grievance_detail_system_flagging(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    country: Country,
    household1: Household,
    individuals1: list[Individual],
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
    existing_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
        household_unicef_id=household1.unicef_id,
    )
    sanction_list_individual = SanctionListIndividualFactory(full_name="Sanction Individual")
    sanction_list_individual_document = SanctionListIndividualDocumentFactory(
        individual=sanction_list_individual,
        document_number="123-456-789",
        type_of_document="DOC",
    )
    sanction_list_date_of_birth = SanctionListIndividualDateOfBirthFactory(
        individual=sanction_list_individual,
        date=date(year=1980, month=2, day=1),
    )
    golden_records_individual = individuals1[0]
    golden_records_individual.deduplication_golden_record_status = DUPLICATE
    golden_records_individual.deduplication_golden_record_results = {
        "duplicates": [
            {
                "hit_id": str(golden_records_individual.pk),
                "score": 9.0,
                "proximity_to_score": 3.0,
            }
        ],
        "possible_duplicates": [{"hit_id": str(golden_records_individual.pk)}],
    }
    golden_records_individual.save()
    document_type = DocumentTypeFactory()
    document = DocumentFactory(
        document_number="123-456-789",
        type=document_type,
        individual=golden_records_individual,
        program=program,
        country=country,
    )
    ticket_details = TicketSystemFlaggingDetailsFactory(
        ticket=grievance_ticket,
        golden_records_individual=golden_records_individual,
        sanction_list_individual=sanction_list_individual,
        approve_status=True,
    )
    assign_ticket_data(grievance_ticket, ticket_note, grievance_document, program, linked_ticket)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    assert_base_grievance_data(
        data=data,
        grievance_ticket=grievance_ticket,
        linked_ticket=linked_ticket,
        existing_ticket=existing_ticket,
    )
    assert data["payment_record"] is None

    ticket_details_data = data["ticket_details"]
    assert ticket_details_data["id"] == str(ticket_details.id)
    assert ticket_details_data["approve_status"] == ticket_details.approve_status
    assert ticket_details_data["role_reassign_data"] == ticket_details.role_reassign_data
    assert ticket_details_data["golden_records_individual"] == {
        "id": str(golden_records_individual.id),
        "unicef_id": golden_records_individual.unicef_id,
        "full_name": golden_records_individual.full_name,
        "birth_date": f"{golden_records_individual.birth_date:%Y-%m-%d}",
        "last_registration_date": f"{golden_records_individual.last_registration_date:%Y-%m-%d}",
        "sex": golden_records_individual.sex,
        "duplicate": golden_records_individual.duplicate,
        "program_slug": golden_records_individual.program.slug,
        "household": {
            "id": str(golden_records_individual.household.id),
            "unicef_id": golden_records_individual.household.unicef_id,
            "admin1": {
                "id": str(golden_records_individual.household.admin1.id),
                "name": golden_records_individual.household.admin1.name,
            },
            "admin2": {
                "id": str(golden_records_individual.household.admin2.id),
                "name": golden_records_individual.household.admin2.name,
            },
            "admin3": None,
            "admin4": None,
            "country": golden_records_individual.household.country.name,
            "country_origin": golden_records_individual.household.country_origin.name,
            "address": golden_records_individual.household.address,
            "village": golden_records_individual.household.village,
            "geopoint": golden_records_individual.household.geopoint,
            "first_registration_date": (
                f"{golden_records_individual.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}"
            ),
            "last_registration_date": (
                f"{golden_records_individual.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
            ),
            "total_cash_received": golden_records_individual.household.total_cash_received,
            "total_cash_received_usd": golden_records_individual.household.total_cash_received_usd,
            "delivered_quantities": [
                {
                    "currency": "USD",
                    "total_delivered_quantity": "0.00",
                }
            ],
            "start": f"{golden_records_individual.household.start:%Y-%m-%dT%H:%M:%SZ}",
            "zip_code": golden_records_individual.household.zip_code,
            "residence_status": golden_records_individual.household.get_residence_status_display(),
            "import_id": golden_records_individual.household.unicef_id,
            "program_slug": golden_records_individual.household.program.slug,
        },
        "deduplication_golden_record_results": [
            {
                "hit_id": str(golden_records_individual.pk),
                "unicef_id": golden_records_individual.unicef_id,
                "score": golden_records_individual.deduplication_golden_record_results["duplicates"][0]["score"],
                "proximity_to_score": golden_records_individual.deduplication_golden_record_results["duplicates"][0][
                    "proximity_to_score"
                ],
                "location": "Not provided",
                "age": None,
                "duplicate": False,
                "distinct": False,
            }
        ],
        "documents": [
            {
                "id": str(document.id),
                "type": {
                    "id": str(document.type.id),
                    "label": document.type.label,
                    "key": document.type.key,
                },
                "country": {
                    "id": str(document.country.id),
                    "name": document.country.name,
                    "iso_code3": document.country.iso_code3,
                },
                "document_number": document.document_number,
                "photo": document.photo.url if document.photo else None,
            },
        ],
    }

    assert ticket_details_data["sanction_list_individual"] == {
        "id": str(sanction_list_individual.id),
        "full_name": sanction_list_individual.full_name,
        "reference_number": sanction_list_individual.reference_number,
        "documents": [
            {
                "id": str(sanction_list_individual_document.id),
                "document_number": sanction_list_individual_document.document_number,
                "type_of_document": sanction_list_individual_document.type_of_document,
            }
        ],
        "dates_of_birth": [
            {
                "id": str(sanction_list_date_of_birth.id),
                "date": f"{sanction_list_date_of_birth.date:%Y-%m-%d}",
            }
        ],
        "sanction_list_name": sanction_list_individual.sanction_list.name,
    }


def test_grievance_detail_payment_verification(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
    existing_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        issue_type=None,
        household_unicef_id=household1.unicef_id,
    )
    payment_plan = PaymentPlanFactory(
        name="TEST",
        business_area=afghanistan,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    payment_verification_plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan, status=PaymentVerificationPlan.STATUS_ACTIVE
    )
    payment = PaymentFactory(
        parent=payment_plan,
        household=household1,
        collector=household1.individuals.first(),
        delivered_quantity_usd=50,
        delivered_quantity=100,
        entitlement_quantity=100,
        currency="PLN",
    )
    payment_verification = PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        status_date=timezone.make_aware(datetime(year=2024, month=8, day=25)),
        received_amount=10,
    )
    ticket_details = TicketPaymentVerificationDetailsFactory(
        ticket=grievance_ticket,
        approve_status=True,
        new_status=PaymentVerification.STATUS_RECEIVED,
        old_received_amount=0,
        new_received_amount=20,
        payment_verification_status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        payment_verification=payment_verification,
    )
    assign_ticket_data(grievance_ticket, ticket_note, grievance_document, program, linked_ticket)
    payment_plan.refresh_from_db()

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    assert_base_grievance_data(
        data=data,
        grievance_ticket=grievance_ticket,
        linked_ticket=linked_ticket,
        existing_ticket=existing_ticket,
        delivered_quantities=[
            {"currency": "USD", "total_delivered_quantity": "50.00"},
            {"currency": "PLN", "total_delivered_quantity": "100.00"},
        ],
    )

    assert data["payment_record"] == {
        "id": str(payment.id),
        "unicef_id": payment.unicef_id,
        "parent": {
            "id": str(payment_plan.id),
            "unicef_id": payment_plan.unicef_id,
        },
        "delivered_quantity": f"{payment.delivered_quantity:.2f}",
        "entitlement_quantity": f"{payment.entitlement_quantity:.2f}" if payment.entitlement_quantity else None,
        "verification": payment_verification.id,
    }

    assert data["ticket_details"] == {
        "id": str(ticket_details.id),
        "approve_status": ticket_details.approve_status,
        "new_status": ticket_details.new_status,
        "old_received_amount": f"{ticket_details.old_received_amount:.2f}",
        "new_received_amount": f"{ticket_details.new_received_amount:.2f}",
        "payment_verification_status": ticket_details.payment_verification_status,
        "has_multiple_payment_verifications": False,
        "payment_verification": {
            "id": str(payment_verification.id),
            "status": payment_verification.status,
            "status_date": f"{payment_verification.status_date:%Y-%m-%dT%H:%M:%SZ}",
            "received_amount": f"{payment_verification.received_amount:.2f}",
        },
    }


def test_grievance_detail_needs_adjudication(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    country: Country,
    household1: Household,
    household2: Household,
    individuals1: list[Individual],
    individuals2: list[Individual],
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    ticket_note: Any,
    grievance_document: Any,
    linked_ticket: GrievanceTicket,
    existing_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        household_unicef_id=household1.unicef_id,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
    )
    golden_records_individual, duplicate = sorted(individuals1, key=lambda x: x.id)

    golden_records_individual.deduplication_golden_record_status = DUPLICATE
    golden_records_individual.deduplication_golden_record_results = {
        "duplicates": [
            {
                "hit_id": str(golden_records_individual.pk),
                "score": 9.0,
                "proximity_to_score": 3.0,
            }
        ],
        "possible_duplicates": [{"hit_id": str(golden_records_individual.pk)}],
    }
    golden_records_individual.save()
    document_type = DocumentTypeFactory()
    document = DocumentFactory(
        document_number="123-456-789",
        type=document_type,
        individual=golden_records_individual,
        program=program,
        country=country,
        photo=ContentFile(b"abc", name="doc_aaa.png"),
    )

    dedup_engine_similarity_pair = DeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=golden_records_individual,
        individual2=duplicate,
        similarity_score=0.0,
        status_code="429",
    )
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance_ticket,
        golden_records_individual=golden_records_individual,
        is_multiple_duplicates_version=True,
        possible_duplicate=individuals2[0],
        selected_individual=None,
        role_reassign_data={},
        extra_data={
            "golden_records": [
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(golden_records_individual.pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak",
                    "proximity_to_score": 3.0,
                    "duplicate": False,
                    "distinct": False,
                }
            ],
            "possible_duplicate": [
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(individuals2[0].pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak1",
                    "proximity_to_score": 3.0,
                    "duplicate": True,
                    "distinct": False,
                },
            ],
            "dedup_engine_similarity_pair": {
                "similarity_score": dedup_engine_similarity_pair.similarity_score,
                "status_code": dedup_engine_similarity_pair.status_code,
                "individual1": {
                    "id": str(dedup_engine_similarity_pair.individual1.id),
                    "unicef_id": dedup_engine_similarity_pair.individual1.unicef_id,
                    "full_name": dedup_engine_similarity_pair.individual1.full_name,
                    "photo_name": None,
                },
                "individual2": {
                    "id": str(dedup_engine_similarity_pair.individual2.id),
                    "unicef_id": dedup_engine_similarity_pair.individual2.unicef_id,
                    "full_name": dedup_engine_similarity_pair.individual2.full_name,
                    "photo_name": None,
                },
            },
        },
    )
    ticket_details.possible_duplicates.set([individuals2[0]])
    ticket_details.selected_individuals.set([duplicate])
    assign_ticket_data(grievance_ticket, ticket_note, grievance_document, program, linked_ticket)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    assert_base_grievance_data(
        data=data,
        grievance_ticket=grievance_ticket,
        linked_ticket=linked_ticket,
        existing_ticket=existing_ticket,
    )
    assert data["payment_record"] is None

    ticket_details_data = data["ticket_details"]
    assert ticket_details_data["id"] == str(ticket_details.id)
    assert ticket_details_data["is_multiple_duplicates_version"] == ticket_details.is_multiple_duplicates_version
    assert ticket_details_data["golden_records_individual"] == {
        "id": str(golden_records_individual.id),
        "unicef_id": golden_records_individual.unicef_id,
        "full_name": golden_records_individual.full_name,
        "birth_date": f"{golden_records_individual.birth_date:%Y-%m-%d}",
        "last_registration_date": f"{golden_records_individual.last_registration_date:%Y-%m-%d}",
        "sex": golden_records_individual.sex,
        "duplicate": golden_records_individual.duplicate,
        "program_slug": golden_records_individual.program.slug,
        "household": {
            "id": str(golden_records_individual.household.id),
            "unicef_id": golden_records_individual.household.unicef_id,
            "admin1": {
                "id": str(golden_records_individual.household.admin1.id),
                "name": golden_records_individual.household.admin1.name,
            },
            "admin2": {
                "id": str(golden_records_individual.household.admin2.id),
                "name": golden_records_individual.household.admin2.name,
            },
            "admin3": None,
            "admin4": None,
            "country": golden_records_individual.household.country.name,
            "country_origin": golden_records_individual.household.country_origin.name,
            "address": golden_records_individual.household.address,
            "village": golden_records_individual.household.village,
            "geopoint": golden_records_individual.household.geopoint,
            "first_registration_date": (
                f"{golden_records_individual.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}"
            ),
            "last_registration_date": (
                f"{golden_records_individual.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
            ),
            "total_cash_received": golden_records_individual.household.total_cash_received,
            "total_cash_received_usd": golden_records_individual.household.total_cash_received_usd,
            "delivered_quantities": [
                {
                    "currency": "USD",
                    "total_delivered_quantity": "0.00",
                }
            ],
            "start": f"{golden_records_individual.household.start:%Y-%m-%dT%H:%M:%SZ}",
            "zip_code": golden_records_individual.household.zip_code,
            "residence_status": golden_records_individual.household.get_residence_status_display(),
            "import_id": golden_records_individual.household.unicef_id,
            "program_slug": program.slug,
        },
        "deduplication_golden_record_results": [
            {
                "hit_id": str(golden_records_individual.pk),
                "unicef_id": golden_records_individual.unicef_id,
                "score": golden_records_individual.deduplication_golden_record_results["duplicates"][0]["score"],
                "proximity_to_score": golden_records_individual.deduplication_golden_record_results["duplicates"][0][
                    "proximity_to_score"
                ],
                "location": "Not provided",
                "age": None,
                "duplicate": False,
                "distinct": False,
            }
        ],
        "documents": [
            {
                "id": str(document.id),
                "type": {
                    "id": str(document.type.id),
                    "label": document.type.label,
                    "key": document.type.key,
                },
                "country": {
                    "id": str(document.country.id),
                    "name": document.country.name,
                    "iso_code3": document.country.iso_code3,
                },
                "document_number": document.document_number,
                "photo": document.photo.url if document.photo else None,
            },
        ],
    }
    assert ticket_details_data["possible_duplicate"] == {
        "id": str(individuals2[0].id),
        "unicef_id": individuals2[0].unicef_id,
        "full_name": individuals2[0].full_name,
        "birth_date": f"{individuals2[0].birth_date:%Y-%m-%d}",
        "last_registration_date": f"{individuals2[0].last_registration_date:%Y-%m-%d}",
        "sex": individuals2[0].sex,
        "duplicate": individuals2[0].duplicate,
        "program_slug": individuals2[0].program.slug,
        "household": {
            "id": str(individuals2[0].household.id),
            "unicef_id": individuals2[0].household.unicef_id,
            "admin1": {
                "id": str(individuals2[0].household.admin1.id),
                "name": individuals2[0].household.admin1.name,
            },
            "admin2": {
                "id": str(individuals2[0].household.admin2.id),
                "name": individuals2[0].household.admin2.name,
            },
            "admin3": None,
            "admin4": None,
            "country": individuals2[0].household.country.name,
            "country_origin": individuals2[0].household.country_origin.name,
            "address": individuals2[0].household.address,
            "village": individuals2[0].household.village,
            "geopoint": individuals2[0].household.geopoint,
            "first_registration_date": (f"{individuals2[0].household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}"),
            "last_registration_date": (f"{individuals2[0].household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"),
            "total_cash_received": individuals2[0].household.total_cash_received,
            "total_cash_received_usd": individuals2[0].household.total_cash_received_usd,
            "delivered_quantities": [
                {
                    "currency": "USD",
                    "total_delivered_quantity": "0.00",
                }
            ],
            "start": f"{individuals2[0].household.start:%Y-%m-%dT%H:%M:%SZ}",
            "zip_code": individuals2[0].household.zip_code,
            "residence_status": individuals2[0].household.get_residence_status_display(),
            "import_id": individuals2[0].household.unicef_id,
            "program_slug": program.slug,
        },
        "deduplication_golden_record_results": [],
        "documents": [],
    }
    assert ticket_details_data["possible_duplicates"] == [
        {
            "id": str(individuals2[0].id),
            "unicef_id": individuals2[0].unicef_id,
            "full_name": individuals2[0].full_name,
            "birth_date": f"{individuals2[0].birth_date:%Y-%m-%d}",
            "last_registration_date": f"{individuals2[0].last_registration_date:%Y-%m-%d}",
            "sex": individuals2[0].sex,
            "duplicate": individuals2[0].duplicate,
            "program_slug": individuals2[0].program.slug,
            "household": {
                "id": str(individuals2[0].household.id),
                "unicef_id": individuals2[0].household.unicef_id,
                "admin1": {
                    "id": str(individuals2[0].household.admin1.id),
                    "name": individuals2[0].household.admin1.name,
                },
                "admin2": {
                    "id": str(individuals2[0].household.admin2.id),
                    "name": individuals2[0].household.admin2.name,
                },
                "admin3": None,
                "admin4": None,
                "country": individuals2[0].household.country.name,
                "country_origin": individuals2[0].household.country_origin.name,
                "address": individuals2[0].household.address,
                "village": individuals2[0].household.village,
                "geopoint": individuals2[0].household.geopoint,
                "first_registration_date": (f"{individuals2[0].household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}"),
                "last_registration_date": (f"{individuals2[0].household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"),
                "total_cash_received": individuals2[0].household.total_cash_received,
                "total_cash_received_usd": individuals2[0].household.total_cash_received_usd,
                "delivered_quantities": [
                    {
                        "currency": "USD",
                        "total_delivered_quantity": "0.00",
                    }
                ],
                "start": f"{individuals2[0].household.start:%Y-%m-%dT%H:%M:%SZ}",
                "zip_code": individuals2[0].household.zip_code,
                "residence_status": individuals2[0].household.get_residence_status_display(),
                "import_id": individuals2[0].household.unicef_id,
                "program_slug": program.slug,
            },
            "deduplication_golden_record_results": [],
            "documents": [],
        },
    ]
    assert ticket_details_data["selected_duplicates"] == [
        {
            "id": str(duplicate.id),
            "unicef_id": duplicate.unicef_id,
            "full_name": duplicate.full_name,
            "birth_date": f"{duplicate.birth_date:%Y-%m-%d}",
            "last_registration_date": f"{duplicate.last_registration_date:%Y-%m-%d}",
            "sex": duplicate.sex,
            "duplicate": duplicate.duplicate,
            "program_slug": duplicate.program.slug,
            "household": {
                "id": str(duplicate.household.id),
                "unicef_id": duplicate.household.unicef_id,
                "admin1": {
                    "id": str(duplicate.household.admin1.id),
                    "name": duplicate.household.admin1.name,
                },
                "admin2": {
                    "id": str(duplicate.household.admin2.id),
                    "name": duplicate.household.admin2.name,
                },
                "admin3": None,
                "admin4": None,
                "country": duplicate.household.country.name,
                "country_origin": duplicate.household.country_origin.name,
                "address": duplicate.household.address,
                "village": duplicate.household.village,
                "geopoint": duplicate.household.geopoint,
                "first_registration_date": f"{duplicate.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "last_registration_date": f"{duplicate.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "total_cash_received": duplicate.household.total_cash_received,
                "total_cash_received_usd": duplicate.household.total_cash_received_usd,
                "delivered_quantities": [
                    {
                        "currency": "USD",
                        "total_delivered_quantity": "0.00",
                    }
                ],
                "start": f"{duplicate.household.start:%Y-%m-%dT%H:%M:%SZ}",
                "zip_code": duplicate.household.zip_code,
                "residence_status": duplicate.household.get_residence_status_display(),
                "import_id": duplicate.household.unicef_id,
                "program_slug": program.slug,
            },
            "deduplication_golden_record_results": [],
            "documents": [],
        },
    ]
    assert ticket_details_data["selected_individual"] is None
    assert ticket_details_data["selected_distinct"] == []
    assert ticket_details_data["role_reassign_data"] == ticket_details.role_reassign_data

    assert ticket_details_data["extra_data"] == {
        "golden_records": [
            {
                "unicef_id": golden_records_individual.unicef_id,
                "full_name": ticket_details.extra_data["golden_records"][0]["full_name"],
                "hit_id": ticket_details.extra_data["golden_records"][0]["hit_id"],
                "score": ticket_details.extra_data["golden_records"][0]["score"],
                "proximity_to_score": ticket_details.extra_data["golden_records"][0]["proximity_to_score"],
                "location": ticket_details.extra_data["golden_records"][0]["location"],
                "age": relativedelta(
                    date.today(),
                    parse(ticket_details.extra_data["golden_records"][0]["dob"]),
                ).years,
                "duplicate": ticket_details.extra_data["golden_records"][0]["duplicate"],
                "distinct": ticket_details.extra_data["golden_records"][0]["distinct"],
            }
        ],
        "possible_duplicate": [
            {
                "unicef_id": individuals2[0].unicef_id,
                "full_name": ticket_details.extra_data["possible_duplicate"][0]["full_name"],
                "hit_id": ticket_details.extra_data["possible_duplicate"][0]["hit_id"],
                "score": ticket_details.extra_data["possible_duplicate"][0]["score"],
                "proximity_to_score": ticket_details.extra_data["possible_duplicate"][0]["proximity_to_score"],
                "location": ticket_details.extra_data["possible_duplicate"][0]["location"],
                "age": relativedelta(
                    date.today(),
                    parse(ticket_details.extra_data["possible_duplicate"][0]["dob"]),
                ).years,
                "duplicate": ticket_details.extra_data["possible_duplicate"][0]["duplicate"],
                "distinct": ticket_details.extra_data["possible_duplicate"][0]["distinct"],
            },
        ],
        "dedup_engine_similarity_pair": {},  # No permissions
    }

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_BIOMETRIC_RESULTS],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK

    assert response.data["ticket_details"]["extra_data"]["dedup_engine_similarity_pair"] == {
        "similarity_score": f"{ticket_details.extra_data['dedup_engine_similarity_pair']['similarity_score']:.1f}",
        "status_code": ticket_details.extra_data["dedup_engine_similarity_pair"]["status_code"],
        "individual1": {
            "id": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual1"]["id"],
            "unicef_id": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual1"]["unicef_id"],
            "full_name": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual1"]["full_name"],
            "photo": "",
        },
        "individual2": {
            "id": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual2"]["id"],
            "unicef_id": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual2"]["unicef_id"],
            "full_name": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual2"]["full_name"],
            "photo": "",
        },
    }

    # test only one individual in dedup engine results
    dedup_engine_similarity_pair.individual2 = None
    dedup_engine_similarity_pair.save()
    ticket_details.extra_data["dedup_engine_similarity_pair"]["individual2"] = {
        "id": "",
        "unicef_id": "",
        "full_name": "",
        "photo_name": "",
    }
    ticket_details.save()

    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK

    assert response.data["ticket_details"]["extra_data"]["dedup_engine_similarity_pair"] == {
        "similarity_score": f"{ticket_details.extra_data['dedup_engine_similarity_pair']['similarity_score']:.1f}",
        "status_code": ticket_details.extra_data["dedup_engine_similarity_pair"]["status_code"],
        "individual1": {
            "id": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual1"]["id"],
            "unicef_id": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual1"]["unicef_id"],
            "full_name": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual1"]["full_name"],
            "photo": "",
        },
        "individual2": {
            "id": "",
            "unicef_id": "",
            "full_name": "",
            "photo": "",
        },
    }


def test_grievance_detail_individual_data_update_with_photo(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    individuals1: list[Individual],
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        household_unicef_id=household1.unicef_id,
    )
    TicketIndividualDataUpdateDetailsFactory(
        ticket=grievance_ticket,
        individual=individuals1[0],
        individual_data={
            "photo": {
                "value": "photos/new_photo.jpg",
                "previous_value": "photos/old_photo.jpg",
                "approve_status": False,
            }
        },
    )
    grievance_ticket.programs.add(program)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    # Verify photo URLs are serialized correctly
    photo_data = data["ticket_details"]["individual_data"]["photo"]
    assert "photos/new_photo.jpg" in photo_data["value"]
    assert "photos/old_photo.jpg" in photo_data["previous_value"]


def test_grievance_detail_individual_data_update_with_photo_value_only(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    individuals1: list[Individual],
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        household_unicef_id=household1.unicef_id,
    )
    TicketIndividualDataUpdateDetailsFactory(
        ticket=grievance_ticket,
        individual=individuals1[0],
        individual_data={
            "photo": {
                "value": "photos/new_photo.jpg",
                "previous_value": "",
                "approve_status": False,
            }
        },
    )
    grievance_ticket.programs.add(program)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    photo_data = data["ticket_details"]["individual_data"]["photo"]
    assert "photos/new_photo.jpg" in photo_data["value"]
    assert photo_data["previous_value"] == ""


def test_grievance_detail_add_individual_with_photo(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        household_unicef_id=household1.unicef_id,
    )
    TicketAddIndividualDetailsFactory(
        ticket=grievance_ticket,
        household=household1,
        approve_status=True,
        individual_data={
            "given_name": "Test",
            "full_name": "Test Example",
            "family_name": "Example",
            "sex": "MALE",
            "birth_date": date(year=1980, month=2, day=1).isoformat(),
            "marital_status": SINGLE,
            "documents": [],
            "photo": "photos/individual_photo.jpg",
        },
    )
    grievance_ticket.programs.add(program)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data

    # Verify photo URL is serialized correctly
    assert "photos/individual_photo.jpg" in data["ticket_details"]["individual_data"]["photo"]


def test_grievance_detail_individual_data_update_no_photo(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    individuals1: list[Individual],
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        household_unicef_id=household1.unicef_id,
    )
    TicketIndividualDataUpdateDetailsFactory(
        ticket=grievance_ticket,
        individual=individuals1[0],
        individual_data={
            "full_name": {
                "value": "New Name",
                "previous_value": "Old Name",
                "approve_status": False,
            }
        },
    )
    grievance_ticket.programs.add(program)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data
    assert "photo" not in data["ticket_details"]["individual_data"]


def test_grievance_detail_add_individual_no_photo(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        household_unicef_id=household1.unicef_id,
    )
    TicketAddIndividualDetailsFactory(
        ticket=grievance_ticket,
        household=household1,
        approve_status=True,
        individual_data={
            "given_name": "Test",
            "full_name": "Test Example",
            "family_name": "Example",
            "sex": "MALE",
            "birth_date": date(year=1980, month=2, day=1).isoformat(),
            "marital_status": SINGLE,
            "documents": [],
        },
    )
    grievance_ticket.programs.add(program)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data
    assert "photo" not in data["ticket_details"]["individual_data"]


def test_grievance_detail_individual_data_update_null_individual_data(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    individuals1: list[Individual],
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        household_unicef_id=household1.unicef_id,
    )
    TicketIndividualDataUpdateDetailsFactory(
        ticket=grievance_ticket,
        individual=individuals1[0],
        individual_data=None,
    )
    grievance_ticket.programs.add(program)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data
    assert data["ticket_details"]["individual_data"] is None


def test_grievance_detail_add_individual_null_individual_data(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    household1: Household,
    grievance_ticket_base_data: dict,
    detail_url_name: str,
    create_user_role_with_permissions: Callable,
) -> None:
    grievance_ticket = GrievanceTicketFactory(
        **grievance_ticket_base_data,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        household_unicef_id=household1.unicef_id,
    )
    TicketAddIndividualDetailsFactory(
        ticket=grievance_ticket,
        household=household1,
        approve_status=True,
        individual_data=None,
    )
    grievance_ticket.programs.add(program)

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
        afghanistan,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        reverse(
            detail_url_name,
            kwargs={
                "business_area_slug": afghanistan.slug,
                "pk": str(grievance_ticket.id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data
    assert data["ticket_details"]["individual_data"] is None
