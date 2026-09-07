"""E2E coverage for the Needs Adjudication Tickets Management screen.

The screen keeps every adjudication decision in React session state and only posts it
on Finalize (`bulk-needs-adjudication`). The role handover required before an individual
holding HEAD or PRIMARY can be withdrawn is derived client-side, while the backend
re-validates it at close time — so a mismatch between the two only shows up end to end.
"""

import pytest

from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from extras.test_utils.factories.household import HouseholdFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import ROLE_PRIMARY
from hope.models import Individual, IndividualRoleInHousehold, Program

from .conftest import NaScenario

pytestmark = pytest.mark.django_db()


def _open_ticket(browser: HopeTestBrowser, program: Program, scenario: NaScenario) -> None:
    # Program-scoped, not `programs/all`: the reassign modal's individual lookup reads
    # the selected program from the program context.
    browser.open(f"/{program.business_area.slug}/programs/{program.code}/grievance/na-tickets-management")
    browser.wait_for_text("NA Tickets Management", 'h5[data-cy="page-header-title"]', timeout=60)
    browser.click(f'[data-cy="na-ticket-list-item-{scenario.ticket.unicef_id}"]')
    browser.wait_for_element_visible('[data-cy="na-comparison-table"]')


def _withdraw_person2(browser: HopeTestBrowser) -> None:
    browser.click('button[data-cy="button-na-withdraw-person2"]')
    browser.wait_for_text("Tickets managed: 1", '[data-cy="na-tickets-managed-count"]')


def _reassign_role(browser: HopeTestBrowser, role: str, replacement: Individual) -> None:
    browser.click(f'button[data-cy="button-na-reassign-{role}"]')
    # The row radio carries the individual id as its aria-label, so the replacement can
    # be picked without filtering the lookup table first. MUI renders the native input
    # with opacity 0, which Selenium treats as not visible, hence js_click.
    radio = f'input[aria-label="{replacement.id}"]'
    browser.wait_for_element_present(radio)
    browser.js_click(radio)
    browser.click('[data-cy="input-identityVerified"]')
    # SAVE stays disabled until both the radio and the identity checkbox are set.
    browser.wait_for_element_absent('button[data-cy="button-na-reassign-save"][disabled]')
    browser.click('button[data-cy="button-na-reassign-save"]')
    browser.wait_for_element_absent('button[data-cy="button-na-reassign-save"]')


def _finalize(browser: HopeTestBrowser) -> None:
    browser.click('button[data-cy="button-na-finalize"]')
    browser.wait_for_element_visible('button[data-cy="button-confirm"]').click()
    # Session decisions are cleared only after the bulk request succeeds.
    browser.wait_for_text("Tickets managed: 0", '[data-cy="na-tickets-managed-count"]', timeout=60)


@pytest.fixture
def na_ticket_closed(na_program: Program) -> GrievanceTicket:
    """An already adjudicated ticket, which the list must not offer again."""
    golden = HouseholdFactory(
        program=na_program, business_area=na_program.business_area, create_role=False
    ).head_of_household
    duplicate = HouseholdFactory(
        program=na_program, business_area=na_program.business_area, create_role=False
    ).head_of_household
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        status=GrievanceTicket.STATUS_CLOSED,
        business_area=na_program.business_area,
        consent=True,
    )
    grievance.programs.set([na_program])
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=golden,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    ticket_details.possible_duplicates.add(duplicate)
    return grievance


def test_na_management_lists_only_the_selected_program_tickets(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_plain: NaScenario,
    na_ticket_in_other_program: GrievanceTicket,
) -> None:
    login.open(f"/{na_program.business_area.slug}/programs/{na_program.code}/grievance/na-tickets-management")
    login.wait_for_text("NA Tickets Management", 'h5[data-cy="page-header-title"]', timeout=60)
    login.wait_for_element_visible(f'[data-cy="na-ticket-list-item-{na_ticket_plain.ticket.unicef_id}"]')

    login.assert_element_absent(f'[data-cy="na-ticket-list-item-{na_ticket_in_other_program.unicef_id}"]')


def test_na_management_does_not_list_a_closed_ticket(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_plain: NaScenario,
    na_ticket_closed: GrievanceTicket,
) -> None:
    login.open(f"/{na_program.business_area.slug}/programs/{na_program.code}/grievance/na-tickets-management")
    login.wait_for_text("NA Tickets Management", 'h5[data-cy="page-header-title"]', timeout=60)
    login.wait_for_element_visible(f'[data-cy="na-ticket-list-item-{na_ticket_plain.ticket.unicef_id}"]')

    login.assert_element_absent(f'[data-cy="na-ticket-list-item-{na_ticket_closed.unicef_id}"]')


