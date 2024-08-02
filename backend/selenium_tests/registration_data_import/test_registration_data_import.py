from django.conf import settings
from django.core.management import call_command

import pytest
from elasticsearch_dsl import connections
from page_object.programme_population.households_details import HouseholdsDetails
from page_object.registration_data_import.rdi_details_page import RDIDetailsPage
from page_object.registration_data_import.registration_data_import import (
    RegistrationDataImport,
)

from hct_mis_api.apps.account.fixtures import PartnerFactory
from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area, AreaType, Country
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.django_db(transaction=True, databases=["registration_datahub", "default"])


@pytest.fixture
def registration_datahub(db) -> None:  # type: ignore
    connections.create_connection(alias="registration_datahub", hosts=[settings.ELASTICSEARCH_HOST], timeout=20)
    rebuild_search_index()
    yield
    connections.remove_connection(alias="registration_datahub")


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    yield


@pytest.fixture
def add_rdi() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    yield


@pytest.fixture
def unicef_partner() -> Partner:
    yield PartnerFactory(name="UNICEF")


@pytest.fixture
def unhcr_partner() -> Partner:
    yield PartnerFactory(name="UNHCR")


@pytest.fixture
def wfp_partner() -> Partner:
    yield PartnerFactory(name="WFP")


@pytest.fixture
def country() -> Country:
    yield Country.objects.get(name="Afghanistan")


@pytest.fixture
def kobo_setup(business_area: BusinessArea, country: Country) -> None:
    business_area.kobo_token = "kobo_token"
    business_area.kobo_username = "hope_kobo_admin_nga"
    business_area.save()
    business_area.countries.set([country])


@pytest.fixture
def areas(country: Country) -> None:
    area_type_1 = AreaType.objects.create(name="State", area_level=1, country=country)
    area_type_2 = AreaType.objects.create(
        name="Local government area", area_level=2, country=country, parent=area_type_1
    )
    area_type_3 = AreaType.objects.create(name="Ward", area_level=3, country=country, parent=area_type_2)
    area_1 = Area.objects.create(name="Borno", p_code="NG008", area_type=area_type_1)
    area_2 = Area.objects.create(name="Bama", p_code="NG008003", area_type=area_type_2, parent=area_1)
    Area.objects.create(name="Andara", p_code="NG008003001", area_type=area_type_3, parent=area_2)


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


