from datetime import timezone as dt_timezone
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Any, Callable
from unittest.mock import MagicMock, Mock, patch
from zipfile import BadZipFile

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    ApprovalProcessFactory,
    BusinessAreaFactory,
    CurrencyFactory,
    DeliveryMechanismFactory,
    FileTempFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FundsCommitmentGroupFactory,
    FundsCommitmentItemFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    PaymentPlanSplitFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RuleCommitFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.api.views import PaymentPlanViewSet
from hope.apps.payment.xlsx.xlsx_error import XlsxError
from hope.models import (
    FileTemp,
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
    Program,
    Rule,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def payment_plan_actions_context(
    api_client: Callable,
    business_area: Any,
) -> dict[str, Any]:
    partner = PartnerFactory(name="unittest")
    user = UserFactory(partner=partner)
    program_active = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program_active)
    client = api_client(user)
    CurrencyFactory(code="USD", name="United States Dollar")
    currency_pln = CurrencyFactory(code="PLN", name="Polish Zloty")
    pp = PaymentPlanFactory(
        unicef_id="PP-0060-23-0.000.001",
        name="DRAFT PP",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.DRAFT,
        created_by=user,
        created_at=timezone.datetime(2022, 2, 24, tzinfo=dt_timezone.utc),
        currency=currency_pln,
    )
    purpose = PaymentPlanPurposeFactory(business_area=business_area)
    pp.payment_plan_purposes.add(purpose)
    url_kwargs = {
        "business_area_slug": business_area.slug,
        "program_code": program_active.code,
        "pk": pp.pk,
    }
    url_kwargs_ba_program = {
        "business_area_slug": business_area.slug,
        "program_code": program_active.code,
    }
    return {
        "business_area": business_area,
        "partner": partner,
        "user": user,
        "client": client,
        "program_active": program_active,
        "cycle": cycle,
        "pp": pp,
        "purpose": purpose,
        "url_kwargs_ba_program": url_kwargs_ba_program,
        "url_list": reverse("api:payments:payment-plans-list", kwargs=url_kwargs_ba_program),
        "url_lock": reverse("api:payments:payment-plans-lock", kwargs=url_kwargs),
        "url_unlock": reverse("api:payments:payment-plans-unlock", kwargs=url_kwargs),
        "url_exclude_hh": reverse("api:payments:payment-plans-exclude-beneficiaries", kwargs=url_kwargs),
        "url_apply_steficon": reverse("api:payments:payment-plans-apply-engine-formula", kwargs=url_kwargs),
        "url_lock_fsp": reverse("api:payments:payment-plans-lock-fsp", kwargs=url_kwargs),
        "url_unlock_fsp": reverse("api:payments:payment-plans-unlock-fsp", kwargs=url_kwargs),
        "url_export_entitlement_xlsx": reverse("api:payments:payment-plans-entitlement-export-xlsx", kwargs=url_kwargs),
        "url_import_entitlement_xlsx": reverse("api:payments:payment-plans-entitlement-import-xlsx", kwargs=url_kwargs),
        "url_import_entitlement_flat_amount": reverse(
            "api:payments:payment-plans-entitlement-flat-amount", kwargs=url_kwargs
        ),
        "url_custom_exchange_rate": reverse("api:payments:payment-plans-custom-exchange-rate", kwargs=url_kwargs),
        "url_send_for_approval": reverse("api:payments:payment-plans-send-for-approval", kwargs=url_kwargs),
        "url_approval_process_reject": reverse("api:payments:payment-plans-reject", kwargs=url_kwargs),
        "url_approval_process_approve": reverse("api:payments:payment-plans-approve", kwargs=url_kwargs),
        "url_approval_process_authorize": reverse("api:payments:payment-plans-authorize", kwargs=url_kwargs),
        "url_approval_process_mark_as_released": reverse(
            "api:payments:payment-plans-mark-as-released", kwargs=url_kwargs
        ),
        "url_send_to_payment_gate_way": reverse(
            "api:payments:payment-plans-send-to-payment-gateway", kwargs=url_kwargs
        ),
        "url_export_pdf_payment_plan_summary": reverse(
            "api:payments:payment-plans-export-pdf-payment-plan-summary", kwargs=url_kwargs
        ),
        "url_generate_xlsx_with_auth_code": reverse(
            "api:payments:payment-plans-generate-xlsx-with-auth-code", kwargs=url_kwargs
        ),
        "url_send_xlsx_password": reverse("api:payments:payment-plans-send-xlsx-password", kwargs=url_kwargs),
        "url_reconciliation_export_xlsx": reverse(
            "api:payments:payment-plans-reconciliation-export-xlsx", kwargs=url_kwargs
        ),
        "url_reconciliation_import_xlsx": reverse(
            "api:payments:payment-plans-reconciliation-import-xlsx", kwargs=url_kwargs
        ),
        "url_pp_split": reverse("api:payments:payment-plans-split", kwargs=url_kwargs),
        "url_create_follow_up": reverse("api:payments:payment-plans-create-follow-up", kwargs=url_kwargs),
        "url_funds_commitments": reverse("api:payments:payment-plans-assign-funds-commitments", kwargs=url_kwargs),
        "url_pp_close": reverse("api:payments:payment-plans-close", kwargs=url_kwargs),
        "url_pp_abort": reverse("api:payments:payment-plans-abort", kwargs=url_kwargs),
        "url_pp_reactivate_abort": reverse("api:payments:payment-plans-reactivate-abort", kwargs=url_kwargs),
    }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_CREATE], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_pp(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    data = {
        "dispersion_start_date": "2025-02-01",
        "dispersion_end_date": "2099-03-01",
        "currency": "USD",
        "target_population_id": str(payment_plan_actions_context["pp"].id),
    }
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_list"],
        data,
        format="json",
    )

    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["currency"] == "USD"
        assert resp_data["status"] == "OPEN"


