import io
from typing import Any, Callable
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import openpyxl
import pytest
from rest_framework import status

from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import BusinessAreaFactory, CurrencyFactory
from extras.test_utils.factories.household import HouseholdFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.old_factories.account import UserFactory
from hope.apps.account.permissions import Permissions
from hope.apps.payment.xlsx.xlsx_top_up_create_import_service import XlsxTopUpCreateImportService
from hope.models import Payment, PaymentPlan, Program


@pytest.fixture
def business_area(db):
    return BusinessAreaFactory(slug="afghanistan-topup")


@pytest.fixture
def user(business_area):
    partner = PartnerFactory(name="unittest-topup")
    return UserFactory(partner=partner)


@pytest.fixture
def client(user: Any, api_client: Callable):
    return api_client(user)


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def currency_pln(db):
    return CurrencyFactory(code="PLN", name="Polish Zloty")


@pytest.fixture
def source_pp(business_area, cycle, user, currency_pln):
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        created_by=user,
        currency=currency_pln,
        plan_type=PaymentPlan.PlanType.REGULAR,
        name="TopUp Source PP",
    )


@pytest.fixture
def eligible_payment(source_pp):
    household = HouseholdFactory(
        program=source_pp.program_cycle.program,
        business_area=source_pp.business_area,
    )
    return PaymentFactory(
        parent=source_pp,
        household=household,
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        currency=source_pp.currency,
    )


