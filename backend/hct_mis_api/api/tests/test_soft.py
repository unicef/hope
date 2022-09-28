import base64
from pathlib import Path

from django.urls import reverse

from rest_framework import status

from hct_mis_api.api.models import Grant
from hct_mis_api.api.tests.base import HOPEApiTestCase
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_FULL,
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SON_DAUGHTER,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocumentType,
    ImportedHousehold,
    RegistrationDataImportDatahub,
)


class PushLaxToRDITests(HOPEApiTestCase):
    databases = ["default", "registration_datahub"]
    user_permissions = [Grant.API_RDI_CREATE]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ImportedDocumentType.objects.create(country="AF", type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, label="--")
        cls.rdi = RegistrationDataImportDatahub.objects.create(business_area_slug=cls.business_area.slug)
        cls.url = reverse("api:rdi-push-lax", args=[cls.business_area.slug, str(cls.rdi.id)])

    def test_push(self):
        image = Path(__file__).parent / "logo.png"
        base64_encoded_data = base64.b64encode(image.read_bytes())
        data = [
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
                                "doc_date": "2010-01-01",
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
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
                                "doc_date": "2010-01-01",
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
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
                                "doc_date": "2010-01-01",
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
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
                                "doc_date": "2010-01-01",
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
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
                                "doc_date": "2010-01-01",
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
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
                                "doc_date": "2010-01-01",
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
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
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))

        data = response.json()
        self.assertEquals(len(data["households"]), 6)
        self.assertEquals(data["processed"], 6)
        self.assertEquals(data["errors"], 2)
        self.assertEquals(data["accepted"], 4)
        hrdi = RegistrationDataImportDatahub.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(hrdi)
        for valid in ["village1", "village4", "village5"]:
            self.assertTrue(ImportedHousehold.objects.filter(registration_data_import=hrdi, village=valid).exists())
        self.assertDictEqual(
            data["households"][2], {"Household #3": [{"primary_collector": ["Missing Primary Collector"]}]}
        )
        self.assertDictEqual(
            data["households"][5], {"Household #6": [{"head_of_household": ["Missing Head Of Household"]}]}
        )