def test_create_pp_validation_errors(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_CREATE],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_list"],
        {"target_population_id": str(payment_plan_actions_context["pp"].pk)},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "dispersion_start_date" in response.json()
    assert "dispersion_end_date" in response.json()
    assert "currency" in response.json()


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_LOCK_AND_UNLOCK], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pp_lock(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.OPEN
    payment_plan_actions_context["pp"].save()
    PaymentFactory(parent=payment_plan_actions_context["pp"])
    response = payment_plan_actions_context["client"].get(payment_plan_actions_context["url_lock"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Payment Plan locked"}


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_LOCK_AND_UNLOCK], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pp_unlock(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].save()

    response = payment_plan_actions_context["client"].get(payment_plan_actions_context["url_unlock"])
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Payment Plan unlocked"}


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_CREATE], status.HTTP_204_NO_CONTENT),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_payment_plan_delete(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    pp = PaymentPlanFactory(
        name="new pp for delete test",
        business_area=payment_plan_actions_context["business_area"],
        program_cycle=payment_plan_actions_context["cycle"],
        status=PaymentPlan.Status.OPEN,
        created_by=payment_plan_actions_context["user"],
    )
    delete_url = reverse(
        "api:payments:payment-plans-detail",
        kwargs={
            "business_area_slug": payment_plan_actions_context["business_area"].slug,
            "program_code": payment_plan_actions_context["program_active"].code,
            "pk": str(pp.pk),
        },
    )
    response = payment_plan_actions_context["client"].delete(delete_url)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_204_NO_CONTENT:
        assert PaymentPlan.objects.filter(name="new pp for delete test").count() == 1
        assert PaymentPlan.objects.filter(name="new pp for delete test").first().status == PaymentPlan.Status.DRAFT


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_exclude_beneficiaries(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].save()
    data = {
        "excluded_households_ids": ["HH-1", "HH-2"],
        "exclusion_reason": "Test Reason",
    }
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_exclude_hh"],
        data,
        format="json",
    )

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["background_action_status"] == "EXCLUDE_BENEFICIARIES"


def test_exclude_beneficiaries_validation_errors(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )

    response_1 = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_exclude_hh"],
        {"excluded_households_ids": ["HH-1"]},
        format="json",
    )
    assert response_1.status_code == status.HTTP_400_BAD_REQUEST
    assert "Beneficiary can be excluded only for 'Open' or 'Locked' status of Payment Plan" in response_1.data

    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].save()
    response_2 = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_exclude_hh"],
        {"excluded_households_ids": ["HH-1", "HH-1"]},
        format="json",
    )
    assert response_2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Duplicate IDs are not allowed." in response_2.data["excluded_households_ids"][0]

    response_3 = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_exclude_hh"],
        {},
        format="json",
    )
    assert response_3.status_code == status.HTTP_400_BAD_REQUEST
    assert "excluded_households_ids" in response_3.json()


@patch("hope.apps.payment.api.views.payment_plan_apply_custom_exchange_rate_async_task")
def test_apply_custom_exchange_rate(
    mock_delay: Mock,
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_CUSTOM_EXCHANGE_RATE],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_REVIEW
    payment_plan_actions_context["pp"].save(update_fields=["status"])

    with TestCase.captureOnCommitCallbacks(execute=True):
        response = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_custom_exchange_rate"],
            {
                "unore_exchange_rate": "2.00000000",
                "custom_exchange_rate": "1.25000000",
            },
            format="json",
        )

    payment_plan_actions_context["pp"].refresh_from_db(
        fields=[
            "background_action_status",
            "custom_exchange_rate",
            "exchange_rate",
            "custom_exchange_rate_set_by",
        ]
    )
    assert response.status_code == status.HTTP_200_OK
    assert (
        payment_plan_actions_context["pp"].background_action_status
        == PaymentPlan.BackgroundActionStatus.APPLYING_CUSTOM_EXCHANGE_RATE
    )
    assert payment_plan_actions_context["pp"].custom_exchange_rate is True
    assert payment_plan_actions_context["pp"].exchange_rate == Decimal("1.25000000")
    assert payment_plan_actions_context["pp"].custom_exchange_rate_set_by == payment_plan_actions_context["user"]
    mock_delay.assert_called_once_with(payment_plan_actions_context["pp"])


