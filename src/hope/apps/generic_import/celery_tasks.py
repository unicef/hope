import logging
from typing import Any

from django_celery_boost.models import AsyncJobModel
from sentry_sdk import capture_exception

from hope.apps.core.celery import app
from hope.apps.generic_import.generic_upload_service.importer import Importer
from hope.apps.generic_import.generic_upload_service.parsers.xlsx_somalia_parser import (
    XlsxSomaliaParser,
)
from hope.apps.registration_data.celery_tasks import locked_cache
from hope.apps.registration_data.exceptions import AlreadyRunningError
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag
from hope.models import AsyncJob

logger = logging.getLogger(__name__)


def _handle_validation_errors(import_data, rdi, errors, logger) -> None:
    from hope.apps.generic_import.generic_upload_service.importer import format_validation_errors
    from hope.models import ImportData, RegistrationDataImport

    import_data.status = ImportData.STATUS_VALIDATION_ERROR
    import_data.validation_errors = str(errors)
    import_data.save(update_fields=["status", "validation_errors"])

    error_details = format_validation_errors(errors)
    error_message = f"Validation errors ({len(errors)} errors found):\n\n{error_details}"

    rdi.status = RegistrationDataImport.IMPORT_ERROR
    rdi.error_message = error_message
    rdi.save(update_fields=["status", "error_message"])

    logger.warning(f"Import {rdi.id} completed with {len(errors)} validation errors: {error_details}")


def _handle_import_success(import_data, rdi, logger) -> None:
    from hope.models import Household, ImportData, Individual, RegistrationDataImport

    households_count = Household.pending_objects.filter(registration_data_import=rdi).count()
    individuals_count = Individual.pending_objects.filter(registration_data_import=rdi).count()

    import_data.status = ImportData.STATUS_FINISHED
    import_data.number_of_households = households_count
    import_data.number_of_individuals = individuals_count
    import_data.save(update_fields=["status", "number_of_households", "number_of_individuals"])

    rdi.status = RegistrationDataImport.IN_REVIEW
    rdi.number_of_households = households_count
    rdi.number_of_individuals = individuals_count
    rdi.save(update_fields=["status", "number_of_households", "number_of_individuals"])

    logger.info(
        f"Import {rdi.id} completed successfully: {households_count} households, {individuals_count} individuals"
    )


def _process_generic_import(registration_data_import_id: str, import_data_id: str) -> None:
    from hope.models import ImportData, RegistrationDataImport

    with locked_cache(key=f"process_generic_import_task-{registration_data_import_id}") as locked:
        if not locked:
            raise AlreadyRunningError(
                f"Task with key process_generic_import_task-{registration_data_import_id} is already running"
            )

        import_data = ImportData.objects.get(id=import_data_id)
        rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)

        set_sentry_business_area_tag(rdi.business_area.name)

        import_data.status = ImportData.STATUS_RUNNING
        import_data.save(update_fields=["status"])

        rdi.status = RegistrationDataImport.LOADING
        rdi.save(update_fields=["status"])

        parser = XlsxSomaliaParser(business_area=rdi.business_area)
        parser.parse(import_data.file.path)

        importer = Importer(
            registration_data_import=rdi,
            households_data=parser.households_data,
            individuals_data=parser.individuals_data,
            documents_data=parser.documents_data,
            accounts_data=parser.accounts_data,
            identities_data=parser.identities_data,
        )

        errors = importer.import_data()

        if errors:
            _handle_validation_errors(import_data, rdi, errors, logger)
        else:
            _handle_import_success(import_data, rdi, logger)


def _capture_sentry_id(exc: Exception) -> str:
    try:
        return str(capture_exception(exc))
    except Exception:
        logger.exception("Failed to capture Sentry exception")
        return "N/A"


def _update_generic_import_error_status(registration_data_import_id: str, import_data_id: str, exc: Exception) -> None:
    from hope.models import ImportData, RegistrationDataImport

    sentry_id = _capture_sentry_id(exc)

    try:
        import_data = ImportData.objects.get(id=import_data_id)
        import_data.status = ImportData.STATUS_ERROR
        import_data.error = str(exc)
        import_data.save(update_fields=["status", "error"])
    except Exception:
        logger.exception("Failed to update ImportData status")

    try:
        rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)
        rdi.status = RegistrationDataImport.IMPORT_ERROR
        rdi.error_message = str(exc)
        rdi.sentry_id = sentry_id
        rdi.save(update_fields=["status", "error_message", "sentry_id"])
    except Exception:
        logger.exception("Failed to update RegistrationDataImport status")


def process_generic_import_task_action(job: AsyncJob) -> None:
    registration_data_import_id = job.config["registration_data_import_id"]
    import_data_id = job.config["import_data_id"]

    try:
        _process_generic_import(registration_data_import_id, import_data_id)
        if job.errors:
            job.errors = {}
            job.save(update_fields=["errors"])

    except AlreadyRunningError as exc:
        job.errors = {"error": str(exc)}
        job.save(update_fields=["errors"])
        logger.exception("Generic import task already running")
        raise

    except Exception as e:
        logger.exception(f"Error processing generic import {registration_data_import_id}")
        job.errors = {"error": str(e)}
        job.save(update_fields=["errors"])
        _update_generic_import_error_status(registration_data_import_id, import_data_id, e)
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def process_generic_import_task(
    self: Any,
    registration_data_import_id: str,
    import_data_id: str,
) -> None:
    from hope.models import RegistrationDataImport

    rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)
    job = AsyncJob.objects.create(
        owner=rdi.imported_by,
        program=rdi.program,
        type=AsyncJobModel.JobType.JOB_TASK,
        action="hope.apps.generic_import.celery_tasks.process_generic_import_task_action",
        config={
            "registration_data_import_id": str(registration_data_import_id),
            "import_data_id": str(import_data_id),
        },
        group_key=f"process_generic_import_task:{registration_data_import_id},{import_data_id}",
        description=f"Process generic import for registration data import {registration_data_import_id}",
    )
    job.queue()
