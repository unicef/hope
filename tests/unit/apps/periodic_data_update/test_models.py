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
    PDUXlsxTemplateFactory,
    PDUXlsxUploadFactory,
    ProgramFactory,
)
from hope.models import (
    AsyncJob,
    BusinessArea,
    FlexibleAttribute,
    PDUOnlineEdit,
    PDUXlsxTemplate,
    PDUXlsxUpload,
    Program,
)

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
        job_name="generate_pdu_online_edit_data_async_task",
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.generate_pdu_online_edit_data_async_task_action",
        config={"pdu_online_edit_id": pdu_online_edit.pk},
        group_key=f"generate_pdu_online_edit_data_async_task:{pdu_online_edit.pk}",
        curr_async_result_id="generate-id",
    )
    AsyncJob.objects.create(
        program=pdu_online_edit.program,
        content_object=pdu_online_edit,
        job_name="merge_pdu_online_edit_async_task",
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.merge_pdu_online_edit_async_task_action",
        config={"pdu_online_edit_id": pdu_online_edit.pk},
        group_key=f"merge_pdu_online_edit_async_task:{pdu_online_edit.pk}",
        curr_async_result_id="merge-id",
    )

    async_jobs = list(pdu_online_edit.async_jobs.order_by("job_name"))

    assert [job.job_name for job in async_jobs] == [
        "generate_pdu_online_edit_data_async_task",
        "merge_pdu_online_edit_async_task",
    ]
    assert [job.curr_async_result_id for job in async_jobs] == ["generate-id", "merge-id"]


def test_pdu_online_edit_async_jobs_returns_none_for_unsaved_instance() -> None:
    pdu_online_edit = PDUOnlineEditFactory.build()

    assert list(pdu_online_edit.async_jobs) == []


def test_pdu_online_edit_get_async_job_status_prefers_local_revoked_status() -> None:
    pdu_online_edit = PDUOnlineEditFactory()
    job = AsyncJob(local_status=AsyncJob.REVOKED)

    with patch.object(pdu_online_edit, "_get_async_job", return_value=job):
        assert pdu_online_edit._get_async_job_status(PDUOnlineEdit.GENERATE_EDIT_DATA_JOB_NAME) == AsyncJob.REVOKED


def test_pdu_online_edit_combined_status_maps_missing_job_to_not_scheduled() -> None:
    pdu_online_edit = PDUOnlineEditFactory(status=PDUOnlineEdit.Status.PENDING_CREATE)
    AsyncJob.objects.create(
        program=pdu_online_edit.program,
        content_object=pdu_online_edit,
        job_name="generate_pdu_online_edit_data_async_task",
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.generate_pdu_online_edit_data_async_task_action",
        config={"pdu_online_edit_id": pdu_online_edit.pk},
        group_key=f"generate_pdu_online_edit_data_async_task:{pdu_online_edit.pk}",
        curr_async_result_id="generate-id",
    )

    with patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=AsyncJob.MISSING):
        assert pdu_online_edit.combined_status == PDUOnlineEdit.Status.NOT_SCHEDULED_CREATE


def test_pdu_online_edit_combined_status_uses_async_job_started_state_for_merge() -> None:
    pdu_online_edit = PDUOnlineEditFactory(status=PDUOnlineEdit.Status.PENDING_MERGE)
    AsyncJob.objects.create(
        program=pdu_online_edit.program,
        content_object=pdu_online_edit,
        job_name="merge_pdu_online_edit_async_task",
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.merge_pdu_online_edit_async_task_action",
        config={"pdu_online_edit_id": pdu_online_edit.pk},
        group_key=f"merge_pdu_online_edit_async_task:{pdu_online_edit.pk}",
        curr_async_result_id="merge-id",
    )

    with patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=AsyncJob.STARTED):
        assert pdu_online_edit.combined_status == PDUOnlineEdit.Status.MERGING


def test_pdu_xlsx_template_async_jobs_returns_none_for_unsaved_instance() -> None:
    template = PDUXlsxTemplateFactory.build()

    assert list(template.async_jobs) == []


