import pytest
from page_object.registration_data_import.registration_data_import import (
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.usefixtures("login")
class TestRegistrationDataImport:
    def test_smoke_registration_data_import(self, pageRegistrationDataImport: RegistrationDataImport) -> None:
        # Go to Registration Data Import
        pageRegistrationDataImport.getNavRegistrationDataImport().click()
        pageRegistrationDataImport.screenshot("1")
