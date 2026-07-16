import pytest

from extras.test_utils.factories import PDUOnlineEditFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import FlexibleAttribute, Individual, PDUOnlineEdit, Program, User

pytestmark = pytest.mark.django_db()


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
    login.wait_for_element_clickable(f'[data-cy="checkbox-{string_attribute.name}"]').click()
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
    login.wait_for_element_clickable(f'[data-cy="checkbox-authorized-user-{create_super_user.id}"]').click()
    login.wait_for_element_clickable('button[data-cy="button-save-authorized-users"]').click()

    # Saving redirects back to the template details page.
    login.wait_for_text("Online Edits Template Details", 'h5[data-cy="page-header-title"]')
    assert online_edit.authorized_users.filter(pk=create_super_user.pk).exists()
