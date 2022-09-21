import base64
from pathlib import Path

from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.api.tests.base import HOPEApiTestCase
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    MALE,
    NON_BENEFICIARY,
    ROLE_PRIMARY,
    SON_DAUGHTER,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
)


class UploadRDITests(HOPEApiTestCase):
    databases = ["default", "registration_datahub"]
    user_permissions = [Permissions.API_UPLOAD_RDI]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ImportedDocumentType.objects.create(country="AF", type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, label="--")
        cls.url = reverse("api:rdi-upload", args=[cls.business_area.slug])

    def test_upload_single_household(self):
        data = {
            "name": "aaaa",
            "number_of_households": 1,
            "number_of_individuals": 1,
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
                            "relationship": SON_DAUGHTER,
                            "full_name": "Mary Doe",
                            "birth_date": "2000-01-01",
                            "role": "",
                            "sex": "FEMALE",
                        },
                    ],
                    "collect_individual_data": "FULL",
                    "size": 1,
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        data = response.json()
        self.assertEqual(data["households"], 1)
        self.assertEqual(data["individuals"], 2)

        hoh = ImportedIndividual.objects.filter(birth_date="2000-01-01", full_name="John Doe", sex=MALE).first()

        self.assertTrue(hoh)
        hh: ImportedHousehold = hoh.household
        self.assertEqual(hoh.household.village, "village1")
        self.assertEqual(hoh.household.primary_collector, hoh)
        self.assertFalse(hoh.household.alternate_collector)
        members = hh.individuals.all()
        self.assertEqual(len(members), 2)

    def test_upload_external_collector(self):
        data = {
            "name": "aaaa",
            "number_of_households": 1,
            "number_of_individuals": 1,
            "households": [
                {
                    "residence_status": "",
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
                    "collect_individual_data": "FULL",
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

    def test_upload_with_documents(self):
        data = {
            "name": "aaaa",
            "number_of_households": 1,
            "number_of_individuals": 1,
            "households": [
                {
                    "residence_status": "",
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
                    "collect_individual_data": "FULL",
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
            "number_of_households": 1,
            "number_of_individuals": 1,
            "households": [
                {
                    "residence_status": "",
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
                    "collect_individual_data": "FULL",
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
        self.assertTrue(hoh.documents.first().photo)

    def test_upload_error_too_many_hoh(self):
        data = {
            "name": "aaaa",
            "number_of_households": 1,
            "number_of_individuals": 1,
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
                    "collect_individual_data": "FULL",
                    "size": 1,
                }
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(
            response.json(), {"households": [{"members": {"head_of_household": ["Only one HoH allowed"]}}]}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, str(response.json()))
