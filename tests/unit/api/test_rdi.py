import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import (
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    NON_BENEFICIARY,
    ROLE_PRIMARY,
)
from hope.models import (
    BusinessArea,
    FinancialInstitution,
    PendingAccount,
    PendingHousehold,
    Program,
    RegistrationDataImport,
    User,
)

pytestmark = pytest.mark.django_db


def test_create_rdi(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
    imported_by_user: User,
) -> None:
    url = reverse("api:rdi-create", args=[user_business_area.slug])
    data = {
        "name": "aaaa",
        "collect_data_policy": "FULL",
        "program": str(program.id),
        "imported_by_email": imported_by_user.email,
    }

    response = token_api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    rdi = RegistrationDataImport.objects.filter(name="aaaa").first()
    assert rdi is not None
    assert rdi.program == program
    assert rdi.status == RegistrationDataImport.LOADING
    assert rdi.imported_by == imported_by_user
    assert response.json()["id"] == str(rdi.id)


def test_create_rdi_permission_denied_for_invalid_email(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
) -> None:
    url = reverse("api:rdi-create", args=[user_business_area.slug])
    data = {
        "name": "aaaa",
        "collect_data_policy": "FULL",
        "program": str(program.id),
        "imported_by_email": "nonexistentuser@example.com",
    }

    response = token_api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN, str(response.json())
    assert "User with this email does not exist." in str(response.json())


@pytest.fixture
def biometric_program(request, business_area: BusinessArea) -> Program:
    return ProgramFactory(
        status=Program.DRAFT,
        business_area=business_area,
        biometric_deduplication_enabled=request.param,
    )


@pytest.mark.parametrize(
    ("biometric_program", "expected_dedup_status"),
    [
        (True, RegistrationDataImport.DEDUP_ENGINE_PENDING),
        (False, None),
    ],
    indirect=["biometric_program"],
)
def test_create_rdi_biometric_deduplication_status(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    biometric_program: Program,
    expected_dedup_status: str | None,
    imported_by_user: User,
) -> None:
    url = reverse("api:rdi-create", args=[user_business_area.slug])
    data = {
        "name": "rdi_biometric_test",
        "collect_data_policy": "FULL",
        "program": str(biometric_program.id),
        "imported_by_email": imported_by_user.email,
    }

    response = token_api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    rdi = RegistrationDataImport.objects.filter(name="rdi_biometric_test").first()
    assert rdi is not None
    assert rdi.deduplication_engine_status == expected_dedup_status


def test_push_creates_household_and_individuals(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    program: Program,
    rdi_loading: RegistrationDataImport,
    financial_institution: FinancialInstitution,
    afghanistan_country,
    birth_certificate_doc_type,
    bank_account_type,
    generic_bank,
    base64_image: str,
) -> None:
    url = reverse("api:rdi-push", args=[user_business_area.slug, str(rdi_loading.id)])
    input_data = [
        {
            "residence_status": "",
            "village": "village1",
            "country": "AF",
            "members": [
                {
                    "relationship": HEAD,
                    "full_name": "James Head #1",
                    "birth_date": "2000-01-01",
                    "sex": "MALE",
                    "photo": base64_image,
                    "role": "",
                    "documents": [
                        {
                            "document_number": 10,
                            "image": base64_image,
                            "country": "AF",
                            "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
                        }
                    ],
                    "accounts": [
                        {
                            "type": "bank",
                            "number": "123",
                            "data": {"field_name": "field_value"},
                            "financial_institution": financial_institution.id,
                        },
                        {
                            "type": "bank",
                            "number": "444",
                            "data": {"field_name": "field_value"},
                        },
                    ],
                },
                {
                    "relationship": NON_BENEFICIARY,
                    "full_name": "Mary Primary #1",
                    "birth_date": "2000-01-01",
                    "role": ROLE_PRIMARY,
                    "sex": "FEMALE",
                },
            ],
            "size": 1,
        }
    ]

    response = token_api_client.post(url, input_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    data = response.json()
    rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
    assert rdi is not None
    hh = PendingHousehold.objects.filter(registration_data_import=rdi, village="village1").first()
    assert hh is not None
    assert hh.head_of_household is not None
    assert hh.primary_collector is not None
    assert hh.alternate_collector is None
    assert hh.program_id == program.id
    assert hh.primary_collector.full_name == "Mary Primary #1"
    assert hh.head_of_household.full_name == "James Head #1"
    assert hh.head_of_household.photo is not None
    account_1 = PendingAccount.objects.filter(individual=hh.head_of_household).order_by("number").first()
    account_2 = PendingAccount.objects.filter(individual=hh.head_of_household).order_by("number").last()
    assert account_1 is not None
    assert account_1.account_type.key == "bank"
    assert account_1.financial_institution.name == "mbank"
    assert account_1.number == "123"
    assert account_1.data == {"field_name": "field_value"}
    assert account_2 is not None
    assert account_2.account_type.key == "bank"
    assert account_2.financial_institution.name == "Generic Bank"
    assert account_2.number == "444"
    assert account_2.data == {"field_name": "field_value"}
    assert hh.primary_collector.program_id == program.id
    assert hh.head_of_household.program_id == program.id
    assert data["households"] == 1
    assert data["individuals"] == 2


@pytest.fixture
def rdi_in_review(business_area: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        status=RegistrationDataImport.IN_REVIEW,
        number_of_individuals=0,
        number_of_households=0,
    )


def test_push_returns_404_when_rdi_not_loading(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    rdi_in_review: RegistrationDataImport,
) -> None:
    url = reverse("api:rdi-push", args=[user_business_area.slug, str(rdi_in_review.id)])

    response = token_api_client.post(url, [], format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_complete_transitions_rdi_to_in_review(
    token_api_client: APIClient,
    user_business_area: BusinessArea,
    rdi_loading: RegistrationDataImport,
) -> None:
    url = reverse("api:rdi-complete", args=[user_business_area.slug, str(rdi_loading.id)])

    response = token_api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_200_OK, str(response.json())
    data = response.json()
    assert data[0] == {"id": str(rdi_loading.id), "status": "IN_REVIEW"}
    rdi_loading.refresh_from_db()
    assert rdi_loading.status == RegistrationDataImport.IN_REVIEW
