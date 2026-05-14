import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, PaymentPlanGroup, ProgramCycle, User

pytestmark = pytest.mark.django_db()


def test_create_payment_plan_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    program_cycle: ProgramCycle,
) -> None:
    program = program_cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
        Permissions.PM_PAYMENT_PLAN_GROUP_CREATE,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/program-cycles")

        browser.click('[data-cy="program-cycle-title"] a')
        browser.wait_for_element_clickable('[data-cy="button-create-payment-plan-group"]')
        browser.click('[data-cy="button-create-payment-plan-group"]')

        browser.wait_for_element_visible('input[name="groupName"]')
        browser.type('input[name="groupName"]', "E2E Test Group")
        browser.click('[data-cy="button-create-group-submit"]')
        browser.wait_for_text("Payment Plan Group created")

        browser.click('[data-cy="nav-Payment Module"]')
        browser.wait_for_element_clickable('a[data-cy="nav-Groups"]')
        browser.click('a[data-cy="nav-Groups"]')

        browser.wait_for_text("E2E Test Group")


def test_edit_payment_plan_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_group: PaymentPlanGroup,
) -> None:
    program = payment_plan_group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
        Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{payment_plan_group.id}")

        browser.wait_for_element_clickable('[data-cy="button-edit-group-name"]')
        browser.click('[data-cy="button-edit-group-name"]')

        browser.wait_for_element_visible('input[name="name"]')
        browser.clear('input[name="name"]')
        browser.type('input[name="name"]', "Updated Group Name")
        browser.click('[data-cy="button-submit"]')

        browser.wait_for_text("Group name updated")
        browser.assert_text("Updated Group Name")


def test_delete_payment_plan_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_group: PaymentPlanGroup,
) -> None:
    program = payment_plan_group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
        Permissions.PM_PAYMENT_PLAN_GROUP_DELETE,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{payment_plan_group.id}")

        browser.wait_for_element_clickable('[data-cy="button-delete-group"]')
        browser.click('[data-cy="button-delete-group"]')

        browser.wait_for_element_clickable('[data-cy="button-submit"]')
        browser.click('[data-cy="button-submit"]')

        browser.wait_for_text("Group Deleted")


def test_delete_button_hidden_when_group_has_payment_plans(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    group_with_payment_plan: PaymentPlanGroup,
) -> None:
    program = group_with_payment_plan.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
        Permissions.PM_PAYMENT_PLAN_GROUP_DELETE,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(
            f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group_with_payment_plan.id}"
        )

        browser.wait_for_element_visible('h5[data-cy="page-header-title"]')
        browser.assert_element_absent('[data-cy="button-delete-group"]')
