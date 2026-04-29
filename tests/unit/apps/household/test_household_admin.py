from typing import Any
from unittest.mock import patch

from django.contrib.admin import AdminSite
from django.contrib.auth.models import Permission
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache import cache
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.admin.household import HouseholdAdmin, HouseholdWithdrawFromListMixin
from hope.apps.grievance.models import GrievanceTicket, TicketComplaintDetails, TicketIndividualDataUpdateDetails
from hope.apps.household.api.caches import get_household_list_program_key, get_individual_list_program_key
from hope.apps.household.services.household_withdraw import HouseholdWithdraw
from hope.models import Document, Household

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
    monkeypatch.setattr(HouseholdWithdrawFromListMixin, "get_common_context", lambda *a, **k: {}, raising=False)
    monkeypatch.setattr(HouseholdWithdrawFromListMixin, "message_user", lambda *a, **k: None, raising=False)


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

    with patch("hope.admin.household.increment_grievance_ticket_version_cache_for_ticket_ids") as mocked_increment:
        with django_assert_num_queries(26):
            HouseholdWithdrawFromListMixin().withdraw_households_from_list(request=post_request)

    mocked_increment.assert_called_once()
    assert mocked_increment.call_args.args[0] == program.business_area.slug
    assert set(mocked_increment.call_args.args[1]) == {
        grievance_ticket.id,
        grievance_ticket2.id,
        grievance_ticket_household2.id,
    }

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


def test_mass_withdraw_from_list_bulk_invalidates_cache(households_context) -> None:
    program = households_context["program"]
    household = households_context["household"]
    household2 = households_context["household2"]

    cache.clear()

    initial_hh_version = get_household_list_program_key(program.id)
    initial_ind_version = get_individual_list_program_key(program.id)

    with TestCase.captureOnCommitCallbacks(execute=True):
        HouseholdWithdrawFromListMixin().mass_withdraw_households_from_list_bulk(
            [household.unicef_id, household2.unicef_id],
            "test tag",
            program,
        )

    new_hh_version = get_household_list_program_key(program.id)
    new_ind_version = get_individual_list_program_key(program.id)

    assert new_hh_version > initial_hh_version
    assert new_ind_version > initial_ind_version


# ── mass_withdraw / mass_unwithdraw action tests ──────────────────────────


@pytest.fixture
def admin_user():
    return UserFactory(username="admin_btn", is_staff=True, is_superuser=True, is_active=True, status="ACTIVE")


@pytest.fixture
def admin_withdraw_mocks(monkeypatch):
    monkeypatch.setattr(HouseholdAdmin, "get_common_context", lambda *a, **k: {}, raising=False)
    monkeypatch.setattr(HouseholdAdmin, "message_user", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(HouseholdAdmin, "log_change", lambda *a, **k: None, raising=False)


@pytest.fixture
def admin_post_request(admin_user):
    def _make(household, extra_post: dict | None = None) -> HttpRequest:
        request = HttpRequest()
        request.method = "POST"
        request.user = admin_user
        request.POST = {"apply": "1", "reason": "", "_selected_action": str(household.pk), **(extra_post or {})}  # type: ignore
        return request

    return _make


@pytest.fixture
def active_household_with_ticket(business_area, programs):
    program = programs["program"]
    household = HouseholdFactory(business_area=business_area, program=program, create_role=False)
    individual = IndividualFactory(household=household, business_area=business_area, program=program)
    household.head_of_household = individual
    household.save(update_fields=["head_of_household"])
    document = DocumentFactory(individual=individual, program=program)
    ticket = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS, business_area=business_area)
    ticket.programs.add(program)
    TicketComplaintDetails.objects.create(ticket=ticket, household=household)
    return {"household": household, "individual": individual, "document": document, "ticket": ticket}


@pytest.fixture
def withdrawn_household_with_ticket(business_area, programs):
    program = programs["program"]
    household = HouseholdFactory(business_area=business_area, program=program, create_role=False, withdrawn=True)
    individual = IndividualFactory(household=household, business_area=business_area, program=program, withdrawn=True)
    household.head_of_household = individual
    household.save(update_fields=["head_of_household"])
    ticket = GrievanceTicketFactory(
        status=GrievanceTicket.STATUS_CLOSED,
        business_area=business_area,
        extras={"status_before_withdrawn": str(GrievanceTicket.STATUS_IN_PROGRESS)},
    )
    ticket.programs.add(program)
    TicketComplaintDetails.objects.create(ticket=ticket, household=household)
    document = DocumentFactory(individual=individual, program=program, status=Document.STATUS_INVALID)
    return {"household": household, "individual": individual, "ticket": ticket, "document": document}


