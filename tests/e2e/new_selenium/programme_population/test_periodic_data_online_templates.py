from collections.abc import Callable

import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories import PDUOnlineEditFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import (
    BusinessArea,
    FlexibleAttribute,
    Individual,
    PDUOnlineEdit,
    PDUOnlineEditSentBackComment,
    Program,
    User,
)

pytestmark = pytest.mark.django_db()

OnlineEditFactory = Callable[..., PDUOnlineEdit]

STATUS = '[data-cy="status-container"]'
SEND_FOR_APPROVAL = 'button[data-cy="send-for-approval"]'
SEND_BACK = 'button[data-cy="send-back"]'
APPROVE = 'button[data-cy="approve"]'
MERGE = 'button[data-cy="merge"]'
VIEW_PERMISSIONS = (
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
    Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
    Permissions.PDU_VIEW_LIST_AND_DETAILS,
)
ALL_ONLINE_PERMISSIONS = (
    Permissions.PDU_ONLINE_SAVE_DATA,
    Permissions.PDU_ONLINE_APPROVE,
    Permissions.PDU_ONLINE_MERGE,
)


def individuals_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/population/individuals"


def open_details(browser: HopeTestBrowser, online_edit: PDUOnlineEdit) -> None:
    browser.open(f"{individuals_url(online_edit.program)}/online-templates/{online_edit.id}")
    browser.wait_for_text("Online Edits Template Details", 'h5[data-cy="page-header-title"]')


def edit_row(individual: Individual) -> str:
    return f'button[data-cy="button-edit-row-{individual.unicef_id}"]'


def round_value(online_edit: PDUOnlineEdit, field_name: str) -> dict:
    online_edit.refresh_from_db()
    return online_edit.edit_data[0]["pdu_fields"][field_name]


def test_create_online_template(
    login: HopeTestBrowser,
    program: Program,
    string_attribute: FlexibleAttribute,
    individual: Individual,
) -> None:
    """Creating an online edit through the wizard persists a PDUOnlineEdit for the program."""
    ba_slug = program.business_area.slug

    login.open(f"/{ba_slug}/programs/{program.code}/population/individuals")
    login.wait_for_element_clickable('button[data-cy="tab-periodic-data-updates"]').click()
    login.wait_for_element_clickable('button[data-cy="pdu-online-edits"]').click()
    login.wait_for_element_clickable('[data-cy="button-new-online-edit"]').click()

    # Step 0 (Filter) - keep the whole population, just continue.
    login.wait_for_element_clickable('button[data-cy="next-button"]').click()
    # Step 1 (Fields to Update) - select the periodic field to update.
    login.check_checkbox(f'[data-cy="checkbox-{string_attribute.name}"]')
    login.click('button[data-cy="next-button"]')
    # Step 2 (Authorized Users) - optional, skip.
    login.wait_for_element_clickable('button[data-cy="next-button"]').click()
    # Step 3 (Template Name) - optional, generate the template.
    login.wait_for_element_clickable('button[data-cy="submit-button"]').click()

    # The template is created (celery runs eagerly) and we are redirected to the list.
    login.wait_for_element_present('[data-cy^="online-edit-row-"]')
    assert PDUOnlineEdit.objects.count() == 1
    online_edit = PDUOnlineEdit.objects.first()
    assert online_edit.program == program
    login.assert_text(str(online_edit.id), f'[data-cy="online-edit-row-{online_edit.id}"]')


def test_online_template_details_send_for_approval(
    login: HopeTestBrowser,
    program: Program,
    create_super_user: User,
) -> None:
    """Sending an online edit for approval transitions it from NEW to READY."""
    online_edit = PDUOnlineEditFactory(
        name="Online Edit For Approval",
        program=program,
        business_area=program.business_area,
        created_by=create_super_user,
        status=PDUOnlineEdit.Status.NEW,
        authorized_users=[create_super_user],
    )
    ba_slug = program.business_area.slug

    login.open(f"/{ba_slug}/programs/{program.code}/population/individuals/online-templates/{online_edit.id}")
    login.assert_text("Online Edits Template Details", 'h5[data-cy="page-header-title"]')

    login.wait_for_element_clickable('button[data-cy="send-for-approval"]').click()

    # The send-for-approval button only renders while status is NEW; its disappearance
    # signals the READY transition completed.
    login.wait_for_element_absent('button[data-cy="send-for-approval"]')
    online_edit.refresh_from_db()
    assert online_edit.status == PDUOnlineEdit.Status.READY