def test_apply_custom_exchange_rate_validation_errors(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_CUSTOM_EXCHANGE_RATE],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_custom_exchange_rate"],
        {
            "unore_exchange_rate": "2.00000000",
            "custom_exchange_rate": "1.25000000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "User can only set custom exchange rate for OPEN/IN_REVIEW Payment Plan" in response.data


def test_apply_custom_exchange_rate_requires_one_rate_value(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_CUSTOM_EXCHANGE_RATE],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_REVIEW
    payment_plan_actions_context["pp"].save(update_fields=["status"])

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_custom_exchange_rate"],
        {
            "unore_exchange_rate": None,
            "custom_exchange_rate": None,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["non_field_errors"] == ["One of custom_exchange_rate or unore_exchange_rate must be provided."]


@patch("hope.apps.payment.api.views.payment_plan_apply_custom_exchange_rate_async_task")
def test_apply_unore_exchange_rate_clears_custom_flag(
    mock_delay: Mock,
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_CUSTOM_EXCHANGE_RATE],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_REVIEW
    payment_plan_actions_context["pp"].custom_exchange_rate = True
    payment_plan_actions_context["pp"].exchange_rate = Decimal("1.25000000")
    payment_plan_actions_context["pp"].custom_exchange_rate_set_by = payment_plan_actions_context["user"]
    payment_plan_actions_context["pp"].save(
        update_fields=["status", "custom_exchange_rate", "exchange_rate", "custom_exchange_rate_set_by"]
    )

    with TestCase.captureOnCommitCallbacks(execute=True):
        response = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_custom_exchange_rate"],
            {
                "unore_exchange_rate": "2.00000000",
                "custom_exchange_rate": None,
            },
            format="json",
        )

    payment_plan_actions_context["pp"].refresh_from_db(
        fields=[
            "background_action_status",
            "custom_exchange_rate",
            "exchange_rate",
            "custom_exchange_rate_set_by",
        ]
    )
    assert response.status_code == status.HTTP_200_OK
    assert payment_plan_actions_context["pp"].custom_exchange_rate is False
    assert payment_plan_actions_context["pp"].exchange_rate == Decimal("2.00000000")
    assert payment_plan_actions_context["pp"].custom_exchange_rate_set_by is None
    mock_delay.assert_called_once_with(payment_plan_actions_context["pp"])


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_apply_engine_formula_pp(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    rule_for_pp = RuleCommitFactory(rule__type=Rule.TYPE_PAYMENT_PLAN, rule__enabled=True, version=11).rule
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].save()
    payment_plan_actions_context["pp"].refresh_from_db()
    data = {
        "engine_formula_rule_id": str(rule_for_pp.pk),
        "version": payment_plan_actions_context["pp"].version,
    }
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_apply_steficon"],
        data,
        format="json",
    )

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        payment_plan_actions_context["pp"].refresh_from_db(fields=["background_action_status"])
        assert payment_plan_actions_context["pp"].background_action_status == "RULE_ENGINE_RUN"
        assert "RULE_ENGINE_RUN" in resp_data["background_action_status"]


