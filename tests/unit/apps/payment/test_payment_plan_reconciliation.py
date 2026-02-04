from collections import namedtuple
from datetime import datetime
from decimal import Decimal
import io
from typing import Any

import pytest
import pytz

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)
from hope.models import Payment, PaymentPlan, PaymentVerification, PaymentVerificationPlan, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def base_context(user: User) -> dict[str, Any]:
    business_area = BusinessAreaFactory()
    program = ProgramFactory(business_area=business_area)
    program_cycle = ProgramCycleFactory(program=program)
    registration_data_import = RegistrationDataImportFactory(business_area=business_area, program=program)
    return {
        "business_area": business_area,
        "program": program,
        "program_cycle": program_cycle,
        "registration_data_import": registration_data_import,
        "user": user,
    }


@pytest.fixture
def households_with_individuals(base_context: dict[str, Any]) -> list[dict[str, Any]]:
    households = []
    for _ in range(3):
        household = HouseholdFactory(
            business_area=base_context["business_area"],
            program=base_context["program"],
            registration_data_import=base_context["registration_data_import"],
        )
        households.append({"household": household, "individual": household.head_of_household})
    return households


@pytest.fixture
def payment_plan(base_context: dict[str, Any]) -> PaymentPlan:
    return PaymentPlanFactory(
        created_by=base_context["user"],
        business_area=base_context["business_area"],
        program_cycle=base_context["program_cycle"],
    )


@pytest.fixture
def payment_plan_finished(base_context: dict[str, Any]) -> PaymentPlan:
    return PaymentPlanFactory(
        created_by=base_context["user"],
        business_area=base_context["business_area"],
        program_cycle=base_context["program_cycle"],
        status=PaymentPlan.Status.FINISHED,
    )


@pytest.fixture
def payment_verification_plan(payment_plan_finished: PaymentPlan) -> PaymentVerificationPlan:
    return PaymentVerificationPlanFactory(
        payment_plan=payment_plan_finished,
        status=PaymentVerificationPlan.STATUS_ACTIVE,
    )


RECONCILIATION_STATUS_CASES = [
    pytest.param(-1, Decimal("100.00"), None, Payment.STATUS_ERROR, id="negative_int_error"),
    pytest.param(0, Decimal("0.00"), Decimal("0.00"), Payment.STATUS_NOT_DISTRIBUTED, id="zero_not_distributed"),
    pytest.param(400.10, Decimal("400.23"), Decimal("400.10"), Payment.STATUS_DISTRIBUTION_PARTIAL, id="float_partial"),
    pytest.param(400.23, Decimal("400.23"), Decimal("400.23"), Payment.STATUS_DISTRIBUTION_SUCCESS, id="float_exact"),
    pytest.param(500.00, Decimal("500.00"), Decimal("500.00"), Payment.STATUS_DISTRIBUTION_SUCCESS, id="float_round"),
    pytest.param(500, Decimal("500.00"), Decimal("500.00"), Payment.STATUS_DISTRIBUTION_SUCCESS, id="int_success"),
    pytest.param("-1", Decimal("100.00"), None, Payment.STATUS_ERROR, id="string_negative"),
    pytest.param("0", Decimal("0.00"), Decimal("0.00"), Payment.STATUS_NOT_DISTRIBUTED, id="string_zero"),
    pytest.param(
        "400.10", Decimal("400.23"), Decimal("400.10"), Payment.STATUS_DISTRIBUTION_PARTIAL, id="string_partial"
    ),
    pytest.param(
        "400.23", Decimal("400.23"), Decimal("400.23"), Payment.STATUS_DISTRIBUTION_SUCCESS, id="string_exact"
    ),
    pytest.param("500", Decimal("500.00"), Decimal("500.00"), Payment.STATUS_DISTRIBUTION_SUCCESS, id="string_int"),
    pytest.param(
        "500.00", Decimal("500.00"), Decimal("500.00"), Payment.STATUS_DISTRIBUTION_SUCCESS, id="string_float"
    ),
]

RECONCILIATION_ERROR_CASES = [
    pytest.param(600.00, Decimal("100.00"), id="delivered_exceeds_entitlement"),
]


@pytest.mark.parametrize(
    ("delivered_quantity", "entitlement_quantity", "expected_delivered", "expected_status"),
    RECONCILIATION_STATUS_CASES,
)
def test_get_delivered_quantity_status_and_value_valid_inputs(
    payment_plan: PaymentPlan,
    delivered_quantity: int | float | str,
    entitlement_quantity: Decimal,
    expected_delivered: Decimal | None,
    expected_status: str,
) -> None:
    service = XlsxPaymentPlanImportPerFspService(payment_plan, None)

    status, value = service._get_delivered_quantity_status_and_value(
        delivered_quantity, entitlement_quantity, "test_payment_id"
    )

    assert status == expected_status
    assert value == expected_delivered


