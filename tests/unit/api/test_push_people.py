import base64
from io import BytesIO
from typing import Any

import pytest
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from parameterized import parameterized
from PIL import Image
from rest_framework import status
from rest_framework.reverse import reverse
from unit.api.base import HOPEApiTestCase

from hct_mis_api.api.endpoints.rdi.push_people import PeopleUploadMixin
from hct_mis_api.api.models import Grant
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.models import (
    FEMALE,
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    MALE,
    NOT_COLLECTED,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class TestPushPeople(HOPEApiTestCase):
    user_permissions = [Grant.API_RDI_UPLOAD]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        DocumentType.objects.create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE], label="--"
        )
        data_collecting_type = DataCollectingTypeFactory(
            label="Full",
            code="full",
            weight=1,
            business_areas=[cls.business_area],
            type=DataCollectingType.Type.SOCIAL.value,
        )
        cls.program = ProgramFactory.create(
            status=Program.DRAFT, business_area=cls.business_area, data_collecting_type=data_collecting_type
        )
        cls.rdi: RegistrationDataImport = RegistrationDataImport.objects.create(
            business_area=cls.business_area,
            number_of_individuals=0,
            number_of_households=0,
            status=RegistrationDataImport.LOADING,
            program=cls.program,
        )

        cls.url = reverse("api:rdi-push-people", args=[cls.business_area.slug, str(cls.rdi.id)])

        country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
        admin_type_3 = AreaTypeFactory(country=country, area_level=3, parent=admin_type_2)

        area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
        AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_3)

    def test_upload_single_person(self) -> None:
        data = [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "full_name": "John Doe",
                "birth_date": "2000-01-01",
                "sex": "NOT_COLLECTED",
                "type": "",
                "program": str(self.program.id),
            }
        ]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        response_json = response.json()

        rdi = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
        self.assertIsNotNone(rdi)

        self.assertEqual(rdi.program, self.program)

        hh = PendingHousehold.objects.filter(registration_data_import=rdi).first()
        ind = PendingIndividual.objects.filter(registration_data_import=rdi).first()
        self.assertIsNotNone(hh)
        self.assertIsNotNone(ind)
        self.assertEqual(hh.head_of_household, ind)
        self.assertEqual(hh.primary_collector, ind)
        self.assertEqual(hh.village, "village1")

        self.assertEqual(ind.full_name, "John Doe")
        self.assertEqual(ind.sex, NOT_COLLECTED)
        self.assertEqual(ind.relationship, HEAD)

        self.assertEqual(response_json["id"], str(self.rdi.id))
        self.assertEqual(len(response_json["people"]), 1)

    def test_upload_single_person_with_documents(self) -> None:
        data = [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "full_name": "John Doe",
                "birth_date": "2000-01-01",
                "sex": "MALE",
                "type": "",
                "documents": [
                    {
                        "document_number": "10",
                        "image": "",
                        "doc_date": "2010-01-01",
                        "country": "AF",
                        "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
                    }
                ],
                "program": str(self.program.id),
            }
        ]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        response_json = response.json()

        rdi = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
        self.assertIsNotNone(rdi)

        ind = PendingIndividual.objects.filter(registration_data_import=rdi).first()
        self.assertIsNotNone(ind)
        self.assertEqual(ind.full_name, "John Doe")
        self.assertEqual(ind.sex, MALE)

        document = PendingDocument.objects.filter(individual=ind).first()
        self.assertIsNotNone(document)
        self.assertEqual(document.document_number, "10")

    def test_upload_multiple_people_with_documents(self) -> None:
        data = [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "full_name": "John Doe",
                "birth_date": "2000-01-01",
                "sex": "MALE",
                "type": "",
                "documents": [
                    {
                        "document_number": "10",
                        "image": "",
                        "doc_date": "2010-01-01",
                        "country": "AF",
                        "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
                    }
                ],
                "program": str(self.program.id),
            },
            {
                "residence_status": "IDP",
                "village": "village2",
                "country": "AF",
                "full_name": "Mary Doe",
                "birth_date": "1990-01-01",
                "sex": "FEMALE",
                "type": "",
                "program": str(self.program.id),
            },
        ]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        response_json = response.json()

        rdi = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
        self.assertIsNotNone(rdi)

        self.assertEqual(len(response_json["people"]), 2)

        households = PendingHousehold.objects.filter(registration_data_import=rdi)
        self.assertEqual(len(households), 2)

        individuals = PendingIndividual.objects.filter(registration_data_import=rdi)
        self.assertEqual(len(individuals), 2)

        john_doe = PendingIndividual.objects.filter(full_name="John Doe").first()

        self.assertIsNotNone(john_doe)
        self.assertEqual(john_doe.full_name, "John Doe")
        self.assertEqual(john_doe.sex, MALE)

        mary_doe = PendingIndividual.objects.filter(full_name="Mary Doe").first()

        self.assertIsNotNone(mary_doe)
        self.assertEqual(mary_doe.full_name, "Mary Doe")
        self.assertEqual(mary_doe.sex, FEMALE)

        document = PendingDocument.objects.filter(individual=john_doe).first()
        self.assertIsNotNone(document)
        self.assertEqual(document.document_number, "10")

    def test_upload_with_errors(self) -> None:
        data = [
            {
                "residence_status": "IDP",
                "country": "AF",
                "full_name": "John Doe",
                "sex": "MALE",
                "documents": [
                    {
                        "image": "",
                        "country": "AF",
                    }
                ],
                "program": str(self.program.id),
            },
            {
                "residence_status": "IDP",
                "village": "village2",
                "country": "AF",
                "full_name": "Mary Doe",
                "sex": "FEMALE",
                "program": str(self.program.id),
            },
        ]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, str(response.json()))
        self.assertEqual(
            response.json(),
            [
                {
                    "birth_date": ["This field is required."],
                    "documents": [
                        {
                            "document_number": ["This field is required."],
                            "type": ["This field is required."],
                        }
                    ],
                    "type": ["This field is required."],
                },
                {"birth_date": ["This field is required."], "type": ["This field is required."]},
            ],
        )

    @parameterized.expand(
        [
            ("invalid_phone_no", "phone_no", "invalid", False),
            ("invalid_phone_no_alternative", "phone_no", "invalid", False),
            ("valid_phone_no", "phone_no_alternative", "+48 632 215 789", True),
            ("valid_phone_no_alternative", "phone_no_alternative", "+48 632 215 789", True),
            ("phone_no_alternative_as_null", "phone_no_alternative", None, False),
            ("phone_no_as_null", "phone_no", None, False),
        ]
    )
    def test_upload_single_person_with_phone_number(
        self, _: Any, field_name: str, phone_number: str, expected_value: bool
    ) -> None:
        data = [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "full_name": "John Doe",
                "birth_date": "2000-01-01",
                "sex": "MALE",
                "type": "",
                field_name: phone_number,
                "program": str(self.program.id),
            }
        ]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        response_json = response.json()

        rdi = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
        self.assertIsNotNone(rdi)
        ind = PendingIndividual.objects.filter(registration_data_import=rdi).first()
        self.assertIsNotNone(ind)
        self.assertEqual(ind.full_name, "John Doe")
        self.assertEqual(getattr(ind, f"{field_name}_valid"), expected_value)

    @parameterized.expand(
        [
            ("valid-village", "village1", "village1"),
            ("empty-village", "", ""),
            ("null-village", None, ""),
        ]
    )
    def test_push_single_person_with_village(self, _: Any, village: str, expected_value: str) -> None:
        data = [
            {
                "residence_status": "IDP",
                "village": village,
                "country": "AF",
                "full_name": "John Doe",
                "birth_date": "2000-01-01",
                "sex": "MALE",
                "type": "",
                "program": str(self.program.id),
            }
        ]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        response_json = response.json()

        rdi = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
        self.assertIsNotNone(rdi)
        ind = PendingIndividual.objects.filter(registration_data_import=rdi).first()
        self.assertEqual(ind.household.village, expected_value)

    def test_push_single_person_with_admin_areas(self) -> None:
        data = [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "full_name": "John Doe",
                "birth_date": "2000-01-01",
                "sex": "MALE",
                "type": "",
                "admin1": "AF01",
                "admin2": "AF0101",
                "admin3": "",
                "admin4": None,
                "program": str(self.program.id),
            }
        ]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        response_json = response.json()

        rdi = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
        self.assertIsNotNone(rdi)
        ind = PendingIndividual.objects.filter(registration_data_import=rdi).first()
        self.assertEqual(ind.household.admin1.p_code, "AF01")
        self.assertEqual(ind.household.admin2.p_code, "AF0101")
        self.assertEqual(ind.household.admin3, None)
        self.assertEqual(ind.household.admin4, None)


