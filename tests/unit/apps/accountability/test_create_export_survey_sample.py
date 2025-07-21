from unittest.mock import patch
from uuid import uuid4

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.program.models import Program
from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from tests.extras.test_utils.factories.accountability import SurveyFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from tests.extras.test_utils.factories.program import ProgramFactory


class TestSurveyQueries(APITestCase):
    MUTATION = """
mutation ExportSurveySample($surveyId: ID!) {
  exportSurveySample (surveyId: $surveyId) {
    survey {
      title
      paymentPlan {
        name
      }
    }
  }
}
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory(first_name="John", last_name="Wick", partner=partner)
        cls.program = ProgramFactory(status=Program.ACTIVE, business_area=cls.business_area)
        cls.payment_plan = PaymentPlanFactory(
            business_area=cls.business_area,
            name="Test Target Population",
            created_by=cls.user,
            program_cycle=cls.program.cycles.first(),
        )
        cls.update_partner_access_to_program(partner, cls.program)

        households = [create_household()[0] for _ in range(14)]
        for hh in households:
            PaymentFactory(
                parent=cls.payment_plan,
                household=hh,
            )

        cls.survey = SurveyFactory(title="Test survey", payment_plan=cls.payment_plan, created_by=cls.user)

    def test_create_export_survey_sample_without_permissions(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "surveyId": self.id_to_base64(self.survey.id, "SurveyNode"),
            },
        )

    @patch(
        "hct_mis_api.apps.accountability.celery_tasks.export_survey_sample_task.delay",
        new=lambda *args, **kwargs: None,
    )
    def test_create_export_survey_sample_with_valid_survey_id(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "surveyId": self.id_to_base64(self.survey.id, "SurveyNode"),
            },
        )

    @patch(
        "hct_mis_api.apps.accountability.celery_tasks.export_survey_sample_task.delay",
        new=lambda *args, **kwargs: None,
    )
    def test_create_export_survey_sample_with_invalid_survey_id(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "surveyId": self.id_to_base64(str(uuid4()), "SurveyNode"),
            },
        )
