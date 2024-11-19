import base64
from pathlib import Path
from typing import Any, Dict

from django.core.management import call_command
from django.urls import reverse

from rest_framework import status

from hct_mis_api.api.models import Grant
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_FULL,
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SON_DAUGHTER,
    DocumentType,
    PendingHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from tests.unit.api.base import HOPEApiTestCase


class PushLaxToRDITests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = [Grant.API_RDI_CREATE]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        call_command("loadcountrycodes")
        DocumentType.objects.create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE], label="--"
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
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_push(self) -> None:
        image = Path(__file__).parent / "logo.png"
        base64_encoded_data = base64.b64encode(image.read_bytes())
        input_data = [
            {
                "residence_status": "",
                "village": "village1",
                "country": "AF",
                "collect_individual_data": COLLECT_TYPE_FULL,
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
                "collect_individual_data": COLLECT_TYPE_FULL,
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
                "collect_individual_data": COLLECT_TYPE_FULL,
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
                "collect_individual_data": COLLECT_TYPE_FULL,
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
                "collect_individual_data": COLLECT_TYPE_FULL,
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
                "collect_individual_data": COLLECT_TYPE_FULL,
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))

        data: Dict[Any, Any] = response.json()
        self.assertEqual(len(data["households"]), 6)
        self.assertEqual(data["processed"], 6)
        self.assertEqual(data["errors"], 2)
        self.assertEqual(data["accepted"], 4)
        rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(rdi)
        for valid in ["village1", "village4", "village5"]:
            self.assertTrue(PendingHousehold.objects.filter(registration_data_import=rdi, village=valid).exists())

        self.assertDictEqual(
            data["households"][2], {"Household #3": [{"primary_collector": ["Missing Primary Collector"]}]}
        )
        self.assertDictEqual(
            data["households"][5], {"Household #6": [{"head_of_household": ["Missing Head Of Household"]}]}
        )
        pk1 = list(data["households"][0].values())[0][0]["pk"]
        hh = PendingHousehold.objects.get(pk=pk1)
        self.assertEqual(hh.program_id, self.program.id)
        self.assertEqual(hh.head_of_household.full_name, "James Head #1")
        self.assertEqual(hh.primary_collector.full_name, "Mary Primary #1")
        self.assertEqual(hh.head_of_household.program_id, self.program.id)
        self.assertEqual(hh.primary_collector.program_id, self.program.id)

        pk2 = list(data["households"][1].values())[0][0]["pk"]
        hh = PendingHousehold.objects.get(pk=pk2)
        self.assertEqual(hh.program_id, self.program.id)
        self.assertEqual(hh.head_of_household.full_name, "James Head #1")
        self.assertEqual(hh.primary_collector.full_name, "James Head #1")
        self.assertEqual(hh.head_of_household.program_id, self.program.id)
        self.assertEqual(hh.primary_collector.program_id, self.program.id)
