from typing import Any

from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.test import TestCase

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    create_household_and_individuals,
)
from extras.test_utils.factories.program import ProgramFactory

from hct_mis_api.admin.household_admin_household import HouseholdWithdrawFromListMixin
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketIndividualDataUpdateDetails,
)
from hct_mis_api.apps.household.models import Document
from hct_mis_api.apps.household.services.household_withdraw import HouseholdWithdraw


class TestHouseholdWithdrawFromListMixin(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=business_area, status="ACTIVE")
        cls.program_other = ProgramFactory(business_area=business_area)
        cls.household_unicef_id = "HH-20-0192.6628"
        cls.household2_unicef_id = "HH-20-0192.6629"
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "business_area": business_area,
                "program": cls.program,
                "unicef_id": cls.household_unicef_id,
            },
            individuals_data=[{}],
        )
        cls.household2, cls.individuals2 = create_household_and_individuals(
            household_data={
                "business_area": business_area,
                "program": cls.program,
                "unicef_id": cls.household2_unicef_id,
            },
            individuals_data=[{}, {}],
        )

        cls.household_other_program, cls.individuals_other_program = create_household_and_individuals(
            household_data={
                "business_area": business_area,
                "program": cls.program_other,
                "unicef_id": cls.household_unicef_id,
            },
            individuals_data=[{}],
        )

        cls.document = DocumentFactory(
            individual=cls.individuals[0],
            program=cls.program,
        )

        cls.grievance_ticket = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS)
        cls.ticket_complaint_details = TicketComplaintDetails.objects.create(
            ticket=cls.grievance_ticket,
            household=cls.household,
        )
        cls.grievance_ticket2 = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS)
        cls.ticket_individual_data_update = TicketIndividualDataUpdateDetails.objects.create(
            ticket=cls.grievance_ticket2,
            individual=cls.individuals[0],
        )
        cls.grievance_ticket_household2 = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS)
        cls.ticket_complaint_details_household2 = TicketComplaintDetails.objects.create(
            ticket=cls.grievance_ticket_household2,
            household=cls.household2,
        )

        cls.program.household_count = 2
        cls.program.individual_count = 3
        cls.program.save()

    def _request_with_post_method_and_session_ba(self) -> HttpRequest:
        request = HttpRequest()
        request.method = "POST"
        middleware = SessionMiddleware(lambda req: None)  # type: ignore
        middleware.process_request(request)
        request.session.save()
        request.session["business_area"] = str(self.program.business_area.pk)
        return request

    def test_households_withdraw_from_list(self) -> None:
        def mock_get_common_context(*args: Any, **kwargs: Any) -> dict:
            return {}

        def mock_message_user(*args: Any, **kwargs: Any) -> None:
            pass

        HouseholdWithdrawFromListMixin.get_common_context = mock_get_common_context
        HouseholdWithdrawFromListMixin.message_user = mock_message_user

        request = self._request_with_post_method_and_session_ba()
        tag = "Some tag reason"
        request.POST = {  # type: ignore
            "step": "3",
            "household_list": f"{self.household.unicef_id}, {self.household2.unicef_id}",
            "tag": tag,
            "program": str(self.program.id),
            "business_area": self.program.business_area,
        }

        with self.assertNumQueries(28):
            HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=request)

        self.household.refresh_from_db()
        self.household_other_program.refresh_from_db()
        self.household2.refresh_from_db()
        self.individuals_other_program[0].refresh_from_db()
        self.individuals[0].refresh_from_db()
        self.individuals2[0].refresh_from_db()
        self.individuals2[1].refresh_from_db()
        self.document.refresh_from_db()
        self.grievance_ticket.refresh_from_db()
        self.grievance_ticket2.refresh_from_db()
        self.grievance_ticket_household2.refresh_from_db()

        self.assertEqual(
            self.household.withdrawn,
            True,
        )
        self.assertIsNotNone(self.household.withdrawn_date)
        self.assertEqual(
            self.household.internal_data["withdrawn_tag"],
            tag,
        )
        self.assertEqual(
            self.individuals[0].withdrawn,
            True,
        )
        self.assertIsNotNone(self.individuals[0].withdrawn_date)
        self.assertEqual(
            self.document.status,
            Document.STATUS_INVALID,
        )
        self.assertEqual(
            self.grievance_ticket.status,
            GrievanceTicket.STATUS_CLOSED,
        )
        self.assertEqual(
            self.grievance_ticket.extras["status_before_withdrawn"], str(GrievanceTicket.STATUS_IN_PROGRESS)
        )
        self.assertEqual(
            self.grievance_ticket2.status,
            GrievanceTicket.STATUS_CLOSED,
        )
        self.assertEqual(
            self.grievance_ticket2.extras["status_before_withdrawn"], str(GrievanceTicket.STATUS_IN_PROGRESS)
        )

        self.assertEqual(
            self.household2.withdrawn,
            True,
        )
        self.assertIsNotNone(self.household2.withdrawn_date)
        self.assertEqual(
            self.household2.internal_data["withdrawn_tag"],
            tag,
        )
        self.assertEqual(
            self.individuals2[0].withdrawn,
            True,
        )
        self.assertIsNotNone(self.individuals2[0].withdrawn_date)
        self.assertEqual(
            self.individuals2[1].withdrawn,
            True,
        )
        self.assertIsNotNone(self.individuals2[1].withdrawn_date)
        self.assertEqual(
            self.grievance_ticket_household2.status,
            GrievanceTicket.STATUS_CLOSED,
        )
        self.assertEqual(
            self.grievance_ticket_household2.extras["status_before_withdrawn"], str(GrievanceTicket.STATUS_IN_PROGRESS)
        )

        # household from another program is not withdrawn
        self.assertEqual(
            self.household_other_program.withdrawn,
            False,
        )
        self.assertEqual(
            self.individuals_other_program[0].withdrawn,
            False,
        )

        # check ability to revert this action
        service = HouseholdWithdraw(self.household)
        service.unwithdraw()
        service.change_tickets_status([self.ticket_complaint_details, self.ticket_individual_data_update])
        self.household.refresh_from_db()
        self.individuals[0].refresh_from_db()
        self.grievance_ticket.refresh_from_db()
        self.grievance_ticket2.refresh_from_db()
        self.assertEqual(
            self.household.withdrawn,
            False,
        )
        self.assertIsNone(self.household.withdrawn_date)
        self.assertEqual(
            self.individuals[0].withdrawn,
            False,
        )
        self.assertIsNone(self.individuals[0].withdrawn_date)
        self.assertEqual(
            self.grievance_ticket.status,
            GrievanceTicket.STATUS_IN_PROGRESS,
        )
        self.assertEqual(
            self.grievance_ticket.extras.get("status_before_withdrawn"),
            "",
        )
        self.assertEqual(
            self.grievance_ticket2.status,
            GrievanceTicket.STATUS_IN_PROGRESS,
        )
        self.assertEqual(
            self.grievance_ticket2.extras.get("status_before_withdrawn"),
            "",
        )

    def test_split_list_of_ids(self) -> None:
        self.assertEqual(
            HouseholdWithdrawFromListMixin.split_list_of_ids(
                "HH-1, HH-2/HH-3|HH-4 new line HH-5        HH-6",
            ),
            ["HH-1", "HH-2", "HH-3", "HH-4", "HH-5", "HH-6"],
        )

    def test_get_and_set_context_data(self) -> None:
        request = self._request_with_post_method_and_session_ba()
        household_list = f"{self.household.unicef_id}"
        tag = "Some tag reason"
        request.POST = {  # type: ignore
            "household_list": household_list,
            "tag": tag,
            "program": str(self.program.id),
            "business_area": str(self.program.business_area.pk),
        }
        context = {}
        HouseholdWithdrawFromListMixin.get_and_set_context_data(request, context)
        self.assertEqual(context["program"], str(self.program.id))
        self.assertEqual(context["household_list"], household_list)
        self.assertEqual(context["tag"], tag)
        self.assertEqual(context["business_area"], str(self.program.business_area.pk))

    def test_get_request(self) -> None:
        def mock_get_common_context(*args: Any, **kwargs: Any) -> dict:
            return {}

        HouseholdWithdrawFromListMixin.get_common_context = mock_get_common_context

        request = HttpRequest()
        request.method = "GET"
        resp = HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=request)
        self.assertEqual(resp.status_code, 200)

    def test_post_households_withdraw_from_list_step_0(self) -> None:
        def mock_get_common_context(*args: Any, **kwargs: Any) -> dict:
            return {}

        def mock_message_user(*args: Any, **kwargs: Any) -> None:
            pass

        HouseholdWithdrawFromListMixin.get_common_context = mock_get_common_context
        HouseholdWithdrawFromListMixin.message_user = mock_message_user

        request = self._request_with_post_method_and_session_ba()
        request.POST = {  # type: ignore
            "step": "0",
            "business_area": self.program.business_area,
        }

        with self.assertNumQueries(0):
            resp = HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=request)

        self.assertEqual(resp.status_code, 200)

    def test_post_households_withdraw_from_list_step_1(self) -> None:
        def mock_get_common_context(*args: Any, **kwargs: Any) -> dict:
            return {}

        def mock_message_user(*args: Any, **kwargs: Any) -> None:
            pass

        HouseholdWithdrawFromListMixin.get_common_context = mock_get_common_context
        HouseholdWithdrawFromListMixin.message_user = mock_message_user

        request = self._request_with_post_method_and_session_ba()
        tag = "Some tag reason"
        request.POST = {  # type: ignore
            "step": "1",
            "household_list": f"{self.household.unicef_id}, {self.household2.unicef_id}",
            "tag": tag,
            "program": str(self.program.id),
            "business_area": self.program.business_area,
        }

        with self.assertNumQueries(0):
            resp = HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=request)

        self.assertEqual(resp.status_code, 200)

    def test_post_households_withdraw_from_list_step_2(self) -> None:
        def mock_get_common_context(*args: Any, **kwargs: Any) -> dict:
            return {}

        def mock_message_user(*args: Any, **kwargs: Any) -> None:
            pass

        HouseholdWithdrawFromListMixin.get_common_context = mock_get_common_context
        HouseholdWithdrawFromListMixin.message_user = mock_message_user

        request = self._request_with_post_method_and_session_ba()
        tag = "Some tag reason"
        request.POST = {  # type: ignore
            "step": "2",
            "household_list": f"{self.household.unicef_id}, {self.household2.unicef_id}",
            "tag": tag,
            "program": str(self.program.id),
            "business_area": self.program.business_area,
        }

        with self.assertNumQueries(3):
            resp = HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=request)

        self.assertEqual(resp.status_code, 200)
