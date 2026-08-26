from typing import Any, Callable
from uuid import UUID

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    DataCollectingTypeFactory,
)
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import HEAD
from hope.models import BusinessArea, DataCollectingType, Individual, Partner, Program, User

pytestmark = pytest.mark.django_db()

LIST_PERMISSIONS = [
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
]

# The household unicef id both business areas below reuse. Only the business-area predicate
# under test separates the local household from the foreign one.
SHARED_HOUSEHOLD_UNICEF_ID = "HH-BATCH-0001"

# The fallback lookup keeps the lowest individual id per household unicef id, so an unscoped
# lookup collapses both business areas into one group and answers with whichever id sorts
# first. Pinning the ids makes the foreign individual that one: unscoped, this test fails.
FOREIGN_INDIVIDUAL_ID = UUID("00000000-0000-4000-8000-000000000001")
LOCAL_INDIVIDUAL_ID = UUID("ffffffff-0000-4000-8000-000000000002")


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan", code="AFG")


@pytest.fixture
def ukraine() -> BusinessArea:
    return BusinessAreaFactory(slug="ukraine", name="Ukraine", code="UKR")


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def social_dct() -> DataCollectingType:
    return DataCollectingTypeFactory(label="Social", code="social", type=DataCollectingType.Type.SOCIAL)


@pytest.fixture
def social_beneficiary_group() -> Any:
    return BeneficiaryGroupFactory(master_detail=False)


@pytest.fixture
def social_program_afghanistan(
    afghanistan: BusinessArea, social_dct: DataCollectingType, social_beneficiary_group: Any
) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="afghanistan social program",
        data_collecting_type=social_dct,
        beneficiary_group=social_beneficiary_group,
    )


@pytest.fixture
def social_program_ukraine(
    ukraine: BusinessArea, social_dct: DataCollectingType, social_beneficiary_group: Any
) -> Program:
    return ProgramFactory(
        business_area=ukraine,
        status=Program.ACTIVE,
        name="ukraine social program",
        data_collecting_type=social_dct,
        beneficiary_group=social_beneficiary_group,
    )


@pytest.fixture
def local_head_of_household(afghanistan: BusinessArea, social_program_afghanistan: Program) -> Individual:
    individual = IndividualFactory(
        id=LOCAL_INDIVIDUAL_ID,
        business_area=afghanistan,
        program=social_program_afghanistan,
        household=None,
        full_name="Local Resident",
        relationship=HEAD,
    )
    household = HouseholdFactory(
        business_area=afghanistan,
        program=social_program_afghanistan,
        head_of_household=individual,
    )
    household.unicef_id = SHARED_HOUSEHOLD_UNICEF_ID
    household.save(update_fields=["unicef_id"])
    individual.household = household
    individual.unicef_id = "IND-BATCH-LOCAL"
    individual.save(update_fields=["household", "unicef_id"])
    return individual


@pytest.fixture
def foreign_head_of_household(ukraine: BusinessArea, social_program_ukraine: Program) -> Individual:
    individual = IndividualFactory(
        id=FOREIGN_INDIVIDUAL_ID,
        business_area=ukraine,
        program=social_program_ukraine,
        household=None,
        full_name="Foreign Namesake",
        relationship=HEAD,
    )
    household = HouseholdFactory(
        business_area=ukraine,
        program=social_program_ukraine,
        head_of_household=individual,
    )
    household.unicef_id = SHARED_HOUSEHOLD_UNICEF_ID
    household.save(update_fields=["unicef_id"])
    individual.household = household
    individual.unicef_id = "IND-BATCH-FOREIGN"
    individual.save(update_fields=["household", "unicef_id"])
    return individual


@pytest.fixture
def local_ticket(afghanistan: BusinessArea, social_program_afghanistan: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        household_unicef_id=SHARED_HOUSEHOLD_UNICEF_ID,
    )
    ticket.programs.add(social_program_afghanistan)
    return ticket


@pytest.fixture
def foreign_ticket(ukraine: BusinessArea, social_program_ukraine: Program) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        business_area=ukraine,
        household_unicef_id=SHARED_HOUSEHOLD_UNICEF_ID,
    )
    ticket.programs.add(social_program_ukraine)
    return ticket


@pytest.fixture
def list_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-list",
        kwargs={"business_area_slug": afghanistan.slug},
    )


def test_target_id_falls_back_to_the_head_of_household_in_the_request_business_area(
    afghanistan: BusinessArea,
    user: User,
    api_client: Any,
    create_user_role_with_permissions: Callable,
    local_head_of_household: Individual,
    foreign_head_of_household: Individual,
    local_ticket: GrievanceTicket,
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert [result["target_id"] for result in response.data["results"]] == ["IND-BATCH-LOCAL"]


def test_related_tickets_count_ignores_a_ticket_for_the_same_household_in_another_business_area(
    afghanistan: BusinessArea,
    user: User,
    api_client: Any,
    create_user_role_with_permissions: Callable,
    local_ticket: GrievanceTicket,
    foreign_ticket: GrievanceTicket,
    list_url: str,
) -> None:
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert [result["related_tickets_count"] for result in response.data["results"]] == [0]


def test_related_tickets_count_still_counts_a_second_ticket_in_the_request_business_area(
    afghanistan: BusinessArea,
    user: User,
    api_client: Any,
    create_user_role_with_permissions: Callable,
    social_program_afghanistan: Program,
    local_ticket: GrievanceTicket,
    foreign_ticket: GrievanceTicket,
    list_url: str,
) -> None:
    sibling = GrievanceTicketFactory(
        business_area=afghanistan,
        household_unicef_id=SHARED_HOUSEHOLD_UNICEF_ID,
    )
    sibling.programs.add(social_program_afghanistan)
    create_user_role_with_permissions(user, LIST_PERMISSIONS, afghanistan, whole_business_area_access=True)

    response = api_client(user).get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert [result["related_tickets_count"] for result in response.data["results"]] == [1, 1]
