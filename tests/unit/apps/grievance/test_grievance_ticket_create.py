"""Tests for grievance ticket creation functionality."""

from datetime import date
from typing import Any, Callable

from django.core.files.uploadedfile import SimpleUploadedFile
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
from extras.test_utils.factories.payment import (
    AccountFactory,
    AccountTypeFactory,
    FinancialInstitutionFactory,
    PaymentFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
)
from hope.apps.household.const import (
    IDENTIFICATION_TYPE_CHOICE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    RELATIONSHIP_UNKNOWN,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SINGLE,
    UNHCR,
)
from hope.models import (
    BusinessArea,
    DocumentType,
    IndividualRoleInHousehold,
    Program,
)
from hope.models.utils import MergeStatusModel


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def document_types() -> None:
    identification_type_choice = tuple((doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE)
    document_types = []
    for doc_type, label in identification_type_choice:
        document_types.append(DocumentType(label=label, key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[doc_type]))
    DocumentType.objects.bulk_create(document_types, ignore_conflicts=True)


@pytest.fixture
def partner() -> PartnerFactory:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: PartnerFactory) -> UserFactory:
    return UserFactory(partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )


@pytest.fixture
def program_2(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        status=Program.ACTIVE,
        business_area=afghanistan,
    )


@pytest.fixture
def household_with_individuals(afghanistan: BusinessArea, program: Program) -> dict:
    individual = IndividualFactory(
        household=None,
        program=program,
        business_area=afghanistan,
        full_name="Test Individual",
        given_name="Test",
        family_name="Individual",
    )
    household = HouseholdFactory(
        size=1,
        business_area=afghanistan,
        program=program,
        head_of_household=individual,
    )

    individual.household = household
    individual.save()

    return {
        "household": household,
        "individuals": [individual],
    }


@pytest.fixture
def account_data(household_with_individuals: dict) -> dict:
    account_type = AccountTypeFactory(key="bank_account", label="Bank Account")
    financial_institution = FinancialInstitutionFactory()
    account = AccountFactory(
        number="1",
        individual=household_with_individuals["individuals"][0],
        account_type=account_type,
        financial_institution=financial_institution,
    )
    return {
        "account": account,
        "account_type": account_type,
        "financial_institution": financial_institution,
    }


@pytest.fixture
def list_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-list",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status", "create_perm_for_program"),
    [
        ([Permissions.GRIEVANCES_CREATE], status.HTTP_201_CREATED, True),
        ([], status.HTTP_403_FORBIDDEN, True),
        ([Permissions.GRIEVANCES_CREATE], status.HTTP_403_FORBIDDEN, False),
    ],
)
def test_create_grievance_ticket_add_individual(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    program_2: Program,
    household_with_individuals: dict,
    document_types: None,
    list_url: str,
    permissions: list,
    expected_status: int,
    create_perm_for_program: bool,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        program if create_perm_for_program else program_2,
    )

    data = {
        "description": "Test",
        "assigned_to": str(user.id),
        "issue_type": 16,
        "category": 2,
        "consent": True,
        "language": "PL",
        "program": str(program.pk),
        "documentation": [],
        "extras": {
            "issue_type": {
                "add_individual_issue_type_extras": {
                    "household": str(household_with_individuals["household"].id),
                    "individual_data": {
                        "given_name": "Test",
                        "full_name": "Test Test",
                        "family_name": "Romaniak",
                        "sex": "MALE",
                        "birth_date": date(year=1980, month=2, day=1).isoformat(),
                        "marital_status": SINGLE,
                        "estimated_birth_date": False,
                        "relationship": RELATIONSHIP_UNKNOWN,
                        "documents": [
                            {
                                "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                                "country": "POL",
                                "number": "123-123-UX-321",
                                "new_photo": None,
                            }
                        ],
                        "identities": [
                            {
                                "partner": UNHCR,
                                "country": "POL",
                                "number": "2222",
                            }
                        ],
                        "payment_channels": [
                            {
                                "type": "BANK_TRANSFER",
                                "bank_name": "privatbank",
                                "bank_account_number": 2356789789789789,
                                "account_holder_name": "Holder Name 132",
                                "bank_branch_name": "newName 123",
                            },
                        ],
                    },
                }
            }
        },
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketAddIndividualDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, data, format="json")
    resp_data = response.json()

    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert len(resp_data) == 1
        assert GrievanceTicket.objects.all().count() == 1
        assert TicketAddIndividualDetails.objects.all().count() == 1


