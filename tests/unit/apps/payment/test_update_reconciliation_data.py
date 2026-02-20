from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

from django.conf import settings
import pytest
import pytz
from pytz import utc

from extras.test_utils.factories import (
    ApprovalFactory,
    ApprovalProcessFactory,
    BusinessAreaFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)
from hope.models import Approval, PaymentPlan, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def file_without_delivery_dates() -> BytesIO:
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/import_file_no_delivery_date.xlsx").read_bytes()
    return BytesIO(content)


@pytest.fixture
def file_with_existing_delivery_dates() -> BytesIO:
    content = Path(
        f"{settings.TESTS_ROOT}/apps/payment/test_file/import_file_with_existing_delivery_date.xlsx"
    ).read_bytes()
    return BytesIO(content)


@pytest.fixture
def file_one_record() -> BytesIO:
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/import_file_one_record.xlsx").read_bytes()
    return BytesIO(content)


@pytest.fixture
def file_reference_id() -> BytesIO:
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/import_file_reference_id.xlsx").read_bytes()
    return BytesIO(content)


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(name="Afghanistan")


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def program(business_area: Any) -> Program:
    return ProgramFactory(
        business_area=business_area,
        status=Program.ACTIVE,
        start_date=date(2011, 1, 1),
        end_date=date(2099, 1, 1),
    )


@pytest.fixture
def payment_plan_context(business_area: Any, user: Any, program: Program) -> dict[str, Any]:
    cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(
        dispersion_start_date=date(2020, 8, 10),
        dispersion_end_date=date(2020, 12, 10),
        created_by=user,
        business_area=business_area,
        program_cycle=cycle,
        exchange_rate=2.0,
    )
    payment_ids = [
        "RCPT-0060-24-0.000.001",
        "RCPT-0060-24-0.000.002",
        "RCPT-0060-24-0.000.003",
    ]
    payments = []
    for unicef_id in payment_ids:
        household = HouseholdFactory(program=program, business_area=business_area)
        payment = PaymentFactory(
            parent=payment_plan,
            household=household,
            head_of_household=household.head_of_household,
            collector=household.head_of_household,
            entitlement_quantity=212,
            delivered_quantity=150,
            currency="PLN",
            delivery_date=datetime(2023, 10, 23).replace(tzinfo=utc),
        )
        payment.unicef_id = unicef_id
        payment.save(update_fields=["unicef_id"])
        payments.append(payment)

    return {
        "payment_plan": payment_plan,
        "payments": payments,
    }


def test_uploading_delivery_date_with_xlsx(
    payment_plan_context: dict[str, Any],
    file_without_delivery_dates: BytesIO,
) -> None:
    payment_1, payment_2, payment_3 = payment_plan_context["payments"]
    payment_1.delivery_date = None
    payment_1.save(update_fields=["delivery_date"])
    old_delivery_date2 = payment_2.delivery_date
    old_delivery_date3 = payment_3.delivery_date
    with (
        patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0),
        patch(
            "hope.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service.timezone.now",
            return_value=datetime(2024, 11, 22).replace(tzinfo=utc),
        ),
    ):
        import_service = XlsxPaymentPlanImportPerFspService(
            payment_plan_context["payment_plan"],
            file_without_delivery_dates,
        )
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()

    payment_1.refresh_from_db()
    payment_2.refresh_from_db()
    payment_3.refresh_from_db()
    date_now = pytz.utc.localize(datetime(2024, 11, 22))
    assert payment_1.delivery_date == date_now
    assert payment_2.delivery_date == old_delivery_date2
    assert payment_3.delivery_date == old_delivery_date3


def test_uploading_xlsx_file_with_existing_dates_throws_error(
    payment_plan_context: dict[str, Any],
    file_with_existing_delivery_dates: BytesIO,
) -> None:
    with patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0):
        import_service = XlsxPaymentPlanImportPerFspService(
            payment_plan_context["payment_plan"],
            file_with_existing_delivery_dates,
        )
        import_service.open_workbook()
        import_service.validate()

    assert len(import_service.errors) == 2

    error = import_service.errors[1]
    assert [error.sheet, error.coordinates, error.message] == [
        "Test FSP 1",
        None,
        "There aren't any updates in imported file, please add changes and try again",
    ]
    error_2 = import_service.errors[0]
    assert [error_2.sheet, error_2.coordinates, error_2.message] == [
        "Test FSP 1",
        "A5",
        "Payment id RCPT-0060-24-0.000.003 appears multiple times in the import file",
    ]


