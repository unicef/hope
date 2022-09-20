import base64
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock

from PIL.Image import Image
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from hct_mis_api.api.auth import HOPEPermission
from hct_mis_api.apps.account.export_users_xlsx import User
from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
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
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
)


class CreateRDITests(APITestCase):
    databases = ["default", "registration_datahub"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.business_area = BusinessAreaFactory(name="Afghanistan")
        cls.user: User = UserFactory()
        cls.role = RoleFactory(subsystem="API", name="c", permissions=[Permissions.API_CREATE_RDI])
        cls.user.user_roles.create(role=cls.role, business_area=cls.business_area)
        cls.url = reverse("api:rdi-create", args=[cls.business_area.slug])

    def setUp(self):
        self.client.login(username=self.user.username, password="password")

    def test_create_rdi(self):
        data = {
            "name": "aaaa",
            "number_of_households": 1,
            "number_of_individuals": 1,
        }
        response = self.client.post(self.url, data, format="json")
        rdi = RegistrationDataImportDatahub.objects.filter(name="aaaa").first()
        self.assertTrue(rdi)
        self.assertEqual(response.json()["id"], str(rdi.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))


class PushToRDITests(APITestCase):
    databases = ["default", "registration_datahub"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ImportedDocumentType.objects.create(country="AF", type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, label="--")
        cls.business_area = BusinessAreaFactory(name="Afghanistan")
        cls.user: User = UserFactory()
        cls.rdi = RegistrationDataImportDatahub.objects.create(business_area_slug=cls.business_area.slug)
        cls.role = RoleFactory(subsystem="API", name="c", permissions=[Permissions.API_CREATE_RDI])
        cls.user.user_roles.create(role=cls.role, business_area=cls.business_area)
        cls.url = reverse("api:rdi-push", args=[cls.business_area.slug, str(cls.rdi.id)])

    def setUp(self):
        self.client.login(username=self.user.username, password="password")

    def test_push(self):
        image = Path(__file__).parent / "logo.png"
        base64_encoded_data = base64.b64encode(image.read_bytes())
        data = [
            {
                "residence_status": "",
                "village": "village1",
                "country": "AF",
                "members": [
                    {
                        "relationship": HEAD,
                        "full_name": "Jhon Doe",
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
        ]
        response = self.client.post(self.url, data, format="json")
        # self.assertTrue(rdi)
        # self.assertEqual(response.json()["id"], str(rdi.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        hoh = ImportedIndividual.objects.filter(birth_date="2000-01-01", full_name="Jhon Doe", sex=MALE).first()
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
