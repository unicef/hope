from unittest.mock import patch
from uuid import uuid4

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.fixtures import SurveyFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


class TestSurveyQueries(APITestCase):
    MUTATION = """
mutation ExportSurveySample($surveyId: ID!) {
  exportSurveySample (surveyId: $surveyId) {
    survey {
      title
      targetPopulation {
        name
      }
    }
  }
}
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.user = UserFactory(first_name="John", last_name="Wick")
        cls.target_population = TargetPopulationFactory(business_area=cls.business_area, name="Test Target Population")

        households = [create_household()[0] for _ in range(14)]
        cls.target_population.households.set(households)

        cls.survey = SurveyFactory(title="Test survey", target_population=cls.target_population, created_by=cls.user)

    def test_create_export_survey_sample_without_permissions(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
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
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
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
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "surveyId": self.id_to_base64(str(uuid4()), "SurveyNode"),
            },
        )
