from typing import Any

from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
)
from hope.admin.household import HouseholdWithdrawFromListMixin
from hope.apps.grievance.models import GrievanceTicket, TicketComplaintDetails, TicketIndividualDataUpdateDetails
from hope.apps.household.services.household_withdraw import HouseholdWithdraw
from hope.models import Document

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def programs(business_area):
    return {
        "program": ProgramFactory(business_area=business_area, status="ACTIVE"),
        "program_other": ProgramFactory(business_area=business_area),
    }


@pytest.fixture
def households_context(programs, business_area):
    program = programs["program"]
    program_other = programs["program_other"]
    household_unicef_id = "HH-20-0192.6628"
    household2_unicef_id = "HH-20-0192.6629"

    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        create_role=False,
    )
    household.unicef_id = household_unicef_id
    household.save(update_fields=["unicef_id"])
    individual = IndividualFactory(household=household, business_area=business_area, program=program)
    household.head_of_household = individual
    household.save(update_fields=["head_of_household"])

    household2 = HouseholdFactory(
        business_area=business_area,
        program=program,
        create_role=False,
    )
    household2.unicef_id = household2_unicef_id
    household2.save(update_fields=["unicef_id"])
    individuals2 = [
        IndividualFactory(household=household2, business_area=business_area, program=program),
        IndividualFactory(household=household2, business_area=business_area, program=program),
    ]
    household2.head_of_household = individuals2[0]
    household2.save(update_fields=["head_of_household"])

    household_other_program = HouseholdFactory(
        business_area=business_area,
        program=program_other,
        create_role=False,
    )
    household_other_program.unicef_id = household_unicef_id
    household_other_program.save(update_fields=["unicef_id"])
    individual_other_program = IndividualFactory(
        household=household_other_program,
        business_area=business_area,
        program=program_other,
    )
    household_other_program.head_of_household = individual_other_program
    household_other_program.save(update_fields=["head_of_household"])

    document = DocumentFactory(
        individual=individual,
        program=program,
    )

    grievance_ticket = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS, business_area=business_area)
    ticket_complaint_details = TicketComplaintDetails.objects.create(
        ticket=grievance_ticket,
        household=household,
    )
    grievance_ticket2 = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS, business_area=business_area)
    ticket_individual_data_update = TicketIndividualDataUpdateDetails.objects.create(
        ticket=grievance_ticket2,
        individual=individual,
    )
    grievance_ticket_household2 = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_IN_PROGRESS, business_area=business_area
    )
    ticket_complaint_details_household2 = TicketComplaintDetails.objects.create(
        ticket=grievance_ticket_household2,
        household=household2,
    )

    program.household_count = 2
    program.individual_count = 3
    program.save(update_fields=["household_count", "individual_count"])

    return {
        "program": program,
        "program_other": program_other,
        "household": household,
        "household2": household2,
        "household_other_program": household_other_program,
        "individual": individual,
        "individuals2": individuals2,
        "individual_other_program": individual_other_program,
        "document": document,
        "grievance_ticket": grievance_ticket,
        "grievance_ticket2": grievance_ticket2,
        "grievance_ticket_household2": grievance_ticket_household2,
        "ticket_complaint_details": ticket_complaint_details,
        "ticket_individual_data_update": ticket_individual_data_update,
        "ticket_complaint_details_household2": ticket_complaint_details_household2,
    }


@pytest.fixture
def post_request(programs):
    request = HttpRequest()
    request.method = "POST"
    middleware = SessionMiddleware(lambda req: None)  # type: ignore
    middleware.process_request(request)
    request.session.save()
    request.session["business_area"] = str(programs["program"].business_area.pk)
    return request


@pytest.fixture
def mixin_mocks(monkeypatch):
    monkeypatch.setattr(HouseholdWithdrawFromListMixin, "get_common_context", lambda *a, **k: {})
    monkeypatch.setattr(HouseholdWithdrawFromListMixin, "message_user", lambda *a, **k: None)


