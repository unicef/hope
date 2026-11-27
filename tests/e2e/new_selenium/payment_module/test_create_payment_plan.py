import datetime as dt

import pytest

from extras.test_utils.factories import CurrencyFactory
from extras.test_utils.selenium import HopeTestBrowser, ui_date
from hope.models import Currency, PaymentPlan, Program, Rule

from .conftest import PAYMENT_PLANS_PROGRAM_NAME, TARGET_POPULATION_NAME

pytestmark = pytest.mark.django_db()

PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
STATUS = 'div[data-cy="status-container"]'
SAVE = 'button[data-cy="button-save-payment-plan"]'
TARGET_POPULATION = 'div[data-cy="input-target-population"]'
CURRENCY = 'div[data-cy="input-currency"]'
DISPERSION_START_DATE = 'div[data-cy="input-dispersion-start-date"]'
DISPERSION_END_DATE = 'div[data-cy="input-dispersion-end-date"]'
SUBMIT = 'button[data-cy="button-submit"]'
LOCK = 'button[data-cy="button-lock-plan"]'


@pytest.fixture
def afn_currency() -> Currency:
    return CurrencyFactory(code="AFN", name="Afghan afghani")


def open_new_payment_plan_form(browser: HopeTestBrowser, program: Program) -> None:
    browser.select_global_program(PAYMENT_PLANS_PROGRAM_NAME)
    browser.open_nav_section("Payment Module")
    browser.click('a[data-cy="nav-Programme Cycles"]')
    cycle = program.cycles.get()
    browser.assert_text("Draft", 'td[data-cy="program-cycle-status"]')
    browser.click_link(cycle.title)
    browser.wait_for_element_clickable('a[data-cy="button-create-payment-plan"]').click()
    browser.wait_for_text("New Payment Plan", PAGE_HEADER_TITLE)


def submit_action(browser: HopeTestBrowser, button: str, message: str, status: str) -> None:
    browser.wait_for_element_clickable(button).click()
    browser.wait_for_element_clickable(SUBMIT).click()
    browser.wait_for_text(message)
    browser.wait_for_text(status, STATUS)


def test_new_payment_plan_form_shows_fields(login: HopeTestBrowser, payment_plans_program: Program) -> None:
    open_new_payment_plan_form(login, payment_plans_program)

    login.assert_text("SAVE", SAVE)
    login.assert_text("Target Population", TARGET_POPULATION)
    login.assert_text("Currency", CURRENCY)
    # MUI renders the required-field asterisk after a thin space (U+2009).
    login.assert_text("Dispersion Start Date *", DISPERSION_START_DATE)
    login.assert_text("Dispersion End Date *", DISPERSION_END_DATE)


def test_saving_empty_payment_plan_form_shows_required_errors(
    login: HopeTestBrowser,
    draft_target_population: PaymentPlan,
) -> None:
    open_new_payment_plan_form(login, draft_target_population.program_cycle.program)

    login.click(SAVE)

    login.wait_for_text("Target Population is required", TARGET_POPULATION)
    login.assert_text("Dispersion Start Date is required", DISPERSION_START_DATE)
    login.assert_text("Dispersion End Date is required", DISPERSION_END_DATE)
    login.assert_text("Currency is required", CURRENCY)
    assert PaymentPlan.objects.get(pk=draft_target_population.pk).status == PaymentPlan.Status.DRAFT


def test_create_payment_plan_and_take_it_to_accepted(
    login: HopeTestBrowser,
    draft_target_population: PaymentPlan,
    household_size_entitlement_rule: Rule,
    afn_currency: Currency,
) -> None:
    start_date = dt.date.today() + dt.timedelta(days=1)
    end_date = start_date + dt.timedelta(days=30)
    open_new_payment_plan_form(login, draft_target_population.program_cycle.program)

    login.click(TARGET_POPULATION)
    login.select_listbox_element(TARGET_POPULATION_NAME)
    login.click(CURRENCY)
    login.select_listbox_element("Afghan afghani")
    login.fill_date('input[name="dispersionStartDate"]', start_date.isoformat())
    login.fill_date('input[name="dispersionEndDate"]', end_date.isoformat())
    login.click(SAVE)

    login.wait_for_text("OPEN", STATUS)
    login.assert_text("AFN", 'div[data-cy="label-Currency"]')
    login.assert_text(ui_date(start_date), 'div[data-cy="label-Dispersion Start Date"]')
    login.assert_text(ui_date(end_date), 'div[data-cy="label-Dispersion End Date"]')

    submit_action(login, LOCK, "Payment Plan has been locked.", "LOCKED")
    login.wait_for_element_clickable('div[data-cy="input-entitlement-formula"]').click()
    login.select_listbox_element(household_size_entitlement_rule.name)
    login.wait_for_element_clickable('button[data-cy="button-apply-steficon"]').click()
    login.wait_for_text("Formula is executing, please wait until completed")
    login.wait_for_text("60 AFN", '[data-cy="total-entitled-quantity-usd"]')  # 3 households x size 2 x 10
    login.wait_for_text("LOCK FSP", f"{LOCK}:enabled")
    submit_action(login, LOCK, "Payment Plan FSPs are locked.", "LOCKED FSP")
    login.wait_for_element_clickable('button[data-cy="button-send-for-approval"]').click()
    login.wait_for_text("Payment Plan has been sent for approval.")
    login.wait_for_text("IN APPROVAL", STATUS)
    submit_action(login, 'button[data-cy="button-approve"]', "Payment Plan has been approved.", "IN AUTHORIZATION")
    submit_action(login, 'button[data-cy="button-authorize"]', "Payment Plan has been authorized", "IN REVIEW")
    submit_action(
        login, 'button[data-cy="button-mark-as-released"]', "Payment Plan has been marked as released.", "ACCEPTED"
    )

    payment_plan = PaymentPlan.objects.get(pk=draft_target_population.pk)
    assert payment_plan.status == PaymentPlan.Status.ACCEPTED
    assert payment_plan.currency == afn_currency
    assert (payment_plan.dispersion_start_date, payment_plan.dispersion_end_date) == (start_date, end_date)
    assert payment_plan.steficon_rule.rule == household_size_entitlement_rule
    assert not payment_plan.eligible_payments.filter(entitlement_quantity__isnull=True).exists()