def test_create_grievance_ticket_update_household(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_with_individuals: dict,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], afghanistan, program)

    data = {
        "description": "Description upd HH",
        "language": "Polish",
        "issue_type": 13,
        "category": 2,
        "consent": True,
        "extras": {
            "issue_type": {
                "household_data_update_issue_type_extras": {
                    "household": str(household_with_individuals["household"].id),
                    "household_data": {
                        "village": "Test Town",
                        "size": 3,
                        "country": "AFG",
                    },
                }
            },
        },
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketHouseholdDataUpdateDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, data, format="json")
    resp_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert len(resp_data) == 1
    assert GrievanceTicket.objects.all().count() == 1
    assert TicketHouseholdDataUpdateDetails.objects.all().count() == 1


def test_create_grievance_ticket_update_individual(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_with_individuals: dict,
    account_data: dict,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], afghanistan, program)

    data = {
        "description": "Upd Ind",
        "language": "Polish",
        "issue_type": 14,
        "category": 2,
        "consent": True,
        "extras": {
            "issue_type": {
                "individual_data_update_issue_type_extras": {
                    "individual": str(household_with_individuals["individuals"][0].pk),
                    "individual_data": {
                        "full_name": "New full_name",
                        "accounts_to_edit": [
                            {
                                "id": str(account_data["account"].pk),
                                "number": "999999999999",
                                "financial_institution": account_data["financial_institution"].pk,
                            }
                        ],
                    },
                }
            },
        },
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketIndividualDataUpdateDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, data, format="json")
    resp_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert len(resp_data) == 1
    assert GrievanceTicket.objects.all().count() == 1
    assert TicketIndividualDataUpdateDetails.objects.all().count() == 1


def test_create_grievance_ticket_update_individual_with_document(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_with_individuals: dict,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD],
        afghanistan,
        program,
    )

    fake_file = SimpleUploadedFile("test.jpeg", b"test file content", content_type="image/jpeg")
    data = {
        "description": "Upd Ind",
        "language": "Polish",
        "issue_type": 14,
        "category": 2,
        "consent": True,
        "extras.issue_type.individual_data_update_issue_type_extras.individual": str(
            household_with_individuals["individuals"][0].pk
        ),
        "extras.issue_type.individual_data_update_issue_type_extras.individual_data.full_name": "New full_name",
        "documentation[0].file": fake_file,
        "documentation[0].name": fake_file.name,
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketIndividualDataUpdateDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, data, format="multipart")
    resp_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert len(resp_data) == 1
    assert GrievanceTicket.objects.all().count() == 1
    assert TicketIndividualDataUpdateDetails.objects.all().count() == 1
    assert GrievanceTicket.objects.first().support_documents.count() == 1


def test_create_grievance_ticket_delete_individual(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_with_individuals: dict,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], afghanistan, program)

    data = {
        "description": "Delete Ind",
        "language": "Polish",
        "issue_type": 15,
        "category": 2,
        "consent": True,
        "extras": {
            "issue_type": {
                "individual_delete_issue_type_extras": {
                    "individual": str(household_with_individuals["individuals"][0].pk),
                }
            },
        },
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketDeleteIndividualDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, data, format="json")
    resp_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert len(resp_data) == 1
    assert GrievanceTicket.objects.all().count() == 1
    assert TicketDeleteIndividualDetails.objects.all().count() == 1


def test_create_grievance_ticket_delete_household(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_with_individuals: dict,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], afghanistan, program)

    data = {
        "description": "Remove HH",
        "language": "Polish",
        "issue_type": 17,
        "category": 2,
        "consent": True,
        "extras": {
            "issue_type": {
                "household_delete_issue_type_extras": {
                    "household": str(household_with_individuals["household"].pk),
                }
            },
        },
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketDeleteHouseholdDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, data, format="json")
    resp_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert len(resp_data) == 1
    assert GrievanceTicket.objects.all().count() == 1
    assert TicketDeleteHouseholdDetails.objects.all().count() == 1