def test_apply_engine_formula_pp_validation_errors(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    rule_for_pp = RuleCommitFactory(rule__type=Rule.TYPE_PAYMENT_PLAN, rule__enabled=False, version=22).rule
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].save()

    data = {
        "engine_formula_rule_id": str(rule_for_pp.pk),
        "version": payment_plan_actions_context["pp"].version,
    }
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_apply_steficon"],
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "This engine rule is not enabled or is deprecated." in response.data

    payment_plan_actions_context["pp"].status = PaymentPlan.Status.TP_OPEN
    payment_plan_actions_context["pp"].save()
    data = {
        "engine_formula_rule_id": str(rule_for_pp.pk),
        "version": payment_plan_actions_context["pp"].version,
    }
    response_2 = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_apply_steficon"],
        data,
        format="json",
    )

    assert response_2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Not allowed to run engine formula within status TP_OPEN." in response_2.data

    response_3 = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_apply_steficon"],
        {},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "engine_formula_rule_id" in response_3.data


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_LOCK_AND_UNLOCK_FSP], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pp_fsp_lock(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].financial_service_provider = FinancialServiceProviderFactory()
    payment_plan_actions_context["pp"].delivery_mechanism = DeliveryMechanismFactory()
    payment_plan_actions_context["pp"].save()
    PaymentFactory(parent=payment_plan_actions_context["pp"], entitlement_quantity=999)
    response = payment_plan_actions_context["client"].get(payment_plan_actions_context["url_lock_fsp"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Payment Plan FSP locked"}


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_LOCK_AND_UNLOCK_FSP], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pp_fsp_unlock(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED_FSP
    payment_plan_actions_context["pp"].save()

    response = payment_plan_actions_context["client"].get(payment_plan_actions_context["url_unlock_fsp"])
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Payment Plan FSP unlocked"}


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_VIEW_LIST], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pp_entitlement_export_xlsx(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
    django_capture_on_commit_callbacks: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].save()

    with django_capture_on_commit_callbacks(execute=True):
        response = payment_plan_actions_context["client"].get(
            payment_plan_actions_context["url_export_entitlement_xlsx"]
        )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        payment_plan_actions_context["pp"].refresh_from_db()
        assert payment_plan_actions_context["pp"].has_export_file is True


def test_pp_entitlement_export_xlsx_invalid_status(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_VIEW_LIST],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.OPEN
    payment_plan_actions_context["pp"].save()

    response = payment_plan_actions_context["client"].get(payment_plan_actions_context["url_export_entitlement_xlsx"])
    assert status.HTTP_400_BAD_REQUEST
    assert "You can only export Payment List for LOCKED Payment Plan" in response.data


@patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_pp_entitlement_import_xlsx(
    mock_exchange_rate: Any,
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].save()
    payment_1 = PaymentFactory(
        parent=payment_plan_actions_context["pp"],
        status=Payment.STATUS_PENDING,
    )
    payment_2 = PaymentFactory(
        unicef_id="RCPT-0060-24-0.000.022",
        parent=payment_plan_actions_context["pp"],
        status=Payment.STATUS_PENDING,
    )
    payment_1.unicef_id = "RCPT-0060-24-0.000.011"
    payment_1.save()
    payment_2.unicef_id = "RCPT-0060-24-0.000.022"
    payment_2.save()

    file = BytesIO(Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/pp_entitlement_valid.xlsx").read_bytes())
    file.name = "pp_entitlement_valid.xlsx"
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_import_entitlement_xlsx"],
        {"file": file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    pp = response.json()
    assert pp["background_action_status"] == "XLSX_IMPORTING_ENTITLEMENTS"
    assert pp["imported_file_name"].startswith("pp_entitlement_valid") is True


def test_pp_entitlement_flat_value_invalid_status(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.OPEN
    payment_plan_actions_context["pp"].save()

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_import_entitlement_flat_amount"],
        {"flat_amount_value": "111"},
        format="json",
    )
    assert status.HTTP_400_BAD_REQUEST
    assert "User can only set entitlements for LOCKED Payment Plan" in response.data

    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context[
        "pp"
    ].background_action_status = PaymentPlan.BackgroundActionStatus.IMPORTING_ENTITLEMENTS
    payment_plan_actions_context["pp"].save()

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_import_entitlement_flat_amount"],
        {"flat_amount_value": "222"},
        format="json",
    )
    assert status.HTTP_400_BAD_REQUEST
    assert "Import in progress" in response.data


@patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_pp_entitlement_import_flat_value(
    mock_exchange_rate: Any,
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].background_action_status = None
    payment_plan_actions_context["pp"].save()
    PaymentFactory(
        parent=payment_plan_actions_context["pp"],
        status=Payment.STATUS_PENDING,
    )
    # check serializer validation
    response400 = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_import_entitlement_flat_amount"],
        {"version": payment_plan_actions_context["pp"].version},
        format="json",
    )
    assert response400.status_code == status.HTTP_400_BAD_REQUEST
    assert "flat_amount_value" in response400.data

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_import_entitlement_flat_amount"],
        {"flat_amount_value": "25.11", "version": payment_plan_actions_context["pp"].version},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    pp = response.json()
    assert pp["background_action_status"] == "IMPORTING_ENTITLEMENTS"
    assert pp["flat_amount_value"] == "25.11"


def test_pp_entitlement_import_xlsx_status_invalid(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.OPEN
    payment_plan_actions_context["pp"].save()
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    test_file = SimpleUploadedFile("test.xlsx", b"123", content_type="application/vnd.ms-excel")
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_import_entitlement_xlsx"],
        {"file": test_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "User can only import for LOCKED Payment Plan" in response.data[0]


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_SEND_FOR_APPROVAL], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_send_for_approval(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED_FSP
    payment_plan_actions_context["pp"].save()
    response = payment_plan_actions_context["client"].get(payment_plan_actions_context["url_send_for_approval"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json()["status"] == "IN_APPROVAL"


@pytest.mark.parametrize(
    ("permissions", "expected_status", "payment_plan_status"),
    [
        (
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE, Permissions.PM_VIEW_LIST],
            status.HTTP_200_OK,
            PaymentPlan.Status.IN_APPROVAL,
        ),
        (
            [Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE, Permissions.PM_VIEW_LIST],
            status.HTTP_200_OK,
            PaymentPlan.Status.IN_AUTHORIZATION,
        ),
        (
            [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW, Permissions.PM_VIEW_LIST],
            status.HTTP_200_OK,
            PaymentPlan.Status.IN_REVIEW,
        ),
        ([], status.HTTP_403_FORBIDDEN, PaymentPlan.Status.IN_APPROVAL),
    ],
)
def test_approval_process_reject(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    payment_plan_status: PaymentPlan.Status,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    ApprovalProcessFactory(payment_plan=payment_plan_actions_context["pp"])
    payment_plan_actions_context["pp"].status = payment_plan_status
    payment_plan_actions_context["pp"].save()
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_approval_process_reject"],
        {"comment": "test123"},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json()["status"] == "LOCKED_FSP"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_ACCEPTANCE_PROCESS_APPROVE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_approval_process_approve(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    ApprovalProcessFactory(payment_plan=payment_plan_actions_context["pp"])
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_APPROVAL
    payment_plan_actions_context["pp"].save()
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_approval_process_approve"],
        {"comment": "test123"},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json()["status"] == "IN_AUTHORIZATION"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_approval_process_authorize(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    ApprovalProcessFactory(payment_plan=payment_plan_actions_context["pp"])
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_AUTHORIZATION
    payment_plan_actions_context["pp"].save()
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_approval_process_authorize"],
        {"comment": "test123"},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json()["status"] == "IN_REVIEW"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_approval_process_mark_as_released(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    ApprovalProcessFactory(payment_plan=payment_plan_actions_context["pp"])
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_REVIEW
    payment_plan_actions_context["pp"].save()
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_approval_process_mark_as_released"],
        {"comment": "test123"},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json()["status"] == "ACCEPTED"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_SEND_TO_PAYMENT_GATEWAY], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pp_send_to_payment_gateway(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    fsp = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="123",
    )
    PaymentPlanSplitFactory(payment_plan=payment_plan_actions_context["pp"])
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.ACCEPTED
    payment_plan_actions_context["pp"].financial_service_provider = fsp
    payment_plan_actions_context["pp"].save()
    PaymentFactory(parent=payment_plan_actions_context["pp"])
    response = payment_plan_actions_context["client"].get(payment_plan_actions_context["url_send_to_payment_gate_way"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json()["status"] == "ACCEPTED"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_DOWNLOAD_FSP_AUTH_CODE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_generate_xlsx_with_auth_code(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    fsp_xlsx_template_id = FinancialServiceProviderXlsxTemplateFactory().pk
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    test_file = FileTemp.objects.create(
        object_id=payment_plan_actions_context["pp"].pk,
        content_type=get_content_type_for_model(payment_plan_actions_context["pp"]),
        created_by=payment_plan_actions_context["user"],
    )
    fsp = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="123",
    )
    PaymentPlanSplitFactory(payment_plan=payment_plan_actions_context["pp"])
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_APPROVAL
    payment_plan_actions_context["pp"].financial_service_provider = fsp
    payment_plan_actions_context["pp"].save()
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_generate_xlsx_with_auth_code"],
        {"fsp_xlsx_template_id": fsp_xlsx_template_id},
        format="json",
    )

    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Payment List Per FSP export is only available for ACCEPTED or FINISHED Payment Plans." in response.data

        payment_plan_actions_context["pp"].status = PaymentPlan.Status.ACCEPTED
        payment_plan_actions_context["pp"].export_file_per_fsp = test_file
        payment_plan_actions_context["pp"].save()
        response_2 = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_generate_xlsx_with_auth_code"],
            {"fsp_xlsx_template_id": fsp_xlsx_template_id},
            format="json",
        )

        assert response_2.status_code == status.HTTP_400_BAD_REQUEST
        assert "Export failed: Payment Plan already has created exported file." in response_2.data

        payment_plan_actions_context["pp"].export_file_per_fsp = None
        payment_plan_actions_context["pp"].save()
        payment = PaymentFactory(parent=payment_plan_actions_context["pp"], status=Payment.STATUS_PENDING)
        response_3 = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_generate_xlsx_with_auth_code"],
            {"fsp_xlsx_template_id": fsp_xlsx_template_id},
            format="json",
        )

        assert response_3.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Export failed: There could be not Pending Payments and FSP communication channel should be set to API."
            in response_3.data
        )

        payment.status = Payment.STATUS_SENT_TO_PG
        payment.save()
        response_ok = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_generate_xlsx_with_auth_code"],
            {"fsp_xlsx_template_id": fsp_xlsx_template_id},
            format="json",
        )

        assert response_ok.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_SEND_XLSX_PASSWORD], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_send_xlsx_password(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.ACCEPTED
    payment_plan_actions_context["pp"].save()

    response = payment_plan_actions_context["client"].get(payment_plan_actions_context["url_send_xlsx_password"])
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_VIEW_LIST], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_reconciliation_export_xlsx(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.ACCEPTED
    payment_plan_actions_context["pp"].save()
    PaymentFactory(parent=payment_plan_actions_context["pp"], status=Payment.STATUS_PENDING)

    response = payment_plan_actions_context["client"].get(
        payment_plan_actions_context["url_reconciliation_export_xlsx"]
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert "id" in response.data

        payment_plan_actions_context["pp"].eligible_payments.delete()
        response_1 = payment_plan_actions_context["client"].get(
            payment_plan_actions_context["url_reconciliation_export_xlsx"]
        )
        assert response_1.status_code == status.HTTP_400_BAD_REQUEST
        assert "Export failed: The Payment List is empty." in response_1.data

        payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_APPROVAL
        payment_plan_actions_context["pp"].save()
        response_2 = payment_plan_actions_context["client"].get(
            payment_plan_actions_context["url_reconciliation_export_xlsx"]
        )
        assert response_2.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Payment List Per FSP export is only available for ACCEPTED or FINISHED Payment Plans." in response_2.data
        )


def test_pp_reconciliation_import_xlsx_invalid(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.OPEN
    payment_plan_actions_context["pp"].save()
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    test_file = SimpleUploadedFile("test.xlsx", b"123", content_type="application/vnd.ms-excel")
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_reconciliation_import_xlsx"],
        {"file": test_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Payment List Per FSP export is only available for ACCEPTED or FINISHED Payment Plans." in response.data[0]

    fsp_api = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="123",
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.ACCEPTED
    payment_plan_actions_context["pp"].financial_service_provider = fsp_api
    payment_plan_actions_context["pp"].save()
    response_2 = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_reconciliation_import_xlsx"],
        {"file": test_file},
        format="multipart",
    )
    assert response_2.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Manual reconciliation import is not available for payment plans using payment gateway." in response_2.data[0]
    )

    fsp_xlsx = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        payment_gateway_id="1234",
    )
    payment_plan_actions_context["pp"].financial_service_provider = fsp_xlsx
    payment_plan_actions_context["pp"].use_payment_gateway = True
    payment_plan_actions_context["pp"].save(update_fields=["financial_service_provider", "use_payment_gateway"])
    response_3 = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_reconciliation_import_xlsx"],
        {"file": test_file},
        format="multipart",
    )
    assert response_3.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Manual reconciliation import is not available for payment plans using payment gateway." in response_3.data[0]
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_SPLIT], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_split(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    fsp = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="123",
    )
    split = PaymentPlanSplitFactory(payment_plan=payment_plan_actions_context["pp"], sent_to_payment_gateway=True)
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_APPROVAL
    payment_plan_actions_context["pp"].financial_service_provider = fsp
    payment_plan_actions_context["pp"].save()
    data = {"payments_no": 1, "split_type": PaymentPlanSplit.SplitType.BY_RECORDS}
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_pp_split"],
        data,
        format="json",
    )

    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Payment plan is already sent to payment gateway" in response.data

        split.sent_to_payment_gateway = False
        split.save()
        response_2 = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_pp_split"],
            data,
            format="json",
        )
        assert response_2.status_code == status.HTTP_400_BAD_REQUEST
        assert "Payment plan must be accepted to make a split" in response_2.data

        payment_plan_actions_context["pp"].status = PaymentPlan.Status.ACCEPTED
        payment_plan_actions_context["pp"].save()
        payment_plan_actions_context["pp"].eligible_payments.delete()
        response_3 = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_pp_split"],
            {"split_type": PaymentPlanSplit.SplitType.BY_RECORDS},
            format="json",
        )
        assert response_3.status_code == status.HTTP_400_BAD_REQUEST
        assert "Payment Number is required for split by records" in response_3.data

        fsp_api = FinancialServiceProviderFactory(
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            payment_gateway_id="123",
        )
        PaymentFactory.create_batch(
            3,
            parent=payment_plan_actions_context["pp"],
            status=Payment.STATUS_PENDING,
            financial_service_provider=fsp_api,
        )
        with patch.object(PaymentPlanSplit, "MAX_CHUNKS", 2):
            response_4 = payment_plan_actions_context["client"].post(
                payment_plan_actions_context["url_pp_split"],
                data,
                format="json",
            )
            assert response_4.status_code == status.HTTP_400_BAD_REQUEST
            assert "Cannot split Payment Plan into more than 2 parts" in response_4.data

        with patch.object(PaymentPlanSplit, "MIN_NO_OF_PAYMENTS_IN_CHUNK", 1):
            response_ok = payment_plan_actions_context["client"].post(
                payment_plan_actions_context["url_pp_split"],
                {"payments_no": 1, "split_type": PaymentPlanSplit.SplitType.BY_RECORDS},
                format="json",
            )
            assert response_ok.status_code == status.HTTP_200_OK
        assert "id" in response_ok.data


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_EXPORT_PDF_SUMMARY], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_export_pdf_payment_plan_summary(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].save()
    PaymentFactory(parent=payment_plan_actions_context["pp"])
    response = payment_plan_actions_context["client"].get(
        payment_plan_actions_context["url_export_pdf_payment_plan_summary"]
    )

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert "id" in response.json()


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_CREATE], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_follow_up(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    PaymentFactory(parent=payment_plan_actions_context["pp"], status=Payment.STATUS_FORCE_FAILED)

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_create_follow_up"],
        {
            "dispersion_start_date": "2024-01-01",
            "dispersion_end_date": "2026-01-01",
        },
        format="json",
    )
    assert response.status_code == expected_status

    if expected_status == status.HTTP_201_CREATED:
        data = response.json()
        assert "id" in data
        assert data["plan_type"] == PaymentPlan.PlanType.FOLLOW_UP
        assert "id" in data["source_payment_plan"]
        assert data["name"] == "DRAFT PP Follow Up"
        assert data["dispersion_start_date"] == "2024-01-01"
        assert data["dispersion_end_date"] == "2026-01-01"
        assert data["currency"] == "PLN"
        purpose = payment_plan_actions_context["purpose"]
        assert data["payment_plan_purposes"] == [{"id": str(purpose.id), "name": purpose.name}]


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_ASSIGN_FUNDS_COMMITMENTS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_assign_funds_commitments(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_REVIEW
    payment_plan_actions_context["pp"].save()

    group = FundsCommitmentGroupFactory()

    funds_commitment_item = FundsCommitmentItemFactory(
        funds_commitment_group=group,
        office=payment_plan_actions_context["business_area"],
        rec_serial_number=999,
        payment_plan=None,
    )
    assert funds_commitment_item.payment_plan is None

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_funds_commitments"],
        {"fund_commitment_items_ids": ["999"]},
        format="json",
    )
    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        assert "id" in response.json()
        funds_commitment_item.refresh_from_db()
        assert funds_commitment_item.payment_plan_id == payment_plan_actions_context["pp"].pk


