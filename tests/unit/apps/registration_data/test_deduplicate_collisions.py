from types import SimpleNamespace
from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CountryFactory,
    HouseholdFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.program.collision_detectors import IdentificationKeyCollisionDetector
from hope.apps.registration_data.tasks.deduplicate import DeduplicateTask, DeduplicationResult
from hope.models import PendingIndividual, Program, RegistrationDataImport

pytestmark = pytest.mark.django_db


@pytest.fixture
def collision_context() -> dict[str, Any]:
    business_area = BusinessAreaFactory()
    poland = CountryFactory(name="Poland", short_name="Poland", iso_code2="PL", iso_code3="POL", iso_num="616")
    business_area.countries.add(poland)

    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    program.collision_detector = IdentificationKeyCollisionDetector
    program.save(update_fields=["collision_detector"])

    importing_rdi = RegistrationDataImportFactory(
        program=program,
        business_area=business_area,
        status=RegistrationDataImport.IMPORTING,
    )
    merged_rdi = RegistrationDataImportFactory(
        program=program,
        business_area=business_area,
        status=RegistrationDataImport.MERGED,
    )

    HouseholdFactory(
        program=program,
        business_area=business_area,
        registration_data_import=merged_rdi,
        identification_key="COLLISION-KEY-001",
    )

    pending_household = PendingHouseholdFactory(
        program=program,
        business_area=business_area,
        registration_data_import=importing_rdi,
        identification_key="COLLISION-KEY-001",
        create_role=False,
    )
    pending_individual = PendingIndividualFactory(
        household=pending_household,
        business_area=business_area,
        program=program,
        registration_data_import=importing_rdi,
        identification_key="IND-KEY-2",
    )
    pending_household.head_of_household = pending_individual
    pending_household.save(update_fields=["head_of_household"])

    return {
        "program": program,
        "importing_rdi": importing_rdi,
        "pending_individual": pending_individual,
    }


def test_collided_individuals_ids_to_exclude(collision_context: dict[str, Any]) -> None:
    program = collision_context["program"]
    importing_rdi = collision_context["importing_rdi"]
    pending_individual = collision_context["pending_individual"]

    task = DeduplicateTask(program.business_area.slug, program.id)
    ids_to_exclude = task.collided_individuals_ids_to_exclude(
        PendingIndividual.objects.filter(registration_data_import=importing_rdi),
        importing_rdi,
    )

    assert str(pending_individual.id) in ids_to_exclude


def test_deduplicate_pending_individuals_skips_collided(
    collision_context: dict[str, Any],
    mocker: Any,
) -> None:
    program = collision_context["program"]
    importing_rdi = collision_context["importing_rdi"]

    task = DeduplicateTask(program.business_area.slug, program.id)
    mocker.patch(
        "hope.apps.registration_data.tasks.deduplicate.get_individual_doc",
        return_value=SimpleNamespace(_index=SimpleNamespace(_name="test-index")),
    )
    mocker.patch("hope.apps.registration_data.tasks.deduplicate.populate_index")
    mocker.patch("hope.apps.registration_data.tasks.deduplicate.ensure_index_ready")
    mocker.patch("hope.apps.registration_data.tasks.deduplicate.remove_elasticsearch_documents_by_matching_ids")
    mocker.patch.object(
        task,
        "_deduplicate_single_pending_individual",
        return_value=DeduplicationResult([], [], [], [], {"duplicates": [], "possible_duplicates": []}),
    )

    spy = mocker.spy(task, "_deduplicate_single_individual")
    task.deduplicate_pending_individuals(importing_rdi)

    assert spy.call_count == 0
