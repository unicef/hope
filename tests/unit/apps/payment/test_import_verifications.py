from decimal import Decimal
import io
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from unittest.mock import patch
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.household import EntitlementCardFactory, HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.payment.xlsx.xlsx_verification_export_service import XlsxVerificationExportService
from hope.apps.payment.xlsx.xlsx_verification_import_service import XlsxVerificationImportService
from hope.models import DataCollectingType, PaymentVerification

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def admin_areas():
    return [AreaFactory() for _ in range(3)]


@pytest.fixture
def program(business_area, admin_areas):
    program = ProgramFactory(business_area=business_area)
    program.admin_areas.set(admin_areas)
    return program


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def payment_plan(program_cycle, business_area):
    return PaymentPlanFactory(program_cycle=program_cycle, business_area=business_area)


@pytest.fixture
def verification_plan(payment_plan):
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    return PaymentVerificationPlanFactory(payment_plan=payment_plan)


@pytest.fixture
def verification_setup(verification_plan, program, business_area, admin_areas):
    payments = []
    for _ in range(10):
        household = HouseholdFactory(
            business_area=business_area,
            program=program,
            admin2=admin_areas[0],
        )
        payment = PaymentFactory(
            parent=verification_plan.payment_plan,
            household=household,
            head_of_household=household.head_of_household,
            currency="PLN",
            delivered_quantity=Decimal("150.00"),
            entitlement_quantity=Decimal("120.00"),
            program=program,
        )
        PaymentVerificationFactory(
            payment=payment,
            payment_verification_plan=verification_plan,
            status=PaymentVerification.STATUS_PENDING,
        )
        EntitlementCardFactory(household=household)
        payments.append(payment)
    return {
        "payment_plan": verification_plan.payment_plan,
        "verification_plan": verification_plan,
        "payments": payments,
    }


@pytest.mark.parametrize(
    ("initial_status", "result"),
    [
        (PaymentVerification.STATUS_PENDING, None),
        (PaymentVerification.STATUS_NOT_RECEIVED, "NO"),
        (PaymentVerification.STATUS_RECEIVED, "YES"),
        (PaymentVerification.STATUS_RECEIVED_WITH_ISSUES, "YES"),
    ],
)
def test_export_received_from_pending(verification_setup, initial_status, result):
    verification_plan = verification_setup["verification_plan"]
    verification_plan.payment_record_verifications.all().update(status=initial_status)
    export_service = XlsxVerificationExportService(verification_plan)

    wb = export_service.generate_workbook()
    assert wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"].value == result


