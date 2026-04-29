import os
import tempfile
from typing import Any
from unittest.mock import patch

from django.core.files.storage import default_storage
from django.test.utils import override_settings
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
    ProgramFactory,
    RegistrationDataImportFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.api.endpoints.rdi.lax import IndividualSerializer
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import DISABLED, IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
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
from hope.models.household import BLANK, NONE, NOT_COLLECTED, NOT_DISABLED, NOT_PROVIDED

pytestmark = pytest.mark.django_db


# ── Shared fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def document_type() -> Any:
    return DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE])


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


# ── CreateLaxIndividuals tests ───────────────────────────────────────────


def test_create_single_individual_success(
    lax_api_client, lax_push_url, document_type, afghanistan_country, django_assert_max_num_queries
):
    individual_data = {
        "individual_id": "IND001",
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
        "country_workspace_id": 42,
    }

    with django_assert_max_num_queries(35):
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
    assert individual.country_workspace_id == 42


def test_create_single_individual_account_with_explicit_fi(
    lax_api_client, lax_push_url, bank_account_type, financial_institution
):
    individual_data = {
        "individual_id": "IND001",
        "country_workspace_id": 100,
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
        "individual_id": "IND001",
        "country_workspace_id": 101,
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
            "individual_id": "IND001",
            "country_workspace_id": 110,
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "observed_disability": ["NONE"],
            "marital_status": "SINGLE",
        },
        {
            "individual_id": "IND002",
            "country_workspace_id": 111,
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
        "individual_id": "IND001",
        "country_workspace_id": 120,
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
            "individual_id": "IND001",
            "country_workspace_id": 130,
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "observed_disability": ["NONE"],
            "marital_status": "SINGLE",
        },
        {
            "individual_id": "IND002",
            "country_workspace_id": 131,
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
        "individual_id": "IND001",
        "country_workspace_id": 140,
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
        "individual_id": "IND001",
        "country_workspace_id": 141,
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


def test_create_individual_with_photo(lax_api_client, lax_push_url, lax_program, base64_image):
    individual_data = {
        "individual_id": "IND001",
        "country_workspace_id": 150,
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
        "photo": base64_image,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0

    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    assert individual.photo is not None
    assert individual.photo.name.startswith(lax_program.code)
    assert individual.photo.name.endswith(".png")


def test_create_individual_with_disability_certificate_picture(lax_api_client, lax_push_url, lax_program, base64_image):
    individual_data = {
        "individual_id": "IND001",
        "country_workspace_id": 151,
        "full_name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "observed_disability": ["NONE"],
        "marital_status": "SINGLE",
        "disability_certificate_picture": base64_image,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0

    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    assert individual.disability_certificate_picture is not None
    assert individual.disability_certificate_picture.name.startswith(lax_program.code)
    assert individual.disability_certificate_picture.name.endswith(".png")


def test_create_individual_with_document_image(
    lax_api_client, lax_push_url, lax_program, base64_image, document_type, afghanistan_country
):
    individual_data = {
        "individual_id": "IND001",
        "country_workspace_id": 152,
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
                "image": base64_image,
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
    assert document.photo is not None
    assert document.photo.name.startswith(lax_program.code)
    assert document.photo.name.endswith(".png")


def test_phone_number_validation_flags(lax_api_client, lax_push_url):
    individuals_data = [
        {
            "individual_id": "IND_VALID_PHONE",
            "country_workspace_id": 160,
            "full_name": "Valid Phone",
            "given_name": "Valid",
            "family_name": "Phone",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "phone_no": "+48609456789",
            "phone_no_alternative": "+48500100200",
        },
        {
            "individual_id": "IND_NO_PHONE",
            "country_workspace_id": 161,
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


def test_file_cleanup_on_failure(
    lax_api_client, lax_push_url, lax_rdi, base64_image, document_type, afghanistan_country
):
    individual_data = {
        "individual_id": "IND_CLEANUP",
        "country_workspace_id": 170,
        "full_name": "Jane Doe",
        "given_name": "Jane",
        "family_name": "Doe",
        "birth_date": "1992-02-02",
        "sex": "FEMALE",
        "documents": [
            {
                "type": document_type.key,
                "country": "AF",
                "document_number": "DOC987654",
                "issuance_date": "2021-01-01",
                "expiry_date": "2031-01-01",
                "image": base64_image,
            }
        ],
        "photo": base64_image,
    }

    with tempfile.TemporaryDirectory() as media_root:
        with override_settings(MEDIA_ROOT=media_root):

            def fail_after_files_exist(*args: list[Any]) -> None:
                pre_cleanup_files = []
                for root, _, files in os.walk(media_root):
                    pre_cleanup_files.extend(os.path.join(root, f) for f in files)
                assert len(pre_cleanup_files) > 0
                raise RuntimeError("forced failure for cleanup test")

            with patch(
                "hope.api.endpoints.rdi.lax.CreateLaxIndividuals._bulk_create_accounts",
                side_effect=fail_after_files_exist,
            ):
                response = lax_api_client.post(lax_push_url, [individual_data], format="json")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {
                "detail": "Failed to create lax individuals.",
                "rdi_id": str(lax_rdi.id),
            }

            leftover_files = []
            for root, _, files in os.walk(media_root):
                leftover_files.extend(os.path.join(root, f) for f in files)
            assert leftover_files == []


def test_create_individual_default_values(lax_api_client, lax_push_url):
    individual_data = {
        "individual_id": "IND001",
        "country_workspace_id": 180,
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
    assert individual.wallet_name == ""
    assert individual.blockchain_name == ""
    assert individual.wallet_address == ""


# ── IndividualSerializer tests ───────────────────────────────────────────


@pytest.fixture
def serializer_common_data() -> dict[str, str | int]:
    return {
        "birth_date": "2000-01-01",
        "full_name": "John Doe",
        "individual_id": "IND001",
        "country_workspace_id": 190,
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


def test_individual_with_image_flex_field(lax_api_client, lax_push_url, base64_image, individual_image_flex_attribute):
    individual_data = {
        "individual_id": "IND_FLEX_IMG",
        "country_workspace_id": 200,
        "full_name": "Flex Image Test",
        "given_name": "Flex",
        "family_name": "Test",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "individual_photo": base64_image,
    }

    response = lax_api_client.post(lax_push_url, [individual_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1

    individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
    assert "individual_photo" in individual.flex_fields
    assert not individual.flex_fields["individual_photo"].startswith(base64_image[:20])
    assert default_storage.exists(individual.flex_fields["individual_photo"])


def test_image_flex_field_cleanup_on_failure(
    lax_api_client, lax_push_url, lax_rdi, base64_image, individual_image_flex_attribute
):
    individual_data = {
        "individual_id": "IND_FLEX_IMG",
        "country_workspace_id": 201,
        "full_name": "Flex Image Test",
        "given_name": "Flex",
        "family_name": "Test",
        "birth_date": "1990-01-01",
        "sex": "MALE",
        "individual_photo": base64_image,
    }

    with tempfile.TemporaryDirectory() as media_root:
        with override_settings(MEDIA_ROOT=media_root):

            def fail_after_files_exist(*args: Any, **kwargs: Any) -> None:
                pre_cleanup_files = []
                for root, _, files in os.walk(media_root):
                    pre_cleanup_files.extend(os.path.join(root, f) for f in files)
                assert len(pre_cleanup_files) > 0
                raise RuntimeError("forced failure for image flex field cleanup test")

            with patch(
                "hope.api.endpoints.rdi.lax.CreateLaxIndividuals._bulk_create_accounts",
                side_effect=fail_after_files_exist,
            ):
                response = lax_api_client.post(lax_push_url, [individual_data], format="json")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {
                "detail": "Failed to create lax individuals.",
                "rdi_id": str(lax_rdi.id),
            }

            leftover_files = []
            for root, _, files in os.walk(media_root):
                leftover_files.extend(os.path.join(root, f) for f in files)
            assert leftover_files == []
