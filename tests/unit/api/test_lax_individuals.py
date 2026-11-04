from collections.abc import Callable
from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    APITokenFactory,
    BusinessAreaFactory,
    DocumentTypeFactory,
    FinancialInstitutionFactory,
    FlexibleAttributeFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.api.endpoints.rdi.lax import IndividualSerializer
from hope.api.endpoints.rdi.stored_images import get_stored_image_prefix
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import (
    BLANK,
    DISABLED,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE,
    NONE,
    NOT_COLLECTED,
    NOT_DISABLED,
    NOT_PROVIDED,
)
from hope.models import (
    AccountType,
    FinancialInstitution,
    FlexibleAttribute,
    PendingAccount,
    PendingDocument,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)
from hope.models.grant import Grant

pytestmark = pytest.mark.django_db

PHOTO_MAX_LENGTH = PendingIndividual._meta.get_field("photo").max_length


# ── Shared fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def document_type() -> Any:
    return DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE])


@pytest.fixture
def disability_certificate_document_type() -> Any:
    return DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE])


@pytest.fixture
def financial_institution() -> Any:
    return FinancialInstitutionFactory()


@pytest.fixture
def generic_bank() -> FinancialInstitution:
    fi, _ = FinancialInstitution.objects.get_or_create(
        name="Generic Bank",
        defaults={"type": FinancialInstitution.FinancialInstitutionType.BANK},
    )
    return fi


@pytest.fixture
def bank_account_type() -> Any:
    account_type, _ = AccountType.objects.get_or_create(key="bank")
    return account_type


@pytest.fixture
def lax_business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def lax_program(lax_business_area) -> Program:
    return ProgramFactory(status=Program.DRAFT, business_area=lax_business_area)


@pytest.fixture
def lax_rdi(lax_business_area, lax_program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=lax_business_area,
        number_of_individuals=0,
        number_of_households=0,
        status=RegistrationDataImport.LOADING,
        program=lax_program,
    )


@pytest.fixture
def lax_api_client(lax_business_area) -> APIClient:
    user = UserFactory()
    role = RoleFactory(name="API Role", permissions=[Grant.API_RDI_CREATE.name])
    RoleAssignmentFactory(user=user, role=role, business_area=lax_business_area)
    token = APITokenFactory(
        user=user,
        grants=[Grant.API_RDI_CREATE.name],
    )
    token.valid_for.set([lax_business_area])
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return client


@pytest.fixture
def lax_push_url(lax_business_area, lax_rdi) -> str:
    return reverse("api:rdi-push-lax-individuals", args=[lax_business_area.slug, str(lax_rdi.id)])


@pytest.fixture
def file_prefix(lax_rdi: RegistrationDataImport) -> str:
    return get_stored_image_prefix(lax_rdi.business_area.code, lax_rdi.program.code)


@pytest.fixture
def stored_image(store_image: Callable[[str], str], file_prefix: str) -> str:
    return store_image(f"{file_prefix}CW_image.png")


@pytest.fixture
def missing_image(file_prefix: str) -> str:
    return f"{file_prefix}does_not_exist.png"


# ── CreateLaxIndividuals tests ───────────────────────────────────────────


def test_create_single_individual_success(lax_api_client, lax_push_url, document_type, afghanistan_country):
    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
        "photo": "",
        "documents": [
            {
                "type": document_type.key,
                "country": "AF",
                "document_number": "DOC123456",
                "issuance_date": "2020-01-01",
                "expiry_date": "2030-01-01",
            }
        ],
        "originating_id": "AUR#123#123",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0
    assert "IND001" in response.data["individual_id_mapping"]

    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    assert individual.full_name == "John Doe"
    assert individual.given_name == "John"
    assert individual.family_name == "Doe"
    assert individual.observed_disability == ["NONE"]
    assert individual.marital_status == "SINGLE"
    assert individual.originating_id == "AUR#123#123"
    assert individual.country_workspace_id == "IND001"


