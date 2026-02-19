from datetime import date
from typing import Any, Callable

from django.core.files.base import ContentFile
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DeduplicationEngineSimilarityPairFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets,
    create_needs_adjudication_tickets_for_biometrics,
)
from hope.models import (
    BusinessArea,
    DeduplicationEngineSimilarityPair,
    Individual,
    Program,
    RegistrationDataImport,
    User,
)

pytestmark = [
    pytest.mark.usefixtures("django_elasticsearch_setup"),
    pytest.mark.django_db,
]


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def program_one(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        name="Test program ONE",
        business_area=business_area,
    )


@pytest.fixture
def basic_context(program_one: Program, business_area: BusinessArea) -> dict[str, Any]:
    household = HouseholdFactory(
        business_area=business_area,
        program=program_one,
        create_role=False,
    )
    individuals_to_create = [
        {
            "full_name": "test name",
            "given_name": "test",
            "family_name": "name",
            "birth_date": date(1999, 1, 22),
            "deduplication_golden_record_results": {
                "duplicates": [],
                "possible_duplicates": [],
            },
        },
        {
            "full_name": "Test2 Name2",
            "given_name": "Test2",
            "family_name": "Name2",
            "birth_date": date(1999, 1, 22),
            "deduplication_golden_record_results": {
                "duplicates": [],
                "possible_duplicates": [],
            },
        },
    ]
    individuals = [
        IndividualFactory(
            household=household,
            business_area=business_area,
            program=program_one,
            registration_data_import=household.registration_data_import,
            **individual_data,
        )
        for individual_data in individuals_to_create
    ]
    household.head_of_household = individuals[0]
    household.save(update_fields=["head_of_household"])

    return {
        "household": household,
        "individuals": individuals,
    }


@pytest.fixture
def biometric_context(
    business_area: BusinessArea,
    user: User,
) -> dict[str, Any]:
    business_area.biometric_deduplication_threshold = 44.44
    business_area.save(update_fields=["biometric_deduplication_threshold"])

    program = ProgramFactory(
        name="Test HOPE",
        business_area=business_area,
    )
    program2 = ProgramFactory(
        name="Test HOPE2",
        business_area=business_area,
    )
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        create_role=False,
    )
    household2 = HouseholdFactory(
        business_area=business_area,
        program=program,
        create_role=False,
    )
    household3 = HouseholdFactory(
        business_area=business_area,
        program=program2,
        create_role=False,
    )
    rdi = household.registration_data_import

    individuals = [
        IndividualFactory(
            id="11111111-1111-1111-1111-111111111111",
            household=household,
            business_area=business_area,
            program=program,
            registration_data_import=rdi,
            full_name="test name",
            given_name="test",
            family_name="name",
            birth_date=date(1999, 1, 22),
            deduplication_golden_record_results={"duplicates": [], "possible_duplicates": []},
            photo=ContentFile(b"aaa", name="fooa.png"),
        ),
        IndividualFactory(
            id="22222222-2222-2222-2222-222222222222",
            household=household,
            business_area=business_area,
            program=program,
            registration_data_import=rdi,
            full_name="Test2 Name2",
            given_name="Test2",
            family_name="Name2",
            birth_date=date(1999, 1, 22),
            deduplication_golden_record_results={"duplicates": [], "possible_duplicates": []},
            photo=ContentFile(b"bbb", name="foob.png"),
        ),
    ]
    other_individual = IndividualFactory(
        id="33333333-3333-3333-3333-333333333333",
        household=household2,
        business_area=business_area,
        program=program,
        registration_data_import=household2.registration_data_import,
        full_name="test name",
        given_name="test",
        family_name="name",
        birth_date=date(1999, 1, 22),
        deduplication_golden_record_results={"duplicates": [], "possible_duplicates": []},
        photo=ContentFile(b"aaa", name="fooa.png"),
    )
    other_individual2 = IndividualFactory(
        id="33333333-3333-3333-4444-333333333333",
        household=household3,
        business_area=business_area,
        program=program2,
        registration_data_import=household3.registration_data_import,
        full_name="test name 2",
        given_name="test 2",
        family_name="name 2",
        birth_date=date(1999, 1, 22),
        deduplication_golden_record_results={"duplicates": [], "possible_duplicates": []},
        photo=ContentFile(b"aaa", name="fooa2.png"),
    )

    household.head_of_household = individuals[0]
    household.save(update_fields=["head_of_household"])
    household2.head_of_household = other_individual
    household2.save(update_fields=["head_of_household"])
    household3.head_of_household = other_individual2
    household3.save(update_fields=["head_of_household"])

    ind1, ind2 = sorted(individuals, key=lambda item: item.id)
    ind3, ind4 = sorted([ind1, other_individual], key=lambda item: item.id)
    ind5 = other_individual2

    dedup_engine_similarity_pair = DeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=ind1,
        individual2=ind2,
        similarity_score=55.55,
        status_code=DeduplicationEngineSimilarityPair.StatusCode.STATUS_200,
    )
    dedup_engine_similarity_pair_2 = DeduplicationEngineSimilarityPairFactory(
        program=program,
        individual1=ind3,
        individual2=ind4,
        similarity_score=75.25,
        status_code=DeduplicationEngineSimilarityPair.StatusCode.STATUS_200,
    )
    dedup_engine_similarity_pair_3 = DeduplicationEngineSimilarityPairFactory(
        program=program2,
        individual1=ind5,
        individual2=None,
        similarity_score=0.0,
        status_code=DeduplicationEngineSimilarityPair.StatusCode.STATUS_429,
    )

    return {
        "business_area": business_area,
        "user": user,
        "program": program,
        "program2": program2,
        "rdi": rdi,
        "ind5": ind5,
        "pair_1": dedup_engine_similarity_pair,
        "pair_2": dedup_engine_similarity_pair_2,
        "pair_3": dedup_engine_similarity_pair_3,
    }


