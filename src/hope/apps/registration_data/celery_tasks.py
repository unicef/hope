from contextlib import contextmanager
import logging
from typing import TYPE_CHECKING, Any

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from hope.apps.core.celery import app
from hope.apps.registration_data.exceptions import (
    AlreadyRunningError,
    WrongStatusError,
)
from hope.apps.registration_data.tasks.deduplicate import HardDocumentDeduplication
from hope.apps.registration_data.tasks.rdi_program_population_create import (
    RdiProgramPopulationCreateTask,
)
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import AsyncRetryJob, Document, Program, RegistrationDataImport

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


def handle_rdi_exception(rdi_id: str, e: BaseException) -> None:
    try:
        from sentry_sdk import capture_exception

        err = capture_exception(e)
    except Exception as exc:  # pragma: no cover
        err = "N/A"  # pragma: no cover
        logger.exception(exc)  # pragma: no cover
    rdi = RegistrationDataImport.objects.get(id=rdi_id)
    rdi.status = RegistrationDataImport.IMPORT_ERROR
    rdi.sentry_id = err
    rdi.error_message = str(e)
    rdi.save(update_fields=["status", "sentry_id", "error_message"])


@contextmanager
def locked_cache(key: int | str, timeout: int = 60 * 60 * 24) -> Any:
    now = timezone.now()
    acquired = False
    try:
        acquired = cache.get_or_set(key, now, timeout=timeout) == now

        if acquired:
            logger.info(f"Task with key {key} started")
            yield True
        else:
            logger.info(f"Task with key {key} is already running")
            yield False
    finally:
        if acquired:
            cache.delete(key)
            logger.info(f"Task with key {key} finished")


def registration_xlsx_import_async_task_action(job: AsyncRetryJob) -> bool:
    try:
        from hope.apps.registration_data.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )
        from hope.apps.registration_data.tasks.rdi_xlsx_people_create import (
            RdiXlsxPeopleCreateTask,
        )
        from hope.models import Program

        registration_data_import_id = job.config["registration_data_import_id"]
        import_data_id = job.config["import_data_id"]
        business_area_id = job.config["business_area_id"]
        program_id = job.config["program_id"]

        with locked_cache(key=f"registration_xlsx_import_async_task-{registration_data_import_id}") as locked:
            if not locked:
                raise AlreadyRunningError(
                    f"Task with key registration_xlsx_import_async_task"
                    f" {registration_data_import_id} is already running"
                )
            rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)
            set_sentry_business_area_tag(rdi.business_area.name)
            if rdi.status not in (
                RegistrationDataImport.IMPORT_SCHEDULED,
                RegistrationDataImport.IMPORT_ERROR,
            ):
                raise WrongStatusError("Rdi is not in status IMPORT_SCHEDULED while trying to import")
            rdi.status = RegistrationDataImport.IMPORTING
            rdi.save()

            program = Program.objects.get(id=program_id)
            is_social_worker_program = program.is_social_worker_program

            if is_social_worker_program:
                RdiXlsxPeopleCreateTask().execute(
                    registration_data_import_id=registration_data_import_id,
                    import_data_id=import_data_id,
                    business_area_id=business_area_id,
                    program_id=str(program_id),
                )
            else:
                RdiXlsxCreateTask().execute(
                    registration_data_import_id=registration_data_import_id,
                    import_data_id=import_data_id,
                    business_area_id=business_area_id,
                    program_id=str(program_id),
                )
            return True
    except (WrongStatusError, AlreadyRunningError) as exc:
        logger.info(str(exc))
        return True
    except Exception as exc:  # noqa
        handle_rdi_exception(job.config["registration_data_import_id"], exc)
        raise


def registration_xlsx_import_async_task(
    registration_data_import_id: str,
    import_data_id: str,
    business_area_id: str,
    program_id: str,
) -> None:
    config = {
        "registration_data_import_id": registration_data_import_id,
        "import_data_id": import_data_id,
        "business_area_id": business_area_id,
        "program_id": program_id,
    }
    AsyncRetryJob.queue_task(
        job_name=registration_xlsx_import_async_task.__name__,
        program_id=program_id,
        action="hope.apps.registration_data.celery_tasks.registration_xlsx_import_async_task_action",
        config=config,
        group_key=f"registration_xlsx_import_async_task:{registration_data_import_id}",
        description=f"Import registration xlsx for {registration_data_import_id}",
    )