def test_pdu_xlsx_template_async_jobs_returns_related_jobs() -> None:
    template = PDUXlsxTemplateFactory()
    other_template = PDUXlsxTemplateFactory(program=template.program, business_area=template.business_area)
    AsyncJob.objects.create(
        program=template.program,
        content_object=template,
        job_name=PDUXlsxTemplate.EXPORT_JOB_NAME,
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.export_periodic_data_update_export_template_service_async_task_action",
        config={"template_id": template.pk},
        group_key=f"export_periodic_data_update_export_template_service_async_task:{template.pk}",
        curr_async_result_id="template-id",
    )
    AsyncJob.objects.create(
        program=other_template.program,
        content_object=other_template,
        job_name=PDUXlsxTemplate.EXPORT_JOB_NAME,
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.export_periodic_data_update_export_template_service_async_task_action",
        config={"template_id": other_template.pk},
        group_key=f"export_periodic_data_update_export_template_service_async_task:{other_template.pk}",
        curr_async_result_id="other-template-id",
    )

    async_jobs = list(template.async_jobs)

    assert len(async_jobs) == 1
    assert async_jobs[0].curr_async_result_id == "template-id"


def test_pdu_xlsx_template_get_async_job_status_returns_not_scheduled_without_job() -> None:
    template = PDUXlsxTemplateFactory()

    assert (
        template._get_async_job_status(PDUXlsxTemplate.EXPORT_JOB_NAME) == PDUXlsxTemplate.CELERY_STATUS_NOT_SCHEDULED
    )


def test_pdu_xlsx_template_get_async_job_status_prefers_local_canceled_status() -> None:
    template = PDUXlsxTemplateFactory()
    job = AsyncJob(local_status=AsyncJob.CANCELED)

    with patch.object(template, "_get_async_job", return_value=job):
        assert template._get_async_job_status(PDUXlsxTemplate.EXPORT_JOB_NAME) == AsyncJob.CANCELED


def test_pdu_xlsx_template_get_async_job_status_maps_missing_to_not_scheduled() -> None:
    template = PDUXlsxTemplateFactory()
    job = AsyncJob(local_status="")

    with (
        patch.object(template, "_get_async_job", return_value=job),
        patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=AsyncJob.MISSING),
    ):
        assert (
            template._get_async_job_status(PDUXlsxTemplate.EXPORT_JOB_NAME)
            == PDUXlsxTemplate.CELERY_STATUS_NOT_SCHEDULED
        )


def test_pdu_xlsx_template_get_async_job_status_maps_not_scheduled_to_not_scheduled() -> None:
    template = PDUXlsxTemplateFactory()
    job = AsyncJob(local_status="")

    with (
        patch.object(template, "_get_async_job", return_value=job),
        patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=AsyncJob.NOT_SCHEDULED),
    ):
        assert (
            template._get_async_job_status(PDUXlsxTemplate.EXPORT_JOB_NAME)
            == PDUXlsxTemplate.CELERY_STATUS_NOT_SCHEDULED
        )


def test_pdu_xlsx_template_get_async_job_status_returns_regular_task_status() -> None:
    template = PDUXlsxTemplateFactory()
    job = AsyncJob(local_status="")

    with (
        patch.object(template, "_get_async_job", return_value=job),
        patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=AsyncJob.SUCCESS),
    ):
        assert template._get_async_job_status(PDUXlsxTemplate.EXPORT_JOB_NAME) == AsyncJob.SUCCESS


def test_pdu_xlsx_template_get_active_async_job_status_ignores_inactive_status() -> None:
    template = PDUXlsxTemplateFactory()

    with patch.object(template, "_get_async_job_status", return_value=AsyncJob.FAILURE):
        assert (
            template._get_active_async_job_status(PDUXlsxTemplate.EXPORT_JOB_NAME)
            == PDUXlsxTemplate.CELERY_STATUS_NOT_SCHEDULED
        )


def test_pdu_xlsx_template_get_active_async_job_status_returns_scheduled_status() -> None:
    template = PDUXlsxTemplateFactory()

    with patch.object(template, "_get_async_job_status", return_value=AsyncJob.RETRY):
        assert template._get_active_async_job_status(PDUXlsxTemplate.EXPORT_JOB_NAME) == AsyncJob.RETRY


def test_pdu_xlsx_template_combined_status_maps_started_to_exporting() -> None:
    template = PDUXlsxTemplateFactory(status=PDUXlsxTemplate.Status.EXPORTED)

    with patch.object(template, "_get_active_async_job_status", return_value=AsyncJob.STARTED):
        assert template.combined_status == PDUXlsxTemplate.Status.EXPORTING


