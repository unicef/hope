import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import PaymentList

pytestmark = pytest.mark.django_db()


def test_activate_verification_plan_flow(
    login: HopeTestBrowser,
    pending_verification_payment_list: PaymentList,
) -> None:
    """Regression for PR #6001 — block concurrent activation of verification plans."""
    payment_list = pending_verification_payment_list
    program = payment_list.program_cycle.program
    url = (
        f"/{payment_list.business_area.slug}/programs/{program.code}"
        f"/payment-verification/payment-list/{payment_list.id}"
    )
    login.open(url)

    # Plan starts PENDING and the Activate action is offered.
    login.assert_text("PENDING", 'div[data-cy="verification-plan-status"]')
    login.wait_for_element_clickable('button[data-cy="button-activate-plan"]').click()

    # Confirm in the dialog.
    login.wait_for_element_clickable('button[data-cy="button-submit"]').click()

    # The page re-fetches after activation, so wait for the status text to settle on ACTIVE.
    login.wait_for_text("ACTIVE", 'div[data-cy="verification-plan-status"]')
    login.wait_for_element_absent('button[data-cy="button-activate-plan"]')
