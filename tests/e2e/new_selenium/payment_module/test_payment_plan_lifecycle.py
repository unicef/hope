import datetime

import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories import CurrencyFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import Approval, BusinessArea, PaymentPlan, PaymentPlanGroup, PaymentPlanSplit, User

pytestmark = pytest.mark.django_db()

GROUP_STATUS = 'div[data-cy="group-status"]'
PLAN_STATUS = 'div[data-cy="status-container"]'
COMMENT_INPUT = 'textarea[data-cy="input-comment"]'
DIALOG_SUBMIT = '[role="dialog"] button[data-cy="button-submit"]'
REJECT = 'button[data-cy="button-reject"]'
ABORT = 'button[data-cy="button-abort"]'
ABORT_SUBMIT = 'button[data-cy="button-submit-abort"]'
REACTIVATE = 'button[data-cy="button-reactivate-payment-plan-group"]'
SPLIT = 'button[data-cy="button-split-group"]'
SPLIT_TYPE = 'div[data-cy="select-splitType"]'
SPLIT_PAYMENTS_NO = 'input[name="paymentsNo"]'
SPLIT_SUBMIT = 'button[data-cy="button-split"]'
EDIT = 'button[data-cy="button-edit-group-name"]'
CURRENCY_INPUT = 'div[data-cy="input-group-currency"] input'
DELETE = 'button[data-cy="button-delete-pp"]'
DELETE_SUBMIT = 'button[data-cy="button-submit"]'
GROUP_VIEW_PERMISSIONS = (
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.PM_VIEW_LIST,
    Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
)
# The plan page also loads the plan's group.
PLAN_VIEW_PERMISSIONS = (
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.PM_VIEW_LIST,
    Permissions.PM_VIEW_DETAILS,
    Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
)
REJECT_COMMENT = "Wrong entitlements, please recheck"
ABORT_COMMENT = "Funds are no longer available"


def open_group_as(browser: HopeTestBrowser, group: PaymentPlanGroup, status: str) -> None:
    program = group.cycle.program
    browser.login(username="noperm_user")
    browser.open(f"/{program.business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}")
    browser.wait_for_text(status, GROUP_STATUS)


def open_payment_plan_as(browser: HopeTestBrowser, payment_plan: PaymentPlan, status: str) -> None:
    browser.login(username="noperm_user")
    browser.open(
        f"/{payment_plan.business_area.slug}/programs/{payment_plan.program.code}"
        f"/payment-module/payment-plans/{payment_plan.id}"
    )
    browser.wait_for_text(status, PLAN_STATUS)


@pytest.mark.parametrize(
    ("group_fixture", "status", "permission"),
    [
        pytest.param("in_approval_group", "IN APPROVAL", Permissions.PM_ACCEPTANCE_PROCESS_APPROVE, id="approval"),
        pytest.param(
            "in_authorization_group",
            "IN AUTHORIZATION",
            Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            id="authorization",
        ),
    ],
)
def test_reject_payment_plan_group(
    request: pytest.FixtureRequest,
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    group_fixture: str,
    status: str,
    permission: Permissions,
) -> None:
    group = request.getfixturevalue(group_fixture)
    with grant_permission(user_with_no_permissions, business_area, *GROUP_VIEW_PERMISSIONS, permission):
        open_group_as(browser, group, status)
        browser.wait_for_element_clickable(REJECT).click()
        browser.set_value(COMMENT_INPUT, REJECT_COMMENT)
        browser.wait_for_element_clickable(DIALOG_SUBMIT).click()
        browser.wait_for_text("Payment Plan has been rejected.")
        browser.wait_for_text("LOCKED", GROUP_STATUS)

    group.refresh_from_db()
    assert group.status == PaymentPlanGroup.Status.LOCKED
    assert group.payment_plans.get().status == PaymentPlan.Status.LOCKED_FSP
    approvals = Approval.objects.filter(approval_process__payment_plan_group=group)
    assert list(approvals.values_list("type", "comment", "created_by")) == [
        (Approval.REJECT, REJECT_COMMENT, user_with_no_permissions.pk)
    ]