def test_create_grievance_ticket_complaint(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_with_individuals: dict,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], afghanistan, program)

    payment = PaymentFactory(
        household=household_with_individuals["household"],
        collector=household_with_individuals["individuals"][0],
        business_area=afghanistan,
        currency="PLN",
        parent__created_by=user,
        program=program,
    )

    data = {
        "description": "Test Feedback",
        "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        "issue_type": GrievanceTicket.ISSUE_TYPE_FSP_COMPLAINT,
        "language": "Polish, English",
        "consent": True,
        "extras": {
            "category": {
                "grievance_complaint_ticket_extras": {
                    "household": str(household_with_individuals["household"].pk),
                    "individual": str(household_with_individuals["individuals"][0].pk),
                    "payment_record": [str(payment.pk)],
                }
            }
        },
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketComplaintDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, data, format="json")
    resp_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert len(resp_data) == 1
    assert GrievanceTicket.objects.all().count() == 1
    assert TicketComplaintDetails.objects.all().count() == 1


def test_create_grievance_ticket_validation_errors(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], afghanistan, program)

    data = {
        "description": "Test Feedback",
        "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
        "issue_type": GrievanceTicket.ISSUE_TYPE_FSP_COMPLAINT,
        "language": "Polish, English",
        "consent": True,
        "extras": {},
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketComplaintDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Feedback tickets are not allowed to be created through this mutation." in response.json()


def test_create_grievance_ticket_duplicate_roles_not_allowed(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], afghanistan, program)

    individual = IndividualFactory(program=program, business_area=afghanistan, household=None)
    household = HouseholdFactory(program=program, business_area=afghanistan, head_of_household=individual)
    individual.household = household
    individual.save()
    individual_2 = IndividualFactory(program=program, household=household, business_area=afghanistan)

    IndividualRoleInHousehold.objects.create(
        household=household,
        individual=individual_2,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    extras = {
        "issue_type": {
            "household_data_update_issue_type_extras": {
                "household": str(household.pk),
                "household_data": {
                    "village": "New Village",
                    "country": "AGO",
                    "flex_fields": {},
                    "roles": [
                        {"individual": str(individual.pk), "new_role": ROLE_PRIMARY},
                        {"individual": str(individual_2.pk), "new_role": ROLE_PRIMARY},
                    ],
                },
            }
        }
    }

    input_data = {
        "description": "Test update roles",
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "consent": False,
        "language": "",
        "linked_feedback_id": None,
        "issue_type": GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        "extras": extras,
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketComplaintDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, input_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        f"Duplicate roles are not allowed: {ROLE_PRIMARY}"
        in response.json()["extras"]["issue_type"]["household_data_update_issue_type_extras"]["household_data"]["roles"]
    )

    # Test that non-duplicate roles work
    extras["issue_type"]["household_data_update_issue_type_extras"]["household_data"]["roles"] = [
        {"individual": str(individual.pk), "new_role": ROLE_PRIMARY},
        {"individual": str(individual_2.pk), "new_role": ROLE_ALTERNATE},
    ]
    response = client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


def test_create_grievance_ticket_update_individual_with_photo(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_with_individuals: dict,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD],
        afghanistan,
        program,
    )

    fake_photo = SimpleUploadedFile(
        "photo.png",
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82",
        content_type="image/png",
    )

    data = {
        "description": "Update Individual with Photo",
        "language": "Polish",
        "issue_type": 14,
        "category": 2,
        "consent": True,
        "extras.issue_type.individual_data_update_issue_type_extras.individual": str(
            household_with_individuals["individuals"][0].pk
        ),
        "extras.issue_type.individual_data_update_issue_type_extras.individual_data.photo": fake_photo,
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketIndividualDataUpdateDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, data, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED

    ticket = GrievanceTicket.objects.first()
    ticket_details = ticket.individual_data_update_ticket_details
    assert "photo" in ticket_details.individual_data
    assert ticket_details.individual_data["photo"]["value"]
    assert ticket_details.individual_data["photo"]["approve_status"] is False


def test_create_grievance_ticket_update_individual_clear_photo(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_with_individuals: dict,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    # Set photo on individual first
    household_with_individuals["individuals"][0].photo = "photos/existing.jpg"
    household_with_individuals["individuals"][0].save()

    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], afghanistan, program)

    data = {
        "description": "Clear Individual Photo",
        "language": "Polish",
        "issue_type": 14,
        "category": 2,
        "consent": True,
        "extras": {
            "issue_type": {
                "individual_data_update_issue_type_extras": {
                    "individual": str(household_with_individuals["individuals"][0].pk),
                    "individual_data": {
                        "photo": None,
                    },
                }
            }
        },
    }

    client = api_client(user)
    response = client.post(list_url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    ticket = GrievanceTicket.objects.first()
    ticket_details = ticket.individual_data_update_ticket_details
    assert "photo" in ticket_details.individual_data
    assert ticket_details.individual_data["photo"]["value"] == ""
    assert ticket_details.individual_data["photo"]["previous_value"] == "photos/existing.jpg"


def test_create_grievance_ticket_update_individual_photo_previous_value(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_with_individuals: dict,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    # Set photo on individual first
    household_with_individuals["individuals"][0].photo = "photos/old_photo.jpg"
    household_with_individuals["individuals"][0].save()

    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD],
        afghanistan,
        program,
    )

    fake_photo = SimpleUploadedFile(
        "new_photo.png",
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82",
        content_type="image/png",
    )

    data = {
        "description": "Update Individual Photo",
        "language": "Polish",
        "issue_type": 14,
        "category": 2,
        "consent": True,
        "extras.issue_type.individual_data_update_issue_type_extras.individual": str(
            household_with_individuals["individuals"][0].pk
        ),
        "extras.issue_type.individual_data_update_issue_type_extras.individual_data.photo": fake_photo,
    }

    client = api_client(user)
    response = client.post(list_url, data, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED

    ticket = GrievanceTicket.objects.first()
    ticket_details = ticket.individual_data_update_ticket_details
    assert "photo" in ticket_details.individual_data
    assert ticket_details.individual_data["photo"]["value"]
    assert ticket_details.individual_data["photo"]["previous_value"] == "photos/old_photo.jpg"


def test_create_grievance_ticket_add_individual_with_photo(
    api_client: Any,
    user: UserFactory,
    afghanistan: BusinessArea,
    program: Program,
    household_with_individuals: dict,
    document_types: None,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD],
        afghanistan,
        program,
    )

    fake_photo = SimpleUploadedFile(
        "photo.png",
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82",
        content_type="image/png",
    )

    data = {
        "description": "Add Individual with Photo",
        "assigned_to": str(user.id),
        "issue_type": 16,
        "category": 2,
        "consent": True,
        "language": "PL",
        "program": str(program.pk),
        "documentation": [],
        "extras.issue_type.add_individual_issue_type_extras.household": str(household_with_individuals["household"].id),
        "extras.issue_type.add_individual_issue_type_extras.individual_data.given_name": "PhotoTest",
        "extras.issue_type.add_individual_issue_type_extras.individual_data.full_name": "PhotoTest Test",
        "extras.issue_type.add_individual_issue_type_extras.individual_data.family_name": "Test",
        "extras.issue_type.add_individual_issue_type_extras.individual_data.sex": "MALE",
        "extras.issue_type.add_individual_issue_type_extras.individual_data.birth_date": date(
            year=1980, month=2, day=1
        ).isoformat(),
        "extras.issue_type.add_individual_issue_type_extras.individual_data.marital_status": SINGLE,
        "extras.issue_type.add_individual_issue_type_extras.individual_data.estimated_birth_date": False,
        "extras.issue_type.add_individual_issue_type_extras.individual_data.relationship": RELATIONSHIP_UNKNOWN,
        "extras.issue_type.add_individual_issue_type_extras.individual_data.photo": fake_photo,
    }

    assert GrievanceTicket.objects.all().count() == 0
    assert TicketAddIndividualDetails.objects.all().count() == 0

    client = api_client(user)
    response = client.post(list_url, data, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED

    ticket = GrievanceTicket.objects.first()
    ticket_details = ticket.add_individual_ticket_details
    assert "photo" in ticket_details.individual_data
    assert ticket_details.individual_data["photo"]
