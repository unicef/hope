import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import HouseholdFactory, IndividualFactory, ProgramFactory
from hope.apps.grievance.services.data_change.utils import handle_role
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.models import IndividualRoleInHousehold, Program
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def role_context() -> dict:
    program = ProgramFactory(name="Test Program", status=Program.ACTIVE)
    household = HouseholdFactory(
        program=program,
        business_area=program.business_area,
        create_role=False,
    )
    individual = IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        registration_data_import=household.registration_data_import,
    )
    household.head_of_household = individual
    household.save(update_fields=["head_of_household"])
    return {"household": household, "individual": individual}


def test_handle_role_alternate_into_primary(role_context: dict) -> None:
    household = role_context["household"]
    individual = role_context["individual"]
    IndividualRoleInHousehold.objects.create(
        household=household,
        individual=individual,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 1
    assert IndividualRoleInHousehold.objects.get(household=household, individual=individual).role == ROLE_ALTERNATE

    handle_role(household, individual, ROLE_PRIMARY)

    assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 1
    assert IndividualRoleInHousehold.objects.get(household=household, individual=individual).role == ROLE_PRIMARY


def test_handle_role_no_role_into_alternate(role_context: dict) -> None:
    household = role_context["household"]
    individual = role_context["individual"]
    assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 0

    handle_role(household, individual, ROLE_ALTERNATE)

    assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 1
    assert IndividualRoleInHousehold.objects.get(household=household, individual=individual).role == ROLE_ALTERNATE


def test_handle_role_alternate_into_no_role(role_context: dict) -> None:
    household = role_context["household"]
    individual = role_context["individual"]
    IndividualRoleInHousehold.objects.create(
        household=household,
        individual=individual,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 1
    handle_role(household, individual, None)
    assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 0


def test_handle_role_primary_into_no_role(role_context: dict) -> None:
    household = role_context["household"]
    individual = role_context["individual"]
    IndividualRoleInHousehold.objects.create(
        household=household,
        individual=individual,
        role=ROLE_PRIMARY,
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    assert IndividualRoleInHousehold.objects.filter(household=household, individual=individual).count() == 1
    with pytest.raises(ValidationError, match="Ticket cannot be closed, primary collector role has to be reassigned"):
        handle_role(household, individual, None)
