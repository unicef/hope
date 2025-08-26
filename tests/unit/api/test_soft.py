import base64
from pathlib import Path
from typing import Any, Dict

from django.core.management import call_command
from django.urls import reverse
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status
from unit.api.base import HOPEApiTestCase

from hope.api.models import Grant
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.models.household import (
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SON_DAUGHTER,
    PendingHousehold,
)
from hope.models.document_type import DocumentType
from hope.models.program import Program
from hope.models.registration_data_import import RegistrationDataImport


class PushLaxToRDITests(HOPEApiTestCase):
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
        cls.program = ProgramFactory.create(status=Program.DRAFT, business_area=cls.business_area)
        cls.rdi = RegistrationDataImport.objects.create(
            business_area=cls.business_area,
            number_of_individuals=0,
            number_of_households=0,
            status=RegistrationDataImport.LOADING,
            program=cls.program,
        )
        cls.url = reverse("api:rdi-push-lax", args=[cls.business_area.slug, str(cls.rdi.id)])

        country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
        admin_type_3 = AreaTypeFactory(country=country, area_level=3, parent=admin_type_2)

        area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
        AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_3)

    def test_push_error_if_not_loading(self) -> None:
        rdi = RegistrationDataImport.objects.create(
            name="test_push_error_if_not_loading",
            business_area=self.business_area,
            number_of_individuals=0,
            number_of_households=0,
            status=RegistrationDataImport.IN_REVIEW,
            program=self.program,
        )
        url = reverse("api:rdi-push-lax", args=[self.business_area.slug, str(rdi.id)])
        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_push(self) -> None:
        image = Path(__file__).parent / "logo.png"
        base64_encoded_data = base64.b64encode(image.read_bytes())
        input_data = [
            {
                "residence_status": "",
                "village": "village1",
                "country": "AF",
                "admin1": "AF01",
                "admin2": None,
                "members": [
                    {
                        "relationship": HEAD,
                        "full_name": "James Head #1",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                        "role": "",
                        "documents": [
                            {
                                "document_number": 10,
                                "image": base64_encoded_data,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
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
            },  # household 1
            {
                "residence_status": "",
                "village": "village2",
                "country": "AF",
                "members": [
                    {
                        "relationship": HEAD,
                        "full_name": "James Head #1",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                        "role": ROLE_PRIMARY,
                        "documents": [
                            {
                                "document_number": 10,
                                "image": base64_encoded_data,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
                            }
                        ],
                    }
                ],
            },  # household 2
            {
                "residence_status": "IDP",
                "village": "village3",
                "country": "AF",
                "size": 1,
                "members": [
                    {
                        "full_name": "Jhon Primary #1",
                        "birth_date": "2000-01-01",
                        "role": "",
                        "sex": "FEMALE",
                    },
                    {
                        "relationship": NON_BENEFICIARY,
                        "full_name": "Mary Alternate #1",
                        "birth_date": "2000-01-01",
                        "role": ROLE_ALTERNATE,
                        "sex": "MALE",
                    },
                    {
                        "relationship": HEAD,
                        "full_name": "James Head #1",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                        "role": "",
                        "documents": [
                            {
                                "document_number": 10,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
                            }
                        ],
                    },
                    {
                        "relationship": SON_DAUGHTER,
                        "full_name": "Mary Son #1",
                        "birth_date": "2000-01-01",
                        "role": "",
                        "sex": "MALE",
                    },
                ],
            },  # household 3
            {
                "residence_status": "",
                "village": "village4",
                "country": "AF",
                "size": 1,
                "members": [
                    {
                        "relationship": HEAD,
                        "full_name": "John Head #2",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                        "role": "",
                        "documents": [
                            {
                                "document_number": 10,
                                "image": base64_encoded_data,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
                            }
                        ],
                    },
                    {
                        "relationship": NON_BENEFICIARY,
                        "full_name": "Mary Primary #2",
                        "birth_date": "2000-01-01",
                        "role": ROLE_PRIMARY,
                        "sex": "FEMALE",
                    },
                ],
            },  # household 4
            {
                "residence_status": "",
                "village": "village5",
                "country": "AF",
                "size": 1,
                "members": [
                    {
                        "relationship": HEAD,
                        "full_name": "John Doe",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                        "role": "",
                        "documents": [
                            {
                                "document_number": 10,
                                "image": base64_encoded_data,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
                            }
                        ],
                    },
                    {
                        "relationship": NON_BENEFICIARY,
                        "full_name": "Mary Doe",
                        "birth_date": "2000-01-01",
                        "role": ROLE_PRIMARY,
                        "sex": "FEMALE",
                    },
                ],
            },  # household 5
            {
                "residence_status": "",
                "village": "village6",
                "country": "AF",
                "size": 1,
                "members": [
                    {
                        "full_name": "James Head #1",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                        "role": "",
                        "documents": [
                            {
                                "document_number": 10,
                                "image": base64_encoded_data,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
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
            },  # household 6
        ]
        response = self.client.post(self.url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED, str(response.json())

        data: Dict[Any, Any] = response.json()
        assert len(data["households"]) == 6
        assert data["processed"] == 6
        assert data["errors"] == 2
        assert data["accepted"] == 4
        rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
        assert rdi is not None
        for valid in ["village1", "village4", "village5"]:
            assert PendingHousehold.objects.filter(registration_data_import=rdi, village=valid).exists()

        assert data["households"][2] == {"Household #3": [{"primary_collector": ["Missing Primary Collector"]}]}
        assert data["households"][5] == {"Household #6": [{"head_of_household": ["Missing Head Of Household"]}]}
        pk1 = list(data["households"][0].values())[0][0]["pk"]
        hh = PendingHousehold.objects.get(pk=pk1)
        assert hh.program_id == self.program.id
        assert hh.head_of_household.full_name == "James Head #1"
        assert hh.primary_collector.full_name == "Mary Primary #1"
        assert hh.head_of_household.program_id == self.program.id
        assert hh.primary_collector.program_id == self.program.id

        pk2 = list(data["households"][1].values())[0][0]["pk"]
        hh = PendingHousehold.objects.get(pk=pk2)
        assert hh.program_id == self.program.id
        assert hh.head_of_household.full_name == "James Head #1"
        assert hh.primary_collector.full_name == "James Head #1"
        assert hh.head_of_household.program_id == self.program.id
        assert hh.primary_collector.program_id == self.program.id
