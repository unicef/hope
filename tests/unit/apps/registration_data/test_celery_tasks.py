from unittest.mock import Mock, patch

from celery.exceptions import Retry
from django.db import Error
from openpyxl.utils.exceptions import InvalidFileException
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    ImportDataFactory,
    KoboImportDataFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.core.celery_tasks import async_job_task, async_retry_job_task
from hope.apps.registration_data.celery_tasks import (
    check_and_set_taxid,
    deduplicate_documents_for_rdi,
    deduplication_engine_process_async_task,
    fetch_biometric_deduplication_results_and_process_async_task,
    merge_registration_data_import_async_task,
    pull_kobo_submissions_async_task,
    pull_kobo_submissions_async_task_action,
    rdi_deduplication_async_task,
    registration_kobo_import_async_task,
    registration_kobo_import_async_task_action,
    registration_kobo_import_hourly_async_task,
    registration_kobo_import_hourly_async_task_action,
    validate_xlsx_import_async_task,
    validate_xlsx_import_async_task_action,
)
from hope.apps.registration_data.tasks.pull_kobo_submissions import PullKoboSubmissions
from hope.models import AsyncJob, AsyncRetryJob, ImportData, KoboImportData, Program, RegistrationDataImport

pytestmark = pytest.mark.django_db


def queue_and_run_async_task(task: object, *args: object, **kwargs: object) -> object:
    with patch("hope.apps.registration_data.celery_tasks.AsyncJob.queue", autospec=True):
        task(*args, **kwargs)
    job = AsyncJob.objects.latest("pk")
    return async_job_task.run(job._meta.label_lower, job.pk, job.version)


def queue_and_run_retry_task(task: object, *args: object, **kwargs: object) -> object:
    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue", autospec=True):
        task(*args, **kwargs)
    job = AsyncRetryJob.objects.latest("pk")
    return async_retry_job_task.run(job._meta.label_lower, job.pk, job.version)


