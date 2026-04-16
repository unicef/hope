import pytest

from extras.test_utils.factories import RegistrationDataImportFactory


@pytest.fixture
def rdi_syria_import(db):
    return RegistrationDataImportFactory(name="June 2026 Syria import")


@pytest.fixture
def rdi_afghanistan_import(db):
    return RegistrationDataImportFactory(name="Afghanistan baseline")


@pytest.fixture
def rdi_syria_lowercase(db):
    return RegistrationDataImportFactory(name="syria lowercase")