def test_na_management_lists_ticket_and_renders_comparison(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_plain: NaScenario,
) -> None:
    _open_ticket(login, na_program, na_ticket_plain)

    login.assert_text("Karimi", '[data-cy="na-comparison-row-Last Name"]')
    login.assert_text("Ahmadzai", '[data-cy="na-comparison-row-Last Name"]')
    login.assert_text("Zahra", '[data-cy="na-comparison-row-First Name"]')
    login.assert_text("Farid", '[data-cy="na-comparison-row-First Name"]')
    # Address is rendered only when the two values differ — the two live in different villages.
    login.assert_text("Kandahar", '[data-cy="na-comparison-row-Address"]')
    login.assert_text("Herat", '[data-cy="na-comparison-row-Address"]')
    # Similarity comes from the ticket's extra_data, not from the individuals.
    login.assert_text("8.5", '[data-cy="na-comparison-table"]')


def test_na_withdrawing_a_person_marks_the_ticket_managed_and_finalizes(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_plain: NaScenario,
) -> None:
    _open_ticket(login, na_program, na_ticket_plain)

    _withdraw_person2(login)

    login.assert_text("Ticket managed", '[data-cy="na-ticket-managed-label"]')
    # Neither individual holds a blocking role, so nothing stands in the way of Finalize.
    login.assert_element_absent('[data-cy="na-reassign-section"]')

    _finalize(login)

    ticket = na_ticket_plain.ticket
    ticket.refresh_from_db()
    assert ticket.status == GrievanceTicket.STATUS_CLOSED
    details = na_ticket_plain.ticket_details
    assert list(details.selected_individuals.all()) == [na_ticket_plain.person2]
    assert list(details.selected_distinct.all()) == [na_ticket_plain.person1]
    na_ticket_plain.person2.refresh_from_db()
    na_ticket_plain.person1.refresh_from_db()
    assert na_ticket_plain.person2.duplicate is True
    assert na_ticket_plain.person1.duplicate is False


def test_na_clear_drops_the_decision(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_plain: NaScenario,
) -> None:
    _open_ticket(login, na_program, na_ticket_plain)

    _withdraw_person2(login)
    login.click('button[data-cy="button-na-clear"]')

    # Clearing the only mark removes the ticket from the session decisions entirely,
    # so there is nothing left to finalize.
    login.wait_for_text("Tickets managed: 0", '[data-cy="na-tickets-managed-count"]')
    login.assert_element_absent('[data-cy="na-ticket-managed-label"]')
    login.assert_element_present('button[data-cy="button-na-finalize"][disabled]')

    na_ticket_plain.ticket.refresh_from_db()
    assert na_ticket_plain.ticket.status == GrievanceTicket.STATUS_NEW


def test_na_not_duplicates_marks_both_individuals_distinct(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_plain: NaScenario,
) -> None:
    _open_ticket(login, na_program, na_ticket_plain)

    login.click('button[data-cy="button-na-not-duplicates"]')
    login.wait_for_text("Tickets managed: 1", '[data-cy="na-tickets-managed-count"]')

    _finalize(login)

    details = na_ticket_plain.ticket_details
    assert not details.selected_individuals.exists()
    assert set(details.selected_distinct.all()) == {na_ticket_plain.person1, na_ticket_plain.person2}
    na_ticket_plain.person2.refresh_from_db()
    assert na_ticket_plain.person2.duplicate is False


def test_na_finalize_is_blocked_until_every_duplicate_is_decided(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_two_duplicates: NaScenario,
) -> None:
    """Finalize stays disabled while any compared pair is still unmarked, and unlocks once all are."""
    _open_ticket(login, na_program, na_ticket_two_duplicates)

    _withdraw_person2(login)

    login.assert_text("1 of 2 decided", '[data-cy="na-duplicate-selector"]')
    login.assert_text("Decision incomplete", '[data-cy="na-ticket-decision-incomplete"]')
    login.assert_element_present('button[data-cy="button-na-finalize"][disabled]')

    login.click('button[data-cy="button-na-duplicate-next"]')
    login.click('button[data-cy="button-na-withdraw-person2"]')

    login.wait_for_element_absent('button[data-cy="button-na-finalize"][disabled]')
    login.assert_element_absent('[data-cy="na-ticket-decision-incomplete"]')


def test_na_finalize_skips_a_ticket_closed_while_the_operator_was_deciding(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_plain: NaScenario,
) -> None:
    _open_ticket(login, na_program, na_ticket_plain)

    _withdraw_person2(login)

    ticket = na_ticket_plain.ticket
    ticket.status = GrievanceTicket.STATUS_CLOSED
    ticket.save(update_fields=["status"])

    login.click('button[data-cy="button-na-finalize"]')
    login.wait_for_element_visible('button[data-cy="button-confirm"]').click()

    login.wait_for_text("Tickets managed: 0", '[data-cy="na-tickets-managed-count"]', timeout=60)
    login.assert_text(f"Closed by someone else in the meantime and skipped: {ticket.unicef_id}")


