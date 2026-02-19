from typing import Any
from unittest.mock import patch

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    IndividualFactory,
    ProgramFactory,
    SanctionListFactory,
)
from hope.apps.grievance.tasks.deduplicate_and_check_sanctions import (
    deduplicate_and_check_against_sanctions_list_task_single_individual,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def task_context() -> dict[str, Any]:
    business_area = BusinessAreaFactory(slug="afghanistan")
    program = ProgramFactory(
        name="Test program ONE",
        business_area=business_area,
    )
    individual = IndividualFactory(
        household=None,
        program=program,
        business_area=business_area,
        full_name="Benjamin Butler",
        given_name="Benjamin",
        family_name="Butler",
        phone_no="(953)682-4596",
        birth_date="1943-07-30",
    )
    return {
        "business_area": business_area,
        "program": program,
        "individual": individual,
    }


@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.populate_index")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.HardDocumentDeduplication.deduplicate")
@patch(
    "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.DeduplicateTask.deduplicate_individuals_from_other_source"
)
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.create_needs_adjudication_tickets")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.check_against_sanction_list_pre_merge")
def test_execute_postponed_deduplication(
    sanction_execute_mock: Any,
    create_needs_adjudication_tickets_mock: Any,
    deduplicate_individuals_mock: Any,
    deduplicate_mock: Any,
    populate_index_mock: Any,
    task_context: dict[str, Any],
) -> None:
    business_area = task_context["business_area"]
    individual = task_context["individual"]
    business_area.postpone_deduplication = True
    business_area.save(update_fields=["postpone_deduplication"])

    deduplicate_and_check_against_sanctions_list_task_single_individual(
        should_populate_index=True,
        individual=individual,
    )

    assert populate_index_mock.call_count == 1
    assert deduplicate_mock.call_count == 1
    assert deduplicate_individuals_mock.call_count == 0
    assert create_needs_adjudication_tickets_mock.call_count == 0
    assert sanction_execute_mock.call_count == 0


@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.populate_index")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.HardDocumentDeduplication.deduplicate")
@patch(
    "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.DeduplicateTask.deduplicate_individuals_from_other_source"
)
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.create_needs_adjudication_tickets")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.check_against_sanction_list_pre_merge")
def test_execute_non_postponed_without_screening(
    sanction_execute_mock: Any,
    create_needs_adjudication_tickets_mock: Any,
    deduplicate_individuals_mock: Any,
    deduplicate_mock: Any,
    populate_index_mock: Any,
    task_context: dict[str, Any],
) -> None:
    business_area = task_context["business_area"]
    individual = task_context["individual"]
    business_area.postpone_deduplication = False
    business_area.save(update_fields=["postpone_deduplication"])

    deduplicate_and_check_against_sanctions_list_task_single_individual(
        should_populate_index=False,
        individual=individual,
    )

    assert populate_index_mock.call_count == 0
    assert deduplicate_mock.call_count == 1
    assert deduplicate_individuals_mock.call_count == 1
    assert create_needs_adjudication_tickets_mock.call_count == 2
    assert sanction_execute_mock.call_count == 0


@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.populate_index")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.HardDocumentDeduplication.deduplicate")
@patch(
    "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.DeduplicateTask.deduplicate_individuals_from_other_source"
)
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.create_needs_adjudication_tickets")
@patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.check_against_sanction_list_pre_merge")
def test_execute_non_postponed_with_screening(
    sanction_execute_mock: Any,
    create_needs_adjudication_tickets_mock: Any,
    deduplicate_individuals_mock: Any,
    deduplicate_mock: Any,
    populate_index_mock: Any,
    task_context: dict[str, Any],
) -> None:
    business_area = task_context["business_area"]
    individual = task_context["individual"]
    program = task_context["program"]
    business_area.postpone_deduplication = False
    business_area.save(update_fields=["postpone_deduplication"])

    sanction_list = SanctionListFactory()
    program.sanction_lists.add(sanction_list)

    deduplicate_and_check_against_sanctions_list_task_single_individual(
        should_populate_index=False,
        individual=individual,
    )

    assert populate_index_mock.call_count == 0
    assert deduplicate_mock.call_count == 1
    assert deduplicate_individuals_mock.call_count == 1
    assert create_needs_adjudication_tickets_mock.call_count == 2
    assert sanction_execute_mock.call_count == 1
