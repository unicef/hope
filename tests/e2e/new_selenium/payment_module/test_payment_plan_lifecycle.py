import datetime

import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories import CurrencyFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import Approval, BusinessArea, PaymentPlan, PaymentPlanSplit, User

pytestmark = pytest.mark.django_db()

STATUS = 'div[data-cy="status-container"]'
COMMENT_INPUT = 'textarea[data-cy="input-comment"]'
REJECT = 'button[data-cy="button-reject"]'
REJECT_SUBMIT = 'button[data-cy="button-reject-submit"]'
ABORT = 'button[data-cy="button-abort"]'
ABORT_SUBMIT = 'button[data-cy="button-submit-abort"]'
REACTIVATE = 'button[data-cy="button-reactivate-payment-plan"]'
SPLIT = 'button[data-cy="button-split-payment-plan"]'
SPLIT_TYPE = 'div[data-cy="select-splitType"]'
SPLIT_PAYMENTS_NO = 'input[data-cy="input-paymentsNo"]'
SPLIT_SUBMIT = 'button[data-cy="button-split"]'
EDIT = 'a[data-cy="button-edit-payment-plan"]'
EDIT_SAVE = 'button[data-cy="button-save"]'
CURRENCY_INPUT = 'div[data-cy="input-currency"] input'
DELETE = 'button[data-cy="button-delete-pp"]'
DELETE_SUBMIT = 'button[data-cy="button-submit"]'
VIEW_PERMISSIONS = (
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.PM_VIEW_LIST,
    Permissions.PM_VIEW_DETAILS,
    Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
)
REJECT_COMMENT = "Wrong entitlements, please recheck"
ABORT_COMMENT = "Funds are no longer available"


def payment_plan_url(payment_plan: PaymentPlan) -> str:
    return (
        f"/{payment_plan.business_area.slug}/programs/{payment_plan.program.code}"
        f"/payment-module/payment-plans/{payment_plan.id}"
    )


def open_payment_plan_as(
    browser: HopeTestBrowser,
    payment_plan: PaymentPlan,
    status: str,
) -> None:
    browser.login(username="noperm_user")
    browser.open(payment_plan_url(payment_plan))
    browser.wait_for_text(status, STATUS)


@pytest.mark.parametrize(
    ("payment_plan_fixture", "status", "permission"),
    [
        pytest.param(
            "in_approval_payment_plan", "IN APPROVAL", Permissions.PM_ACCEPTANCE_PROCESS_APPROVE, id="approval"
        ),
        pytest.param(
            "in_authorization_payment_plan",
            "IN AUTHORIZATION",
            Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            id="authorization",
        ),
    ],
)
def test_reject_payment_plan(
    request: pytest.FixtureRequest,
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_fixture: str,
    status: str,
    permission: Permissions,
) -> None:
    payment_plan = request.getfixturevalue(payment_plan_fixture)
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, permission):
        open_payment_plan_as(browser, payment_plan, status)
        browser.wait_for_element_clickable(REJECT).click()
        browser.set_value(COMMENT_INPUT, REJECT_COMMENT)
        browser.wait_for_element_clickable(REJECT_SUBMIT).click()
        browser.wait_for_text("Payment Plan has been rejected.")
        browser.wait_for_text("LOCKED FSP", STATUS)

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.LOCKED_FSP
    approvals = Approval.objects.filter(approval_process__payment_plan=payment_plan)
    assert list(approvals.values_list("type", "comment", "created_by")) == [
        (Approval.REJECT, REJECT_COMMENT, user_with_no_permissions.pk)
    ]


def test_abort_payment_plan(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    locked_fsp_payment_plan: PaymentPlan,
) -> None:
    payment_plan = locked_fsp_payment_plan
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, Permissions.PM_ABORT):
        open_payment_plan_as(browser, payment_plan, "LOCKED FSP")
        browser.wait_for_element_clickable(ABORT).click()
        browser.set_value(COMMENT_INPUT, ABORT_COMMENT)
        browser.wait_for_element_clickable(ABORT_SUBMIT).click()
        browser.wait_for_text("Payment Plan has been aborted.")
        browser.wait_for_text("ABORTED", STATUS)

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.ABORTED
    assert payment_plan.abort_comment == ABORT_COMMENT


def test_reactivate_aborted_payment_plan(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    aborted_targeted_payment_plan: PaymentPlan,
) -> None:
    payment_plan = aborted_targeted_payment_plan
    old_payment_ids = set(payment_plan.payment_items.values_list("id", flat=True))
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, Permissions.PM_REACTIVATE_ABORT):
        open_payment_plan_as(browser, payment_plan, "ABORTED")
        browser.wait_for_element_clickable(REACTIVATE).click()
        browser.wait_for_text("Payment Plan has been reactivated.")
        browser.wait_for_text("OPEN", STATUS)

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.OPEN
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
    new_payment_ids = set(payment_plan.payment_items.values_list("id", flat=True))
    assert len(new_payment_ids) == 3
    assert new_payment_ids.isdisjoint(old_payment_ids)


