from datetime import date
from io import BytesIO
from typing import Any, Callable

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse
from PIL import Image
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentFactory,
    FinancialInstitutionFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import (
    FEMALE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    RELATIONSHIP_UNKNOWN,
    SINGLE,
    UNHCR,
    WIDOWED,
)
from hope.models import (
    AccountType,
    BusinessArea,
    DocumentType,
    Program,
    User,
)

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def generated_document_types() -> None:
    call_command("generatedocumenttypes")


@pytest.fixture
def countries(generated_document_types: None) -> dict[str, Any]:
    afghanistan = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    poland = CountryFactory(
        name="Poland",
        short_name="Poland",
        iso_code2="PL",
        iso_code3="POL",
        iso_num="0616",
    )
    return {"afghanistan": afghanistan, "poland": poland}


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        slug="afghanistan",
    )


@pytest.fixture
def user() -> User:
    partner = PartnerFactory(name="TestPartner")
    return UserFactory(partner=partner, first_name="TestUser")


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
    )


@pytest.fixture
def admin_context(countries: dict[str, Any]) -> dict[str, Any]:
    area_type = AreaTypeFactory(
        name="Admin type one",
        country=countries["afghanistan"],
        area_level=2,
    )
    admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="dffgh565556")
    AreaFactory(name="City Example", area_type=area_type, p_code="fggtyjyj")

    area_type_level_1 = AreaTypeFactory(name="State1", country=countries["afghanistan"], area_level=1)
    area = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")
    return {"admin_area": admin_area, "area": area}


@pytest.fixture
def grievance_context(
    business_area: BusinessArea,
    program: Program,
    countries: dict[str, Any],
    admin_context: dict[str, Any],
) -> dict[str, Any]:
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        country=countries["afghanistan"],
        unicef_id="HH-0001",
        create_role=False,
    )
    individual = IndividualFactory(
        id="b6ffb227-a2dd-4103-be46-0c9ebe9f001a",
        household=household,
        business_area=business_area,
        program=program,
        registration_data_import=household.registration_data_import,
        full_name="Benjamin Butler",
        given_name="Benjamin",
        family_name="Butler",
        phone_no="(953)682-4596",
        birth_date="1943-07-30",
        sex=FEMALE,
        marital_status=WIDOWED,
        estimated_birth_date=False,
        relationship=RELATIONSHIP_UNKNOWN,
    )
    household.head_of_household = individual
    household.save(update_fields=["head_of_household"])

    national_id_type = DocumentType.objects.get(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID])
    national_id = DocumentFactory(
        country=countries["poland"],
        type=national_id_type,
        document_number="789-789-645",
        individual=individual,
    )

    unhcr_partner = PartnerFactory(name=UNHCR, is_un=True)
    identity = IndividualIdentityFactory(
        partner=unhcr_partner,
        individual=individual,
        number="1111",
        country=countries["poland"],
    )
    return {
        "household": household,
        "individual": individual,
        "national_id": national_id,
        "identity": identity,
        "admin_area": admin_context["admin_area"],
        "area": admin_context["area"],
    }


@pytest.fixture
def list_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance-tickets:grievance-tickets-global-list",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def load_test_image() -> Callable[[], SimpleUploadedFile]:
    def _load() -> SimpleUploadedFile:
        image = Image.new("RGB", (8, 8), color=(255, 0, 0))
        file_buffer = BytesIO()
        image.save(file_buffer, format="JPEG")
        file_buffer.seek(0)
        return SimpleUploadedFile("generated-test-image.jpg", file_buffer.read(), content_type="image/jpeg")

    return _load


@pytest.fixture
def grant_create_permission(
    create_user_role_with_permissions: Callable,
    user: User,
    business_area: BusinessArea,
    program: Program,
) -> None:
    create_user_role_with_permissions(user, [Permissions.GRIEVANCES_CREATE], business_area, program)