VALID_JSON = [
    {
        "_notes": [],
        "wash_questions/score_num_items": "8",
        "wash_questions/bed_hhsize": "NaN",
        "monthly_income_questions/total_inc_h_f": "0",
        "household_questions/m_0_5_age_group_h_c": "0",
        "_xform_id_string": "aPkhoRMrkkDwgsvWuwi39s",
        "_bamboo_dataset_id": "",
        "_tags": [],
        "health_questions/pregnant_member_h_c": "0",
        "health_questions/start": "2020-04-28T17:34:22.979+02:00",
        "health_questions/end": "2020-05-28T18:56:33.979+02:00",
        "household_questions/first_registration_date_h_c": "2020-07-18",
        "household_questions/f_0_5_disability_h_c": "0",
        "household_questions/size_h_c": "1",
        "household_questions/country_h_c": "AFG",
        "monthly_expenditures_questions/total_expense_h_f": "0",
        "individual_questions": [
            {
                "individual_questions/preferred_language_i_c": "pl-pl",
                "individual_questions/role_i_c": "primary",
                "individual_questions/age": "40",
                "individual_questions/first_registration_date_i_c": "2020-07-18",
                "individual_questions/more_information/marital_status_i_c": "married",
                "individual_questions/individual_index": "1",
                "individual_questions/birth_date_i_c": "1980-07-18",
                "individual_questions/estimated_birth_date_i_c": "0",
                "individual_questions/relationship_i_c": "head",
                "individual_questions/gender_i_c": "male",
                "individual_questions/individual_vulnerabilities/disability_i_c": "not disabled",
                "individual_questions/full_name_i_c": "Test Testowy",
                "individual_questions/is_only_collector": "NO",
                "individual_questions/mas_treatment_i_f": "1",
                "individual_questions/arm_picture_i_f": "signature-17_32_52.png",
                "individual_questions/identification/tax_id_no_i_c": "45638193",
                "individual_questions/identification/tax_id_issuer_i_c": "UKR",
            }
        ],
        "wash_questions/score_bed": "5",
        "meta/instanceID": "uuid:512ca816-5cab-45a6-a676-1f47cfe7658e",
        "wash_questions/blanket_hhsize": "NaN",
        "household_questions/f_adults_disability_h_c": "0",
        "wash_questions/score_childclothes": "5",
        "household_questions/org_enumerator_h_c": "UNICEF",
        "household_questions/specific_residence_h_f": "returnee",
        "household_questions/org_name_enumerator_h_c": "Test",
        "household_questions/name_enumerator_h_c": "Test",
        "household_questions/consent_h_c": "0",
        "household_questions/consent_sharing_h_c": "UNICEF",
        "household_questions/m_12_17_age_group_h_c": "0",
        "household_questions/f_adults_h_c": "0",
        "household_questions/f_12_17_disability_h_c": "0",
        "household_questions/f_0_5_age_group_h_c": "0",
        "household_questions/m_6_11_age_group_h_c": "0",
        "wash_questions/score_womencloth": "5",
        "household_questions/f_12_17_age_group_h_c": "0",
        "wash_questions/score_jerrycan": "5",
        "start": "2020-05-28T17:32:43.054+02:00",
        "_attachments": [
            {
                "mimetype": "image/png",
                "download_small_url": "https://kc.humanitarianresponse.info/media/small?"
                "media_file=wnosal%2Fattachments%"
                "2Fb83407aca1d647a5bf65a3383ee761d4%2F512ca816-5cab-45a6-a676-1f47cfe7658e"
                "%2Fsignature-17_32_52.png",
                "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal%"
                "2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2F512ca816-5cab-45a6-a676-1f47cfe7658e%2Fsignature-17_32_52.png",
                "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2F512ca816-5cab-45a6-a676-1f47cfe7658e%2Fsignature-17_32_52.png",
                "filename": "wnosal/attachments/b83407aca1d647a5bf65a3383ee761d4/"
                "512ca816-5cab-45a6-a676-1f47cfe7658e/signature-17_32_52.png",
                "instance": 101804069,
                "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2F512ca816-5cab-45a6-a676-1f47cfe7658e%2Fsignature-17_32_52.png",
                "id": 34814249,
                "xform": 549831,
            }
        ],
        "_status": "submitted_via_web",
        "__version__": "vrBoKHPPCWpiRNvCbmnXCK",
        "household_questions/m_12_17_disability_h_c": "0",
        "wash_questions/score_tool": "5",
        "wash_questions/total_liter_yesterday_h_f": "0",
        "wash_questions/score_NFI_h_f": "5",
        "food_security_questions/FCS_h_f": "NaN",
        "wash_questions/jerrycan_hhsize": "NaN",
        "enumerator/name_enumerator": "Test",
        "wash_questions/score_bassin": "5",
        "_validation_status": {},
        "_uuid": "512ca816-5cab-45a6-a676-1f47cfe7658e",
        "household_questions/m_adults_h_c": "1",
        "consent/consent_sign_h_c": "signature-17_32_52.png",
        "wash_questions/score_total": "40",
        "_submitted_by": None,
        "individual_questions_count": "1",
        "end": "2020-05-28T17:34:22.979+02:00",
        "household_questions/pregnant_h_c": "0",
        "household_questions/m_6_11_disability_h_c": "0",
        "household_questions/m_0_5_disability_h_c": "0",
        "formhub/uuid": "b83407aca1d647a5bf65a3383ee761d4",
        "enumerator/org_enumerator": "unicef",
        "monthly_income_questions/round_total_income_h_f": "0",
        "wash_questions/score_cookingpot": "5",
        "household_questions/m_adults_disability_h_c": "0",
        "_submission_time": "2020-05-28T15:34:37",
        "household_questions/household_location/residence_status_h_c": "refugee",
        "_geolocation": [None, None],
        "monthly_expenditures_questions/round_total_expense_h_f": "0",
        "deviceid": "ee.humanitarianresponse.info:AqAb03KLuEfWXes0",
        "food_security_questions/cereals_tuber_score_h_f": "NaN",
        "household_questions/f_6_11_disability_h_c": "0",
        "wash_questions/score_blanket": "5",
        "household_questions/f_6_11_age_group_h_c": "0",
        "_id": 101804069,
    },
    {
        "_notes": [],
        "wash_questions/score_num_items": "8",
        "wash_questions/bed_hhsize": "NaN",
        "monthly_income_questions/total_inc_h_f": "0",
        "household_questions/m_0_5_age_group_h_c": "0",
        "_xform_id_string": "aPkhoRMrkkDwgsvWuwi39s",
        "_bamboo_dataset_id": "",
        "_tags": [],
        "health_questions/pregnant_member_h_c": "0",
        "health_questions/start": "2020-04-28T17:34:22.979+02:00",
        "health_questions/end": "2020-05-28T18:56:33.979+02:00",
        "household_questions/first_registration_date_h_c": "2020-07-18",
        "household_questions/f_0_5_disability_h_c": "0",
        "household_questions/size_h_c": "1",
        "household_questions/country_h_c": "AFG",
        "monthly_expenditures_questions/total_expense_h_f": "0",
        "individual_questions": [
            {
                "individual_questions/preferred_language_i_c": "pl-pl",
                "individual_questions/role_i_c": "primary",
                "individual_questions/age": "40",
                "individual_questions/first_registration_date_i_c": "2020-07-18",
                "individual_questions/more_information/marital_status_i_c": "married",
                "individual_questions/individual_index": "1",
                "individual_questions/birth_date_i_c": "1980-07-18",
                "individual_questions/estimated_birth_date_i_c": "0",
                "individual_questions/relationship_i_c": "head",
                "individual_questions/gender_i_c": "male",
                "individual_questions/individual_vulnerabilities/disability_i_c": "not disabled",
                "individual_questions/full_name_i_c": "Test Testowy",
                "individual_questions/is_only_collector": "NO",
                "individual_questions/mas_treatment_i_f": "1",
                "individual_questions/arm_picture_i_f": "signature-17_32_52.png",
                "individual_questions/identification/tax_id_no_i_c": "45638193",
                "individual_questions/identification/tax_id_issuer_i_c": "UKR",
            }
        ],
        "wash_questions/score_bed": "5",
        "meta/instanceID": "uuid:512ca816-5cab-45a6-a676-1f47cfe7658e",
        "wash_questions/blanket_hhsize": "NaN",
        "household_questions/f_adults_disability_h_c": "0",
        "wash_questions/score_childclothes": "5",
        "household_questions/org_enumerator_h_c": "UNICEF",
        "household_questions/specific_residence_h_f": "returnee",
        "household_questions/org_name_enumerator_h_c": "Test",
        "household_questions/name_enumerator_h_c": "Test",
        "household_questions/consent_h_c": "0",
        "household_questions/consent_sharing_h_c": "UNICEF",
        "household_questions/m_12_17_age_group_h_c": "0",
        "household_questions/f_adults_h_c": "0",
        "household_questions/f_12_17_disability_h_c": "0",
        "household_questions/f_0_5_age_group_h_c": "0",
        "household_questions/m_6_11_age_group_h_c": "0",
        "wash_questions/score_womencloth": "5",
        "household_questions/f_12_17_age_group_h_c": "0",
        "wash_questions/score_jerrycan": "5",
        "start": "2020-05-28T17:32:43.054+02:00",
        "_attachments": [],
        "_status": "submitted_via_web",
        "__version__": "vrBoKHPPCWpiRNvCbmnXCK",
        "household_questions/m_12_17_disability_h_c": "0",
        "wash_questions/score_tool": "5",
        "wash_questions/total_liter_yesterday_h_f": "0",
        "wash_questions/score_NFI_h_f": "5",
        "food_security_questions/FCS_h_f": "NaN",
        "wash_questions/jerrycan_hhsize": "NaN",
        "enumerator/name_enumerator": "Test",
        "wash_questions/score_bassin": "5",
        "_validation_status": {},
        "_uuid": "512ca816-5cab-45a6-a676-1f47cfe7658e",
        "household_questions/m_adults_h_c": "1",
        "consent/consent_sign_h_c": "signature-17_32_52.png",
        "wash_questions/score_total": "40",
        "_submitted_by": None,
        "individual_questions_count": "1",
        "end": "2020-05-28T17:34:22.979+02:00",
        "household_questions/pregnant_h_c": "0",
        "household_questions/m_6_11_disability_h_c": "0",
        "household_questions/m_0_5_disability_h_c": "0",
        "formhub/uuid": "b83407aca1d647a5bf65a3383ee761d4",
        "enumerator/org_enumerator": "unicef",
        "monthly_income_questions/round_total_income_h_f": "0",
        "wash_questions/score_cookingpot": "5",
        "household_questions/m_adults_disability_h_c": "0",
        "_submission_time": "2020-05-28T15:34:37",
        "household_questions/household_location/residence_status_h_c": "refugee",
        "_geolocation": [None, None],
        "monthly_expenditures_questions/round_total_expense_h_f": "0",
        "deviceid": "ee.humanitarianresponse.info:AqAb03KLuEfWXes0",
        "food_security_questions/cereals_tuber_score_h_f": "NaN",
        "household_questions/f_6_11_disability_h_c": "0",
        "wash_questions/score_blanket": "5",
        "household_questions/f_6_11_age_group_h_c": "0",
        "_id": 23456,
    },
]


