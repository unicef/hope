from datetime import date
from decimal import Decimal
from io import BytesIO

from django.core.exceptions import ValidationError
from django.db import connection
import openpyxl
import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories.payment import PaymentFactory
from hope.apps.core.api.fields import HopeCurrencyDecimalField
from hope.apps.core.fields import HopeCurrencyField, normalize_currency_decimal
from hope.apps.payment.api.serializers import PaymentListSerializer
from hope.apps.payment.services.handle_total_cash_in_households import handle_total_cash_in_specific_households
from hope.apps.payment.services.payment_gateway import PaymentPayloadSerializer
from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_import_service import XlsxPaymentPlanDeliveryImportService
from hope.models import Household, Payment, PaymentPlan


@pytest.fixture
def payment(db):
    return PaymentFactory(entitlement_quantity=Decimal("123.45"))


@pytest.fixture
def delivered_payment(db):
    return PaymentFactory(
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        delivered_quantity=Decimal("123.12"),
        delivered_quantity_usd=Decimal("123.1234567891"),
    )


@pytest.mark.parametrize(
    ("model", "field_name"),
    [
        (Payment, "entitlement_quantity_usd"),
        (Payment, "delivered_quantity_usd"),
        (PaymentPlan, "total_entitled_quantity_usd"),
        (PaymentPlan, "total_entitled_quantity_revised_usd"),
        (PaymentPlan, "total_delivered_quantity_usd"),
        (PaymentPlan, "total_undelivered_quantity_usd"),
        (Household, "total_cash_received_usd"),
    ],
)
def test_money_model_field_has_precision_and_admin_labels(model, field_name):
    field = model._meta.get_field(field_name)

    assert isinstance(field, HopeCurrencyField)
    assert field.max_digits == 30
    assert field.decimal_places == 10
    assert field.verbose_name
    assert "10 decimal places" in field.help_text


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("123.45", Decimal("123.4500000000")),
        ("123.12345678905", Decimal("123.1234567891")),
        ("99999999999999999999.99999999994", Decimal("99999999999999999999.9999999999")),
    ],
)
def test_currency_rounding_uses_half_up(source, expected):
    assert normalize_currency_decimal(source) == expected


def test_currency_form_accepts_ten_decimal_places():
    assert HopeCurrencyField().formfield().clean("123.1234567890") == Decimal("123.1234567890")


def test_currency_form_rejects_more_than_ten_decimal_places():
    with pytest.raises(ValidationError, match="no more than 10 decimal places"):
        HopeCurrencyField().formfield().clean("123.12345678901")


def test_currency_field_uses_unbounded_postgresql_numeric_type():
    assert HopeCurrencyField().db_type(connection) == "numeric"


@pytest.mark.parametrize(
    "source",
    [
        "99999999999999999999.99999999995",
        "100000000000000000000",
        "-0.01",
        "NaN",
    ],
)
def test_currency_normalization_rejects_invalid_amounts(source):
    with pytest.raises(ValidationError, match="at most 20 digits before the decimal point"):
        normalize_currency_decimal(source)


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        ("123", "123.00"),
        ("123.45", "123.45"),
        ("123.4500000001", "123.45"),
    ],
)
def test_currency_api_representation_keeps_two_places_and_meaningful_precision(amount, expected):
    assert HopeCurrencyDecimalField().to_representation(Decimal(amount)) == expected


@pytest.mark.parametrize("source", ["NaN", "100000000000000000000", "-0.01"])
def test_currency_api_rejects_invalid_amount(source):
    with pytest.raises(DRFValidationError) as exc_info:
        HopeCurrencyDecimalField().to_internal_value(source)

    assert exc_info.value.get_codes() == ["invalid"]


def test_currency_api_accepts_ten_decimal_places():
    assert HopeCurrencyDecimalField().to_internal_value("123.1234567891") == Decimal("123.1234567891")


def test_currency_api_representation_is_a_string_even_when_coercion_is_disabled():
    representation = HopeCurrencyDecimalField(coerce_to_string=False).to_representation(Decimal("123.45"))

    assert representation == "123.45"


def test_payment_model_serializer_uses_currency_api_field():
    assert isinstance(PaymentListSerializer().fields["entitlement_quantity_usd"], HopeCurrencyDecimalField)


def test_payment_save_load_preserves_ten_fractional_digits(payment, django_assert_num_queries):
    payment.entitlement_quantity_usd = Decimal("123.1234567891")
    payment.save(update_fields=["entitlement_quantity_usd"])

    with django_assert_num_queries(1):
        payment.refresh_from_db(fields=["entitlement_quantity_usd"])

    assert payment.entitlement_quantity_usd == Decimal("123.1234567891")
    assert payment.entitlement_quantity_usd.as_tuple().exponent == -10


