import base64
import os
from pathlib import Path
import tempfile
from typing import Any
from unittest.mock import patch

from django.core.management import call_command
from django.test.utils import override_settings
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.payment import FinancialInstitutionFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.api.models import Grant
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    PendingDocument,
    PendingIndividual,
)
from hope.apps.payment.models import AccountType
from hope.apps.program.models import Program
from hope.apps.registration_data.models import RegistrationDataImport
from unit.api.base import HOPEApiTestCase


class CreateLaxIndividualsTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = [Grant.API_RDI_CREATE]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        call_command("loadcountrycodes")

        image = Path(__file__).parent / "logo.png"
        cls.base64_encoded_data = base64.b64encode(image.read_bytes()).decode("utf-8")

        cls.document_type = DocumentTypeFactory(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]
        )

        cls.fi = FinancialInstitutionFactory()

        cls.program = ProgramFactory(status=Program.DRAFT, business_area=cls.business_area)

        cls.rdi: RegistrationDataImport = RegistrationDataImportFactory(
            business_area=cls.business_area,
            number_of_individuals=0,
            number_of_households=0,
            status=RegistrationDataImport.LOADING,
            program=cls.program,
        )

        cls.account_type, created = AccountType.objects.get_or_create(
            key="bank", defaults={"label": "Bank", "unique_fields": ["number"]}
        )

        cls.url = reverse("api:rdi-push-lax-individuals", args=[cls.business_area.slug, str(cls.rdi.id)])

    def test_create_single_individual_success(self) -> None:
        individual_data = {
            "individual_id": "IND001",
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "observed_disability": "NONE",
            "marital_status": "SINGLE",
            "photo": "",
            "documents": [
                {
                    "type": self.document_type.key,
                    "country": "AF",
                    "document_number": "DOC123456",
                    "issuance_date": "2020-01-01",
                    "expiry_date": "2030-01-01",
                }
            ],
            "accounts": [
                {
                    "account_type": "bank",
                    "number": "123456789",
                    "financial_institution": self.fi.id,
                    "data": {"field_name": "field_value"},
                }
            ],
        }

        response = self.client.post(self.url, [individual_data], format="json")

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

    def test_create_multiple_individuals_success(self) -> None:
        individuals_data = [
            {
                "individual_id": "IND001",
                "full_name": "John Doe",
                "given_name": "John",
                "family_name": "Doe",
                "birth_date": "1990-01-01",
                "sex": "MALE",
                "observed_disability": "NONE",
                "marital_status": "SINGLE",
            },
            {
                "individual_id": "IND002",
                "full_name": "Jane Smith",
                "given_name": "Jane",
                "family_name": "Smith",
                "birth_date": "1992-05-15",
                "sex": "FEMALE",
                "observed_disability": "NONE",
                "marital_status": "MARRIED",
            },
        ]

        response = self.client.post(self.url, individuals_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 2
        assert response.data["accepted"] == 2
        assert response.data["errors"] == 0
        assert len(response.data["individual_id_mapping"]) == 2

    def test_create_individual_with_validation_errors(self) -> None:
        individual_data = {
            "individual_id": "IND001",
            "full_name": "",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "INVALID_SEX",
            "observed_disability": "NONE",
            "marital_status": "SINGLE",
        }

        response = self.client.post(self.url, [individual_data], format="json")

        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 1
        assert response.data["accepted"] == 0
        assert response.data["errors"] == 1
        assert len(response.data["individual_id_mapping"]) == 0

    def test_create_individuals_mixed_success_and_errors(self) -> None:
        individuals_data = [
            {
                "individual_id": "IND001",
                "full_name": "John Doe",
                "given_name": "John",
                "family_name": "Doe",
                "birth_date": "1990-01-01",
                "sex": "MALE",
                "observed_disability": "NONE",
                "marital_status": "SINGLE",
            },
            {
                "individual_id": "IND002",
                "full_name": "",
                "given_name": "Jane",
                "family_name": "Smith",
                "birth_date": "1992-05-15",
                "sex": "FEMALE",
                "observed_disability": "NONE",
                "marital_status": "MARRIED",
            },
        ]

        response = self.client.post(self.url, individuals_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 2
        assert response.data["accepted"] == 1
        assert response.data["errors"] == 1
        assert len(response.data["individual_id_mapping"]) == 1

    def test_empty_request_data(self) -> None:
        response = self.client.post(self.url, [], format="json")

        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 0
        assert response.data["accepted"] == 0
        assert response.data["errors"] == 0

    def test_rdi_not_found(self) -> None:
        url = reverse(
            "api:rdi-push-lax-individuals",
            args=[self.business_area.slug, "00000000-0000-0000-0000-000000000000"],
        )

        individual_data = {
            "individual_id": "IND001",
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "observed_disability": "NONE",
            "marital_status": "SINGLE",
        }

        response = self.client.post(url, [individual_data], format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND, str(response.json())

    def test_rdi_not_in_loading_status(self) -> None:
        self.rdi.status = RegistrationDataImport.IN_REVIEW
        self.rdi.save()

        individual_data = {
            "individual_id": "IND001",
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "observed_disability": "NONE",
            "marital_status": "SINGLE",
        }

        response = self.client.post(self.url, [individual_data], format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND, str(response.json())

    def test_create_individual_with_photo(self) -> None:
        individual_data = {
            "individual_id": "IND001",
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "observed_disability": "NONE",
            "marital_status": "SINGLE",
            "photo": self.base64_encoded_data,
        }

        response = self.client.post(self.url, [individual_data], format="json")

        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 1
        assert response.data["accepted"] == 1
        assert response.data["errors"] == 0

        individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
        assert individual.photo is not None
        assert individual.photo.name.startswith("photo")
        assert individual.photo.name.endswith(".png")

    def test_create_individual_with_document_image(self) -> None:
        individual_data = {
            "individual_id": "IND001",
            "full_name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1990-01-01",
            "sex": "MALE",
            "observed_disability": "NONE",
            "marital_status": "SINGLE",
            "documents": [
                {
                    "type": self.document_type.key,
                    "country": "AF",
                    "document_number": "DOC123456",
                    "issuance_date": "2020-01-01",
                    "expiry_date": "2030-01-01",
                    "image": self.base64_encoded_data,
                }
            ],
        }

        response = self.client.post(self.url, [individual_data], format="json")
        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 1
        assert response.data["accepted"] == 1
        assert response.data["errors"] == 0

        individual = PendingIndividual.objects.get(unicef_id=list(response.data["individual_id_mapping"].values())[0])
        document = PendingDocument.objects.get(individual=individual)
        assert document.photo is not None
        assert document.photo.name.startswith("photo")
        assert document.photo.name.endswith(".png")

    def test_file_cleanup_on_failure(self) -> None:
        individual_data = {
            "individual_id": "IND_CLEANUP",
            "full_name": "Jane Doe",
            "given_name": "Jane",
            "family_name": "Doe",
            "birth_date": "1992-02-02",
            "sex": "FEMALE",
            "documents": [
                {
                    "type": self.document_type.key,
                    "country": "AF",
                    "document_number": "DOC987654",
                    "issuance_date": "2021-01-01",
                    "expiry_date": "2031-01-01",
                    "image": self.base64_encoded_data,
                }
            ],
            "photo": self.base64_encoded_data,
        }

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):

                def fail_after_files_exist(*args: list[Any]) -> None:
                    pre_cleanup_files = [os.path.join(root, f) for root, _, files in os.walk(media_root) for f in files]
                    assert len(pre_cleanup_files) > 0
                    raise RuntimeError("forced failure for cleanup test")

                with patch(
                    "hope.api.endpoints.rdi.lax.CreateLaxIndividuals._bulk_create_accounts",
                    side_effect=fail_after_files_exist,
                ):
                    with pytest.raises(RuntimeError):
                        self.client.post(self.url, [individual_data], format="json")

                leftover_files = [os.path.join(root, f) for root, _, files in os.walk(media_root) for f in files]
                assert leftover_files == []
