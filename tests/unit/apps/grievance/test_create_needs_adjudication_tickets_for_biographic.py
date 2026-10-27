from datetime import date
from decimal import Decimal

import pytest

from extras.test_utils.factories import (
    BiographicDeduplicationEngineSimilarityPairFactory,
    GrievanceTicketFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets_for_biographic,
)
from hope.models import (
    BiographicDedupeSimilarityPair,
    Individual,
    Program,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def program() -> Program:
    return ProgramFactory()


@pytest.fixture
def rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(program=program, business_area=program.business_area)


@pytest.fixture
def rdi_individual(program: Program, rdi: RegistrationDataImport) -> Individual:
    return IndividualFactory(
        id="22222222-2222-2222-2222-222222222222",
        program=program,
        business_area=program.business_area,
        registration_data_import=rdi,
        full_name="Rdi Person",
    )


@pytest.fixture
def population_individual(program: Program) -> Individual:
    # Lower id than rdi_individual, so pairs store it as individual1.
    return IndividualFactory(
        id="11111111-1111-1111-1111-111111111111",
        program=program,
        business_area=program.business_area,
        full_name="Population One",
        birth_date=date(1985, 5, 5),
    )


@pytest.fixture
def population_individual_2(program: Program) -> Individual:
    return IndividualFactory(
        id="33333333-3333-3333-3333-333333333333",
        program=program,
        business_area=program.business_area,
        full_name="Population Two",
        birth_date=date(1970, 7, 7),
    )


@pytest.fixture
def population_pairs(
    program: Program,
    rdi_individual: Individual,
    population_individual: Individual,
    population_individual_2: Individual,
) -> list[BiographicDedupeSimilarityPair]:
    return [
        BiographicDeduplicationEngineSimilarityPairFactory(
            program=program,
            individual1=population_individual,
            individual2=rdi_individual,
            similarity_score=Decimal("12.50"),
            proximity_to_score=Decimal("2.50"),
        ),
        BiographicDeduplicationEngineSimilarityPairFactory(
            program=program,
            individual1=rdi_individual,
            individual2=population_individual_2,
            similarity_score=Decimal("20.00"),
            proximity_to_score=Decimal("10.00"),
        ),
    ]


@pytest.fixture
def rdi_individual_lower_id(program: Program, rdi: RegistrationDataImport) -> Individual:
    return IndividualFactory(
        id="00000000-0000-0000-0000-000000000001",
        program=program,
        business_area=program.business_area,
        registration_data_import=rdi,
    )


@pytest.fixture
def intra_batch_pair(
    program: Program, rdi_individual: Individual, rdi_individual_lower_id: Individual
) -> BiographicDedupeSimilarityPair:
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=rdi_individual,
        individual2=rdi_individual_lower_id,
    )


@pytest.fixture
def population_pair(
    program: Program, rdi_individual: Individual, population_individual: Individual
) -> BiographicDedupeSimilarityPair:
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=rdi_individual,
        individual2=population_individual,
    )


@pytest.fixture
def population_pair_of_rdi_individual_lower_id(
    program: Program, rdi_individual_lower_id: Individual, population_individual_2: Individual
) -> BiographicDedupeSimilarityPair:
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=rdi_individual_lower_id,
        individual2=population_individual_2,
    )


@pytest.fixture
def pair_with_missing_individual(program: Program, rdi_individual: Individual) -> BiographicDedupeSimilarityPair:
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=rdi_individual,
        individual2=None,
    )


@pytest.fixture
def open_biographical_ticket_for_population_pair(
    program: Program, rdi_individual: Individual, population_individual: Individual
) -> GrievanceTicket:
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=GrievanceTicketFactory(
            business_area=program.business_area,
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        ),
        golden_records_individual=rdi_individual,
    )
    ticket_details.possible_duplicates.add(population_individual)
    return ticket_details.ticket


def test_create_needs_adjudication_tickets_for_biographic_groups_population_duplicates_of_rdi_individual(
    rdi: RegistrationDataImport,
    rdi_individual: Individual,
    population_individual: Individual,
    population_individual_2: Individual,
    population_pairs: list[BiographicDedupeSimilarityPair],
) -> None:
    create_needs_adjudication_tickets_for_biographic(BiographicDedupeSimilarityPair.objects.all(), rdi)

    ticket = GrievanceTicket.objects.get()
    assert ticket.ticket_details.golden_records_individual == rdi_individual
    assert set(ticket.ticket_details.possible_duplicates.all()) == {population_individual, population_individual_2}


def test_create_needs_adjudication_tickets_for_biographic_creates_biographical_similarity_ticket_for_rdi(
    program: Program,
    rdi: RegistrationDataImport,
    population_pairs: list[BiographicDedupeSimilarityPair],
) -> None:
    create_needs_adjudication_tickets_for_biographic(BiographicDedupeSimilarityPair.objects.all(), rdi)

    ticket = GrievanceTicket.objects.get()
    assert ticket.category == GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION
    assert ticket.issue_type == GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY
    assert ticket.registration_data_import == rdi
    assert ticket.business_area == program.business_area
    assert list(ticket.programs.all()) == [program]