def test_mass_withdraw_closes_linked_tickets_and_invalidates_documents(
    active_household_with_ticket, admin_withdraw_mocks, admin_post_request
) -> None:
    household = active_household_with_ticket["household"]
    ticket = active_household_with_ticket["ticket"]
    document = active_household_with_ticket["document"]

    HouseholdAdmin(Household, AdminSite()).mass_withdraw(
        admin_post_request(household, {"tag": "test-tag"}),
        Household.objects.filter(pk=household.pk),
    )

    ticket.refresh_from_db()
    document.refresh_from_db()
    assert ticket.status == GrievanceTicket.STATUS_CLOSED
    assert ticket.extras["status_before_withdrawn"] == GrievanceTicket.STATUS_IN_PROGRESS
    assert document.status == Document.STATUS_INVALID


def test_mass_withdraw_skips_already_withdrawn(
    withdrawn_household_with_ticket, admin_withdraw_mocks, admin_post_request
) -> None:
    household = withdrawn_household_with_ticket["household"]

    HouseholdAdmin(Household, AdminSite()).mass_withdraw(
        admin_post_request(household, {"tag": "test-tag"}),
        Household.objects.filter(pk=household.pk),
    )

    household.refresh_from_db()
    assert household.withdrawn is True


def test_mass_unwithdraw_reopens_linked_tickets(
    withdrawn_household_with_ticket, admin_withdraw_mocks, admin_post_request
) -> None:
    household = withdrawn_household_with_ticket["household"]
    ticket = withdrawn_household_with_ticket["ticket"]

    HouseholdAdmin(Household, AdminSite()).mass_unwithdraw(
        admin_post_request(household, {"reopen_tickets": "on"}),
        Household.objects.filter(pk=household.pk),
    )

    household.refresh_from_db()
    ticket.refresh_from_db()
    assert household.withdrawn is False
    assert ticket.status == GrievanceTicket.STATUS_IN_PROGRESS
    assert ticket.extras.get("status_before_withdrawn") == ""


def test_mass_unwithdraw_restores_document_status(
    withdrawn_household_with_ticket, admin_withdraw_mocks, admin_post_request
) -> None:
    household = withdrawn_household_with_ticket["household"]
    document = withdrawn_household_with_ticket["document"]

    HouseholdAdmin(Household, AdminSite()).mass_unwithdraw(
        admin_post_request(household),
        Household.objects.filter(pk=household.pk),
    )

    document.refresh_from_db()
    assert document.status == Document.STATUS_NEED_INVESTIGATION


def test_mass_unwithdraw_keeps_tickets_closed_when_reopen_not_requested(
    withdrawn_household_with_ticket, admin_withdraw_mocks, admin_post_request
) -> None:
    household = withdrawn_household_with_ticket["household"]
    ticket = withdrawn_household_with_ticket["ticket"]

    HouseholdAdmin(Household, AdminSite()).mass_unwithdraw(
        admin_post_request(household),
        Household.objects.filter(pk=household.pk),
    )

    household.refresh_from_db()
    ticket.refresh_from_db()
    assert household.withdrawn is False
    assert ticket.status == GrievanceTicket.STATUS_CLOSED


def test_mass_withdraw_counts_only_newly_withdrawn(
    active_household_with_ticket, withdrawn_household_with_ticket, admin_post_request
) -> None:
    active_hh = active_household_with_ticket["household"]
    already_withdrawn_hh = withdrawn_household_with_ticket["household"]
    qs = Household.objects.filter(pk__in=[active_hh.pk, already_withdrawn_hh.pk])
    messages_sent = []
    with (
        patch.object(HouseholdAdmin, "get_common_context", return_value={}),
        patch.object(HouseholdAdmin, "log_change"),
        patch.object(HouseholdAdmin, "message_user", side_effect=lambda req, msg, *a, **k: messages_sent.append(msg)),
    ):
        HouseholdAdmin(Household, AdminSite()).mass_withdraw(
            admin_post_request(active_hh, {"tag": "test-tag"}),
            qs,
        )
    assert messages_sent == ["Changed 1 Households."]


