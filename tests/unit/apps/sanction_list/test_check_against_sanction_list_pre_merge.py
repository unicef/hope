from datetime import date
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
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.grievance.models import GrievanceTicket, TicketSystemFlaggingDetails
from hope.apps.household.const import HEAD, IDENTIFICATION_TYPE_NATIONAL_ID
from hope.apps.household.services.index_management import rebuild_program_indexes
from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask
from hope.apps.sanction_list.strategies.un import UNSanctionList
from hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    check_against_sanction_list_pre_merge,
)
from hope.apps.sanction_list.tasks.load_xml import LoadSanctionListXMLTask
from hope.models import Individual, RegistrationDataImport

if TYPE_CHECKING:
    from hope.models import SanctionList


pytestmark = [
    pytest.mark.usefixtures("django_elasticsearch_setup"),
    pytest.mark.elasticsearch,
    pytest.mark.xdist_group(name="elasticsearch"),
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
    )
    # update Head_of_household data >> # DUPLICATE Ind
    ind_1 = household.head_of_household
    ind_1.given_name = "Alias"
    ind_1.family_name = "Name2"
    ind_1.full_name = "Alias Name2"
    ind_1.middle_name = ""
    ind_1.birth_date = "1922-04-11"
    ind_1.save()
    individuals_data = [
        # other Individuals
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


@override_config(SANCTION_LIST_MATCH_SCORE=3.5)
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_execute(program, sanction_list, household_with_individuals, national_id_document):
    rebuild_program_indexes(str(program.id))
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
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_create_system_flag_tickets(program, household_with_individuals, sanction_list, national_id_document):
    rebuild_program_indexes(str(program.id))
    check_against_sanction_list_pre_merge(program_id=program.id)

    tickets = GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING)

    assert tickets.count() == 1

    ticket = tickets.first()
    assert ticket.programs.count() == 1
    assert ticket.programs.first() == program

    household_with_individuals.refresh_from_db()
    assert ticket.household_unicef_id == household_with_individuals.unicef_id


@override_config(SANCTION_LIST_MATCH_SCORE=3.5)
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_create_system_flag_tickets_during_cw_auto_merge(
    business_area, program, sanction_list, django_capture_on_commit_callbacks
):
    dct = program.data_collecting_type
    dct.recalculate_composition = True
    dct.save(update_fields=["recalculate_composition"])

    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        status=RegistrationDataImport.IN_REVIEW,
        screen_beneficiary=True,
        country_workspace_id="test-correlation-id",
    )
    pending_head = PendingIndividualFactory(
        full_name="Alias Name2",
        given_name="Alias",
        family_name="Name2",
        middle_name="",
        birth_date=date(1922, 4, 11),
        relationship=HEAD,
        sex="MALE",
        registration_data_import=rdi,
        business_area=business_area,
        program=program,
        household=None,
    )
    household = PendingHouseholdFactory(
        registration_data_import=rdi,
        business_area=business_area,
        program=program,
        head_of_household=pending_head,
        create_role=False,
    )
    pending_head.household = household
    pending_head.save(update_fields=["household"])

    rebuild_program_indexes(str(program.id))

    with django_capture_on_commit_callbacks(execute=True):
        RdiMergeTask().execute(rdi.pk)

    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.MERGED
    assert rdi.country_workspace_id == "test-correlation-id"

    tickets = GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING)
    assert tickets.count() == 1
    ticket = tickets.first()
    assert ticket.registration_data_import == rdi
    assert ticket.programs.count() == 1
    assert ticket.programs.first() == program

    merged_individual = Individual.objects.get(full_name="Alias Name2")
    assert merged_individual.sanction_list_possible_match is True
    assert TicketSystemFlaggingDetails.objects.filter(
        ticket=ticket,
        golden_records_individual=merged_individual,
    ).exists()
