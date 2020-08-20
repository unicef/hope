from datetime import datetime

from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea
from program.fixtures import CashPlanFactory, ProgramFactory


class TestCashPlanQueries(APITestCase):
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
      allCashPlans {
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

    CASH_PLANS_TO_CREATE = []

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory()
        program = ProgramFactory.create(business_area=BusinessArea.objects.order_by("?").first())
        self.CASH_PLANS_TO_CREATE = [
            {
                "business_area": BusinessArea.objects.first(),
                "id": "c7e768f1-5626-413e-a032-5fb18789f985",
                "ca_id": "7ff3542c-8c48-4ed4-8283-41966093995b",
                "coverage_duration": 21,
                "coverage_unit": "Day(s)",
                "assistance_measurement": "Syrian pound",
                "dispersion_date": "2020-04-25",
                "distribution_level": "Registration Group",
                "end_date": datetime.strptime("2064-03-14T22:52:54", "%Y-%m-%dT%H:%M:%S",),
                "name": "Far yet reveal area bar almost dinner.",
                "total_persons_covered": 540,
                "start_date": datetime.strptime("2051-11-30T00:02:09", "%Y-%m-%dT%H:%M:%S",),
                "status": "Transaction Completed",
                "total_delivered_quantity": 53477453.27,
                "total_entitled_quantity": 56657648.82,
                "total_undelivered_quantity": 55497021.04,
                "delivery_type": "Deposit to Card",
                "assistance_through": "Cairo Amman Bank",
            },
            {
                "business_area": BusinessArea.objects.first(),
                "ca_id": "04b9d44b-67fe-425c-9095-509e31ba7494",
                "coverage_duration": 19,
                "coverage_unit": "Week(s)",
                "assistance_measurement": "Cuban peso",
                "dispersion_date": "2020-02-22",
                "distribution_level": "Registration Group",
                "end_date": datetime.strptime("2028-03-31T18:44:15", "%Y-%m-%dT%H:%M:%S",),
                "name": "Despite action TV after.",
                "total_persons_covered": 100,
                "start_date": datetime.strptime("2041-06-14T10:15:44", "%Y-%m-%dT%H:%M:%S",),
                "status": "Transaction Completed",
                "total_delivered_quantity": 41935107.03,
                "total_entitled_quantity": 38204833.92,
                "total_undelivered_quantity": 63098825.46,
                "delivery_type": "Deposit to Card",
                "assistance_through": "Cairo Amman Bank",
            },
        ]

        for cash_plan in self.CASH_PLANS_TO_CREATE:
            CashPlanFactory.create(
                program=program, **cash_plan,
            )

    def test_get_single_cash_plan(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_SINGLE_CASH_PLAN,
            variables={"id": "Q2FzaFBsYW5Ob2RlOmM3ZTc2OGYxLTU2M" "jYtNDEzZS1hMDMyLTVmYjE4Nzg5Zjk4NQ=="},
            context={"user": self.user},
        )

    def test_get_all_cash_plans(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_ALL_CASH_PLANS, context={"user": self.user},
        )