@pytest.fixture
def registration_import_context() -> dict[str, object]:
    business_area = BusinessAreaFactory(name="Afghanistan")
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area)
    import_data = ImportDataFactory(
        number_of_households=3,
        number_of_individuals=6,
        business_area_slug=business_area.slug,
    )
    registration_data_import = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        import_data=import_data,
        status=RegistrationDataImport.IN_REVIEW,
    )
    return {
        "business_area": business_area,
        "program": program,
        "import_data": import_data,
        "registration_data_import": registration_data_import,
    }


@patch("hope.apps.registration_data.tasks.rdi_kobo_create.RdiKoboCreateTask")
def test_registration_kobo_import_task_execute_called_once(
    mock_rdi_kobo_create_task: Mock, registration_import_context: dict[str, object]
) -> None:
    registration_data_import = registration_import_context["registration_data_import"]
    import_data = registration_import_context["import_data"]
    business_area = registration_import_context["business_area"]
    program = registration_import_context["program"]

    mock_task_instance = mock_rdi_kobo_create_task.return_value
    queue_and_run_retry_task(
        registration_kobo_import_async_task,
        registration_data_import=registration_data_import,
        import_data_id=str(import_data.id),
        business_area_id=str(business_area.id),
        program_id=str(program.id),
    )
    mock_task_instance.execute.assert_called_once_with(
        import_data_id=str(import_data.id),
        program_id=str(program.id),
    )


