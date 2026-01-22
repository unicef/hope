import pytest

from extras.test_utils.factories import RegistrationDataImportFactory

pytestmark = pytest.mark.django_db


def test_registration_data_factories():
    assert RegistrationDataImportFactory()
