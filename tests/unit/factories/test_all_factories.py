import pytest

from extras.test_utils import factories

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("factory_name", factories.__all__)
def test_factory(factory_name):
    factory_class = getattr(factories, factory_name)
    instance = factory_class()
    assert instance is not None
