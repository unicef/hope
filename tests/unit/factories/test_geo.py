import pytest

from extras.test_utils.factories import AreaFactory, AreaTypeFactory, CountryFactory

pytestmark = pytest.mark.django_db


def test_geo_factories():
    assert CountryFactory()
    assert AreaTypeFactory()
    assert AreaFactory()