def test_uploading_xlsx_file_with_one_record_not_overrides_other_payments_dates(
    payment_plan_context: dict[str, Any],
    file_one_record: BytesIO,
) -> None:
    payment_1, payment_2, payment_3 = payment_plan_context["payments"]

    with (
        patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0),
    ):
        import_service = XlsxPaymentPlanImportPerFspService(
            payment_plan_context["payment_plan"],
            file_one_record,
        )
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()

    payment_1.refresh_from_db()
    payment_2.refresh_from_db()
    payment_3.refresh_from_db()

    assert payment_1.delivery_date == datetime(2023, 5, 5).replace(tzinfo=utc)
    assert payment_2.delivery_date == datetime(2023, 10, 23).replace(tzinfo=utc)
    assert payment_3.delivery_date == datetime(2023, 10, 23).replace(tzinfo=utc)


def test_upload_reference_id(
    business_area: Any,
    user: Any,
    program: Program,
    file_reference_id: BytesIO,
) -> None:
    cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(
        dispersion_start_date=date(2024, 2, 10),
        dispersion_end_date=date(2024, 12, 10),
        status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
        program_cycle=cycle,
        created_by=user,
        exchange_rate=2.0,
    )
    approval_process = ApprovalProcessFactory(payment_plan=payment_plan)
    ApprovalFactory(
        approval_process=approval_process,
        type=Approval.FINANCE_RELEASE,
        created_by=user,
        created_at=datetime(2023, 5, 5).replace(tzinfo=utc),
    )

    payment_1 = PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=212,
        delivered_quantity=150,
    )
    payment_1.unicef_id = "RCPT-0060-24-0.000.665"
    payment_1.save(update_fields=["unicef_id"])

    payment_2 = PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=212,
        delivered_quantity=150,
    )
    payment_2.unicef_id = "RCPT-0060-24-0.000.666"
    payment_2.save(update_fields=["unicef_id"])

    with patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0):
        import_service = XlsxPaymentPlanImportPerFspService(payment_plan, file_reference_id)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()

    payment_1.refresh_from_db()
    payment_2.refresh_from_db()

    assert payment_1.transaction_reference_id == "ref1"
    assert payment_2.transaction_reference_id == "ref2"


def test_upload_transaction_status_blockchain_link(
    business_area: Any,
    user: Any,
    program: Program,
    file_reference_id: BytesIO,
) -> None:
    cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(
        dispersion_start_date=date(2024, 2, 10),
        dispersion_end_date=date(2024, 12, 10),
        status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
        program_cycle=cycle,
        created_by=user,
        exchange_rate=1.0,
    )
    approval_process = ApprovalProcessFactory(payment_plan=payment_plan)
    ApprovalFactory(
        approval_process=approval_process,
        type=Approval.FINANCE_RELEASE,
        created_by=user,
        created_at=datetime(2023, 5, 5).replace(tzinfo=utc),
    )
    payment_1 = PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=212,
        delivered_quantity=150,
    )
    payment_1.unicef_id = "RCPT-0060-24-0.000.665"
    payment_1.save(update_fields=["unicef_id"])

    payment_2 = PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=212,
        delivered_quantity=150,
    )
    payment_2.unicef_id = "RCPT-0060-24-0.000.666"
    payment_2.save(update_fields=["unicef_id"])

    with patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=1.0):
        import_service = XlsxPaymentPlanImportPerFspService(payment_plan, file_reference_id)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()

    payment_1.refresh_from_db(fields=["transaction_status_blockchain_link"])
    payment_2.refresh_from_db(fields=["transaction_status_blockchain_link"])

    assert payment_1.transaction_status_blockchain_link == "transaction_status_blockchain_link_111"
    assert payment_2.transaction_status_blockchain_link == "www_link"