def test_mass_unwithdraw_counts_only_newly_unwithdrawn(
    active_household_with_ticket, withdrawn_household_with_ticket, admin_post_request
) -> None:
    withdrawn_hh = withdrawn_household_with_ticket["household"]
    not_withdrawn_hh = active_household_with_ticket["household"]
    qs = Household.objects.filter(pk__in=[withdrawn_hh.pk, not_withdrawn_hh.pk])
    messages_sent = []
    with (
        patch.object(HouseholdAdmin, "get_common_context", return_value={}),
        patch.object(HouseholdAdmin, "log_change"),
        patch.object(HouseholdAdmin, "message_user", side_effect=lambda req, msg, *a, **k: messages_sent.append(msg)),
    ):
        HouseholdAdmin(Household, AdminSite()).mass_unwithdraw(
            admin_post_request(withdrawn_hh, {"reopen_tickets": "on"}),
            qs,
        )
    assert messages_sent == ["Changed 1 Households."]


def test_has_withdrawn_permission_grants_access_with_perm() -> None:
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="can_withdrawn"))
    request = HttpRequest()
    request.user = user

    assert HouseholdAdmin(Household, AdminSite()).has_withdrawn_permission(request) is True


def test_has_withdrawn_permission_denies_access_without_perm() -> None:
    user = UserFactory(is_staff=True)
    request = HttpRequest()
    request.user = user

    assert HouseholdAdmin(Household, AdminSite()).has_withdrawn_permission(request) is False


def test_mass_withdraw_unwithdraw_not_available_without_withdrawn_permission() -> None:
    user = UserFactory(is_staff=True)
    request = HttpRequest()
    request.user = user

    actions = HouseholdAdmin(Household, AdminSite()).get_actions(request)

    assert "mass_withdraw" not in actions
    assert "mass_unwithdraw" not in actions


def test_mass_withdraw_unwithdraw_available_with_withdrawn_permission() -> None:
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="can_withdrawn"))
    request = HttpRequest()
    request.user = user

    actions = HouseholdAdmin(Household, AdminSite()).get_actions(request)

    assert "mass_withdraw" in actions
    assert "mass_unwithdraw" in actions


def test_mass_withdraw_fires_household_withdrawn_signal(
    active_household_with_ticket, admin_withdraw_mocks, admin_post_request
) -> None:
    from hope.apps.household.signals import household_withdrawn

    household = active_household_with_ticket["household"]
    signal_calls = []

    def on_signal(sender, instance, **kwargs):
        signal_calls.append(instance)

    household_withdrawn.connect(on_signal)
    try:
        HouseholdAdmin(Household, AdminSite()).mass_withdraw(
            admin_post_request(household, {"tag": "test-tag"}),
            Household.objects.filter(pk=household.pk),
        )
    finally:
        household_withdrawn.disconnect(on_signal)

    assert len(signal_calls) == 1
    assert signal_calls[0].pk == household.pk


def test_mass_withdraw_invalidates_grievance_ticket_cache(
    active_household_with_ticket, admin_withdraw_mocks, admin_post_request
) -> None:
    household = active_household_with_ticket["household"]

    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mock_cache:
        HouseholdAdmin(Household, AdminSite()).mass_withdraw(
            admin_post_request(household, {"tag": "test-tag"}),
            Household.objects.filter(pk=household.pk),
        )

    assert mock_cache.called


def test_mass_unwithdraw_invalidates_grievance_ticket_cache(
    withdrawn_household_with_ticket, admin_withdraw_mocks, admin_post_request
) -> None:
    household = withdrawn_household_with_ticket["household"]

    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mock_cache:
        HouseholdAdmin(Household, AdminSite()).mass_unwithdraw(
            admin_post_request(household, {"reopen_tickets": "on"}),
            Household.objects.filter(pk=household.pk),
        )

    assert mock_cache.called


def test_mass_unwithdraw_calls_adjust_program_size(
    withdrawn_household_with_ticket, admin_withdraw_mocks, admin_post_request
) -> None:
    household = withdrawn_household_with_ticket["household"]

    with patch("hope.admin.household.adjust_program_size") as mock_adjust:
        HouseholdAdmin(Household, AdminSite()).mass_unwithdraw(
            admin_post_request(household),
            Household.objects.filter(pk=household.pk),
        )

    mock_adjust.assert_called_once_with(household.program)