def test_edit_authorized_users(
    login: HopeTestBrowser,
    program: Program,
    create_super_user: User,
) -> None:
    """Adding an authorized user on the edit page persists the relationship."""
    online_edit = PDUOnlineEditFactory(
        name="Online Edit For Auth Users",
        program=program,
        business_area=program.business_area,
        created_by=create_super_user,
        status=PDUOnlineEdit.Status.NEW,
    )
    assert online_edit.authorized_users.count() == 0
    ba_slug = program.business_area.slug

    login.open(
        f"/{ba_slug}/programs/{program.code}/population/individuals/"
        f"online-templates/{online_edit.id}/edit-authorised-users"
    )
    login.check_checkbox(f'[data-cy="checkbox-authorized-user-{create_super_user.id}"]')
    login.wait_for_element_clickable('button[data-cy="button-save-authorized-users"]').click()

    # Saving redirects back to the template details page.
    login.wait_for_text("Online Edits Template Details", 'h5[data-cy="page-header-title"]')
    assert online_edit.authorized_users.filter(pk=create_super_user.pk).exists()


def test_edit_value_in_row(
    login: HopeTestBrowser,
    online_edit_factory: OnlineEditFactory,
    string_attribute: FlexibleAttribute,
    individual: Individual,
) -> None:
    online_edit = online_edit_factory()
    open_details(login, online_edit)

    login.wait_for_element_clickable(edit_row(individual)).click()
    login.set_value(f'input[data-cy="input-pdu-{string_attribute.name}-{individual.unicef_id}"]', "Round one value")
    login.click(f'button[data-cy="button-save-row-{individual.unicef_id}"]')

    # Saving leaves edit mode, so the Edit button comes back.
    login.wait_for_element_clickable(edit_row(individual))
    field = round_value(online_edit, string_attribute.name)
    assert field["value"] == "Round one value"
    assert field["collection_date"] is not None


def test_send_back_with_comment(
    login: HopeTestBrowser,
    online_edit_factory: OnlineEditFactory,
    create_super_user: User,
) -> None:
    online_edit = online_edit_factory(status=PDUOnlineEdit.Status.READY)
    open_details(login, online_edit)

    login.wait_for_element_clickable(SEND_BACK).click()
    login.set_value('textarea[data-cy="input-send-back-comment"]', "Fix round one")
    login.wait_for_element_clickable('button[data-cy="button-confirm"]').click()

    login.wait_for_text("Fix round one", '[data-testid="sent-back-comment"]')
    login.wait_for_element_clickable(SEND_FOR_APPROVAL)
    online_edit.refresh_from_db()
    assert online_edit.status == PDUOnlineEdit.Status.NEW
    comment = PDUOnlineEditSentBackComment.objects.get(pdu_online_edit=online_edit)
    assert comment.comment == "Fix round one"
    assert comment.created_by.username == create_super_user.username


def test_approve(
    login: HopeTestBrowser,
    online_edit_factory: OnlineEditFactory,
    create_super_user: User,
) -> None:
    online_edit = online_edit_factory(status=PDUOnlineEdit.Status.READY)
    open_details(login, online_edit)

    login.wait_for_element_clickable(APPROVE).click()

    login.wait_for_element_clickable(MERGE)
    online_edit.refresh_from_db()
    assert online_edit.status == PDUOnlineEdit.Status.APPROVED
    assert online_edit.approved_by.username == create_super_user.username
    assert online_edit.approved_at is not None


