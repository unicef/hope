import pytest

from extras.test_utils.factories import (
    ApprovalProcessFactory,
    CurrencyFactory,
    PaymentPlanFactory,
    ProgramFactory,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Approval, BusinessArea, PaymentPlan, Program

pytestmark = pytest.mark.django_db()

NAV_MANAGERIAL_CONSOLE = 'a[data-cy="nav-Managerial Console"]'
PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
SECTION_TITLE = 'h6[data-cy="title"]'
LISTBOX = 'ul[role="listbox"]'
PROGRAM_SELECT_APPROVAL = 'div[data-cy="program-select-approval"]'
SELECT_ALL_APPROVAL = 'span[data-cy="select-all-approval"]'
APPROVE_BUTTON = 'button[data-cy="approve-button"]'
COMMENT_APPROVE = 'div[data-cy="comment-approve"] textarea'
PROGRAM_SELECT_AUTHORIZATION = 'div[data-cy="program-select-authorization"]'
COLUMN_FIELD_AUTHORIZATION = 'td[data-cy="column-field-authorization"]'
SELECT_AUTHORIZATION = 'span[data-cy="select-authorization"]'
SELECT_ALL_AUTHORIZATION = 'span[data-cy="select-all-authorization"]'
AUTHORIZE_BUTTON = 'button[data-cy="authorize-button"]'
PROGRAM_SELECT_RELEASE = 'div[data-cy="program-select-release"]'
COLUMN_FIELD_RELEASE = 'td[data-cy="column-field-release"]'
SELECT_ALL_RELEASE = 'span[data-cy="select-all-release"]'
RELEASE_BUTTON = 'button[data-cy="release-button"]'
SEARCH_RELEASED = 'div[data-cy="search-released"] input'
COLUMN_FIELD_RELEASED = 'td[data-cy="column-field-released"]'
PLANS_IDS = 'span[data-cy="plans-ids"]'
BUTTON_SAVE = 'button[data-cy="button-save"]'
DIALOG = 'div[role="dialog"]'

PROGRAM_NAME = "Managerial Console Programme"
OTHER_PROGRAM_NAME = "Other Programme"
APPROVE_COMMENT = "Approved from the managerial console"


def _payment_plan(program: Program, status: PaymentPlan.Status, **kwargs) -> PaymentPlan:
    payment_plan = PaymentPlanFactory(
        business_area=program.business_area,
        program_cycle=program.cycles.first(),
        status=status,
        plan_type=PaymentPlan.PlanType.REGULAR,
        currency=CurrencyFactory(code="USD", name="United States Dollar"),
        **kwargs,
    )
    ApprovalProcessFactory(payment_plan=payment_plan)
    return payment_plan


@pytest.fixture
def payment_plan(business_area: BusinessArea) -> PaymentPlan:
    program = ProgramFactory(name=PROGRAM_NAME, status=Program.ACTIVE, business_area=business_area)
    return _payment_plan(program, PaymentPlan.Status.IN_APPROVAL, name="Managerial Console Plan")


@pytest.fixture
def plan_in_authorization(business_area: BusinessArea) -> PaymentPlan:
    program = ProgramFactory(name=PROGRAM_NAME, status=Program.ACTIVE, business_area=business_area)
    return _payment_plan(program, PaymentPlan.Status.IN_AUTHORIZATION)


@pytest.fixture
def released_plan(business_area: BusinessArea) -> PaymentPlan:
    program = ProgramFactory(name=PROGRAM_NAME, status=Program.ACTIVE, business_area=business_area)
    return _payment_plan(program, PaymentPlan.Status.ACCEPTED)


@pytest.fixture
def other_released_plan(other_program: Program) -> PaymentPlan:
    return _payment_plan(other_program, PaymentPlan.Status.ACCEPTED)


@pytest.fixture
def other_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(name=OTHER_PROGRAM_NAME, status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def other_plan_in_approval(other_program: Program) -> PaymentPlan:
    return _payment_plan(other_program, PaymentPlan.Status.IN_APPROVAL)


@pytest.fixture
def other_plan_in_authorization(other_program: Program) -> PaymentPlan:
    return _payment_plan(other_program, PaymentPlan.Status.IN_AUTHORIZATION)


@pytest.fixture
def other_plan_in_review(other_program: Program) -> PaymentPlan:
    return _payment_plan(other_program, PaymentPlan.Status.IN_REVIEW)


def open_managerial_console(browser: HopeTestBrowser) -> None:
    browser.wait_for_element_clickable(NAV_MANAGERIAL_CONSOLE).click()
    browser.assert_text("Managerial Console", PAGE_HEADER_TITLE)


def filter_by_program(browser: HopeTestBrowser, program_select: str, program_name: str) -> None:
    browser.click(program_select)
    browser.select_listbox_element(program_name, LISTBOX)


def save_dialog(browser: HopeTestBrowser, *plans: PaymentPlan) -> None:
    browser.assert_exact_text(", ".join(plan.unicef_id for plan in plans), PLANS_IDS)
    browser.click(BUTTON_SAVE)
    browser.wait_for_element_absent(DIALOG)


def test_managerial_console_renders_all_sections(login: HopeTestBrowser) -> None:
    open_managerial_console(login)

    login.assert_elements_visible(
        f'{SECTION_TITLE}:contains("Payment Plans pending for Approval")',
        f'{SECTION_TITLE}:contains("Payment Plans pending for Authorization")',
        f'{SECTION_TITLE}:contains("Payment Plans pending for Release")',
        f'{SECTION_TITLE}:contains("Released Payment Plans")',
    )


def test_managerial_console_approve_authorize_and_release_payment_plan(
    payment_plan: PaymentPlan,
    other_plan_in_approval: PaymentPlan,
    other_plan_in_authorization: PaymentPlan,
    other_plan_in_review: PaymentPlan,
    login: HopeTestBrowser,
) -> None:
    open_managerial_console(login)

    filter_by_program(login, PROGRAM_SELECT_APPROVAL, PROGRAM_NAME)
    login.assert_element_not_visible(f'td:contains("{other_plan_in_approval.unicef_id}")')
    login.check_checkbox(SELECT_ALL_APPROVAL)
    login.click(APPROVE_BUTTON)
    login.type(COMMENT_APPROVE, APPROVE_COMMENT)
    save_dialog(login, payment_plan)

    login.assert_element(f'{COLUMN_FIELD_AUTHORIZATION}:contains("{payment_plan.unicef_id}")')
    filter_by_program(login, PROGRAM_SELECT_AUTHORIZATION, PROGRAM_NAME)
    login.assert_element_not_visible(f'td:contains("{other_plan_in_authorization.unicef_id}")')
    login.check_checkbox(SELECT_ALL_AUTHORIZATION)
    login.click(AUTHORIZE_BUTTON)
    save_dialog(login, payment_plan)

    login.assert_element(f'{COLUMN_FIELD_RELEASE}:contains("{payment_plan.unicef_id}")')
    filter_by_program(login, PROGRAM_SELECT_RELEASE, PROGRAM_NAME)
    login.assert_element_not_visible(f'td:contains("{other_plan_in_review.unicef_id}")')
    login.check_checkbox(SELECT_ALL_RELEASE)
    login.click(RELEASE_BUTTON)
    save_dialog(login, payment_plan)

    login.assert_text(payment_plan.unicef_id, COLUMN_FIELD_RELEASED)
    payment_plan.refresh_from_db()
    other_plan_in_approval.refresh_from_db()
    other_plan_in_authorization.refresh_from_db()
    other_plan_in_review.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.ACCEPTED
    assert other_plan_in_approval.status == PaymentPlan.Status.IN_APPROVAL
    assert other_plan_in_authorization.status == PaymentPlan.Status.IN_AUTHORIZATION
    assert other_plan_in_review.status == PaymentPlan.Status.IN_REVIEW
    approvals = Approval.objects.filter(approval_process__payment_plan=payment_plan).order_by("created_at")
    assert list(approvals.values_list("type", "comment")) == [
        (Approval.APPROVAL, APPROVE_COMMENT),
        (Approval.AUTHORIZATION, ""),
        (Approval.FINANCE_RELEASE, ""),
    ]


def test_managerial_console_filter_change_clears_selection(
    plan_in_authorization: PaymentPlan,
    other_plan_in_authorization: PaymentPlan,
    login: HopeTestBrowser,
) -> None:
    open_managerial_console(login)

    filter_by_program(login, PROGRAM_SELECT_AUTHORIZATION, PROGRAM_NAME)
    login.assert_element_not_visible(f'td:contains("{other_plan_in_authorization.unicef_id}")')
    login.check_checkbox(SELECT_AUTHORIZATION)
    login.assert_element(f"{AUTHORIZE_BUTTON}:enabled")

    filter_by_program(login, PROGRAM_SELECT_AUTHORIZATION, OTHER_PROGRAM_NAME)
    login.assert_text(other_plan_in_authorization.unicef_id, COLUMN_FIELD_AUTHORIZATION)
    login.assert_element(f"{AUTHORIZE_BUTTON}:disabled")

    filter_by_program(login, PROGRAM_SELECT_AUTHORIZATION, PROGRAM_NAME)
    login.assert_text(plan_in_authorization.unicef_id, COLUMN_FIELD_AUTHORIZATION)
    login.assert_element_not_present(f"{SELECT_AUTHORIZATION} input:checked")
    login.assert_element(f"{AUTHORIZE_BUTTON}:disabled")


def test_managerial_console_search_filters_released_plans(
    released_plan: PaymentPlan,
    other_released_plan: PaymentPlan,
    login: HopeTestBrowser,
) -> None:
    open_managerial_console(login)
    login.assert_element(f'{COLUMN_FIELD_RELEASED}:contains("{released_plan.unicef_id}")')
    login.assert_element(f'{COLUMN_FIELD_RELEASED}:contains("{other_released_plan.unicef_id}")')

    login.type(SEARCH_RELEASED, released_plan.unicef_id)
    login.assert_element_not_present(f'{COLUMN_FIELD_RELEASED}:contains("{other_released_plan.unicef_id}")')
    login.assert_text(released_plan.unicef_id, COLUMN_FIELD_RELEASED)
