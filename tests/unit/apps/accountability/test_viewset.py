from typing import Any, List

from django.urls import reverse

import pytest
from rest_framework import status

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.fixtures import FeedbackFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db


class TestFeedbackViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.program_active = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.hh_1 = HouseholdFactory(program=self.program_active)
        self.individual_1 = IndividualFactory(household_id=self.hh_1.id)
        self.area_1 = AreaFactory(name="AREA_name")

        self.feedback_1 = FeedbackFactory(
            program=self.program_active, household_lookup=self.hh_1, individual_lookup=self.individual_1
        )
        self.feedback_2 = FeedbackFactory(program=None)
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
            # print("resp_data === ", resp_data)
            assert "id" in resp_data
            assert resp_data["admin2_name"] == "AREA_name"
            # TODO: add more

    # @pytest.mark.parametrize(
    #     "permissions, expected_status",
    #     [
    #         ([Permissions.GRIEVANCES_FEEDBACK_VIEW_CREATE], status.HTTP_201_CREATED),
    #         ([], status.HTTP_403_FORBIDDEN),
    #     ],
    # )
    # def test_create_feedback(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
    #     create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
    #     PaymentFactory(parent=self.pp, status=Payment.STATUS_SUCCESS, delivered_quantity=111, entitlement_quantity=112)
    #     response = self.client.post(
    #         self.url_create,
    #         {
    #             "sampling": "FULL_LIST"},
    #         format="json",
    #     )
    #     assert response.status_code == expected_status
    #     if expected_status == status.HTTP_201_CREATED:
    #         assert response.status_code == status.HTTP_201_CREATED
    #         resp_data = response.json()
    #         assert "id" in resp_data
    #
    # @pytest.mark.parametrize(
    #     "permissions, expected_status",
    #     [
    #         ([Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE], status.HTTP_200_OK),
    #         ([], status.HTTP_403_FORBIDDEN),
    #     ],
    # )
    # def test_update_feedback(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
    #     create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
    #     response = self.client.patch(
    #         self.url_update,
    #         {
    #             "sampling": "FULL_LIST"},
    #         format="json",
    #     )
    #     assert response.status_code == expected_status
    #     if expected_status == status.HTTP_200_OK:
    #         assert response.status_code == status.HTTP_200_OK
    #         resp_data = response.json()
    #         assert "id" in resp_data

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
