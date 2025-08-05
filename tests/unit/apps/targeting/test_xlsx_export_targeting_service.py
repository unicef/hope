from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    create_household_and_individuals,
)
from extras.test_utils.factories.payment import (
    AccountFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.targeting import TargetingCriteriaRuleFactory

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.payment.models import AccountType, PaymentPlan
from hct_mis_api.apps.targeting.services.xlsx_export_targeting_service import (
    XlsxExportTargetingService,
)


class TestXlsxExportTargetingService(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.payment_plan = PaymentPlanFactory(
            business_area=cls.business_area,
            status=PaymentPlan.Status.TP_OPEN,
            created_by=cls.user,
        )

    def test_add_version(self) -> None:
        service = XlsxExportTargetingService(self.payment_plan)
        service._create_workbook()
        service._add_version()
        self.assertEqual(
            service.ws_meta[XlsxExportTargetingService.VERSION_CELL_NAME_COORDINATES].value,
            XlsxExportTargetingService.VERSION_CELL_NAME,
        )
        self.assertEqual(
            service.ws_meta[XlsxExportTargetingService.VERSION_CELL_COORDINATES].value,
            XlsxExportTargetingService.VERSION,
        )

    def test_add_standard_columns_headers(self) -> None:
        service = XlsxExportTargetingService(self.payment_plan)
        service._create_workbook()
        service._add_standard_columns_headers()
        headers = [cell.value for cell in service.ws_individuals[1]]
        self.assertEqual(headers, ["Household unicef_id", "unicef_id", "Linked Households", "Accounts information"])

    def test_export_service_households_property(self) -> None:
        program = self.payment_plan.program_cycle.program
        hh1 = HouseholdFactory(
            business_area=self.business_area, program=program, head_of_household=IndividualFactory(household=None)
        )
        hh2 = HouseholdFactory(
            business_area=self.business_area, program=program, head_of_household=IndividualFactory(household=None)
        )
        p1 = PaymentFactory(
            parent=self.payment_plan,
            vulnerability_score=11,
            household=hh1,
        )
        p2 = PaymentFactory(
            parent=self.payment_plan,
            vulnerability_score=99,
            household=hh2,
        )
        TargetingCriteriaRuleFactory(
            household_ids=f"{p1.household.unicef_id}, {p2.household.unicef_id}",
            payment_plan=self.payment_plan,
        )

        service = XlsxExportTargetingService(self.payment_plan)
        self.assertEqual(len(service.households), 2)

        self.payment_plan.status = PaymentPlan.Status.LOCKED
        self.payment_plan.vulnerability_score_min = 10
        self.payment_plan.vulnerability_score_max = 12
        self.payment_plan.save()

        service = XlsxExportTargetingService(self.payment_plan)
        self.assertEqual(len(service.households), 1)
        self.assertEqual(service.households.first().unicef_id, p1.household.unicef_id)

    def test_accounts_info(self) -> None:
        generate_delivery_mechanisms()
        service = XlsxExportTargetingService(self.payment_plan)

        _, individuals = create_household_and_individuals(
            household_data={"business_area": self.business_area, "program": self.payment_plan.program_cycle.program},
            individuals_data=[
                {
                    "full_name": "Benjamin Butler",
                    "given_name": "Benjamin",
                    "family_name": "Butler",
                    "phone_no": "(953)682-4596",
                    "birth_date": "1943-07-30",
                    "id": "ffb2576b-126f-42de-b0f5-ef889b7bc1fe",
                    "business_area": self.business_area,
                },
            ],
        )
        individual = individuals[0]
        AccountFactory(
            individual=individual,
            account_type=AccountType.objects.get(key="bank"),
            data={
                "card_number": "123",
                "card_expiry_date": "2022-01-01",
                "name_of_cardholder": "Marek",
            },
            number="123",
        )
        AccountFactory(
            individual=individual,
            account_type=AccountType.objects.get(key="mobile"),
            data={
                "service_provider_code": "ABC",
                "delivery_phone_number": "123456789",
                "provider": "Provider",
            },
            number="321",
        )

        self.assertEqual(
            service._accounts_info(individual),
            "{'card_number': '123', 'card_expiry_date': '2022-01-01',"
            " 'name_of_cardholder': 'Marek', 'number': '123'}, {'provider': 'Provider', 'delivery_phone_number': '123456789', 'service_provider_code': 'ABC', 'number': '321'}",
        )
