from typing import TYPE_CHECKING, Any

from constance.test import override_config
from django.conf import settings
import pytest
from strategy_field.utils import fqn

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CountryFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import IDENTIFICATION_TYPE_NATIONAL_ID
from hope.apps.sanction_list.strategies.un import UNSanctionList
from hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    check_against_sanction_list_pre_merge,
)
from hope.apps.sanction_list.tasks.load_xml import LoadSanctionListXMLTask
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.models import Individual

if TYPE_CHECKING:
    from hope.models import SanctionList


pytestmark = [
    pytest.mark.usefixtures("django_elasticsearch_setup"),
    pytest.mark.elasticsearch,
]


@pytest.fixture
def sanction_list(db: Any) -> "SanctionList":
    from extras.test_utils.factories import SanctionListFactory

    sanction_list = SanctionListFactory(strategy=fqn(UNSanctionList))
    full_path = f"{settings.TESTS_ROOT}/apps/sanction_list/test_files/full_sanction_list.xml"

    task = LoadSanctionListXMLTask(sanction_list)
    task.load_from_file(full_path)

    return sanction_list


@pytest.fixture
def business_area():
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        slug="afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        has_data_sharing_agreement=True,
    )


@pytest.fixture
def country():
    return CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )


@pytest.fixture
def program(business_area, sanction_list):
    program = ProgramFactory(business_area=business_area)
    program.sanction_lists.add(sanction_list)
    return program


@pytest.fixture
def registration_data_import(business_area, program):
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
    )


@pytest.fixture
def household_with_individuals(program, registration_data_import, business_area):
    household = HouseholdFactory(
        program=program,
        registration_data_import=registration_data_import,
        business_area=business_area,
        without_hoh=True,
    )
    individuals_data = [
        ("Alias", "Alias Name2", "", "Name2", "1922-04-11"),  # DUPLICATE
        ("Choo", "Choo Ryoong", "", "Ryong", "1960-04-04"),
        ("Tescik", "Tescik Testowski", "", "Testowski", "1996-12-12"),
        ("Tessta", "Tessta Testowski", "", "Testowski", "1997-07-07"),  # DUPLICATE
        ("Test", "Test Testowski", "", "Testowski", "1955-09-04"),  # DUPLICATE
        ("Test", "Test Example", "", "Example", "1997-08-08"),
        ("Tessta", "Tessta Testowski", "", "Testowski", "1997-07-07"),  # DUPLICATE
        ("Abdul", "Abdul Afghanistan", "", "Afghanistan", "1997-07-07"),
    ]
    for given, full, middle, family, birth in individuals_data:
        IndividualFactory(
            household=household,
            program=program,
            given_name=given,
            full_name=full,
            middle_name=middle,
            family_name=family,
            birth_date=birth,
            business_area=business_area,
        )
    return household


@pytest.fixture
def national_id_document(program, country):
    ind = Individual.objects.get(full_name="Abdul Afghanistan")
    doc_type = DocumentTypeFactory(
        label="National ID",
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
    )
    DocumentFactory(
        document_number="55130",
        individual=ind,
        type=doc_type,
        country=country,
        program=program,
    )


@pytest.fixture
def prepare_search_index(
    sanction_list,
    household_with_individuals,
    national_id_document,
):
    rebuild_search_index()


@override_config(SANCTION_LIST_MATCH_SCORE=3.5)
def test_execute(program, prepare_search_index):
    check_against_sanction_list_pre_merge(program_id=program.id)

    expected = [
        {"full_name": "Abdul Afghanistan", "sanction_list_possible_match": False},
        {"full_name": "Alias Name2", "sanction_list_possible_match": True},
        {"full_name": "Choo Ryoong", "sanction_list_possible_match": False},
        {"full_name": "Tescik Testowski", "sanction_list_possible_match": False},
        {"full_name": "Tessta Testowski", "sanction_list_possible_match": False},
        {"full_name": "Tessta Testowski", "sanction_list_possible_match": False},
        {"full_name": "Test Example", "sanction_list_possible_match": False},
        {"full_name": "Test Testowski", "sanction_list_possible_match": False},
    ]

    result = list(Individual.objects.order_by("full_name").values("full_name", "sanction_list_possible_match"))
    assert result == expected


@override_config(SANCTION_LIST_MATCH_SCORE=3.5)
def test_create_system_flag_tickets(program, household_with_individuals, prepare_search_index):
    check_against_sanction_list_pre_merge(program_id=program.id)

    tickets = GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING)

    assert tickets.count() == 1

    ticket = tickets.first()
    assert ticket.programs.count() == 1
    assert ticket.programs.first() == program

    household_with_individuals.refresh_from_db()
    assert ticket.household_unicef_id == household_with_individuals.unicef_id
