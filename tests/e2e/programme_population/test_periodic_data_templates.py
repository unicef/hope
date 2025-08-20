import os
from time import sleep

import pytest
from e2e.page_object.programme_population.individuals import Individuals
from e2e.page_object.programme_population.periodic_data_update_templates import (
    PDUXlsxTemplates,
    PDUXlsxTemplatesDetails,
)
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.periodic_data_update import (
    PDUXlsxTemplateFactory,
)
from extras.test_utils.factories.program import BeneficiaryGroupFactory, ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from selenium.webdriver.common.by import By

from hope.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hope.apps.household.models import Individual
from hope.apps.periodic_data_update.models import PDUXlsxTemplate
from hope.apps.periodic_data_update.utils import (
    field_label_to_field_name,
    populate_pdu_with_null_values,
)
from hope.apps.program.models import Program
from hope.apps.registration_data.models import RegistrationDataImport

pytestmark = pytest.mark.django_db()


@pytest.fixture
def clear_downloaded_files(download_path: str) -> None:
    for file in os.listdir(download_path):
        os.remove(os.path.join(download_path, file))
    yield
    for file in os.listdir(download_path):
        os.remove(os.path.join(download_path, file))


@pytest.fixture
def program() -> Program:
    business_area = create_afghanistan()
    beneficiary_group = BeneficiaryGroupFactory(
        name="Main Menu",
        group_label="Items Group",
        group_label_plural="Items Groups",
        member_label="Item",
        member_label_plural="Items",
        master_detail=True,
    )
    return ProgramFactory(
        name="Test Program",
        status=Program.ACTIVE,
        business_area=business_area,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def individual(program: Program) -> Individual:
    business_area = create_afghanistan()
    rdi = RegistrationDataImportFactory(status=RegistrationDataImport.MERGED, program=program)
    household, individuals = create_household_and_individuals(
        household_data={
            "business_area": business_area,
            "program_id": program.pk,
            "registration_data_import": rdi,
        },
        individuals_data=[
            {
                "business_area": business_area,
                "program_id": program.pk,
                "registration_data_import": rdi,
            },
        ],
    )
    return individuals[0]


@pytest.fixture
def string_attribute(program: Program) -> FlexibleAttribute:
    return create_flexible_attribute(
        label="Test String Attribute",
        subtype=FlexibleAttribute.STRING,
        number_of_rounds=1,
        rounds_names=["Test Round"],
        program=program,
    )


@pytest.fixture
def date_attribute(program: Program) -> FlexibleAttribute:
    return create_flexible_attribute(
        label="Test Date Attribute",
        subtype=FlexibleAttribute.DATE,
        number_of_rounds=1,
        rounds_names=["Test Round"],
        program=program,
    )


def create_flexible_attribute(
    label: str,
    subtype: str,
    number_of_rounds: int,
    rounds_names: list[str],
    program: Program,
) -> FlexibleAttribute:
    name = field_label_to_field_name(label)
    flexible_attribute = FlexibleAttribute.objects.create(
        label={"English(EN)": label},
        name=name,
        type=FlexibleAttribute.PDU,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        program=program,
    )
    flexible_attribute.pdu_data = PeriodicFieldData.objects.create(
        subtype=subtype, number_of_rounds=number_of_rounds, rounds_names=rounds_names
    )
    flexible_attribute.save()
    return flexible_attribute


@pytest.mark.usefixtures("login")
class TestPeriodicDataTemplates:
    def test_periodic_data_template_export_and_download(
        self,
        clear_downloaded_files: None,
        program: Program,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
        individual: Individual,
        download_path: str,
    ) -> None:
        populate_pdu_with_null_values(program, individual.flex_fields)
        individual.save()
        periodic_data_update_template = PDUXlsxTemplate.objects.create(
            program=program,
            business_area=program.business_area,
            status=PDUXlsxTemplate.Status.TO_EXPORT,
            filters={},
            rounds_data=[
                {
                    "field": string_attribute.name,
                    "round": 1,
                    "round_name": string_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
        )
        pageIndividuals.selectGlobalProgramFilter(program.name)
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()
        status = pageIndividuals.getTemplateStatus(periodic_data_update_template.pk).text
        assert status == "NOT SCHEDULED"
        pageIndividuals.getExportBtn(periodic_data_update_template.pk).click()
        for _ in range(10):
            status = pageIndividuals.getTemplateStatus(periodic_data_update_template.pk).text
            if status == "EXPORTED":
                break
            sleep(1)
        else:
            assert status == "EXPORTED"
        pageIndividuals.getDownloadBtn(periodic_data_update_template.pk).click()
        periodic_data_update_template.refresh_from_db()
        assert (
            pageIndividuals.check_file_exists(os.path.join(download_path, periodic_data_update_template.file.file.name))
            is True
        )

    @pytest.mark.night
    def test_periodic_data_template_list(
        self,
        program: Program,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
        pagePDUXlsxTemplates: PDUXlsxTemplates,
    ) -> None:
        periodic_data_update_template = PDUXlsxTemplateFactory(
            program=program,
            business_area=program.business_area,
            status=PDUXlsxTemplate.Status.EXPORTED,
            number_of_records=10,
            filters={},
            rounds_data=[
                {
                    "field": string_attribute.name,
                    "round": 1,
                    "round_name": string_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
        )
        periodic_data_update_template.refresh_from_db()
        index = periodic_data_update_template.id

        pageIndividuals.selectGlobalProgramFilter(program.name)
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()

        pagePDUXlsxTemplates.getPduTemplatesBtn().click()
        assert str(index) in pagePDUXlsxTemplates.getTemplateId(index).text
        assert (
            str(periodic_data_update_template.number_of_records)
            in pagePDUXlsxTemplates.getTemplateRecords(index).text
        )
        assert (
            f"{periodic_data_update_template.created_at:%-d %b %Y}"
            in pagePDUXlsxTemplates.getTemplateCreatedAt(index).text
        )
        assert (
            periodic_data_update_template.created_by.get_full_name()
            in pagePDUXlsxTemplates.getTemplateCreatedBy(index).text
        )

        assert "EXPORTED" in pagePDUXlsxTemplates.getTemplateStatus(index).text

    @pytest.mark.night
    def test_periodic_data_template_details(
        self,
        program: Program,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
        pagePDUXlsxTemplates: PDUXlsxTemplates,
        individual: Individual,
    ) -> None:
        populate_pdu_with_null_values(program, individual.flex_fields)
        individual.save()
        rounds_data = [
            {
                "field": string_attribute.name,
                "round": 1,
                "round_name": string_attribute.pdu_data.rounds_names[0],
                "number_of_records": 0,
            }
        ]
        periodic_data_update_template = PDUXlsxTemplate.objects.create(
            program=program,
            business_area=program.business_area,
            status=PDUXlsxTemplate.Status.TO_EXPORT,
            filters={},
            rounds_data=rounds_data,
        )
        periodic_data_update_template.refresh_from_db()
        index = periodic_data_update_template.id

        pageIndividuals.selectGlobalProgramFilter(program.name)
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()

        pagePDUXlsxTemplates.getPduTemplatesBtn().click()

        btn = pagePDUXlsxTemplates.getTemplateDetailsBtn(index)
        btn.find_element(By.TAG_NAME, "button").click()
        pagePDUXlsxTemplates.getDetailModal()

        assert string_attribute.label["English(EN)"] in pagePDUXlsxTemplates.getTemplateField(0).text
        assert str(rounds_data[0]["round"]) in pagePDUXlsxTemplates.getTemplateRoundNumber(0).text
        assert rounds_data[0]["round_name"] in pagePDUXlsxTemplates.getTemplateRoundName(0).text
        assert (
            str(rounds_data[0]["number_of_records"])
            in pagePDUXlsxTemplates.getTemplateNumberOfIndividuals(0).text
        )

    @pytest.mark.night
    def test_periodic_data_template_create_and_download(
        self,
        program: Program,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
        pagePDUXlsxTemplates: PDUXlsxTemplates,
        pagePDUXlsxTemplatesDetails: PDUXlsxTemplatesDetails,
        individual: Individual,
        download_path: str,
        clear_downloaded_files: None,
    ) -> None:
        populate_pdu_with_null_values(program, individual.flex_fields)
        individual.save()
        pageIndividuals.selectGlobalProgramFilter(program.name)
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()

        pagePDUXlsxTemplates.getNewTemplateButton().click()
        pagePDUXlsxTemplatesDetails.getFiltersRegistrationDataImport().click()

        pagePDUXlsxTemplatesDetails.select_listbox_element(individual.registration_data_import.name)
        pagePDUXlsxTemplatesDetails.getSubmitButton().click()
        pagePDUXlsxTemplatesDetails.getCheckbox(string_attribute.name).click()
        pagePDUXlsxTemplatesDetails.getSubmitButton().click()
        pagePDUXlsxTemplates.getNewTemplateButton()  # wait for the page to load
        assert PDUXlsxTemplate.objects.count() == 1
        periodic_data_update_template = PDUXlsxTemplate.objects.first()
        assert (
            str(periodic_data_update_template.id)
            in pagePDUXlsxTemplates.getTemplateId(periodic_data_update_template.id).text
        )

        for _ in range(10):
            status = pageIndividuals.getTemplateStatus(periodic_data_update_template.pk).text
            if status == "EXPORTED":
                break
            sleep(1)
        else:
            assert status == "EXPORTED"

        pageIndividuals.getDownloadBtn(periodic_data_update_template.pk).click()
        periodic_data_update_template.refresh_from_db()
        assert (
            pageIndividuals.check_file_exists(os.path.join(download_path, periodic_data_update_template.file.file.name))
            is True
        )