def test_merge_writes_value_to_individual(
    login: HopeTestBrowser,
    online_edit_factory: OnlineEditFactory,
    string_attribute: FlexibleAttribute,
    individual: Individual,
) -> None:
    online_edit = online_edit_factory(status=PDUOnlineEdit.Status.APPROVED, value="Merged value")
    open_details(login, online_edit)

    login.wait_for_element_clickable(MERGE).click()

    login.wait_for_text("Merged", STATUS)
    online_edit.refresh_from_db()
    assert online_edit.status == PDUOnlineEdit.Status.MERGED
    individual.refresh_from_db()
    assert individual.flex_fields[string_attribute.name]["1"]["value"] == "Merged value"


def test_full_flow_from_edit_to_individual_page(
    login: HopeTestBrowser,
    online_edit_factory: OnlineEditFactory,
    string_attribute: FlexibleAttribute,
    individual: Individual,
) -> None:
    """Edit a value, send it for approval, approve and merge it, then see it on the individual."""
    online_edit = online_edit_factory()
    open_details(login, online_edit)

    login.wait_for_element_clickable(edit_row(individual)).click()
    login.set_value(f'input[data-cy="input-pdu-{string_attribute.name}-{individual.unicef_id}"]', "Full flow value")
    login.click(f'button[data-cy="button-save-row-{individual.unicef_id}"]')
    login.wait_for_element_clickable(edit_row(individual))

    login.click(SEND_FOR_APPROVAL)
    login.wait_for_element_clickable(APPROVE).click()
    login.wait_for_element_clickable(MERGE).click()
    login.wait_for_text("Merged", STATUS)

    login.open(f"{individuals_url(online_edit.program)}/{individual.id}")
    login.wait_for_text("Full flow value", 'table[aria-label="programme time series fields"]')


def online_edits_list_url(program: Program) -> str:
    return f"{individuals_url(program)}?tab=periodic-data-updates&subtab=online-edits"


def check_rows(browser: HopeTestBrowser, list_name: str, edits: list[PDUOnlineEdit]) -> None:
    for edit in edits:
        browser.check_checkbox(f'[data-cy="{list_name}-row-{edit.id}"] [data-cy="checkbox-row-{edit.id}"]')


def wait_for_rows(browser: HopeTestBrowser, list_name: str, edits: list[PDUOnlineEdit]) -> None:
    for edit in edits:
        browser.wait_for_element_present(f'[data-cy="{list_name}-row-{edit.id}"]')


def statuses(edits: list[PDUOnlineEdit]) -> set[str]:
    return set(PDUOnlineEdit.objects.filter(pk__in=[edit.pk for edit in edits]).values_list("status", flat=True))


def test_bulk_approve_from_pending_approval_list(
    login: HopeTestBrowser,
    program: Program,
    online_edit_factory: OnlineEditFactory,
) -> None:
    edits = [
        online_edit_factory(status=PDUOnlineEdit.Status.READY),
        online_edit_factory(status=PDUOnlineEdit.Status.READY),
    ]
    login.open(online_edits_list_url(program))

    check_rows(login, "pending-approval", edits)
    login.click('button[data-cy="button-bulk-approve"]')

    wait_for_rows(login, "pending-merge", edits)
    assert statuses(edits) == {PDUOnlineEdit.Status.APPROVED}


def test_bulk_merge_from_pending_merge_list(
    login: HopeTestBrowser,
    program: Program,
    online_edit_factory: OnlineEditFactory,
    string_attribute: FlexibleAttribute,
    individual: Individual,
) -> None:
    # Merging the same individual's round twice fails, so only the first edit carries a value.
    edits = [
        online_edit_factory(status=PDUOnlineEdit.Status.APPROVED, value="Bulk value"),
        online_edit_factory(status=PDUOnlineEdit.Status.APPROVED),
    ]
    login.open(online_edits_list_url(program))

    check_rows(login, "pending-merge", edits)
    login.click('button[data-cy="button-bulk-merge"]')

    wait_for_rows(login, "merged", edits)
    assert statuses(edits) == {PDUOnlineEdit.Status.MERGED}
    individual.refresh_from_db()
    assert individual.flex_fields[string_attribute.name]["1"]["value"] == "Bulk value"


