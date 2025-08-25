from datetime import datetime
from typing import Any, List

import pytest
import pytz
from django.core.management import call_command
from django.urls import reverse
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status

from hope.apps.account.permissions import Permissions
from models.core import BusinessArea
from models.geo import Country
from hope.apps.grievance.models import GrievanceTicket

pytestmark = pytest.mark.django_db


class TestGrievanceDashboardAPI:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        call_command("loadcountries")
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner, first_name="Test", last_name="User")
        self.client = api_client(self.user)
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        country = Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            area_level=2,
            country=country,
        )
        self.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="123aa123")

        created_at_dates_to_set = {
            GrievanceTicket.STATUS_NEW: datetime(year=2020, month=3, day=12, tzinfo=pytz.UTC),
            GrievanceTicket.STATUS_ON_HOLD: datetime(year=2020, month=7, day=12, tzinfo=pytz.UTC),
            GrievanceTicket.STATUS_IN_PROGRESS: datetime(year=2020, month=8, day=22, tzinfo=pytz.UTC),
        }

        grievances_to_create = (
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                status=GrievanceTicket.STATUS_NEW,
            ),
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                status=GrievanceTicket.STATUS_ON_HOLD,
            ),
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                status=GrievanceTicket.STATUS_IN_PROGRESS,
            ),
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                status=GrievanceTicket.STATUS_CLOSED,
            ),
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                status=GrievanceTicket.STATUS_CLOSED,
            ),
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                status=GrievanceTicket.STATUS_CLOSED,
            ),
        )

        for grievance_ticket in grievances_to_create:
            grievance_ticket.created_by = self.user
            grievance_ticket.assigned_to = self.user
            grievance_ticket.business_area = self.business_area
            grievance_ticket.admin2 = self.admin_area_1
            grievance_ticket.consent = True
            grievance_ticket.language = "Polish, English"
            grievance_ticket.description = "Just random description"

        GrievanceTicket.objects.bulk_create(grievances_to_create)

        for status_value, date in created_at_dates_to_set.items():
            gt = GrievanceTicket.objects.get(status=status_value)
            gt.created_at = date
            gt.updated_at = datetime.now()
            gt.save()

        self.url = reverse(
            "api:grievance:grievance-tickets-global-dashboard",
            kwargs={"business_area_slug": self.business_area.slug},
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
                status.HTTP_200_OK,
            ),
            (
                [],
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_dashboard_api_endpoint(
        self,
        permissions: List[Permissions],
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.business_area, whole_business_area_access=True)

        response = self.client.get(self.url)
        assert response.status_code == expected_status

        if expected_status == status.HTTP_200_OK:
            data = response.json()

            # Check main structure
            assert "tickets_by_type" in data
            assert "tickets_by_status" in data
            assert "tickets_by_category" in data
            assert "tickets_by_location_and_category" in data

            # Check tickets_by_type structure
            tickets_by_type = data["tickets_by_type"]
            assert "user_generated_count" in tickets_by_type
            assert "system_generated_count" in tickets_by_type
            assert "closed_user_generated_count" in tickets_by_type
            assert "closed_system_generated_count" in tickets_by_type
            assert "user_generated_avg_resolution" in tickets_by_type
            assert "system_generated_avg_resolution" in tickets_by_type

            # Check chart data structures
            for chart_key in ["tickets_by_status", "tickets_by_category"]:
                chart_data = data[chart_key]
                assert "labels" in chart_data
                assert "datasets" in chart_data
                assert isinstance(chart_data["labels"], list)
                assert isinstance(chart_data["datasets"], list)

            # Check detailed chart data structure
            detailed_chart = data["tickets_by_location_and_category"]
            assert "labels" in detailed_chart
            assert "datasets" in detailed_chart
            assert isinstance(detailed_chart["labels"], list)
            assert isinstance(detailed_chart["datasets"], list)

    def test_dashboard_data_accuracy(self, create_user_role_with_permissions: Any) -> None:
        """Test that the dashboard returns accurate data based on test fixtures"""
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
            whole_business_area_access=True,
        )

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        tickets_by_type = data["tickets_by_type"]

        # We have 3 positive feedback (manual) and 2 needs adjudication (system) tickets
        # Plus 1 negative feedback (manual)
        expected_user_generated = 4  # 3 positive + 1 negative feedback
        expected_system_generated = 2  # 2 needs adjudication

        assert tickets_by_type["user_generated_count"] == expected_user_generated
        assert tickets_by_type["system_generated_count"] == expected_system_generated

        # We have 2 closed tickets (1 positive feedback + 2 needs adjudication from fixtures)
        expected_closed_user = 1  # 1 closed positive feedback
        expected_closed_system = 2  # 2 closed needs adjudication

        assert tickets_by_type["closed_user_generated_count"] == expected_closed_user
        assert tickets_by_type["closed_system_generated_count"] == expected_closed_system