def test_abort_payment_plan_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    locked_lifecycle_group: PaymentPlanGroup,
) -> None:
    group = locked_lifecycle_group
    with grant_permission(user_with_no_permissions, business_area, *GROUP_VIEW_PERMISSIONS, Permissions.PM_ABORT):
        open_group_as(browser, group, "LOCKED")
        browser.wait_for_element_clickable(ABORT).click()
        browser.set_value(COMMENT_INPUT, ABORT_COMMENT)
        browser.wait_for_element_clickable(ABORT_SUBMIT).click()
        browser.wait_for_text("Payment Plan has been aborted.")
        browser.wait_for_text("ABORTED", GROUP_STATUS)

    group.refresh_from_db()
    payment_plan = group.payment_plans.get()
    assert group.status == PaymentPlanGroup.Status.ABORTED
    assert group.abort_comment == ABORT_COMMENT
    assert payment_plan.status == PaymentPlan.Status.ABORTED
    assert payment_plan.abort_comment == ABORT_COMMENT


def test_reactivate_aborted_payment_plan_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    aborted_targeted_group: PaymentPlanGroup,
) -> None:
    group = aborted_targeted_group
    payment_plan = group.payment_plans.get()
    payment_ids = set(payment_plan.payment_items.values_list("id", flat=True))
    with grant_permission(
        user_with_no_permissions, business_area, *GROUP_VIEW_PERMISSIONS, Permissions.PM_REACTIVATE_ABORT
    ):
        open_group_as(browser, group, "ABORTED")
        browser.wait_for_element_clickable(REACTIVATE).click()
        browser.wait_for_text("Payment Plan has been reactivated.")
        browser.wait_for_text("OPEN", GROUP_STATUS)

    group.refresh_from_db()
    payment_plan.refresh_from_db()
    assert group.status == PaymentPlanGroup.Status.OPEN
    assert payment_plan.status == PaymentPlan.Status.OPEN
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
    assert payment_plan.background_action_status is None
    assert set(payment_plan.payment_items.values_list("id", flat=True)) == payment_ids
    assert len(payment_ids) == 3
    assert not payment_plan.payment_items.filter(entitlement_quantity__isnull=False).exists()


def test_split_payment_plan_group_by_records(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    accepted_lifecycle_group: PaymentPlanGroup,
) -> None:
    group = accepted_lifecycle_group
    with grant_permission(user_with_no_permissions, business_area, *GROUP_VIEW_PERMISSIONS, Permissions.PM_SPLIT):
        open_group_as(browser, group, "ACCEPTED")
        browser.wait_for_element_clickable(SPLIT).click()
        browser.wait_for_element_clickable(SPLIT_TYPE).click()
        browser.select_listbox_element("By Records")
        browser.set_value(SPLIT_PAYMENTS_NO, "10")
        browser.wait_for_element_clickable(SPLIT_SUBMIT).click()
        browser.wait_for_text("Split was successful!")

    payment_plan = group.payment_plans.get()
    splits = payment_plan.splits.order_by("order")
    assert [split.split_payment_items.count() for split in splits] == [10, 10, 5]
    assert {split.split_type for split in splits} == {PaymentPlanSplit.SplitType.BY_RECORDS}
    assert not payment_plan.eligible_payments.filter(parent_split__isnull=True).exists()


def test_split_payment_plan_group_by_collector(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    accepted_shared_collectors_group: PaymentPlanGroup,
) -> None:
    group = accepted_shared_collectors_group
    with grant_permission(user_with_no_permissions, business_area, *GROUP_VIEW_PERMISSIONS, Permissions.PM_SPLIT):
        open_group_as(browser, group, "ACCEPTED")
        browser.wait_for_element_clickable(SPLIT).click()
        browser.wait_for_element_clickable(SPLIT_TYPE).click()
        browser.select_listbox_element("By Collector")
        browser.wait_for_element_clickable(SPLIT_SUBMIT).click()
        browser.wait_for_text("Split was successful!")

    splits = group.payment_plans.get().splits.all()
    assert splits.count() == 3
    for split in splits:
        assert split.split_type == PaymentPlanSplit.SplitType.BY_COLLECTOR
        assert split.split_payment_items.values("collector").distinct().count() == 1
        assert split.split_payment_items.count() == 4


