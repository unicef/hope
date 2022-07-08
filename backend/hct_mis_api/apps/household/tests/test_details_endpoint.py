from django.test import TestCase
from rest_framework.test import APIClient

from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory
from hct_mis_api.apps.registration_datahub.fixtures import ImportedIndividualFactory
from hct_mis_api.apps.account.fixtures import UserFactory, BusinessAreaFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_TAX_ID
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    DocumentTypeFactory,
    create_household
)


class TestDetails(TestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.business_area = BusinessAreaFactory(
            code="0060",
        )
        cls.program = ProgramFactory(business_area=cls.business_area)
        household, individuals = create_household(household_args={"size": 1})
        cls.household = household
        cls.individual = individuals[0]
        cls.document_type = DocumentTypeFactory(type=IDENTIFICATION_TYPE_TAX_ID)
        cls.document = DocumentFactory(
            individual=cls.individual,
            type=cls.document_type
        )
        cls.tax_id = cls.document.document_number

        cls.registration_id = "HOPE-202253186077"
        cls.household.kobo_asset_id = cls.registration_id
        cls.household.save()

        cls.api_client = APIClient()
        cls.api_client.force_authenticate(user=cls.user)

    def test_getting_non_existent_individual(self):
        self.assertEqual(self.api_client.get("/api/details?tax_id=non-existent").status_code, 400)

    def test_getting_individual_with_status_not_imported(self):
        response = self.api_client.get(f"/api/details?tax_id={self.tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "not imported")
        self.assertIsNotNone(info["date"])
        # TODO: relationship & role in household

    def test_getting_individual_with_status_imported(self):
        ImportedIndividualFactory(individual_id=self.individual.id)
        response = self.api_client.get(f"/api/details?tax_id={self.tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "imported")
        # TODO: date of import

    def test_getting_individual_with_status_merged_to_population(self):
        # TODO: create some objs in db
        response = self.api_client.get(f"/api/details?tax_id={self.tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "merged to population")
        # TODO: date of merge

    def test_getting_individual_with_status_targeted(self):
        # TODO: create some objs in db
        response = self.api_client.get(f"/api/details?tax_id={self.tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "targeted")
        # TODO: date of targeting

    def test_getting_individual_with_status_sent_to_cash_assist(self):
        # TODO: create some objs in db
        response = self.api_client.get(f"/api/details?tax_id={self.tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "sent to cash assist")
        # TODO: date of sending to cash assist

    def test_getting_individual_with_status_paid(self):
        PaymentRecordFactory(household=self.household)
        response = self.api_client.get(f"/api/details?tax_id={self.tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "paid")
        # TODO: date of payment

    def test_getting_non_existend_household(self):
        self.assertEqual(self.api_client.get("/api/details?registration_id=non-existent").status_code, 400)

    def test_getting_household(self):
        response = self.api_client.get(f"/api/details?registration_id={self.registration_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertIsNotNone(info["date"])
        self.assertIsNotNone(info["status"])

