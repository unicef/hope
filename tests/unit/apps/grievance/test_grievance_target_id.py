"""`target_id` falls back to an individual of the ticket's household for social worker
programmes. `GrievanceListBatchMixin` (`src/hope/apps/grievance/api/mixins.py`) resolves that
fallback once per page instead of as a correlated subquery in the main list statement, which
is what kept `household` in that statement's lock set (ticket 331051).
"""

from typing import Any, Callable

import hope.apps.household.api.serializers.household  # noqa: F401, isort: skip - resolve circular import; must load before grievance views

from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BeneficiaryGroupFactory, BusinessAreaFactory, DataCollectingTypeFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory, TicketHouseholdDataUpdateDetailsFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.sql import main_list_statement
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.api.mixins import get_fallback_individual_unicef_ids
from hope.apps.grievance.api.views import GrievanceTicketGlobalViewSet, GrievanceTicketViewSet
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, DataCollectingType, Household, Partner, Program, User

pytestmark = pytest.mark.django_db()

LIST_PERMISSIONS = [
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
]


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan", code="AFG")


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def social_program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="social worker program",
        data_collecting_type=DataCollectingTypeFactory(
            label="Social", code="social", type=DataCollectingType.Type.SOCIAL
        ),
        beneficiary_group=BeneficiaryGroupFactory(master_detail=False),
    )


@pytest.fixture
def standard_program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE, name="standard program")


@pytest.fixture
def household_with_three_individuals(afghanistan: BusinessArea, social_program: Program) -> Household:
    household = HouseholdFactory(
        business_area=afghanistan,
        program=social_program,
        head_of_household=IndividualFactory(household=None, business_area=afghanistan, program=social_program),
    )
    IndividualFactory(household=household, business_area=afghanistan, program=social_program)
    IndividualFactory(household=household, business_area=afghanistan, program=social_program)
    household.head_of_household.household = household
    household.head_of_household.save()
    return household


@pytest.fixture
def social_program_ticket(
    afghanistan: BusinessArea,
    social_program: Program,
    household_with_three_individuals: Household,
) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=None, description="social worker ticket")
    ticket.programs.set([social_program])
    # The household data update details carry no individual, so target_id takes the fallback branch.
    TicketHouseholdDataUpdateDetailsFactory(ticket=ticket, household=household_with_three_individuals)
    ticket.refresh_from_db()
    return ticket


@pytest.fixture
def second_household(afghanistan: BusinessArea, social_program: Program) -> Household:
    household = HouseholdFactory(
        business_area=afghanistan,
        program=social_program,
        head_of_household=IndividualFactory(household=None, business_area=afghanistan, program=social_program),
    )
    household.head_of_household.household = household
    household.head_of_household.save()
    return household


@pytest.fixture
def second_social_program_ticket(
    afghanistan: BusinessArea,
    social_program: Program,
    second_household: Household,
) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=None, description="second social worker ticket")
    ticket.programs.set([social_program])
    TicketHouseholdDataUpdateDetailsFactory(ticket=ticket, household=second_household)
    ticket.refresh_from_db()
    return ticket


@pytest.fixture
def standard_program_ticket(
    afghanistan: BusinessArea,
    standard_program: Program,
    household_with_three_individuals: Household,
) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(business_area=afghanistan, admin2=None, description="standard ticket")
    ticket.programs.set([standard_program])
    TicketHouseholdDataUpdateDetailsFactory(ticket=ticket, household=household_with_three_individuals)
    ticket.refresh_from_db()
    return ticket


def global_list_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-list",
        kwargs={"business_area_slug": business_area.slug},
    )


def program_list_url(business_area: BusinessArea, program: Program) -> str:
    return reverse(
        "api:grievance:grievance-tickets-list",
        kwargs={"business_area_slug": business_area.slug, "program_code": program.code},
    )


LIST_URL_BUILDERS = [
    pytest.param(lambda business_area, program: global_list_url(business_area), id="global-list"),
    pytest.param(program_list_url, id="program-list"),
]


