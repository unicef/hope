from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone
from freezegun import freeze_time
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.household.celery_tasks import (
    cleanup_indexes_in_inactive_programs_task,
    enroll_households_to_program_task,
)
from hope.apps.household.const import ROLE_PRIMARY
from hope.models import Document, Household, IndividualIdentity, Program
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program_source(business_area):
    return ProgramFactory(status=Program.ACTIVE, name="Program source", business_area=business_area)


@pytest.fixture
def program_target(business_area):
    return ProgramFactory(status=Program.ACTIVE, name="Program target", business_area=business_area)


@pytest.fixture
def household_one_context(business_area, program_source):
    individual = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program_source,
    )
    household = HouseholdFactory(
        business_area=business_area,
        program=program_source,
        head_of_household=individual,
        create_role=False,
    )
    household.head_of_household = individual
    household.household_collection = None
    household.save(update_fields=["head_of_household", "household_collection"])
    individual.individual_collection = None
    individual.save(update_fields=["individual_collection"])
    IndividualRoleInHouseholdFactory(
        individual=individual,
        household=household,
        role=ROLE_PRIMARY,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    DocumentFactory(individual=individual, program=individual.program, rdi_merge_status=MergeStatusModel.MERGED)
    IndividualIdentityFactory(individual=individual, rdi_merge_status=MergeStatusModel.MERGED)
    return {"household": household, "individual": individual}


@pytest.fixture
def household_two_context(business_area, program_source, program_target):
    household_source = HouseholdFactory(
        business_area=business_area,
        program=program_source,
    )
    individual_source = household_source.individuals.first()
    if household_source.household_collection is None:
        household_source.household_collection = HouseholdCollectionFactory()
        household_source.save(update_fields=["household_collection"])
    if individual_source.individual_collection is None:
        individual_source.individual_collection = IndividualCollectionFactory()
        individual_source.save(update_fields=["individual_collection"])

    individual_target = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program_target,
        individual_collection=individual_source.individual_collection,
    )
    individual_target.unicef_id = individual_source.unicef_id
    individual_target.save(update_fields=["unicef_id"])
    household_target = HouseholdFactory(
        business_area=business_area,
        program=program_target,
        household_collection=household_source.household_collection,
        head_of_household=individual_target,
        create_role=False,
    )
    household_target.unicef_id = household_source.unicef_id
    household_target.save(update_fields=["unicef_id"])

    return {
        "household_source": household_source,
        "individual_source": individual_source,
        "household_target": household_target,
        "individual_target": individual_target,
    }


@pytest.mark.elasticsearch
def test_enroll_households_to_program_task(
    user,
    program_source,
    program_target,
    household_one_context,
    household_two_context,
) -> None:
    household1 = household_one_context["household"]
    individual = household_one_context["individual"]
    household2 = household_two_context["household_source"]

    assert program_target.households.count() == 1
    assert program_target.individuals.count() == 1
    assert program_source.households.count() == 2
    assert program_source.individuals.count() == 2

    assert household1.household_collection is None

    assert Household.objects.filter(unicef_id=household1.unicef_id).count() == 1
    assert Household.objects.filter(unicef_id=household2.unicef_id).count() == 2

    enroll_households_to_program_task(
        households_ids=[household1.id, household2.id],
        program_for_enroll_id=str(program_target.id),
        user_id=str(user.pk),
    )
    household1.refresh_from_db()
    household2.refresh_from_db()

    assert program_target.households.count() == 2
    assert program_target.individuals.count() == 2
    assert program_source.households.count() == 2
    assert program_source.individuals.count() == 2

    assert household1.household_collection is not None

    assert Household.objects.filter(unicef_id=household1.unicef_id).count() == 2
    assert Household.objects.filter(unicef_id=household2.unicef_id).count() == 2
    enrolled_household = Household.objects.filter(program=program_target, unicef_id=household1.unicef_id).first()
    assert (
        enrolled_household.individuals_and_roles.filter(role=ROLE_PRIMARY).first().individual.unicef_id
        == individual.unicef_id
    )
    assert Document.objects.filter(individual__household=enrolled_household).count() == 1
    assert IndividualIdentity.objects.filter(individual__household=enrolled_household).count() == 1


@pytest.mark.parametrize(
    ("days_ago", "should_delete"),
    [
        (7, True),  # same date - 7 days ago, matches
        (6.9, True),  # same date, matches
        (7.5, False),  # day before, no match
        (8, False),  # day before, no match
        (6, False),  # too recent, no match
        (0, False),  # just now, no match
    ],
)
@freeze_time("2026-02-26 01:00:00")
@patch("hope.apps.household.celery_tasks.delete_program_indexes", return_value=(True, "ok"))
def test_cleanup_inactive_program_indexes_task_window(delete_mock, days_ago, should_delete):
    program = ProgramFactory(status=Program.FINISHED)
    updated_at = timezone.now() - timedelta(days=days_ago)
    Program.objects.filter(pk=program.pk).update(updated_at=updated_at)

    cleanup_indexes_in_inactive_programs_task()

    if should_delete:
        delete_mock.assert_called_once_with(str(program.id))
    else:
        delete_mock.assert_not_called()


@freeze_time("2026-02-26 01:00:00")
@patch("hope.apps.household.celery_tasks.delete_program_indexes", return_value=(True, "ok"))
def test_cleanup_inactive_program_indexes_task_skips_active(delete_mock):
    program = ProgramFactory(status=Program.ACTIVE)
    Program.objects.filter(pk=program.pk).update(updated_at=timezone.now() - timedelta(days=7))

    cleanup_indexes_in_inactive_programs_task()

    delete_mock.assert_not_called()


@freeze_time("2026-02-26 01:00:00")
@patch("hope.apps.household.celery_tasks.delete_program_indexes", return_value=(True, "ok"))
def test_cleanup_inactive_program_indexes_task_multiple_programs(delete_mock):
    to_cleanup = ProgramFactory(status=Program.FINISHED)
    too_recent = ProgramFactory(status=Program.FINISHED)
    too_old = ProgramFactory(status=Program.FINISHED)
    active = ProgramFactory(status=Program.ACTIVE)

    Program.objects.filter(pk=to_cleanup.pk).update(updated_at=timezone.now() - timedelta(days=7))
    Program.objects.filter(pk=too_recent.pk).update(updated_at=timezone.now() - timedelta(days=3))
    Program.objects.filter(pk=too_old.pk).update(updated_at=timezone.now() - timedelta(days=10))
    Program.objects.filter(pk=active.pk).update(updated_at=timezone.now() - timedelta(days=7))

    cleanup_indexes_in_inactive_programs_task()

    delete_mock.assert_called_once_with(str(to_cleanup.id))
