import pytest

from extras.test_utils.factories import DocumentFactory, HouseholdFactory, IndividualFactory, ProgramFactory
from hope.apps.household.services.household_withdraw import HouseholdWithdraw
from hope.models import Document, Household, Individual
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def households_with_documents():
    household_one = HouseholdFactory(size=5)
    individuals_one = [household_one.head_of_household] + IndividualFactory.create_batch(
        4,
        household=household_one,
        business_area=household_one.business_area,
        program=household_one.program,
        registration_data_import=household_one.registration_data_import,
        rdi_merge_status=household_one.rdi_merge_status,
    )
    for individual in individuals_one:
        DocumentFactory.create_batch(
            2,
            individual=individual,
            status=Document.STATUS_VALID,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        DocumentFactory.create_batch(
            3,
            individual=individual,
            status=Document.STATUS_NEED_INVESTIGATION,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

    household_two = HouseholdFactory(size=5, program=ProgramFactory())
    individuals_two = [household_two.head_of_household] + IndividualFactory.create_batch(
        4,
        household=household_two,
        business_area=household_two.business_area,
        program=household_two.program,
        registration_data_import=household_two.registration_data_import,
        rdi_merge_status=household_two.rdi_merge_status,
    )
    for individual in individuals_two:
        DocumentFactory.create_batch(
            2,
            individual=individual,
            status=Document.STATUS_VALID,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        DocumentFactory.create_batch(
            3,
            individual=individual,
            status=Document.STATUS_NEED_INVESTIGATION,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

    return {"household": household_two}


def test_withdraw(households_with_documents) -> None:
    household = households_with_documents["household"]

    assert Household.objects.filter(withdrawn=True).count() == 0
    assert Individual.objects.filter(withdrawn=True).count() == 0
    assert Document.objects.filter(status=Document.STATUS_NEED_INVESTIGATION).count() == 30

    service = HouseholdWithdraw(household)
    service.withdraw()

    assert Household.objects.filter(withdrawn=True).count() == 1
    assert Individual.objects.filter(withdrawn=True).count() == 5
    assert Document.objects.filter(status=Document.STATUS_INVALID).count() == 25
