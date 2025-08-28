from datetime import datetime
from time import sleep

from django.conf import settings
from e2e.page_object.programme_population.households_details import HouseholdsDetails
from e2e.page_object.registration_data_import.rdi_details_page import RDIDetailsPage
from e2e.page_object.registration_data_import.registration_data_import import (
    RegistrationDataImport as RegistrationDataImportComponent,
)
from elasticsearch_dsl import connections
import pytest

from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.models import Partner, User
from hope.apps.core.models import BusinessArea, DataCollectingType
from hope.apps.geo.models import Area, AreaType, Country
from hope.apps.program.models import BeneficiaryGroup, Program
from hope.apps.registration_data.models import ImportData, RegistrationDataImport
from hope.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.django_db()


@pytest.fixture
def registration_datahub(db) -> None:  # type: ignore
    connections.create_connection(alias="registration_datahub", hosts=[settings.ELASTICSEARCH_HOST], timeout=20)
    rebuild_search_index()
    yield
    connections.remove_connection(alias="registration_datahub")


@pytest.fixture
def create_programs() -> None:
    business_area = create_afghanistan()
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    ProgramFactory(
        name="Test Programm",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def add_rdi() -> None:
    business_area = BusinessArea.objects.get(slug="afghanistan")
    programme = Program.objects.filter(name="Test Programm").first()
    imported_by = User.objects.first()
    number_of_individuals = 9
    number_of_households = 3
    status = RegistrationDataImport.IN_REVIEW

    import_data = ImportData.objects.create(
        status=ImportData.STATUS_PENDING,
        business_area_slug=business_area.slug,
        data_type=ImportData.FLEX_REGISTRATION,
        number_of_individuals=number_of_individuals,
        number_of_households=number_of_households,
        created_by_id=imported_by.id if imported_by else None,
    )
    RegistrationDataImport.objects.create(
        name="Test",
        data_source=RegistrationDataImport.FLEX_REGISTRATION,
        imported_by=imported_by,
        number_of_individuals=number_of_individuals,
        number_of_households=number_of_households,
        business_area=business_area,
        status=status,
        program=programme,
        import_data=import_data,
    )

    RegistrationDataImport.objects.create(
        name="Test Other Status",
        data_source=RegistrationDataImport.KOBO,
        imported_by=imported_by,
        number_of_individuals=number_of_individuals,
        number_of_households=number_of_households,
        business_area=business_area,
        status=status,
        program=programme,
    )


@pytest.fixture
def unicef_partner() -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_hq() -> Partner:
    return PartnerFactory(name="UNICEF HQ", parent=PartnerFactory(name="UNICEF"))


@pytest.fixture
def unhcr_partner() -> Partner:
    return PartnerFactory(name="UNHCR")


@pytest.fixture
def wfp_partner() -> Partner:
    return PartnerFactory(name="WFP")


@pytest.fixture
def country() -> Country:
    return Country.objects.get(name="Afghanistan")


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
        self,
        create_programs: None,
        add_rdi: None,
        page_registration_data_import: RegistrationDataImportComponent,
    ) -> None:
        # Go to Registration Data Import
        page_registration_data_import.select_global_program_filter("Test Programm")
        page_registration_data_import.get_nav_registration_data_import().click()
        # Check Elements on Page
        assert page_registration_data_import.title_text in page_registration_data_import.get_page_header_title().text
        assert page_registration_data_import.import_text in page_registration_data_import.get_button_import().text
        assert page_registration_data_import.table_title_text in page_registration_data_import.get_table_title().text
        assert page_registration_data_import.expected_rows(2)
        assert "2" in page_registration_data_import.get_table_title().text
        assert "Title" in page_registration_data_import.get_table_label()[0].text
        assert "Status" in page_registration_data_import.get_table_label()[1].text
        assert "Import Date" in page_registration_data_import.get_table_label()[2].text
        assert "Num. of Items" in page_registration_data_import.get_table_label()[3].text
        assert "Num. of Items Groups" in page_registration_data_import.get_table_label()[4].text
        assert "Imported by" in page_registration_data_import.get_table_label()[5].text
        assert "Data Source" in page_registration_data_import.get_table_label()[6].text

    @pytest.mark.skip(reason="RDI import only possible though Program Population")
    def test_smoke_registration_data_import_select_file(
        self,
        create_programs: None,
        page_registration_data_import: RegistrationDataImportComponent,
    ) -> None:
        # Go to Registration Data Import
        page_registration_data_import.select_global_program_filter("Test Programm")
        page_registration_data_import.get_nav_registration_data_import().click()
        assert page_registration_data_import.title_text in page_registration_data_import.get_page_header_title().text
        page_registration_data_import.get_button_import().click()
        # Check Elements on Page
        assert (
            page_registration_data_import.download_template_text
            in page_registration_data_import.get_download_template().text
        )
        assert page_registration_data_import.import_text in page_registration_data_import.get_button_import_file().text
        assert not page_registration_data_import.get_button_import_file().is_enabled()
        assert page_registration_data_import.get_button_import_file().get_property("disabled")
        page_registration_data_import.get_import_type_select().click()
        assert page_registration_data_import.kobo_item_text in page_registration_data_import.get_kobo_item().text
        assert page_registration_data_import.excel_item_text in page_registration_data_import.get_excel_item().text
        page_registration_data_import.get_excel_item().click()
        page_registration_data_import.get_input_name()

    def test_smoke_registration_data_details_page(
        self,
        create_programs: None,
        add_rdi: None,
        page_registration_data_import: RegistrationDataImportComponent,
        page_details_registration_data_import: RDIDetailsPage,
    ) -> None:
        # Go to Registration Data Import
        page_registration_data_import.select_global_program_filter("Test Programm")
        page_registration_data_import.get_nav_registration_data_import().click()
        assert page_registration_data_import.expected_rows(2)
        assert "2" in page_registration_data_import.get_table_title().text
        page_registration_data_import.get_rows()[0].click()
        # Check Elements on Details page
        assert "Test Other Status" in page_details_registration_data_import.get_page_header_title().text
        assert "IN REVIEW" in page_details_registration_data_import.get_label_status().text
        assert "KoBo" in page_details_registration_data_import.get_label_source_of_data().text
        assert (
            datetime.now().strftime("%-d %b %Y") in page_details_registration_data_import.get_label_import_date().text
        )
        page_details_registration_data_import.get_label_imported_by()
        assert (
            "TOTAL NUMBER OF ITEMS GROUPS"
            in page_details_registration_data_import.get_labelized_field_container_households().text
        )
        assert "3" in page_details_registration_data_import.get_label_total_number_of_households().text
        assert (
            "TOTAL NUMBER OF ITEMS"
            in page_details_registration_data_import.get_labelized_field_container_individuals().text
        )
        assert "9" in page_details_registration_data_import.get_label_total_number_of_individuals().text
        assert (
            page_details_registration_data_import.button_merge_rdi_text
            in page_details_registration_data_import.get_button_merge_rdi().text
        )
        assert (
            page_details_registration_data_import.button_refuse_rdi_text
            in page_details_registration_data_import.get_button_refuse_rdi().text
        )