def test_create_individual_with_custom_document_type_key(lax_api_client, lax_push_url, afghanistan_country):
    # `type` is validated against actual DocumentType.key values, not the static
    # IDENTIFICATION_TYPE_CHOICE list, so a non-standard key is accepted.
    custom_doc_type = DocumentTypeFactory(key="test_type", label="Test Type")
    individual_data = {
        "individual_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "country_workspace_id": "123123123",
        "documents": [
            {
                "type": "test_type",
                "country": "AF",
                "document_number": "DOC123456",
            }
        ],
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0

    document = PendingDocument.objects.get(document_number="DOC123456")
    assert document.type_id == custom_doc_type.id


def test_create_individual_with_invalid_document_type(lax_api_client, lax_push_url, document_type, afghanistan_country):
    # A `type` that does not match any DocumentType.key is rejected by the serializer.
    individual_data = {
        "individual_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "documents": [
            {
                "type": "does_not_exist",
                "country": "AF",
                "document_number": "DOC123456",
            }
        ],
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1
    assert not PendingDocument.objects.filter(document_number="DOC123456").exists()


def test_create_single_individual_account_with_explicit_fi(
    lax_api_client, lax_push_url, bank_account_type, financial_institution
):
    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "accounts": [
            {
                "type": bank_account_type.key,
                "number": "123456789",
                "financial_institution": financial_institution.id,
                "data": {"field_name": "field_value"},
            }
        ],
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0
    assert "IND001" in response.data["individual_id_mapping"]

    assert PendingIndividual.objects.count() == 1
    assert PendingAccount.objects.count() == 1
    account = PendingAccount.objects.first()
    assert account.number == "123456789"
    assert account.financial_institution == financial_institution
    assert account.data == {"field_name": "field_value"}
    assert account.account_type == bank_account_type


def test_create_single_individual_account_defaults_to_generic_bank(
    lax_api_client, lax_push_url, bank_account_type, generic_bank
):
    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "accounts": [
            {
                "type": bank_account_type.key,
                "number": "123456789",
                "data": {"field_name": "field_value"},
            }
        ],
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0

    assert PendingIndividual.objects.count() == 1
    assert PendingAccount.objects.count() == 1
    account = PendingAccount.objects.first()
    assert account.financial_institution.name == "Generic Bank"


def test_create_multiple_individuals_success(lax_api_client, lax_push_url):
    individuals_data = [
        {
            "country_workspace_id": "IND001",
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "observed_disability": ["NONE"],
            "marital_status": "SINGLE",
        },
        {
            "country_workspace_id": "IND002",
            "full_name": "Jane Smith",
            "given_name": "Jane",
            "family_name": "Smith",
            "birth_date": "1992-05-15",
            "sex": "FEMALE",
            "observed_disability": ["NONE"],
            "marital_status": "MARRIED",
        },
    ]

    response = lax_api_client.post(lax_push_url, individuals_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 2
    assert response.data["accepted"] == 2
    assert response.data["errors"] == 0
    assert len(response.data["individual_id_mapping"]) == 2


def test_create_individual_with_validation_errors(lax_api_client, lax_push_url):
    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "INVALID_SEX",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1
    assert len(response.data["individual_id_mapping"]) == 0


def test_create_individuals_mixed_success_and_errors(lax_api_client, lax_push_url):
    individuals_data = [
        {
            "country_workspace_id": "IND001",
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "observed_disability": ["NONE"],
            "marital_status": "SINGLE",
        },
        {
            "country_workspace_id": "IND002",
            "full_name": "",
            "given_name": "Jane",
            "family_name": "Smith",
            "birth_date": "1992-05-15",
            "sex": "FEMALE",
            "observed_disability": ["NONE"],
            "marital_status": "MARRIED",
        },
    ]

    response = lax_api_client.post(lax_push_url, individuals_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 2
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 1
    assert len(response.data["individual_id_mapping"]) == 1


def test_empty_request_data(lax_api_client, lax_push_url):
    response = lax_api_client.post(lax_push_url, [], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 0
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 0


def test_rdi_not_found(lax_api_client, lax_business_area):
    url = reverse(
        "api:rdi-push-lax-individuals",
        args=[lax_business_area.slug, "00000000-0000-0000-0000-000000000000"],
    )

    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
    }

    response = lax_api_client.post(url, [individual_data], format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, str(response.json())


def test_rdi_not_in_loading_status(lax_api_client, lax_push_url, lax_rdi):
    lax_rdi.status = RegistrationDataImport.IN_REVIEW
    lax_rdi.save()

    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, str(response.json())


def test_create_individual_with_photo(lax_api_client, lax_push_url, stored_image):
    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
        "photo": stored_image,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0

    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    assert individual.photo.name == stored_image


def test_create_individual_with_disability_certificate_picture(lax_api_client, lax_push_url, stored_image):
    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
        "disability_certificate_picture": stored_image,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0

    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    assert individual.disability_certificate_picture.name == stored_image


def test_create_individual_with_document_image(
    lax_api_client, lax_push_url, stored_image, document_type, afghanistan_country
):
    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
        "documents": [
            {
                "type": document_type.key,
                "country": "AF",
                "document_number": "DOC123456",
                "issuance_date": "2020-01-01",
                "expiry_date": "2030-01-01",
                "image": stored_image,
            }
        ],
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")
    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0

    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    document = PendingDocument.objects.get(individual=individual)
    assert document.photo.name == stored_image


def test_create_individual_with_non_default_document_type_is_accepted(
    lax_api_client, lax_push_url, disability_certificate_document_type, afghanistan_country
):
    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
        "documents": [
            {
                "type": "disability_certificate",
                "country": "AF",
                "document_number": "DOC123456",
            }
        ],
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0

    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    document = PendingDocument.objects.get(individual=individual)
    assert document.type.key == "disability_certificate"


def test_retry_with_same_originating_id_does_not_raise_integrity_error(
    lax_api_client, lax_push_url, document_type, afghanistan_country, bank_account_type, generic_bank
):
    individual_data = [
        {
            "country_workspace_id": "IND001",
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "originating_id": "AUR#100#1",
            "documents": [
                {
                    "type": document_type.key,
                    "country": "AF",
                    "document_number": "DOC111",
                }
            ],
            "accounts": [
                {
                    "type": bank_account_type.key,
                    "number": "ACCT111",
                }
            ],
        },
        {
            "country_workspace_id": "IND002",
            "full_name": "Jane Doe",
            "given_name": "Jane",
            "family_name": "Doe",
            "birth_date": "1992-06-15",
            "sex": "FEMALE",
            "originating_id": "AUR#100#2",
        },
    ]

    resp1 = lax_api_client.post(lax_push_url, individual_data, format="json")
    assert resp1.status_code == status.HTTP_201_CREATED, resp1.json()
    assert resp1.data["accepted"] == 2
    assert PendingIndividual.objects.count() == 2
    assert PendingDocument.objects.count() == 1
    assert PendingAccount.objects.count() == 1

    resp2 = lax_api_client.post(lax_push_url, individual_data, format="json")
    assert resp2.status_code == status.HTTP_201_CREATED, resp2.json()
    assert resp2.data["accepted"] == 2

    assert PendingIndividual.objects.count() == 2
    assert PendingDocument.objects.count() == 1
    assert PendingAccount.objects.count() == 1

    assert "IND001" in resp2.data["individual_id_mapping"]
    assert "IND002" in resp2.data["individual_id_mapping"]

    ind1 = PendingIndividual.objects.get(originating_id="AUR#100#1")
    assert ind1.full_name == "John Doe"
    ind2 = PendingIndividual.objects.get(originating_id="AUR#100#2")
    assert ind2.full_name == "Jane Doe"


def test_retry_with_updated_data_reflects_changes(lax_api_client, lax_push_url):
    payload_v1 = [
        {
            "country_workspace_id": "IND001",
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "originating_id": "AUR#200#1",
        },
    ]

    resp1 = lax_api_client.post(lax_push_url, payload_v1, format="json")
    assert resp1.status_code == status.HTTP_201_CREATED

    payload_v2 = [
        {
            "country_workspace_id": "IND001",
            "full_name": "Jonathan Doe",
            "given_name": "Jonathan",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "originating_id": "AUR#200#1",
        },
    ]

    resp2 = lax_api_client.post(lax_push_url, payload_v2, format="json")
    assert resp2.status_code == status.HTTP_201_CREATED
    assert resp2.data["accepted"] == 1
    assert PendingIndividual.objects.count() == 1

    ind = PendingIndividual.objects.get(originating_id="AUR#200#1")
    assert ind.full_name == "Jonathan Doe"
    assert ind.given_name == "Jonathan"


def test_retry_without_originating_id_is_rejected(lax_api_client, lax_push_url):
    payload = [
        {
            "country_workspace_id": "IND_NO_OID",
            "full_name": "No Origin",
            "given_name": "No",
            "family_name": "Origin",
            "birth_date": "1990-01-01",
            "sex": "MALE",
        },
    ]

    resp1 = lax_api_client.post(lax_push_url, payload, format="json")
    assert resp1.status_code == status.HTTP_201_CREATED
    assert PendingIndividual.objects.count() == 1

    resp2 = lax_api_client.post(lax_push_url, payload, format="json")

    assert resp2.status_code == status.HTTP_201_CREATED, str(resp2.json())
    assert resp2.data["accepted"] == 0
    assert resp2.data["errors"] == 1
    assert "country_workspace_id" in resp2.data["results"][0]
    assert PendingIndividual.objects.count() == 1


def test_existing_country_workspace_id_rejected_and_siblings_still_imported(
    lax_api_client, lax_push_url, lax_business_area, lax_program
):
    IndividualFactory(
        business_area=lax_business_area,
        program=lax_program,
        country_workspace_id="IND_TAKEN",
    )
    payload = [
        {
            "country_workspace_id": "IND_TAKEN",
            "full_name": "Already Here",
            "given_name": "Already",
            "family_name": "Here",
            "birth_date": "1990-01-01",
            "sex": "MALE",
        },
        {
            "country_workspace_id": "IND_FRESH",
            "full_name": "Brand New",
            "given_name": "Brand",
            "family_name": "New",
            "birth_date": "1991-02-02",
            "sex": "FEMALE",
        },
    ]

    response = lax_api_client.post(lax_push_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 2
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 1
    assert response.data["results"][0] == {
        "country_workspace_id": [
            "Individual with country_workspace_id 'IND_TAKEN' already exists in this business area."
        ]
    }
    assert list(response.data["individual_id_mapping"]) == ["IND_FRESH"]
    assert PendingIndividual.objects.filter(country_workspace_id="IND_TAKEN").count() == 0


def test_existing_withdrawn_country_workspace_id_allowed(lax_api_client, lax_push_url, lax_business_area, lax_program):
    IndividualFactory(
        business_area=lax_business_area,
        program=lax_program,
        country_workspace_id="IND_WITHDRAWN",
        withdrawn=True,
    )
    payload = [
        {
            "country_workspace_id": "IND_WITHDRAWN",
            "full_name": "Replacement Row",
            "given_name": "Replacement",
            "family_name": "Row",
            "birth_date": "1990-01-01",
            "sex": "MALE",
        },
    ]

    response = lax_api_client.post(lax_push_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0
    assert PendingIndividual.objects.filter(country_workspace_id="IND_WITHDRAWN").count() == 1


def test_existing_removed_country_workspace_id_allowed(lax_api_client, lax_push_url, lax_business_area, lax_program):
    IndividualFactory(
        business_area=lax_business_area,
        program=lax_program,
        country_workspace_id="IND_REMOVED",
        is_removed=True,
    )
    payload = [
        {
            "country_workspace_id": "IND_REMOVED",
            "full_name": "Replacement Row",
            "given_name": "Replacement",
            "family_name": "Row",
            "birth_date": "1990-01-01",
            "sex": "MALE",
        },
    ]

    response = lax_api_client.post(lax_push_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0
    assert PendingIndividual.objects.filter(country_workspace_id="IND_REMOVED", is_removed=False).count() == 1


def test_existing_country_workspace_id_in_other_business_area_allowed(lax_api_client, lax_push_url):
    other_business_area = BusinessAreaFactory(name="Ukraine", slug="ukraine")
    IndividualFactory(business_area=other_business_area, country_workspace_id="IND_OTHER_BA")
    payload = [
        {
            "country_workspace_id": "IND_OTHER_BA",
            "full_name": "Other Area",
            "given_name": "Other",
            "family_name": "Area",
            "birth_date": "1990-01-01",
            "sex": "MALE",
        },
    ]

    response = lax_api_client.post(lax_push_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0
    assert "IND_OTHER_BA" in response.data["individual_id_mapping"]


def test_retry_with_same_originating_id_allowed_despite_existing_country_workspace_id(lax_api_client, lax_push_url):
    payload = [
        {
            "country_workspace_id": "IND_REPUSH",
            "full_name": "First Version",
            "given_name": "First",
            "family_name": "Version",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "originating_id": "AUR#300#1",
        },
    ]

    resp1 = lax_api_client.post(lax_push_url, payload, format="json")
    assert resp1.status_code == status.HTTP_201_CREATED, str(resp1.json())
    assert resp1.data["accepted"] == 1

    resp2 = lax_api_client.post(lax_push_url, payload, format="json")

    assert resp2.status_code == status.HTTP_201_CREATED, str(resp2.json())
    assert resp2.data["accepted"] == 1
    assert resp2.data["errors"] == 0
    assert PendingIndividual.objects.filter(country_workspace_id="IND_REPUSH").count() == 1


def test_duplicate_country_workspace_id_within_payload_rejected(lax_api_client, lax_push_url):
    payload = [
        {
            "country_workspace_id": "IND_TWICE",
            "full_name": "First Twin",
            "given_name": "First",
            "family_name": "Twin",
            "birth_date": "1990-01-01",
            "sex": "MALE",
        },
        {
            "country_workspace_id": "IND_TWICE",
            "full_name": "Second Twin",
            "given_name": "Second",
            "family_name": "Twin",
            "birth_date": "1991-02-02",
            "sex": "FEMALE",
        },
    ]

    response = lax_api_client.post(lax_push_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 2
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 2
    assert response.data["results"][0] == {
        "country_workspace_id": ["country_workspace_id 'IND_TWICE' is duplicated within this payload."]
    }
    assert PendingIndividual.objects.filter(country_workspace_id="IND_TWICE").count() == 0


def test_phone_number_validation_flags(lax_api_client, lax_push_url):
    individuals_data = [
        {
            "country_workspace_id": "IND_VALID_PHONE",
            "full_name": "Valid Phone",
            "given_name": "Valid",
            "family_name": "Phone",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "phone_no": "+48609456789",
            "phone_no_alternative": "+48500100200",
        },
        {
            "country_workspace_id": "IND_NO_PHONE",
            "full_name": "No Phone",
            "given_name": "No",
            "family_name": "Phone",
            "birth_date": "1990-01-01",
            "sex": "MALE",
        },
    ]

    response = lax_api_client.post(lax_push_url, individuals_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 2

    valid = PendingIndividual.objects.get(full_name="Valid Phone")
    assert valid.phone_no_valid is True
    assert valid.phone_no_alternative_valid is True

    no_phone = PendingIndividual.objects.get(full_name="No Phone")
    assert no_phone.phone_no_valid is False
    assert no_phone.phone_no_alternative_valid is False


def test_create_individual_with_missing_photo_file_returns_error(lax_api_client, lax_push_url, missing_image):
    individual_data = {
        "country_workspace_id": "IND_MISSING_PHOTO",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        "photo": missing_image,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1
    assert response.data["results"][0]["photo"] == [f"File '{missing_image}' does not exist in storage."]
    assert not PendingIndividual.objects.filter(country_workspace_id="IND_MISSING_PHOTO").exists()


def test_create_individual_with_missing_document_image_returns_error(
    lax_api_client, lax_push_url, document_type, afghanistan_country, missing_image
):
    individual_data = {
        "country_workspace_id": "IND_MISSING_DOC_IMG",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        "documents": [
            {
                "type": document_type.key,
                "country": "AF",
                "document_number": "DOC123456",
                "image": missing_image,
            }
        ],
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1
    assert response.data["results"][0]["documents"][0]["image"] == [
        f"File '{missing_image}' does not exist in storage."
    ]


def test_create_individual_with_missing_disability_certificate_picture_returns_error(
    lax_api_client, lax_push_url, missing_image
):
    individual_data = {
        "country_workspace_id": "IND_MISSING_DCP",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        "disability_certificate_picture": missing_image,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1
    assert response.data["results"][0]["disability_certificate_picture"] == [
        f"File '{missing_image}' does not exist in storage."
    ]


def test_create_individual_with_file_of_another_program_returns_error(
    lax_api_client, lax_push_url, store_image, file_prefix
):
    individual_data = {
        "country_workspace_id": "IND_OTHER_PROGRAM",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        "photo": store_image("OTH/zz99/CW_ind_1_photo.png"),
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 0
    assert response.data["results"][0]["photo"] == [f"File name must start with '{file_prefix}'."]


def test_create_individual_with_invalid_file_name_returns_error(lax_api_client, lax_push_url):
    individual_data = {
        "country_workspace_id": "IND_BAD_PATH",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        "photo": "../../etc/passwd",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1
    assert response.data["results"][0]["photo"] == ["Invalid file name '../../etc/passwd'."]


def test_create_individual_with_photo_name_longer_than_column_returns_error(lax_api_client, lax_push_url, file_prefix):
    file_name = f"{file_prefix}{'a' * PHOTO_MAX_LENGTH}.png"
    individual_data = {
        "country_workspace_id": "IND_LONG_PATH",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        "photo": file_name,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 0
    assert response.data["results"][0]["photo"] == [f"File name must have no more than {PHOTO_MAX_LENGTH} characters."]


def test_create_individual_with_photo_leading_slash_is_normalized(lax_api_client, lax_push_url, stored_image):
    individual_data = {
        "country_workspace_id": "IND_SLASH",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        "photo": f"/{stored_image}",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1
    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    assert individual.photo.name == stored_image


@pytest.mark.parametrize(
    ("field_name", "empty_value"),
    [("photo", ""), ("disability_certificate_picture", ""), ("disability_certificate_picture", None)],
)
def test_create_individual_with_empty_file_value(lax_api_client, lax_push_url, field_name, empty_value):
    individual_data = {
        "country_workspace_id": "IND_EMPTY_FILE",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        field_name: empty_value,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1
    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    assert not getattr(individual, field_name)


def test_create_individual_default_values(lax_api_client, lax_push_url):
    individual_data = {
        "country_workspace_id": "IND001",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")
    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])

    assert individual.estimated_birth_date is False
    assert individual.marital_status == BLANK
    assert individual.work_status == NOT_PROVIDED
    assert individual.fchild_hoh is False
    assert individual.child_hoh is False
    assert individual.disability == NOT_DISABLED
    assert individual.observed_disability == [NONE]
    assert individual.relationship_confirmed is False


# ── IndividualSerializer tests ───────────────────────────────────────────


@pytest.fixture
def serializer_common_data() -> dict[str, str]:
    return {
        "birth_date": "2000-01-01",
        "full_name": "John Doe",
        "country_workspace_id": "IND001",
    }


def test_individual_serializer_empty_disability(serializer_common_data):
    serializer = IndividualSerializer(data={**serializer_common_data, "disability": ""})
    serializer.is_valid()
    assert serializer.validated_data.get("disability") == NOT_DISABLED


def test_individual_serializer_disability(serializer_common_data):
    serializer = IndividualSerializer(data={**serializer_common_data, "disability": "disabled"})
    serializer.is_valid()
    assert serializer.validated_data.get("disability") == DISABLED


def test_individual_serializer_sex_missing_value(serializer_common_data):
    serializer = IndividualSerializer(data=serializer_common_data)
    serializer.is_valid()
    assert serializer.validated_data["sex"] == NOT_COLLECTED


# ── Flex field image tests ───────────────────────────────────────────────


@pytest.fixture
def individual_image_flex_attribute(db: Any) -> FlexibleAttribute:
    return FlexibleAttributeFactory(
        name="individual_photo_i_f",
        label={"English(EN)": "Individual Photo"},
        type=FlexibleAttribute.IMAGE,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )


def test_individual_with_image_flex_field(lax_api_client, lax_push_url, stored_image, individual_image_flex_attribute):
    individual_data = {
        "country_workspace_id": "IND_FLEX_IMG",
        "full_name": "Flex Image Test",
        "given_name": "Flex",
        "family_name": "Test",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "individual_photo": stored_image,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1

    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    assert individual.flex_fields["individual_photo"] == stored_image


def test_individual_with_missing_image_flex_field_file_returns_error(
    lax_api_client, lax_push_url, individual_image_flex_attribute, missing_image
):
    individual_data = {
        "country_workspace_id": "IND_FLEX_IMG_MISSING",
        "full_name": "Flex Image Test",
        "birth_date": "1990-01-01",
        "individual_photo": missing_image,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1
    assert response.data["results"][0] == {
        "flex_fields": {"individual_photo": [f"File '{missing_image}' does not exist in storage."]}
    }
    assert not PendingIndividual.objects.filter(country_workspace_id="IND_FLEX_IMG_MISSING").exists()


def test_individual_reports_flex_field_and_regular_field_errors_together(
    lax_api_client, lax_push_url, individual_image_flex_attribute, file_prefix
):
    individual_data = {
        "country_workspace_id": "IND_FLEX_AND_PHOTO",
        "full_name": "Flex Image Test",
        "birth_date": "1990-01-01",
        "photo": f"{file_prefix}missing_photo.png",
        "individual_photo": f"{file_prefix}missing_flex.png",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["errors"] == 1
    assert response.data["results"][0] == {
        "photo": [f"File '{file_prefix}missing_photo.png' does not exist in storage."],
        "flex_fields": {"individual_photo": [f"File '{file_prefix}missing_flex.png' does not exist in storage."]},
    }


def test_individual_with_empty_image_flex_field(lax_api_client, lax_push_url, individual_image_flex_attribute):
    individual_data = {
        "country_workspace_id": "IND_FLEX_IMG_EMPTY",
        "full_name": "Flex Image Test",
        "birth_date": "1990-01-01",
        "individual_photo": "",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1


# ── country_workspace_id required-field tests ───────────────────────────


def test_lax_push_without_country_workspace_id_reports_error(lax_api_client, lax_push_url, afghanistan_country):
    individual_data = {
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1
    assert response.data["results"][0] == {"country_workspace_id": ["This field is required."]}
    assert PendingIndividual.objects.count() == 0


def test_lax_push_blank_country_workspace_id_reports_error(lax_api_client, lax_push_url, afghanistan_country):
    individual_data = {
        "country_workspace_id": "",
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1
    assert response.data["results"][0] == {"country_workspace_id": ["This field may not be blank."]}
    assert PendingIndividual.objects.count() == 0


def test_lax_push_null_country_workspace_id_reports_error(lax_api_client, lax_push_url, afghanistan_country):
    individual_data = {
        "country_workspace_id": None,
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1
    assert response.data["results"][0] == {"country_workspace_id": ["This field may not be null."]}
    assert PendingIndividual.objects.count() == 0
