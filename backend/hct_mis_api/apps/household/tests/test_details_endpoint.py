from unittest import TestCase
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.household.models import DocumentType
from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import UserFactory, BusinessAreaFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_TAX_ID
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    DocumentTypeFactory,
    create_household
)


class TestDetails(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.business_area = BusinessAreaFactory(
            code="0060",
        )
        self.program = ProgramFactory(business_area=self.business_area)
        household, individuals = create_household(household_args={"size": 1})
        self.household = household
        self.individual = individuals[0]
        self.document_type = DocumentType.objects.get(type=IDENTIFICATION_TYPE_TAX_ID)
        self.document = DocumentFactory(
            individual=self.individual,
            type=self.document_type
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        # due to --keepdb, with each run, there are more households
        # which causes the search to fail on finding multiple objects
        Household.objects.all().delete()

    def test_getting_individual(self):
        tax_id = self.document.document_number
        self.assertEqual(self.client.get("/api/details?tax_id=non-existent").status_code, 400)
        response = self.client.get(f"/api/details?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["individual"])
        individual = data["individual"]
        # TODO: what about status here?
        # TODO: what about date here? just today's timestamp?

    def test_getting_household(self):
        registration_id = "HOPE-202253186077"
        self.household.kobo_asset_id = registration_id
        self.household.save()
        self.assertEqual(self.client.get("/api/details?registration_id=non-existent").status_code, 400)
        response = self.client.get(f"/api/details?registration_id={registration_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["household"])
        household = data["household"]
        # TODO: what info here? not described in task

