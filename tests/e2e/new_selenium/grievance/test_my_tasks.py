from datetime import datetime, timedelta
from urllib.parse import urlsplit

from dateutil.relativedelta import relativedelta
from django.utils import timezone
import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import BeneficiaryGroupFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.constants import PRESET_MINE, PRESET_NEEDS_ASSIGNMENT
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.utils import my_tasks_url
from hope.models import BusinessArea, Program, User

pytestmark = pytest.mark.django_db()

# --- My Tasks ------------------------------------------------------------------------
#
# The My Tasks page has two tabs: Needs Assignment (unassigned, active) and Assigned To Me. The
# daily digest emails deep-link into them with ?tab=, ?sensitive= and ?overdue=. Every fixture
# below is one ticket placed on exactly one side of one of those axes, so each test can list a
# handful and state which of them must show.


def _ticket(
    program: Program,
    *,
    category: int,
    issue_type: int,
    assigned_to: User | None = None,
    status: int = GrievanceTicket.STATUS_NEW,
    age: timedelta | None = None,
) -> GrievanceTicket:
    """One ticket in ``program``, optionally backdated by ``age`` so it counts as overdue.

    ``created_at`` is ``auto_now_add`` and the live server runs in its own thread, so the
    backdate is a queryset update rather than freezegun. ``unicef_id`` comes from a DB trigger.
    """
    ticket = GrievanceTicketFactory(
        business_area=program.business_area,
        category=category,
        issue_type=issue_type,
        assigned_to=assigned_to,
        status=status,
    )
    ticket.programs.set([program])
    if age is not None:
        GrievanceTicket.objects.filter(pk=ticket.pk).update(created_at=timezone.now() - age)
    ticket.refresh_from_db()
    return ticket


def _complaint(program: Program, **kwargs: object) -> GrievanceTicket:
    return _ticket(
        program,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_FSP_COMPLAINT,
        **kwargs,
    )


def _sensitive(program: Program, **kwargs: object) -> GrievanceTicket:
    return _ticket(
        program,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        **kwargs,
    )


@pytest.fixture
def my_tasks_program(business_area: BusinessArea) -> Program:
    """Active, so the all-programmes list (``is_active_program=true``) includes its tickets."""
    beneficiary_group = BeneficiaryGroupFactory(
        name="My Tasks Household Group",
        group_label="Household",
        group_label_plural="Households",
        member_label="Individual",
        member_label_plural="Individuals",
        master_detail=True,
    )
    return ProgramFactory(
        name="My Tasks Program",
        status=Program.ACTIVE,
        business_area=business_area,
        beneficiary_group=beneficiary_group,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )


@pytest.fixture
def other_user() -> User:
    return UserFactory()


@pytest.fixture
def unassigned_complaint(my_tasks_program: Program) -> GrievanceTicket:
    return _complaint(my_tasks_program)


@pytest.fixture
def unassigned_sensitive(my_tasks_program: Program) -> GrievanceTicket:
    return _sensitive(my_tasks_program)


@pytest.fixture
def unassigned_closed(my_tasks_program: Program) -> GrievanceTicket:
    """Closed without ever being assigned - Needs Assignment must never offer it."""
    return _complaint(my_tasks_program, status=GrievanceTicket.STATUS_CLOSED)


@pytest.fixture
def unassigned_in_other_program(business_area: BusinessArea) -> GrievanceTicket:
    """An unassigned ticket in a second active programme.

    The all-programmes page lists it; the programme-scoped page must not.
    """
    other_program = ProgramFactory(
        name="Other My Tasks Program",
        status=Program.ACTIVE,
        business_area=business_area,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )
    return _complaint(other_program)


@pytest.fixture
def my_complaint(my_tasks_program: Program, me: User) -> GrievanceTicket:
    return _complaint(my_tasks_program, assigned_to=me, status=GrievanceTicket.STATUS_ASSIGNED)


@pytest.fixture
def my_sensitive(my_tasks_program: Program, me: User) -> GrievanceTicket:
    return _sensitive(my_tasks_program, assigned_to=me, status=GrievanceTicket.STATUS_ASSIGNED)


@pytest.fixture
def my_closed(my_tasks_program: Program, me: User) -> GrievanceTicket:
    """Hidden by the default "Active Tickets" status filter."""
    return _complaint(my_tasks_program, assigned_to=me, status=GrievanceTicket.STATUS_CLOSED)


