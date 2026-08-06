import importlib

from django.apps import apps
import pytest

from extras.test_utils.factories.core import DataCollectingTypeFactory
from hope.models import DataCollectingType

pytestmark = pytest.mark.django_db

_migration = importlib.import_module("hope.apps.core.migrations.0031_migration")
set_collects_individual_data = _migration.set_collects_individual_data
reverse_set_collects_individual_data = _migration.reverse_set_collects_individual_data


@pytest.fixture
def recalculating_dct() -> DataCollectingType:
    return DataCollectingTypeFactory(recalculate_composition=True, collects_individual_data=False)


@pytest.fixture
def non_recalculating_dct() -> DataCollectingType:
    return DataCollectingTypeFactory(recalculate_composition=False, collects_individual_data=False)


def test_data_migration_enables_flag_only_for_recalculating(
    recalculating_dct: DataCollectingType, non_recalculating_dct: DataCollectingType
) -> None:
    set_collects_individual_data(apps, None)

    recalculating_dct.refresh_from_db()
    non_recalculating_dct.refresh_from_db()
    assert recalculating_dct.collects_individual_data is True
    assert non_recalculating_dct.collects_individual_data is False


def test_data_migration_reverse_disables_flag(recalculating_dct: DataCollectingType) -> None:
    set_collects_individual_data(apps, None)
    reverse_set_collects_individual_data(apps, None)

    recalculating_dct.refresh_from_db()
    assert recalculating_dct.collects_individual_data is False