def test_split_payment_plan_by_records(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    accepted_payment_plan: PaymentPlan,
) -> None:
    payment_plan = accepted_payment_plan
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, Permissions.PM_SPLIT):
        open_payment_plan_as(browser, payment_plan, "ACCEPTED")
        browser.wait_for_element_clickable(SPLIT).click()
        browser.wait_for_element_clickable(SPLIT_TYPE).click()
        browser.select_listbox_element("By Records")
        browser.set_value(SPLIT_PAYMENTS_NO, "10")
        browser.wait_for_element_clickable(SPLIT_SUBMIT).click()
        browser.wait_for_text("Split was successful!")

    splits = payment_plan.splits.order_by("order")
    assert [split.split_payment_items.count() for split in splits] == [10, 10, 5]
    assert {split.split_type for split in splits} == {PaymentPlanSplit.SplitType.BY_RECORDS}
    assert not payment_plan.eligible_payments.filter(parent_split__isnull=True).exists()


def test_split_payment_plan_by_collector(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    accepted_shared_collectors_payment_plan: PaymentPlan,
) -> None:
    payment_plan = accepted_shared_collectors_payment_plan
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, Permissions.PM_SPLIT):
        open_payment_plan_as(browser, payment_plan, "ACCEPTED")
        browser.wait_for_element_clickable(SPLIT).click()
        browser.wait_for_element_clickable(SPLIT_TYPE).click()
        browser.select_listbox_element("By Collector")
        browser.wait_for_element_clickable(SPLIT_SUBMIT).click()
        browser.wait_for_text("Split was successful!")

    splits = payment_plan.splits.all()
    assert splits.count() == 3
    for split in splits:
        assert split.split_type == PaymentPlanSplit.SplitType.BY_COLLECTOR
        assert split.split_payment_items.values("collector").distinct().count() == 1
        assert split.split_payment_items.count() == 4


def test_edit_payment_plan(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    open_payment_plan: PaymentPlan,
) -> None:
    payment_plan = open_payment_plan
    CurrencyFactory(code="PLN", name="Polish Zloty")
    start_date = datetime.date.today() + datetime.timedelta(days=10)
    end_date = start_date + datetime.timedelta(days=20)
    # The edit page also lists target populations and programme cycles; without these list permissions
    # the whole page shows Access Denied.
    with grant_permission(
        user_with_no_permissions,
        business_area,
        *VIEW_PERMISSIONS,
        Permissions.PM_CREATE,
        Permissions.TARGETING_VIEW_LIST,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
    ):
        open_payment_plan_as(browser, payment_plan, "OPEN")
        browser.wait_for_element_clickable(EDIT).click()
        browser.fill_date('input[name="dispersionStartDate"]', start_date.isoformat())
        browser.fill_date('input[name="dispersionEndDate"]', end_date.isoformat())
        browser.set_value(CURRENCY_INPUT, "Polish")
        browser.select_listbox_element("Polish złoty")
        browser.wait_for_element_clickable(EDIT_SAVE).click()
        browser.wait_for_text("Payment Plan Edited")
        browser.wait_for_text("OPEN", STATUS)

    payment_plan.refresh_from_db()
    assert payment_plan.dispersion_start_date == start_date
    assert payment_plan.dispersion_end_date == end_date
    assert payment_plan.currency.code == "PLN"


def test_delete_payment_plan(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    open_payment_plan: PaymentPlan,
) -> None:
    payment_plan = open_payment_plan
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, Permissions.PM_CREATE):
        open_payment_plan_as(browser, payment_plan, "OPEN")
        browser.wait_for_element_clickable(DELETE).click()
        browser.wait_for_element_clickable(DELETE_SUBMIT).click()
        browser.wait_for_text("Payment Plan Deleted")
        browser.wait_for_text("No results", 'tr[data-cy="table-row"]')

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.DRAFT
    assert payment_plan.payment_items.count() == 3


@pytest.mark.parametrize(
    ("payment_plan_fixture", "status", "permission", "with_permission", "without_permission"),
    [
        pytest.param(
            "in_approval_payment_plan",
            "IN APPROVAL",
            Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
            REJECT,
            None,
            id="reject-at-approval",
        ),
        pytest.param(
            "in_authorization_payment_plan",
            "IN AUTHORIZATION",
            Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            REJECT,
            None,
            id="reject-at-authorization",
        ),
        pytest.param("locked_fsp_payment_plan", "LOCKED FSP", Permissions.PM_ABORT, ABORT, None, id="abort"),
        pytest.param(
            "aborted_targeted_payment_plan",
            "ABORTED",
            Permissions.PM_REACTIVATE_ABORT,
            REACTIVATE,
            None,
            id="reactivate",
        ),
        pytest.param(
            "accepted_payment_plan",
            "ACCEPTED",
            Permissions.PM_SPLIT,
            f"{SPLIT}:enabled",
            f"{SPLIT}:disabled",
            id="split",
        ),
        pytest.param("open_payment_plan", "OPEN", Permissions.PM_CREATE, EDIT, None, id="edit"),
        pytest.param("open_payment_plan", "OPEN", Permissions.PM_CREATE, DELETE, None, id="delete"),
    ],
)
@pytest.mark.parametrize("granted", [True, False], ids=["granted", "not-granted"])
def test_lifecycle_actions_follow_permissions(
    request: pytest.FixtureRequest,
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_fixture: str,
    status: str,
    permission: Permissions,
    with_permission: str,
    without_permission: str | None,
    granted: bool,
) -> None:
    payment_plan = request.getfixturevalue(payment_plan_fixture)
    extra_permissions = (permission,) if granted else ()
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, *extra_permissions):
        open_payment_plan_as(browser, payment_plan, status)
        if granted:
            browser.wait_for_element_present(with_permission)
        elif without_permission:
            browser.wait_for_element_present(without_permission)
        else:
            browser.assert_elements_absent(with_permission)