@patch("hope.apps.registration_data.celery_tasks.handle_rdi_exception")
@patch("hope.apps.registration_data.celery_tasks.logger.warning")
@patch("hope.apps.registration_data.tasks.rdi_kobo_create.RdiKoboCreateTask.execute")
def test_registration_kobo_import_task_action_handles_exception(
    mock_execute: Mock,
    mock_warning: Mock,
    mock_handle_rdi_exception: Mock,
    registration_import_context: dict[str, object],
) -> None:
    registration_data_import = registration_import_context["registration_data_import"]
    import_data = registration_import_context["import_data"]
    business_area = registration_import_context["business_area"]
    program = registration_import_context["program"]
    job = AsyncRetryJob(
        config={
            "registration_data_import_id": str(registration_data_import.id),
            "import_data_id": str(import_data.id),
            "business_area_id": str(business_area.id),
            "program_id": str(program.id),
        }
    )
    exc = RuntimeError("kobo import failed")
    mock_execute.side_effect = exc

    with pytest.raises(RuntimeError, match="kobo import failed"):
        registration_kobo_import_async_task_action(job)

    mock_warning.assert_called_once_with(exc)
    mock_handle_rdi_exception.assert_called_once_with(str(registration_data_import.id), exc)


@patch("hope.apps.registration_data.tasks.rdi_kobo_create.RdiKoboCreateTask")
def test_registration_kobo_import_hourly_task_action_runs(
    mock_rdi_kobo_create_task: Mock,
) -> None:
    business_area = BusinessAreaFactory(name="Afghanistan")
    program = ProgramFactory(business_area=business_area)
    import_data = ImportDataFactory(business_area_slug=business_area.slug)
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        import_data=import_data,
        status=RegistrationDataImport.LOADING,
    )

    registration_kobo_import_hourly_async_task_action()

    mock_rdi_kobo_create_task.return_value.execute.assert_called_once_with(
        import_data_id=str(import_data.id),
        program_id=str(program.id),
    )
    mock_rdi_kobo_create_task.assert_called_once_with(
        registration_data_import_id=str(rdi.id),
        business_area_id=str(business_area.id),
    )