def test_create_needs_adjudication_ticket_with_the_same_ind(
    basic_context: dict[str, Any],
    business_area: BusinessArea,
) -> None:
    individuals = basic_context["individuals"]
    household = basic_context["household"]
    rdi = household.registration_data_import

    ind, ind_2 = individuals
    individual_ids = [ind.id, ind_2.id]
    assert Individual.objects.filter(id__in=individual_ids).count() == 2
    ind.deduplication_golden_record_results = {
        "duplicates": [{"hit_id": str(ind.pk)}],
        "possible_duplicates": [{"hit_id": str(ind.pk)}],
    }
    ind.save(update_fields=["deduplication_golden_record_results"])

    create_needs_adjudication_tickets(
        Individual.objects.filter(id__in=individual_ids),
        "duplicates",
        business_area,
        GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        rdi,
    )
    assert GrievanceTicket.objects.count() == 0

    ind.refresh_from_db()
    ind_2.refresh_from_db()
    ind.deduplication_golden_record_results = {
        "duplicates": [{"hit_id": str(ind.pk)}],
        "possible_duplicates": [{"hit_id": str(ind.pk)}],
    }
    ind_2.deduplication_golden_record_results = {
        "duplicates": [],
        "possible_duplicates": [],
    }
    ind.save(update_fields=["deduplication_golden_record_results"])
    ind_2.save(update_fields=["deduplication_golden_record_results"])

    create_needs_adjudication_tickets(
        Individual.objects.filter(id__in=individual_ids),
        "possible_duplicates",
        business_area,
        GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        rdi,
    )
    assert GrievanceTicket.objects.count() == 0

    ind.deduplication_golden_record_results = {
        "duplicates": [{"hit_id": str(ind_2.pk)}],
        "possible_duplicates": [{"hit_id": str(ind_2.pk)}],
    }
    ind_2.deduplication_golden_record_results = {
        "duplicates": [],
        "possible_duplicates": [],
    }
    ind.save(update_fields=["deduplication_golden_record_results"])
    ind_2.save(update_fields=["deduplication_golden_record_results"])

    create_needs_adjudication_tickets(
        Individual.objects.filter(id__in=individual_ids),
        "duplicates",
        business_area,
        GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        rdi,
    )
    assert GrievanceTicket.objects.count() == 1