def registration_program_population_import_async_task_action(job: AsyncRetryJob) -> bool:
    try:
        registration_data_import_id = job.config["registration_data_import_id"]
        cache_key = f"registration_program_population_import_async_task-{registration_data_import_id}"
        with locked_cache(key=cache_key) as locked:
            if not locked:
                raise AlreadyRunningError(f"Task with key {cache_key} is already running")

            rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)
            set_sentry_business_area_tag(rdi.business_area.name)
            if rdi.status not in (
                RegistrationDataImport.IMPORT_SCHEDULED,
                RegistrationDataImport.IMPORT_ERROR,
            ):
                raise WrongStatusError("Rdi is not in status IMPORT_SCHEDULED while trying to import")
            rdi.status = RegistrationDataImport.IMPORTING
            rdi.save()

            RdiProgramPopulationCreateTask().execute(
                registration_data_import_id=registration_data_import_id,
                business_area_id=job.config["business_area_id"],
                import_from_program_id=job.config["import_from_program_id"],
                import_to_program_id=job.config["import_to_program_id"],
            )
            return True
    except (WrongStatusError, AlreadyRunningError) as exc:
        logger.info(str(exc))
        return True
    except RegistrationDataImport.DoesNotExist:
        raise
    except Exception as exc:  # noqa
        logger.warning(exc)
        handle_rdi_exception(job.config["registration_data_import_id"], exc)
        raise


def registration_program_population_import_async_task(
    registration_data_import_id: str,
    business_area_id: str,
    import_from_program_id: str,
    import_to_program_id: str,
) -> None:
    config = {
        "registration_data_import_id": registration_data_import_id,
        "business_area_id": business_area_id,
        "import_from_program_id": import_from_program_id,
        "import_to_program_id": import_to_program_id,
    }
    AsyncRetryJob.queue_task(
        job_name=registration_program_population_import_async_task.__name__,
        program_id=import_to_program_id,
        action="hope.apps.registration_data.celery_tasks.registration_program_population_import_async_task_action",
        config=config,
        group_key=f"registration_program_population_import_async_task:{registration_data_import_id}",
        description=f"Import registration program population for {registration_data_import_id}",
    )


def registration_kobo_import_async_task_action(job: AsyncRetryJob) -> None:
    try:
        from hope.apps.registration_data.tasks.rdi_kobo_create import (
            RdiKoboCreateTask,
        )
        from hope.models import BusinessArea

        registration_data_import_id = job.config["registration_data_import_id"]
        import_data_id = job.config["import_data_id"]
        business_area_id = job.config["business_area_id"]
        program_id = job.config["program_id"]

        set_sentry_business_area_tag(BusinessArea.objects.get(pk=business_area_id).name)
        RdiKoboCreateTask(
            registration_data_import_id=registration_data_import_id,
            business_area_id=business_area_id,
        ).execute(
            import_data_id=import_data_id,
            program_id=program_id,
        )
    except Exception as exc:  # noqa
        logger.warning(exc)
        handle_rdi_exception(job.config["registration_data_import_id"], exc)
        raise


def registration_kobo_import_async_task(
    registration_data_import_id: str,
    import_data_id: str,
    business_area_id: str,
    program_id: str,
) -> None:
    config = {
        "registration_data_import_id": registration_data_import_id,
        "import_data_id": import_data_id,
        "business_area_id": business_area_id,
        "program_id": program_id,
    }
    AsyncRetryJob.queue_task(
        job_name=registration_kobo_import_async_task.__name__,
        program_id=program_id,
        action="hope.apps.registration_data.celery_tasks.registration_kobo_import_async_task_action",
        config=config,
        group_key=f"registration_kobo_import_async_task:{registration_data_import_id}",
        description=f"Import Kobo registration data for {registration_data_import_id}",
    )


def registration_kobo_import_hourly_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from hope.apps.registration_data.tasks.rdi_kobo_create import (
        RdiKoboCreateTask,
    )

    not_started_rdi = (
        RegistrationDataImport.objects.select_related("business_area", "program", "import_data")
        .filter(status=RegistrationDataImport.LOADING)
        .first()
    )
    if not_started_rdi is None:
        return
    business_area = not_started_rdi.business_area
    program_id = not_started_rdi.program.id
    set_sentry_business_area_tag(business_area.name)

    RdiKoboCreateTask(
        registration_data_import_id=str(not_started_rdi.id),
        business_area_id=str(business_area.id),
    ).execute(
        import_data_id=str(not_started_rdi.import_data.id),
        program_id=str(program_id),
    )


