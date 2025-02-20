import datetime

from django.conf import settings
from django.test import TestCase

from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.fixtures import (
    DocumentTypeFactory,
    PendingDocumentFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    create_household,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_TAX_ID,
    ROLE_NO_ROLE,
    PendingIndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


# used for ease of assertions, so it imitates serializer's behaviour
def _time(some_time: datetime.date) -> str:
    return str(some_time).replace(" ", "T").replace("+00:00", "Z")


class TestDetails(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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

    def test_filtering_business_area_code_with_tax_id(self) -> None:
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID])
        document = PendingDocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number

        response_ok = self.api_client.get(
            f"/api/hh-status?tax_id={tax_id}&business_area_code={self.business_area.code}"
        )
        self.assertEqual(response_ok.status_code, 200)

        response_nok = self.api_client.get(f"/api/hh-status?tax_id={tax_id}&business_area_code=non-existent")
        self.assertEqual(response_nok.status_code, 404)

    def test_filtering_business_area_code_with_detail_id(self) -> None:
        rdi = RegistrationDataImportFactory(business_area=self.business_area)
        pending_household = PendingHouseholdFactory(registration_data_import=rdi)
        pending_individual = PendingIndividualFactory(household=pending_household, relationship=HEAD)
        pending_household.head_of_household = pending_individual
        pending_household.detail_id = "HOPE-2022530111222"
        pending_household.save()
        PendingIndividualRoleInHousehold.objects.create(
            individual=pending_individual,
            role=ROLE_NO_ROLE,
            household=pending_household,
        )

        detail_id = pending_household.detail_id

        response_ok = self.api_client.get(
            f"/api/hh-status?detail_id={detail_id}&business_area_code={self.business_area.code}"
        )
        self.assertEqual(response_ok.status_code, 200)

        response_nok = self.api_client.get(f"/api/hh-status?detail_id={detail_id}&business_area_code=non-existent")
        self.assertEqual(response_nok.status_code, 404)

    def test_getting_non_existent_individual(self) -> None:
        response = self.api_client.get("/api/hh-status?tax_id=non-existent")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["status"], "not found")

    def test_getting_individual_with_status_imported(self) -> None:
        pending_household = PendingHouseholdFactory()
        pending_individual = PendingIndividualFactory(household=pending_household, relationship=HEAD)
        pending_household.head_of_household = pending_individual
        pending_household.save()
        PendingIndividualRoleInHousehold.objects.create(
            individual=pending_individual,
            role=ROLE_NO_ROLE,
            household=pending_household,
        )

        document_type = DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID])
        pending_document = PendingDocumentFactory(individual=pending_individual, type=document_type)
        tax_id = pending_document.document_number

        response = self.api_client.get(f"/api/hh-status?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "imported")
        self.assertEqual(info["date"], _time(pending_household.updated_at))

        individual = info["individual"]
        self.assertIsNotNone(individual)
        self.assertEqual(individual["relationship"], HEAD)
        self.assertEqual(individual["role"], ROLE_NO_ROLE)
        self.assertEqual(individual["tax_id"], tax_id)

    def test_getting_individual_with_status_merged_to_population(self) -> None:
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID])
        document = PendingDocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number

        response = self.api_client.get(f"/api/hh-status?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "merged to population")
        self.assertEqual(info["date"], _time(household.created_at))

    def test_getting_individual_with_status_targeted(self) -> None:
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID])
        document = PendingDocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number
        payment_plan = PaymentPlanFactory(
            business_area=self.business_area,
            created_by=self.user,
        )
        PaymentFactory(
            parent=payment_plan,
            household=household,
            delivered_quantity=None,
        )

        response = self.api_client.get(f"/api/hh-status?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "merged to population")
        self.assertEqual(info["date"], _time(household.created_at))

    def test_getting_individual_with_status_sent_to_cash_assist(self) -> None:
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID])
        document = PendingDocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number
        payment_plan = PaymentPlanFactory(
            business_area=self.business_area,
            created_by=self.user,
            status=PaymentPlan.Status.TP_LOCKED,
        )
        PaymentFactory(
            parent=payment_plan,
            household=household,
            status=Payment.STATUS_PENDING,
            delivered_quantity=999,
        )

        response = self.api_client.get(f"/api/hh-status?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "paid")

    def test_getting_individual_with_status_paid(self) -> None:
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID])
        document = PendingDocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number
        payment = PaymentFactory(
            household=household, currency="PLN", delivery_date=datetime.date.today(), delivered_quantity=1
        )

        response = self.api_client.get(f"/api/hh-status?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "paid")
        self.assertEqual(datetime.datetime.fromisoformat(info["date"].replace("Z", "")).date(), payment.delivery_date)

    def test_getting_non_existent_household(self) -> None:
        response = self.api_client.get("/api/hh-status?detail_id=non-existent")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["status"], "not found")

    def test_getting_household_with_status_imported(self) -> None:
        pending_household = PendingHouseholdFactory()
        pending_individual = PendingIndividualFactory(household=pending_household, relationship=HEAD)
        pending_household.head_of_household = pending_individual
        pending_household.detail_id = "HOPE-2022530111222"
        pending_household.save()
        PendingIndividualRoleInHousehold.objects.create(
            individual=pending_individual,
            role=ROLE_NO_ROLE,
            household=pending_household,
        )

        detail_id = pending_household.detail_id

        response = self.api_client.get(f"/api/hh-status?detail_id={detail_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "imported")
        self.assertEqual(info["date"], _time(pending_household.updated_at))
        self.assertTrue("individual" not in info)
