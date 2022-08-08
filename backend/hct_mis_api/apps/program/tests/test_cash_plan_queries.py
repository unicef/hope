from datetime import datetime
from django.utils import timezone

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.payment.fixtures import CashPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory

QUERY_SINGLE_CASH_PLAN = """
query CashPlan($id: ID!) {
  cashPlan(id: $id) {
    name
    startDate
    endDate
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
        startDate
        endDate
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
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory()
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
                "end_date": timezone.make_aware(
                    datetime.strptime(
                        "2064-03-14T22:52:54",
                        "%Y-%m-%dT%H:%M:%S",
                    )
                ),
                "name": "Far yet reveal area bar almost dinner.",
                "total_persons_covered": 540,
                "start_date": timezone.make_aware(
                    datetime.strptime(
                        "2051-11-30T00:02:09",
                        "%Y-%m-%dT%H:%M:%S",
                    )
                ),
                "status": "Transaction Completed",
                "total_delivered_quantity": 53477453.27,
                "total_entitled_quantity": 56657648.82,
                "total_undelivered_quantity": 55497021.04,
                "delivery_type": PaymentRecord.DELIVERY_TYPE_DEPOSIT_TO_CARD,
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
                "end_date": timezone.make_aware(
                    datetime.strptime(
                        "2028-03-31T18:44:15",
                        "%Y-%m-%dT%H:%M:%S",
                    )
                ),
                "name": "Despite action TV after.",
                "total_persons_covered": 100,
                "start_date": timezone.make_aware(
                    datetime.strptime(
                        "2041-06-14T10:15:44",
                        "%Y-%m-%dT%H:%M:%S",
                    )
                ),
                "status": "Transaction Completed",
                "total_delivered_quantity": 41935107.03,
                "total_entitled_quantity": 38204833.92,
                "total_undelivered_quantity": 63098825.46,
                "delivery_type": PaymentRecord.DELIVERY_TYPE_DEPOSIT_TO_CARD,
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
    def test_cash_plans(self, name, permissions, query):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        variables = {}
        if "single" in name:
            variables["id"] = self.id_to_base64("c7e768f1-5626-413e-a032-5fb18789f985", "CashPlanNode")

        self.snapshot_graphql_request(
            request_string=query,
            variables=variables,
            context={"user": self.user},
        )