@app.task()
def registration_kobo_import_hourly_async_task() -> None:
    AsyncRetryJob.queue_task(
        job_name=registration_kobo_import_hourly_async_task.__name__,
        action="hope.apps.registration_data.celery_tasks.registration_kobo_import_hourly_async_task_action",
        config={},
        group_key="registration_kobo_import_hourly_async_task",
        description="Import hourly Kobo registration data",
    )


def merge_registration_data_import_async_task_action(job: AsyncRetryJob) -> bool:
    registration_data_import_id = job.config["registration_data_import_id"]
    logger.info(
        f"merge_registration_data_import_async_task started for"
        f" registration_data_import_id: {registration_data_import_id}"
    )
    with locked_cache(key=f"merge_registration_data_import_async_task-{registration_data_import_id}") as locked:
        if not locked:
            return True
        from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask
        from hope.models import RegistrationDataImport

        try:
            obj_hct = RegistrationDataImport.objects.get(id=registration_data_import_id)
            set_sentry_business_area_tag(obj_hct.business_area.name)

            obj_hct.status = RegistrationDataImport.MERGING
            obj_hct.save(update_fields=["status"])

            RdiMergeTask().execute(registration_data_import_id)
        except Exception as e:  # noqa
            logger.exception(e)
            RegistrationDataImport.objects.filter(
                id=registration_data_import_id,
            ).update(status=RegistrationDataImport.MERGE_ERROR, error_message=str(e))
            raise

    logger.info(
        f"merge_registration_data_import_async_task finished for"
        f" registration_data_import_id: {registration_data_import_id}"
    )
    return True


def merge_registration_data_import_async_task(registration_data_import: RegistrationDataImport) -> None:
    registration_data_import_id = str(registration_data_import.id)
    config = {"registration_data_import_id": registration_data_import_id}
    AsyncRetryJob.queue_task(
        job_name=merge_registration_data_import_async_task.__name__,
        program=registration_data_import.program,
        action="hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task_action",
        config=config,
        group_key=f"merge_registration_data_import_async_task:{registration_data_import_id}",
        description=f"Merge registration data import {registration_data_import_id}",
    )


def rdi_deduplication_async_task_action(job: AsyncRetryJob) -> None:
    try:
        from hope.apps.registration_data.tasks.deduplicate import DeduplicateTask

        rdi_obj = RegistrationDataImport.objects.get(id=job.config["registration_data_import_id"])
        program_id = rdi_obj.program.id
        set_sentry_business_area_tag(rdi_obj.business_area.slug)
        with transaction.atomic():
            DeduplicateTask(rdi_obj.business_area.slug, program_id).deduplicate_pending_individuals(
                registration_data_import=rdi_obj
            )
    except Exception as exc:  # noqa
        handle_rdi_exception(job.config["registration_data_import_id"], exc)
        raise


def rdi_deduplication_async_task(registration_data_import: RegistrationDataImport) -> None:
    config = {"registration_data_import_id": str(registration_data_import.id)}
    AsyncRetryJob.queue_task(
        job_name=rdi_deduplication_async_task.__name__,
        program=registration_data_import.program,
        action="hope.apps.registration_data.celery_tasks.rdi_deduplication_async_task_action",
        config=config,
        group_key=f"rdi_deduplication_async_task:{str(registration_data_import.id)}",
        description=f"Deduplicate registration data import {str(registration_data_import.id)}",
    )


def pull_kobo_submissions_async_task_action(job: AsyncRetryJob) -> dict:
    from hope.models import KoboImportData

    kobo_import_data = KoboImportData.objects.get(id=job.config["import_data_id"])
    program = Program.objects.get(id=job.config["program_id"])
    set_sentry_business_area_tag(kobo_import_data.business_area_slug)
    from hope.apps.registration_data.tasks.pull_kobo_submissions import (
        PullKoboSubmissions,
    )

    try:
        return PullKoboSubmissions().execute(kobo_import_data, program)
    except Exception as exc:  # noqa
        KoboImportData.objects.filter(
            id=kobo_import_data.id,
        ).update(status=KoboImportData.STATUS_ERROR, error=str(exc))
        raise


def pull_kobo_submissions_async_task(import_data_id: str, program_id: str) -> None:
    config = {
        "import_data_id": import_data_id,
        "program_id": program_id,
    }
    AsyncRetryJob.queue_task(
        job_name=pull_kobo_submissions_async_task.__name__,
        program_id=program_id,
        action="hope.apps.registration_data.celery_tasks.pull_kobo_submissions_async_task_action",
        config=config,
        group_key=f"pull_kobo_submissions_async_task:{import_data_id}",
        description=f"Pull Kobo submissions for import data {import_data_id}",
    )


