import base64
from pathlib import Path

from django.core.management import call_command

from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.api.models import Grant
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    MALE,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SON_DAUGHTER,
    DocumentType,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from tests.unit.api.base import HOPEApiTestCase


class UploadRDITests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = [Grant.API_RDI_UPLOAD]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        call_command("loadcountrycodes")
        DocumentType.objects.create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE], label="--"
        )
        cls.url = reverse("api:rdi-upload", args=[cls.business_area.slug])
        cls.program = ProgramFactory.create(
            status=Program.DRAFT,
            business_area=cls.business_area,
            biometric_deduplication_enabled=True,
        )

    def test_upload_single_household(self) -> None:
        data = {
            "name": "aaaa",
            "program": str(self.program.id),
            "households": [
                {
                    "residence_status": "IDP",
                    "village": "village1",
                    "country": "AF",
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
        rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(rdi)
        self.assertEqual(rdi.program, self.program)
        self.assertEqual(rdi.deduplication_engine_status, RegistrationDataImport.DEDUP_ENGINE_PENDING)

        hh = PendingHousehold.objects.filter(registration_data_import=rdi).first()
        self.assertIsNotNone(hh)
        self.assertIsNotNone(hh.head_of_household)
        self.assertIsNotNone(hh.primary_collector)
        self.assertIsNone(hh.alternate_collector)

        self.assertEqual(hh.head_of_household.full_name, "John Doe")
        self.assertEqual(hh.head_of_household.sex, MALE)
        self.assertEqual(data["households"], 1)
        self.assertEqual(data["individuals"], 2)

    def test_upload_external_collector(self) -> None:
        data = {
            "name": "aaaa",
            "program": str(self.program.id),
            "households": [
                {
                    "residence_status": "IDP",
                    "village": "village1",
                    "country": "AF",
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

        rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(rdi)

        hh = PendingHousehold.objects.filter(registration_data_import=rdi).first()
        self.assertIsNotNone(hh)
        self.assertIsNotNone(hh.head_of_household)
        self.assertIsNotNone(hh.primary_collector)
        self.assertIsNone(hh.alternate_collector)

        self.assertEqual(hh.head_of_household.full_name, "John Doe")
        self.assertEqual(hh.head_of_household.sex, MALE)
        self.assertEqual(data["households"], 1)
        self.assertEqual(data["individuals"], 2)

    def test_upload_with_documents(self) -> None:
        data = {
            "name": "aaaa",
            "program": str(self.program.id),
            "households": [
                {
                    "residence_status": "IDP",
                    "village": "village1",
                    "country": "AF",
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
                    "size": 1,
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        hoh = PendingIndividual.objects.filter(birth_date="2000-01-01", full_name="John Doe", sex=MALE).first()

        self.assertTrue(hoh)
        hh = hoh.pending_household
        self.assertEqual(hh.village, "village1")

        # check collectors
        self.assertNotEqual(hh.primary_collector, hoh)
        self.assertIsNone(hh.alternate_collector)
        members = hh.individuals.all()
        self.assertEqual(len(members), 1)

        self.assertTrue(hoh.documents.exists())

    def test_upload_with_document_photo(self) -> None:
        image = Path(__file__).parent / "logo.png"
        base64_encoded_data = base64.b64encode(image.read_bytes())

        data = {
            "name": "aaaa",
            "program": str(self.program.id),
            "households": [
                {
                    "residence_status": "IDP",
                    "village": "village1",
                    "country": "AF",
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
                    "size": 1,
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        data = response.json()
        rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(rdi)

        hh = PendingHousehold.objects.filter(registration_data_import=rdi).first()
        self.assertIsNotNone(hh)
        self.assertIsNotNone(hh.head_of_household)
        self.assertIsNotNone(hh.primary_collector)
        self.assertIsNone(hh.alternate_collector)

        self.assertEqual(hh.head_of_household.full_name, "John Doe")
        self.assertEqual(hh.head_of_household.sex, MALE)
        self.assertEqual(data["households"], 1)
        self.assertEqual(data["individuals"], 2)

    def test_upload_with_multiple_households(self) -> None:
        image = Path(__file__).parent / "logo.png"
        base64_encoded_data = base64.b64encode(image.read_bytes())

        data = {
            "name": "aaaa",
            "program": str(self.program.id),
            "households": [
                {
                    "residence_status": "IDP",
                    "village": "village1",
                    "country": "AF",
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
                    "size": 1,
                },
                {
                    "residence_status": "",
                    "village": "village2",
                    "country": "AF",
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
                    "size": 1,
                },
                {
                    "residence_status": "",
                    "village": "village3",
                    "country": "AF",
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
                    "size": 1,
                },
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        data = response.json()
        rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(rdi)

        hh = PendingHousehold.objects.filter(registration_data_import=rdi, village="village1").first()
        self.assertIsNotNone(hh)
        self.assertIsNotNone(hh.head_of_household)
        self.assertIsNotNone(hh.primary_collector)
        self.assertIsNotNone(hh.alternate_collector)

        self.assertEqual(hh.primary_collector.full_name, "Jhon Primary #1")
        self.assertEqual(hh.head_of_household.full_name, "James Head #1")

        self.assertEqual(data["households"], 3)
        self.assertEqual(data["individuals"], 8)

    def test_upload_error_too_many_hoh(self) -> None:
        data = {
            "name": "aaaa",
            "program": str(self.program.id),
            "households": [
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
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

    def test_upload_error_missing_primary(self) -> None:
        data = {
            "name": "aaaa",
            "program": str(self.program.id),
            "households": [
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
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
                    "size": 1,
                },
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
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

    def test_upload_multiple_errors(self) -> None:
        data = {
            "name": "aaaa",
            "households": [
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
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
                    "size": 1,
                },
                {
                    "residence_status": "",
                    "village": "village1",
                    "country": "AF",
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
                ],
                "program": ["This field is required."],
            },
            f"""
==== RESULT ====
{str(response.json())}
================
""",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, str(response.json()))
