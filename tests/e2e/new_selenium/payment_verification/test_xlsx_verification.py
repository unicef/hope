from decimal import Decimal
from pathlib import Path

import pytest

from e2e.new_selenium.payment_verification.conftest import (
    DELIVERED_QUANTITY,
    PLAN_STATUS,
    RECORD_STATUS,
    activate_plan,
    export_and_download_xlsx,
    fill_verification_xlsx,
    import_xlsx,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import PaymentVerification, PaymentVerificationPlan

pytestmark = pytest.mark.django_db()

BUTTON_DISCARD = 'button[data-cy="button-discard-plan"]'
BUTTON_MARK_AS_INVALID = 'button[data-cy="button-mark-as-invalid"]'


@pytest.mark.parametrize(
    ("received", "received_amount", "status"),
    [
        pytest.param("YES", DELIVERED_QUANTITY, "RECEIVED", id="received"),
        pytest.param("YES", DELIVERED_QUANTITY - 1, "RECEIVED WITH ISSUES", id="received-with-issues"),
        pytest.param("NO", Decimal(0), "NOT RECEIVED", id="not-received"),
    ],
)
def test_xlsx_import_sets_payment_status(
    login: HopeTestBrowser,
    xlsx_verification: PaymentVerification,
    tmp_path: Path,
    received: str,
    received_amount: Decimal,
    status: str,
) -> None:
    verification_plan = xlsx_verification.payment_verification_plan
    activate_plan(login, verification_plan.payment_plan)
    exported = export_and_download_xlsx(login, verification_plan)
    filled = tmp_path / "verification.xlsx"
    fill_verification_xlsx(exported, filled, received, received_amount)

    import_xlsx(login, filled)

    login.wait_for_text(status, RECORD_STATUS)
    login.assert_exact_text(status, RECORD_STATUS)
    login.assert_element_visible('button[data-cy="button-ed-plan"]')  # Finish is offered once a file is imported
    xlsx_verification.refresh_from_db()
    assert xlsx_verification.status == status.replace(" ", "_")
    assert xlsx_verification.received_amount == received_amount


def test_downloaded_xlsx_plan_can_be_marked_as_invalid_but_not_discarded(
    login: HopeTestBrowser,
    xlsx_verification: PaymentVerification,
) -> None:
    verification_plan = xlsx_verification.payment_verification_plan
    activate_plan(login, verification_plan.payment_plan)
    login.assert_element_visible(BUTTON_DISCARD)
    login.assert_element_absent(BUTTON_MARK_AS_INVALID)

    export_and_download_xlsx(login, verification_plan)

    login.wait_for_element_absent(BUTTON_DISCARD)
    login.wait_for_element_clickable(BUTTON_MARK_AS_INVALID).click()
    login.wait_for_text("Verification plan marked as invalid.")
    login.wait_for_text("INVALID", PLAN_STATUS)
    verification_plan.refresh_from_db()
    assert verification_plan.status == PaymentVerificationPlan.STATUS_INVALID
