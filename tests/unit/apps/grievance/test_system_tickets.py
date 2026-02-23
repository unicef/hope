import pytest

from extras.test_utils.factories import (
    IndividualFactory,
    SanctionListIndividualFactory,
    TicketSystemFlaggingDetailsFactory,
    UserFactory,
)
from hope.apps.grievance.services.system_ticket_service import close_system_flagging_ticket_service
from hope.models import Individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def system_ticket_context() -> dict:
    user = UserFactory()
    individual = IndividualFactory()
    sanction_list_individual = SanctionListIndividualFactory()
    return {
        "user": user,
        "individual": individual,
        "sanction_list_individual": sanction_list_individual,
    }


def test_close_system_flagging_ticket_with_approve_status(system_ticket_context: dict) -> None:
    ticket_details = TicketSystemFlaggingDetailsFactory(
        golden_records_individual=system_ticket_context["individual"],
        sanction_list_individual=system_ticket_context["sanction_list_individual"],
        approve_status=True,
    )

    close_system_flagging_ticket_service(ticket_details.ticket, system_ticket_context["user"])
    individual = Individual.objects.get(pk=system_ticket_context["individual"].pk)
    assert individual.sanction_list_confirmed_match


def test_close_system_flagging_ticket_without_approve_status(system_ticket_context: dict) -> None:
    ticket_details = TicketSystemFlaggingDetailsFactory(
        golden_records_individual=system_ticket_context["individual"],
        sanction_list_individual=system_ticket_context["sanction_list_individual"],
        approve_status=False,
    )

    close_system_flagging_ticket_service(ticket_details.ticket, system_ticket_context["user"])
    individual = Individual.objects.get(pk=system_ticket_context["individual"].pk)
    assert not individual.sanction_list_confirmed_match
