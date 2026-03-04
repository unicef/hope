"""Tests for grievance ticket related tickets functionality."""

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
