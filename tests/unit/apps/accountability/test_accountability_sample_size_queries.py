from parameterized import parameterized

from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.program.models import Program
from tests.extras.test_utils.factories.account import UserFactory
from tests.extras.test_utils.factories.accountability import SurveyFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from tests.extras.test_utils.factories.program import ProgramFactory


class TestAccountabilitySampleSizeQueries(APITestCase):
    QUERY = """
    query AccountabilitySampleSize(
        $input: AccountabilitySampleSizeInput!
    ) {
      accountabilitySampleSize(input: $input) {
        numberOfRecipients
        sampleSize
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory(first_name="John", last_name="Wick")
        cls.program = ProgramFactory(status=Program.ACTIVE)
        cls.payment_plan = PaymentPlanFactory(
            business_area=cls.business_area, created_by=cls.user, program_cycle=cls.program.cycles.first()
        )

        households = [create_household()[0] for _ in range(14)]
        for household in households:
            PaymentFactory(parent=cls.payment_plan, household=household)

        SurveyFactory.create_batch(3, payment_plan=cls.payment_plan, created_by=cls.user)
        SurveyFactory(title="Test survey", payment_plan=cls.payment_plan, created_by=cls.user)
        SurveyFactory.create_batch(
            3,
            payment_plan=PaymentPlanFactory(
                business_area=cls.business_area, created_by=cls.user, program_cycle=cls.program.cycles.first()
            ),
            created_by=UserFactory(),
        )
        cls.sampling_data = {
            Survey.SAMPLING_FULL_LIST: {
                "fullListArguments": {
                    "excludedAdminAreas": [],
                },
            },
            Survey.SAMPLING_RANDOM: {
                "randomSamplingArguments": {
                    "age": {"min": 20, "max": 80},
                    # "sex": MALE,
                    "confidenceInterval": 0.8,
                    "marginOfError": 80,
                    "excludedAdminAreas": [],
                },
            },
        }

    @parameterized.expand(
        [
            (Survey.SAMPLING_FULL_LIST,),
            (Survey.SAMPLING_RANDOM,),
        ]
    )
    def test_sample_size_by_target_population(self, sampling_type: str) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "paymentPlan": self.id_to_base64(self.payment_plan.id, "PaymentPlanNode"),
                    "samplingType": sampling_type,
                    **self.sampling_data[sampling_type],
                }
            },
        )