def test_grievance_create_individual_data_change(
    authenticated_client: Any,
    grant_create_permission: None,
    user: User,
    grievance_context: dict[str, Any],
    list_url: str,
    load_test_image: Callable[[], SimpleUploadedFile],
) -> None:
    extra_path = "extras.issue_type.add_individual_issue_type_extras."
    response = authenticated_client.post(
        list_url,
        {
            "description": "Test",
            "assigned_to": str(user.id),
            "issue_type": GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
            "consent": True,
            "language": "PL",
            f"{extra_path}household": str(grievance_context["household"].id),
            f"{extra_path}individual_data.given_name": "Test",
            f"{extra_path}individual_data.full_name": "Test Test",
            f"{extra_path}individual_data.family_name": "Romaniak",
            f"{extra_path}individual_data.sex": "MALE",
            f"{extra_path}individual_data.birth_date": "1980-02-01",
            f"{extra_path}individual_data.marital_status": SINGLE,
            f"{extra_path}individual_data.estimated_birth_date": False,
            f"{extra_path}individual_data.relationship": RELATIONSHIP_UNKNOWN,
            f"{extra_path}individual_data.documents[0].key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[
                IDENTIFICATION_TYPE_NATIONAL_ID
            ],
            f"{extra_path}individual_data.documents[0].country": "POL",
            f"{extra_path}individual_data.documents[0].number": "123-123-UX-321",
            f"{extra_path}individual_data.documents[0].photo": load_test_image(),
        },
        format="multipart",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data[0]
    assert response.data[0]["ticket_details"]["individual_data"]["documents"][0]["photo"] is not None
    assert response.data[0]["ticket_details"]["individual_data"]["documents"][0]["photoraw"] is not None


def test_grievance_update_individual_data_change(
    authenticated_client: Any,
    grant_create_permission: None,
    user: User,
    grievance_context: dict[str, Any],
    list_url: str,
    load_test_image: Callable[[], SimpleUploadedFile],
) -> None:
    extra_path = "extras.issue_type.individual_data_update_issue_type_extras."
    data = {
        "description": "Test",
        "assigned_to": str(user.id),
        "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "consent": True,
        "language": "PL",
        f"{extra_path}individual": str(grievance_context["individual"].id),
        f"{extra_path}individual_data.given_name": "Test",
        f"{extra_path}individual_data.full_name": "Test Test",
        f"{extra_path}individual_data.sex": "MALE",
        f"{extra_path}individual_data.birth_date": date(year=1980, month=2, day=1).isoformat(),
        f"{extra_path}individual_data.marital_status": SINGLE,
        f"{extra_path}individual_data.preferred_language": "pl-pl",
        f"{extra_path}individual_data.documents[0].key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[
            IDENTIFICATION_TYPE_NATIONAL_PASSPORT
        ],
        f"{extra_path}individual_data.documents[0].country": "POL",
        f"{extra_path}individual_data.documents[0].number": "321-321-XU-987",
        f"{extra_path}individual_data.documents[0].photo": load_test_image(),
        f"{extra_path}individual_data.documents_to_edit[0].id": str(grievance_context["national_id"].id),
        f"{extra_path}individual_data.documents_to_edit[0].key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[
            IDENTIFICATION_TYPE_NATIONAL_ID
        ],
        f"{extra_path}individual_data.documents_to_edit[0].country": "POL",
        f"{extra_path}individual_data.documents_to_edit[0].number": "321-321-XU-123",
        f"{extra_path}individual_data.documents_to_edit[0].new_photo": load_test_image(),
        f"{extra_path}individual_data.identities[0].partner": UNHCR,
        f"{extra_path}individual_data.identities[0].country": "POL",
        f"{extra_path}individual_data.identities[0].number": "2222",
        f"{extra_path}individual_data.identities_to_edit[0].id": str(grievance_context["identity"].id),
        f"{extra_path}individual_data.identities_to_edit[0].partner": UNHCR,
        f"{extra_path}individual_data.identities_to_edit[0].country": "POL",
        f"{extra_path}individual_data.identities_to_edit[0].number": "3333",
        f"{extra_path}individual_data.disability": "disabled",
    }
    response = authenticated_client.post(list_url, data, format="multipart")

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data[0]
    individual_data = response.data[0]["ticket_details"]["individual_data"]
    assert individual_data["documents"][0]["value"]["photo"] is not None
    assert individual_data["documents"][0]["value"]["photoraw"] is not None
    assert individual_data["documents_to_edit"][0]["value"]["photo"] is not None
    assert individual_data["documents_to_edit"][0]["value"]["photoraw"] is not None


