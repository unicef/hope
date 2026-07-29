"""The Amendment endpoint funds itself the same way the Top-Up one does.

The serializer and the file parser are shared between the two flows, so these tests exist to make
the Amendment side fail on its own if that sharing is ever broken.
"""

from io import BytesIO
from typing import Any, Callable

from django.core.files.uploadedfile import SimpleUploadedFile
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    PaymentFactory,
    PaymentHouseholdSnapshotFactory,
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.services.top_up_amount_service import TopUpAmountTemplateService
from hope.apps.payment.xlsx.xlsx_payment_plan_base_service import XlsxPaymentPlanBaseService
from hope.models import Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db

DATES = {"dispersion_start_date": "2024-01-01", "dispersion_end_date": "2099-12-31"}


@pytest.fixture
def amendment_context(api_client: Callable, create_user_role_with_permissions: Any) -> dict[str, Any]:
    business_area = BusinessAreaFactory(slug="afghanistan")
    user = UserFactory()
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program)
    purpose = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.add(purpose)
    regular_pp = PaymentPlanFactory(
        name="Standard PP",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=PaymentPlan.Status.ACCEPTED,
        currency=CurrencyFactory(code="USD"),
        payment_plan_purposes=[purpose],
    )
    top_up_pp = PaymentPlanFactory(
        name="Standard PP Top Up",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        status=PaymentPlan.Status.ACCEPTED,
        source_payment_plan=regular_pp,
        currency=regular_pp.currency,
        payment_plan_purposes=[purpose],
    )
    payments = [PaymentFactory(parent=top_up_pp, status=Payment.STATUS_PENDING) for _ in range(3)]
    # The template is rendered from household snapshots, which a real released plan always has.
    for payment in payments:
        PaymentHouseholdSnapshotFactory(
            payment=payment,
            snapshot_data={"unicef_id": payment.household.unicef_id, "size": payment.household.size},
        )
    create_user_role_with_permissions(user, [Permissions.PM_CREATE], business_area, program)
    url_kwargs = {
        "business_area_slug": business_area.slug,
        "program_code": program.code,
        "pk": top_up_pp.pk,
    }
    return {
        "top_up_pp": top_up_pp,
        "payments": payments,
        "client": api_client(user),
        "template_url": reverse("api:payments:payment-plans-top-up-amount-template", kwargs=url_kwargs),
        "create_url": reverse("api:payments:payment-plans-create-top-up-amendment", kwargs=url_kwargs),
    }


def _amount_file(source_pp: PaymentPlan, amounts_by_payment_id: dict[str, str | None]) -> SimpleUploadedFile:
    """Build a filled-in amount template. Payment ids missing from the mapping are left blank."""
    workbook = TopUpAmountTemplateService(source_pp).generate_workbook()
    worksheet = workbook.active
    headers = [cell.value for cell in worksheet[1]]
    payment_id_column = headers.index(XlsxPaymentPlanBaseService.COLUMN_PAYMENT_ID) + 1
    amount_column = headers.index(XlsxPaymentPlanBaseService.COLUMN_ENTITLEMENT_QUANTITY) + 1
    for row_index in range(2, worksheet.max_row + 1):
        payment_id = worksheet.cell(row=row_index, column=payment_id_column).value
        worksheet.cell(row=row_index, column=amount_column).value = amounts_by_payment_id.get(str(payment_id))
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return SimpleUploadedFile("amounts.xlsx", buffer.read())


def test_amendment_amount_template_arrange_top_up_source_act_get_assert_lists_its_own_payments(
    amendment_context: dict[str, Any],
) -> None:
    """Asked on a Top-Up, the shared template endpoint lists that Top-Up's amendable payments."""
    response = amendment_context["client"].get(amendment_context["template_url"])

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Disposition"].startswith("attachment;")


def test_create_amendment_arrange_both_fixed_and_file_act_post_assert_400(
    amendment_context: dict[str, Any],
) -> None:
    upload = _amount_file(amendment_context["top_up_pp"], {amendment_context["payments"][0].unicef_id: "40.00"})

    response = amendment_context["client"].post(
        amendment_context["create_url"],
        {**DATES, "fixed_amount": "10.00", "file": upload},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not both" in str(response.json())


def test_create_amendment_arrange_no_amount_given_act_post_assert_400(amendment_context: dict[str, Any]) -> None:
    response = amendment_context["client"].post(amendment_context["create_url"], DATES, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not both" in str(response.json())


def test_create_amendment_arrange_zero_amount_in_file_act_post_assert_row_left_out(
    amendment_context: dict[str, Any],
    django_capture_on_commit_callbacks: Any,
) -> None:
    funded, zeroed, skipped = amendment_context["payments"]
    upload = _amount_file(
        amendment_context["top_up_pp"],
        {funded.unicef_id: "40.00", zeroed.unicef_id: "0", skipped.unicef_id: None},
    )

    with django_capture_on_commit_callbacks(execute=True):
        response = amendment_context["client"].post(
            amendment_context["create_url"], {**DATES, "file": upload}, format="multipart"
        )

    assert response.status_code == status.HTTP_201_CREATED
    amendment = PaymentPlan.objects.get(pk=response.json()["id"])
    assert list(amendment.payment_items.values_list("source_payment_id", flat=True)) == [funded.id]
    # The zeroed and the blank row are both still available for a later Amendment.
    assert set(amendment_context["top_up_pp"].eligible_payments_for_top_up_amendment()) == {zeroed, skipped}