def test_validation_valid_not_changed_file(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()

    assert import_service.errors == []


def test_validation_valid_status_changed_for_people(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    dct = verification_plan.payment_plan.program_cycle.program.data_collecting_type
    dct.type = DataCollectingType.Type.SOCIAL
    dct.save()
    export_service = XlsxVerificationExportService(verification_plan)
    verification_plan.refresh_from_db()
    wb = export_service.generate_workbook()
    wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
    wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER_PEOPLE}2"] = 2
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()
    assert import_service.errors == []


def test_validation_valid_status_changed(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NO"
    wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = 0
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()
    assert import_service.errors == []


def test_validation_invalid_received_changed(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NOT_CORRECT_RECEIVED"
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()

    error = import_service.errors[0]
    assert [error.sheet, error.coordinates, error.message] == [
        "Payment Verifications",
        f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2",
        "The received of this payment verification is not correct: NOT_CORRECT_RECEIVED should be one of: "
        "(None, 'YES', 'NO')",
    ]


def test_validation_invalid_version(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    wb[XlsxVerificationExportService.META_SHEET][XlsxVerificationExportService.VERSION_CELL_COORDINATES] = "-1"
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    with pytest.raises(
        ValidationError,
        match=(rf"Unsupported file version \(-1\). Only version: {XlsxVerificationExportService.VERSION} is supported"),
    ):
        import_service.validate()


def test_validation_payment_record_id(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    wrong_uuid = str(uuid.uuid4())
    wb.active["A2"] = wrong_uuid
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()
    error = import_service.errors[0]
    assert [error.sheet, error.coordinates, error.message] == [
        "Payment Verifications",
        "A2",
        f"This payment record id {wrong_uuid} is not in Cash Plan Payment Record Verification",
    ]


def test_validation_wrong_type(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}3"] = "A"
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()
    error = import_service.errors[0]

    assert [error.sheet, error.coordinates, error.message] == [
        "Payment Verifications",
        f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}3",
        "Wrong type off cell number expected, text given.",
    ]


def test_validation_invalid_received_not_received_with_amount(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NO"
    wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = 10
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()
    error = import_service.errors[0]
    assert [error.sheet, error.coordinates, error.message] == [
        "Payment Verifications",
        f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2",
        "If received_amount(10.00) is not 0, you should set received to YES",
    ]


def test_validation_invalid_received_received_with_0_amount(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
    wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = 0
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()
    error = import_service.errors[0]
    assert [error.sheet, error.coordinates, error.message] == [
        "Payment Verifications",
        f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2",
        "Amount Received' equals to 0, please set status as 'Not Received'",
    ]


def test_import_valid_status_changed_received_no(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    payment_record_id = wb.active["A2"].value
    payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
    assert payment_verification.status == PaymentVerification.STATUS_PENDING
    wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NO"
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()
    import_service.import_verifications()
    assert import_service.errors == []

    payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
    assert payment_verification.status == PaymentVerification.STATUS_NOT_RECEIVED


def test_import_valid_status_changed_received_yes_not_full(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    payment_record_id = wb.active["A2"].value
    payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
    assert payment_verification.status == PaymentVerification.STATUS_PENDING
    wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
    wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = (
        payment_verification.payment.delivered_quantity - 1
    )
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()
    import_service.import_verifications()
    assert import_service.errors == []

    payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
    assert payment_verification.status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
    assert payment_verification.received_amount == payment_verification.payment.delivered_quantity - 1


def test_import_valid_status_changed_received_yes_full(verification_setup):
    verification_plan = verification_setup["verification_plan"]
    export_service = XlsxVerificationExportService(verification_plan)
    wb = export_service.generate_workbook()
    payment_record_id = wb.active["A2"].value
    payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
    assert payment_verification.status == PaymentVerification.STATUS_PENDING
    wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
    wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = (
        payment_verification.payment.delivered_quantity
    )
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        file = io.BytesIO(tmp.read())
    import_service = XlsxVerificationImportService(verification_plan, file)
    import_service.open_workbook()
    import_service.validate()
    import_service.import_verifications()
    assert import_service.errors == []

    payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
    assert payment_verification.status == PaymentVerification.STATUS_RECEIVED
    assert payment_verification.received_amount == payment_verification.payment.delivered_quantity


@pytest.mark.parametrize(
    "file_name",
    [
        "unordered_columns_1",
        "unordered_columns_2",
        "unordered_columns_3",
    ],
)
@patch(
    "hope.apps.payment.xlsx.xlsx_verification_import_service.XlsxVerificationImportService._check_version",
    return_value=None,
)
def test_validation_of_unordered_columns(mock_check_version: Any, file_name: str):
    program = ProgramFactory()
    program_cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, business_area=program.business_area)
    registration_data_import = RegistrationDataImportFactory(
        business_area=payment_plan.business_area,
        program=payment_plan.program,
    )

    hoh1 = IndividualFactory(
        household=None,
        business_area=payment_plan.business_area,
        program=payment_plan.program,
        registration_data_import=registration_data_import,
    )
    household_1 = HouseholdFactory(
        business_area=payment_plan.business_area,
        program=payment_plan.program,
        registration_data_import=registration_data_import,
        head_of_household=hoh1,
    )
    payment_1 = PaymentFactory(
        id=uuid.UUID("0329a41f-affd-4669-9e38-38ec2d6699b3"),
        parent=payment_plan,
        household=household_1,
        entitlement_quantity=Decimal("120.00"),
        delivered_quantity=Decimal("150.00"),
        currency="PLN",
        program=payment_plan.program,
        collector=household_1.head_of_household,
    )

    hoh2 = IndividualFactory(
        household=None,
        business_area=payment_plan.business_area,
        program=payment_plan.program,
        registration_data_import=registration_data_import,
    )
    household_2 = HouseholdFactory(
        business_area=payment_plan.business_area,
        program=payment_plan.program,
        registration_data_import=registration_data_import,
        head_of_household=hoh2,
    )
    payment_2 = PaymentFactory(
        id=uuid.UUID("299811ef-b123-427d-b77d-9fd5d1bc8946"),
        parent=payment_plan,
        household=household_2,
        entitlement_quantity=Decimal("120.00"),
        delivered_quantity=Decimal("150.00"),
        currency="PLN",
        program=payment_plan.program,
        collector=household_2.head_of_household,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    payment_verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)

    PaymentVerificationFactory(
        payment=payment_1,
        payment_verification_plan=payment_verification_plan,
        status=PaymentVerification.STATUS_PENDING,
    )
    PaymentVerificationFactory(
        payment=payment_2,
        payment_verification_plan=payment_verification_plan,
        status=PaymentVerification.STATUS_PENDING,
    )

    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/{file_name}.xlsx").read_bytes()
    xlsx_verification_import_service = XlsxVerificationImportService(payment_verification_plan, io.BytesIO(content))
    xlsx_verification_import_service.open_workbook()
    xlsx_verification_import_service.validate()

    assert xlsx_verification_import_service.errors == []