class TestRegistrationDataImport:
    def test_registration_data_import_happy_path(
        self,
        registration_datahub: None,
        login: None,
        create_programs: None,
        add_rdi: None,
        unhcr_partner: Partner,
        wfp_partner: Partner,
        pageRegistrationDataImport: RegistrationDataImport,
        pageDetailsRegistrationDataImport: RDIDetailsPage,
        pageHouseholdsDetails: HouseholdsDetails,
    ) -> None:
        # Go to Registration Data Import
        pageRegistrationDataImport.selectGlobalProgramFilter("Test Programm").click()
        pageRegistrationDataImport.getNavRegistrationDataImport().click()
        assert pageRegistrationDataImport.titleText in pageRegistrationDataImport.getPageHeaderTitle().text
        pageRegistrationDataImport.getButtonImport().click()
        pageRegistrationDataImport.getImportTypeSelect().click()
        pageRegistrationDataImport.getExcelItem().click()
        pageRegistrationDataImport.upload_file(f"{pytest.SELENIUM_PATH}/helpers/rdi_import_50_hh_50_ind.xlsx")
        pageRegistrationDataImport.getInputName().send_keys("Test 1234 !")
        assert pageRegistrationDataImport.buttonImportFileIsEnabled()
        assert "50" in pageRegistrationDataImport.getNumberOfHouseholds().text
        assert "208" in pageRegistrationDataImport.getNumberOfIndividuals().text
        pageRegistrationDataImport.getButtonImportFile().click()
        pageRegistrationDataImport.disappearButtonImportFile()
        pageDetailsRegistrationDataImport.waitForStatus("IN REVIEW")
        assert "50" in pageDetailsRegistrationDataImport.getLabelTotalNumberOfHouseholds().text
        assert "208" in pageDetailsRegistrationDataImport.getLabelTotalNumberOfIndividuals().text
        pageDetailsRegistrationDataImport.getButtonMergeRdi().click()
        pageDetailsRegistrationDataImport.getButtonMerge().click()
        pageDetailsRegistrationDataImport.waitForStatus("MERGED")
        assert "MERGED" == pageDetailsRegistrationDataImport.getStatusContainer().text
        assert "VIEW TICKETS" in pageDetailsRegistrationDataImport.getButtonViewTickets().text
        pageDetailsRegistrationDataImport.getButtonIndividuals().click()
        pageDetailsRegistrationDataImport.getButtonHouseholds().click()
        hausehold_id = (
            pageDetailsRegistrationDataImport.getImportedHouseholdsRow(0).find_elements("tag name", "td")[1].text
        )
        pageDetailsRegistrationDataImport.getImportedHouseholdsRow(0).find_elements("tag name", "td")[1].click()
        assert hausehold_id in pageHouseholdsDetails.getPageHeaderTitle().text

    @pytest.mark.xfail(reason="Unskip after fix: 210576")
    @pytest.mark.vcr(ignore_localhost=True)
    def test_import_empty_kobo_form(
        self, login: None, create_programs: None, pageRegistrationDataImport: RegistrationDataImport, kobo_setup: None
    ) -> None:
        # Go to Registration Data Import
        pageRegistrationDataImport.selectGlobalProgramFilter("Test Programm").click()
        pageRegistrationDataImport.getNavRegistrationDataImport().click()
        assert pageRegistrationDataImport.titleText in pageRegistrationDataImport.getPageHeaderTitle().text
        pageRegistrationDataImport.getButtonImport().click()
        # Check Elements on Page
        assert pageRegistrationDataImport.getButtonImportFile().get_property("disabled")
        pageRegistrationDataImport.getImportTypeSelect().click()
        assert pageRegistrationDataImport.koboItemText in pageRegistrationDataImport.getKoboItem().text
        pageRegistrationDataImport.getKoboItem().click()
        pageRegistrationDataImport.getInputName().send_keys("Test 1234 !")

        pageRegistrationDataImport.getKoboProjectSelect().click()
        pageRegistrationDataImport.select_listbox_element("Education new programme").click()

        assert pageRegistrationDataImport.buttonImportFileIsEnabled(timeout=300)
        assert "0" in pageRegistrationDataImport.getNumberOfHouseholds().text
        assert "0" in pageRegistrationDataImport.getNumberOfIndividuals().text
        pageRegistrationDataImport.getButtonImportFile().click()
        pageRegistrationDataImport.checkAlert("Cannot import empty form")

    @pytest.mark.vcr(ignore_localhost=True, ignore_hosts=["elasticsearch"])
    def test_import_kobo_form(
        self,
        login: None,
        create_programs: None,
        pageRegistrationDataImport: RegistrationDataImport,
        pageDetailsRegistrationDataImport: RDIDetailsPage,
        kobo_setup: None,
        areas: None
    ) -> None:
        # Go to Registration Data Import
        pageRegistrationDataImport.selectGlobalProgramFilter("Test Programm").click()
        pageRegistrationDataImport.getNavRegistrationDataImport().click()
        assert pageRegistrationDataImport.titleText in pageRegistrationDataImport.getPageHeaderTitle().text
        pageRegistrationDataImport.getButtonImport().click()
        # Check Elements on Page
        assert pageRegistrationDataImport.getButtonImportFile().get_property("disabled")
        pageRegistrationDataImport.getImportTypeSelect().click()
        assert pageRegistrationDataImport.koboItemText in pageRegistrationDataImport.getKoboItem().text
        pageRegistrationDataImport.getKoboItem().click()
        pageRegistrationDataImport.getInputName().send_keys("Test 1234 !")

        pageRegistrationDataImport.getKoboProjectSelect().click()
        pageRegistrationDataImport.select_listbox_element("UNICEF NGA Education").click()

        assert pageRegistrationDataImport.buttonImportFileIsEnabled(timeout=10)
        assert "1" in pageRegistrationDataImport.getNumberOfHouseholds().text
        assert "2" in pageRegistrationDataImport.getNumberOfIndividuals().text

        pageRegistrationDataImport.getButtonImportFile().click()
        pageRegistrationDataImport.disappearButtonImportFile()
        pageDetailsRegistrationDataImport.waitForStatus("IN REVIEW")
        assert "1" in pageDetailsRegistrationDataImport.getLabelTotalNumberOfHouseholds().text
        assert "2" in pageDetailsRegistrationDataImport.getLabelTotalNumberOfIndividuals().text
