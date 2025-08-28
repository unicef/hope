from typing import Any, List
from urllib.parse import urlencode

from django.urls import reverse
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.program import ProgramFactory
import pytest
from rest_framework import status

from hope.apps.account.permissions import Permissions
from hope.apps.activity_log.models import LogEntry
from hope.apps.activity_log.utils import create_diff
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db


class TestLogEntryView:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner, first_name="Test", last_name="User")
        self.client = api_client(self.user)
        self.partner_2 = PartnerFactory(name="Test_2")
        self.user_without_perms = UserFactory(partner=self.partner_2)

        self.program_1 = ProgramFactory(
            name="Program 1",
            business_area=self.afghanistan,
            pk="ad17c53d-11b0-4e9b-8407-2e034f03fd31",
        )
        self.program_2 = ProgramFactory(
            name="Program 2",
            business_area=self.afghanistan,
            pk="c74612a1-212c-4148-be5b-4b41d20e623c",
        )
        self.grv = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            business_area=self.afghanistan,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )

        self.l1 = LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=self.program_1,
            user=self.user,
            business_area=self.afghanistan,
            object_repr=str(self.program_1),
            changes=create_diff(None, self.program_1, Program.ACTIVITY_LOG_MAPPING),
        )
        self.l1.programs.add(self.program_1)
        self.l2 = LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=self.program_2,
            user=self.user,
            business_area=self.afghanistan,
            object_repr=str(self.program_2),
            changes=create_diff(None, self.program_2, Program.ACTIVITY_LOG_MAPPING),
        )
        self.l2.programs.add(self.program_2)
        self.l3 = LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=self.program_1,
            user=self.user_without_perms,
            business_area=self.afghanistan,
            object_repr=str(self.program_1),
            changes=create_diff(None, self.program_1, Program.ACTIVITY_LOG_MAPPING),
        )
        self.l3.programs.add(self.program_1)
        self.l4 = LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=self.grv,
            user=None,
            business_area=self.afghanistan,
            object_repr=str(self.grv),
            changes=create_diff(None, self.grv, GrievanceTicket.ACTIVITY_LOG_MAPPING),
        )
        self.l4.programs.add(self.program_2)
        self.l5 = LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=self.program_2,
            user=self.user_without_perms,
            business_area=None,
            object_repr=str(self.program_2),
            changes=create_diff(None, self.program_2, Program.ACTIVITY_LOG_MAPPING),
        )
        self.l5.programs.add(self.program_2)

        # per BA
        self.url_list = reverse(
            "api:activity-logs:activity-logs-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )
        self.url_count = reverse(
            "api:activity-logs:activity-logs-count",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )
        self.url_choices = reverse(
            "api:activity-logs:activity-logs-log-entry-action-choices",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
            },
        )
        # per Program
        self.url_list_per_program = reverse(
            "api:activity-logs:activity-logs-per-program-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_1.slug,
            },
        )
        self.url_count_per_program = reverse(
            "api:activity-logs:activity-logs-per-program-count",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_1.slug,
            },
        )
        self.url_choices_per_program = reverse(
            "api:activity-logs:activity-logs-per-program-log-entry-action-choices",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_1.slug,
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACTIVITY_LOG_VIEW],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_activity_logs_list(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_1)
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_2)
        response = self.client.get(self.url_list)
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            response_results = response.json()["results"]
            assert len(response_results) == 4
            for i, log in enumerate([self.l4, self.l3, self.l2, self.l1]):
                log_result = response_results[i]
                assert log_result["object_id"] == str(log.object_id)
                assert log_result["action"] == log.get_action_display()
                assert log_result["changes"] == log.changes
                assert log_result["user"] == (f"{log.user.first_name} {log.user.last_name}" if log.user else "-")
                assert log_result["object_repr"] == log.object_repr
                assert log_result["content_type"] == log.content_type.name
                assert log_result["timestamp"] == f"{log.timestamp:%Y-%m-%dT%H:%M:%S.%fZ}"

                if isinstance(log.content_object, GrievanceTicket):
                    expected_is_user_generated = log.content_object.grievance_type_to_string() == "user"
                else:
                    expected_is_user_generated = None
                assert log_result["is_user_generated"] == expected_is_user_generated

            assert response_results[0]["program_slug"] is None
            assert response_results[1]["program_slug"] == self.program_1.slug
            assert response_results[2]["program_slug"] == self.program_2.slug
            assert response_results[3]["program_slug"] == self.program_1.slug

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACTIVITY_LOG_VIEW],
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
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_1)
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_2)
        response = self.client.get(self.url_count)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert resp_data["count"] == 4

    # per Program
    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACTIVITY_LOG_VIEW],
                status.HTTP_200_OK,
            ),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_activity_logs_list_per_program(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_1)
        response = self.client.get(self.url_list_per_program)
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            response_results = response.json()["results"]
            assert len(response_results) == 2
            for i, log in enumerate([self.l3, self.l1]):
                log_result = response_results[i]
                assert log_result["object_id"] == str(log.object_id)
                assert log_result["action"] == log.get_action_display()
                assert log_result["changes"] == log.changes
                assert log_result["user"] == (f"{log.user.first_name} {log.user.last_name}" if log.user else "-")
                assert log_result["object_repr"] == log.object_repr
                assert log_result["content_type"] == log.content_type.name
                assert log_result["timestamp"] == f"{log.timestamp:%Y-%m-%dT%H:%M:%S.%fZ}"

                if isinstance(log.content_object, GrievanceTicket):
                    expected_is_user_generated = log.content_object.grievance_type_to_string() == "user"
                else:
                    expected_is_user_generated = None
                assert log_result["is_user_generated"] == expected_is_user_generated

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.ACTIVITY_LOG_VIEW],
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
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_1)
        response = self.client.get(self.url_count_per_program)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert resp_data["count"] == 2

    def test_activity_logs_filters(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.ACTIVITY_LOG_VIEW], self.afghanistan, self.program_2)
        create_user_role_with_permissions(self.user, [Permissions.ACTIVITY_LOG_VIEW], self.afghanistan, self.program_1)
        response = self.client.get(
            reverse(
                "api:activity-logs:activity-logs-list",
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
            + "?"
            + urlencode({"object_id": "c74612a1-212c-4148-be5b-4b41d20e623c"})
        )
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data["results"]) == 1
        log = resp_data["results"][0]
        assert "object_id" in log
        assert log["object_id"] == "c74612a1-212c-4148-be5b-4b41d20e623c"
        assert log["object_repr"] == "Program 2"
        # user_id
        response = self.client.get(
            reverse(
                "api:activity-logs:activity-logs-list",
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
            + "?"
            + urlencode({"user_id": str(self.user_without_perms.pk)})
        )
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data["results"]) == 1
        log = resp_data["results"][0]
        assert "object_id" in log
        assert log["object_id"] == "ad17c53d-11b0-4e9b-8407-2e034f03fd31"
        assert log["object_repr"] == "Program 1"
        assert log["user"] == f"{self.user_without_perms.first_name} {self.user_without_perms.last_name}"
        # module
        response = self.client.get(
            reverse(
                "api:activity-logs:activity-logs-list",
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
            + "?"
            + urlencode({"module": "grievanceticket"})
        )
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data["results"]) == 1
        log = resp_data["results"][0]
        assert "object_id" in log
        assert log["object_id"] == str(self.grv.pk)
        assert log["object_repr"] == self.grv.__str__()
        assert log["is_user_generated"] is True
        # program
        response = self.client.get(
            reverse(
                "api:activity-logs:activity-logs-list",
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
            + "?"
            + urlencode({"program_id": str(self.program_2.pk)})
        )
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data["results"]) == 2
        log = resp_data["results"][0]
        assert "object_id" in log
        assert log["object_id"] == str(self.grv.pk)
        assert log["object_repr"] == self.grv.__str__()
        assert log["is_user_generated"] is True

    def test_activity_logs_choices(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.ACTIVITY_LOG_VIEW], self.afghanistan, self.program_1)
        response = self.client.get(self.url_choices)
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert len(resp_data) == 4
        choice = resp_data[0]
        assert "name" in choice
        assert "value" in choice
