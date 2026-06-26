import pytest

from hope.models.currency import Currency


@pytest.mark.django_db
class TestCurrencyQueryChanges:
    """Tests for changed query patterns across the codebase."""

    def test_filter_code_first_returns_none_when_no_match(self):
        assert Currency.objects.filter(code="MISSING").first() is None

    def test_filter_code_first_returns_match_when_single(self):
        c = Currency.objects.create(code="TST", name="Test")
        assert Currency.objects.filter(code="TST").first() == c

    def test_filter_code_first_returns_match_with_duplicate_codes(self):
        c1 = Currency.objects.create(code="XYC", name="A", vision_code="XYC")
        Currency.objects.create(code="XYC", name="B", vision_code="XYCO")

        result = Currency.objects.filter(code="XYC").first()
        assert result is not None
        assert result.id == c1.id

    def test_filter_code_exists_with_single(self):
        Currency.objects.create(code="TST", name="Test")
        assert Currency.objects.filter(code="TST").exists()

    def test_filter_code_exists_with_duplicate_codes(self):
        Currency.objects.create(code="XYC", name="A", vision_code="XYC")
        Currency.objects.create(code="XYC", name="B", vision_code="XYCO")
        assert Currency.objects.filter(code="XYC").exists()

    def test_filter_code_exists_with_no_match(self):
        assert not Currency.objects.filter(code="MISSING").exists()

    def test_handle_currency_field_returns_none_for_none(self):
        from hope.apps.universal_update_script.universal_individual_update_service.validator_and_handlers import (
            handle_currency_field,
        )

        assert handle_currency_field(None, "currency", None, None, None) is None

    def test_handle_currency_field_returns_none_for_empty(self):
        from hope.apps.universal_update_script.universal_individual_update_service.validator_and_handlers import (
            handle_currency_field,
        )

        assert handle_currency_field("", "currency", None, None, None) is None

    def test_handle_currency_field_returns_currency(self):
        from hope.apps.universal_update_script.universal_individual_update_service.validator_and_handlers import (
            handle_currency_field,
        )

        c = Currency.objects.create(code="TST", name="Test")
        result = handle_currency_field("TST", "currency", None, None, None)
        assert result == c

    def test_handle_currency_field_returns_first_with_duplicate_codes(self):
        from hope.apps.universal_update_script.universal_individual_update_service.validator_and_handlers import (
            handle_currency_field,
        )

        c1 = Currency.objects.create(code="XYC", name="A", vision_code="XYC")
        Currency.objects.create(code="XYC", name="B", vision_code="XYCO")

        result = handle_currency_field("XYC", "currency", None, None, None)
        assert result == c1

    def test_validate_currency_returns_none_for_valid(self):
        from hope.apps.universal_update_script.universal_individual_update_service.validator_and_handlers import (
            validate_currency,
        )

        Currency.objects.create(code="TST", name="Test")
        assert validate_currency("TST", "currency", None, None, None) is None

    def test_validate_currency_returns_error_for_invalid(self):
        from hope.apps.universal_update_script.universal_individual_update_service.validator_and_handlers import (
            validate_currency,
        )

        result = validate_currency("MISSING", "currency", None, None, None)
        assert result is not None
        assert "Invalid currency code" in result

    def test_validate_currency_returns_none_for_none(self):
        from hope.apps.universal_update_script.universal_individual_update_service.validator_and_handlers import (
            validate_currency,
        )

        assert validate_currency(None, "currency", None, None, None) is None