class TestGrievanceProgramDashboardAPI:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        call_command("loadcountries")
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner, first_name="Test", last_name="User")
        self.client = api_client(self.user)
        self.business_area = BusinessArea.objects.get(slug="afghanistan")

        # Create program for program-specific testing
        self.program = ProgramFactory(name="Test Program", business_area=self.business_area)

        country = Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            area_level=2,
            country=country,
        )
        self.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="123aa123")

        created_at_dates_to_set = {
            GrievanceTicket.STATUS_NEW: datetime(year=2020, month=3, day=12, tzinfo=pytz.UTC),
            GrievanceTicket.STATUS_ON_HOLD: datetime(year=2020, month=7, day=12, tzinfo=pytz.UTC),
            GrievanceTicket.STATUS_IN_PROGRESS: datetime(year=2020, month=8, day=22, tzinfo=pytz.UTC),
        }

        grievances_to_create = (
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                status=GrievanceTicket.STATUS_NEW,
            ),
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                status=GrievanceTicket.STATUS_ON_HOLD,
            ),
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                status=GrievanceTicket.STATUS_IN_PROGRESS,
            ),
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                status=GrievanceTicket.STATUS_CLOSED,
            ),
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                status=GrievanceTicket.STATUS_CLOSED,
            ),
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                status=GrievanceTicket.STATUS_CLOSED,
            ),
        )

        for grievance_ticket in grievances_to_create:
            grievance_ticket.created_by = self.user
            grievance_ticket.assigned_to = self.user
            grievance_ticket.business_area = self.business_area
            grievance_ticket.admin2 = self.admin_area_1
            grievance_ticket.consent = True
            grievance_ticket.language = "Polish, English"
            grievance_ticket.description = "Just random description"

        GrievanceTicket.objects.bulk_create(grievances_to_create)

        # Associate some tickets with the program
        tickets = list(GrievanceTicket.objects.all())
        for ticket in tickets[:3]:  # Associate first 3 tickets with program
            ticket.programs.add(self.program)

        for status_value, date in created_at_dates_to_set.items():
            gt = GrievanceTicket.objects.get(status=status_value)
            gt.created_at = date
            gt.updated_at = datetime.now()
            gt.save()

        self.url = reverse(
            "api:grievance:grievance-tickets-dashboard",
            kwargs={
                "business_area_slug": self.business_area.slug,
                "program_slug": self.program.slug,
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
                status.HTTP_200_OK,
            ),
            (
                [],
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_program_dashboard_api_endpoint(
        self,
        permissions: List[Permissions],
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

        response = self.client.get(self.url)
        assert response.status_code == expected_status

        if expected_status == status.HTTP_200_OK:
            data = response.json()

            # Check main structure
            assert "tickets_by_type" in data
            assert "tickets_by_status" in data
            assert "tickets_by_category" in data
            assert "tickets_by_location_and_category" in data

            # Check tickets_by_type structure
            tickets_by_type = data["tickets_by_type"]
            assert "user_generated_count" in tickets_by_type
            assert "system_generated_count" in tickets_by_type
            assert "closed_user_generated_count" in tickets_by_type
            assert "closed_system_generated_count" in tickets_by_type
            assert "user_generated_avg_resolution" in tickets_by_type
            assert "system_generated_avg_resolution" in tickets_by_type

    def test_program_dashboard_filters_by_program(self, create_user_role_with_permissions: Any) -> None:
        """Test that the program dashboard only returns tickets associated with the program"""
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
            self.program,
        )

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        tickets_by_type = data["tickets_by_type"]

        # Should only include tickets associated with the program (first 3 tickets)
        # Looking at tickets created: pos_feedback(NEW), neg_feedback(ON_HOLD), pos_feedback(IN_PROGRESS), pos_feedback(CLOSED), needs_adj(CLOSED), needs_adj(CLOSED)
        # First 3 are: pos_feedback(NEW), neg_feedback(ON_HOLD), pos_feedback(IN_PROGRESS)
        # So we have: 2 positive feedback (user-generated) + 1 negative feedback (user-generated) = 3 user-generated
        expected_user_generated = 3  # 2 positive feedback + 1 negative feedback tickets associated with program
        expected_system_generated = 0  # 0 needs adjudication tickets in first 3

        assert tickets_by_type["user_generated_count"] == expected_user_generated
        assert tickets_by_type["system_generated_count"] == expected_system_generated
