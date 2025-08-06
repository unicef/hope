from django.core.management import call_command

from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.payment import FinancialInstitutionFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from rest_framework import status
from rest_framework.reverse import reverse
from unit.api.base import HOPEApiTestCase

from hct_mis_api.api.models import Grant
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    PendingIndividual,
)
from hct_mis_api.apps.payment.models import AccountType
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class CreateLaxIndividualsTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = [Grant.API_RDI_CREATE]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        call_command("loadcountrycodes")

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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 1)
        self.assertEqual(response.data["accepted"], 1)
        self.assertEqual(response.data["errors"], 0)
        self.assertIn("IND001", response.data["individual_id_mapping"])

        individual = PendingIndividual.objects.get(individual_id="IND001")
        self.assertEqual(individual.full_name, "John Doe")
        self.assertEqual(individual.given_name, "John")
        self.assertEqual(individual.family_name, "Doe")
        self.assertEqual(individual.observed_disability, ["NONE"])
        self.assertEqual(individual.marital_status, "SINGLE")

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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 2)
        self.assertEqual(response.data["accepted"], 2)
        self.assertEqual(response.data["errors"], 0)
        self.assertEqual(len(response.data["individual_id_mapping"]), 2)

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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 1)
        self.assertEqual(response.data["accepted"], 0)
        self.assertEqual(response.data["errors"], 1)
        self.assertEqual(len(response.data["individual_id_mapping"]), 0)

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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 2)
        self.assertEqual(response.data["accepted"], 1)
        self.assertEqual(response.data["errors"], 1)
        self.assertEqual(len(response.data["individual_id_mapping"]), 1)

    def test_empty_request_data(self) -> None:
        response = self.client.post(self.url, [], format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 0)
        self.assertEqual(response.data["accepted"], 0)
        self.assertEqual(response.data["errors"], 0)

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

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, str(response.json()))

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

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, str(response.json()))
