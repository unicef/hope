"""Tests for grievance ticket related tickets functionality."""

from unittest.mock import MagicMock

import pytest

from extras.test_utils.factories.grievance import GrievanceTicketFactory


@pytest.fixture
def grievance_tickets() -> list:
    return GrievanceTicketFactory.create_batch(5)


def test_should_return_distinct_related_tickets(
    grievance_tickets: list,
) -> None:
    ticket1 = GrievanceTicketFactory()
    ticket2 = GrievanceTicketFactory()

    # ticket1 links to 5 grievance_tickets
    ticket1.linked_tickets.set(grievance_tickets)

    # ticket2 links to the same 5 tickets PLUS ticket1
    ticket2.linked_tickets.set(list(grievance_tickets) + [ticket1])

    # ticket1 should have: 5 original + ticket2 (added via ticket2 linking to ticket1) = 6
    # ticket2 should have: 5 original + ticket1 = 6
    assert ticket1.linked_tickets.count() == 6
    assert ticket2.linked_tickets.count() == 6


def test_get_related_tickets_count_deduplicates_linked_ticket_with_same_household() -> None:
    """A linked ticket that shares household_unicef_id with obj is counted only once."""
    from hope.apps.grievance.api.serializers.grievance_ticket import GrievanceTicketListSerializer

    serializer = GrievanceTicketListSerializer()

    same_hh_ticket = MagicMock()
    same_hh_ticket.household_unicef_id = "HH-001"

    other_hh_ticket = MagicMock()
    other_hh_ticket.household_unicef_id = "HH-002"

    obj = MagicMock()
    obj.household_unicef_id = "HH-001"
    obj.existing_tickets_count = 3
    obj.linked_tickets.all.return_value = [same_hh_ticket, other_hh_ticket]

    # overlap = 1 (same_hh_ticket matches obj.household_unicef_id)
    # result = len([same, other]) + 3 - 1 = 4
    assert serializer.get_related_tickets_count(obj) == 4
