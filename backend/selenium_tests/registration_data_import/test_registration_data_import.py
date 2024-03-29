from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.registration_data_import.rdi_details_page import RDIDetailsPage
from page_object.registration_data_import.registration_data_import import (
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


@pytest.fixture
def add_rdi() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    return


@pytest.mark.usefixtures("login")
class TestSmokeRegistrationDataImport:
    def test_smoke_registration_data_import(
            self, create_programs: None, add_rdi: None, pageRegistrationDataImport: RegistrationDataImport
    ) -> None:
        # Go to Registration Data Import
        pageRegistrationDataImport.selectGlobalProgramFilter("Test Programm").click()
        pageRegistrationDataImport.getNavRegistrationDataImport().click()
        # Check Elements on Page
        assert pageRegistrationDataImport.titleText in pageRegistrationDataImport.getPageHeaderTitle().text
        assert pageRegistrationDataImport.importText in pageRegistrationDataImport.getButtonImport().text
        assert pageRegistrationDataImport.tableTitleText in pageRegistrationDataImport.getTableTitle().text
        assert pageRegistrationDataImport.expectedRows(2)
        assert "2" in pageRegistrationDataImport.getTableTitle().text
        assert "Title" in pageRegistrationDataImport.getTableLabel()[0].text
        assert "Status" in pageRegistrationDataImport.getTableLabel()[1].text
        assert "Import Date" in pageRegistrationDataImport.getTableLabel()[2].text
        assert "Num. of Individuals" in pageRegistrationDataImport.getTableLabel()[3].text
        assert "Num. of Households" in pageRegistrationDataImport.getTableLabel()[4].text
        assert "Imported by" in pageRegistrationDataImport.getTableLabel()[5].text
        assert "Data Source" in pageRegistrationDataImport.getTableLabel()[6].text

    def test_smoke_registration_data_import_select_file(
            self, create_programs: None, pageRegistrationDataImport: RegistrationDataImport
    ) -> None:
        # Go to Registration Data Import
        pageRegistrationDataImport.selectGlobalProgramFilter("Test Programm").click()
        pageRegistrationDataImport.getNavRegistrationDataImport().click()
        assert pageRegistrationDataImport.titleText in pageRegistrationDataImport.getPageHeaderTitle().text
        pageRegistrationDataImport.getButtonImport().click()
        # Check Elements on Page
        assert pageRegistrationDataImport.downloadTemplateText in pageRegistrationDataImport.getDownloadTemplate().text
        assert pageRegistrationDataImport.importText in pageRegistrationDataImport.getButtonImportFile().text
        assert not pageRegistrationDataImport.getButtonImportFile().is_enabled()
        assert pageRegistrationDataImport.getButtonImportFile().get_property("disabled")
        pageRegistrationDataImport.getImportTypeSelect().click()
        assert pageRegistrationDataImport.koboItemText in pageRegistrationDataImport.getKoboItem().text
        assert pageRegistrationDataImport.excelItemText in pageRegistrationDataImport.getExcelItem().text
        pageRegistrationDataImport.getExcelItem().click()
        pageRegistrationDataImport.getInputName()

    def test_smoke_registration_data_details_page(
            self,
            create_programs: None,
            add_rdi: None,
            pageRegistrationDataImport: RegistrationDataImport,
            pageDetailsRegistrationDataImport: RDIDetailsPage,
    ) -> None:
        # Go to Registration Data Import
        pageRegistrationDataImport.selectGlobalProgramFilter("Test Programm").click()
        pageRegistrationDataImport.getNavRegistrationDataImport().click()
        assert pageRegistrationDataImport.expectedRows(2)
        assert "2" in pageRegistrationDataImport.getTableTitle().text
        pageRegistrationDataImport.getRows()[0].click()
        # Check Elements on Details page
        assert "Test Other Status" in pageDetailsRegistrationDataImport.getPageHeaderTitle().text
        assert "IN REVIEW" in pageDetailsRegistrationDataImport.getLabelStatus().text
        assert "KOBO" in pageDetailsRegistrationDataImport.getLabelSourceOfData().text
        assert "21 Mar 2023 9:22 AM" in pageDetailsRegistrationDataImport.getLabelImportDate().text
        pageDetailsRegistrationDataImport.getLabelImportedBy()
        assert (
            "TOTAL NUMBER OF HOUSEHOLDS"
            in pageDetailsRegistrationDataImport.getLabelizedFieldContainerHouseholds().text
        )
        assert "3" in pageDetailsRegistrationDataImport.getLabelTotalNumberOfHouseholds().text
        assert (
            "TOTAL NUMBER OF INDIVIDUALS"
            in pageDetailsRegistrationDataImport.getLabelizedFieldContainerIndividuals().text
        )
        assert "9" in pageDetailsRegistrationDataImport.getLabelTotalNumberOfIndividuals().text
        assert (
            pageDetailsRegistrationDataImport.buttonMergeRdiText
            in pageDetailsRegistrationDataImport.getButtonMergeRdi().text
        )
        assert (
            pageDetailsRegistrationDataImport.buttonRefuseRdiText
            in pageDetailsRegistrationDataImport.getButtonRefuseRdi().text
        )


@pytest.mark.usefixtures("login")
class TestRegistrationDataImport:
    def test_smoke_registration_data_import_happy_path(
            self, create_programs: None, add_rdi: None, pageRegistrationDataImport: RegistrationDataImport
    ) -> None:
        # Go to Registration Data Import
        pageRegistrationDataImport.driver.get_log('browser')
        pageRegistrationDataImport.selectGlobalProgramFilter("Test Programm").click()
        pageRegistrationDataImport.getNavRegistrationDataImport().click()
        assert pageRegistrationDataImport.titleText in pageRegistrationDataImport.getPageHeaderTitle().text
        pageRegistrationDataImport.getButtonImport().click()
        pageRegistrationDataImport.getImportTypeSelect().click()
        pageRegistrationDataImport.getExcelItem().click()
        pageRegistrationDataImport.upload_file(f"{pytest.SELENIUM_PATH}/helpers/registration_data_import_template.xlsx")
        pageRegistrationDataImport.screenshot("1", delay_sec=5)
        logs = pageRegistrationDataImport.driver.get_log('browser')
        print(logs)
        for entry in logs:
            print(entry)
        pageRegistrationDataImport.getInputName().send_keys("Test 1234 !")