@patch("hope.apps.registration_data.tasks.rdi_kobo_create.RdiKoboCreateTask")
def test_registration_kobo_import_hourly_task_action_returns_when_no_loading_rdi(
    mock_rdi_kobo_create_task: Mock,
) -> None:
    registration_kobo_import_hourly_async_task_action()

    mock_rdi_kobo_create_task.assert_not_called()


def test_registration_kobo_import_task_queues_retry_job_with_rdi_content_object() -> None:
    business_area = BusinessAreaFactory(name="Afghanistan")
    program = ProgramFactory(business_area=business_area)
    import_data = ImportDataFactory(business_area_slug=business_area.slug)
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        import_data=import_data,
    )

    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        registration_kobo_import_async_task(
            registration_data_import=rdi,
            import_data_id=str(import_data.id),
            business_area_id=str(business_area.id),
            program_id=str(program.id),
        )

    job = AsyncRetryJob.objects.latest("pk")
    assert job.content_object == rdi
    assert job.job_name == "registration_kobo_import_async_task"
    assert job.action == "hope.apps.registration_data.celery_tasks.registration_kobo_import_async_task_action"
    assert job.config == {
        "registration_data_import_id": str(rdi.id),
        "import_data_id": str(import_data.id),
        "business_area_id": str(business_area.id),
        "program_id": str(program.id),
    }
    mock_queue.assert_called_once_with(job)


def test_registration_kobo_import_hourly_task_queues_retry_job() -> None:
    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        registration_kobo_import_hourly_async_task()

    job = AsyncRetryJob.objects.latest("pk")
    assert job.job_name == "registration_kobo_import_hourly_async_task"
    assert job.action == "hope.apps.registration_data.celery_tasks.registration_kobo_import_hourly_async_task_action"
    assert job.config == {}
    assert job.group_key == "registration_kobo_import_hourly_async_task"
    assert job.description == "Import hourly Kobo registration data"
    mock_queue.assert_called_once_with(job)


@patch("hope.apps.registration_data.tasks.rdi_merge.RdiMergeTask")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
def test_merge_registration_data_import_task_exception(
    mock_retry: Mock,
    mock_rdi_merge_task: Mock,
    registration_import_context: dict[str, object],
) -> None:
    registration_data_import = registration_import_context["registration_data_import"]

    mock_rdi_merge_task_instance = mock_rdi_merge_task.return_value
    mock_rdi_merge_task_instance.execute.side_effect = Error("Test Exception")
    mock_retry.side_effect = Retry("retry")
    assert registration_data_import.status == RegistrationDataImport.IN_REVIEW

    with pytest.raises(Retry):
        queue_and_run_retry_task(
            merge_registration_data_import_async_task,
            registration_data_import=registration_data_import,
        )
    registration_data_import.refresh_from_db()

    assert registration_data_import.status == RegistrationDataImport.MERGE_ERROR
    assert registration_data_import.error_message == "Test Exception"


