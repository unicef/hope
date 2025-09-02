import datetime
from typing import Any, List
from unittest.mock import MagicMock, patch
from urllib.parse import urlencode

from django.urls import reverse
from django.utils import timezone
import pytest
from rest_framework import status

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.accountability import (
    CommunicationMessageFactory,
    FeedbackFactory,
    SurveyFactory,
)
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    create_household,
)
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.services.rapid_pro.api import TokenNotProvidedError
from hope.models.payment_plan import PaymentPlan
from hope.models.program import Program
from hope.models.survey import Survey

pytestmark = pytest.mark.django_db


class TestFeedbackViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner, first_name="Test", last_name="User")
        self.client = api_client(self.user)
        self.program_active = ProgramFactory(
            name="Test Active Program",
            business_area=self.afghanistan,
            status=Program.ACTIVE,
        )
        self.hh_1 = HouseholdFactory(program=self.program_active)
        self.individual_1 = IndividualFactory(household_id=self.hh_1.id)
        self.area_1 = AreaFactory(name="AREA_name")
        self.area_2 = AreaFactory(name="Wroclaw")
        self.user_creator = UserFactory(first_name="Creator", last_name="User", partner=self.partner)

        self.feedback_1 = FeedbackFactory(
            program=self.program_active,
            household_lookup=self.hh_1,
            individual_lookup=self.individual_1,
            created_by=self.user,
            description="test description 111",
            area="test area 111",
            language="test language 111",
            comments="test comments 111",
            issue_type="NEGATIVE_FEEDBACK",
            admin2=self.area_1,
        )
        self.feedback_2 = FeedbackFactory(
            program=None,
            household_lookup=self.hh_1,
            individual_lookup=self.individual_1,
            created_by=self.user,
            issue_type="POSITIVE_FEEDBACK",
            description="test description",
            area="test area",
            language="test language",
            comments="test comments",
            admin2=self.area_1,
        )
        self.program_2 = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.feedback_3 = FeedbackFactory(
            program=self.program_2,
            issue_type="NEGATIVE_FEEDBACK",
            created_by=self.user_creator,
        )

        # per BA
        self.url_list = reverse(
            "api:accountability:feedbacks-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )
        self.url_count = reverse(
            "api:accountability:feedbacks-count",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )
        self.url_details = reverse(
            "api:accountability:feedbacks-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "pk": str(self.feedback_2.pk),
            },
        )
        self.url_details_feedback_1 = reverse(
            "api:accountability:feedbacks-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "pk": str(self.feedback_1.pk),
            },
        )
        self.url_msg_create = reverse(
            "api:accountability:feedbacks-message",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "pk": str(self.feedback_2.pk),
            },
        )
        self.url_msg_create_for_feedback_1 = reverse(
            "api:accountability:feedbacks-message",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "pk": str(self.feedback_1.pk),
            },
        )
        # per Program
        self.url_list_per_program = reverse(
            "api:accountability:feedbacks-per-program-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        self.url_count_per_program = reverse(
            "api:accountability:feedbacks-per-program-count",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        self.url_details_per_program = reverse(
            "api:accountability:feedbacks-per-program-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
                "pk": str(self.feedback_1.pk),
            },
        )
        self.url_msg_create_per_program = reverse(
            "api:accountability:feedbacks-per-program-message",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
                "pk": str(self.feedback_1.pk),
            },
        )

    # per BA
    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
                ],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_get_list(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_2)
        response = self.client.get(self.url_list)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            response_results = response.json()["results"]
            assert len(response_results) == 3
            for i, feedback in enumerate([self.feedback_1, self.feedback_2, self.feedback_3]):
                feedback_result = response_results[i]
                assert feedback_result["id"] == str(feedback.id)
                assert feedback_result["issue_type"] == feedback.issue_type
                assert feedback_result["unicef_id"] == str(feedback.unicef_id)
                assert feedback_result["household_unicef_id"] == (
                    str(feedback.household_lookup.unicef_id) if feedback.household_lookup else None
                )
                assert feedback_result["household_id"] == (
                    str(feedback.household_lookup.id) if feedback.household_lookup else None
                )
                assert feedback_result["individual_unicef_id"] == (
                    str(feedback.individual_lookup.unicef_id) if feedback.individual_lookup else None
                )
                assert feedback_result["individual_id"] == (
                    str(feedback.individual_lookup.id) if feedback.individual_lookup else None
                )
                assert feedback_result["linked_grievance_id"] == (
                    str(feedback.linked_grievance.id) if feedback.linked_grievance else None
                )
                assert feedback_result["linked_grievance_unicef_id"] == (
                    str(feedback.linked_grievance.unicef_id) if feedback.linked_grievance else None
                )
                assert feedback_result["program_name"] == (feedback.program.name if feedback.program else None)
                assert feedback_result["program_id"] == (str(feedback.program.id) if feedback.program else None)
                assert (
                    feedback_result["created_by"] == f"{feedback.created_by.first_name} {feedback.created_by.last_name}"
                )
                assert feedback_result["created_at"] == f"{feedback.created_at:%Y-%m-%dT%H:%M:%S.%fZ}"
                assert feedback_result["feedback_messages"] == []

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
                ],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_get_count(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_count)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert resp_data["count"] == 2

            # add permissions to second program
            create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_2)
            response = self.client.get(self.url_count)
            resp_data = response.json()
            assert resp_data["count"] == 3

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
                ],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_details(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_details)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["admin2"] == {
                "id": str(self.area_1.id),
                "name": "AREA_name",
            }
            assert resp_data["household_unicef_id"] is not None
            assert resp_data["household_id"] is not None
            assert resp_data["individual_unicef_id"] is not None
            assert resp_data["individual_id"] is not None
            assert resp_data["program_name"] is None
            assert resp_data["program_id"] is None
            assert resp_data["created_by"] == "Test User"
            assert resp_data["description"] == "test description"
            assert resp_data["area"] == "test area"
            assert resp_data["language"] == "test language"
            assert resp_data["comments"] == "test comments"
            assert resp_data["admin_url"] == f"/api/unicorn/accountability/feedback/{str(self.feedback_2.id)}/change/"

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_201_CREATED),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_feedback(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.post(
            self.url_list,
            {
                "area": "Area 1",
                "comments": "Test Comments",
                "consent": True,
                "description": "Test new description",
                "household_lookup": str(self.hh_1.pk),
                "issue_type": "POSITIVE_FEEDBACK",
                "admin2": str(self.area_1.pk),
                "language": "polish",
                "program_id": str(self.program_active.pk),
            },
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert response.status_code == status.HTTP_201_CREATED
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["admin2"] == {
                "id": str(self.area_1.id),
                "name": "AREA_name",
            }
            assert resp_data["issue_type"] == "POSITIVE_FEEDBACK"
            assert resp_data["household_id"] is not None
            assert resp_data["household_unicef_id"] is not None
            assert resp_data["individual_unicef_id"] is None
            assert resp_data["individual_id"] is None
            assert resp_data["program_name"] == self.hh_1.program.name
            assert resp_data["program_id"] is not None
            assert resp_data["created_by"] == "Test User"
            assert resp_data["description"] == "Test new description"
            assert resp_data["area"] == "Area 1"
            assert resp_data["language"] == "polish"
            assert resp_data["comments"] == "Test Comments"

    def test_create_feedback_without_permission_in_program(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE],
            self.afghanistan,
            self.program_2,
        )
        response = self.client.post(
            self.url_list,
            {
                "area": "Area 1",
                "comments": "Test Comments",
                "consent": True,
                "description": "Test new description",
                "household_lookup": str(self.hh_1.pk),
                "issue_type": "POSITIVE_FEEDBACK",
                "admin2": str(self.area_1.pk),
                "language": "polish",
                "program_id": str(self.program_active.pk),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE],
                status.HTTP_400_BAD_REQUEST,
            ),
        ],
    )
    def test_create_feedback_for_finished_program(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        program_finished = ProgramFactory(
            name="Test Finished Program",
            business_area=self.afghanistan,
            status=Program.FINISHED,
        )
        response = self.client.post(
            self.url_list,
            {
                "area": "Area 1",
                "comments": "Test Comments",
                "consent": True,
                "description": "Test new description",
                "household_lookup": str(self.hh_1.pk),
                "issue_type": "POSITIVE_FEEDBACK",
                "admin2": str(self.area_1.pk),
                "language": "polish",
                "program_id": str(program_finished.pk),
            },
            format="json",
        )
        assert response.status_code == expected_status
        assert "It is not possible to create Feedback for a Finished Program." in response.json()

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_201_CREATED),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_feedback_with_minimum_data(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.post(
            self.url_list,
            {
                "description": "small",
                "issue_type": "NEGATIVE_FEEDBACK",
            },
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert response.status_code == status.HTTP_201_CREATED
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["admin2"] is None
            assert resp_data["issue_type"] == "NEGATIVE_FEEDBACK"
            assert resp_data["household_id"] is None
            assert resp_data["household_unicef_id"] is None
            assert resp_data["individual_unicef_id"] is None
            assert resp_data["individual_id"] is None
            assert resp_data["program_name"] is None
            assert resp_data["program_id"] is None
            assert resp_data["created_by"] == "Test User"
            assert resp_data["description"] == "small"
            assert resp_data["area"] == ""
            assert resp_data["language"] == ""
            assert resp_data["comments"] is None
            assert resp_data["consent"] is True

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_feedback_without_program(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.patch(
            self.url_details,
            {
                "issue_type": "NEGATIVE_FEEDBACK",
                "individual_lookup": str(self.individual_1.pk),
                "description": "Test_update",
                "comments": "AAA_update",
                "admin2": str(self.area_2.pk),
                "area": "Area 1_updated",
                "language": "eng_update",
                "consent": False,
            },
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["admin2"] == {
                "id": str(self.area_2.id),
                "name": "Wroclaw",
            }
            assert resp_data["issue_type"] == "NEGATIVE_FEEDBACK"
            assert resp_data["household_id"] is not None
            assert resp_data["household_unicef_id"] is not None
            assert resp_data["individual_unicef_id"] is not None
            assert resp_data["individual_id"] is not None
            assert resp_data["program_name"] is None
            assert resp_data["program_id"] is None
            assert resp_data["created_by"] == "Test User"
            assert resp_data["description"] == "Test_update"
            assert resp_data["area"] == "Area 1_updated"
            assert resp_data["language"] == "eng_update"
            assert resp_data["comments"] == "AAA_update"
            assert resp_data["consent"] is False

    def test_update_feedback_with_program_with_permission_in_program(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE],
            self.afghanistan,
            self.program_active,
        )
        response = self.client.patch(
            self.url_details_feedback_1,
            {
                "issue_type": "NEGATIVE_FEEDBACK",
                "individual_lookup": str(self.individual_1.pk),
                "description": "Test_update",
                "comments": "AAA_update",
                "admin2": str(self.area_2.pk),
                "area": "Area 1_updated",
                "language": "eng_update",
                "consent": False,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_update_feedback_with_program_without_permission_in_program(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE],
            self.afghanistan,
            self.program_2,
        )
        response = self.client.patch(
            self.url_details_feedback_1,
            {
                "issue_type": "NEGATIVE_FEEDBACK",
                "individual_lookup": str(self.individual_1.pk),
                "description": "Test_update",
                "comments": "AAA_update",
                "admin2": str(self.area_2.pk),
                "area": "Area 1_updated",
                "language": "eng_update",
                "consent": False,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_feedback_hh_lookup(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.patch(
            self.url_details,
            {
                "issue_type": "NEGATIVE_FEEDBACK",
                "household_lookup": str(self.hh_1.pk),
                "description": "Test_update",
                "comments": "AAA_update",
                "admin2": str(self.area_2.pk),
                "area": "Area 1_updated",
                "language": "eng_update",
                "consent": False,
            },
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["admin2"] == {
                "id": str(self.area_2.id),
                "name": "Wroclaw",
            }
            assert resp_data["issue_type"] == "NEGATIVE_FEEDBACK"
            assert resp_data["household_id"] is not None
            assert resp_data["household_unicef_id"] is not None
            assert resp_data["individual_unicef_id"] is not None
            assert resp_data["individual_id"] is not None
            assert resp_data["program_name"] is None
            assert resp_data["program_id"] is None
            assert resp_data["created_by"] == "Test User"
            assert resp_data["description"] == "Test_update"
            assert resp_data["area"] == "Area 1_updated"
            assert resp_data["language"] == "eng_update"
            assert resp_data["comments"] == "AAA_update"
            assert resp_data["consent"] is False

    # per Program
    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
                ],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_per_program(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_list_per_program)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            response_results = response.json()["results"]
            assert len(response_results) == 1
            feedback_result = response_results[0]
            assert feedback_result["id"] == str(self.feedback_1.id)
            assert feedback_result["issue_type"] == self.feedback_1.issue_type
            assert feedback_result["unicef_id"] == str(self.feedback_1.unicef_id)
            assert feedback_result["household_unicef_id"] == str(self.feedback_1.household_lookup.unicef_id)
            assert feedback_result["household_id"] == str(self.feedback_1.household_lookup.id)
            assert feedback_result["individual_unicef_id"] == str(self.feedback_1.individual_lookup.unicef_id)
            assert feedback_result["individual_id"] == str(self.feedback_1.individual_lookup.id)
            assert feedback_result["linked_grievance_id"] is None
            assert feedback_result["linked_grievance_unicef_id"] is None
            assert feedback_result["program_name"] == self.feedback_1.program.name
            assert feedback_result["program_id"] == str(self.feedback_1.program.id)
            assert (
                feedback_result["created_by"]
                == f"{self.feedback_1.created_by.first_name} {self.feedback_1.created_by.last_name}"
            )
            assert feedback_result["created_at"] == f"{self.feedback_1.created_at:%Y-%m-%dT%H:%M:%S.%fZ}"
            assert feedback_result["feedback_messages"] == []

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
                ],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_get_count_per_program(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, whole_business_area_access=True)
        response = self.client.get(self.url_count_per_program)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert resp_data["count"] == 1

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
                ],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_details_per_program(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_details_per_program)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["admin2"] == {
                "id": str(self.area_1.id),
                "name": "AREA_name",
            }
            assert resp_data["household_unicef_id"] is not None
            assert resp_data["household_id"] is not None
            assert resp_data["individual_unicef_id"] is not None
            assert resp_data["individual_id"] is not None
            assert resp_data["program_name"] == "Test Active Program"
            assert resp_data["program_id"] is not None
            assert resp_data["created_by"] == "Test User"
            assert resp_data["description"] == "test description 111"
            assert resp_data["area"] == "test area 111"
            assert resp_data["language"] == "test language 111"
            assert resp_data["comments"] == "test comments 111"
            assert resp_data["admin_url"] == f"/api/unicorn/accountability/feedback/{str(self.feedback_1.id)}/change/"

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_201_CREATED),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_feedback_per_program(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.post(
            self.url_list_per_program,
            {
                "issue_type": "POSITIVE_FEEDBACK",
                "individual_lookup": str(self.individual_1.pk),
                "description": "Description per Program Create",
                "comments": "New comments per Program Create",
                "admin2": str(self.area_1.pk),
                "area": "Area new",
                "language": "polish_english",
            },
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert response.status_code == status.HTTP_201_CREATED
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["program_name"] == "Test Active Program"
            assert resp_data["description"] == "Description per Program Create"
            assert resp_data["comments"] == "New comments per Program Create"
            assert resp_data["admin2"] == {
                "id": str(self.area_1.id),
                "name": "AREA_name",
            }
            assert resp_data["area"] == "Area new"
            assert resp_data["language"] == "polish_english"
            assert resp_data["issue_type"] == "POSITIVE_FEEDBACK"
            assert resp_data["individual_unicef_id"] == str(self.individual_1.unicef_id)
            assert resp_data["individual_id"] == str(self.individual_1.id)

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_feedback_per_program(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.patch(
            self.url_details_per_program,
            {
                "issue_type": "POSITIVE_FEEDBACK",
                "individual_lookup": str(self.individual_1.pk),
                "description": "new description",
                "comments": "new comments",
                "admin2": str(self.area_1.pk),
                "area": "Area new",
                "language": "polish_english",
            },
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["admin2"] == {
                "id": str(self.area_1.id),
                "name": "AREA_name",
            }
            assert resp_data["issue_type"] == "POSITIVE_FEEDBACK"
            assert resp_data["household_id"] is not None
            assert resp_data["household_unicef_id"] is not None
            assert resp_data["individual_unicef_id"] is not None
            assert resp_data["individual_id"] is not None
            assert resp_data["program_name"] is not None
            assert resp_data["program_id"] is not None
            assert resp_data["created_by"] == "Test User"
            assert resp_data["description"] == "new description"
            assert resp_data["area"] == "Area new"
            assert resp_data["language"] == "polish_english"
            assert resp_data["comments"] == "new comments"
            assert resp_data["consent"] is True

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE],
                status.HTTP_400_BAD_REQUEST,
            ),
        ],
    )
    def test_update_feedback_per_program_when_finished(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        self.program_active.status = Program.FINISHED
        self.program_active.save()
        response = self.client.patch(
            self.url_details_per_program,
            {
                "issue_type": "POSITIVE_FEEDBACK",
                "individual_lookup": str(self.individual_1.pk),
                "description": "new description",
                "comments": "new comments",
                "admin2": str(self.area_1.pk),
                "area": "Area new",
                "language": "polish_english",
            },
            format="json",
        )
        assert response.status_code == expected_status
        assert "It is not possible to update Feedback for a Finished Program." in response.json()

    def test_list_feedback_issue_type(self) -> None:
        response_data = self.client.get(reverse("api:choices-feedback-issue-type")).data
        assert response_data is not None
        assert len(response_data) == 2
        assert "NEGATIVE_FEEDBACK" in response_data[0]["value"]
        assert "POSITIVE_FEEDBACK" in response_data[1]["value"]

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [
                    Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE,
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
                ],
                status.HTTP_201_CREATED,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_feedback_message(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.post(
            self.url_msg_create,
            {"description": "Message for Feedback #1"},
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert response.status_code == status.HTTP_201_CREATED
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["description"] == "Message for Feedback #1"
            assert "created_by" in resp_data
            assert "id" in resp_data
            assert "created_at" in resp_data

            # check message details
            response_details = self.client.get(self.url_details)
            assert response_details.status_code == status.HTTP_200_OK
            resp_data = response_details.json()
            assert "id" in resp_data
            assert len(resp_data["feedback_messages"]) == 1
            feedback_message = resp_data["feedback_messages"][0]
            assert feedback_message["description"] == "Message for Feedback #1"
            assert feedback_message["created_by"] == "Test User"
            assert "id" in feedback_message
            assert "created_at" in feedback_message

    def test_create_feedback_message_with_program_with_permission_in_program(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE],
            self.afghanistan,
            self.program_active,
        )
        response = self.client.post(
            self.url_msg_create_for_feedback_1,
            {"description": "Message for Feedback #1"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_feedback_message_with_program_without_permission_in_program(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE],
            self.afghanistan,
            self.program_2,
        )
        response = self.client.post(
            self.url_msg_create_for_feedback_1,
            {"description": "Message for Feedback #1"},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [
                    Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE,
                    Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
                ],
                status.HTTP_201_CREATED,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_feedback_message_per_program(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.post(
            self.url_msg_create_per_program,
            {"description": "New Message for Feedback Per Program"},
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert response.status_code == status.HTTP_201_CREATED
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["description"] == "New Message for Feedback Per Program"
            assert "created_by" in resp_data
            assert "id" in resp_data
            assert "created_at" in resp_data

            # check message details
            response_details = self.client.get(self.url_details_per_program)
            assert response_details.status_code == status.HTTP_200_OK
            resp_data = response_details.json()
            assert "id" in resp_data
            assert len(resp_data["feedback_messages"]) == 1
            feedback_message = resp_data["feedback_messages"][0]
            assert feedback_message["description"] == "New Message for Feedback Per Program"
            assert feedback_message["created_by"] == "Test User"
            assert "id" in feedback_message
            assert "created_at" in feedback_message

    @pytest.mark.parametrize(
        ("filter_value", "expected_count"),
        [
            ("POSITIVE_FEEDBACK", 1),
            ("NEGATIVE_FEEDBACK", 2),
        ],
    )
    def test_filter_feedback_by_issue_type(
        self,
        filter_value: str,
        expected_count: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(self.url_list, {"issue_type": filter_value})
        response_count = self.client.get(self.url_count, {"issue_type": filter_value})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == expected_count
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == expected_count

    def test_filter_by_created_at(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        self.feedback_1.created_at = timezone.make_aware(datetime.datetime(year=2020, month=3, day=12))
        self.feedback_1.save()
        self.feedback_2.created_at = timezone.make_aware(datetime.datetime(year=2023, month=1, day=31))
        self.feedback_2.save()
        self.feedback_3.created_at = timezone.make_aware(datetime.datetime(year=2023, month=2, day=1))
        self.feedback_3.save()
        response = self.client.get(
            self.url_list,
            {
                "created_at_after": "2023-01-30",
                "created_at_before": "2023-03-01",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 2
        results_ids = [feedback["id"] for feedback in results]
        assert str(self.feedback_1.id) not in results_ids
        assert str(self.feedback_2.id) in results_ids
        assert str(self.feedback_3.id) in results_ids

        # check count
        response_count = self.client.get(
            self.url_count,
            {
                "created_at_after": "2023-01-30",
                "created_at_before": "2023-03-01",
            },
        )
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 2

    def test_filter_by_created_by(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(self.url_list, {"created_by": str(self.user_creator.id)})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(self.feedback_3.id)

    def filter_by_is_active_program(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        response_true = self.client.get(self.url_list, {"is_active_program": True})
        assert response_true.status_code == status.HTTP_200_OK
        results = response_true.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(self.feedback_1.id)

        response_false = self.client.get(self.url_list, {"is_active_program": False})
        assert response_false.status_code == status.HTTP_200_OK
        results = response_false.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(self.feedback_2.id)


class TestMessageViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner, first_name="Test", last_name="User")
        self.client = api_client(self.user)
        self.program_active = ProgramFactory(
            name="Test Active Program",
            business_area=self.afghanistan,
            status=Program.ACTIVE,
        )
        self.program_finished = ProgramFactory(
            name="Test Finished Program",
            business_area=self.afghanistan,
            status=Program.FINISHED,
        )
        self.payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.TP_LOCKED,
            created_by=self.user,
            business_area=self.afghanistan,
            program_cycle=self.program_active.cycles.first(),
        )
        self.households = [
            create_household(
                household_args={"program": self.program_active},
            )[0]
            for _ in range(14)
        ]
        for hh in self.households:
            PaymentFactory(
                parent=self.payment_plan,
                program=self.program_active,
                household=hh,
            )

        self.msg_1 = CommunicationMessageFactory(
            program=self.program_active,
            business_area=self.afghanistan,
            title="MSG title",
            body="MSG body",
            created_by=self.user,
            sampling_type=Survey.SAMPLING_FULL_LIST,
            payment_plan=PaymentPlanFactory(
                status=PaymentPlan.Status.TP_LOCKED,
                created_by=self.user,
                business_area=self.afghanistan,
                program_cycle=self.program_active.cycles.first(),
            ),
        )
        self.msg_2 = CommunicationMessageFactory(
            program=self.program_active,
            business_area=self.afghanistan,
            title="MSG title 2",
            body="MSG body 2",
            created_by=self.user,
            sampling_type=Survey.SAMPLING_RANDOM,
            payment_plan=PaymentPlanFactory(
                status=PaymentPlan.Status.TP_LOCKED,
                created_by=self.user,
                business_area=self.afghanistan,
                program_cycle=self.program_active.cycles.first(),
            ),
        )
        # Message in different program
        self.msg_3 = CommunicationMessageFactory(
            program=self.program_finished,
            business_area=self.afghanistan,
            title="MSG title in different program",
            body="MSG body in different program",
            created_by=self.user,
            sampling_type=Survey.SAMPLING_RANDOM,
        )
        self.url_list = reverse(
            "api:accountability:messages-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        self.url_count = reverse(
            "api:accountability:messages-count",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        self.url_details = reverse(
            "api:accountability:messages-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
                "pk": str(self.msg_1.pk),
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_msg_get_list(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_list)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            response_results = response.json()["results"]
            assert len(response_results) == 2
            for i, message in enumerate([self.msg_1, self.msg_2]):
                message_result = response_results[i]
                assert message_result["id"] == str(message.id)
                assert message_result["unicef_id"] == str(message.unicef_id)
                assert message_result["title"] == message.title
                assert message_result["number_of_recipients"] == message.number_of_recipients
                assert message_result["created_by"] == f"{self.user.first_name} {self.user.last_name}"
                assert message_result["created_at"] == f"{message.created_at:%Y-%m-%dT%H:%M:%S.%fZ}"

    def test_msg_filter_by_program(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(self.url_list + "?" + urlencode({"program": str(self.program_active.pk)}))

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data["results"]) == 2
        results_ids = [msg["id"] for msg in resp_data["results"]]
        assert str(self.msg_1.id) in results_ids
        assert str(self.msg_2.id) in results_ids

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_msg_get_count(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_count)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert resp_data["count"] == 2

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_msg_details(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_details)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["body"] == "MSG body"
            assert resp_data["households"] is not None
            assert resp_data["payment_plan"] is not None
            assert resp_data["registration_data_import"] is None
            assert resp_data["sampling_type"] == Survey.SAMPLING_FULL_LIST
            assert resp_data["full_list_arguments"]["excluded_admin_areas"] == []
            assert resp_data["random_sampling_arguments"] is None
            assert resp_data["sample_size"] == 0
            assert resp_data["admin_url"] is not None

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
                status.HTTP_201_CREATED,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_new_message(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        broadcast_message_mock = MagicMock(return_value=None)
        with (
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
                MagicMock(return_value=None),
            ),
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
                broadcast_message_mock,
            ),
        ):
            response = self.client.post(
                self.url_list,
                {
                    "title": "New Message for Active Program",
                    "body": "Thank you for tests! Looks Good To Me!",
                    "sampling_type": Survey.SAMPLING_FULL_LIST,
                    "full_list_arguments": {"excluded_admin_areas": []},
                    "random_sampling_arguments": None,
                    "households": [str(self.households[0].pk)],
                },
                format="json",
            )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert response.status_code == status.HTTP_201_CREATED
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["title"] == "New Message for Active Program"
            assert resp_data["body"] == "Thank you for tests! Looks Good To Me!"
            assert resp_data["sample_size"] == 1

    def test_create_new_message_by_households_full_list(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
            self.afghanistan,
            self.program_active,
        )
        broadcast_message_mock = MagicMock(return_value=None)
        with (
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
                MagicMock(return_value=None),
            ),
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
                broadcast_message_mock,
            ),
        ):
            response = self.client.post(
                self.url_list,
                {
                    "title": "New Message 1 for Active Program",
                    "body": "Thank you for tests! Looks Good To Me!",
                    "sampling_type": Survey.SAMPLING_FULL_LIST,
                    "full_list_arguments": {"excluded_admin_areas": []},
                    "households": [str(hh.id) for hh in self.households],
                },
                format="json",
            )
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert resp_data["sample_size"] == len(self.households)

    def test_create_new_message_by_households_random(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
            self.afghanistan,
            self.program_active,
        )
        broadcast_message_mock = MagicMock(return_value=None)
        with (
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
                MagicMock(return_value=None),
            ),
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
                broadcast_message_mock,
            ),
        ):
            response = self.client.post(
                self.url_list,
                {
                    "title": "New Message 2 for Active Program",
                    "body": "Thank you for tests! Looks Good To Me!",
                    "sampling_type": Survey.SAMPLING_RANDOM,
                    "random_sampling_arguments": {
                        "age": {"max": 80, "min": 30},
                        "sex": "MALE",
                        "margin_of_error": 20.0,
                        "confidence_interval": 0.9,
                        "excluded_admin_areas": [],
                    },
                    "households": [str(hh.id) for hh in self.households],
                },
                format="json",
            )
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert resp_data["sample_size"] == 1

    def test_create_new_message_by_target_population_full_list(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
            self.afghanistan,
            self.program_active,
        )
        broadcast_message_mock = MagicMock(return_value=None)
        with (
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
                MagicMock(return_value=None),
            ),
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
                broadcast_message_mock,
            ),
        ):
            response = self.client.post(
                self.url_list,
                {
                    "title": "New Message 1 for Active Program",
                    "body": "Thank you for tests! Looks Good To Me!",
                    "sampling_type": Survey.SAMPLING_FULL_LIST,
                    "full_list_arguments": {"excluded_admin_areas": []},
                    "payment_plan": str(self.payment_plan.id),
                },
                format="json",
            )
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert resp_data["sample_size"] == len(self.households)

    def test_create_new_message_target_population_random(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
            self.afghanistan,
            self.program_active,
        )
        broadcast_message_mock = MagicMock(return_value=None)
        with (
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
                MagicMock(return_value=None),
            ),
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
                broadcast_message_mock,
            ),
        ):
            response = self.client.post(
                self.url_list,
                {
                    "title": "New Message 2 for Active Program",
                    "body": "Thank you for tests! Looks Good To Me!",
                    "sampling_type": Survey.SAMPLING_RANDOM,
                    "random_sampling_arguments": {
                        "age": {"max": 80, "min": 30},
                        "sex": "MALE",
                        "margin_of_error": 20.0,
                        "confidence_interval": 0.9,
                        "excluded_admin_areas": [],
                    },
                    "payment_plan": str(self.payment_plan.id),
                },
                format="json",
            )
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert resp_data["sample_size"] == 1

    def test_create_message_validation_error(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
            self.afghanistan,
            self.program_active,
        )
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.TP_LOCKED,
            created_by=self.user,
            business_area=self.afghanistan,
            program_cycle=self.program_active.cycles.first(),
        )
        rdi = RegistrationDataImportFactory(imported_by=self.user, business_area=self.afghanistan)

        response = self.client.post(
            self.url_list,
            {
                "title": "Test Error",
                "body": "Thank you for tests!",
                "sampling_type": Survey.SAMPLING_FULL_LIST,
                "full_list_arguments": {"excluded_admin_areas": []},
                "payment_plan": str(payment_plan.pk),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No recipients found for the given criteria" in response.json()

        response_2 = self.client.post(
            self.url_list,
            {
                "title": "Test Error",
                "body": "Thank you for tests!",
                "sampling_type": Survey.SAMPLING_FULL_LIST,
                "full_list_arguments": {"excluded_admin_areas": []},
                "random_sampling_arguments": None,
                "registration_data_import": str(rdi.pk),
            },
            format="json",
        )
        assert response_2.status_code == status.HTTP_400_BAD_REQUEST
        assert "No recipients found for the given criteria" in response_2.json()

    def test_create_message_invalid_request(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
            self.afghanistan,
            self.program_active,
        )

        response = self.client.post(
            self.url_list,
            {
                "title": "Test Error",
                "body": "Thank you for tests!",
                "sampling_type": Survey.SAMPLING_RANDOM,
                "full_list_arguments": {"excluded_admin_areas": []},
                "random_sampling_arguments": {
                    "age": {"max": 80, "min": 30},
                    "sex": "MALE",
                    "margin_of_error": 20.0,
                    "confidence_interval": 0.9,
                    "excluded_admin_areas": [],
                },
                "households": [str(self.households[0].pk)],
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert f"Must not provide full_list_arguments for {Survey.SAMPLING_RANDOM}" in response.json()

    def test_sample_size(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
            self.afghanistan,
            self.program_active,
        )
        url = reverse(
            "api:accountability:messages-sample-size",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        data = {
            "payment_plan": str(self.payment_plan.pk),
            "sampling_type": Survey.SAMPLING_RANDOM,
            "random_sampling_arguments": {
                "age": {"max": 80, "min": 30},
                "sex": "MALE",
                "margin_of_error": 20.0,
                "confidence_interval": 0.9,
                "excluded_admin_areas": [],
            },
        }

        response = self.client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {"number_of_recipients": 14, "sample_size": 1}

    def test_filter_messages_by_created_at(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        self.msg_1.created_at = timezone.make_aware(datetime.datetime(year=2021, month=3, day=12))
        self.msg_1.save()
        self.msg_2.created_at = timezone.make_aware(datetime.datetime(year=2020, month=5, day=15))
        self.msg_2.save()
        response = self.client.get(
            self.url_list,
            {
                "created_at_after": "2020-01-01",
                "created_at_before": "2020-12-31",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(self.msg_2.id)

    def test_filter_messages_by_title(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(self.url_list, {"title": "MSG title"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 2
        results_ids = [msg["id"] for msg in results]
        assert str(self.msg_1.id) in results_ids
        assert str(self.msg_2.id) in results_ids

        response = self.client.get(self.url_list, {"title": "2"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 1
        results_ids = [msg["id"] for msg in results]
        assert str(self.msg_2.id) in results_ids

    def test_filter_messages_by_body(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(self.url_list, {"body": "MSG body"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 2
        results_ids = [msg["id"] for msg in results]
        assert str(self.msg_1.id) in results_ids
        assert str(self.msg_2.id) in results_ids

        response = self.client.get(self.url_list, {"body": "2"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 1
        results_ids = [msg["id"] for msg in results]
        assert str(self.msg_2.id) in results_ids

    def test_filter_messages_by_sampling_type(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(self.url_list, {"sampling_type": Survey.SAMPLING_FULL_LIST})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(self.msg_1.id)

        response = self.client.get(self.url_list, {"sampling_type": Survey.SAMPLING_RANDOM})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(self.msg_2.id)


class TestSurveyViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner, first_name="Test", last_name="User")
        self.client = api_client(self.user)
        self.program_active = ProgramFactory(
            name="Test Active Program",
            business_area=self.afghanistan,
            status=Program.ACTIVE,
        )
        hoh1 = IndividualFactory(household=None)
        self.hh_1 = HouseholdFactory(program=self.program_active, head_of_household=hoh1)
        self.payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.TP_LOCKED,
            created_by=self.user,
            business_area=self.afghanistan,
            program_cycle=self.program_active.cycles.first(),
        )
        self.payment = PaymentFactory(parent=self.payment_plan, program=self.program_active, household=self.hh_1)
        self.user_creator = UserFactory(partner=self.partner, first_name="Creator", last_name="User")
        self.srv = SurveyFactory(
            unicef_id="SUR-24-0012",
            program=self.program_active,
            business_area=self.afghanistan,
            created_by=self.user,
            title="Survey 1",
            body="Survey 1 body",
            flow_id="id123",
            sample_file=None,
            sample_file_generated_at=None,
            sampling_type=Survey.SAMPLING_FULL_LIST,
            category=Survey.CATEGORY_SMS,
            payment_plan=self.payment_plan,
        )
        self.srv_2 = SurveyFactory(
            program=self.program_active,
            business_area=self.afghanistan,
            created_by=self.user_creator,
            title="Survey 2",
            body="Survey 2 body",
            flow_id="id456",
            sample_file=None,
            sample_file_generated_at=None,
            sampling_type=Survey.SAMPLING_RANDOM,
            category=Survey.CATEGORY_MANUAL,
            payment_plan=self.payment_plan,
        )
        self.url_list = reverse(
            "api:accountability:surveys-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        self.url_count = reverse(
            "api:accountability:surveys-count",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        self.url_details = reverse(
            "api:accountability:surveys-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
                "pk": str(self.srv.pk),
            },
        )
        self.url_export_sample = reverse(
            "api:accountability:surveys-export-sample",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
                "pk": str(self.srv.pk),
            },
        )
        self.url_flows = reverse(
            "api:accountability:surveys-available-flows",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        self.url_category_choices = reverse(
            "api:accountability:surveys-category-choices",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_survey_list(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_list)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            response_results = response.json()["results"]
            assert len(response_results) == 2
            for i, survey in enumerate([self.srv, self.srv_2]):
                survey_result = response_results[i]
                assert survey_result["id"] == str(survey.id)
                assert survey_result["unicef_id"] == str(survey.unicef_id)
                assert survey_result["title"] == survey.title
                assert survey_result["body"] == survey.body
                assert survey_result["category"] == survey.get_category_display()
                assert survey_result["flow_id"] == survey.flow_id
                assert survey_result["rapid_pro_url"] == f"https://rapidpro.io/flow/results/{survey.flow_id}/"
                assert survey_result["created_by"] == f"{survey.created_by.first_name} {survey.created_by.last_name}"
                assert survey_result["has_valid_sample_file"] is None
                assert survey_result["sample_file_path"] is None
                assert survey_result["created_at"] == f"{survey.created_at:%Y-%m-%dT%H:%M:%S.%fZ}"
                assert survey_result["number_of_recipients"] == survey.number_of_recipients

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_survey_get_count(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_count)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert resp_data["count"] == 2

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [
                    Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
                    Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST,
                ],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_survey_details(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_details)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["title"] == "Survey 1"
            assert resp_data["body"] == "Survey 1 body"
            assert resp_data["category"] == "Survey with SMS"

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE], status.HTTP_201_CREATED),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_survey(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.post(
            self.url_list,
            {
                "title": "New SRV",
                "body": "LGTM",
                "category": "MANUAL",
                "sampling_type": Survey.SAMPLING_FULL_LIST,
                "full_list_arguments": {"excluded_admin_areas": []},
            },
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert response.status_code == status.HTTP_201_CREATED
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["title"] == "New SRV"
            assert resp_data["body"] == "LGTM"

            # create new one with PaymentPlan (TP)
            response = self.client.post(
                self.url_list,
                {
                    "title": "New SRV with TP",
                    "body": "LGTM",
                    "category": "MANUAL",
                    "sampling_type": Survey.SAMPLING_FULL_LIST,
                    "full_list_arguments": {"excluded_admin_areas": []},
                    "random_sampling_arguments": None,
                    "payment_plan": str(self.payment_plan.pk),
                },
                format="json",
            )
            assert response.status_code == status.HTTP_201_CREATED
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["title"] == "New SRV with TP"
            assert Survey.objects.get(title="New SRV with TP").payment_plan_id == self.payment_plan.pk

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
                status.HTTP_202_ACCEPTED,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_survey_export_sample(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_export_sample)
        assert response.status_code == expected_status
        if expected_status == status.HTTP_202_ACCEPTED:
            assert response.status_code == status.HTTP_202_ACCEPTED
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["title"] == "Survey 1"

    def test_get_category_choices(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
            self.afghanistan,
            self.program_active,
        )
        response = self.client.get(self.url_category_choices)
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data) == 3
        assert resp_data[0]["name"] == "Survey with RapidPro"
        assert resp_data[0]["value"] == "RAPID_PRO"
        assert resp_data[1]["name"] == "Survey with SMS"
        assert resp_data[1]["value"] == "SMS"
        assert resp_data[2]["name"] == "Survey with manual process"
        assert resp_data[2]["value"] == "MANUAL"

    def test_get_available_flows(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
            self.afghanistan,
            self.program_active,
        )
        with (
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
                MagicMock(return_value=None),
            ),
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.get_flows",
                MagicMock(
                    return_value=[
                        {"uuid": 123, "name": "flow2"},
                        {"uuid": 234, "name": "flow2"},
                    ]
                ),
            ),
        ):
            response = self.client.get(self.url_flows)
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data) == 2

    def test_sample_size(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE],
            self.afghanistan,
            self.program_active,
        )
        url = reverse(
            "api:accountability:surveys-sample-size",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        data = {
            "payment_plan": str(self.payment_plan.pk),
            "sampling_type": Survey.SAMPLING_RANDOM,
            "random_sampling_arguments": {
                "age": {"max": 80, "min": 30},
                "sex": "MALE",
                "margin_of_error": 20.0,
                "confidence_interval": 0.9,
                "excluded_admin_areas": [],
            },
        }

        response = self.client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {"number_of_recipients": 1, "sample_size": 0}

        data = {
            "sampling_type": Survey.SAMPLING_FULL_LIST,
            "full_list_arguments": {"excluded_admin_areas": []},
        }

        response = self.client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {"number_of_recipients": 1, "sample_size": 1}

    def test_filter_surveys_by_created_at(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        self.srv.created_at = timezone.make_aware(datetime.datetime(year=2021, month=3, day=12))
        self.srv.save()
        self.srv_2.created_at = timezone.make_aware(datetime.datetime(year=2020, month=5, day=15))
        self.srv_2.save()
        response = self.client.get(
            self.url_list,
            {
                "created_at_after": "2020-01-01",
                "created_at_before": "2020-12-31",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(self.srv_2.id)

    def test_filter_surveys_by_created_by(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(self.url_list, {"created_by": f"{self.user_creator.id}"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(self.srv_2.id)

    def test_search_surveys(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST],
            self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(self.url_list, {"search": "Survey 1"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(self.srv.id)

        response = self.client.get(self.url_list, {"search": "0012"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(self.srv.id)

        response = self.client.get(self.url_list, {"search": "SUR-"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 2
        results_ids = [survey["id"] for survey in results]
        assert str(self.srv.id) in results_ids
        assert str(self.srv_2.id) in results_ids

    def test_get_available_flows_no_token(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
            self.afghanistan,
            self.program_active,
        )
        with (
            patch(
                "hope.apps.accountability.api.views.RapidProAPI.__init__",
                MagicMock(side_effect=TokenNotProvidedError),
            ),
        ):
            response = self.client.get(self.url_flows)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == ["Token is not provided."]
