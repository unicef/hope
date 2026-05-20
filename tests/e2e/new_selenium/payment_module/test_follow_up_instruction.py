from decimal import Decimal
from tempfile import NamedTemporaryFile
from types import SimpleNamespace
from urllib.parse import urlparse

import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.payment.celery_tasks import create_follow_up_instruction_delivery_xlsx_async_task_action
from hope.apps.payment.xlsx.xlsx_follow_up_instruction_delivery_export_service import (
    XlsxFollowUpInstructionDeliveryExportService,
)
from hope.models import BusinessArea, FollowUpInstruction, PaymentPlanGroup, Program, User

pytestmark = pytest.mark.django_db()


def _select_autocomplete_option(browser: HopeTestBrowser, label: str) -> None:
    browser.type('input[aria-label="Payment Plan Groups"]', label)
    browser.wait_for_element_visible('li[role="option"]')
    browser.click('li[role="option"]')


def _confirm_workflow_button(browser: HopeTestBrowser, button_cy: str) -> None:
    browser.wait_for_element_clickable(f'[data-cy="{button_cy}"]')
    browser.click(f'[data-cy="{button_cy}"]')
    browser.wait_for_element_clickable(f'[data-cy="{button_cy}-confirm"]')
    browser.click(f'[data-cy="{button_cy}-confirm"]')


def _build_reconciliation_workbook(instruction: FollowUpInstruction):
    """Generate the export workbook and fill in 3 delivery cases.

    Row for hh_a (entitlement 140): fully delivered — delivered_quantity = 140
    Row for hh_b (entitlement  60): partially delivered — delivered_quantity = 30
    Row for hh_c (entitlement  80): no value — delivered_quantity left empty
    """
    wb = XlsxFollowUpInstructionDeliveryExportService(instruction).generate_workbook()
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    delivered_col = headers.index("delivered_quantity") + 1

    ws.cell(row=2, column=delivered_col).value = Decimal("140.00")
    ws.cell(row=3, column=delivered_col).value = Decimal("30.00")
    ws.cell(row=4, column=delivered_col).value = None

    return wb


def test_follow_up_instruction_full_flow(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    fi_program: Program,
    fi_source_plans: tuple[PaymentPlanGroup, PaymentPlanGroup],
) -> None:
    group_one, group_two = fi_source_plans
    ba_slug = business_area.slug
    program_code = fi_program.code
    base_url = f"/{ba_slug}/programs/{program_code}"

    # --- Step 1: Follow-up Instructions list is empty ---
    login.open(f"{base_url}/payment-module/follow-up-instructions")
    login.wait_for_text("Follow-up Instructions")

    # --- Step 2: Open create dialog and fill form ---
    login.wait_for_element_clickable('[data-cy="button-create-follow-up-instruction"]')
    login.click('[data-cy="button-create-follow-up-instruction"]')
    login.wait_for_element_visible('input[aria-label="Payment Plan Groups"]')

    # Select both groups via the Autocomplete field.
    # Groups are identified by their unicef_id (set automatically) which may differ per run,
    # so we clear the input, open the dropdown, and pick by exact text match.
    _select_autocomplete_option(login, group_one.unicef_id or group_one.name)
    _select_autocomplete_option(login, group_two.unicef_id or group_two.name)

    login.type('input[name="dispersionStartDate"]', "01/01/2027")
    login.type('input[name="dispersionEndDate"]', "12/31/2027")
    login.click('[data-cy="button-submit-create-follow-up-instruction"]')

    # --- Step 3: Detail page — OPEN state ---
    login.wait_for_text("Open")
    login.wait_for_element_visible('[data-cy="button-lock"]')
    login.assert_element_absent('[data-cy="button-lock-fsp"]')
    login.assert_element_absent('[data-cy="button-send-for-approval"]')

    detail_path = urlparse(login.get_current_url()).path

    # --- Step 4: Lock ---
    login.click('[data-cy="button-lock"]')
    login.wait_for_text("Locked")  # status transitions to Locked
    login.wait_for_element_absent('[data-cy="button-lock"]')
    login.wait_for_element_visible('[data-cy="button-unlock"]')
    login.wait_for_element_visible('[data-cy="button-lock-fsp"]')

    # --- Step 5: Lock FSP ---
    login.click('[data-cy="button-lock-fsp"]')
    login.wait_for_text("Locked FSP")
    login.wait_for_element_absent('[data-cy="button-lock-fsp"]')
    login.wait_for_element_visible('[data-cy="button-send-for-approval"]')

    # --- Step 6: Send for Approval ---
    login.click('[data-cy="button-send-for-approval"]')
    login.wait_for_text("In Approval")
    login.wait_for_element_visible('[data-cy="button-approve"]')
    login.wait_for_element_visible('[data-cy="button-reject"]')
    login.wait_for_element_absent('[data-cy="button-send-for-approval"]')

    # --- Step 7: Approve ---
    _confirm_workflow_button(login, "button-approve")
    login.wait_for_text("In Authorization")
    login.wait_for_element_visible('[data-cy="button-authorize"]')
    login.wait_for_element_absent('[data-cy="button-approve"]')

    # --- Step 8: Authorize ---
    _confirm_workflow_button(login, "button-authorize")
    login.wait_for_text("In Review")
    login.wait_for_element_visible('[data-cy="button-mark-as-released"]')
    login.wait_for_element_absent('[data-cy="button-authorize"]')

    # --- Step 9: Mark as Released → Accepted ---
    _confirm_workflow_button(login, "button-mark-as-released")
    login.wait_for_text("Accepted")
    login.wait_for_element_visible('[data-cy="button-reconciliation-export"]')
    login.wait_for_element_visible('[data-cy="button-reconciliation-import"]')
    login.wait_for_element_absent('[data-cy="button-mark-as-released"]')

    # --- Step 10: Trigger XLSX export ---
    login.click('[data-cy="button-reconciliation-export"]')
    login.wait_for_text("Exporting XLSX started")

    # Execute the background Celery task synchronously in the test process.
    # The task is queued via AsyncRetryJob; we call its action function directly
    # with the instruction ID extracted from the browser URL.
    instruction_id = detail_path.rstrip("/").rsplit("/", 1)[-1]
    superuser = User.objects.get(username="superuser")
    job = SimpleNamespace(config={"follow_up_instruction_id": instruction_id, "user_id": str(superuser.pk)})
    create_follow_up_instruction_delivery_xlsx_async_task_action(job)

    # Reload the page — the export file is now ready.
    login.open(detail_path)
    login.wait_for_element_visible('[data-cy="button-download-export"]')

    # --- Step 11: Build reconciliation XLSX with 3 delivery cases and upload it ---
    instruction = FollowUpInstruction.objects.get(pk=instruction_id)
    wb = _build_reconciliation_workbook(instruction)

    with NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        wb.save(tmp.name)
        reconciliation_path = tmp.name

    login.click('[data-cy="button-reconciliation-import"]')
    login.wait_for_element_visible('[data-cy="dialog-reconciliation-import"]')
    login.choose_file('input[type="file"]', reconciliation_path)
    login.wait_for_element_clickable('[data-cy="button-reconciliation-import-submit"]')
    login.click('[data-cy="button-reconciliation-import-submit"]')

    # --- Step 12: Confirm reconciliation import started ---
    login.wait_for_text("Reconciliation import started")