def test_create_needs_adjudication_tickets_for_biographic_stores_golden_records_and_score_range_from_pairs(
    rdi: RegistrationDataImport,
    population_pairs: list[BiographicDedupeSimilarityPair],
) -> None:
    create_needs_adjudication_tickets_for_biographic(BiographicDedupeSimilarityPair.objects.all(), rdi)

    ticket_details = GrievanceTicket.objects.get().ticket_details
    assert ticket_details.extra_data == {
        "golden_records": [
            {
                "hit_id": "11111111-1111-1111-1111-111111111111",
                "full_name": "Population One",
                "score": 12.5,
                "location": None,
                "dob": "1985-05-05",
                "proximity_to_score": 2.5,
            },
            {
                "hit_id": "33333333-3333-3333-3333-333333333333",
                "full_name": "Population Two",
                "score": 20.0,
                "location": None,
                "dob": "1970-07-07",
                "proximity_to_score": 10.0,
            },
        ],
        "possible_duplicate": None,
    }
    assert (ticket_details.score_min, ticket_details.score_max) == (12.5, 20.0)
    assert ticket_details.possible_duplicate is None
    assert ticket_details.is_multiple_duplicates_version is True


def test_create_needs_adjudication_tickets_for_biographic_intra_batch_pair_makes_lower_id_individual_main(
    rdi: RegistrationDataImport,
    rdi_individual: Individual,
    rdi_individual_lower_id: Individual,
    intra_batch_pair: BiographicDedupeSimilarityPair,
) -> None:
    create_needs_adjudication_tickets_for_biographic(BiographicDedupeSimilarityPair.objects.all(), rdi)

    ticket_details = GrievanceTicket.objects.get().ticket_details
    assert ticket_details.golden_records_individual == rdi_individual_lower_id
    assert list(ticket_details.possible_duplicates.all()) == [rdi_individual]


def test_create_needs_adjudication_tickets_for_biographic_skips_pair_with_missing_individual(
    rdi: RegistrationDataImport,
    pair_with_missing_individual: BiographicDedupeSimilarityPair,
) -> None:
    create_needs_adjudication_tickets_for_biographic(BiographicDedupeSimilarityPair.objects.all(), rdi)

    assert not GrievanceTicket.objects.exists()


def test_create_needs_adjudication_tickets_for_biographic_without_pairs_creates_no_ticket(
    rdi: RegistrationDataImport,
) -> None:
    create_needs_adjudication_tickets_for_biographic(BiographicDedupeSimilarityPair.objects.all(), rdi)

    assert not GrievanceTicket.objects.exists()


def test_create_needs_adjudication_tickets_for_biographic_skips_individuals_with_open_ticket(
    rdi: RegistrationDataImport,
    population_pair: BiographicDedupeSimilarityPair,
    open_biographical_ticket_for_population_pair: GrievanceTicket,
) -> None:
    create_needs_adjudication_tickets_for_biographic(BiographicDedupeSimilarityPair.objects.all(), rdi)

    assert list(GrievanceTicket.objects.all()) == [open_biographical_ticket_for_population_pair]


def test_create_needs_adjudication_tickets_for_biographic_links_tickets_of_different_main_individuals(
    rdi: RegistrationDataImport,
    population_pair: BiographicDedupeSimilarityPair,
    population_pair_of_rdi_individual_lower_id: BiographicDedupeSimilarityPair,
) -> None:
    create_needs_adjudication_tickets_for_biographic(BiographicDedupeSimilarityPair.objects.all(), rdi)

    ticket_1, ticket_2 = GrievanceTicket.objects.all()
    assert list(ticket_1.linked_tickets.all()) == [ticket_2]
    assert list(ticket_2.linked_tickets.all()) == [ticket_1]


def test_create_needs_adjudication_tickets_for_biographic_main_in_intra_batch_pair_gets_separate_ticket(
    rdi: RegistrationDataImport,
    rdi_individual: Individual,
    rdi_individual_lower_id: Individual,
    population_individual: Individual,
    population_pair: BiographicDedupeSimilarityPair,
    intra_batch_pair: BiographicDedupeSimilarityPair,
) -> None:
    # Pairs (rdi_individual, population) and (rdi_individual_lower_id, rdi_individual) are not merged
    # into one group: each main individual gets its own ticket.
    create_needs_adjudication_tickets_for_biographic(BiographicDedupeSimilarityPair.objects.all(), rdi)

    assert GrievanceTicket.objects.count() == 2
    assert list(
        TicketNeedsAdjudicationDetails.objects.get(golden_records_individual=rdi_individual).possible_duplicates.all()
    ) == [population_individual]
    assert list(
        TicketNeedsAdjudicationDetails.objects.get(
            golden_records_individual=rdi_individual_lower_id
        ).possible_duplicates.all()
    ) == [rdi_individual]
