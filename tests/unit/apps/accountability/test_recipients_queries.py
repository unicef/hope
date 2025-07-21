from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from tests.extras.test_utils.factories.accountability import SurveyFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory


class TestSurveyQueries(APITestCase):
    QUERY_LIST = """
    query Recipients(
        $survey: String!
    ) {
      recipients(survey: $survey) {
        totalCount
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.partner = PartnerFactory(name="TestPartner")
        cls.user = UserFactory.create(first_name="John", last_name="Wick", partner=cls.partner)
        cls.payment_plan = PaymentPlanFactory(business_area=cls.business_area, created_by=cls.user)

        create_household()
        cls.households = [create_household()[0] for _ in range(4)]
        for household in cls.households:
            PaymentFactory(parent=cls.payment_plan, household=household)

    @parameterized.expand(
        [
            ("without_permissions", []),
            ("with_permissions", [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS]),
        ]
    )
    def test_query_list(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        survey = SurveyFactory(payment_plan=self.payment_plan, created_by=self.user)
        survey.recipients.set(self.households)

        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "survey": self.id_to_base64(survey.id, "SurveyNode"),
            },
        )
