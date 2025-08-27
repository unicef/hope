import base64
from pathlib import Path
from typing import Dict

from django.core.management import call_command
from extras.test_utils.factories.program import (
    ProgramFactory,
    get_program_with_dct_type_and_name,
)
from rest_framework import status
from rest_framework.reverse import reverse
from unit.api.base import HOPEApiTestCase
from unit.api.factories import UserFactory

from hope.models.grant import Grant
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.models.household import (
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    NON_BENEFICIARY,
    ROLE_PRIMARY,
    PendingHousehold,
)
from hope.models.document_type import DocumentType
from hope.models.account_type import AccountType
from hope.models.financial_institution import FinancialInstitution
from hope.models.account import PendingAccount
from hope.models.program import Program
from hope.models.registration_data_import import RegistrationDataImport


class CreateRDITests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = [Grant.API_RDI_CREATE]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.url = reverse("api:rdi-create", args=[cls.business_area.slug])
        cls.program = ProgramFactory.create(status=Program.DRAFT, business_area=cls.business_area)

    def test_create_rdi(self) -> None:
        user = UserFactory()
        data = {
            "name": "aaaa",
            "collect_data_policy": "FULL",
            "program": str(self.program.id),
            "imported_by_email": user.email,
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        rdi = RegistrationDataImport.objects.filter(name="aaaa").first()
        assert rdi is not None
        assert rdi.program == self.program
        assert rdi.status == RegistrationDataImport.LOADING
        assert rdi.imported_by == user
        assert response.json()["id"] == str(rdi.id)
        assert response.status_code == status.HTTP_201_CREATED, str(response.json())

    def test_create_rdi_permission_denied_for_invalid_email(self) -> None:
        data = {
            "name": "aaaa",
            "collect_data_policy": "FULL",
            "program": str(self.program.id),
            "imported_by_email": "nonexistentuser@example.com",
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN, str(response.json())
        assert "User with this email does not exist." in str(response.json())


class PushToRDITests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = [Grant.API_RDI_CREATE]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        call_command("loadcountrycodes")
        DocumentType.objects.create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
            label="--",
        )
        cls.fi = FinancialInstitution.objects.create(
            name="mbank", type=FinancialInstitution.FinancialInstitutionType.BANK
        )
        cls.program = ProgramFactory.create(status=Program.DRAFT, business_area=cls.business_area)
        cls.rdi: RegistrationDataImport = RegistrationDataImport.objects.create(
            business_area=cls.business_area,
            number_of_individuals=0,
            number_of_households=0,
            status=RegistrationDataImport.LOADING,
            program=cls.program,
        )
        AccountType.objects.get_or_create(key="bank", defaults={"label": "Bank", "unique_fields": ["number"]})
        cls.url = reverse("api:rdi-push", args=[cls.business_area.slug, str(cls.rdi.id)])

    def test_push(self) -> None:
        image = Path(__file__).parent / "logo.png"
        base64_encoded_data = base64.b64encode(image.read_bytes())
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
                        "photo": base64_encoded_data,
                        "role": "",
                        "documents": [
                            {
                                "document_number": 10,
                                "image": base64_encoded_data,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
                            }
                        ],
                        "accounts": [
                            {
                                "account_type": "bank",
                                "number": "123",
                                "financial_institution": self.fi.id,
                                "data": {"field_name": "field_value"},
                            }
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
        response = self.client.post(self.url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED, str(response.json())

        data: Dict = response.json()
        rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
        assert rdi is not None

        hh = PendingHousehold.objects.filter(registration_data_import=rdi, village="village1").first()
        assert hh is not None
        assert hh.head_of_household is not None
        assert hh.primary_collector is not None
        assert hh.alternate_collector is None
        assert hh.program_id == self.program.id

        assert hh.primary_collector.full_name == "Mary Primary #1"
        assert hh.head_of_household.full_name == "James Head #1"
        assert hh.head_of_household.photo is not None
        account = PendingAccount.objects.filter(individual=hh.head_of_household).first()
        assert account is not None
        assert account.account_type.key == "bank"
        assert account.financial_institution.id == self.fi.id
        assert account.number == "123"
        assert account.data == {"field_name": "field_value"}

        assert hh.primary_collector.program_id == self.program.id
        assert hh.head_of_household.program_id == self.program.id

        assert data["households"] == 1
        assert data["individuals"] == 2

    def test_push_fail_if_not_loading(self) -> None:
        program = get_program_with_dct_type_and_name()
        rdi = RegistrationDataImport.objects.create(
            name="test_push_fail_if_not_loading",
            business_area=self.business_area,
            number_of_individuals=0,
            number_of_households=0,
            status=RegistrationDataImport.IN_REVIEW,
            program=program,
        )
        url = reverse("api:rdi-push", args=[self.business_area.slug, str(rdi.id)])
        response = self.client.post(url, [], format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.data


class CompleteRDITests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = [Grant.API_RDI_CREATE]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.program = ProgramFactory.create(status=Program.DRAFT, business_area=cls.business_area)
        cls.rdi: RegistrationDataImport = RegistrationDataImport.objects.create(
            business_area=cls.business_area,
            number_of_individuals=0,
            number_of_households=0,
            status=RegistrationDataImport.LOADING,
            program=cls.program,
        )

        cls.url = reverse("api:rdi-complete", args=[cls.business_area.slug, str(cls.rdi.id)])

    def test_complete(self) -> None:
        data = {}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_200_OK, str(response.json())
        data = response.json()
        assert data[0] == {"id": str(self.rdi.id), "status": "IN_REVIEW"}
        self.rdi.refresh_from_db()
        assert self.rdi.status == RegistrationDataImport.IN_REVIEW
