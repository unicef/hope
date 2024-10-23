import os
from time import sleep

from django.conf import settings

import pytest
from selenium.webdriver.common.by import By

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.periodic_data_update.fixtures import (
    PeriodicDataUpdateTemplateFactory,
)
from hct_mis_api.apps.periodic_data_update.models import PeriodicDataUpdateTemplate
from hct_mis_api.apps.periodic_data_update.utils import (
    field_label_to_field_name,
    populate_pdu_with_null_values,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from tests.selenium.page_object.programme_population.individuals import Individuals
from tests.selenium.page_object.programme_population.periodic_data_update_templates import (
    PeriodicDatUpdateTemplates,
    PeriodicDatUpdateTemplatesDetails,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def clear_downloaded_files() -> None:
    yield
    for file in os.listdir(settings.DOWNLOAD_DIRECTORY):
        os.remove(os.path.join(settings.DOWNLOAD_DIRECTORY, file))


@pytest.fixture
def program() -> Program:
    business_area = create_afghanistan()
    return ProgramFactory(name="Test Program", status=Program.ACTIVE, business_area=business_area)


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
    label: str, subtype: str, number_of_rounds: int, rounds_names: list[str], program: Program
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
        program: Program,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
        individual: Individual,
        clear_downloaded_files: None,
    ) -> None:
        populate_pdu_with_null_values(program, individual.flex_fields)
        individual.save()
        periodic_data_update_template = PeriodicDataUpdateTemplate.objects.create(
            program=program,
            business_area=program.business_area,
            status=PeriodicDataUpdateTemplate.Status.TO_EXPORT,
            filters=dict(),
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
            pageIndividuals.check_file_exists(
                os.path.join(settings.DOWNLOAD_DIRECTORY, periodic_data_update_template.file.file.name)
            )
            is True
        )

    @pytest.mark.night
    def test_periodic_data_template_list(
        self,
        program: Program,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
        pagePeriodicDataUpdateTemplates: PeriodicDatUpdateTemplates,
    ) -> None:
        periodic_data_update_template = PeriodicDataUpdateTemplateFactory(
            program=program,
            business_area=program.business_area,
            status=PeriodicDataUpdateTemplate.Status.EXPORTED,
            number_of_records=10,
            filters=dict(),
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

        pagePeriodicDataUpdateTemplates.getPduTemplatesBtn().click()
        assert str(index) in pagePeriodicDataUpdateTemplates.getTemplateId(index).text
        assert (
            str(periodic_data_update_template.number_of_records)
            in pagePeriodicDataUpdateTemplates.getTemplateRecords(index).text
        )
        assert (
            f"{periodic_data_update_template.created_at:%-d %b %Y}"
            in pagePeriodicDataUpdateTemplates.getTemplateCreatedAt(index).text
        )
        assert (
            periodic_data_update_template.created_by.get_full_name()
            in pagePeriodicDataUpdateTemplates.getTemplateCreatedBy(index).text
        )

        assert "EXPORTED" in pagePeriodicDataUpdateTemplates.getTemplateStatus(index).text

    @pytest.mark.night
    def test_periodic_data_template_details(
        self,
        program: Program,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
        pagePeriodicDataUpdateTemplates: PeriodicDatUpdateTemplates,
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
        periodic_data_update_template = PeriodicDataUpdateTemplate.objects.create(
            program=program,
            business_area=program.business_area,
            status=PeriodicDataUpdateTemplate.Status.TO_EXPORT,
            filters=dict(),
            rounds_data=rounds_data,
        )
        periodic_data_update_template.refresh_from_db()
        index = periodic_data_update_template.id

        pageIndividuals.selectGlobalProgramFilter(program.name)
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()

        pagePeriodicDataUpdateTemplates.getPduTemplatesBtn().click()

        btn = pagePeriodicDataUpdateTemplates.getTemplateDetailsBtn(index)
        btn.find_element(By.TAG_NAME, "button").click()
        pagePeriodicDataUpdateTemplates.getDetailModal()

        assert string_attribute.label["English(EN)"] in pagePeriodicDataUpdateTemplates.getTemplateField(0).text
        assert str(rounds_data[0]["round"]) in pagePeriodicDataUpdateTemplates.getTemplateRoundNumber(0).text
        assert rounds_data[0]["round_name"] in pagePeriodicDataUpdateTemplates.getTemplateRoundName(0).text
        assert (
            str(rounds_data[0]["number_of_records"])
            in pagePeriodicDataUpdateTemplates.getTemplateNumberOfIndividuals(0).text
        )

    def test_periodic_data_template_create_and_download(
        self,
        program: Program,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
        pagePeriodicDataUpdateTemplates: PeriodicDatUpdateTemplates,
        pagePeriodicDataUpdateTemplatesDetails: PeriodicDatUpdateTemplatesDetails,
        individual: Individual,
    ) -> None:
        populate_pdu_with_null_values(program, individual.flex_fields)
        individual.save()
        pageIndividuals.selectGlobalProgramFilter(program.name)
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()

        pagePeriodicDataUpdateTemplates.getNewTemplateButton().click()
        pagePeriodicDataUpdateTemplatesDetails.getFiltersRegistrationDataImport().click()

        pagePeriodicDataUpdateTemplatesDetails.select_listbox_element(individual.registration_data_import.name)
        pagePeriodicDataUpdateTemplatesDetails.getSubmitButton().click()
        pagePeriodicDataUpdateTemplatesDetails.getCheckbox(string_attribute.name).click()
        pagePeriodicDataUpdateTemplatesDetails.getSubmitButton().click()
        pagePeriodicDataUpdateTemplates.getNewTemplateButton()  # wait for the page to load
        assert PeriodicDataUpdateTemplate.objects.count() == 1
        periodic_data_update_template = PeriodicDataUpdateTemplate.objects.first()
        assert (
            str(periodic_data_update_template.id)
            in pagePeriodicDataUpdateTemplates.getTemplateId(periodic_data_update_template.id).text
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
            pageIndividuals.check_file_exists(
                os.path.join(settings.DOWNLOAD_DIRECTORY, periodic_data_update_template.file.file.name)
            )
            is True
        )
