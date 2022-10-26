from django.test import TestCase

from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    DocumentTypeFactory,
    create_household,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_TAX_ID,
    ROLE_NO_ROLE,
)
from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory
from hct_mis_api.apps.registration_datahub.fixtures import (
    ImportedDocumentFactory,
    ImportedDocumentTypeFactory,
    ImportedHouseholdFactory,
    ImportedIndividualFactory,
    RegistrationDataImportDatahubFactory,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedIndividualRoleInHousehold,
)
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation


# used for ease of assertions, so it imitates serializer's behaviour
def _time(some_time):
    return str(some_time).replace(" ", "T").replace("+00:00", "Z")


class TestDetails(TestCase):
    databases = "__all__"
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.api_client = APIClient()
        cls.api_client.force_authenticate(user=cls.user)

        cls.business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            has_data_sharing_agreement=True,
        )

    def test_filtering_business_area_code_with_tax_id(self):
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(type=IDENTIFICATION_TYPE_TAX_ID)
        document = DocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number

        response_ok = self.api_client.get(
            f"/api/hh-status?tax_id={tax_id}&business_area_code={self.business_area.code}"
        )
        self.assertEqual(response_ok.status_code, 200)

        response_nok = self.api_client.get(f"/api/hh-status?tax_id={tax_id}&business_area_code=non-existent")
        self.assertEqual(response_nok.status_code, 404)

    def test_filtering_business_area_code_with_registration_id(self):
        rdi_datahub = RegistrationDataImportDatahubFactory(business_area_slug=self.business_area.slug)
        imported_household = ImportedHouseholdFactory(registration_data_import=rdi_datahub)
        imported_individual = ImportedIndividualFactory(household=imported_household, relationship=HEAD)
        imported_household.head_of_household = imported_individual
        imported_household.kobo_asset_id = "HOPE-2022530111222"
        imported_household.save()
        ImportedIndividualRoleInHousehold.objects.create(
            individual=imported_individual, role=ROLE_NO_ROLE, household=imported_household
        )

        registration_id = imported_household.kobo_asset_id

        response_ok = self.api_client.get(
            f"/api/hh-status?registration_id={registration_id}&business_area_code={self.business_area.code}"
        )
        self.assertEqual(response_ok.status_code, 200)

        response_nok = self.api_client.get(
            f"/api/hh-status?registration_id={registration_id}&business_area_code=non-existent"
        )
        self.assertEqual(response_nok.status_code, 404)

    def test_getting_non_existent_individual(self):
        response = self.api_client.get("/api/hh-status?tax_id=non-existent")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["status"], "not found")

    def test_getting_individual_with_status_imported(self):
        imported_household = ImportedHouseholdFactory()
        imported_individual = ImportedIndividualFactory(household=imported_household, relationship=HEAD)
        imported_household.head_of_household = imported_individual
        imported_household.save()
        ImportedIndividualRoleInHousehold.objects.create(
            individual=imported_individual, role=ROLE_NO_ROLE, household=imported_household
        )

        imported_document_type = ImportedDocumentTypeFactory(type=IDENTIFICATION_TYPE_TAX_ID)
        imported_document = ImportedDocumentFactory(individual=imported_individual, type=imported_document_type)
        tax_id = imported_document.document_number

        response = self.api_client.get(f"/api/hh-status?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "imported")
        self.assertEqual(info["date"], _time(imported_household.updated_at))

        individual = info["individual"]
        self.assertIsNotNone(individual)
        self.assertEqual(individual["relationship"], HEAD)
        self.assertEqual(individual["role"], ROLE_NO_ROLE)
        self.assertEqual(individual["tax_id"], tax_id)

    def test_getting_individual_with_status_merged_to_population(self):
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(type=IDENTIFICATION_TYPE_TAX_ID)
        document = DocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number

        response = self.api_client.get(f"/api/hh-status?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "merged to population")
        self.assertEqual(info["date"], _time(household.created_at))

    def test_getting_individual_with_status_targeted(self):
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(type=IDENTIFICATION_TYPE_TAX_ID)
        document = DocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number

        target_popuplation = TargetPopulationFactory(
            business_area=self.business_area,
            created_by=self.user,
        )
        target_popuplation.households.add(household)

        response = self.api_client.get(f"/api/hh-status?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "targeted")
        self.assertEqual(info["date"], _time(HouseholdSelection.objects.first().updated_at))

    def test_getting_individual_with_status_sent_to_cash_assist(self):
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(type=IDENTIFICATION_TYPE_TAX_ID)
        document = DocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number

        target_popuplation = TargetPopulationFactory(
            business_area=self.business_area,
            created_by=self.user,
        )
        target_popuplation.households.add(household)
        target_popuplation.status = TargetPopulation.STATUS_PROCESSING
        target_popuplation.save()

        response = self.api_client.get(f"/api/hh-status?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "sent to cash assist")

    def test_getting_individual_with_status_paid(self):
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(type=IDENTIFICATION_TYPE_TAX_ID)
        document = DocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number
        payment_record = PaymentRecordFactory(household=household)

        response = self.api_client.get(f"/api/hh-status?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "paid")
        self.assertEqual(info["date"], _time(payment_record.updated_at))

    def test_getting_non_existent_household(self):
        response = self.api_client.get("/api/hh-status?registration_id=non-existent")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["status"], "not found")

    def test_getting_household_with_status_imported(self):
        imported_household = ImportedHouseholdFactory()
        imported_individual = ImportedIndividualFactory(household=imported_household, relationship=HEAD)
        imported_household.head_of_household = imported_individual
        imported_household.kobo_asset_id = "HOPE-2022530111222"
        imported_household.save()
        ImportedIndividualRoleInHousehold.objects.create(
            individual=imported_individual, role=ROLE_NO_ROLE, household=imported_household
        )

        registration_id = imported_household.kobo_asset_id

        response = self.api_client.get(f"/api/hh-status?registration_id={registration_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "imported")
        self.assertEqual(info["date"], _time(imported_household.updated_at))
        self.assertTrue("individual" not in info)
