from unittest import TestCase
from unittest.mock import Mock

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
)


class HOPEPermissionTests(TestCase):
    def setUp(self):
        self.user: User = UserFactory()
        self.business_area = BusinessAreaFactory(name="Afghanistan")
        self.role = RoleFactory(subsystem="API", permissions=[Permissions.API_UPLOAD_RDI])
        self.user.user_roles.create(role=self.role, business_area=self.business_area)

    def test_permissions(self):
        p = HOPEPermission()

        assert p.has_permission(
            Mock(user=self.user), Mock(selected_business_area=self.business_area, permission=Permissions.API_UPLOAD_RDI)
        )


class UploadRDITests(APITestCase):
    databases = ["default", "registration_datahub"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.business_area = BusinessAreaFactory(name="Afghanistan")
        ImportedDocumentType.objects.create(country="AF", type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, label="--")

        cls.user: User = UserFactory()
        cls.role = RoleFactory(subsystem="API", permissions=[Permissions.API_UPLOAD_RDI])
        cls.user.user_roles.create(role=cls.role, business_area=cls.business_area)
        cls.url = reverse("api:rdi-upload", args=[cls.business_area.slug])

    def setUp(self):
        self.client.login(username=self.user.username, password="password")

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
                            "full_name": "Jhon Doe",
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
        hoh = ImportedIndividual.objects.filter(birth_date="2000-01-01", full_name="Jhon Doe", sex=MALE).first()

        self.assertTrue(hoh)
        hh: ImportedHousehold = hoh.household
        self.assertEqual(hoh.household.village, "village1")
        # can we test this ?
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
                            "full_name": "Jhon Doe",
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
                            "full_name": "Jhon Doe",
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
