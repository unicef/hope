import pytest

from extras.test_utils.factories import (
    ApprovalProcessFactory,
    CurrencyFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
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
SELECT_APPROVAL = 'span[data-cy="select-approval"]'
APPROVE_BUTTON = 'button[data-cy="approve-button"]'
COMMENT_APPROVE = 'div[data-cy="comment-approve"] textarea'
PROGRAM_SELECT_AUTHORIZATION = 'div[data-cy="program-select-authorization"]'
SELECT_ALL_AUTHORIZATION = 'span[data-cy="select-all-authorization"]'
AUTHORIZE_BUTTON = 'button[data-cy="authorize-button"]'
COLUMN_FIELD_RELEASE = 'td[data-cy="column-field-release"]'
SELECT_ALL_RELEASE = 'span[data-cy="select-all-release"]'
RELEASE_BUTTON = 'button[data-cy="release-button"]'
COLUMN_FIELD_RELEASED = 'td[data-cy="column-field-released"]'
BUTTON_SAVE = 'button[data-cy="button-save"]'
DIALOG = 'div[role="dialog"]'

PROGRAM_NAME = "Managerial Console Programme"
APPROVE_COMMENT = "Approved from the managerial console"


def _in_approval_payment_plan(program: Program, **kwargs) -> PaymentPlan:
    payment_plan = PaymentPlanFactory(
        business_area=program.business_area,
        program_cycle=ProgramCycleFactory(program=program),
        status=PaymentPlan.Status.IN_APPROVAL,
        plan_type=PaymentPlan.PlanType.REGULAR,
        currency=CurrencyFactory(code="USD", name="United States Dollar"),
        **kwargs,
    )
    ApprovalProcessFactory(payment_plan=payment_plan)
    return payment_plan


@pytest.fixture
def payment_plan(business_area: BusinessArea) -> PaymentPlan:
    program = ProgramFactory(name=PROGRAM_NAME, status=Program.ACTIVE, business_area=business_area)
    return _in_approval_payment_plan(program, name="Managerial Console Plan")


@pytest.fixture
def other_program_payment_plan(business_area: BusinessArea) -> PaymentPlan:
    program = ProgramFactory(name="Other Programme", status=Program.ACTIVE, business_area=business_area)
    return _in_approval_payment_plan(program)


def open_managerial_console(browser: HopeTestBrowser) -> None:
    browser.wait_for_element_clickable(NAV_MANAGERIAL_CONSOLE).click()
    browser.assert_text("Managerial Console", PAGE_HEADER_TITLE)


def filter_by_program(browser: HopeTestBrowser, program_select: str, program_name: str) -> None:
    browser.click(program_select)
    browser.select_listbox_element(program_name, LISTBOX)


def save_dialog(browser: HopeTestBrowser) -> None:
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
    other_program_payment_plan: PaymentPlan,
    login: HopeTestBrowser,
) -> None:
    open_managerial_console(login)

    filter_by_program(login, PROGRAM_SELECT_APPROVAL, PROGRAM_NAME)
    login.assert_element_not_visible(f'td:contains("{other_program_payment_plan.unicef_id}")')
    login.click(SELECT_APPROVAL)
    login.click(APPROVE_BUTTON)
    login.type(COMMENT_APPROVE, APPROVE_COMMENT)
    save_dialog(login)

    filter_by_program(login, PROGRAM_SELECT_AUTHORIZATION, PROGRAM_NAME)
    login.check_checkbox(SELECT_ALL_AUTHORIZATION)
    login.click(AUTHORIZE_BUTTON)
    save_dialog(login)

    login.assert_text(payment_plan.unicef_id, COLUMN_FIELD_RELEASE)
    login.check_checkbox(SELECT_ALL_RELEASE)
    login.click(RELEASE_BUTTON)
    save_dialog(login)

    login.assert_text(payment_plan.unicef_id, COLUMN_FIELD_RELEASED)
    payment_plan.refresh_from_db()
    other_program_payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.ACCEPTED
    assert other_program_payment_plan.status == PaymentPlan.Status.IN_APPROVAL
    approvals = Approval.objects.filter(approval_process__payment_plan=payment_plan).order_by("created_at")
    assert list(approvals.values_list("type", "comment")) == [
        (Approval.APPROVAL, APPROVE_COMMENT),
        (Approval.AUTHORIZATION, ""),
        (Approval.FINANCE_RELEASE, ""),
    ]
