from datetime import date, datetime
from typing import NamedTuple

from dateutil.relativedelta import relativedelta
import pytest

from extras.test_utils.factories.core import BeneficiaryGroupFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.models import (
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    Household,
    Individual,
    Program,
)


@pytest.fixture
def social_worker_program(business_area: BusinessArea) -> Program:
    beneficiary_group, _ = BeneficiaryGroup.objects.get_or_create(name="People")
    return ProgramFactory(
        name="Social Program",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=DataCollectingType.objects.filter(type=DataCollectingType.Type.SOCIAL).first(),
        beneficiary_group=beneficiary_group,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )


@pytest.fixture
def household_update_program(business_area: BusinessArea) -> Program:
    beneficiary_group = BeneficiaryGroupFactory(
        name="Household Group",
        group_label="Household",
        group_label_plural="Households",
        member_label="Individual",
        member_label_plural="Individuals",
        master_detail=True,
    )
    return ProgramFactory(
        name="HH Update Program",
        status=Program.ACTIVE,
        business_area=business_area,
        beneficiary_group=beneficiary_group,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )


@pytest.fixture
def household_for_update(business_area: BusinessArea, household_update_program: Program) -> Household:
    return HouseholdFactory(business_area=business_area, program=household_update_program)


# --- Needs Adjudication Management -------------------------------------------------
#
# The NA Tickets Management screen compares one golden record ("Person 1") against a
# possible duplicate ("Person 2") and lets the operator withdraw one of them. Any HEAD
# or PRIMARY role the withdrawn individual holds in a surviving household has to be
# handed over first (frontend `getRequiredReassignments`, backend
# `reassign_roles_on_marking_as_duplicate_individual_service`).
#
# In every scenario below Person 1 is deliberately role-free, so only Person 2 drives
# the reassignment section and the tests can always click "Withdraw" on Person 2.


class NaScenario(NamedTuple):
    """One Needs Adjudication ticket plus the objects its test asserts on."""

    ticket_details: TicketNeedsAdjudicationDetails
    person1: Individual
    person2: Individual
    household: Household  # Person 2's household
    replacement: Individual  # who Person 2's role is meant to be handed over to

    @property
    def ticket(self) -> GrievanceTicket:
        return self.ticket_details.ticket


def _household(program: Program, village: str) -> Household:
    """Household with a single auto-generated member, which is also its head.

    ``create_role=False`` stops the factory from silently granting PRIMARY to that head
    — every scenario assigns collector roles explicitly, and a stray PRIMARY would add
    an unintended reassignment row.
    """
    return HouseholdFactory(
        program=program,
        business_area=program.business_area,
        village=village,
        create_role=False,
    )


def _member(
    household: Household,
    full_name: str,
    given_name: str,
    family_name: str,
    sex: str,
    birth_date: date,
) -> Individual:
    return IndividualFactory(
        household=household,
        program=household.program,
        business_area=household.business_area,
        registration_data_import=household.registration_data_import,
        full_name=full_name,
        given_name=given_name,
        family_name=family_name,
        sex=sex,
        birth_date=birth_date,
    )


def _rename(
    individual: Individual,
    full_name: str,
    given_name: str,
    family_name: str,
    sex: str,
    birth_date: date,
) -> Individual:
    """Give the member ``HouseholdFactory`` generates on its own a recognisable identity.

    Reusing it rather than adding another individual keeps ``active_individuals_count``
    equal to the number of people the scenario actually describes — that count is what
    decides whether a reassignment is required at all.
    """
    individual.full_name = full_name
    individual.given_name = given_name
    individual.family_name = family_name
    individual.sex = sex
    individual.birth_date = birth_date
    individual.save()
    return individual


def _golden_record(program: Program) -> Individual:
    """Person 1: a plain member of a household headed by somebody else, so role-free."""
    household = _household(program, village="Kandahar")
    _rename(
        household.head_of_household,
        full_name="Nadia Rahimi",
        given_name="Nadia",
        family_name="Rahimi",
        sex="FEMALE",
        birth_date=date(1991, 4, 2),
    )
    return _member(
        household,
        full_name="Zahra Karimi",
        given_name="Zahra",
        family_name="Karimi",
        sex="FEMALE",
        birth_date=date(1984, 7, 21),
    )


def _na_ticket(
    program: Program,
    golden: Individual,
    duplicate: Individual,
    score: float = 8.5,
) -> TicketNeedsAdjudicationDetails:
    """Wire two individuals into a Needs Adjudication ticket the management screen can render.

    ``possible_duplicate`` (the legacy FK) is set as well as the M2M because the
    comparison panel resolves Person 2 from ``possibleDuplicates`` first and falls back
    to ``possibleDuplicate``; ``extra_data`` is what makes the "Similarity score" row
    render a number. ``unicef_id`` is assigned by a DB trigger, so it is never passed in.
    """
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        status=GrievanceTicket.STATUS_NEW,
        business_area=program.business_area,
        consent=True,
        household_unicef_id=golden.household.unicef_id,
    )
    grievance.programs.set([program])
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=golden,
        is_multiple_duplicates_version=True,
        possible_duplicate=duplicate,
        selected_individual=None,
        role_reassign_data={},
        extra_data={
            "golden_records": [_dedup_hit(duplicate, score)],
            "possible_duplicate": [_dedup_hit(golden, score)],
        },
        score_min=score,
        score_max=score,
    )
    ticket_details.possible_duplicates.set([duplicate])
    return ticket_details


