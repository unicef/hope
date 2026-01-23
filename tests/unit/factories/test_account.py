import pytest

from extras.test_utils.factories import PartnerFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_account_factories():
    assert PartnerFactory()
    assert UserFactory()