def test_edit_payment_plan_group_settings(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    open_lifecycle_group: PaymentPlanGroup,
) -> None:
    group = open_lifecycle_group
    CurrencyFactory(code="PLN", name="Polish Zloty")
    start_date = datetime.date.today() + datetime.timedelta(days=10)
    end_date = start_date + datetime.timedelta(days=20)
    with grant_permission(
        user_with_no_permissions,
        business_area,
        *GROUP_VIEW_PERMISSIONS,
        Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE,
    ):
        open_group_as(browser, group, "OPEN")
        browser.wait_for_element_clickable(EDIT).click()
        browser.fill_date('input[name="dispersionStartDate"]', start_date.isoformat())
        browser.fill_date('input[name="dispersionEndDate"]', end_date.isoformat())
        browser.set_value(CURRENCY_INPUT, "Polish")
        browser.select_listbox_element("Polish złoty")
        browser.wait_for_element_clickable(DIALOG_SUBMIT).click()
        browser.wait_for_text("Payment Plan updated")

    group.refresh_from_db()
    assert group.dispersion_start_date == start_date
    assert group.dispersion_end_date == end_date
    assert group.currency.code == "PLN"


def test_delete_payment_plan_from_open_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    open_payment_plan: PaymentPlan,
) -> None:
    payment_plan = open_payment_plan
    with grant_permission(user_with_no_permissions, business_area, *PLAN_VIEW_PERMISSIONS, Permissions.PM_CREATE):
        open_payment_plan_as(browser, payment_plan, "OPEN")
        browser.wait_for_element_clickable(DELETE).click()
        browser.wait_for_element_clickable(DELETE_SUBMIT).click()
        browser.wait_for_text("Payment Plan Component Deleted")

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.DRAFT
    assert payment_plan.payment_items.count() == 3


@pytest.mark.parametrize(
    ("group_fixture", "status", "permission", "button"),
    [
        pytest.param(
            "in_approval_group",
            "IN APPROVAL",
            Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
            REJECT,
            id="reject-at-approval",
        ),
        pytest.param(
            "in_authorization_group",
            "IN AUTHORIZATION",
            Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            REJECT,
            id="reject-at-authorization",
        ),
        pytest.param("locked_lifecycle_group", "LOCKED", Permissions.PM_ABORT, ABORT, id="abort"),
        pytest.param(
            "aborted_targeted_group",
            "ABORTED",
            Permissions.PM_REACTIVATE_ABORT,
            REACTIVATE,
            id="reactivate",
        ),
        pytest.param("accepted_lifecycle_group", "ACCEPTED", Permissions.PM_SPLIT, SPLIT, id="split"),
        pytest.param("open_lifecycle_group", "OPEN", Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE, EDIT, id="edit"),
    ],
)
def test_group_lifecycle_action_shown_with_permission(
    request: pytest.FixtureRequest,
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    group_fixture: str,
    status: str,
    permission: Permissions,
    button: str,
) -> None:
    group = request.getfixturevalue(group_fixture)
    with grant_permission(user_with_no_permissions, business_area, *GROUP_VIEW_PERMISSIONS, permission):
        open_group_as(browser, group, status)
        browser.wait_for_element_present(button)


@pytest.mark.parametrize(
    ("group_fixture", "status", "button"),
    [
        pytest.param("in_approval_group", "IN APPROVAL", REJECT, id="reject-at-approval"),
        pytest.param("in_authorization_group", "IN AUTHORIZATION", REJECT, id="reject-at-authorization"),
        pytest.param("locked_lifecycle_group", "LOCKED", ABORT, id="abort"),
        pytest.param("aborted_targeted_group", "ABORTED", REACTIVATE, id="reactivate"),
        pytest.param("accepted_lifecycle_group", "ACCEPTED", SPLIT, id="split"),
        pytest.param("open_lifecycle_group", "OPEN", EDIT, id="edit"),
    ],
)
def test_group_lifecycle_action_hidden_without_permission(
    request: pytest.FixtureRequest,
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    group_fixture: str,
    status: str,
    button: str,
) -> None:
    group = request.getfixturevalue(group_fixture)
    with grant_permission(user_with_no_permissions, business_area, *GROUP_VIEW_PERMISSIONS):
        open_group_as(browser, group, status)
        browser.assert_elements_absent(button)


def test_delete_payment_plan_hidden_without_permission(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    open_payment_plan: PaymentPlan,
) -> None:
    with grant_permission(user_with_no_permissions, business_area, *PLAN_VIEW_PERMISSIONS):
        open_payment_plan_as(browser, open_payment_plan, "OPEN")
        browser.assert_elements_absent(DELETE)