@pytest.fixture
def my_overdue_complaint(my_tasks_program: Program, me: User) -> GrievanceTicket:
    """Past the 30-day default threshold for non-sensitive tickets."""
    return _complaint(
        my_tasks_program,
        assigned_to=me,
        status=GrievanceTicket.STATUS_ASSIGNED,
        age=timedelta(days=40),
    )


@pytest.fixture
def my_recent_sensitive_overdue(my_tasks_program: Program, me: User) -> GrievanceTicket:
    """Past the 1-day sensitive threshold but well inside the 30-day one.

    Only listed as overdue if the filter applies the threshold of the ticket's own category.
    """
    return _sensitive(
        my_tasks_program,
        assigned_to=me,
        status=GrievanceTicket.STATUS_ASSIGNED,
        age=timedelta(days=2),
    )


@pytest.fixture
def someone_elses_complaint(my_tasks_program: Program, other_user: User) -> GrievanceTicket:
    return _complaint(my_tasks_program, assigned_to=other_user, status=GrievanceTicket.STATUS_ASSIGNED)


@pytest.fixture
def restricted_user_complaint(my_tasks_program: Program, user_with_no_permissions: User) -> GrievanceTicket:
    """Assigned to the user who holds only the non-sensitive grant."""
    return _complaint(my_tasks_program, assigned_to=user_with_no_permissions, status=GrievanceTicket.STATUS_ASSIGNED)


@pytest.fixture
def restricted_user_sensitive(my_tasks_program: Program, user_with_no_permissions: User) -> GrievanceTicket:
    """Assigned to the same user, who must never see it."""
    return _sensitive(my_tasks_program, assigned_to=user_with_no_permissions, status=GrievanceTicket.STATUS_ASSIGNED)


PAGE_TITLE = 'h5[data-cy="page-header-title"]'
TAB_NEEDS_ASSIGNMENT = '[data-cy="tab-needs-assignment"]'
TAB_MINE = '[data-cy="tab-mine"]'
FILTER_SENSITIVE = 'div[data-cy="filters-sensitive"]'
FILTER_CATEGORY = 'div[data-cy="filters-category"]'
FILTER_ISSUE_TYPE = 'div[data-cy="filters-issue-type"]'
FILTER_STATUS = 'div[data-cy="filters-active-tickets"]'
FILTER_OVERDUE = 'div[data-cy="filters-overdue"]'
BUTTON_APPLY = 'button[data-cy="button-filters-apply"]'
BUTTON_BULK_CLOSE = 'button[data-cy="button-close tickets"]'
BUTTON_BULK_ASSIGN = 'button[data-cy="button-Assign"]'
BUTTON_CLEAR = 'button[data-cy="button-filters-clear"]'
PAGINATION = '[data-cy="table-pagination"]'
DATA_ROWS = 'tbody tr[role="checkbox"]'


def _open(browser: HopeTestBrowser, business_area: BusinessArea, query: str = "") -> None:
    browser.open(f"/{business_area.slug}/programs/all/grievance/my-tasks{query}")
    browser.wait_for_text("My Tasks", PAGE_TITLE, timeout=60)


def _open_email_link(browser: HopeTestBrowser, url: str) -> None:
    """Open the exact URL the digest email carries, minus the host the live server replaces."""
    parts = urlsplit(url)
    browser.open(f"{parts.path}?{parts.query}")
    browser.wait_for_text("My Tasks", PAGE_TITLE, timeout=60)


def _wait_for_rows(browser: HopeTestBrowser, *tickets: GrievanceTicket) -> None:
    """Wait until the list holds exactly ``tickets``.

    The rows of the previous query stay on screen while the next one loads, so the pagination
    count - refetched with every query - is what says the new page has arrived. MUI writes it
    with an en dash.
    """
    browser.wait_for_text(f"1–{len(tickets)} of {len(tickets)}", PAGINATION)
    for ticket in tickets:
        browser.assert_text(ticket.unicef_id, "tbody")


def _pick_filter(browser: HopeTestBrowser, selector: str, option: str) -> None:
    browser.click(selector)
    browser.select_listbox_element(option)


def _apply(browser: HopeTestBrowser) -> None:
    browser.click(BUTTON_APPLY)