@patch("hope.apps.registration_data.tasks.rdi_merge.RdiMergeTask")
def test_merge_registration_data_import_task(
    mock_rdi_merge_task: Mock, registration_import_context: dict[str, object]
) -> None:
    registration_data_import = registration_import_context["registration_data_import"]

    mock_rdi_merge_task_instance = mock_rdi_merge_task.return_value
    assert registration_data_import.status == RegistrationDataImport.IN_REVIEW

    queue_and_run_retry_task(
        merge_registration_data_import_async_task,
        registration_data_import=registration_data_import,
    )

    mock_rdi_merge_task_instance.execute.assert_called_once()


def test_merge_registration_data_import_task_queues_retry_job_with_rdi_content_object(
    registration_import_context: dict[str, object],
) -> None:
    registration_data_import = registration_import_context["registration_data_import"]

    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        merge_registration_data_import_async_task(registration_data_import=registration_data_import)

    job = AsyncRetryJob.objects.latest("pk")
    assert job.content_object == registration_data_import
    assert job.job_name == "merge_registration_data_import_async_task"
    assert job.action == "hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task_action"
    assert job.config == {"registration_data_import_id": str(registration_data_import.id)}
    mock_queue.assert_called_once_with(job)


@patch("hope.apps.registration_data.celery_tasks.locked_cache")
def test_merge_registration_data_import_task_returns_true_when_lock_not_acquired(
    mock_locked_cache: Mock,
    registration_import_context: dict[str, object],
) -> None:
    registration_data_import = registration_import_context["registration_data_import"]
    mock_locked_cache.return_value.__enter__.return_value = False

    result = queue_and_run_retry_task(
        merge_registration_data_import_async_task,
        registration_data_import=registration_data_import,
    )

    assert result is True


@patch("hope.apps.registration_data.tasks.deduplicate.DeduplicateTask")
@patch("hope.apps.core.celery_tasks.async_retry_job_task.retry")
def test_rdi_deduplication_task_exception(
    mock_retry: Mock,
    mock_deduplicate_task: Mock,
    registration_import_context: dict[str, object],
) -> None:
    registration_data_import = registration_import_context["registration_data_import"]
    mock_deduplicate_task_task_instance = mock_deduplicate_task.return_value
    mock_deduplicate_task_task_instance.deduplicate_pending_individuals.side_effect = InvalidFileException(
        "Test Exception"
    )
    mock_retry.side_effect = Retry("retry")
    assert registration_data_import.status == RegistrationDataImport.IN_REVIEW

    with pytest.raises(Retry):
        queue_and_run_retry_task(rdi_deduplication_async_task, registration_data_import=registration_data_import)
    registration_data_import.refresh_from_db()

    assert registration_data_import.status == RegistrationDataImport.IMPORT_ERROR


def test_rdi_deduplication_task_queues_retry_job_with_rdi_content_object(
    registration_import_context: dict[str, object],
) -> None:
    registration_data_import = registration_import_context["registration_data_import"]

    with patch("hope.apps.registration_data.celery_tasks.AsyncRetryJob.queue", autospec=True) as mock_queue:
        rdi_deduplication_async_task(registration_data_import=registration_data_import)

    job = AsyncRetryJob.objects.latest("pk")
    assert job.content_object == registration_data_import
    assert job.job_name == "rdi_deduplication_async_task"
    assert job.action == "hope.apps.registration_data.celery_tasks.rdi_deduplication_async_task_action"
    assert job.config == {"registration_data_import_id": str(registration_data_import.id)}
    mock_queue.assert_called_once_with(job)


@patch("hope.apps.registration_data.tasks.pull_kobo_submissions.PullKoboSubmissions")
def test_pull_kobo_submissions_task(
    mock_pull_kobo_submissions_task: Mock, registration_import_context: dict[str, object]
) -> None:
    program = registration_import_context["program"]
    kobo_import_data = KoboImportDataFactory(kobo_asset_id="1234", pull_pictures=True)
    mock_task_instance = mock_pull_kobo_submissions_task.return_value

    queue_and_run_retry_task(pull_kobo_submissions_async_task, str(kobo_import_data.id), str(program.id))

    mock_task_instance.execute.assert_called_once()


