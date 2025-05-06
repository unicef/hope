from unittest.mock import MagicMock, patch

import django

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.celery_tasks import send_survey_to_users
from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.services.rapid_pro.api import RapidProFlowResponse
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


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
        surveyAvailableFlows {
            id
            name
        }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory(first_name="John", last_name="Doe", partner=partner)
        cls.program = ProgramFactory(status=Program.ACTIVE, business_area=cls.business_area)
        cls.pp = PaymentPlanFactory(
            business_area=cls.business_area, created_by=cls.user, program_cycle=cls.program.cycles.first()
        )
        cls.update_partner_access_to_program(partner, cls.program)

    def test_create_survey_without_permission(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    "title": "Test survey",
                    "category": Survey.CATEGORY_MANUAL,
                    "samplingType": Survey.SAMPLING_RANDOM,
                    "flow": "flow123",
                    "paymentPlan": self.id_to_base64(str(self.pp.pk), "PaymentPlanNode"),
                }
            },
        )

    def test_create_survey_without_target_population_and_program(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
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
        for household in households:
            PaymentFactory(parent=self.pp, household=household)

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    "title": "Test survey",
                    "category": Survey.CATEGORY_MANUAL,
                    "samplingType": Survey.SAMPLING_FULL_LIST,
                    "paymentPlan": self.id_to_base64(str(self.pp.id), "PaymentPlanNode"),
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
        for household in households:
            PaymentFactory(parent=self.pp, household=household)

        with (
            patch.object(django.db.transaction, "on_commit", lambda t: t()),
            patch("hct_mis_api.apps.accountability.celery_tasks.send_survey_to_users.delay") as task_mock,
        ):
            self.snapshot_graphql_request(
                request_string=self.CREATE_SURVEY_MUTATION,
                context={
                    "user": self.user,
                    "headers": {
                        "Business-Area": self.business_area.slug,
                        "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    },
                },
                variables={
                    "input": {
                        "title": "Test survey",
                        "category": Survey.CATEGORY_RAPID_PRO,
                        "samplingType": Survey.SAMPLING_FULL_LIST,
                        "paymentPlan": self.id_to_base64(self.pp.id, "PaymentPlanNode"),
                        "fullListArguments": {
                            "excludedAdminAreas": [],
                        },
                        "flow": "flow123",
                    }
                },
            )
            survey = Survey.objects.get(title="Test survey")
            assert task_mock.called
            assert task_mock.call_args[0][0] == survey.id

        households_ids = self.pp.payment_items.values_list("household_id", flat=True)
        households = Household.objects.filter(id__in=households_ids)
        assert households[0].individuals.count() == 3
        phone_number_1 = households[0].head_of_household.phone_no
        phone_number_2 = households[1].head_of_household.phone_no
        phone_number_3 = households[2].head_of_household.phone_no

        with patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)):
            start_flow_mock_1 = MagicMock(
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
                "hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.start_flow",
                start_flow_mock_1,
            ):
                survey.refresh_from_db()
                assert len(survey.successful_rapid_pro_calls) == 0

                send_survey_to_users(survey.id)
                survey.refresh_from_db()

                assert start_flow_mock_1.call_count == 1
                assert start_flow_mock_1.call_args[0][0] == "flow123"
                assert len(start_flow_mock_1.call_args[0][1]) == 3  # sending only to HOHs, 3 households
                assert len(survey.successful_rapid_pro_calls) == 1
                assert survey.successful_rapid_pro_calls[0]["flow_uuid"] == "flow123"
                assert survey.successful_rapid_pro_calls[0]["urns"] == [phone_number_1, phone_number_2]

            start_flow_mock_2 = MagicMock(
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
                "hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.start_flow",
                start_flow_mock_2,
            ):
                send_survey_to_users(survey.id)
                survey.refresh_from_db()
                assert start_flow_mock_2.call_count == 1
                assert start_flow_mock_2.call_args[0][0] == "flow123"
                assert len(start_flow_mock_2.call_args[0][1]) == 1  # 2 HOHs in households remaining total
                assert len(survey.successful_rapid_pro_calls) == 2
                assert survey.successful_rapid_pro_calls[1]["flow_uuid"] == "flow123"
                assert survey.successful_rapid_pro_calls[1]["urns"] == [phone_number_3]

    def test_create_survey_without_recipients(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.CREATE_SURVEY_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "input": {
                    "title": "Test survey",
                    "category": Survey.CATEGORY_MANUAL,
                    "samplingType": Survey.SAMPLING_FULL_LIST,
                    "paymentPlan": self.id_to_base64(self.pp.id, "PaymentPlanNode"),
                    "fullListArguments": {
                        "excludedAdminAreas": [],
                    },
                    "flow": "flow123",
                }
            },
        )

    def test_getting_available_flows(self) -> None:
        with (
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)),
            patch(
                "hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.get_flows",
                MagicMock(return_value=[{"uuid": 123, "name": "flow2"}, {"uuid": 234, "name": "flow2"}]),
            ),
        ):
            self.snapshot_graphql_request(
                request_string=self.AVAILABLE_FLOWS,
                context={
                    "user": self.user,
                    "headers": {
                        "Business-Area": self.business_area.slug,
                        "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    },
                },
                variables={},
            )
