from unittest.mock import patch

from flags.models import FlagState
import pytest


@pytest.mark.django_db
@patch("hope.apps.core.management.commands.init_core_fixtures.generate_country_codes")
@patch("hope.apps.core.management.commands.init_core_fixtures.generate_business_areas")
@patch("hope.apps.core.management.commands.init_core_fixtures.generate_data_collecting_types")
def test_initialize_core_fixtures_creates_flag_states(
    mock_generate_data_collecting_types,
    mock_generate_business_areas,
    mock_generate_country_codes,
):
    from hope.apps.core.management.commands.init_core_fixtures import initialize_core_fixtures

    initialize_core_fixtures()

    assert FlagState.objects.filter(name="ALLOW_ACCOUNTABILITY_MODULE").exists()
    assert FlagState.objects.filter(name="VISION_INTEGRATION_ACTIVE").exists()
    mock_generate_country_codes.assert_called_once()
    mock_generate_business_areas.assert_called_once()
    mock_generate_data_collecting_types.assert_called_once()


@pytest.mark.django_db
@patch("hope.apps.core.management.commands.init_core_fixtures.generate_country_codes")
@patch("hope.apps.core.management.commands.init_core_fixtures.generate_business_areas")
@patch("hope.apps.core.management.commands.init_core_fixtures.generate_data_collecting_types")
def test_initialize_core_fixtures_is_idempotent(
    mock_generate_data_collecting_types,
    mock_generate_business_areas,
    mock_generate_country_codes,
):
    from hope.apps.core.management.commands.init_core_fixtures import initialize_core_fixtures

    initialize_core_fixtures()
    count = FlagState.objects.count()

    initialize_core_fixtures()

    assert FlagState.objects.count() == count