def test_na_withdrawing_a_head_of_household_requires_reassignment(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_head: NaScenario,
) -> None:
    _open_ticket(login, na_program, na_ticket_head)

    _withdraw_person2(login)

    household = na_ticket_head.household
    login.assert_element_present('[data-cy="na-reassign-section"]')
    login.assert_text("Not reassigned", f'[data-cy="na-reassign-row-HEAD-{household.unicef_id}"]')
    login.assert_text("Reassignment required", '[data-cy="na-ticket-reassignment-required"]')
    login.assert_element_present('button[data-cy="button-na-finalize"][disabled]')

    _reassign_role(login, "HEAD", na_ticket_head.replacement)

    login.assert_text(
        na_ticket_head.replacement.full_name,
        f'[data-cy="na-reassign-row-HEAD-{household.unicef_id}"]',
    )
    login.assert_element_absent('[data-cy="na-ticket-reassignment-required"]')

    _finalize(login)

    household.refresh_from_db()
    assert household.head_of_household == na_ticket_head.replacement
    assert not household.withdrawn
    na_ticket_head.ticket.refresh_from_db()
    assert na_ticket_head.ticket.status == GrievanceTicket.STATUS_CLOSED
    na_ticket_head.person2.refresh_from_db()
    assert na_ticket_head.person2.duplicate is True


def test_na_withdrawing_a_primary_collector_requires_reassignment(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_primary: NaScenario,
) -> None:
    _open_ticket(login, na_program, na_ticket_primary)

    _withdraw_person2(login)

    household = na_ticket_primary.household
    login.assert_text("Not reassigned", f'[data-cy="na-reassign-row-PRIMARY-{household.unicef_id}"]')
    # Person 2 is not the head, so only the collector role is up for reassignment.
    login.assert_element_absent(f'[data-cy="na-reassign-row-HEAD-{household.unicef_id}"]')
    login.assert_element_present('button[data-cy="button-na-finalize"][disabled]')

    _reassign_role(login, "PRIMARY", na_ticket_primary.replacement)
    _finalize(login)

    primary_roles = IndividualRoleInHousehold.objects.filter(household=household, role=ROLE_PRIMARY)
    assert primary_roles.count() == 1
    assert primary_roles.first().individual == na_ticket_primary.replacement
    na_ticket_primary.ticket.refresh_from_db()
    assert na_ticket_primary.ticket.status == GrievanceTicket.STATUS_CLOSED


def test_na_withdrawing_an_alternate_collector_needs_no_reassignment(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_alternate: NaScenario,
) -> None:
    _open_ticket(login, na_program, na_ticket_alternate)

    _withdraw_person2(login)

    # ALTERNATE never leaves a household without a head or a collector, so it must not
    # block the operator.
    login.assert_element_absent('[data-cy="na-reassign-section"]')
    login.assert_element_absent('[data-cy="na-ticket-reassignment-required"]')

    _finalize(login)

    household = na_ticket_alternate.household
    household.refresh_from_db()
    assert household.head_of_household == na_ticket_alternate.replacement
    primary_role = IndividualRoleInHousehold.objects.get(household=household, role=ROLE_PRIMARY)
    assert primary_role.individual == na_ticket_alternate.replacement
    na_ticket_alternate.ticket.refresh_from_db()
    assert na_ticket_alternate.ticket.status == GrievanceTicket.STATUS_CLOSED


def test_na_reassign_picker_offers_only_individuals_from_the_ticket_program(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_primary: NaScenario,
    individual_in_other_program: Individual,
) -> None:
    _open_ticket(login, na_program, na_ticket_primary)

    _withdraw_person2(login)
    login.click('button[data-cy="button-na-reassign-PRIMARY"]')

    login.wait_for_element_present(f'input[aria-label="{na_ticket_primary.replacement.id}"]')

    login.assert_element_absent(f'input[aria-label="{individual_in_other_program.id}"]')


def test_na_reassign_picker_offers_only_individuals_from_the_ticket_program_in_all_programmes(
    login: HopeTestBrowser,
    na_program: Program,
    na_ticket_primary: NaScenario,
    individual_in_other_program: Individual,
) -> None:
    login.open(f"/{na_program.business_area.slug}/programs/all/grievance/na-tickets-management")
    login.wait_for_text("NA Tickets Management", 'h5[data-cy="page-header-title"]', timeout=60)
    login.click(f'[data-cy="na-ticket-list-item-{na_ticket_primary.ticket.unicef_id}"]')
    login.wait_for_element_visible('[data-cy="na-comparison-table"]')

    _withdraw_person2(login)
    login.click('button[data-cy="button-na-reassign-PRIMARY"]')

    login.wait_for_element_present(f'input[aria-label="{na_ticket_primary.replacement.id}"]')

    login.assert_element_absent(f'input[aria-label="{individual_in_other_program.id}"]')