def _dedup_hit(individual: Individual, score: float) -> dict:
    return {
        "dob": individual.birth_date.isoformat(),
        "score": score,
        "hit_id": str(individual.pk),
        "location": individual.household.village,
        "full_name": individual.full_name,
        "proximity_to_score": 3.0,
        "duplicate": True,
        "distinct": False,
    }


@pytest.fixture
def na_program(business_area: BusinessArea) -> Program:
    beneficiary_group = BeneficiaryGroupFactory(
        name="NA Household Group",
        group_label="Household",
        group_label_plural="Households",
        member_label="Individual",
        member_label_plural="Individuals",
        master_detail=True,
    )
    return ProgramFactory(
        name="NA Program",
        status=Program.ACTIVE,
        business_area=business_area,
        beneficiary_group=beneficiary_group,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )


@pytest.fixture
def na_ticket_plain(na_program: Program) -> NaScenario:
    """Neither individual holds a blocking role, so withdrawing needs no reassignment.

    The two differ in every always-visible comparison field plus the address, so the
    panel's "differs" rows are exercised too.
    """
    golden = _golden_record(na_program)
    household = _household(na_program, village="Herat")
    head = _rename(
        household.head_of_household,
        full_name="Bilal Sarwar",
        given_name="Bilal",
        family_name="Sarwar",
        sex="MALE",
        birth_date=date(1986, 9, 17),
    )
    duplicate = _member(
        household,
        full_name="Farid Ahmadzai",
        given_name="Farid",
        family_name="Ahmadzai",
        sex="MALE",
        birth_date=date(1980, 3, 4),
    )
    return NaScenario(_na_ticket(na_program, golden, duplicate), golden, duplicate, household, head)


@pytest.fixture
def na_ticket_head(na_program: Program) -> NaScenario:
    """Person 2 heads a household that keeps another active member — HEAD must be handed over.

    The replacement has to come from the same household, so it is that other member.
    """
    golden = _golden_record(na_program)
    household = _household(na_program, village="Mazar")
    replacement = _rename(
        household.head_of_household,
        full_name="Nadia Sarwar",
        given_name="Nadia",
        family_name="Sarwar",
        sex="FEMALE",
        birth_date=date(1988, 2, 6),
    )
    duplicate = _member(
        household,
        full_name="Jamil Noorzai",
        given_name="Jamil",
        family_name="Noorzai",
        sex="MALE",
        birth_date=date(1977, 12, 9),
    )
    household.head_of_household = duplicate
    household.save()
    return NaScenario(_na_ticket(na_program, golden, duplicate), golden, duplicate, household, replacement)


@pytest.fixture
def na_ticket_primary(na_program: Program) -> NaScenario:
    """Person 2 is the primary collector of a surviving household — PRIMARY must be handed over.

    Person 2 is not the head, so HEAD is not expected among the required reassignments.
    """
    golden = _golden_record(na_program)
    household = _household(na_program, village="Kabul")
    _rename(
        household.head_of_household,
        full_name="Rashid Wardak",
        given_name="Rashid",
        family_name="Wardak",
        sex="MALE",
        birth_date=date(1975, 6, 30),
    )
    duplicate = _member(
        household,
        full_name="Idris Safi",
        given_name="Idris",
        family_name="Safi",
        sex="MALE",
        birth_date=date(1978, 4, 14),
    )
    IndividualRoleInHouseholdFactory(household=household, individual=duplicate, role=ROLE_PRIMARY)
    replacement = _member(
        household,
        full_name="Shirin Ayubi",
        given_name="Shirin",
        family_name="Ayubi",
        sex="FEMALE",
        birth_date=date(1993, 3, 8),
    )
    return NaScenario(_na_ticket(na_program, golden, duplicate), golden, duplicate, household, replacement)


@pytest.fixture
def na_ticket_alternate(na_program: Program) -> NaScenario:
    """Person 2 only holds ALTERNATE — never blocking, since head and PRIMARY sit elsewhere."""
    golden = _golden_record(na_program)
    household = _household(na_program, village="Jalalabad")
    head = _rename(
        household.head_of_household,
        full_name="Marwa Hakimi",
        given_name="Marwa",
        family_name="Hakimi",
        sex="FEMALE",
        birth_date=date(1992, 8, 23),
    )
    IndividualRoleInHouseholdFactory(household=household, individual=head, role=ROLE_PRIMARY)
    duplicate = _member(
        household,
        full_name="Yusuf Barakzai",
        given_name="Yusuf",
        family_name="Barakzai",
        sex="MALE",
        birth_date=date(1989, 2, 11),
    )
    IndividualRoleInHouseholdFactory(household=household, individual=duplicate, role=ROLE_ALTERNATE)
    return NaScenario(_na_ticket(na_program, golden, duplicate), golden, duplicate, household, head)


@pytest.fixture
def individual_in_other_program(business_area: BusinessArea) -> Individual:
    other_program = ProgramFactory(
        name="Other NA Program",
        status=Program.ACTIVE,
        business_area=business_area,
        beneficiary_group=BeneficiaryGroupFactory(
            name="Other NA Household Group",
            group_label="Household",
            group_label_plural="Households",
            member_label="Individual",
            member_label_plural="Individuals",
            master_detail=True,
        ),
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )
    household = _household(other_program, village="Jalalabad")
    return _rename(
        household.head_of_household,
        full_name="Nadia Sarwar",
        given_name="Nadia",
        family_name="Sarwar",
        sex="FEMALE",
        birth_date=date(1988, 2, 6),
    )
