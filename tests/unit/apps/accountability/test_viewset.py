from typing import Any, List
from unittest.mock import MagicMock, patch
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.urls import reverse

import pytest
from rest_framework import status

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.fixtures import (
    CommunicationMessageFactory,
    FeedbackFactory,
)
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory

pytestmark = pytest.mark.django_db


class TestFeedbackViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner, first_name="Test", last_name="User")
        self.client = api_client(self.user)
        self.program_active = ProgramFactory(
            name="Test Active Program", business_area=self.afghanistan, status=Program.ACTIVE
        )
        self.hh_1 = HouseholdFactory(program=self.program_active)
        self.individual_1 = IndividualFactory(household_id=self.hh_1.id)
        self.area_1 = AreaFactory(name="AREA_name")
        self.area_2 = AreaFactory(name="Wroclaw")

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
        self.feedback_3 = FeedbackFactory(program=ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE))

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
        self.url_msg_create = reverse(
            "api:accountability:feedbacks-message",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "pk": str(self.feedback_2.pk),
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
        "permissions, expected_status",
        [
            (
                [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_get_list(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_list)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert len(resp_data["results"]) == 3
            feedback = resp_data["results"][0]
            assert "id" in feedback
            assert "issue_type" in feedback
            assert "unicef_id" in feedback
            assert "household_unicef_id" in feedback
            assert "household_id" in feedback
            assert "individual_unicef_id" in feedback
            assert "individual_id" in feedback
            assert "linked_grievance_id" in feedback
            assert "linked_grievance_unicef_id" in feedback
            assert "program_name" in feedback
            assert "program_id" in feedback
            assert "created_by" in feedback
            assert "created_at" in feedback
            assert "feedback_messages" in feedback

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            (
                [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_get_count(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_count)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert resp_data["count"] == 3

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            (
                [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_details(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_details)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["admin2_name"] == "AREA_name"
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

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_201_CREATED),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_feedback(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
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
            assert resp_data["admin2_name"] == "AREA_name"
            assert resp_data["issue_type"] == "Positive feedback"
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

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_400_BAD_REQUEST),
        ],
    )
    def test_create_feedback_for_finished_program(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        program_finished = ProgramFactory(
            name="Test Finished Program", business_area=self.afghanistan, status=Program.FINISHED
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
        assert "In order to proceed this action, program status must not be finished" in response.json()

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_201_CREATED),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_feedback_with_minimum_data(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
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
            assert resp_data["admin2_name"] is None
            assert resp_data["issue_type"] == "Negative feedback"
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
        "permissions, expected_status",
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_feedback(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
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
            assert resp_data["admin2_name"] == "Wroclaw"
            assert resp_data["issue_type"] == "Negative feedback"
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

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_feedback_hh_lookup(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
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
            assert resp_data["admin2_name"] == "Wroclaw"
            assert resp_data["issue_type"] == "Negative feedback"
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
        "permissions, expected_status",
        [
            (
                [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_per_program(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_list_per_program)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert len(resp_data["results"]) == 1
            feedback = resp_data["results"][0]
            assert "id" in feedback
            assert "issue_type" in feedback
            assert "unicef_id" in feedback
            assert "household_unicef_id" in feedback
            assert "household_id" in feedback
            assert "individual_unicef_id" in feedback
            assert "individual_id" in feedback
            assert "linked_grievance_id" in feedback
            assert "linked_grievance_unicef_id" in feedback
            assert "program_name" in feedback
            assert "program_id" in feedback
            assert "created_by" in feedback
            assert "created_at" in feedback
            assert "feedback_messages" in feedback

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            (
                [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_get_count_per_program(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_count_per_program)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert resp_data["count"] == 1

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            (
                [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_feedback_details_per_program(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_details_per_program)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["admin2_name"] == "AREA_name"
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

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_201_CREATED),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_feedback_per_program(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
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

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_feedback_per_program(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
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
            assert resp_data["admin2_name"] == "AREA_name"
            assert resp_data["issue_type"] == "Positive feedback"
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
        "permissions, expected_status",
        [
            ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_400_BAD_REQUEST),
        ],
    )
    def test_update_feedback_per_program_when_finished(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
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
        assert "In order to proceed this action, program status must not be finished" in response.json()

    def test_list_feedback_issue_type(self) -> None:
        response_data = self.client.get(reverse("api:choices-feedback-issue-type")).data
        assert response_data is not None
        assert len(response_data) == 2
        assert "NEGATIVE_FEEDBACK" in response_data[0]["value"]
        assert "POSITIVE_FEEDBACK" in response_data[1]["value"]

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            (
                [Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
                status.HTTP_201_CREATED,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_feedback_message(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
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

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            (
                [Permissions.GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
                status.HTTP_201_CREATED,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_feedback_message_per_program(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
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


class TestMessageViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner, first_name="Test", last_name="User")
        self.client = api_client(self.user)
        self.program_active = ProgramFactory(
            name="Test Active Program", business_area=self.afghanistan, status=Program.ACTIVE
        )
        self.hh_1 = HouseholdFactory(program=self.program_active)
        self.msg_1 = CommunicationMessageFactory(
            program=self.program_active,
            business_area=self.afghanistan,
            title="MSG title",
            body="MSG body",
            created_by=self.user,
            sampling_type="FULL_LIST",
            payment_plan=PaymentPlanFactory(
                status=PaymentPlan.Status.TP_LOCKED,
                created_by=self.user,
                business_area=self.afghanistan,
                program_cycle=self.program_active.cycles.first(),
            ),
        )
        # Message without Program
        CommunicationMessageFactory(
            program=None,
            business_area=self.afghanistan,
            title="MSG title without Program",
            body="MSG body without Program",
            created_by=self.user,
            sampling_type="RANDOM",
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
        "permissions, expected_status",
        [
            (
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_msg_get_list(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_list)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert len(resp_data["results"]) == 1
            msg = resp_data["results"][0]
            assert "id" in msg
            assert "unicef_id" in msg
            assert msg["title"] == "MSG title"
            assert "number_of_recipients" in msg
            assert "created_by" in msg
            assert "created_at" in msg

    def test_msg_filter_by_program(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
            self.afghanistan,
            self.program_active,
        )
        response = self.client.get(self.url_list + "?" + urlencode({"program": str(self.program_active.pk)}))

        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data["results"]) == 1
        msg = resp_data["results"][0]
        assert "id" in msg
        assert "unicef_id" in msg
        assert msg["title"] == "MSG title"

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            (
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_msg_get_count(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_count)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert resp_data["count"] == 1

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            (
                [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_msg_details(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_details)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["body"] == "MSG body"
            assert resp_data["households"] is not None
            assert resp_data["payment_plan"] is None
            assert resp_data["registration_data_import"] is None
            assert resp_data["sampling_type"] == "FULL_LIST"
            assert resp_data["full_list_arguments"]["excluded_admin_areas"] == []
            assert resp_data["random_sampling_arguments"] is None
            assert resp_data["sample_size"] == 0
            assert resp_data["admin_url"] is not None

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE], status.HTTP_201_CREATED),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_new_message(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        broadcast_message_mock = MagicMock(return_value=None)
        with (
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)),
            patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message", broadcast_message_mock),
        ):
            response = self.client.post(
                self.url_list,
                {
                    "title": "New Message for Active Program",
                    "body": "Thank you for tests! Looks Good To Me!",
                    "sampling_type": "FULL_LIST",
                    "full_list_arguments": {"excluded_admin_areas": []},
                    "random_sampling_arguments": None,
                    "households": [str(self.hh_1.pk)],
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

        with pytest.raises(ValidationError) as e:
            self.client.post(
                self.url_list,
                {
                    "title": "Test Error",
                    "body": "Thank you for tests!",
                    "sampling_type": "FULL_LIST",
                    "full_list_arguments": {"excluded_admin_areas": []},
                    "random_sampling_arguments": None,
                    "payment_plan": str(payment_plan.pk),
                },
                format="json",
            )
        assert "No recipients found for the given criteria" in str(e.value)

        with pytest.raises(ValidationError) as e:
            self.client.post(
                self.url_list,
                {
                    "title": "Test Error",
                    "body": "Thank you for tests!",
                    "sampling_type": "FULL_LIST",
                    "full_list_arguments": {"excluded_admin_areas": []},
                    "random_sampling_arguments": None,
                    "registration_data_import": str(rdi.pk),
                },
                format="json",
            )
        assert "No recipients found for the given criteria" in str(e.value)