def test_create_payment_channel_for_individual(
    authenticated_client: Any,
    grant_create_permission: None,
    user: User,
    grievance_context: dict[str, Any],
    list_url: str,
) -> None:
    input_data = {
        "description": "Test",
        "assigned_to": str(user.id),
        "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "consent": True,
        "language": "PL",
        "extras": {
            "issue_type": {
                "individual_data_update_issue_type_extras": {
                    "individual": str(grievance_context["individual"].id),
                    "individual_data": {
                        "payment_channels": [
                            {
                                "type": "BANK_TRANSFER",
                                "bank_name": "privatbank",
                                "bank_account_number": 2356789789789789,
                                "account_holder_name": "Holder Name 333",
                                "bank_branch_name": "New Branch Name 333",
                            },
                        ],
                    },
                }
            }
        },
    }
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data[0]


def test_grievance_delete_individual_data_change(
    authenticated_client: Any,
    grant_create_permission: None,
    user: User,
    grievance_context: dict[str, Any],
    list_url: str,
) -> None:
    input_data = {
        "description": "Test",
        "assigned_to": str(user.id),
        "issue_type": GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "consent": True,
        "language": "PL",
        "extras": {
            "issue_type": {
                "individual_delete_issue_type_extras": {
                    "individual": str(grievance_context["individual"].id),
                }
            }
        },
    }
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data[0]


def test_grievance_update_household_data_change(
    authenticated_client: Any,
    grant_create_permission: None,
    user: User,
    grievance_context: dict[str, Any],
    list_url: str,
) -> None:
    household = grievance_context["household"]
    household.female_age_group_6_11_count = 2
    household.save(update_fields=["female_age_group_6_11_count"])
    input_data = {
        "description": "Test",
        "assigned_to": str(user.id),
        "issue_type": GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "consent": True,
        "language": "PL",
        "extras": {
            "issue_type": {
                "household_data_update_issue_type_extras": {
                    "household": str(household.id),
                    "household_data": {
                        "female_age_group_6_11_count": 14,
                        "country": "AFG",
                        "size": 4,
                    },
                }
            }
        },
    }
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data[0]


def test_grievance_delete_household_data_change(
    authenticated_client: Any,
    grant_create_permission: None,
    user: User,
    grievance_context: dict[str, Any],
    list_url: str,
) -> None:
    input_data = {
        "description": "Test",
        "assigned_to": str(user.id),
        "issue_type": GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "consent": True,
        "language": "PL",
        "extras": {
            "issue_type": {
                "household_delete_issue_type_extras": {
                    "household": str(grievance_context["household"].id),
                }
            }
        },
    }
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data[0]


