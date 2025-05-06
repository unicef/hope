from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetingCriteriaRuleFactory,
)
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
        assert (
            service.ws_meta[XlsxExportTargetingService.VERSION_CELL_NAME_COORDINATES].value
            == XlsxExportTargetingService.VERSION_CELL_NAME
        )
        assert (
            service.ws_meta[XlsxExportTargetingService.VERSION_CELL_COORDINATES].value
            == XlsxExportTargetingService.VERSION
        )

    def test_add_standard_columns_headers(self) -> None:
        service = XlsxExportTargetingService(self.payment_plan)
        service._create_workbook()
        service._add_standard_columns_headers()
        headers = [cell.value for cell in service.ws_individuals[1]]
        assert headers == ["Household unicef_id", "unicef_id", "Linked Households", "Bank account information"]

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
        targeting_criteria = TargetingCriteriaFactory()
        TargetingCriteriaRuleFactory(
            targeting_criteria=targeting_criteria, household_ids=f"{p1.household.unicef_id}, {p2.household.unicef_id}"
        )
        self.payment_plan.targeting_criteria = targeting_criteria
        self.payment_plan.save()
        service = XlsxExportTargetingService(self.payment_plan)
        assert len(service.households) == 2

        self.payment_plan.status = PaymentPlan.Status.LOCKED
        self.payment_plan.vulnerability_score_min = 10
        self.payment_plan.vulnerability_score_max = 12
        self.payment_plan.save()

        service = XlsxExportTargetingService(self.payment_plan)
        assert len(service.households) == 1
        assert service.households.first().unicef_id == p1.household.unicef_id
