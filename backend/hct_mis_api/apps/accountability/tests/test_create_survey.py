from unittest.mock import MagicMock, patch

import django

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.celery_tasks import send_survey_to_users
from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.services.rapid_pro.api import RapidProFlowResponse
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


class TestCreateSurvey(APITestCase):
    CREATE_SURVEY_MUTATION = """
    mutation CreateSurvey($input: CreateSurveyInput!) {
      createSurvey(input: $input) {
        survey {
          title
          numberOfRecipients
          createdBy {
            firstName
            lastName
          }
          rapidProUrl
        }
      }
    }
    """

    AVAILABLE_FLOWS = """
    query AvailableFlows {
        availableFlows {
            id
            name
        }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.user = UserFactory(first_name="John", last_name="Doe")
        cls.tp = TargetPopulationFactory(
            business_area=cls.business_area, program=ProgramFactory(business_area=cls.business_area)
        )

    def test_create_survey_without_permission(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "title": "Test survey",
                    "category": Survey.CATEGORY_MANUAL,
                    "samplingType": Survey.SAMPLING_RANDOM,
                    "flow": "flow123",
                    "targetPopulation": self.id_to_base64(str(self.tp.pk), "TargetPopulationNode"),
                }
            },
        )

    def test_create_survey_without_target_population_and_program(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "title": "Test survey",
                    "category": Survey.CATEGORY_MANUAL,
                    "samplingType": Survey.SAMPLING_RANDOM,
                    "flow": "flow123",
                }
            },
        )

    def test_create_survey(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], self.business_area
        )

        create_household({"size": 3})
        households = [create_household({"size": 3})[0] for _ in range(3)]
        self.tp.households.set(households)

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "title": "Test survey",
                    "category": Survey.CATEGORY_MANUAL,
                    "samplingType": Survey.SAMPLING_FULL_LIST,
                    "targetPopulation": self.id_to_base64(str(self.tp.id), "TargetPopulationNode"),
                    "fullListArguments": {
                        "excludedAdminAreas": [],
                    },
                    "flow": "flow123",
                }
            },
        )

    def test_create_survey_and_send_via_rapidpro(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], self.business_area
        )

        create_household({"size": 3})
        households = [create_household({"size": 3})[0] for _ in range(3)]
        self.tp.households.set(households)

        with patch.object(django.db.transaction, "on_commit", lambda t: t()), patch(
            "hct_mis_api.apps.accountability.celery_tasks.send_survey_to_users.delay"
        ) as task_mock:
            self.snapshot_graphql_request(
                request_string=self.CREATE_SURVEY_MUTATION,
                context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
                variables={
                    "input": {
                        "title": "Test survey",
                        "category": Survey.CATEGORY_MANUAL,
                        "samplingType": Survey.SAMPLING_FULL_LIST,
                        "targetPopulation": self.id_to_base64(self.tp.id, "TargetPopulationNode"),
                        "fullListArguments": {
                            "excludedAdminAreas": [],
                        },
                        "flow": "flow123",
                    }
                },
            )
            survey = Survey.objects.get(title="Test survey")
            self.assertTrue(task_mock.called)
            self.assertEqual(task_mock.call_args[0][0], survey.id)
            self.assertEqual(task_mock.call_args[0][1], "flow123")
            self.assertEqual(task_mock.call_args[0][2], self.business_area.id)

        households = self.tp.households.all()
        self.assertEqual(households[0].individuals.count(), 3)
        phone_number_1 = households[0].individuals.first().phone_no
        phone_number_2 = households[1].individuals.first().phone_no
        phone_number_3 = households[2].individuals.first().phone_no

        with patch(
            "hct_mis_api.apps.payment.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)
        ):
            start_flows_mock_1 = MagicMock(
                return_value=(
                    [
                        RapidProFlowResponse(
                            response={
                                "uuid": "flow123",
                            },
                            urns=[phone_number_1, phone_number_2],
                        )
                    ],
                    None,
                )
            )
            with patch(
                "hct_mis_api.apps.payment.services.rapid_pro.api.RapidProAPI.start_flows",
                start_flows_mock_1,
            ):
                survey.refresh_from_db()
                self.assertEqual(len(survey.successful_rapid_pro_calls), 0)

                send_survey_to_users(survey.id, "flow123", self.business_area.id)
                survey.refresh_from_db()

                self.assertEqual(start_flows_mock_1.call_count, 1)
                self.assertEqual(start_flows_mock_1.call_args[0][0], "flow123")
                self.assertEqual(len(start_flows_mock_1.call_args[0][1]), 9)  # 3 inds in 3 households, 9 total
                self.assertEqual(len(survey.successful_rapid_pro_calls), 1)
                self.assertEqual(survey.successful_rapid_pro_calls[0]["flow_uuid"], "flow123")
                self.assertEqual(survey.successful_rapid_pro_calls[0]["urns"], [phone_number_1, phone_number_2])

            start_flows_mock_2 = MagicMock(
                return_value=(
                    [
                        RapidProFlowResponse(
                            response={
                                "uuid": "flow123",
                            },
                            urns=[phone_number_3],
                        )
                    ],
                    None,
                )
            )
            with patch(
                "hct_mis_api.apps.payment.services.rapid_pro.api.RapidProAPI.start_flows",
                start_flows_mock_2,
            ):
                send_survey_to_users(survey.id, "flow123", self.business_area.id)
                survey.refresh_from_db()
                self.assertEqual(start_flows_mock_2.call_count, 1)
                self.assertEqual(start_flows_mock_2.call_args[0][0], "flow123")
                self.assertEqual(len(start_flows_mock_2.call_args[0][1]), 7)  # 7 inds in households remaining total
                self.assertEqual(len(survey.successful_rapid_pro_calls), 2)
                self.assertEqual(survey.successful_rapid_pro_calls[1]["flow_uuid"], "flow123")
                self.assertEqual(survey.successful_rapid_pro_calls[1]["urns"], [phone_number_3])

    def test_create_survey_without_recipients(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={
                "input": {
                    "title": "Test survey",
                    "category": Survey.CATEGORY_MANUAL,
                    "samplingType": Survey.SAMPLING_FULL_LIST,
                    "targetPopulation": self.id_to_base64(self.tp.id, "TargetPopulationNode"),
                    "fullListArguments": {
                        "excludedAdminAreas": [],
                    },
                    "flow": "flow123",
                }
            },
        )

    def test_getting_available_flows(self) -> None:
        with patch(
            "hct_mis_api.apps.payment.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)
        ), patch(
            "hct_mis_api.apps.payment.services.rapid_pro.api.RapidProAPI.get_flows",
            MagicMock(return_value=[{"uuid": 123, "name": "flow2"}, {"uuid": 234, "name": "flow2"}]),
        ):
            self.snapshot_graphql_request(
                request_string=self.AVAILABLE_FLOWS,
                context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
                variables={},
            )
