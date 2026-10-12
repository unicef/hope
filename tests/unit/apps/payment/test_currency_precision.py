from decimal import Decimal
from io import BytesIO

from django.core.exceptions import ValidationError
import openpyxl
import pytest

from extras.test_utils.factories.payment import PaymentFactory, PaymentVerificationFactory
from hope.apps.core.api.fields import HopeCurrencyDecimalField
from hope.apps.core.fields import HopeCurrencyField, normalize_currency_decimal
from hope.apps.payment.api.serializers import PaymentListSerializer
from hope.apps.payment.services.handle_total_cash_in_households import handle_total_cash_in_specific_households
from hope.apps.payment.services.payment_gateway import PaymentPayloadSerializer
from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_import_service import _format_quantity_for_message
from hope.models import Household, Payment, PaymentPlan, PaymentVerification


@pytest.fixture
def payment(db):
    return PaymentFactory(entitlement_quantity=Decimal("123.45"))


@pytest.fixture
def delivered_payment(db):
    return PaymentFactory(
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        delivered_quantity=Decimal("123.1234567891"),
        delivered_quantity_usd=Decimal("123.1234567891"),
    )


@pytest.fixture
def payment_verification(db):
    return PaymentVerificationFactory(received_amount=Decimal("123.45"))


@pytest.mark.parametrize(
    ("model", "field_name"),
    [
        *(
            (Payment, name)
            for name in (
                "entitlement_quantity",
                "entitlement_quantity_usd",
                "delivered_quantity",
                "delivered_quantity_usd",
            )
        ),
        *(
            (PaymentPlan, name)
            for name in (
                "flat_amount_value",
                "total_entitled_quantity",
                "total_entitled_quantity_usd",
                "total_entitled_quantity_revised",
                "total_entitled_quantity_revised_usd",
                "total_delivered_quantity",
                "total_delivered_quantity_usd",
                "total_undelivered_quantity",
                "total_undelivered_quantity_usd",
            )
        ),
        (Household, "total_cash_received"),
        (Household, "total_cash_received_usd"),
        (PaymentVerification, "received_amount"),
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
        ("-123.12345678905", Decimal("-123.1234567891")),
        ("99999999999999999999.99999999994", Decimal("99999999999999999999.9999999999")),
    ],
)
def test_currency_rounding_uses_half_away_from_zero(source, expected):
    assert normalize_currency_decimal(source) == expected
    assert HopeCurrencyField().formfield().clean(source) == expected


@pytest.mark.parametrize(
    "source",
    [
        "99999999999999999999.99999999995",
        "100000000000000000000",
        "NaN",
    ],
)
def test_currency_rounding_rejects_values_outside_thirty_digits(source):
    with pytest.raises(ValidationError, match="at most 20 digits before the decimal point"):
        normalize_currency_decimal(source)


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        ("123", "123.00"),
        ("123.45", "123.45"),
        ("123.4500000001", "123.4500000001"),
    ],
)
def test_currency_api_representation_keeps_two_places_and_meaningful_precision(amount, expected):
    assert HopeCurrencyDecimalField().to_representation(Decimal(amount)) == expected


def test_payment_model_serializer_uses_currency_api_field():
    assert isinstance(PaymentListSerializer().fields["entitlement_quantity"], HopeCurrencyDecimalField)


def test_reconciliation_conflict_amount_keeps_meaningful_precision():
    assert _format_quantity_for_message(Decimal("123.4500000001")) == "123.4500000001"


def test_payment_save_load_preserves_ten_fractional_digits(payment, django_assert_num_queries):
    payment.entitlement_quantity = Decimal("123.1234567891")
    payment.save(update_fields=["entitlement_quantity"])

    with django_assert_num_queries(1):
        payment.refresh_from_db(fields=["entitlement_quantity"])

    assert payment.entitlement_quantity == Decimal("123.1234567891")
    assert payment.entitlement_quantity.as_tuple().exponent == -10


def test_payment_plan_save_load_pads_legacy_two_decimal_values(payment, django_assert_num_queries):
    payment_plan = payment.parent
    payment_plan.total_entitled_quantity = Decimal("123.45")
    payment_plan.save(update_fields=["total_entitled_quantity"])

    with django_assert_num_queries(1):
        payment_plan.refresh_from_db(fields=["total_entitled_quantity"])

    assert payment_plan.total_entitled_quantity == Decimal("123.4500000000")
    assert payment_plan.total_entitled_quantity.as_tuple().exponent == -10


def test_household_cash_totals_preserve_ten_fractional_digits(delivered_payment, django_assert_num_queries):
    household = delivered_payment.household

    with django_assert_num_queries(1):
        handle_total_cash_in_specific_households([household.pk])
    with django_assert_num_queries(1):
        household.refresh_from_db(fields=["total_cash_received", "total_cash_received_usd"])

    assert household.total_cash_received == Decimal("123.1234567891")
    assert household.total_cash_received_usd == Decimal("123.1234567891")


def test_payment_verification_save_load_preserves_ten_fractional_digits(
    payment_verification, django_assert_num_queries
):
    payment_verification.received_amount = Decimal("123.1234567891")
    payment_verification.save(update_fields=["received_amount"])

    with django_assert_num_queries(1):
        payment_verification.refresh_from_db(fields=["received_amount"])

    assert payment_verification.received_amount == Decimal("123.1234567891")
    assert payment_verification.received_amount.as_tuple().exponent == -10


def test_payment_gateway_payload_preserves_ten_fractional_digits():
    serializer = PaymentPayloadSerializer(data={"amount": "123.1234567891", "delivery_mechanism": "cash"})

    assert serializer.is_valid(), serializer.errors
    assert serializer.data["amount"] == "123.1234567891"


def test_xlsx_money_cell_is_exact_text():
    workbook = openpyxl.Workbook()
    workbook.active["A1"] = XlsxExportBaseService().right_format_for_xlsx(Decimal("123456789.1234567891"))
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    cell = openpyxl.load_workbook(output).active["A1"]
    assert cell.data_type == "s"
    assert cell.value == "123456789.1234567891"