@pytest.mark.parametrize("build_url", LIST_URL_BUILDERS)
def test_list_target_id_is_the_household_individual_for_a_social_worker_program(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    social_program: Program,
    social_program_ticket: GrievanceTicket,
    household_with_three_individuals: Household,
    create_user_role_with_permissions: Callable,
    build_url: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(build_url(afghanistan, social_program))

    assert response.status_code == status.HTTP_200_OK
    # GrievanceTicket.target_id is the same rule computed independently of the API.
    assert response.data["results"][0]["target_id"] == social_program_ticket.target_id
    assert social_program_ticket.target_id in set(
        household_with_three_individuals.individuals.values_list("unicef_id", flat=True)
    )


def test_global_list_target_id_is_the_household_unicef_id_outside_a_social_worker_program(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    standard_program_ticket: GrievanceTicket,
    household_with_three_individuals: Household,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(global_list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0]["target_id"] == household_with_three_individuals.unicef_id


def test_global_list_main_statement_does_not_touch_household(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    social_program_ticket: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    # The point of the chunk: the fallback used to be a correlated subquery over
    # household_individual in this statement, so every list request took household with it.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    with CaptureQueriesContext(connection) as captured:
        response = api_client(user).get(global_list_url(afghanistan))

    assert response.status_code == status.HTTP_200_OK
    main_statement = main_list_statement(captured, "grievance_grievanceticket")
    assert "household_individual" not in main_statement
    assert "household_household" not in main_statement


def test_fallback_map_is_one_query_for_a_page_of_social_worker_tickets(
    social_program_ticket: GrievanceTicket,
    second_social_program_ticket: GrievanceTicket,
    household_with_three_individuals: Household,
    second_household: Household,
    django_assert_num_queries: Any,
) -> None:
    # has_social_worker_program_annotated is what the list viewsets annotate; the helper reads
    # it to leave the rest of the page alone.
    social_program_ticket.has_social_worker_program_annotated = True
    second_social_program_ticket.has_social_worker_program_annotated = True

    with django_assert_num_queries(1):
        result = get_fallback_individual_unicef_ids([social_program_ticket, second_social_program_ticket])

    assert result == {
        household_with_three_individuals.unicef_id: social_program_ticket.target_id,
        second_household.unicef_id: second_social_program_ticket.target_id,
    }


def test_fallback_map_is_no_query_without_a_social_worker_ticket(
    standard_program_ticket: GrievanceTicket,
    django_assert_num_queries: Any,
) -> None:
    standard_program_ticket.has_social_worker_program_annotated = False

    with django_assert_num_queries(0):
        result = get_fallback_individual_unicef_ids([standard_program_ticket])

    assert result == {}


@pytest.mark.parametrize(
    ("viewset_class", "build_kwargs"),
    [
        pytest.param(
            GrievanceTicketGlobalViewSet,
            lambda business_area, program: {"business_area_slug": business_area.slug},
            id="global-list",
        ),
        pytest.param(
            GrievanceTicketViewSet,
            lambda business_area, program: {
                "business_area_slug": business_area.slug,
                "program_code": program.code,
            },
            id="program-list",
        ),
    ],
)
def test_list_queryset_annotates_the_social_worker_program_flag(
    user: User,
    afghanistan: BusinessArea,
    social_program: Program,
    create_user_role_with_permissions: Callable,
    viewset_class: type,
    build_kwargs: Callable,
) -> None:
    # get_fallback_individual_unicef_ids and GrievanceTicketListSerializer.get_target_id both
    # read has_social_worker_program_annotated off the row and treat a missing attribute as
    # "not a social worker programme". Dropping the annotation from either queryset would not
    # raise - it would silently serve household_unicef_id as target_id for every ticket.
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)
    viewset = viewset_class()
    request = APIRequestFactory().get("/")
    request.user = user
    viewset.request = request
    viewset.action = "list"
    viewset.kwargs = build_kwargs(afghanistan, social_program)

    queryset = viewset.get_queryset()

    assert "has_social_worker_program_annotated" in queryset.query.annotations
