import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, PaymentPlan, User

pytestmark = pytest.mark.django_db()

STATUS = 'div[data-cy="target-population-status"]'
LOCK = 'button[data-cy="button-target-population-lock"]'
DELETE = 'button[data-cy="button-delete"]'
EDIT = '[data-cy="button-edit"]'
REBUILD = 'button[data-cy="button-rebuild"]'
DUPLICATE = 'button[data-cy="button-target-population-duplicate"]'
UNLOCK = 'button[data-cy="button-target-population-unlocked"]'
MARK_READY = 'button[data-cy="button-target-population-send-to-hope"]'
OPEN_TP_ACTIONS = (LOCK, DELETE, EDIT, REBUILD, DUPLICATE)
LOCKED_TP_ACTIONS = (UNLOCK, MARK_READY, DUPLICATE)


def tp_url(tp: PaymentPlan) -> str:
    return f"/{tp.business_area.slug}/programs/{tp.program_cycle.program.code}/target-population/{tp.id}"


@pytest.mark.parametrize(
    ("tp_fixture", "status", "permission", "visible", "hidden"),
    [
        pytest.param(
            "built_tp", "OPEN", Permissions.TARGETING_LOCK, (LOCK, REBUILD), (DELETE, EDIT, DUPLICATE), id="lock"
        ),
        pytest.param("built_tp", "OPEN", Permissions.TARGETING_REMOVE, (DELETE,), (LOCK, EDIT, DUPLICATE), id="remove"),
        pytest.param(
            "built_tp", "OPEN", Permissions.TARGETING_UPDATE, (EDIT,), (LOCK, REBUILD, DELETE, DUPLICATE), id="update"
        ),
        pytest.param(
            "built_tp", "OPEN", Permissions.TARGETING_DUPLICATE, (DUPLICATE,), (LOCK, DELETE, EDIT), id="duplicate"
        ),
        pytest.param("locked_tp", "LOCKED", Permissions.TARGETING_UNLOCK, (UNLOCK,), (MARK_READY,), id="unlock"),
        pytest.param("locked_tp", "LOCKED", Permissions.TARGETING_SEND, (MARK_READY,), (UNLOCK,), id="send"),
    ],
)
def test_each_targeting_permission_shows_only_its_action(
    request: pytest.FixtureRequest,
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    tp_fixture: str,
    status: str,
    permission: Permissions,
    visible: tuple[str, ...],
    hidden: tuple[str, ...],
) -> None:
    tp = request.getfixturevalue(tp_fixture)
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.TARGETING_VIEW_DETAILS,
        permission,
    ):
        browser.login(username="noperm_user")
        browser.open(tp_url(tp))
        browser.wait_for_text(status, STATUS)
        browser.wait_for_text(tp.name, 'h5[data-cy="page-header-title"]')
        browser.assert_elements_present(*visible)
        browser.assert_elements_absent(*hidden)


@pytest.mark.parametrize(
    ("tp_fixture", "status", "actions"),
    [
        pytest.param("built_tp", "OPEN", OPEN_TP_ACTIONS, id="open"),
        pytest.param("locked_tp", "LOCKED", LOCKED_TP_ACTIONS, id="locked"),
    ],
)
def test_view_only_user_sees_no_targeting_actions(
    request: pytest.FixtureRequest,
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    tp_fixture: str,
    status: str,
    actions: tuple[str, ...],
) -> None:
    tp = request.getfixturevalue(tp_fixture)
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.TARGETING_VIEW_DETAILS,
    ):
        browser.login(username="noperm_user")
        browser.open(tp_url(tp))
        browser.wait_for_text(status, STATUS)
        browser.wait_for_text(tp.name, 'h5[data-cy="page-header-title"]')
        browser.assert_elements_absent(*actions)