@patch("hope.apps.registration_data.tasks.pull_kobo_submissions.PullKoboSubmissions.execute")
def test_pull_kobo_submissions_task_action_sets_error_status_on_exception(
    mock_execute: Mock,
    registration_import_context: dict[str, object],
) -> None:
    program = registration_import_context["program"]
    kobo_import_data = KoboImportDataFactory(
        business_area_slug=registration_import_context["business_area"].slug,
        status=KoboImportData.STATUS_PENDING,
    )
    job = AsyncRetryJob(config={"import_data_id": str(kobo_import_data.id), "program_id": str(program.id)})
    mock_execute.side_effect = RuntimeError("pull failed")

    with pytest.raises(RuntimeError, match="pull failed"):
        pull_kobo_submissions_async_task_action(job)

    kobo_import_data.refresh_from_db()
    assert kobo_import_data.status == KoboImportData.STATUS_ERROR
    assert kobo_import_data.error == "pull failed"


@patch("hope.apps.registration_data.tasks.validate_xlsx_import.ValidateXlsxImport")
def test_validate_xlsx_import_task(
    mock_validate_xlsx_import_task: Mock, registration_import_context: dict[str, object]
) -> None:
    import_data = registration_import_context["import_data"]
    program = registration_import_context["program"]

    mock_task_instance = mock_validate_xlsx_import_task.return_value
    queue_and_run_retry_task(validate_xlsx_import_async_task, str(import_data.id), str(program.id))
    mock_task_instance.execute.assert_called_once()


@patch("hope.apps.registration_data.tasks.validate_xlsx_import.ValidateXlsxImport.execute")
def test_validate_xlsx_import_task_action_sets_error_status_on_exception(
    mock_execute: Mock,
    registration_import_context: dict[str, object],
) -> None:
    import_data = registration_import_context["import_data"]
    program = registration_import_context["program"]
    job = AsyncRetryJob(config={"import_data_id": str(import_data.id), "program_id": str(program.id)})
    mock_execute.side_effect = RuntimeError("validation failed")

    with pytest.raises(RuntimeError, match="validation failed"):
        validate_xlsx_import_async_task_action(job)

    import_data.refresh_from_db()
    assert import_data.status == ImportData.STATUS_ERROR
    assert import_data.error == "validation failed"


def test_check_and_set_taxid_updates_unique_field_from_primary_individual() -> None:
    record = Mock(pk=1, unique_field=None)
    record.fields = {
        "individuals": [
            {"role_i_c": "n", "tax_id_no_i_c": "SKIP"},
            {"role_i_c": "y", "tax_id_no_i_c": "TAX-123"},
        ]
    }
    queryset = Mock()
    queryset.filter.return_value.iterator.return_value = [record]

    result = check_and_set_taxid(queryset)

    assert record.unique_field == "TAX-123"
    record.save.assert_called_once_with(update_fields=["unique_field"])
    assert result == {"updated": [1], "processed": [1], "errors": []}


@patch("hope.apps.registration_data.celery_tasks.locked_cache")
@patch("hope.apps.registration_data.celery_tasks.HardDocumentDeduplication.deduplicate")
def test_deduplicate_documents_for_rdi_returns_early_when_lock_not_acquired(
    mock_deduplicate: Mock,
    mock_locked_cache: Mock,
) -> None:
    mock_locked_cache.return_value.__enter__.return_value = False

    assert deduplicate_documents_for_rdi("rdi-id") is True

    mock_deduplicate.assert_not_called()