class TestPeopleUploadMixin:
    @pytest.fixture
    def rdi(self) -> RegistrationDataImport:
        create_afghanistan()
        rdi: RegistrationDataImport = RegistrationDataImportFactory()
        return rdi

    @pytest.mark.django_db
    def test_create_individual_with_photo_remove_prefix(self, rdi: RegistrationDataImport) -> None:
        prefix = "data:image/png;base64,"

        buffer = BytesIO()
        image = Image.new("RGB", (1, 1), color="blue")
        image.save(buffer, format="PNG")
        photo_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        base64_photo = f"{prefix}{photo_data}"

        person_data = {
            "type": "NON_BENEFICIARY",
            "photo": base64_photo,
            "first_name": "WithPhoto",
            "birth_date": "2000-01-01",
            "first_registration_date": "2000-01-01",
            "last_registration_date": "2000-01-01",
        }
        assert base64_photo.startswith(prefix) is True

        individual = PeopleUploadMixin()._create_individual(
            documents=[],
            accounts=[],
            hh=None,
            person_data=person_data,
            rdi=rdi,
        )

        assert individual.photo.name[:5] == "photo"
        assert individual.photo.name[-4:] == ".png"
        photo_saved = base64.b64encode(individual.photo.read()).decode("utf-8")
        assert photo_saved.startswith(prefix) is False
        assert photo_saved == photo_data