def test_payment_plan_save_load_pads_legacy_two_decimal_values(payment, django_assert_num_queries):
    payment_plan = payment.parent
    payment_plan.total_entitled_quantity_usd = Decimal("123.45")
    payment_plan.save(update_fields=["total_entitled_quantity_usd"])

    with django_assert_num_queries(1):
        payment_plan.refresh_from_db(fields=["total_entitled_quantity_usd"])

    assert payment_plan.total_entitled_quantity_usd == Decimal("123.4500000000")
    assert payment_plan.total_entitled_quantity_usd.as_tuple().exponent == -10


def test_household_cash_totals_preserve_ten_fractional_digits(delivered_payment, django_assert_num_queries):
    household = delivered_payment.household

    with django_assert_num_queries(1):
        handle_total_cash_in_specific_households([household.pk])
    with django_assert_num_queries(1):
        household.refresh_from_db(fields=["total_cash_received", "total_cash_received_usd"])

    assert household.total_cash_received == Decimal("123.12")
    assert household.total_cash_received_usd == Decimal("123.1234567891")


def test_payment_gateway_payload_keeps_base_currency_precision():
    serializer = PaymentPayloadSerializer(data={"amount": "123.45", "delivery_mechanism": "cash"})

    assert serializer.is_valid(), serializer.errors
    assert serializer.data["amount"] == "123.45"


def test_xlsx_money_cell_is_exact_text():
    workbook = openpyxl.Workbook()
    workbook.active["A1"] = XlsxExportBaseService().right_format_for_xlsx(Decimal("123456789.1234567891"))
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    cell = openpyxl.load_workbook(output).active["A1"]
    assert cell.data_type == "s"
    assert cell.value == "123456789.1234567891"


@pytest.mark.parametrize("value", [10, 10.5])
def test_xlsx_monetary_number_remains_numeric(value):
    result = XlsxExportBaseService().right_format_for_xlsx(value, "entitlement_quantity")

    assert result == value
    assert type(result) is type(value)


def test_xlsx_nonmonetary_number_remains_numeric():
    result = XlsxExportBaseService().right_format_for_xlsx(10, "household_size")

    assert result == 10
    assert isinstance(result, int)


@pytest.fixture
def nonmonetary_date():
    return date(2026, 1, 2)


def test_xlsx_unsupported_value_uses_string_fallback(nonmonetary_date):
    result = XlsxExportBaseService().right_format_for_xlsx(nonmonetary_date, "payment_date")

    assert result == "2026-01-02"
    assert isinstance(result, str)


def test_delivery_import_uses_fsp_provided_usd_amount(payment):
    service = XlsxPaymentPlanDeliveryImportService(payment.parent, BytesIO())
    service.xlsx_headers = ["delivered_quantity_usd"]
    worksheet = openpyxl.Workbook().active
    worksheet["A1"] = "delivered_quantity_usd"
    worksheet["A2"] = "123.1234567891"

    service._apply_reconciliation_values(payment, tuple(worksheet[2]), Decimal("100.00"), None)

    assert payment.delivered_quantity == Decimal("100.00")
    assert payment.delivered_quantity_usd == Decimal("123.1234567891")


def test_delivery_import_rejects_invalid_fsp_usd_amount(payment):
    service = XlsxPaymentPlanDeliveryImportService(payment.parent, BytesIO())
    service.xlsx_headers = ["delivered_quantity_usd"]
    worksheet = openpyxl.Workbook().active
    worksheet["A1"] = "delivered_quantity_usd"
    worksheet["A2"] = "-0.01"

    with pytest.raises(
        XlsxPaymentPlanDeliveryImportService.XlsxPaymentPlanDeliveryImportServiceError,
        match=f"Invalid delivered_quantity_usd provided for payment_id {payment.unicef_id}",
    ):
        service._apply_reconciliation_values(payment, tuple(worksheet[2]), Decimal("100.00"), None)


def test_delivery_import_failed_sentinel_ignores_fsp_usd_amount(payment):
    service = XlsxPaymentPlanDeliveryImportService(payment.parent, BytesIO())
    service.xlsx_headers = ["delivered_quantity_usd"]
    worksheet = openpyxl.Workbook().active
    worksheet["A1"] = "delivered_quantity_usd"
    worksheet["A2"] = "123.1234567891"

    service._apply_reconciliation_values(payment, tuple(worksheet[2]), Decimal("-1.00"), None)

    assert payment.status == Payment.STATUS_ERROR
    assert payment.delivered_quantity is None
    assert payment.delivered_quantity_usd is None
