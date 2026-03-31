"""Tests for periodic data update models."""

from typing import Any
from unittest.mock import PropertyMock, patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django_celery_boost.models import AsyncJobModel
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeForPDUFactory,
    PDUOnlineEditFactory,
    ProgramFactory,
)
from hope.models import AsyncJob, BusinessArea, FlexibleAttribute, PDUOnlineEdit, Program

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program1(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=business_area,
        name="Program 1",
        status=Program.ACTIVE,
    )


@pytest.fixture
def program2(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=business_area,
        name="Program 2",
        status=Program.ACTIVE,
    )


@pytest.fixture
def flex_field() -> FlexibleAttribute:
    return FlexibleAttribute.objects.create(
        name="flex_field_1",
        type=FlexibleAttribute.STRING,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": "value"},
    )


@pytest.fixture
def pdu_field(program1: Program) -> FlexibleAttribute:
    return FlexibleAttributeForPDUFactory(
        program=program1,
        label="PDU Field 1",
    )


def test_unique_name_rules_for_flex_fields_same_name_different_programs(
    program1: Program, program2: Program, pdu_field: FlexibleAttribute
) -> None:
    # Possible to have flex fields with the same name in different programs
    pdu_field2 = FlexibleAttributeForPDUFactory(
        program=program2,
        label="PDU Field 1",
    )
    assert FlexibleAttribute.objects.filter(name=pdu_field2.name).count() == 2


def test_unique_name_rules_for_flex_fields_same_name_same_program(
    program1: Program, pdu_field: FlexibleAttribute
) -> None:
    # Not possible to have flex fields with the same name in the same program
    with pytest.raises(IntegrityError) as ie_context:
        FlexibleAttributeForPDUFactory(
            program=program1,
            label="PDU Field 1",
        )
    assert 'duplicate key value violates unique constraint "unique_name_program"' in str(ie_context.value)


def test_unique_name_rules_for_flex_fields_same_name_without_program(flex_field: FlexibleAttribute) -> None:
    # Not possible to have flex fields with the same name without a program
    with pytest.raises(IntegrityError) as ie_context:
        FlexibleAttribute.objects.create(
            name=flex_field.name,
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"English(EN)": "value"},
        )
    assert 'duplicate key value violates unique constraint "unique_name_without_program"' in str(ie_context.value)


def test_unique_name_rules_for_flex_fields_program_vs_no_program(
    pdu_field: FlexibleAttribute, flex_field: FlexibleAttribute, program1: Program
) -> None:
    # Not possible to have flex fields with the same name in a program and without a program
    with pytest.raises(ValidationError) as ve_context:
        FlexibleAttribute.objects.create(
            name=pdu_field.name,
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"English(EN)": "value"},
        )
    assert f'Flex field with name "{pdu_field.name}" already exists inside a program.' in str(ve_context.value)

    with pytest.raises(ValidationError) as ve_context:
        FlexibleAttributeForPDUFactory(
            program=program1,
            label="Flex Field 1",
        )
    assert f'Flex field with name "{flex_field.name}" already exists without a program.' in str(ve_context.value)


def test_flexible_attribute_label_without_english_en_key() -> None:
    # FlexibleAttribute requires English(EN) key in label
    with pytest.raises(ValidationError, match='The "English\\(EN\\)" key is required in the label.'):
        FlexibleAttribute.objects.create(
            name="flex_field_2",
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"other value": "value"},
        )


def test_flexible_attribute_label_update_without_english_en_key() -> None:
    # Updating FlexibleAttribute label without English(EN) key raises validation error
    flexible_attribute = FlexibleAttribute.objects.create(
        name="flex_field_2",
        type=FlexibleAttribute.STRING,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": "value"},
    )
    flexible_attribute.label = {"wrong": "value"}
    with pytest.raises(ValidationError, match='The "English\\(EN\\)" key is required in the label.'):
        flexible_attribute.save()


def test_pdu_online_edit_async_jobs_returns_related_jobs() -> None:
    pdu_online_edit = PDUOnlineEditFactory()
    AsyncJob.objects.create(
        program=pdu_online_edit.program,
        content_object=pdu_online_edit,
        job_name="generate_edit_data",
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.generate_pdu_online_edit_data_task_action",
        config={"pdu_online_edit_id": pdu_online_edit.pk},
        group_key=f"generate_pdu_online_edit_data_task:{pdu_online_edit.pk}",
        curr_async_result_id="generate-id",
    )
    AsyncJob.objects.create(
        program=pdu_online_edit.program,
        content_object=pdu_online_edit,
        job_name="merge",
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.merge_pdu_online_edit_task_action",
        config={"pdu_online_edit_id": pdu_online_edit.pk},
        group_key=f"merge_pdu_online_edit_task:{pdu_online_edit.pk}",
        curr_async_result_id="merge-id",
    )

    async_jobs = list(pdu_online_edit.async_jobs.order_by("job_name"))

    assert [job.job_name for job in async_jobs] == ["generate_edit_data", "merge"]
    assert [job.curr_async_result_id for job in async_jobs] == ["generate-id", "merge-id"]


def test_pdu_online_edit_combined_status_maps_missing_job_to_not_scheduled() -> None:
    pdu_online_edit = PDUOnlineEditFactory(status=PDUOnlineEdit.Status.PENDING_CREATE)
    AsyncJob.objects.create(
        program=pdu_online_edit.program,
        content_object=pdu_online_edit,
        job_name="generate_edit_data",
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.generate_pdu_online_edit_data_task_action",
        config={"pdu_online_edit_id": pdu_online_edit.pk},
        group_key=f"generate_pdu_online_edit_data_task:{pdu_online_edit.pk}",
        curr_async_result_id="generate-id",
    )

    with patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=AsyncJob.MISSING):
        assert pdu_online_edit.combined_status == PDUOnlineEdit.Status.NOT_SCHEDULED_CREATE


def test_pdu_online_edit_combined_status_uses_async_job_started_state_for_merge() -> None:
    pdu_online_edit = PDUOnlineEditFactory(status=PDUOnlineEdit.Status.PENDING_MERGE)
    AsyncJob.objects.create(
        program=pdu_online_edit.program,
        content_object=pdu_online_edit,
        job_name="merge",
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.merge_pdu_online_edit_task_action",
        config={"pdu_online_edit_id": pdu_online_edit.pk},
        group_key=f"merge_pdu_online_edit_task:{pdu_online_edit.pk}",
        curr_async_result_id="merge-id",
    )

    with patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=AsyncJob.STARTED):
        assert pdu_online_edit.combined_status == PDUOnlineEdit.Status.MERGING