def test_assign_funds_commitments_validation_errors(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_ASSIGN_FUNDS_COMMITMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_funds_commitments"],
        {"fund_commitment_items_ids": ["333"]},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Payment plan must be in review" in response.json()

    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_REVIEW
    payment_plan_actions_context["pp"].save()
    other_pp = PaymentPlanFactory(
        business_area=payment_plan_actions_context["business_area"],
        program_cycle=payment_plan_actions_context["cycle"],
        status=PaymentPlan.Status.DRAFT,
        created_by=payment_plan_actions_context["user"],
    )
    group = FundsCommitmentGroupFactory()
    FundsCommitmentItemFactory(
        funds_commitment_group=group,
        office=None,
        rec_serial_number=333,
        payment_plan=other_pp,
    )

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_funds_commitments"],
        {"fund_commitment_items_ids": ["333"]},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Chosen Funds Commitments are already assigned to different Payment Plan" in response.json()

    FundsCommitmentItemFactory(
        funds_commitment_group=group,
        office=None,
        rec_serial_number=2355,
        payment_plan=None,
    )
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_funds_commitments"],
        {"fund_commitment_items_ids": ["2355"]},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Chosen Funds Commitments have wrong Business Area" in response.json()


def test_fsp_xlsx_template_list(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_EXPORT_XLSX_FOR_FSP],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )

    xlsx_1 = FinancialServiceProviderXlsxTemplateFactory(name="XLSX_1")
    xlsx_2 = FinancialServiceProviderXlsxTemplateFactory(name="XLSX_2")
    xlsx_3 = FinancialServiceProviderXlsxTemplateFactory(name="Other BA")

    financial_service_provider = FinancialServiceProviderFactory()
    financial_service_provider.allowed_business_areas.set([payment_plan_actions_context["business_area"]])
    fsp_2 = FinancialServiceProviderFactory()

    financial_service_provider.xlsx_templates.set([xlsx_1, xlsx_2])
    fsp_2.xlsx_templates.set([xlsx_3])

    response = payment_plan_actions_context["client"].get(
        reverse(
            "api:payments:payment-plans-fsp-xlsx-template-list",
            kwargs=payment_plan_actions_context["url_kwargs_ba_program"],
        ),
        {"fund_commitment_items_ids": ["333"]},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 2
    assert results[0]["name"] == "XLSX_1"
    assert results[1]["name"] == "XLSX_2"


@pytest.mark.parametrize(
    ("permissions", "expected_status", "pp_status"),
    [
        ([Permissions.PM_CLOSE_FINISHED], status.HTTP_200_OK, PaymentPlan.Status.FINISHED),
        ([Permissions.PM_CLOSE_FINISHED], status.HTTP_400_BAD_REQUEST, PaymentPlan.Status.ACCEPTED),
        ([], status.HTTP_403_FORBIDDEN, PaymentPlan.Status.FINISHED),
    ],
)
def test_pp_close(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
    pp_status: str,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = pp_status
    payment_plan_actions_context["pp"].save()
    payment_plan_actions_context["pp"].refresh_from_db()

    assert payment_plan_actions_context["pp"].status == pp_status
    response = payment_plan_actions_context["client"].get(payment_plan_actions_context["url_pp_close"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Payment Plan closed"}

    if expected_status == status.HTTP_400_BAD_REQUEST:
        assert response.json()[0] == f"Close Payment Plan is possible only within Status {PaymentPlan.Status.FINISHED}"


@pytest.mark.parametrize(
    ("permissions", "expected_status", "pp_status"),
    [
        ([Permissions.PM_ABORT], status.HTTP_200_OK, PaymentPlan.Status.IN_REVIEW),
        ([Permissions.PM_ABORT], status.HTTP_400_BAD_REQUEST, PaymentPlan.Status.ACCEPTED),
        ([], status.HTTP_403_FORBIDDEN, PaymentPlan.Status.OPEN),
    ],
)
def test_pp_abort(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
    pp_status: str,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = pp_status
    payment_plan_actions_context["pp"].save()
    payment_plan_actions_context["pp"].refresh_from_db()

    assert payment_plan_actions_context["pp"].status == pp_status
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_pp_abort"],
        {"abort_comment": "test comment"},
        format="json",
    )

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Payment Plan aborted"}
        payment_plan_actions_context["pp"].refresh_from_db()
        assert payment_plan_actions_context["pp"].status == PaymentPlan.Status.ABORTED
        assert payment_plan_actions_context["pp"].abort_comment == "test comment"

    if expected_status == status.HTTP_400_BAD_REQUEST:
        assert response.json()[0] == f"Abort Payment Plan is not possible within Status {pp_status}"


@pytest.mark.parametrize(
    ("permissions", "expected_status", "pp_status"),
    [
        ([Permissions.PM_REACTIVATE_ABORT], status.HTTP_200_OK, PaymentPlan.Status.ABORTED),
        ([Permissions.PM_REACTIVATE_ABORT], status.HTTP_400_BAD_REQUEST, PaymentPlan.Status.OPEN),
        ([], status.HTTP_403_FORBIDDEN, PaymentPlan.Status.ABORTED),
    ],
)
def test_pp_reactivate_abort(
    payment_plan_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
    pp_status: str,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        permissions,
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = pp_status
    payment_plan_actions_context["pp"].save()
    payment_plan_actions_context["pp"].refresh_from_db()

    assert payment_plan_actions_context["pp"].status == pp_status
    response = payment_plan_actions_context["client"].get(payment_plan_actions_context["url_pp_reactivate_abort"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Payment Plan reactivate abort"}

    if expected_status == status.HTTP_400_BAD_REQUEST:
        assert (
            response.json()[0]
            == f"Reactivate Aborted Payment Plan is possible only within Status {PaymentPlan.Status.ABORTED}"
        )


def test_create_pp_without_target_population_id_returns_400(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_CREATE],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_list"],
        {"dispersion_start_date": "2025-02-01", "dispersion_end_date": "2099-03-01", "currency": "USD"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "target_population_id is required" in response.data[0]


def test_apply_engine_formula_without_version_skips_concurrency_check(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    rule = RuleCommitFactory(rule__type=Rule.TYPE_PAYMENT_PLAN, rule__enabled=True, version=12).rule
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].save()

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_apply_steficon"],
        {"engine_formula_rule_id": str(rule.pk)},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK


def test_apply_engine_formula_rejects_when_rule_engine_already_running(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    rule = RuleCommitFactory(rule__type=Rule.TYPE_PAYMENT_PLAN, rule__enabled=True, version=13).rule
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].background_action_status = PaymentPlan.BackgroundActionStatus.RULE_ENGINE_RUN
    payment_plan_actions_context["pp"].save()

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_apply_steficon"],
        {"engine_formula_rule_id": str(rule.pk), "version": payment_plan_actions_context["pp"].version},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Rule Engine run in progress" in response.data


def test_entitlement_import_xlsx_rejects_when_already_importing(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context[
        "pp"
    ].background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS
    payment_plan_actions_context["pp"].save()
    test_file = SimpleUploadedFile("test.xlsx", b"123", content_type="application/vnd.ms-excel")
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_import_entitlement_xlsx"],
        {"file": test_file},
        format="multipart",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Import in progress" in response.data[0]


def test_entitlement_import_xlsx_returns_400_on_validation_errors(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].save()
    test_file = SimpleUploadedFile("test.xlsx", b"123", content_type="application/vnd.ms-excel")
    with patch("hope.apps.payment.api.views.XlsxPaymentPlanImportService") as mock_cls:
        instance = mock_cls.return_value
        instance.errors = [XlsxError(sheet="Sheet1", coordinates="A1", message="Bad row")]
        response = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_import_entitlement_xlsx"],
            {"file": test_file},
            format="multipart",
        )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()
    assert body[0]["sheet"] == "Sheet1"
    assert body[0]["message"] == "Bad row"


@patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_entitlement_import_xlsx_copies_existing_imported_file(
    mock_exchange_rate: Any,
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    pp = payment_plan_actions_context["pp"]
    pp.status = PaymentPlan.Status.LOCKED
    pp.imported_file = FileTempFactory(
        object_id=pp.pk,
        content_type=get_content_type_for_model(pp),
        created_by=payment_plan_actions_context["user"],
    )
    pp.save()
    payment_1 = PaymentFactory(parent=pp, status=Payment.STATUS_PENDING)
    payment_2 = PaymentFactory(parent=pp, status=Payment.STATUS_PENDING)
    payment_1.unicef_id = "RCPT-0060-24-0.000.011"
    payment_1.save()
    payment_2.unicef_id = "RCPT-0060-24-0.000.022"
    payment_2.save()

    file = BytesIO(Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/pp_entitlement_valid.xlsx").read_bytes())
    file.name = "pp_entitlement_valid.xlsx"
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_import_entitlement_xlsx"],
        {"file": file},
        format="multipart",
    )
    assert response.status_code == status.HTTP_200_OK


def test_entitlement_flat_amount_without_version_skips_concurrency_check(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.LOCKED
    payment_plan_actions_context["pp"].background_action_status = None
    payment_plan_actions_context["pp"].save()
    PaymentFactory(parent=payment_plan_actions_context["pp"], status=Payment.STATUS_PENDING)

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_import_entitlement_flat_amount"],
        {"flat_amount_value": "10.00"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK


@patch("hope.apps.payment.api.views.payment_plan_apply_custom_exchange_rate_async_task")
def test_apply_custom_exchange_rate_with_version_runs_concurrency_check(
    mock_delay: Mock,
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_CUSTOM_EXCHANGE_RATE],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.IN_REVIEW
    payment_plan_actions_context["pp"].save(update_fields=["status"])

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_custom_exchange_rate"],
        {
            "unore_exchange_rate": "2.00000000",
            "custom_exchange_rate": "1.25000000",
            "version": payment_plan_actions_context["pp"].version,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK


def test_generate_xlsx_with_auth_code_rejects_when_export_in_progress(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_DOWNLOAD_FSP_AUTH_CODE],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.ACCEPTED
    payment_plan_actions_context["pp"].background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING
    payment_plan_actions_context["pp"].save()

    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_generate_xlsx_with_auth_code"],
        {},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Payment List Per FSP export already in progress." in response.data


def _set_pp_for_reconciliation_import(
    payment_plan_actions_context: dict[str, Any], create_user_role_with_permissions: Any
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    fsp_xlsx = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.ACCEPTED
    payment_plan_actions_context["pp"].financial_service_provider = fsp_xlsx
    payment_plan_actions_context["pp"].save()


def test_reconciliation_import_xlsx_returns_400_when_serializer_invalid(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    _set_pp_for_reconciliation_import(payment_plan_actions_context, create_user_role_with_permissions)
    response = payment_plan_actions_context["client"].post(
        payment_plan_actions_context["url_reconciliation_import_xlsx"],
        {},
        format="multipart",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "file" in response.json()


def test_reconciliation_import_xlsx_rejects_bad_zip_file(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    _set_pp_for_reconciliation_import(payment_plan_actions_context, create_user_role_with_permissions)
    test_file = SimpleUploadedFile("test.xlsx", b"not-a-zip", content_type="application/vnd.ms-excel")
    with patch("hope.apps.payment.api.views.XlsxPaymentPlanImportPerFspService") as mock_cls:
        mock_cls.return_value.open_workbook.side_effect = BadZipFile("not a zip")
        response = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_reconciliation_import_xlsx"],
            {"file": test_file},
            format="multipart",
        )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Wrong file type or password protected" in response.data[0]


def test_reconciliation_import_xlsx_returns_400_on_validation_errors(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    _set_pp_for_reconciliation_import(payment_plan_actions_context, create_user_role_with_permissions)
    test_file = SimpleUploadedFile("test.xlsx", b"abc", content_type="application/vnd.ms-excel")
    with patch("hope.apps.payment.api.views.XlsxPaymentPlanImportPerFspService") as mock_cls:
        instance = mock_cls.return_value
        instance.errors = [XlsxError(sheet="Reconciliation", coordinates="B2", message="Missing column")]
        response = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_reconciliation_import_xlsx"],
            {"file": test_file},
            format="multipart",
        )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()
    assert body[0]["sheet"] == "Reconciliation"
    assert body[0]["message"] == "Missing column"


def test_reconciliation_import_xlsx_succeeds(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    _set_pp_for_reconciliation_import(payment_plan_actions_context, create_user_role_with_permissions)
    test_file = SimpleUploadedFile("test.xlsx", b"abc", content_type="application/vnd.ms-excel")
    pp = payment_plan_actions_context["pp"]
    with (
        patch("hope.apps.payment.api.views.XlsxPaymentPlanImportPerFspService") as mock_import_cls,
        patch("hope.apps.payment.api.views.PaymentPlanService") as mock_service_cls,
    ):
        mock_import_cls.return_value.errors = []
        service = MagicMock()
        service.import_xlsx_per_fsp.return_value = pp
        mock_service_cls.return_value = service
        response = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_reconciliation_import_xlsx"],
            {"file": test_file},
            format="multipart",
        )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(pp.pk)
    service.import_xlsx_per_fsp.assert_called_once()


def test_split_with_split_type_no_split_skips_records_branch(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_SPLIT],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    payment_plan_actions_context["pp"].status = PaymentPlan.Status.ACCEPTED
    payment_plan_actions_context["pp"].save()
    PaymentFactory(parent=payment_plan_actions_context["pp"], status=Payment.STATUS_PENDING)

    with patch("hope.apps.payment.api.views.PaymentPlanService") as mock_service_cls:
        mock_service_cls.return_value.split.return_value = None
        response = payment_plan_actions_context["client"].post(
            payment_plan_actions_context["url_pp_split"],
            {"split_type": PaymentPlanSplit.SplitType.NO_SPLIT},
            format="json",
        )
    assert response.status_code == status.HTTP_200_OK
    mock_service_cls.return_value.split.assert_called_once_with(PaymentPlanSplit.SplitType.NO_SPLIT, None)


def test_fsp_xlsx_template_list_without_pagination_returns_flat_response(
    payment_plan_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_user_role_with_permissions(
        payment_plan_actions_context["user"],
        [Permissions.PM_EXPORT_XLSX_FOR_FSP],
        payment_plan_actions_context["business_area"],
        payment_plan_actions_context["program_active"],
    )
    monkeypatch.setattr(PaymentPlanViewSet, "pagination_class", None)
    template = FinancialServiceProviderXlsxTemplateFactory(name="XLSX_FLAT")
    fsp = FinancialServiceProviderFactory()
    fsp.allowed_business_areas.set([payment_plan_actions_context["business_area"]])
    fsp.xlsx_templates.set([template])

    response = payment_plan_actions_context["client"].get(
        reverse(
            "api:payments:payment-plans-fsp-xlsx-template-list",
            kwargs=payment_plan_actions_context["url_kwargs_ba_program"],
        ),
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert isinstance(body, list)
    assert any(item["name"] == "XLSX_FLAT" for item in body)
