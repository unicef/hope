import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, ProgramCycle, User

pytestmark = pytest.mark.django_db()


def test_create_payment_plan_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    program_cycle: ProgramCycle,
) -> None:
    program = program_cycle.program
    group_name = "E2E Test Group"

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
        browser.type('input[name="groupName"]', group_name)
        browser.click('[data-cy="button-create-group-submit"]')
        browser.wait_for_text("Payment Plan Group created")

        browser.click('[data-cy="nav-Payment Module"]')
        browser.wait_for_element_clickable('a[data-cy="nav-Groups"]')
        browser.click('a[data-cy="nav-Groups"]')

        browser.wait_for_text(group_name)