def _tick(browser: HopeTestBrowser, ticket: GrievanceTicket) -> None:
    """Select a row. MUI renders the native checkbox with opacity 0, hence js_click."""
    browser.js_click(f'[data-cy="ticket-row-{ticket.unicef_id}"] input[type="checkbox"]')


# --- Navigation ----------------------------------------------------------------------


@pytest.mark.usefixtures("unassigned_complaint")
def test_my_tasks_button_opens_the_page_from_the_ticket_list(
    login: HopeTestBrowser, business_area: BusinessArea
) -> None:
    login.open(f"/{business_area.slug}/programs/all/grievance/tickets/user-generated")
    login.wait_for_text("Grievance Tickets", PAGE_TITLE, timeout=60)

    login.click('button[data-cy="button-my-tasks"]')

    login.wait_for_text("My Tasks", PAGE_TITLE)
    login.wait_for_text("My Tasks", '[data-cy="table-title"]')
    # A bare /my-tasks gets its tab written into the URL, so the page is shareable as opened.
    login.assert_true("tab=needs-assignment" in login.get_current_url())
    login.assert_element(f'{TAB_NEEDS_ASSIGNMENT}[aria-selected="true"]')


# --- Needs Assignment ----------------------------------------------------------------


@pytest.mark.usefixtures("unassigned_closed", "my_complaint")
def test_needs_assignment_lists_only_unassigned_active_tickets(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    unassigned_complaint: GrievanceTicket,
    unassigned_sensitive: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=needs-assignment")

    _wait_for_rows(login, unassigned_complaint, unassigned_sensitive)


@pytest.mark.usefixtures("unassigned_complaint", "my_complaint")
def test_needs_assignment_hides_status_filter_and_bulk_close(
    login: HopeTestBrowser, business_area: BusinessArea
) -> None:
    _open(login, business_area, "?tab=needs-assignment")
    login.wait_for_element_visible(FILTER_OVERDUE)

    # Every ticket here is unassigned and active: no status to choose, nothing closable.
    login.assert_element_absent(FILTER_STATUS)
    login.assert_element_absent(BUTTON_BULK_CLOSE)

    login.click(TAB_MINE)

    login.wait_for_element_visible(FILTER_STATUS)
    login.wait_for_element_visible(BUTTON_BULK_CLOSE)


# --- Assigned To Me ------------------------------------------------------------------


@pytest.mark.usefixtures("my_closed", "someone_elses_complaint", "unassigned_complaint")
def test_assigned_to_me_lists_only_my_active_tickets(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    my_complaint: GrievanceTicket,
    my_sensitive: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=mine")

    _wait_for_rows(login, my_complaint, my_sensitive)


def test_assigned_to_me_all_tickets_includes_closed(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    my_complaint: GrievanceTicket,
    my_closed: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=mine")
    _wait_for_rows(login, my_complaint)

    _pick_filter(login, FILTER_STATUS, "All Tickets")
    _apply(login)

    _wait_for_rows(login, my_complaint, my_closed)


# --- Sensitivity filter --------------------------------------------------------------


def test_sensitive_filter_lists_only_sensitive_tickets(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    my_complaint: GrievanceTicket,
    my_sensitive: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=mine")
    _wait_for_rows(login, my_complaint, my_sensitive)

    _pick_filter(login, FILTER_SENSITIVE, "Sensitive")

    # The category is settled, so its select gives way to the sensitive issue types.
    login.wait_for_element_visible(FILTER_ISSUE_TYPE)
    login.assert_element_absent(FILTER_CATEGORY)

    _apply(login)

    _wait_for_rows(login, my_sensitive)


def test_other_filter_excludes_sensitive_tickets(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    my_complaint: GrievanceTicket,
    my_sensitive: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=mine")
    _wait_for_rows(login, my_complaint, my_sensitive)

    _pick_filter(login, FILTER_SENSITIVE, "Other")
    _apply(login)

    _wait_for_rows(login, my_complaint)
    login.assert_element_visible(FILTER_CATEGORY)


# --- Overdue filter ------------------------------------------------------------------


def test_overdue_filter_uses_the_per_category_threshold(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    my_complaint: GrievanceTicket,
    my_overdue_complaint: GrievanceTicket,
    my_recent_sensitive_overdue: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=mine")
    _wait_for_rows(login, my_complaint, my_overdue_complaint, my_recent_sensitive_overdue)

    _pick_filter(login, FILTER_OVERDUE, "Overdue Only")
    _apply(login)

    # Two days is overdue for a sensitive ticket and not for a complaint.
    _wait_for_rows(login, my_overdue_complaint, my_recent_sensitive_overdue)


def test_list_is_ordered_by_total_days_descending(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    my_complaint: GrievanceTicket,
    my_overdue_complaint: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=mine")
    _wait_for_rows(login, my_complaint, my_overdue_complaint)

    login.assert_text(my_overdue_complaint.unicef_id, f"{DATA_ROWS}:first-child")


@pytest.mark.usefixtures("my_complaint")
def test_my_tasks_uses_the_narrow_column_set(login: HopeTestBrowser, business_area: BusinessArea) -> None:
    _open(login, business_area, "?tab=mine")
    login.wait_for_element_visible('th[data-cy="totalDays"]')

    # Across every programme the list gains a Programmes column, whatever the page asked for.
    login.assert_element_visible('th[data-cy="programs"]')
    # Each tab already pins the assignee and the status, so those columns carry nothing.
    login.assert_element_absent('th[data-cy="status"]')
    login.assert_element_absent('th[data-cy="assignedTo"]')


@pytest.mark.usefixtures("unassigned_in_other_program")
def test_program_scoped_page_lists_only_that_programs_tickets(
    login: HopeTestBrowser,
    my_tasks_program: Program,
    unassigned_complaint: GrievanceTicket,
) -> None:
    # Where the ticket list's My Tasks button lands while a programme is selected: a different
    # endpoint from the all-programmes page, with the tab's pinned params on top of the programme.
    login.open(f"/{my_tasks_program.business_area.slug}/programs/{my_tasks_program.code}/grievance/my-tasks")
    login.wait_for_text("My Tasks", PAGE_TITLE, timeout=60)

    _wait_for_rows(login, unassigned_complaint)
    login.assert_element_absent('th[data-cy="programs"]')


# --- Email deep links ----------------------------------------------------------------


@pytest.mark.usefixtures("my_sensitive", "my_overdue_complaint")
def test_email_deep_link_lands_on_mine_overdue_sensitive(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    my_recent_sensitive_overdue: GrievanceTicket,
) -> None:
    _open_email_link(login, my_tasks_url(business_area, PRESET_MINE, overdue=True, sensitive=True))

    login.assert_element(f'{TAB_MINE}[aria-selected="true"]')
    login.assert_text("Overdue Only", FILTER_OVERDUE)
    login.assert_text("Sensitive", FILTER_SENSITIVE)
    login.assert_element_absent(FILTER_CATEGORY)
    _wait_for_rows(login, my_recent_sensitive_overdue)


@pytest.mark.usefixtures("unassigned_sensitive", "my_complaint")
def test_needs_assignment_deep_link_selects_the_tab(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    unassigned_complaint: GrievanceTicket,
) -> None:
    _open_email_link(login, my_tasks_url(business_area, PRESET_NEEDS_ASSIGNMENT, sensitive=False))

    login.assert_element(f'{TAB_NEEDS_ASSIGNMENT}[aria-selected="true"]')
    login.assert_text("Other", FILTER_SENSITIVE)
    _wait_for_rows(login, unassigned_complaint)


# --- Cross-tab state -----------------------------------------------------------------


@pytest.mark.usefixtures("unassigned_complaint")
def test_tab_switch_clears_category_but_keeps_overdue(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    my_overdue_complaint: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=mine&overdue=true")
    _wait_for_rows(login, my_overdue_complaint)

    _pick_filter(login, FILTER_CATEGORY, "Grievance Complaint")
    _apply(login)
    _wait_for_rows(login, my_overdue_complaint)
    login.assert_true("category=" in login.get_current_url())

    login.click(TAB_NEEDS_ASSIGNMENT)
    login.wait_for_element_visible(f'{TAB_NEEDS_ASSIGNMENT}[aria-selected="true"]')

    # The category belonged to the previous tab's list; the overdue narrowing is the reader's own.
    url = login.get_current_url()
    login.assert_true("tab=needs-assignment" in url)
    login.assert_true("overdue=true" in url)
    login.assert_true("category=" not in url)
    login.assert_text("Overdue Only", FILTER_OVERDUE)
    login.assert_text_not_visible("Grievance Complaint", FILTER_CATEGORY)


@pytest.mark.usefixtures("unassigned_complaint")
def test_clear_filters_drops_overdue_and_sensitive(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    my_complaint: GrievanceTicket,
    my_recent_sensitive_overdue: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=mine&overdue=true&sensitive=true")
    _wait_for_rows(login, my_recent_sensitive_overdue)

    login.click(BUTTON_CLEAR)

    # Overdue has to clear to "unset", not to false - `overdue=false` would be its own filter.
    _wait_for_rows(login, my_complaint, my_recent_sensitive_overdue)
    login.assert_text("All Tickets", FILTER_OVERDUE)
    login.assert_text("All Categories", FILTER_SENSITIVE)
    url = login.get_current_url()
    login.assert_true("tab=mine" in url)
    login.assert_true("overdue=" not in url)
    login.assert_true("sensitive=" not in url)


# --- Bulk actions --------------------------------------------------------------------


@pytest.mark.usefixtures("unassigned_sensitive")
def test_bulk_assign_moves_the_ticket_to_assigned_to_me(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    me: User,
    unassigned_complaint: GrievanceTicket,
    unassigned_sensitive: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=needs-assignment")
    _wait_for_rows(login, unassigned_complaint, unassigned_sensitive)

    _tick(login, unassigned_complaint)
    login.wait_for_element_clickable(BUTTON_BULK_ASSIGN).click()
    login.wait_for_text(unassigned_complaint.unicef_id, '[data-cy="selected-tickets"]')
    login.click('[data-cy="dropdown"] [data-cy="assigned-to-dropdown"] input')
    login.select_listbox_element(me.email)
    login.click('button[data-cy="button-save"]')

    # The tab lists unassigned tickets only, so the assigned one leaves it...
    _wait_for_rows(login, unassigned_sensitive)
    # ...and turns up on the other tab, now carrying the assignee.
    login.click(TAB_MINE)
    _wait_for_rows(login, unassigned_complaint)
    unassigned_complaint.refresh_from_db()
    assert str(unassigned_complaint.assigned_to_id) == str(me.id)


@pytest.mark.usefixtures("unassigned_complaint")
def test_selection_is_dropped_when_the_query_changes(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    my_complaint: GrievanceTicket,
) -> None:
    _open(login, business_area, "?tab=mine")
    _wait_for_rows(login, my_complaint)

    _tick(login, my_complaint)
    login.wait_for_element_clickable(BUTTON_BULK_ASSIGN)

    login.click(TAB_NEEDS_ASSIGNMENT)

    # A ticket ticked on the previous list is no longer on screen and must not ride along into
    # the next bulk action, so the action goes back to having nothing to act on.
    login.wait_for_element_visible(f'{TAB_NEEDS_ASSIGNMENT}[aria-selected="true"]')
    login.wait_for_element_present(f"{BUTTON_BULK_ASSIGN}[disabled]")


# --- Permissions ---------------------------------------------------------------------


@pytest.mark.usefixtures("restricted_user_sensitive")
def test_user_without_assign_permission_only_gets_assigned_to_me(
    browser: HopeTestBrowser,
    business_area: BusinessArea,
    user_with_no_permissions: User,
    restricted_user_complaint: GrievanceTicket,
) -> None:
    # The programme grant is what the app shell needs to list programmes at all; without it the
    # global 403 handler replaces every page.
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
    ):
        browser.login(username="noperm_user", password="testtest2", wait_for_drawer=False)
        _open(browser, business_area)

        browser.wait_for_element_visible(TAB_MINE)
        browser.assert_element_absent(TAB_NEEDS_ASSIGNMENT)
        # Holding only the non-sensitive grant leaves nothing to choose, so the filter is gone
        # and the sensitive ticket with it.
        browser.assert_element_absent(FILTER_SENSITIVE)
        _wait_for_rows(browser, restricted_user_complaint)


def test_user_with_no_my_tasks_permissions_is_denied(
    browser: HopeTestBrowser,
    business_area: BusinessArea,
    user_with_no_permissions: User,
) -> None:
    # A user who can open the app but holds neither My Tasks grant. (With no permissions at all the
    # page never leaves its loading state, and without the programme grant the shell itself 403s.)
    with grant_permission(user_with_no_permissions, business_area, Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS):
        browser.login(username="noperm_user", password="testtest2", wait_for_drawer=False)
        browser.open(f"/{business_area.slug}/programs/all/grievance/my-tasks")

        browser.wait_for_text("Permission Denied", timeout=60)
