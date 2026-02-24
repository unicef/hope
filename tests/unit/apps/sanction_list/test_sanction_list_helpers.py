"""Unit tests for extracted helper functions in check_against_sanction_list_pre_merge."""

from unittest.mock import MagicMock, patch
import uuid

from hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    _resolve_individual_hit,
    _save_tickets_and_notify,
)

# ---------------------------------------------------------------------------
# _resolve_individual_hit
# ---------------------------------------------------------------------------


class TestResolveIndividualHit:
    """Tests for _resolve_individual_hit covering all five branches."""

    def _make_hit(self, *, hit_id: str = "ind-1", score: float = 10.0) -> MagicMock:
        hit = MagicMock()
        hit.id = hit_id
        hit.meta.score = score
        return hit

    def _make_program(self, *, program_id: str | None = None) -> MagicMock:
        program = MagicMock()
        program.id = program_id or str(uuid.uuid4())
        return program

    # Branch 1: individuals_ids is non-empty and hit.id is NOT in the list
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
    def test_returns_none_when_hit_id_not_in_individuals_ids(self, mock_individual_cls: MagicMock) -> None:
        hit = self._make_hit(hit_id="not-in-list")
        program = self._make_program()
        individuals_ids = ["id-a", "id-b"]

        result = _resolve_individual_hit(hit, individuals_ids, 5.0, program)

        assert result is None
        # DB should never be queried
        mock_individual_cls.all_objects.filter.assert_not_called()

    # Branch 2: score is below the threshold
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
    def test_returns_none_when_score_below_threshold(self, mock_individual_cls: MagicMock) -> None:
        hit = self._make_hit(hit_id="id-a", score=3.0)
        program = self._make_program()
        individuals_ids = ["id-a"]

        result = _resolve_individual_hit(hit, individuals_ids, 5.0, program)

        assert result is None
        mock_individual_cls.all_objects.filter.assert_not_called()

    # Branch 3: individual not found in the database
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
    def test_returns_none_when_individual_not_in_db(self, mock_individual_cls: MagicMock) -> None:
        hit = self._make_hit(hit_id="id-a", score=10.0)
        program = self._make_program()
        individuals_ids = ["id-a"]
        mock_individual_cls.all_objects.filter.return_value.first.return_value = None

        result = _resolve_individual_hit(hit, individuals_ids, 5.0, program)

        assert result is None
        mock_individual_cls.all_objects.filter.assert_called_once_with(id="id-a")

    # Branch 4: individual program_id does not match program.id
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
    def test_returns_none_when_program_id_mismatch(self, mock_individual_cls: MagicMock) -> None:
        hit = self._make_hit(hit_id="id-a", score=10.0)
        program = self._make_program(program_id="program-1")
        individuals_ids = ["id-a"]

        db_individual = MagicMock()
        db_individual.program_id = "different-program"
        mock_individual_cls.all_objects.filter.return_value.first.return_value = db_individual

        result = _resolve_individual_hit(hit, individuals_ids, 5.0, program)

        assert result is None

    # Branch 5 (success): all checks pass, return the individual
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
    def test_returns_individual_on_success(self, mock_individual_cls: MagicMock) -> None:
        program_id = "program-1"
        hit = self._make_hit(hit_id="id-a", score=10.0)
        program = self._make_program(program_id=program_id)
        individuals_ids = ["id-a"]

        db_individual = MagicMock()
        db_individual.program_id = program_id
        mock_individual_cls.all_objects.filter.return_value.first.return_value = db_individual

        result = _resolve_individual_hit(hit, individuals_ids, 5.0, program)

        assert result is db_individual

    # Extra edge case: empty individuals_ids list skips the membership check
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.Individual")
    def test_empty_individuals_ids_skips_membership_check(self, mock_individual_cls: MagicMock) -> None:
        """When individuals_ids is an empty list (falsy), the first guard is skipped."""
        program_id = "program-1"
        hit = self._make_hit(hit_id="id-a", score=10.0)
        program = self._make_program(program_id=program_id)

        db_individual = MagicMock()
        db_individual.program_id = program_id
        mock_individual_cls.all_objects.filter.return_value.first.return_value = db_individual

        result = _resolve_individual_hit(hit, [], 5.0, program)

        assert result is db_individual


# ---------------------------------------------------------------------------
# _save_tickets_and_notify
# ---------------------------------------------------------------------------