@pytest.fixture
def url_create_top_up(business_area, program, source_pp):
    return reverse(
        "api:payments:payment-plans-create-top-up",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "pk": source_pp.pk,
        },
    )


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_view_arrange_eligible_act_post_assert_201(
    get_exchange_rate_mock: Any,
    client,
    user,
    business_area,
    program,
    source_pp,
    eligible_payment,
    url_create_top_up,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(user, [Permissions.PM_CREATE], business_area, program)

    response = client.post(
        url_create_top_up,
        {
            "dispersion_start_date": "2026-06-01",
            "dispersion_end_date": "2026-07-01",
            "total_entitled_quantity": "150",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["plan_type"] == PaymentPlan.PlanType.TOP_UP
    assert body["name"] == "TopUp Source PP Top Up"
    assert body["currency"] == "PLN"
    assert body["source_payment_plan"]["id"] == str(source_pp.pk)


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_view_arrange_no_permission_act_post_assert_403(
    get_exchange_rate_mock: Any,
    client,
    user,
    business_area,
    program,
    source_pp,
    eligible_payment,
    url_create_top_up,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(user, [], business_area, program)

    response = client.post(
        url_create_top_up,
        {
            "dispersion_start_date": "2026-06-01",
            "dispersion_end_date": "2026-07-01",
            "total_entitled_quantity": "150",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    ("payload", "missing_field"),
    [
        (
            {"dispersion_end_date": "2026-07-01", "total_entitled_quantity": "150"},
            "dispersion_start_date",
        ),
        (
            {"dispersion_start_date": "2026-06-01", "total_entitled_quantity": "150"},
            "dispersion_end_date",
        ),
        (
            {"dispersion_start_date": "2026-06-01", "dispersion_end_date": "2026-07-01"},
            "total_entitled_quantity",
        ),
    ],
)
def test_create_top_up_view_parametrized_missing_field_act_post_assert_400(
    client,
    user,
    business_area,
    program,
    source_pp,
    eligible_payment,
    url_create_top_up,
    create_user_role_with_permissions: Any,
    payload: dict,
    missing_field: str,
):
    create_user_role_with_permissions(user, [Permissions.PM_CREATE], business_area, program)

    response = client.post(url_create_top_up, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert missing_field in response.json()


def test_create_top_up_view_arrange_zero_total_act_post_assert_400(
    client,
    user,
    business_area,
    program,
    source_pp,
    eligible_payment,
    url_create_top_up,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(user, [Permissions.PM_CREATE], business_area, program)

    response = client.post(
        url_create_top_up,
        {
            "dispersion_start_date": "2026-06-01",
            "dispersion_end_date": "2026-07-01",
            "total_entitled_quantity": "0",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_view_arrange_no_eligible_payments_act_post_assert_400(
    get_exchange_rate_mock: Any,
    client,
    user,
    business_area,
    program,
    source_pp,
    url_create_top_up,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(user, [Permissions.PM_CREATE], business_area, program)

    response = client.post(
        url_create_top_up,
        {
            "dispersion_start_date": "2026-06-01",
            "dispersion_end_date": "2026-07-01",
            "total_entitled_quantity": "100",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.fixture
def url_top_up_template(business_area, program, source_pp):
    return reverse(
        "api:payments:payment-plans-download-top-up-template",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "pk": source_pp.pk,
        },
    )


@pytest.fixture
def url_create_top_up_from_xlsx(business_area, program, source_pp):
    return reverse(
        "api:payments:payment-plans-create-top-up-from-xlsx",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "pk": source_pp.pk,
        },
    )


def test_download_top_up_template_view_arrange_eligible_act_get_assert_xlsx_returned(
    client,
    user,
    business_area,
    program,
    source_pp,
    eligible_payment,
    url_top_up_template,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_LIST], business_area, program)

    response = client.get(url_top_up_template)

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def test_download_top_up_template_view_arrange_no_eligible_payments_act_get_assert_400(
    client,
    user,
    business_area,
    program,
    source_pp,
    url_top_up_template,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_LIST], business_area, program)

    response = client.get(url_top_up_template)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_download_top_up_template_view_arrange_follow_up_origin_act_get_assert_400(
    client,
    user,
    business_area,
    program,
    cycle,
    currency_pln,
    url_top_up_template,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_LIST], business_area, program)
    follow_up_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        created_by=user,
        currency=currency_pln,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        name="FU PP",
    )
    follow_up_url = reverse(
        "api:payments:payment-plans-download-top-up-template",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "pk": follow_up_pp.pk,
        },
    )

    response = client.get(follow_up_url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def _build_xlsx(rows: list[list], headers: list[str] | None = None) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = XlsxTopUpCreateImportService.TITLE
    ws.append(headers or ["household_unicef_id", "entitlement_quantity"])
    for row in rows:
        ws.append(row)
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_create_top_up_from_xlsx_view_arrange_valid_file_act_post_assert_201(
    get_exchange_rate_mock: Any,
    client,
    user,
    business_area,
    program,
    source_pp,
    eligible_payment,
    url_create_top_up_from_xlsx,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(
        user,
        [Permissions.PM_CREATE, Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS],
        business_area,
        program,
    )
    file_bytes = _build_xlsx([[eligible_payment.household.unicef_id, "100"]])
    upload = SimpleUploadedFile(
        "top_up.xlsx",
        file_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    response = client.post(
        url_create_top_up_from_xlsx,
        {
            "dispersion_start_date": "2026-06-01",
            "dispersion_end_date": "2026-07-01",
            "file": upload,
        },
        format="multipart",
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["plan_type"] == PaymentPlan.PlanType.TOP_UP


def test_create_top_up_from_xlsx_view_arrange_unknown_household_act_post_assert_400_with_errors(
    client,
    user,
    business_area,
    program,
    source_pp,
    eligible_payment,
    url_create_top_up_from_xlsx,
    create_user_role_with_permissions: Any,
):
    create_user_role_with_permissions(
        user,
        [Permissions.PM_CREATE, Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS],
        business_area,
        program,
    )
    file_bytes = _build_xlsx([["HH-FAKE-9999", "100"]])
    upload = SimpleUploadedFile(
        "top_up.xlsx",
        file_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    response = client.post(
        url_create_top_up_from_xlsx,
        {
            "dispersion_start_date": "2026-06-01",
            "dispersion_end_date": "2026-07-01",
            "file": upload,
        },
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    errors = response.json()
    assert any("not eligible" in error["message"] for error in errors)