@patch("hope.apps.registration_data.celery_tasks.locked_cache")
@patch("hope.apps.registration_data.celery_tasks.HardDocumentDeduplication.deduplicate")
def test_deduplicate_documents_for_rdi_deduplicates_pending_documents_for_rdi(
    mock_deduplicate: Mock,
    mock_locked_cache: Mock,
) -> None:
    mock_locked_cache.return_value.__enter__.return_value = True
    rdi = RegistrationDataImportFactory()
    matching_individual = PendingIndividualFactory(
        registration_data_import=rdi,
        business_area=rdi.business_area,
        program=rdi.program,
    )
    other_rdi = RegistrationDataImportFactory()
    other_individual = PendingIndividualFactory(
        registration_data_import=other_rdi,
        business_area=other_rdi.business_area,
        program=other_rdi.program,
    )
    matching_document = DocumentFactory(
        individual=matching_individual,
        program=rdi.program,
        status="PENDING",
    )
    DocumentFactory(individual=other_individual, program=other_rdi.program, status="PENDING")

    assert deduplicate_documents_for_rdi(str(rdi.id)) is True

    documents_query = mock_deduplicate.call_args.args[0]
    assert list(documents_query.values_list("id", flat=True)) == [matching_document.id]
    assert mock_deduplicate.call_args.kwargs["registration_data_import"] == rdi


@patch("hope.apps.core.kobo.api.KoboAPI.get_project_submissions")
def test_pull_kobo_submissions_execute(
    mock_get_project_submissions: Mock, registration_import_context: dict[str, object]
) -> None:
    business_area = registration_import_context["business_area"]
    program = registration_import_context["program"]
    kobo_import_data_with_pics = KoboImportDataFactory(
        kobo_asset_id="1111",
        business_area_slug=business_area.slug,
        pull_pictures=True,
    )
    mock_get_project_submissions.return_value = VALID_JSON

    resp_1 = PullKoboSubmissions().execute(kobo_import_data_with_pics, program)

    assert str(resp_1["kobo_import_data_id"]) == str(kobo_import_data_with_pics.id)

    kobo_import_data_without_pics = KoboImportDataFactory(
        kobo_asset_id="2222",
        business_area_slug=business_area.slug,
        pull_pictures=False,
    )
    mock_get_project_submissions.return_value = VALID_JSON

    resp_2 = PullKoboSubmissions().execute(kobo_import_data_without_pics, program)

    assert str(resp_2["kobo_import_data_id"]) == str(kobo_import_data_without_pics.id)


@patch.dict(
    "os.environ",
    {
        "DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key",
        "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com",
    },
)
@patch(
    "hope.apps.registration_data.services.biometric_deduplication.BiometricDeduplicationService"
    ".upload_and_process_deduplication_set"
)
def test_deduplication_engine_process_task(
    mock_upload_and_process: Mock,
) -> None:
    program = ProgramFactory(status=Program.ACTIVE, biometric_deduplication_enabled=True, code="code")

    queue_and_run_retry_task(deduplication_engine_process_async_task, str(program.id))

    mock_upload_and_process.assert_called_once_with(program)


@patch.dict(
    "os.environ",
    {
        "DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key",
        "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com",
    },
)
@patch(
    "hope.apps.registration_data.services.biometric_deduplication.BiometricDeduplicationService"
    ".fetch_biometric_deduplication_results_and_process"
)
def test_fetch_biometric_deduplication_results_and_process(
    mock_fetch_biometric_deduplication_results_and_process: Mock,
) -> None:
    program = ProgramFactory(status=Program.ACTIVE, biometric_deduplication_enabled=True, code="code")

    queue_and_run_retry_task(fetch_biometric_deduplication_results_and_process_async_task, str(program.id))

    mock_fetch_biometric_deduplication_results_and_process.assert_called_once_with(program, None)


@patch.dict(
    "os.environ",
    {
        "DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key",
        "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com",
    },
)
@patch(
    "hope.apps.registration_data.services.biometric_deduplication.BiometricDeduplicationService"
    ".fetch_biometric_deduplication_results_and_process"
)
def test_fetch_biometric_deduplication_results_and_process_for_rdi(
    mock_fetch_biometric_deduplication_results_and_process: Mock,
) -> None:
    program = ProgramFactory(status=Program.ACTIVE, biometric_deduplication_enabled=True, code="code")
    rdi = RegistrationDataImportFactory(program=program, business_area=program.business_area)

    queue_and_run_retry_task(fetch_biometric_deduplication_results_and_process_async_task, str(program.id), str(rdi.id))

    mock_fetch_biometric_deduplication_results_and_process.assert_called_once_with(program, rdi)
