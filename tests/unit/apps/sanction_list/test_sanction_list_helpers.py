"""Unit tests for extracted helper functions in check_against_sanction_list_pre_merge."""

from unittest.mock import MagicMock, patch
import uuid

import pytest

from hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    _resolve_individual_hit,
    _save_tickets,
)


@pytest.fixture
def make_hit():
    def _factory(*, hit_id: str = "ind-1", score: float = 10.0) -> MagicMock:
        hit = MagicMock()
        hit.id = hit_id
        hit.meta.score = score
        return hit

    return _factory


@pytest.fixture
def make_program():
    def _factory(*, program_id: str | None = None) -> MagicMock:
        program = MagicMock()
        program.id = program_id or str(uuid.uuid4())
        return program

    return _factory


# ---------------------------------------------------------------------------
# _resolve_individual_hit
# ---------------------------------------------------------------------------


# Branch 1: individuals_ids is non-empty and hit.id is NOT in the list
@patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
def test_returns_none_when_hit_id_not_in_individuals_ids(mock_individual_cls, make_hit, make_program):
    hit = make_hit(hit_id="not-in-list")
    program = make_program()
    individuals_ids = ["id-a", "id-b"]

    result = _resolve_individual_hit(hit, individuals_ids, 5.0, program)

    assert result is None
    # DB should never be queried
    mock_individual_cls.all_objects.filter.assert_not_called()


# Branch 2: score is below the threshold
@patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
def test_returns_none_when_score_below_threshold(mock_individual_cls, make_hit, make_program):
    hit = make_hit(hit_id="id-a", score=3.0)
    program = make_program()
    individuals_ids = ["id-a"]

    result = _resolve_individual_hit(hit, individuals_ids, 5.0, program)

    assert result is None
    mock_individual_cls.all_objects.filter.assert_not_called()


# Branch 3: individual not found in the database
@patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
def test_returns_none_when_individual_not_in_db(mock_individual_cls, make_hit, make_program):
    hit = make_hit(hit_id="id-a", score=10.0)
    program = make_program()
    individuals_ids = ["id-a"]
    mock_individual_cls.all_objects.filter.return_value.first.return_value = None

    result = _resolve_individual_hit(hit, individuals_ids, 5.0, program)

    assert result is None
    mock_individual_cls.all_objects.filter.assert_called_once_with(id="id-a")


# Branch 4: individual program_id does not match program.id
@patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
def test_returns_none_when_program_id_mismatch(mock_individual_cls, make_hit, make_program):
    hit = make_hit(hit_id="id-a", score=10.0)
    program = make_program(program_id="program-1")
    individuals_ids = ["id-a"]

    db_individual = MagicMock()
    db_individual.program_id = "different-program"
    mock_individual_cls.all_objects.filter.return_value.first.return_value = db_individual

    result = _resolve_individual_hit(hit, individuals_ids, 5.0, program)

    assert result is None


# Branch 5 (success): all checks pass, return the individual
@patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
def test_returns_individual_on_success(mock_individual_cls, make_hit, make_program):
    program_id = "program-1"
    hit = make_hit(hit_id="id-a", score=10.0)
    program = make_program(program_id=program_id)
    individuals_ids = ["id-a"]

    db_individual = MagicMock()
    db_individual.program_id = program_id
    mock_individual_cls.all_objects.filter.return_value.first.return_value = db_individual

    result = _resolve_individual_hit(hit, individuals_ids, 5.0, program)

    assert result is db_individual


# Extra edge case: empty individuals_ids list skips the membership check
@patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
def test_empty_individuals_ids_skips_membership_check(mock_individual_cls, make_hit, make_program):
    """When individuals_ids is an empty list (falsy), the first guard is skipped."""
    program_id = "program-1"
    hit = make_hit(hit_id="id-a", score=10.0)
    program = make_program(program_id=program_id)

    db_individual = MagicMock()
    db_individual.program_id = program_id
    mock_individual_cls.all_objects.filter.return_value.first.return_value = db_individual

    result = _resolve_individual_hit(hit, [], 5.0, program)

    assert result is db_individual


# ---------------------------------------------------------------------------
# _save_tickets
# ---------------------------------------------------------------------------


@patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.TicketSystemFlaggingDetails")
@patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.GrievanceTicket")
def test_bulk_creates_tickets_programs_and_details(
    mock_grievance_ticket_cls,
    mock_details_cls,
):
    mock_through = MagicMock()
    mock_grievance_ticket_cls.programs.through = mock_through
    tickets_to_create = [MagicMock(name="ticket_1"), MagicMock(name="ticket_2")]
    tickets_programs = [MagicMock(name="program_through_1")]
    ticket_details_to_create = [MagicMock(name="detail_1")]

    _save_tickets(tickets_to_create, tickets_programs, ticket_details_to_create)

    mock_grievance_ticket_cls.objects.bulk_create.assert_called_once_with(tickets_to_create)
    mock_through.objects.bulk_create.assert_called_once_with(tickets_programs)
    mock_details_cls.objects.bulk_create.assert_called_once_with(ticket_details_to_create)


@patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.TicketSystemFlaggingDetails")
@patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.GrievanceTicket")
def test_empty_lists_still_bulk_create(
    mock_grievance_ticket_cls,
    mock_details_cls,
):
    mock_through = MagicMock()
    mock_grievance_ticket_cls.programs.through = mock_through

    _save_tickets([], [], [])

    mock_grievance_ticket_cls.objects.bulk_create.assert_called_once_with([])
    mock_through.objects.bulk_create.assert_called_once_with([])
    mock_details_cls.objects.bulk_create.assert_called_once_with([])