def test_pdu_xlsx_template_combined_status_maps_pending_to_to_export() -> None:
    template = PDUXlsxTemplateFactory(status=PDUXlsxTemplate.Status.NOT_SCHEDULED)

    with patch.object(template, "_get_active_async_job_status", return_value=AsyncJob.PENDING):
        assert template.combined_status == PDUXlsxTemplate.Status.TO_EXPORT


def test_pdu_xlsx_upload_async_jobs_returns_none_for_unsaved_instance() -> None:
    upload = PDUXlsxUploadFactory.build()

    assert list(upload.async_jobs) == []


def test_pdu_xlsx_upload_async_jobs_returns_related_jobs() -> None:
    upload = PDUXlsxUploadFactory()
    other_upload = PDUXlsxUploadFactory(template=upload.template)
    AsyncJob.objects.create(
        program=upload.template.program,
        content_object=upload,
        job_name=PDUXlsxUpload.IMPORT_JOB_NAME,
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.import_periodic_data_update_async_task_action",
        config={"upload_id": upload.pk},
        group_key=f"import_periodic_data_update_async_task:{upload.pk}",
        curr_async_result_id="upload-id",
    )
    AsyncJob.objects.create(
        program=other_upload.template.program,
        content_object=other_upload,
        job_name=PDUXlsxUpload.IMPORT_JOB_NAME,
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.periodic_data_update.celery_tasks.import_periodic_data_update_async_task_action",
        config={"upload_id": other_upload.pk},
        group_key=f"import_periodic_data_update_async_task:{other_upload.pk}",
        curr_async_result_id="other-upload-id",
    )

    async_jobs = list(upload.async_jobs)

    assert len(async_jobs) == 1
    assert async_jobs[0].curr_async_result_id == "upload-id"


def test_pdu_xlsx_upload_get_async_job_status_prefers_local_revoked_status() -> None:
    upload = PDUXlsxUploadFactory()
    job = AsyncJob(local_status=AsyncJob.REVOKED)

    with patch.object(upload, "_get_async_job", return_value=job):
        assert upload._get_async_job_status(PDUXlsxUpload.IMPORT_JOB_NAME) == AsyncJob.REVOKED


def test_pdu_xlsx_upload_get_async_job_status_maps_missing_to_not_scheduled() -> None:
    upload = PDUXlsxUploadFactory()
    job = AsyncJob(local_status="")

    with (
        patch.object(upload, "_get_async_job", return_value=job),
        patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=AsyncJob.MISSING),
    ):
        assert upload._get_async_job_status(PDUXlsxUpload.IMPORT_JOB_NAME) == PDUXlsxUpload.CELERY_STATUS_NOT_SCHEDULED


def test_pdu_xlsx_upload_get_async_job_status_maps_not_scheduled_to_not_scheduled() -> None:
    upload = PDUXlsxUploadFactory()
    job = AsyncJob(local_status="")

    with (
        patch.object(upload, "_get_async_job", return_value=job),
        patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=AsyncJob.NOT_SCHEDULED),
    ):
        assert upload._get_async_job_status(PDUXlsxUpload.IMPORT_JOB_NAME) == PDUXlsxUpload.CELERY_STATUS_NOT_SCHEDULED


def test_pdu_xlsx_upload_get_async_job_status_returns_regular_task_status() -> None:
    upload = PDUXlsxUploadFactory()
    job = AsyncJob(local_status="")

    with (
        patch.object(upload, "_get_async_job", return_value=job),
        patch.object(AsyncJob, "task_status", new_callable=PropertyMock, return_value=AsyncJob.SUCCESS),
    ):
        assert upload._get_async_job_status(PDUXlsxUpload.IMPORT_JOB_NAME) == AsyncJob.SUCCESS


def test_pdu_xlsx_upload_errors_returns_none_without_error_message() -> None:
    upload = PDUXlsxUploadFactory(error_message="")

    assert upload.errors is None


def test_pdu_xlsx_upload_errors_returns_deserialized_json() -> None:
    upload = PDUXlsxUploadFactory(error_message='{"error": "invalid row"}')

    assert upload.errors == {"error": "invalid row"}