def test_create_na_tickets_biometrics(biometric_context: dict[str, Any]) -> None:
    pair_1 = biometric_context["pair_1"]
    pair_2 = biometric_context["pair_2"]
    rdi: RegistrationDataImport = biometric_context["rdi"]

    assert GrievanceTicket.objects.count() == 0
    assert TicketNeedsAdjudicationDetails.objects.count() == 0
    assert rdi.deduplication_engine_status is None

    create_needs_adjudication_tickets_for_biometrics(DeduplicationEngineSimilarityPair.objects.none(), rdi)
    assert GrievanceTicket.objects.count() == 0
    assert TicketNeedsAdjudicationDetails.objects.count() == 0

    assert DeduplicationEngineSimilarityPair.objects.count() == 3
    create_needs_adjudication_tickets_for_biometrics(
        DeduplicationEngineSimilarityPair.objects.filter(pk=pair_1.pk),
        rdi,
    )

    assert GrievanceTicket.objects.count() == 1
    assert TicketNeedsAdjudicationDetails.objects.count() == 1
    grievance_ticket = GrievanceTicket.objects.first()
    na_ticket = TicketNeedsAdjudicationDetails.objects.first()

    assert grievance_ticket.category == GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION
    assert grievance_ticket.issue_type == GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY
    assert na_ticket.is_multiple_duplicates_version is True
    assert na_ticket.extra_data["dedup_engine_similarity_pair"] == pair_1.serialize_for_ticket()

    create_needs_adjudication_tickets_for_biometrics(
        DeduplicationEngineSimilarityPair.objects.filter(pk=pair_2.pk),
        rdi,
    )
    assert GrievanceTicket.objects.count() == 2
    assert TicketNeedsAdjudicationDetails.objects.count() == 2

    create_needs_adjudication_tickets_for_biometrics(
        DeduplicationEngineSimilarityPair.objects.filter(pk=pair_2.pk),
        rdi,
    )
    assert GrievanceTicket.objects.count() == 2
    assert TicketNeedsAdjudicationDetails.objects.count() == 2


def test_create_na_tickets_biometrics_for_1_ind(biometric_context: dict[str, Any]) -> None:
    pair_3 = biometric_context["pair_3"]
    ind5 = biometric_context["ind5"]
    rdi: RegistrationDataImport = biometric_context["rdi"]

    assert GrievanceTicket.objects.count() == 0
    assert TicketNeedsAdjudicationDetails.objects.count() == 0

    create_needs_adjudication_tickets_for_biometrics(
        DeduplicationEngineSimilarityPair.objects.filter(pk=pair_3.pk),
        rdi,
    )

    assert GrievanceTicket.objects.count() == 1
    assert TicketNeedsAdjudicationDetails.objects.count() == 1
    grievance_ticket = GrievanceTicket.objects.first()
    na_ticket = TicketNeedsAdjudicationDetails.objects.first()

    assert grievance_ticket.category == GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION
    assert grievance_ticket.issue_type == GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY
    assert str(na_ticket.golden_records_individual.id) == str(ind5.id)
    assert na_ticket.possible_duplicate is None
    assert na_ticket.extra_data["dedup_engine_similarity_pair"] == pair_3.serialize_for_ticket()


def test_ticket_biometric_query_response(
    authenticated_client: Any,
    create_user_role_with_permissions: Callable,
    biometric_context: dict[str, Any],
) -> None:
    user = biometric_context["user"]
    business_area = biometric_context["business_area"]
    program = biometric_context["program"]
    rdi: RegistrationDataImport = biometric_context["rdi"]
    pair_1 = biometric_context["pair_1"]

    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_BIOMETRIC_RESULTS,
        ],
        business_area,
        program,
    )

    assert GrievanceTicket.objects.count() == 0
    assert TicketNeedsAdjudicationDetails.objects.count() == 0

    create_needs_adjudication_tickets_for_biometrics(
        DeduplicationEngineSimilarityPair.objects.filter(pk=pair_1.pk),
        rdi,
    )
    assert GrievanceTicket.objects.count() == 1
    assert TicketNeedsAdjudicationDetails.objects.count() == 1

    response = authenticated_client.get(
        reverse(
            "api:grievance:grievance-tickets-list",
            kwargs={
                "business_area_slug": business_area.slug,
                "program_slug": program.slug,
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    data_extra = TicketNeedsAdjudicationDetails.objects.first().extra_data
    assert "individual1" in data_extra["dedup_engine_similarity_pair"]
    assert "individual2" in data_extra["dedup_engine_similarity_pair"]
    assert "status_code" in data_extra["dedup_engine_similarity_pair"]
    assert "similarity_score" in data_extra["dedup_engine_similarity_pair"]
