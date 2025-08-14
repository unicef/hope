import datetime

from django.core.management import call_command
from django.test import TestCase

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.household import (
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    PendingDocumentFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    create_household,
)
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from rest_framework.test import APIClient

from hope.apps.core.models import BusinessArea
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_TAX_ID,
    ROLE_NO_ROLE,
    PendingIndividualRoleInHousehold,
)
from hope.apps.payment.models import Payment, PaymentPlan


# used for ease of assertions, so it imitates serializer's behaviour
def _time(some_time: datetime.date) -> str:
    return str(some_time).replace(" ", "T").replace("+00:00", "Z")


class TestDetails(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init-geo-fixtures")
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
        self.assertEqual(response.json()["detail"], "Document with given tax_id: non-existent not found")

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
        self.assertEqual(response.json()["detail"], "Household with given detail_id: non-existent not found")

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

    def test_getting_household_with_status_paid(self) -> None:
        detail_id = "HOPE-2022530111222"
        household = HouseholdFactory(detail_id=detail_id)
        individual = IndividualFactory(household=household, relationship=HEAD)
        individual.head_of_household = individual
        individual.save()
        payment = PaymentFactory(household=household, delivered_quantity=1000, collector=individual)
        response = self.api_client.get(f"/api/hh-status?detail_id={detail_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "paid")
        self.assertEqual(info["date"], _time(payment.delivery_date))
        self.assertTrue("individual" not in info)

    def test_query_params_validation(self) -> None:
        response = self.api_client.get("/api/hh-status?detail_id=xxx&tax_id=yyy")
        self.assertEqual(response.status_code, 400)

        response = self.api_client.get("/api/hh-status")
        self.assertEqual(response.status_code, 400)

    def test_households_count_gt_1(self) -> None:
        detail_id = "123"

        PendingHouseholdFactory(detail_id=detail_id)
        PendingHouseholdFactory(detail_id=detail_id)
        response = self.api_client.get(f"/api/hh-status?detail_id={detail_id}")
        self.assertEqual(response.status_code, 400)

        HouseholdFactory(detail_id=detail_id)
        HouseholdFactory(detail_id=detail_id)
        response = self.api_client.get(f"/api/hh-status?detail_id={detail_id}")
        self.assertEqual(response.status_code, 400)

    def test_documents_count_gt_1(self) -> None:
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID])
        PendingDocumentFactory(individual=individual, type=document_type, document_number="123")
        PendingDocumentFactory(individual=individual, type=document_type, document_number="123")

        response = self.api_client.get("/api/hh-status?tax_id=123")
        self.assertEqual(response.status_code, 400)