def validate_xlsx_import_async_task_action(job: AsyncRetryJob) -> dict:
    from hope.apps.registration_data.tasks.validate_xlsx_import import (
        ValidateXlsxImport,
    )
    from hope.models import ImportData, Program

    import_data = ImportData.objects.get(id=job.config["import_data_id"])
    program = Program.objects.get(id=job.config["program_id"])
    set_sentry_business_area_tag(import_data.business_area_slug)
    try:
        return ValidateXlsxImport().execute(import_data, program)
    except Exception as exc:  # noqa
        ImportData.objects.filter(
            id=import_data.id,
        ).update(status=ImportData.STATUS_ERROR, error=str(exc))
        raise


def validate_xlsx_import_async_task(import_data_id: str, program_id: str) -> None:
    config = {
        "import_data_id": import_data_id,
        "program_id": program_id,
    }
    AsyncRetryJob.queue_task(
        job_name=validate_xlsx_import_async_task.__name__,
        program_id=program_id,
        action="hope.apps.registration_data.celery_tasks.validate_xlsx_import_async_task_action",
        config=config,
        group_key=f"validate_xlsx_import_async_task:{import_data_id}",
        description=f"Validate XLSX import {import_data_id}",
    )


def check_and_set_taxid(queryset: "QuerySet") -> dict:
    qs = queryset.filter(unique_field__isnull=True)
    results = {"updated": [], "processed": [], "errors": []}
    for record in qs.iterator(chunk_size=1000):
        try:
            for individual in record.fields["individuals"]:
                if individual["role_i_c"] == "y":
                    record.unique_field = individual["tax_id_no_i_c"]
                    record.save(update_fields=["unique_field"])
                    results["updated"].append(record.pk)
                    break
            results["processed"].append(record.pk)

        except Exception as e:  # noqa
            results["errors"].append(f"Record: {record.pk} - {e.__class__.__name__}: {str(e)}")
    return results


def deduplicate_documents_for_rdi(rdi_id: str) -> bool:
    with locked_cache(key="deduplicate_documents") as locked:
        if not locked:
            return True
        rdi = RegistrationDataImport.objects.get(id=rdi_id)
        with transaction.atomic():
            documents_query = Document.objects.filter(
                status=Document.STATUS_PENDING, individual__registration_data_import=rdi
            )
            HardDocumentDeduplication().deduplicate(
                documents_query,
                registration_data_import=rdi,
            )
    return True


def deduplication_engine_process_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.registration_data.services.biometric_deduplication import (
        BiometricDeduplicationService,
    )

    program = Program.objects.get(id=job.config["program_id"])
    set_sentry_business_area_tag(program.business_area.name)
    BiometricDeduplicationService().upload_and_process_deduplication_set(program)


def deduplication_engine_process_async_task(program_id: str) -> None:
    config = {"program_id": program_id}
    AsyncRetryJob.queue_task(
        job_name=deduplication_engine_process_async_task.__name__,
        program_id=program_id,
        action="hope.apps.registration_data.celery_tasks.deduplication_engine_process_async_task_action",
        config=config,
        group_key=f"deduplication_engine_process_async_task:{program_id}",
        description=f"Process biometric deduplication for program {program_id}",
    )


def fetch_biometric_deduplication_results_and_process_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.registration_data.services.biometric_deduplication import (
        BiometricDeduplicationService,
    )

    program = Program.objects.get(id=job.config["program_id"])
    rdi_id = job.config.get("rdi_id")
    rdi = RegistrationDataImport.objects.get(id=rdi_id) if rdi_id else None
    set_sentry_business_area_tag(program.business_area.name)

    service = BiometricDeduplicationService()
    service.fetch_biometric_deduplication_results_and_process(program, rdi)


def fetch_biometric_deduplication_results_and_process_async_task(
    program_id: str,
    rdi_id: str | None = None,
) -> None:
    config = {
        "program_id": program_id,
        "rdi_id": rdi_id,
    }
    AsyncRetryJob.queue_task(
        job_name=fetch_biometric_deduplication_results_and_process_async_task.__name__,
        program_id=program_id,
        action="hope.apps.registration_data.celery_tasks.fetch_biometric_deduplication_results_and_process_async_task_action",
        config=config,
        group_key=f"fetch_biometric_deduplication_results_and_process_async_task:{program_id}:{rdi_id}",
        description=f"Fetch biometric deduplication results for program {program_id}",
    )
