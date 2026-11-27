import pytest

from e2e.new_selenium.payment_verification.conftest import (
    BUTTON_ACTIVATE,
    BUTTON_SUBMIT,
    PLAN_STATUS,
    activate_plan,
    verification_url,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import PaymentPlan, PaymentVerification, PaymentVerificationPlan

pytestmark = pytest.mark.django_db()


def test_activate_verification_plan_flow(
    login: HopeTestBrowser,
    pending_verification_payment_plan: PaymentPlan,
) -> None:
    """Regression for PR #6001 — block concurrent activation of verification plans."""
    login.open(verification_url(pending_verification_payment_plan))

    # Plan starts PENDING and the Activate action is offered.
    login.assert_text("PENDING", PLAN_STATUS)
    login.wait_for_element_clickable(BUTTON_ACTIVATE).click()

    # Confirm in the dialog.
    login.wait_for_element_clickable(BUTTON_SUBMIT).click()

    # The page re-fetches after activation, so wait for the status text to settle on ACTIVE.
    login.wait_for_text("ACTIVE", PLAN_STATUS)
    login.wait_for_element_absent(BUTTON_ACTIVATE)


def test_delete_and_create_verification_plan(
    login: HopeTestBrowser,
    manual_verification: PaymentVerification,
) -> None:
    deleted_plan = manual_verification.payment_verification_plan
    payment_plan = deleted_plan.payment_plan
    login.open(verification_url(payment_plan))

    login.wait_for_element_clickable('button[data-cy="button-delete-plan"]').click()
    login.wait_for_element_clickable(BUTTON_SUBMIT).click()
    login.wait_for_text("Verification plan has been deleted.")
    login.wait_for_element_absent(f'h6[data-cy="verification-plan-{deleted_plan.unicef_id}"]')

    login.wait_for_element_clickable('button[data-cy="button-new-plan"]').click()
    login.wait_for_element_clickable(BUTTON_SUBMIT).click()
    login.wait_for_text("New verification plan created.")

    new_plan = PaymentVerificationPlan.objects.get(payment_plan=payment_plan)
    assert new_plan.pk != deleted_plan.pk
    login.wait_for_text(f"Verification Plan #{new_plan.unicef_id}")
    login.assert_text("PENDING", PLAN_STATUS)
    login.assert_text("MANUAL", 'div[data-cy="label-VERIFICATION CHANNEL"]')
    login.assert_exact_text("1", 'div[data-cy="label-SAMPLE SIZE"]')
    login.assert_text("ACTIVATE", BUTTON_ACTIVATE)


def test_discard_active_verification_plan_returns_it_to_pending(
    login: HopeTestBrowser,
    xlsx_verification: PaymentVerification,
) -> None:
    verification_plan = xlsx_verification.payment_verification_plan
    activate_plan(login, verification_plan.payment_plan)

    login.wait_for_element_clickable('button[data-cy="button-discard-plan"]').click()
    login.assert_text("Discard Verification Plan", 'div[role="dialog"]')
    login.wait_for_element_clickable(BUTTON_SUBMIT).click()
    login.wait_for_text("Verification plan has been discarded.")

    login.wait_for_text("PENDING", PLAN_STATUS)
    verification_plan.refresh_from_db()
    assert verification_plan.status == PaymentVerificationPlan.STATUS_PENDING
    # A discarded plan can be activated again.
    activate_plan(login, verification_plan.payment_plan)
