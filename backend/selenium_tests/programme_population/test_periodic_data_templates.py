import pytest

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.periodic_data_update.models import PeriodicDataUpdateTemplate
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from selenium_tests.page_object.programme_population.individuals import Individuals

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def program() -> Program:
    business_area = create_afghanistan()
    return ProgramFactory(name="Test Program", status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def individual(program: Program) -> Individual:
    business_area = create_afghanistan()
    rdi = RegistrationDataImportFactory()
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
def string_attribute() -> FlexibleAttribute:
    return create_flexible_attribute(
        name="Test String Attribute",
        subtype=FlexibleAttribute.STRING,
        number_of_rounds=1,
        rounds_names=["Test Round"],
    )


@pytest.fixture
def date_attribute() -> FlexibleAttribute:
    return create_flexible_attribute(
        name="Test String Attribute",
        subtype=FlexibleAttribute.DATE,
        number_of_rounds=1,
        rounds_names=["Test Round"],
    )


def create_flexible_attribute(
    name: str, subtype: str, number_of_rounds: int, rounds_names: list[str]
) -> FlexibleAttribute:
    flexible_attribute = FlexibleAttribute.objects.create(
        name=name, type=FlexibleAttribute.PDU, associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
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
        individual: Individual,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
    ) -> None:
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
        pageIndividuals.selectGlobalProgramFilter(program.name).click()
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()
        status = pageIndividuals.getTemplateStatus(periodic_data_update_template.pk).text
        assert status == "NOT SCHEDULED"
        pageIndividuals.getExportBtn(periodic_data_update_template.pk).click()
        pageIndividuals.screenshot("test_periodic_data_template_export")
        status = pageIndividuals.getTemplateStatus(periodic_data_update_template.pk).text
        assert status == "EXPORTED"
        pageIndividuals.getDownloadBtn(periodic_data_update_template.pk).click()
        periodic_data_update_template.refresh_from_db()
        assert (
            pageIndividuals.check_file_exists(f"./report/downloads/{periodic_data_update_template.file.file.name}")
            is True
        )
