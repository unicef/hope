from typing import List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.fixtures import CashPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory

QUERY_SINGLE_CASH_PLAN = """
query CashPlan($id: ID!) {
  cashPlan(id: $id) {
    name
    dispersionDate
    totalPersonsCovered
    coverageDuration
    coverageUnit
    caId
    status
    assistanceMeasurement
    totalEntitledQuantity
    totalDeliveredQuantity
    totalUndeliveredQuantity
    dispersionDate
    deliveryType
    assistanceThrough
  }
}
"""

QUERY_ALL_CASH_PLANS = """
query AllCashPlans {
  allCashPlans(businessArea: "afghanistan") {
    edges {
      node {
        name
        dispersionDate
        totalPersonsCovered
        coverageDuration
        coverageUnit
        caId
        status
        assistanceMeasurement
        totalEntitledQuantity
        totalDeliveredQuantity
        totalUndeliveredQuantity
        dispersionDate
        deliveryType
        assistanceThrough
      }
    }
  }
}
"""


class TestCashPlanQueries(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.partner = PartnerFactory(name="Test1")
        cls.user = UserFactory(partner=cls.partner)
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        program = ProgramFactory.create(business_area=cls.business_area)
        cls.CASH_PLANS_TO_CREATE = [
            {
                "business_area": cls.business_area,
                "id": "c7e768f1-5626-413e-a032-5fb18789f985",
                "ca_id": "7ff3542c-8c48-4ed4-8283-41966093995b",
                "coverage_duration": 21,
                "coverage_unit": "Day(s)",
                "assistance_measurement": "Syrian pound",
                "dispersion_date": "2020-04-25T00:00:00+00:00",
                "distribution_level": "Registration Group",
                "name": "Far yet reveal area bar almost dinner.",
                "total_persons_covered": 540,
                "status": "Transaction Completed",
                "total_delivered_quantity": 53477453.27,
                "total_entitled_quantity": 56657648.82,
                "total_undelivered_quantity": 55497021.04,
                "delivery_type": DeliveryMechanismChoices.DELIVERY_TYPE_DEPOSIT_TO_CARD,
                "assistance_through": "Cairo Amman Bank",
            },
            {
                "business_area": cls.business_area,
                "ca_id": "04b9d44b-67fe-425c-9095-509e31ba7494",
                "coverage_duration": 19,
                "coverage_unit": "Week(s)",
                "assistance_measurement": "Cuban peso",
                "dispersion_date": "2020-02-22T00:00:00+00:00",
                "distribution_level": "Registration Group",
                "name": "Despite action TV after.",
                "total_persons_covered": 100,
                "status": "Transaction Completed",
                "total_delivered_quantity": 41935107.03,
                "total_entitled_quantity": 38204833.92,
                "total_undelivered_quantity": 63098825.46,
                "delivery_type": DeliveryMechanismChoices.DELIVERY_TYPE_DEPOSIT_TO_CARD,
                "assistance_through": "Cairo Amman Bank",
            },
        ]

        for cash_plan in cls.CASH_PLANS_TO_CREATE:
            CashPlanFactory.create(
                program=program,
                **cash_plan,
            )

    @parameterized.expand(
        [
            ("all_with_permission", [Permissions.PAYMENT_VERIFICATION_VIEW_LIST], QUERY_ALL_CASH_PLANS),
            ("all_without_permission", [], QUERY_ALL_CASH_PLANS),
            ("single_with_permission", [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS], QUERY_SINGLE_CASH_PLAN),
            ("single_without_permission", [], QUERY_SINGLE_CASH_PLAN),
        ]
    )
    def test_cash_plans(self, name: str, permissions: List[Permissions], query: str) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        variables = {}
        if "single" in name:
            variables["id"] = self.id_to_base64("c7e768f1-5626-413e-a032-5fb18789f985", "CashPlanNode")

        self.snapshot_graphql_request(
            request_string=query,
            variables=variables,
            context={"user": self.user},
        )