def test_households_withdraw_from_list(
    households_context,
    post_request,
    mixin_mocks,
    django_assert_num_queries,
) -> None:
    program = households_context["program"]
    household = households_context["household"]
    household2 = households_context["household2"]
    household_other_program = households_context["household_other_program"]
    individual = households_context["individual"]
    individuals2 = households_context["individuals2"]
    individual_other_program = households_context["individual_other_program"]
    document = households_context["document"]
    grievance_ticket = households_context["grievance_ticket"]
    grievance_ticket2 = households_context["grievance_ticket2"]
    grievance_ticket_household2 = households_context["grievance_ticket_household2"]
    ticket_complaint_details = households_context["ticket_complaint_details"]
    ticket_individual_data_update = households_context["ticket_individual_data_update"]

    tag = "Some tag reason"
    post_request.POST = {  # type: ignore
        "step": "3",
        "household_list": f"{household.unicef_id}, {household2.unicef_id}",
        "tag": tag,
        "program": str(program.id),
        "business_area": program.business_area,
    }

    with django_assert_num_queries(28):
        HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=post_request)

    household.refresh_from_db()
    household_other_program.refresh_from_db()
    household2.refresh_from_db()
    individual_other_program.refresh_from_db()
    individual.refresh_from_db()
    individuals2[0].refresh_from_db()
    individuals2[1].refresh_from_db()
    document.refresh_from_db()
    grievance_ticket.refresh_from_db()
    grievance_ticket2.refresh_from_db()
    grievance_ticket_household2.refresh_from_db()

    assert household.withdrawn is True
    assert household.withdrawn_date is not None
    assert household.internal_data["withdrawn_tag"] == tag
    assert individual.withdrawn is True
    assert individual.withdrawn_date is not None
    assert document.status == Document.STATUS_INVALID
    assert grievance_ticket.status == GrievanceTicket.STATUS_CLOSED
    assert grievance_ticket.extras["status_before_withdrawn"] == str(GrievanceTicket.STATUS_IN_PROGRESS)
    assert grievance_ticket2.status == GrievanceTicket.STATUS_CLOSED
    assert grievance_ticket2.extras["status_before_withdrawn"] == str(GrievanceTicket.STATUS_IN_PROGRESS)

    assert household2.withdrawn is True
    assert household2.withdrawn_date is not None
    assert household2.internal_data["withdrawn_tag"] == tag
    assert individuals2[0].withdrawn is True
    assert individuals2[0].withdrawn_date is not None
    assert individuals2[1].withdrawn is True
    assert individuals2[1].withdrawn_date is not None
    assert grievance_ticket_household2.status == GrievanceTicket.STATUS_CLOSED
    assert grievance_ticket_household2.extras["status_before_withdrawn"] == str(GrievanceTicket.STATUS_IN_PROGRESS)

    assert household_other_program.withdrawn is False
    assert individual_other_program.withdrawn is False

    service = HouseholdWithdraw(household)
    service.unwithdraw()
    service.change_tickets_status([ticket_complaint_details, ticket_individual_data_update])
    household.refresh_from_db()
    individual.refresh_from_db()
    grievance_ticket.refresh_from_db()
    grievance_ticket2.refresh_from_db()
    assert household.withdrawn is False
    assert household.withdrawn_date is None
    assert individual.withdrawn is False
    assert individual.withdrawn_date is None
    assert grievance_ticket.status == GrievanceTicket.STATUS_IN_PROGRESS
    assert grievance_ticket.extras.get("status_before_withdrawn") == ""
    assert grievance_ticket2.status == GrievanceTicket.STATUS_IN_PROGRESS
    assert grievance_ticket2.extras.get("status_before_withdrawn") == ""


def test_split_list_of_ids() -> None:
    assert HouseholdWithdrawFromListMixin.split_list_of_ids(
        "HH-1, HH-2/HH-3|HH-4 new line HH-5        HH-6",
    ) == ["HH-1", "HH-2", "HH-3", "HH-4", "HH-5", "HH-6"]


def test_get_and_set_context_data(households_context, post_request) -> None:
    program = households_context["program"]
    household = households_context["household"]
    household_list = f"{household.unicef_id}"
    tag = "Some tag reason"
    post_request.POST = {  # type: ignore
        "household_list": household_list,
        "tag": tag,
        "program": str(program.id),
        "business_area": str(program.business_area.pk),
    }
    context: dict[str, Any] = {}
    HouseholdWithdrawFromListMixin.get_and_set_context_data(post_request, context)
    assert context["program"] == str(program.id)
    assert context["household_list"] == household_list
    assert context["tag"] == tag
    assert context["business_area"] == str(program.business_area.pk)


def test_get_request(mixin_mocks) -> None:
    request = HttpRequest()
    request.method = "GET"
    resp = HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=request)
    assert resp.status_code == 200


def test_post_households_withdraw_from_list_step_0(
    households_context,
    post_request,
    mixin_mocks,
    django_assert_num_queries,
) -> None:
    program = households_context["program"]
    post_request.POST = {  # type: ignore
        "step": "0",
        "business_area": program.business_area,
    }

    with django_assert_num_queries(0):
        resp = HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=post_request)

    assert resp.status_code == 200


def test_post_households_withdraw_from_list_step_1(
    households_context,
    post_request,
    mixin_mocks,
    django_assert_num_queries,
) -> None:
    program = households_context["program"]
    household = households_context["household"]
    household2 = households_context["household2"]
    tag = "Some tag reason"
    post_request.POST = {  # type: ignore
        "step": "1",
        "household_list": f"{household.unicef_id}, {household2.unicef_id}",
        "tag": tag,
        "program": str(program.id),
        "business_area": program.business_area,
    }

    with django_assert_num_queries(0):
        resp = HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=post_request)

    assert resp.status_code == 200


def test_post_households_withdraw_from_list_step_2(
    households_context,
    post_request,
    mixin_mocks,
    django_assert_num_queries,
) -> None:
    program = households_context["program"]
    household = households_context["household"]
    household2 = households_context["household2"]
    tag = "Some tag reason"
    post_request.POST = {  # type: ignore
        "step": "2",
        "household_list": f"{household.unicef_id}, {household2.unicef_id}",
        "tag": tag,
        "program": str(program.id),
        "business_area": program.business_area,
    }

    with django_assert_num_queries(3):
        resp = HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=post_request)

    assert resp.status_code == 200