def test_mass_withdraw_from_list_bulk_calls_adjust_program_size(households_context) -> None:
    program = households_context["program"]
    household = households_context["household"]

    with patch("hope.admin.household.adjust_program_size") as mock_adjust:
        HouseholdWithdrawFromListMixin().mass_withdraw_households_from_list_bulk(
            [household.unicef_id], "test-tag", program
        )

    mock_adjust.assert_called_once_with(program)


# ── single withdraw / unwithdraw button tests ─────────────────────────────


@pytest.fixture
def admin_http_client(client, admin_user):
    client.force_login(admin_user, backend="django.contrib.auth.backends.ModelBackend")
    return client


def test_single_withdraw_closes_linked_tickets_and_invalidates_documents(
    active_household_with_ticket, admin_http_client
) -> None:
    household = active_household_with_ticket["household"]
    ticket = active_household_with_ticket["ticket"]
    document = active_household_with_ticket["document"]

    url = reverse("admin:household_household_withdraw", args=[household.pk])
    response = admin_http_client.post(url, {"tag": "test-tag", "reason": ""})

    assert response.status_code == 302
    ticket.refresh_from_db()
    document.refresh_from_db()
    assert ticket.status == GrievanceTicket.STATUS_CLOSED
    assert ticket.extras["status_before_withdrawn"] == GrievanceTicket.STATUS_IN_PROGRESS
    assert document.status == Document.STATUS_INVALID


def test_single_unwithdraw_reopens_linked_tickets_and_restores_documents(
    withdrawn_household_with_ticket, admin_http_client
) -> None:
    household = withdrawn_household_with_ticket["household"]
    ticket = withdrawn_household_with_ticket["ticket"]
    document = withdrawn_household_with_ticket["document"]

    url = reverse("admin:household_household_withdraw", args=[household.pk])
    response = admin_http_client.post(url, {"tag": "", "reason": ""})

    assert response.status_code == 302
    ticket.refresh_from_db()
    document.refresh_from_db()
    assert ticket.status == GrievanceTicket.STATUS_IN_PROGRESS
    assert ticket.extras.get("status_before_withdrawn") == ""
    assert document.status == Document.STATUS_NEED_INVESTIGATION


def test_single_unwithdraw_calls_adjust_program_size(withdrawn_household_with_ticket, admin_http_client) -> None:
    household = withdrawn_household_with_ticket["household"]
    url = reverse("admin:household_household_withdraw", args=[household.pk])

    with patch("hope.admin.household.adjust_program_size") as mock_adjust:
        admin_http_client.post(url, {"tag": "", "reason": ""})

    mock_adjust.assert_called_once_with(household.program)


def test_single_withdraw_button_allowed_with_withdrawn_permission(active_household_with_ticket, client) -> None:
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="can_withdrawn"))
    client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
    household = active_household_with_ticket["household"]

    url = reverse("admin:household_household_withdraw", args=[household.pk])
    response = client.post(url, {"tag": "test-tag", "reason": ""})

    assert response.status_code == 302


def test_single_withdraw_button_requires_withdrawn_permission(active_household_with_ticket, client) -> None:
    user = UserFactory(is_staff=True)
    client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
    household = active_household_with_ticket["household"]

    url = reverse("admin:household_household_withdraw", args=[household.pk])
    response = client.post(url, {"tag": "test-tag", "reason": ""})

    assert response.status_code == 403


def test_single_unwithdraw_button_allowed_with_withdrawn_permission(withdrawn_household_with_ticket, client) -> None:
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="can_withdrawn"))
    client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
    household = withdrawn_household_with_ticket["household"]

    url = reverse("admin:household_household_withdraw", args=[household.pk])
    response = client.post(url, {"tag": "", "reason": ""})

    assert response.status_code == 302


def test_single_unwithdraw_button_requires_withdrawn_permission(withdrawn_household_with_ticket, client) -> None:
    user = UserFactory(is_staff=True)
    client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
    household = withdrawn_household_with_ticket["household"]

    url = reverse("admin:household_household_withdraw", args=[household.pk])
    response = client.post(url, {"tag": "", "reason": ""})

    assert response.status_code == 403