class TestRegistrationDataImport:
    @pytest.mark.skip(reason="RDI import only possible though Program Population")
    def test_registration_data_import_happy_path(
        self,
        registration_datahub: None,
        login: None,
        create_programs: None,
        add_rdi: None,
        unhcr_partner: Partner,
        wfp_partner: Partner,
        page_registration_data_import: RegistrationDataImportComponent,
        page_details_registration_data_import: RDIDetailsPage,
        page_households_details: HouseholdsDetails,
    ) -> None:
        # Go to Registration Data Import
        page_registration_data_import.select_global_program_filter("Test Programm")
        page_registration_data_import.get_nav_registration_data_import().click()
        assert page_registration_data_import.title_text in page_registration_data_import.get_page_header_title().text
        page_registration_data_import.get_button_import().click()
        page_registration_data_import.get_import_type_select().click()
        page_registration_data_import.get_excel_item().click()
        page_registration_data_import.upload_file(f"{pytest.SELENIUM_PATH}/helpers/rdi_import_50_hh_50_ind.xlsx")
        page_registration_data_import.get_input_name().send_keys("Test 1234 !")
        assert page_registration_data_import.button_import_file_is_enabled()
        assert "50" in page_registration_data_import.get_number_of_households().text
        assert "208" in page_registration_data_import.get_number_of_individuals().text
        page_registration_data_import.get_button_import_file().click()
        page_registration_data_import.disappear_button_import_file()

        page_details_registration_data_import.wait_for_status("IN REVIEW")
        assert "50" in page_details_registration_data_import.get_label_total_number_of_households().text
        assert "208" in page_details_registration_data_import.get_label_total_number_of_individuals().text
        page_details_registration_data_import.element_clickable(page_details_registration_data_import.button_merge_rdi)
        sleep(2)
        page_details_registration_data_import.get_button_merge_rdi().click()
        page_details_registration_data_import.element_clickable(page_details_registration_data_import.button_merge)
        sleep(2)
        page_details_registration_data_import.get_button_merge().click()
        page_details_registration_data_import.wait_for_status("MERGED")
        page_details_registration_data_import.wait_for_text(
            "MERGED", page_details_registration_data_import.status_container
        )
        assert "VIEW TICKETS" in page_details_registration_data_import.get_button_view_tickets().text
        page_details_registration_data_import.get_button_individuals().click()
        page_details_registration_data_import.get_button_households().click()
        hausehold_id = (
            page_details_registration_data_import.get_imported_households_row(0).find_elements("tag name", "td")[1].text
        )
        page_details_registration_data_import.get_imported_households_row(0).find_elements("tag name", "td")[1].click()
        assert hausehold_id in page_households_details.get_page_header_title().text

    @pytest.mark.night
    @pytest.mark.skip(reason="Kobo form is not available. This is a external service, we cannot control it.")
    @pytest.mark.vcr(ignore_localhost=True)
    def test_import_empty_kobo_form(
        self,
        login: None,
        create_programs: None,
        page_registration_data_import: RegistrationDataImportComponent,
        kobo_setup: None,
    ) -> None:
        # Go to Registration Data Import
        page_registration_data_import.select_global_program_filter("Test Programm")
        page_registration_data_import.get_nav_registration_data_import().click()
        assert page_registration_data_import.title_text in page_registration_data_import.get_page_header_title().text
        page_registration_data_import.get_button_import().click()
        # Check Elements on Page
        assert page_registration_data_import.get_button_import_file().get_property("disabled")
        page_registration_data_import.get_import_type_select().click()
        assert page_registration_data_import.kobo_item_text in page_registration_data_import.get_kobo_item().text
        page_registration_data_import.get_kobo_item().click()
        page_registration_data_import.get_input_name().send_keys("Test 1234 !")

        page_registration_data_import.get_kobo_project_select().click()
        page_registration_data_import.select_listbox_element("Education new programme")

        assert page_registration_data_import.button_import_file_is_enabled(timeout=300)
        assert "0" in page_registration_data_import.get_number_of_households().text
        assert "0" in page_registration_data_import.get_number_of_individuals().text
        page_registration_data_import.get_button_import_file().click()
        page_registration_data_import.check_alert("Cannot import empty form")

    @pytest.mark.night
    @pytest.mark.skip(reason="Kobo form is not available. This is a external service, we cannot control it.")
    @pytest.mark.vcr(ignore_localhost=True, ignore_hosts=["elasticsearch"])
    def test_import_kobo_form(
        self,
        login: None,
        create_programs: None,
        page_registration_data_import: RegistrationDataImportComponent,
        page_details_registration_data_import: RDIDetailsPage,
        kobo_setup: None,
        areas: None,
    ) -> None:
        # Go to Registration Data Import
        page_registration_data_import.select_global_program_filter("Test Programm")
        page_registration_data_import.get_nav_registration_data_import().click()
        assert page_registration_data_import.title_text in page_registration_data_import.get_page_header_title().text
        page_registration_data_import.get_button_import().click()
        # Check Elements on Page
        assert page_registration_data_import.get_button_import_file().get_property("disabled")
        page_registration_data_import.get_import_type_select().click()
        assert page_registration_data_import.kobo_item_text in page_registration_data_import.get_kobo_item().text
        page_registration_data_import.get_kobo_item().click()
        page_registration_data_import.get_input_name().send_keys("Test 1234 !")

        page_registration_data_import.get_kobo_project_select().click()
        page_registration_data_import.select_listbox_element("UNICEF NGA Education")

        assert page_registration_data_import.button_import_file_is_enabled(timeout=300)
        assert "1" in page_registration_data_import.get_number_of_households().text
        assert "2" in page_registration_data_import.get_number_of_individuals().text

        page_registration_data_import.get_button_import_file().click()
        page_registration_data_import.disappear_button_import_file()
        page_details_registration_data_import.wait_for_status("IN REVIEW")
        assert "1" in page_details_registration_data_import.get_label_total_number_of_households().text
        assert "2" in page_details_registration_data_import.get_label_total_number_of_individuals().text
