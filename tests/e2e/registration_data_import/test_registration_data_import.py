from datetime import datetime

import pytest

from e2e.page_object.registration_data_import.rdi_details_page import RDIDetailsPage
from e2e.page_object.registration_data_import.registration_data_import import (
    RegistrationDataImport as RegistrationDataImportComponent,
)
from extras.test_utils.factories import ProgramFactory
from hope.models import (
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    ImportData,
    Program,
    RegistrationDataImport,
    User,
)

pytestmark = pytest.mark.django_db()


@pytest.fixture
def create_programs(business_area: BusinessArea) -> None:
    dct = DataCollectingType.objects.get(code="full")
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    ProgramFactory(
        name="Test Programm",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def add_rdi(business_area: BusinessArea) -> None:
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
        page_registration_data_import.assert_page_header_title(page_registration_data_import.title_text)
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
        page_details_registration_data_import.assert_page_header_title("Test Other Status")
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
