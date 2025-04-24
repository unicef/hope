from unittest import skip
from unittest.mock import patch
from uuid import uuid4

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.fixtures import SurveyFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


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
        cls.create_partner_role_with_permissions(partner, [], cls.business_area, cls.program)
        cls.payment_plan = PaymentPlanFactory(
            business_area=cls.business_area,
            name="Test Target Population",
            created_by=cls.user,
            program_cycle=cls.program.cycles.first(),
        )

        households = [create_household()[0] for _ in range(14)]
        for hh in households:
            PaymentFactory(
                parent=cls.payment_plan,
                household=hh,
            )

        cls.survey = SurveyFactory(title="Test survey", payment_plan=cls.payment_plan, created_by=cls.user)

    @skip("Because will remove soon after REST refactoring")
    def test_create_export_survey_sample_without_permissions(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area, self.program)

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
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS], self.business_area, self.program
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
    @skip("Because will remove soon after REST refactoring")
    def test_create_export_survey_sample_with_invalid_survey_id(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS], self.business_area, self.program
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