class TestSaveTicketsAndNotify:
    """Tests for _save_tickets_and_notify."""

    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.TicketSystemFlaggingDetails")
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.GrievanceNotification")
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.GrievanceTicket")
    def test_bulk_creates_and_notifies(
        self,
        mock_grievance_ticket_cls: MagicMock,
        mock_notification_cls: MagicMock,
        mock_details_cls: MagicMock,
    ) -> None:
        ticket_1 = MagicMock(name="ticket_1")
        ticket_2 = MagicMock(name="ticket_2")
        tickets_to_create = [ticket_1, ticket_2]

        program_through_1 = MagicMock(name="through_1")
        program_through_2 = MagicMock(name="through_2")
        tickets_programs = [program_through_1, program_through_2]

        detail_1 = MagicMock(name="detail_1")
        detail_2 = MagicMock(name="detail_2")
        ticket_details_to_create = [detail_1, detail_2]

        # Set up the through model mock
        mock_through = MagicMock()
        mock_grievance_ticket_cls.programs.through = mock_through

        # Set up notification mocks - each call returns a list of notifications
        notif_1 = MagicMock(name="notif_1")
        notif_2 = MagicMock(name="notif_2")
        mock_notification_cls.prepare_notification_for_ticket_creation.side_effect = [
            [notif_1],
            [notif_2],
        ]

        _save_tickets_and_notify(tickets_to_create, tickets_programs, ticket_details_to_create)

        # Verify GrievanceTicket bulk_create
        mock_grievance_ticket_cls.objects.bulk_create.assert_called_once_with(tickets_to_create)

        # Verify through model bulk_create for program associations
        mock_through.objects.bulk_create.assert_called_once_with(tickets_programs)

        # Verify TicketSystemFlaggingDetails bulk_create
        mock_details_cls.objects.bulk_create.assert_called_once_with(ticket_details_to_create)

        # Verify notifications prepared and sent for each ticket
        assert mock_notification_cls.prepare_notification_for_ticket_creation.call_count == 2
        mock_notification_cls.prepare_notification_for_ticket_creation.assert_any_call(ticket_1)
        mock_notification_cls.prepare_notification_for_ticket_creation.assert_any_call(ticket_2)

        assert mock_notification_cls.send_all_notifications.call_count == 2
        mock_notification_cls.send_all_notifications.assert_any_call([notif_1])
        mock_notification_cls.send_all_notifications.assert_any_call([notif_2])

    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.TicketSystemFlaggingDetails")
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.GrievanceNotification")
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.GrievanceTicket")
    def test_empty_lists(
        self,
        mock_grievance_ticket_cls: MagicMock,
        mock_notification_cls: MagicMock,
        mock_details_cls: MagicMock,
    ) -> None:
        """When called with empty lists, bulk_create is still called but no notifications are sent."""
        mock_through = MagicMock()
        mock_grievance_ticket_cls.programs.through = mock_through

        _save_tickets_and_notify([], [], [])

        mock_grievance_ticket_cls.objects.bulk_create.assert_called_once_with([])
        mock_through.objects.bulk_create.assert_called_once_with([])
        mock_details_cls.objects.bulk_create.assert_called_once_with([])
        mock_notification_cls.prepare_notification_for_ticket_creation.assert_not_called()
        mock_notification_cls.send_all_notifications.assert_not_called()

    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.TicketSystemFlaggingDetails")
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.GrievanceNotification")
    @patch("hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge.GrievanceTicket")
    def test_notification_order(
        self,
        mock_grievance_ticket_cls: MagicMock,
        mock_notification_cls: MagicMock,
        mock_details_cls: MagicMock,
    ) -> None:
        """Notifications are sent in the order of tickets_to_create, and details bulk_create happens after."""
        mock_through = MagicMock()
        mock_grievance_ticket_cls.programs.through = mock_through

        call_order = []
        mock_notification_cls.prepare_notification_for_ticket_creation.return_value = []
        mock_notification_cls.send_all_notifications.side_effect = lambda x: call_order.append("notify")
        mock_details_cls.objects.bulk_create.side_effect = lambda x: call_order.append("details_bulk")

        ticket = MagicMock(name="ticket")
        _save_tickets_and_notify([ticket], [MagicMock()], [MagicMock()])

        # Notifications should be sent before details are bulk-created
        assert call_order == ["notify", "details_bulk"]
