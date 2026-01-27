import pytest

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    FileTempFactory,
)

pytestmark = pytest.mark.django_db


def test_core_factories():
    assert BusinessAreaFactory()
    assert BeneficiaryGroupFactory()
    assert DataCollectingTypeFactory()
    assert FileTempFactory()
