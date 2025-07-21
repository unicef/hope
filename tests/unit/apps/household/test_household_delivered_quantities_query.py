from typing import Any, List

from django.conf import settings

from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.payment.models import Payment
from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from tests.extras.test_utils.factories.program import ProgramFactory


class TestHouseholdDeliveredQuantitiesQuery(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    QUERY = """
        query Household($id: ID!) {
          household(id: $id) {
            deliveredQuantities {
              totalDeliveredQuantity
              currency
            }
          }
        }
        """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        partner = PartnerFactory(name="TestPartner")
        cls.user = UserFactory(partner=partner)

        business_area = create_afghanistan()
        program = ProgramFactory.create(name="Test program ONE", business_area=business_area)
        household, _ = create_household(
            {
                "size": 2,
                "address": "Lorem Ipsum",
                "country_origin": geo_models.Country.objects.filter(iso_code2="PL").first(),
                "program": program,
            }
        )
        household.save()

        PaymentFactory(
            parent=PaymentPlanFactory(program_cycle=program.cycles.first()),
            currency="AFG",
            delivered_quantity_usd=50,
            delivered_quantity=100,
            household=household,
            status=Payment.STATUS_SUCCESS,
        )

        PaymentFactory(
            parent=PaymentPlanFactory(program_cycle=program.cycles.first()),
            currency="AFG",
            delivered_quantity_usd=33,
            delivered_quantity=133,
            household=household,
        )

        cls.business_area = business_area
        cls.household = household
        cls.program = program

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_household_query_single(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={"id": self.id_to_base64(self.household.id, "HouseholdNode")},
        )