EDIT_ROW = 'button[data-cy="button-edit-row-IND-00-0000.0001"]'


@pytest.mark.parametrize(
    ("status", "button", "permission"),
    [
        pytest.param(
            PDUOnlineEdit.Status.NEW, SEND_FOR_APPROVAL, Permissions.PDU_ONLINE_SAVE_DATA, id="send-for-approval"
        ),
        pytest.param(PDUOnlineEdit.Status.NEW, EDIT_ROW, Permissions.PDU_ONLINE_SAVE_DATA, id="edit-row"),
        pytest.param(PDUOnlineEdit.Status.READY, SEND_BACK, Permissions.PDU_ONLINE_APPROVE, id="send-back"),
        pytest.param(PDUOnlineEdit.Status.READY, APPROVE, Permissions.PDU_ONLINE_APPROVE, id="approve"),
        pytest.param(PDUOnlineEdit.Status.APPROVED, MERGE, Permissions.PDU_ONLINE_MERGE, id="merge"),
    ],
)
def test_action_shown_with_permission(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    online_edit_factory: OnlineEditFactory,
    status: str,
    button: str,
    permission: Permissions,
) -> None:
    online_edit = online_edit_factory(status=status, authorized_users=[user_with_no_permissions])
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, permission):
        browser.login(username="noperm_user")
        open_details(browser, online_edit)
        browser.wait_for_element_clickable(button)


@pytest.mark.parametrize(
    ("status", "button"),
    [
        pytest.param(PDUOnlineEdit.Status.NEW, SEND_FOR_APPROVAL, id="send-for-approval"),
        pytest.param(PDUOnlineEdit.Status.NEW, EDIT_ROW, id="edit-row"),
        pytest.param(PDUOnlineEdit.Status.READY, SEND_BACK, id="send-back"),
        pytest.param(PDUOnlineEdit.Status.READY, APPROVE, id="approve"),
        pytest.param(PDUOnlineEdit.Status.APPROVED, MERGE, id="merge"),
    ],
)
def test_action_hidden_without_permission(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    online_edit_factory: OnlineEditFactory,
    status: str,
    button: str,
) -> None:
    online_edit = online_edit_factory(status=status, authorized_users=[user_with_no_permissions])
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS):
        browser.login(username="noperm_user")
        open_details(browser, online_edit)
        browser.wait_for_element_visible(STATUS)
        browser.assert_element_absent(button)


@pytest.mark.parametrize(
    ("status", "buttons"),
    [
        pytest.param(PDUOnlineEdit.Status.NEW, (SEND_FOR_APPROVAL,), id="new"),
        pytest.param(PDUOnlineEdit.Status.READY, (SEND_BACK, APPROVE), id="ready"),
        pytest.param(PDUOnlineEdit.Status.APPROVED, (MERGE,), id="approved"),
    ],
)
def test_user_not_authorized_for_the_edit_sees_no_actions(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    online_edit_factory: OnlineEditFactory,
    status: str,
    buttons: tuple[str, ...],
) -> None:
    online_edit = online_edit_factory(status=status)
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, *ALL_ONLINE_PERMISSIONS):
        browser.login(username="noperm_user")
        open_details(browser, online_edit)
        browser.wait_for_element_visible(STATUS)
        browser.assert_elements_absent(*buttons)


def test_user_not_authorized_for_the_edit_cannot_edit_rows(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    online_edit_factory: OnlineEditFactory,
) -> None:
    online_edit = online_edit_factory()
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, *ALL_ONLINE_PERMISSIONS):
        browser.login(username="noperm_user")
        open_details(browser, online_edit)
        assert not browser.wait_for_element_visible(EDIT_ROW).is_enabled()