def test_grievance_create_household_data_change_with_admin_area(
    authenticated_client: Any,
    grant_create_permission: None,
    grievance_context: dict[str, Any],
    list_url: str,
) -> None:
    input_data = {
        "description": "AreaTest",
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "issue_type": GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        "consent": True,
        "language": "",
        "extras": {
            "issue_type": {
                "household_data_update_issue_type_extras": {
                    "household": str(grievance_context["household"].id),
                    "household_data": {
                        "admin_area_title": grievance_context["area"].p_code,
                        "flexFields": {},
                    },
                }
            }
        },
    }
    response = authenticated_client.post(list_url, input_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data[0]


@pytest.fixture
def account_types() -> dict[str, AccountType]:
    return {
        "bank": AccountTypeFactory(key="bank", label="Bank"),
        "mobile": AccountTypeFactory(key="mobile", label="Mobile"),
    }


def test_create_account_bank_requires_financial_institution(
    authenticated_client: Any,
    grant_create_permission: None,
    user: User,
    grievance_context: dict[str, Any],
    list_url: str,
    account_types: dict[str, AccountType],
) -> None:
    _ = account_types["mobile"]
    input_data_fail = {
        "description": "Test bank account without financial institution",
        "assigned_to": str(user.id),
        "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "consent": True,
        "language": "PL",
        "extras": {
            "issue_type": {
                "individual_data_update_issue_type_extras": {
                    "individual": str(grievance_context["individual"].id),
                    "individual_data": {
                        "accounts": [
                            {
                                "account_type": "bank",
                                "number": "1234567890",
                            }
                        ],
                    },
                }
            }
        },
    }
    response = authenticated_client.post(list_url, input_data_fail, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "financial_institution" in str(response.data).lower()


def test_create_account_bank_with_financial_institution(
    authenticated_client: Any,
    grant_create_permission: None,
    user: User,
    grievance_context: dict[str, Any],
    list_url: str,
    account_types: dict[str, AccountType],
) -> None:
    _ = account_types["bank"]
    _ = account_types["mobile"]
    financial_institution = FinancialInstitutionFactory(name="Test Bank")
    input_data_success = {
        "description": "Test bank account with financial institution",
        "assigned_to": str(user.id),
        "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "consent": True,
        "language": "PL",
        "extras": {
            "issue_type": {
                "individual_data_update_issue_type_extras": {
                    "individual": str(grievance_context["individual"].id),
                    "individual_data": {
                        "accounts": [
                            {
                                "account_type": "bank",
                                "financial_institution": financial_institution.name,
                                "number": "1234567890",
                            }
                        ],
                    },
                }
            }
        },
    }
    response = authenticated_client.post(list_url, input_data_success, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data[0]


@pytest.fixture
def bank_account(
    grievance_context: dict[str, Any],
    account_types: dict[str, AccountType],
) -> dict[str, Any]:
    financial_institution = FinancialInstitutionFactory(name="Test Bank")
    account = AccountFactory(
        individual=grievance_context["individual"],
        account_type=account_types["bank"],
        financial_institution=financial_institution,
        number="1111111111",
    )
    return {"account": account, "financial_institution": financial_institution}


def test_edit_account_bank_requires_financial_institution(
    authenticated_client: Any,
    grant_create_permission: None,
    user: User,
    grievance_context: dict[str, Any],
    list_url: str,
    bank_account: dict[str, Any],
) -> None:
    input_data_fail = {
        "description": "Test edit bank account without financial institution",
        "assigned_to": str(user.id),
        "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "consent": True,
        "language": "PL",
        "extras": {
            "issue_type": {
                "individual_data_update_issue_type_extras": {
                    "individual": str(grievance_context["individual"].id),
                    "individual_data": {
                        "accounts_to_edit": [
                            {
                                "id": str(bank_account["account"].id),
                                "number": "2222222222",
                            }
                        ],
                    },
                }
            }
        },
    }
    response = authenticated_client.post(list_url, input_data_fail, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "financial_institution" in str(response.data).lower()


def test_edit_account_bank_with_financial_institution(
    authenticated_client: Any,
    grant_create_permission: None,
    user: User,
    grievance_context: dict[str, Any],
    list_url: str,
    bank_account: dict[str, Any],
) -> None:
    input_data_success = {
        "description": "Test edit bank account with financial institution",
        "assigned_to": str(user.id),
        "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
        "consent": True,
        "language": "PL",
        "extras": {
            "issue_type": {
                "individual_data_update_issue_type_extras": {
                    "individual": str(grievance_context["individual"].id),
                    "individual_data": {
                        "accounts_to_edit": [
                            {
                                "id": str(bank_account["account"].id),
                                "financial_institution": "New Bank Name",
                                "number": "3333333333",
                            }
                        ],
                    },
                }
            }
        },
    }
    response = authenticated_client.post(list_url, input_data_success, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data[0]
