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
        disbursementDate
        numberOfHouseholds
        coverageDuration
        coverageUnits
        cashAssistId
        distributionModality
        fsp
        status
        currency
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
            disbursementDate
            numberOfHouseholds
            coverageDuration
            coverageUnits
            cashAssistId
            distributionModality
            fsp
            status
            currency
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

    CASH_PLANS_TO_CREATE = [
        {
            "id": "c7e768f1-5626-413e-a032-5fb18789f985",
            "cash_assist_id": "7ff3542c-8c48-4ed4-8283-41966093995b",
            "coverage_duration": 21,
            "coverage_units": "Day(s)",
            "currency": "Syrian pound",
            "disbursement_date": datetime.strptime(
                "2064-03-09T22:52:54", "%Y-%m-%dT%H:%M:%S",
            ),
            "dispersion_date": "2020-04-25",
            "distribution_modality": "994-94",
            "end_date": datetime.strptime(
                "2064-03-14T22:52:54", "%Y-%m-%dT%H:%M:%S",
            ),
            "fsp": "Sullivan Group",
            "name": "Far yet reveal area bar almost dinner.",
            "number_of_households": 540,
            "start_date": datetime.strptime(
                "2051-11-30T00:02:09", "%Y-%m-%dT%H:%M:%S",
            ),
            "status": "NOT_STARTED",
            "total_delivered_quantity": 53477453.27,
            "total_entitled_quantity": 56657648.82,
            "total_undelivered_quantity": 55497021.04,
            "delivery_type": "Deposit to Card",
            "assistance_through": "Cairo Amman Bank",
        },
        {
            "cash_assist_id": "04b9d44b-67fe-425c-9095-509e31ba7494",
            "coverage_duration": 19,
            "coverage_units": "Week(s)",
            "currency": "Cuban peso",
            "disbursement_date": datetime.strptime(
                "2028-03-26T18:44:15", "%Y-%m-%dT%H:%M:%S",
            ),
            "dispersion_date": "2020-02-22",
            "distribution_modality": "513-17",
            "end_date": datetime.strptime(
                "2028-03-31T18:44:15", "%Y-%m-%dT%H:%M:%S",
            ),
            "fsp": "Fox-Moody",
            "name": "Despite action TV after.",
            "number_of_households": 100,
            "start_date": datetime.strptime(
                "2041-06-14T10:15:44", "%Y-%m-%dT%H:%M:%S",
            ),
            "status": "COMPLETE",
            "total_delivered_quantity": 41935107.03,
            "total_entitled_quantity": 38204833.92,
            "total_undelivered_quantity": 63098825.46,
            "delivery_type": "Deposit to Card",
            "assistance_through": "Cairo Amman Bank",
        },
        {
            "cash_assist_id": "e02e9e29-a9bc-4d72-9c95-23fe123662c4",
            "coverage_duration": 29,
            "coverage_units": "Day(s)",
            "currency": "Swazi lilangeni",
            "disbursement_date": datetime.strptime(
                "2077-02-25T19:04:32", "%Y-%m-%dT%H:%M:%S",
            ),
            "dispersion_date": "2020-08-13",
            "distribution_modality": "126-33",
            "end_date": datetime.strptime(
                "2077-03-02T19:04:32", "%Y-%m-%dT%H:%M:%S",
            ),
            "fsp": "Allen-Vargas",
            "name": "Tonight lay range sometimes serious program.",
            "number_of_households": 198,
            "start_date": datetime.strptime(
                "2075-03-04T08:54:21", "%Y-%m-%dT%H:%M:%S",
            ),
            "status": "COMPLETE",
            "total_delivered_quantity": 67021407.24,
            "total_entitled_quantity": 71574231.27,
            "total_undelivered_quantity": 68666170.96,
            "delivery_type": "Deposit to Card",
            "assistance_through": "Cairo Amman Bank",
        },
        {
            "cash_assist_id": "0772b884-0ae1-4d4b-823d-80037eef00af",
            "coverage_duration": 24,
            "coverage_units": "Week(s)",
            "currency": "Peruvian sol",
            "disbursement_date": datetime.strptime(
                "2024-04-17T10:59:34", "%Y-%m-%dT%H:%M:%S",
            ),
            "dispersion_date": "2021-01-04",
            "distribution_modality": "581-10",
            "end_date": datetime.strptime(
                "2024-04-22T10:59:34", "%Y-%m-%dT%H:%M:%S",
            ),
            "fsp": "Walsh-Johnson",
            "name": "Worry degree current.",
            "number_of_households": 454,
            "start_date": datetime.strptime(
                "2065-01-02T00:00:10", "%Y-%m-%dT%H:%M:%S",
            ),
            "status": "STARTED",
            "total_delivered_quantity": 77590217.09,
            "total_entitled_quantity": 45129411.47,
            "total_undelivered_quantity": 31657176.41,
            "delivery_type": "Deposit to Card",
            "assistance_through": "Cairo Amman Bank",
        },
        {
            "cash_assist_id": "357eeb74-f76d-4f12-a02b-8e67f0f90813",
            "coverage_duration": 17,
            "coverage_units": "Day(s)",
            "currency": "Philippine peso",
            "disbursement_date": datetime.strptime(
                "2032-08-04T19:20:26", "%Y-%m-%dT%H:%M:%S",
            ),
            "dispersion_date": "2020-07-03",
            "distribution_modality": "388-88",
            "end_date": datetime.strptime(
                "2032-08-09T19:20:26", "%Y-%m-%dT%H:%M:%S",
            ),
            "fsp": "Strickland, Flores and Robertson",
            "name": "Wide our office trip.",
            "number_of_households": 227,
            "start_date": datetime.strptime(
                "2092-04-11T02:06:37", "%Y-%m-%dT%H:%M:%S",
            ),
            "status": "STARTED",
            "total_delivered_quantity": 41956165.06,
            "total_entitled_quantity": 23032305.51,
            "total_undelivered_quantity": 71567447.8,
            "delivery_type": "Deposit to Card",
            "assistance_through": "Cairo Amman Bank",
        },
        {
            "cash_assist_id": "be4fcbf6-40ba-405d-86be-0010c19a91c4",
            "coverage_duration": 26,
            "coverage_units": "Week(s)",
            "currency": "Serbian dinar",
            "disbursement_date": datetime.strptime(
                "2020-04-15T17:51:54", "%Y-%m-%dT%H:%M:%S",
            ),
            "dispersion_date": "2020-05-13",
            "distribution_modality": "857-37",
            "end_date": datetime.strptime(
                "2020-04-20T17:51:54", "%Y-%m-%dT%H:%M:%S",
            ),
            "fsp": "Stone, Carpenter and Jones",
            "name": "Just study road leg little.",
            "number_of_households": 140,
            "start_date": datetime.strptime(
                "2045-04-01T18:24:31", "%Y-%m-%dT%H:%M:%S",
            ),
            "status": "COMPLETE",
            "total_delivered_quantity": 75231429.04,
            "total_entitled_quantity": 6478697.79,
            "total_undelivered_quantity": 19931436.71,
            "delivery_type": "Deposit to Card",
            "assistance_through": "Cairo Amman Bank",
        },
        {
            "cash_assist_id": "17502569-0613-44f2-94d0-916ad6a7b860",
            "coverage_duration": 14,
            "coverage_units": "Month(s)",
            "currency": "Albanian lek",
            "disbursement_date": datetime.strptime(
                "2036-06-24T11:08:43", "%Y-%m-%dT%H:%M:%S",
            ),
            "dispersion_date": "2020-07-25",
            "distribution_modality": "386-44",
            "end_date": datetime.strptime(
                "2036-06-29T11:08:43", "%Y-%m-%dT%H:%M:%S",
            ),
            "fsp": "Mcknight-Stewart",
            "name": "Six quickly level want left response become.",
            "number_of_households": 261,
            "start_date": datetime.strptime(
                "2067-07-03T01:23:31", "%Y-%m-%dT%H:%M:%S",
            ),
            "status": "STARTED",
            "total_delivered_quantity": 58925502.75,
            "total_entitled_quantity": 71489015.63,
            "total_undelivered_quantity": 58316677.75,
            "delivery_type": "Deposit to Card",
            "assistance_through": "Cairo Amman Bank",
        },
        {
            "cash_assist_id": "ccd0b2b1-85dc-44c2-82f3-906b33a16645",
            "coverage_duration": 12,
            "coverage_units": "Week(s)",
            "currency": "Falkland Islands pound",
            "disbursement_date": datetime.strptime(
                "2093-10-02T09:41:06", "%Y-%m-%dT%H:%M:%S",
            ),
            "dispersion_date": "2020-03-27",
            "distribution_modality": "053-54",
            "end_date": datetime.strptime(
                "2093-10-07T09:41:06", "%Y-%m-%dT%H:%M:%S",
            ),
            "fsp": "Fitzpatrick-Garcia",
            "name": "Our everybody anyone which whom western cultural.",
            "number_of_households": 366,
            "start_date": datetime.strptime(
                "2091-09-04T16:58:02", "%Y-%m-%dT%H:%M:%S",
            ),
            "status": "COMPLETE",
            "total_delivered_quantity": 47098878.58,
            "total_entitled_quantity": 24371399.57,
            "total_undelivered_quantity": 31178307.82,
            "delivery_type": "Deposit to Card",
            "assistance_through": "Cairo Amman Bank",
        },
        {
            "cash_assist_id": "0d4f1c5e-7f83-4f8a-9a9c-82a2af883a83",
            "coverage_duration": 18,
            "coverage_units": "Year(s)",
            "currency": "Hong Kong dollar",
            "disbursement_date": datetime.strptime(
                "2045-12-16T00:24:00", "%Y-%m-%dT%H:%M:%S",
            ),
            "dispersion_date": "2020-03-25",
            "distribution_modality": "361-32",
            "end_date": datetime.strptime(
                "2045-12-21T00:24:00", "%Y-%m-%dT%H:%M:%S",
            ),
            "fsp": "Mueller Group",
            "name": "Maybe resource eight remember.",
            "number_of_households": 175,
            "start_date": datetime.strptime(
                "2087-01-16T01:15:41", "%Y-%m-%dT%H:%M:%S",
            ),
            "status": "COMPLETE",
            "total_delivered_quantity": 63827276.43,
            "total_entitled_quantity": 41776487.16,
            "total_undelivered_quantity": 76468590.87,
            "delivery_type": "Deposit to Card",
            "assistance_through": "Cairo Amman Bank",
        },
        {
            "cash_assist_id": "056d6d6e-2562-4f1e-a37d-00017020a869",
            "coverage_duration": 27,
            "coverage_units": "Month(s)",
            "currency": "Seborga luigino",
            "disbursement_date": datetime.strptime(
                "2034-06-28T03:05:26", "%Y-%m-%dT%H:%M:%S",
            ),
            "dispersion_date": "2020-03-19",
            "distribution_modality": "949-96",
            "end_date": datetime.strptime(
                "2034-07-03T03:05:26", "%Y-%m-%dT%H:%M:%S",
            ),
            "fsp": "Harris-Lin",
            "name": "Suggest call civil natural single side if cut.",
            "number_of_households": 403,
            "start_date": datetime.strptime(
                "2086-04-18T10:59:10", "%Y-%m-%dT%H:%M:%S",
            ),
            "status": "COMPLETE",
            "total_delivered_quantity": 21181440.08,
            "total_entitled_quantity": 73287521.63,
            "total_undelivered_quantity": 29600156.58,
            "delivery_type": "Deposit to Card",
            "assistance_through": "Cairo Amman Bank",
        },
    ]

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory()
        program = ProgramFactory.create(
            business_area=BusinessArea.objects.order_by("?").first()
        )

        for cash_plan in self.CASH_PLANS_TO_CREATE:
            CashPlanFactory.create(
                program=program, created_by=self.user, **cash_plan,
            )

    def test_get_single_cash_plan(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_SINGLE_CASH_PLAN,
            variables={
                "id": "Q2FzaFBsYW5Ob2RlOmM3ZTc2OGYxLTU2M"
                "jYtNDEzZS1hMDMyLTVmYjE4Nzg5Zjk4NQ=="
            },
            context={"user": self.user},
        )

    def test_get_all_cash_plans(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_ALL_CASH_PLANS,
            context={"user": self.user},
        )
