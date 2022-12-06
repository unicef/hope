import base64
from pathlib import Path

from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.api.models import Grant
from hct_mis_api.api.tests.base import HOPEApiTestCase
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    MALE,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SON_DAUGHTER,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    COLLECT_TYPE_FULL,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
)


class UploadRDITests(HOPEApiTestCase):
    databases = ["default", "registration_datahub"]
    user_permissions = [Grant.API_RDI_UPLOAD]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ImportedDocumentType.objects.create(type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, label="--")
        cls.url = reverse("api:rdi-upload", args=[cls.business_area.slug])

    def test_upload_single_household(self):
        data = {
            "name": "aaaa",
            "collect_individual_data": "FULL",
            "households": [
                {
                    "residence_status": "IDP",
                    "village": "village1",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
                    "members": [
                        {
                            "relationship": HEAD,
                            "role": ROLE_PRIMARY,
                            "full_name": "John Doe",
                            "birth_date": "2000-01-01",
                            "sex": "MALE",
                        },
                        {
                            "relationship": SON_DAUGHTER,
                            "full_name": "Mary Doe",
                            "birth_date": "2000-01-01",
                            "role": "",
                            "sex": "FEMALE",
                        },
                    ],
                    "size": 1,
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        data = response.json()
        hrdi = RegistrationDataImportDatahub.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(hrdi)
        rdi = RegistrationDataImport.objects.filter(datahub_id=str(hrdi.pk)).first()
        self.assertIsNotNone(rdi)

        hh = ImportedHousehold.objects.filter(registration_data_import=hrdi).first()
        self.assertIsNotNone(hh)
        self.assertIsNotNone(hh.head_of_household)
        self.assertIsNotNone(hh.primary_collector)
        self.assertIsNone(hh.alternate_collector)

        self.assertEqual(hh.head_of_household.full_name, "John Doe")
        self.assertEqual(hh.head_of_household.sex, MALE)
        self.assertEqual(data["households"], 1)
        self.assertEqual(data["individuals"], 2)

    def test_upload_external_collector(self):
        data = {
            "name": "aaaa",
            "collect_individual_data": COLLECT_TYPE_FULL,
            "households": [
                {
                    "residence_status": "IDP",
                    "village": "village1",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
                    "members": [
                        {
                            "relationship": HEAD,
                            "full_name": "John Doe",
                            "birth_date": "2000-01-01",
                            "sex": "MALE",
                            "role": "",
                        },
                        {
                            "relationship": NON_BENEFICIARY,
                            "full_name": "Mary Doe",
                            "birth_date": "2000-01-01",
                            "role": ROLE_PRIMARY,
                            "sex": "FEMALE",
                        },
                    ],
                    "size": 1,
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, data)

        hrdi = RegistrationDataImportDatahub.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(hrdi)
        rdi = RegistrationDataImport.objects.filter(datahub_id=str(hrdi.pk)).first()
        self.assertIsNotNone(rdi)

        hh = ImportedHousehold.objects.filter(registration_data_import=hrdi).first()
        self.assertIsNotNone(hh)
        self.assertIsNotNone(hh.head_of_household)
        self.assertIsNotNone(hh.primary_collector)
        self.assertIsNone(hh.alternate_collector)

        self.assertEqual(hh.head_of_household.full_name, "John Doe")
        self.assertEqual(hh.head_of_household.sex, MALE)
        self.assertEqual(data["households"], 1)
        self.assertEqual(data["individuals"], 2)

    def test_upload_with_documents(self):
        data = {
            "name": "aaaa",
            "collect_individual_data": "FULL",
            "households": [
                {
                    "residence_status": "IDP",
                    "village": "village1",
                    "country": "AF",
                    "collect_individual_data": "FULL",
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
                                    "image": "",
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
                    "size": 1,
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        hoh = ImportedIndividual.objects.filter(birth_date="2000-01-01", full_name="John Doe", sex=MALE).first()

        self.assertTrue(hoh)
        hh: ImportedHousehold = hoh.household
        self.assertEqual(hoh.household.village, "village1")

        # check collectors
        self.assertNotEqual(hoh.household.primary_collector, hoh)
        self.assertIsInstance(hoh.household.primary_collector, ImportedIndividual)
        self.assertIsNone(hoh.household.alternate_collector)
        members = hh.individuals.all()
        self.assertEqual(len(members), 1)

        self.assertTrue(hoh.documents.exists())

    def test_upload_with_document_photo(self):
        image = Path(__file__).parent / "logo.png"
        base64_encoded_data = base64.b64encode(image.read_bytes())

        data = {
            "name": "aaaa",
            "collect_individual_data": "FULL",
            "households": [
                {
                    "residence_status": "IDP",
                    "village": "village1",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
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
                    "size": 1,
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")
        data = response.json()
        hrdi = RegistrationDataImportDatahub.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(hrdi)
        rdi = RegistrationDataImport.objects.filter(datahub_id=str(hrdi.pk)).first()
        self.assertIsNotNone(rdi)

        hh = ImportedHousehold.objects.filter(registration_data_import=hrdi).first()
        self.assertIsNotNone(hh)
        self.assertIsNotNone(hh.head_of_household)
        self.assertIsNotNone(hh.primary_collector)
        self.assertIsNone(hh.alternate_collector)

        self.assertEqual(hh.head_of_household.full_name, "John Doe")
        self.assertEqual(hh.head_of_household.sex, MALE)
        self.assertEqual(data["households"], 1)
        self.assertEqual(data["individuals"], 2)

    def test_upload_with_multiple_households(self):
        image = Path(__file__).parent / "logo.png"
        base64_encoded_data = base64.b64encode(image.read_bytes())

        data = {
            "name": "aaaa",
            "collect_individual_data": "FULL",
            "households": [
                {
                    "residence_status": "IDP",
                    "village": "village1",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
                    "members": [
                        {
                            "relationship": NON_BENEFICIARY,
                            "full_name": "Jhon Primary #1",
                            "birth_date": "2000-01-01",
                            "role": ROLE_PRIMARY,
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
                    "size": 1,
                },
                {
                    "residence_status": "",
                    "village": "village2",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
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
                    "size": 1,
                },
                {
                    "residence_status": "",
                    "village": "village3",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
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
                    "size": 1,
                },
            ],
        }
        response = self.client.post(self.url, data, format="json")
        data = response.json()
        hrdi = RegistrationDataImportDatahub.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(hrdi)
        rdi = RegistrationDataImport.objects.filter(datahub_id=str(hrdi.pk)).first()
        self.assertIsNotNone(rdi)

        hh = ImportedHousehold.objects.filter(registration_data_import=hrdi, village="village1").first()
        self.assertIsNotNone(hh)
        self.assertIsNotNone(hh.head_of_household)
        self.assertIsNotNone(hh.primary_collector)
        self.assertIsNotNone(hh.alternate_collector)

        self.assertEqual(hh.collect_individual_data, COLLECT_TYPE_FULL)
        self.assertEqual(hh.primary_collector.full_name, "Jhon Primary #1")
        self.assertEqual(hh.head_of_household.full_name, "James Head #1")

        self.assertEqual(data["households"], 3)
        self.assertEqual(data["individuals"], 8)

    def test_upload_error_too_many_hoh(self):
        data = {
            "name": "aaaa",
            "collect_individual_data": "FULL",
            "households": [
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
                    "members": [
                        {
                            "relationship": HEAD,
                            "role": ROLE_PRIMARY,
                            "full_name": "John Doe",
                            "birth_date": "2000-01-01",
                            "sex": "MALE",
                        },
                        {
                            "relationship": HEAD,
                            "full_name": "Mary Doe",
                            "birth_date": "2000-01-01",
                            "role": "",
                            "sex": "FEMALE",
                        },
                    ],
                    "size": 1,
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(
            response.json(),
            {"households": [{"Household #1": [{"head_of_household": ["Only one HoH allowed"]}]}]},
            f"""
==== RESULT ====
{str(response.json())}
================""",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, str(response.json()))

    def test_upload_error_missing_primary(self):
        data = {
            "name": "aaaa",
            "collect_individual_data": "FULL",
            "households": [
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
                    "members": [
                        {
                            "relationship": NON_BENEFICIARY,
                            "full_name": "Jhon Primary #1",
                            "birth_date": "2000-01-01",
                            "role": ROLE_PRIMARY,
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
                    "size": 1,
                },
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
                    "members": [
                        {
                            "relationship": HEAD,
                            "role": ROLE_ALTERNATE,
                            "full_name": "John Doe",
                            "birth_date": "2000-01-01",
                            "sex": "MALE",
                        },
                        {
                            "relationship": SON_DAUGHTER,
                            "full_name": "Mary Doe",
                            "birth_date": "2000-01-01",
                            "role": "",
                            "sex": "FEMALE",
                        },
                    ],
                    "size": 1,
                },
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(
            response.json(),
            {"households": [{"Household #2": [{"primary_collector": ["Missing Primary Collector"]}]}]},
            f"""
==== RESULT ====
{str(response.json())}
================
""",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, str(response.json()))

    def test_upload_multiple_errors(self):
        data = {
            "name": "aaaa",
            "collect_individual_data": "FULL",
            "households": [
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
                    "members": [
                        {
                            "relationship": NON_BENEFICIARY,
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
                            "relationship": SON_DAUGHTER,
                            "full_name": "James Head #1",
                            "birth_date": "2000-01-01",
                            "sex": "MALE",
                            "role": ROLE_ALTERNATE,
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
                    "size": 1,
                },
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
                    "collect_individual_data": COLLECT_TYPE_FULL,
                    "members": [
                        {
                            "relationship": HEAD,
                            "full_name": "John Doe",
                            "birth_date": "2000-01-01",
                            "role": "",
                            "sex": "MALE",
                        },
                        {
                            "relationship": HEAD,
                            "full_name": "Mary Doe",
                            "birth_date": "2000-01-01",
                            "role": "",
                            "sex": "FEMALE",
                        },
                    ],
                    "size": 1,
                },
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(
            response.json(),
            {
                "households": [
                    {
                        "Household #1": [
                            {
                                "alternate_collector": ["Only one Alternate Collector allowed"],
                                "head_of_household": ["Missing Head Of Household"],
                                "primary_collector": ["Missing Primary Collector"],
                            }
                        ]
                    },
                    {
                        "Household #2": [
                            {
                                "head_of_household": ["Only one HoH allowed"],
                                "primary_collector": ["Missing Primary Collector"],
                            }
                        ]
                    },
                ]
            },
            f"""
==== RESULT ====
{str(response.json())}
================
""",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, str(response.json()))
