"""Tests for PaymentPlan reconciliation functionality."""

from collections import namedtuple
from datetime import datetime
from decimal import Decimal
import io
from typing import Any

from django.contrib.auth import get_user_model
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
from hope.models import (
    BusinessArea,
    Household,
    Individual,
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    Program,
    ProgramCycle,
    RegistrationDataImport,
)

User = get_user_model()


# Fixtures - stay in this test file


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory()


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program: Program) -> ProgramCycle:
    return ProgramCycleFactory(program=program)


@pytest.fixture
def registration_data_import(business_area: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(business_area=business_area, program=program)


@pytest.fixture
def household(
    business_area: BusinessArea, program: Program, registration_data_import: RegistrationDataImport
) -> Household:
    return HouseholdFactory(
        business_area=business_area, program=program, registration_data_import=registration_data_import
    )


@pytest.fixture
def individual(household: Household) -> Individual:
    return household.head_of_household


@pytest.fixture
def household_2(
    business_area: BusinessArea, program: Program, registration_data_import: RegistrationDataImport
) -> Household:
    return HouseholdFactory(
        business_area=business_area, program=program, registration_data_import=registration_data_import
    )


@pytest.fixture
def individual_2(household_2: Household) -> Individual:
    return household_2.head_of_household


@pytest.fixture
def household_3(
    business_area: BusinessArea, program: Program, registration_data_import: RegistrationDataImport
) -> Household:
    return HouseholdFactory(
        business_area=business_area, program=program, registration_data_import=registration_data_import
    )


@pytest.fixture
def individual_3(household_3: Household) -> Individual:
    return household_3.head_of_household


@pytest.fixture
def payment_plan(user: User, business_area: BusinessArea, program_cycle: ProgramCycle) -> PaymentPlan:
    return PaymentPlanFactory(
        created_by=user,
        business_area=business_area,
        program_cycle=program_cycle,
    )


@pytest.fixture
def payment_plan_finished(user: User, business_area: BusinessArea, program_cycle: ProgramCycle) -> PaymentPlan:
    return PaymentPlanFactory(
        created_by=user,
        business_area=business_area,
        program_cycle=program_cycle,
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


@pytest.mark.django_db
class TestGetDeliveredQuantityStatusAndValue:
    """Tests for _get_delivered_quantity_status_and_value method."""

    @pytest.mark.parametrize(
        ("delivered_quantity", "entitlement_quantity", "expected_delivered", "expected_status"),
        RECONCILIATION_STATUS_CASES,
    )
    def test_should_return_correct_status_and_value_for_valid_inputs(
        self,
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
    def test_should_raise_error_when_delivered_exceeds_entitlement(
        self,
        payment_plan: PaymentPlan,
        delivered_quantity: float,
        entitlement_quantity: Decimal,
    ) -> None:
        service = XlsxPaymentPlanImportPerFspService(payment_plan, None)

        with pytest.raises(
            XlsxPaymentPlanImportPerFspService.XlsxPaymentPlanImportPerFspServiceError,
            match=f"Invalid delivered_quantity {delivered_quantity}",
        ):
            service._get_delivered_quantity_status_and_value(
                delivered_quantity, entitlement_quantity, "test_payment_id"
            )


@pytest.mark.django_db
class TestImportRow:
    """Tests for _import_row method of XlsxPaymentPlanImportPerFspService."""

    def test_should_update_payment_and_verification_status(
        self,
        business_area: BusinessArea,
        payment_plan_finished: PaymentPlan,
        payment_verification_plan: PaymentVerificationPlan,
        household: Household,
        individual: Individual,
        household_2: Household,
        individual_2: Individual,
        household_3: Household,
        individual_3: Individual,
    ) -> None:
        payment_1 = PaymentFactory(
            parent=payment_plan_finished,
            business_area=business_area,
            household=household,
            collector=individual,
            entitlement_quantity=Decimal(1111),
            entitlement_quantity_usd=Decimal(100),
            delivered_quantity=Decimal(1000),
            delivered_quantity_usd=Decimal(99),
        )
        payment_2 = PaymentFactory(
            parent=payment_plan_finished,
            business_area=business_area,
            household=household_2,
            collector=individual_2,
            entitlement_quantity=Decimal(2222),
            entitlement_quantity_usd=Decimal(100),
            delivered_quantity=Decimal(2000),
            delivered_quantity_usd=Decimal(500),
        )
        payment_3 = PaymentFactory(
            parent=payment_plan_finished,
            business_area=business_area,
            household=household_3,
            collector=individual_3,
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
            [Row(str(payment_1.id)), Row(999), Row(pytz.utc.localize(datetime(2023, 5, 12)))],
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
