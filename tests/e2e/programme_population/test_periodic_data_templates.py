import os
from time import sleep

import pytest
from e2e.page_object.programme_population.individuals import Individuals
from e2e.page_object.programme_population.periodic_data_update_templates import (
    PeriodicDatUpdateTemplates,
    PeriodicDatUpdateTemplatesDetails,
)
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.periodic_data_update import (
    PeriodicDataUpdateTemplateFactory,
)
from extras.test_utils.factories.program import BeneficiaryGroupFactory, ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from selenium.webdriver.common.by import By

from hope.models.core import FlexibleAttribute, PeriodicFieldData
from hope.models.household import Individual
from hope.models.periodic_data_update import PeriodicDataUpdateTemplate
from hope.apps.periodic_data_update.utils import (
    field_label_to_field_name,
    populate_pdu_with_null_values,
)
from hope.models.program import Program
from hope.models.registration_data import RegistrationDataImport

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
        page_individuals: Individuals,
        individual: Individual,
        download_path: str,
    ) -> None:
        populate_pdu_with_null_values(program, individual.flex_fields)
        individual.save()
        periodic_data_update_template = PeriodicDataUpdateTemplate.objects.create(
            program=program,
            business_area=program.business_area,
            status=PeriodicDataUpdateTemplate.Status.TO_EXPORT,
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
        page_individuals.select_global_program_filter(program.name)
        page_individuals.get_nav_programme_population().click()
        page_individuals.get_nav_individuals().click()
        page_individuals.get_tab_periodic_data_updates().click()
        status = page_individuals.get_template_status(periodic_data_update_template.pk).text
        assert status == "NOT SCHEDULED"
        page_individuals.get_export_btn(periodic_data_update_template.pk).click()
        for _ in range(10):
            status = page_individuals.get_template_status(periodic_data_update_template.pk).text
            if status == "EXPORTED":
                break
            sleep(1)
        else:
            assert status == "EXPORTED"
        page_individuals.get_download_btn(periodic_data_update_template.pk).click()
        periodic_data_update_template.refresh_from_db()
        assert (
            page_individuals.check_file_exists(
                os.path.join(download_path, periodic_data_update_template.file.file.name)
            )
            is True
        )

    @pytest.mark.night
    def test_periodic_data_template_list(
        self,
        program: Program,
        string_attribute: FlexibleAttribute,
        page_individuals: Individuals,
        page_periodic_data_update_templates: PeriodicDatUpdateTemplates,
    ) -> None:
        periodic_data_update_template = PeriodicDataUpdateTemplateFactory(
            program=program,
            business_area=program.business_area,
            status=PeriodicDataUpdateTemplate.Status.EXPORTED,
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

        page_individuals.select_global_program_filter(program.name)
        page_individuals.get_nav_programme_population().click()
        page_individuals.get_nav_individuals().click()
        page_individuals.get_tab_periodic_data_updates().click()

        page_periodic_data_update_templates.get_pdu_templates_btn().click()
        assert str(index) in page_periodic_data_update_templates.get_template_id(index).text
        assert (
            str(periodic_data_update_template.number_of_records)
            in page_periodic_data_update_templates.get_template_records(index).text
        )
        assert (
            f"{periodic_data_update_template.created_at:%-d %b %Y}"
            in page_periodic_data_update_templates.get_template_created_at(index).text
        )
        assert (
            periodic_data_update_template.created_by.get_full_name()
            in page_periodic_data_update_templates.get_template_created_by(index).text
        )

        assert "EXPORTED" in page_periodic_data_update_templates.get_template_status(index).text

    @pytest.mark.night
    def test_periodic_data_template_details(
        self,
        program: Program,
        string_attribute: FlexibleAttribute,
        page_individuals: Individuals,
        page_periodic_data_update_templates: PeriodicDatUpdateTemplates,
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
            filters={},
            rounds_data=rounds_data,
        )
        periodic_data_update_template.refresh_from_db()
        index = periodic_data_update_template.id

        page_individuals.select_global_program_filter(program.name)
        page_individuals.get_nav_programme_population().click()
        page_individuals.get_nav_individuals().click()
        page_individuals.get_tab_periodic_data_updates().click()

        page_periodic_data_update_templates.get_pdu_templates_btn().click()

        btn = page_periodic_data_update_templates.get_template_details_btn(index)
        btn.find_element(By.TAG_NAME, "button").click()
        page_periodic_data_update_templates.get_detail_modal()

        assert string_attribute.label["English(EN)"] in page_periodic_data_update_templates.get_template_field(0).text
        assert str(rounds_data[0]["round"]) in page_periodic_data_update_templates.get_template_round_number(0).text
        assert rounds_data[0]["round_name"] in page_periodic_data_update_templates.get_template_round_name(0).text
        assert (
            str(rounds_data[0]["number_of_records"])
            in page_periodic_data_update_templates.get_template_number_of_individuals(0).text
        )

    @pytest.mark.night
    def test_periodic_data_template_create_and_download(
        self,
        program: Program,
        string_attribute: FlexibleAttribute,
        page_individuals: Individuals,
        page_periodic_data_update_templates: PeriodicDatUpdateTemplates,
        page_periodic_data_update_templates_details: PeriodicDatUpdateTemplatesDetails,
        individual: Individual,
        download_path: str,
        clear_downloaded_files: None,
    ) -> None:
        populate_pdu_with_null_values(program, individual.flex_fields)
        individual.save()
        page_individuals.select_global_program_filter(program.name)
        page_individuals.get_nav_programme_population().click()
        page_individuals.get_nav_individuals().click()
        page_individuals.get_tab_periodic_data_updates().click()

        page_periodic_data_update_templates.get_new_template_button().click()
        page_periodic_data_update_templates_details.get_filters_registration_data_import().click()

        page_periodic_data_update_templates_details.select_listbox_element(individual.registration_data_import.name)
        page_periodic_data_update_templates_details.get_submit_button().click()
        page_periodic_data_update_templates_details.get_checkbox(string_attribute.name).click()
        page_periodic_data_update_templates_details.get_submit_button().click()
        page_periodic_data_update_templates.get_new_template_button()  # wait for the page to load
        assert PeriodicDataUpdateTemplate.objects.count() == 1
        periodic_data_update_template = PeriodicDataUpdateTemplate.objects.first()
        assert (
            str(periodic_data_update_template.id)
            in page_periodic_data_update_templates.get_template_id(periodic_data_update_template.id).text
        )

        for _ in range(10):
            status = page_individuals.get_template_status(periodic_data_update_template.pk).text
            if status == "EXPORTED":
                break
            sleep(1)
        else:
            assert status == "EXPORTED"

        page_individuals.get_download_btn(periodic_data_update_template.pk).click()
        periodic_data_update_template.refresh_from_db()
        assert (
            page_individuals.check_file_exists(
                os.path.join(download_path, periodic_data_update_template.file.file.name)
            )
            is True
        )
