"""Closing a Needs Adjudication ticket must refresh the household counters and the programme size."""

from datetime import date

from dateutil.relativedelta import relativedelta
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.grievance import TicketNeedsAdjudicationDetailsFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.celery_tasks import async_job_task
from hope.apps.grievance.services.needs_adjudication_ticket_services import close_needs_adjudication_new_ticket
from hope.apps.household.const import HEAD, ROLE_PRIMARY
from hope.apps.household.services.household_recalculate_data import recalculate_data
from hope.models import AsyncJob

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def program():
    return ProgramFactory(data_collecting_type=DataCollectingTypeFactory(recalculate_composition=True))


@pytest.fixture
def other_individual(program):
    return HouseholdFactory(program=program, business_area=program.business_area).head_of_household


@pytest.fixture
def household(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        registration_data_import=household.registration_data_import,
    )
    recalculate_data(household)
    household.refresh_from_db()
    return household


@pytest.fixture
def household_with_duplicate_member(program):
    household = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        duplicate=True,
        registration_data_import=household.registration_data_import,
    )
    recalculate_data(household)
    household.refresh_from_db()
    return household


@pytest.fixture
def child_headed_household(program):
    child_head = IndividualFactory(
        household=None,
        program=program,
        business_area=program.business_area,
        birth_date=date.today() - relativedelta(years=10),
    )
    household = HouseholdFactory(
        program=program,
        business_area=program.business_area,
        head_of_household=child_head,
        registration_data_import=child_head.registration_data_import,
    )
    IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        birth_date=date.today() - relativedelta(years=40),
        registration_data_import=household.registration_data_import,
    )
    recalculate_data(household)
    household.refresh_from_db()
    return household


@pytest.fixture
def ticket_marking_member_duplicate(household, other_individual, program):
    member = household.individuals.exclude(pk=household.head_of_household_id).get()
    ticket_details = TicketNeedsAdjudicationDetailsFactory(golden_records_individual=member)
    ticket_details.ticket.programs.add(program)
    ticket_details.possible_duplicates.add(other_individual)
    ticket_details.selected_individuals.add(member)
    ticket_details.selected_distinct.add(other_individual)
    return ticket_details


@pytest.fixture
def ticket_marking_member_distinct(household_with_duplicate_member, other_individual, program):
    member = household_with_duplicate_member.individuals.exclude(
        pk=household_with_duplicate_member.head_of_household_id
    ).get()
    ticket_details = TicketNeedsAdjudicationDetailsFactory(golden_records_individual=member)
    ticket_details.ticket.programs.add(program)
    ticket_details.possible_duplicates.add(other_individual)
    ticket_details.selected_distinct.add(member, other_individual)
    return ticket_details


@pytest.fixture
def ticket_marking_child_head_duplicate(child_headed_household, other_individual, program):
    child_head = child_headed_household.head_of_household
    adult = child_headed_household.individuals.exclude(pk=child_head.pk).get()
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        golden_records_individual=child_head,
        role_reassign_data={
            HEAD: {
                "role": HEAD,
                "household": str(child_headed_household.id),
                "individual": str(child_head.id),
                "new_individual": str(adult.id),
            },
            ROLE_PRIMARY: {
                "role": ROLE_PRIMARY,
                "household": str(child_headed_household.id),
                "individual": str(child_head.id),
                "new_individual": str(adult.id),
            },
        },
    )
    ticket_details.ticket.programs.add(program)
    ticket_details.possible_duplicates.add(other_individual)
    ticket_details.selected_individuals.add(child_head)
    ticket_details.selected_distinct.add(other_individual)
    return ticket_details


def test_close_recalculates_size_of_household_with_duplicate(household, ticket_marking_member_duplicate):
    assert household.size == 2

    close_needs_adjudication_new_ticket(ticket_marking_member_duplicate, UserFactory())

    household.refresh_from_db()
    assert household.size == 1


def test_close_recalculates_size_of_household_with_distinct(
    household_with_duplicate_member, ticket_marking_member_distinct
):
    assert household_with_duplicate_member.size == 1

    close_needs_adjudication_new_ticket(ticket_marking_member_distinct, UserFactory())

    household_with_duplicate_member.refresh_from_db()
    assert household_with_duplicate_member.size == 2


def test_close_derives_child_headed_flag_from_reassigned_head(
    child_headed_household, ticket_marking_child_head_duplicate
):
    assert child_headed_household.child_hoh is True

    close_needs_adjudication_new_ticket(ticket_marking_child_head_duplicate, UserFactory())

    child_headed_household.refresh_from_db()
    assert child_headed_household.child_hoh is False


def test_close_with_distinct_recounts_program_size(
    program, ticket_marking_member_distinct, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        close_needs_adjudication_new_ticket(ticket_marking_member_distinct, UserFactory())
    job = AsyncJob.objects.filter(job_name="adjust_program_size_async_task").latest("pk")

    async_job_task.run(job._meta.label_lower, job.pk, job.version)

    program.refresh_from_db()
    assert program.individual_count == 3