@pytest.mark.parametrize(
    ("delivered_quantity", "entitlement_quantity"),
    RECONCILIATION_ERROR_CASES,
)
def test_get_delivered_quantity_status_and_value_raises(
    payment_plan: PaymentPlan,
    delivered_quantity: float,
    entitlement_quantity: Decimal,
) -> None:
    service = XlsxPaymentPlanImportPerFspService(payment_plan, None)

    with pytest.raises(
        XlsxPaymentPlanImportPerFspService.XlsxPaymentPlanImportPerFspServiceError,
        match=f"Invalid delivered_quantity {delivered_quantity}",
    ):
        service._get_delivered_quantity_status_and_value(delivered_quantity, entitlement_quantity, "test_payment_id")


def test_import_row_updates_payment_and_verification_status(
    payment_plan_finished: PaymentPlan,
    payment_verification_plan: PaymentVerificationPlan,
    households_with_individuals: list[dict[str, Any]],
) -> None:
    payment_1 = PaymentFactory(
        parent=payment_plan_finished,
        household=households_with_individuals[0]["household"],
        collector=households_with_individuals[0]["individual"],
        entitlement_quantity=Decimal(1111),
        entitlement_quantity_usd=Decimal(100),
        delivered_quantity=Decimal(1000),
        delivered_quantity_usd=Decimal(99),
    )
    payment_2 = PaymentFactory(
        parent=payment_plan_finished,
        household=households_with_individuals[1]["household"],
        collector=households_with_individuals[1]["individual"],
        entitlement_quantity=Decimal(2222),
        entitlement_quantity_usd=Decimal(100),
        delivered_quantity=Decimal(2000),
        delivered_quantity_usd=Decimal(500),
    )
    payment_3 = PaymentFactory(
        parent=payment_plan_finished,
        household=households_with_individuals[2]["household"],
        collector=households_with_individuals[2]["individual"],
        entitlement_quantity=Decimal(3333),
        entitlement_quantity_usd=Decimal(300),
        delivered_quantity=Decimal(3000),
        delivered_quantity_usd=Decimal(290),
    )

    verification_1 = PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment_1,
        status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        received_amount=Decimal(999),
    )
    verification_2 = PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment_2,
        status=PaymentVerification.STATUS_RECEIVED,
        received_amount=Decimal(500),
    )
    verification_3 = PaymentVerificationFactory(
        payment_verification_plan=payment_verification_plan,
        payment=payment_3,
        status=PaymentVerification.STATUS_PENDING,
        received_amount=None,
    )

    import_service = XlsxPaymentPlanImportPerFspService(payment_plan_finished, io.BytesIO())
    import_service.xlsx_headers = ["payment_id", "delivered_quantity", "delivery_date"]
    import_service.payments_dict = {
        str(payment_1.pk): payment_1,
        str(payment_2.pk): payment_2,
        str(payment_3.pk): payment_3,
    }

    Row = namedtuple("Row", ["value"])

    import_service._import_row(
        [Row(str(payment_1.id)), Row(999), Row("2023/05/12")],
        1,
    )
    import_service._import_row(
        [Row(str(payment_2.id)), Row(100), Row(pytz.utc.localize(datetime(2022, 12, 14)))],
        1,
    )
    import_service._import_row(
        [Row(str(payment_3.id)), Row(2999), Row(pytz.utc.localize(datetime(2021, 7, 25)))],
        1,
    )

    payment_1.save()
    payment_2.save()
    payment_3.save()

    PaymentVerification.objects.bulk_update(
        import_service.payment_verifications_to_save,
        ("status", "status_date"),
    )

    payment_1.refresh_from_db()
    payment_2.refresh_from_db()
    payment_3.refresh_from_db()
    verification_1.refresh_from_db()
    verification_2.refresh_from_db()
    verification_3.refresh_from_db()

    assert payment_1.delivered_quantity == 999
    assert verification_1.received_amount == 999
    assert verification_1.status == PaymentVerification.STATUS_RECEIVED

    assert payment_2.delivered_quantity == 100
    assert verification_2.received_amount == 500
    assert verification_2.status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES

    assert payment_3.delivered_quantity == 2999
    assert verification_3.received_amount is None
    assert verification_3.status == PaymentVerification.STATUS_PENDING

    # more coverage
    import_service = XlsxPaymentPlanImportPerFspService(payment_plan_finished, io.BytesIO())
    import_service.xlsx_headers = [
        "payment_id",
        "delivered_quantity",
        "reason_for_unsuccessful_payment",
        "additional_collector_name",
        "additional_document_type",
        "additional_document_number",
    ]
    import_service.payments_dict = {
        str(payment_1.pk): payment_1,
    }

    Row = namedtuple("Row", ["value"])

    import_service._import_row(
        [
            Row(str(payment_1.id)),
            Row(999),
            Row("Reason for unsuccessful Payment"),
            Row("Additional Collector"),
            Row("Additional Document Type"),
            Row("Additional Document Number"),
        ],
        1,
    )
    payment_1.save()
    payment_1.refresh_from_db()

    assert payment_1.delivered_quantity == 999
    assert payment_1.reason_for_unsuccessful_payment == "Reason for unsuccessful Payment"
    assert payment_1.additional_collector_name == "Additional Collector"
    assert payment_1.additional_document_type == "Additional Document Type"
    assert payment_1.additional_document_number == "Additional Document Number"
