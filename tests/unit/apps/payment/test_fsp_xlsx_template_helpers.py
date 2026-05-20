import pytest

from hope.models.financial_service_provider_xlsx_template import (
    FinancialServiceProviderXlsxTemplate,
    SnapshotContext,
)


@pytest.fixture
def make_empty_context():
    def _factory(**overrides):
        defaults = {
            "household_data": {},
            "primary_collector": {},
            "alternate_collector": {},
            "collector_data": {},
            "admin_areas_dict": {},
            "countries_dict": {},
        }
        defaults.update(overrides)
        return SnapshotContext(**defaults)

    return _factory


def test_resolve_snapshot_field_unknown_path(make_empty_context):
    ctx = make_empty_context()

    result = FinancialServiceProviderXlsxTemplate._resolve_snapshot_field("unknown_field", ctx)

    assert result is None


def test_resolve_snapshot_field_country(make_empty_context):
    ctx = make_empty_context(
        household_data={"country_id": "c1"},
        countries_dict={"c1": {"iso_code3": "USA"}},
    )

    result = FinancialServiceProviderXlsxTemplate._resolve_snapshot_field("country_id", ctx)

    assert result == "USA"


def test_resolve_snapshot_field_area(make_empty_context):
    ctx = make_empty_context(
        household_data={"admin1_id": "a1"},
        admin_areas_dict={"a1": {"p_code": "AF01", "name": "Kabul"}},
    )

    result = FinancialServiceProviderXlsxTemplate._resolve_snapshot_field("admin1_id", ctx)

    assert result == "AF01 - Kabul"


def test_resolve_snapshot_field_country_not_found(make_empty_context):
    ctx = make_empty_context(
        household_data={"country_id": "c1"},
        countries_dict={},
    )

    result = FinancialServiceProviderXlsxTemplate._resolve_snapshot_field("country_id", ctx)

    assert result is None
