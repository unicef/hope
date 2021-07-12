from decimal import Decimal

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.fixtures import CashPlanFactory, ProgramFactory


class TestHouseholdWithProgramsQuantityQuery(APITestCase):
    QUERY = """
        query Household($id: ID!) {
          household(id: $id) {
            programsWithDeliveredQuantity {
                totalDeliveredQuantity
                totalDeliveredQuantityUsd
                currency
            }
          }
        }
        """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        household, _ = create_household({"size": 2, "address": "Lorem Ipsum", "country_origin": "PL"})
        self.household = household
        self.program = ProgramFactory.create(
            name="Test program ONE",
            business_area=self.business_area,
        )

        cash_plan1 = CashPlanFactory.create(program=self.program)
        cash_plan2 = CashPlanFactory.create(program=self.program)

        PaymentRecordFactory.create_batch(
            3,
            cash_plan=cash_plan1,
            currency="USD",
            delivered_quantity_usd=100,
            delivered_quantity=100,
            household=household,
        )
        PaymentRecordFactory.create_batch(
            3,
            cash_plan=cash_plan2,
            currency="USD",
            delivered_quantity_usd=200,
            delivered_quantity=200,
            household=household,
        )

        payment_records = PaymentRecord.objects.all()[:2]
        for payment_record in payment_records:
            payment_record.currency = "AFG"
            payment_record.delivered_quantity = payment_record.delivered_quantity_usd * Decimal(0.8)

        PaymentRecord.objects.bulk_update(payment_records, ["currency", "delivered_quantity"])

        self.household.programs.add(self.program)

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_household_query_single(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.household.id, "HouseholdNode")},
        )
