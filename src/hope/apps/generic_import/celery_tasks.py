from hope.apps.core.celery import app
from hope.apps.registration_datahub.celery_tasks import locked_cache
from hope.apps.registration_datahub.exceptions import AlreadyRunningError
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags

SOFT_TIME_LIMIT = 30 * 60
HARD_TIME_LIMIT = 35 * 60

RESULT_LOCKED = "locked"
RESULT_SUCCESS = "success"
RESULT_FAILED = "failed"


def format_validation_errors(errors: list) -> str:
    """Format validation errors in a human-readable way."""
    if not errors:
        return "No errors"

    formatted_lines = []

    for idx, error_item in enumerate(errors, 1):
        if not isinstance(error_item, dict):
            formatted_lines.append(f"{idx}. {str(error_item)}")
            continue

        error_type = error_item.get("type", "Unknown")
        data = error_item.get("data", {})
        field_errors = error_item.get("errors", {})

        # Get identifier for the record
        if error_type == "household":
            identifier = data.get("id", "Unknown")[:8]
            header = f"{idx}. Household (ID: {identifier}...)"
        elif error_type == "individual":
            full_name = data.get("full_name", data.get("given_name", "Unknown"))
            header = f"{idx}. Individual ({full_name})"
        elif error_type == "account":
            number = data.get("number", "Unknown")
            header = f"{idx}. Account ({number})"
        else:
            header = f"{idx}. {error_type.title()}"

        formatted_lines.append(header)

        # Format field errors
        for field_name, error_messages in field_errors.items():
            if isinstance(error_messages, list):
                for msg in error_messages:
                    formatted_lines.append(f"   • {field_name}: {msg}")
            else:
                formatted_lines.append(f"   • {field_name}: {error_messages}")

    return "\n".join(formatted_lines)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def process_generic_import_task(
    self,
    registration_data_import_id: str,
    import_data_id: str,
) -> None:
    """Process generic import file asynchronously.

    Args:
        registration_data_import_id: UUID of RegistrationDataImport instance
        import_data_id: UUID of ImportData instance

    """
    import logging

    from hope.apps.generic_import.generic_upload_service.importer import Importer
    from hope.apps.generic_import.generic_upload_service.parsers.xlsx_somalia_parser import (
        XlsxSomaliaParser,
    )
    from hope.apps.registration_data.models import ImportData, RegistrationDataImport
    from hope.apps.utils.sentry import set_sentry_business_area_tag

    logger = logging.getLogger(__name__)

    try:
        with locked_cache(key=f"process_generic_import_task-{registration_data_import_id}") as locked:
            if not locked:
                raise AlreadyRunningError(
                    f"Task with key process_generic_import_task-{registration_data_import_id} is already running"
                )

            # Get objects
            import_data = ImportData.objects.get(id=import_data_id)
            rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)

            set_sentry_business_area_tag(rdi.business_area.name)

            # Update status to RUNNING
            import_data.status = ImportData.STATUS_RUNNING
            import_data.save(update_fields=["status"])

            rdi.status = RegistrationDataImport.LOADING
            rdi.save(update_fields=["status"])

            # Parse file
            parser = XlsxSomaliaParser()
            parser.parse(import_data.file.path)

            # Run importer
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
                # Set validation error status
                import_data.status = ImportData.STATUS_VALIDATION_ERROR
                import_data.validation_errors = str(errors)
                import_data.save(update_fields=["status", "validation_errors"])

                # Format error message with details in human-readable format
                error_details = format_validation_errors(errors)
                error_message = f"Validation errors ({len(errors)} errors found):\n\n{error_details}"

                rdi.status = RegistrationDataImport.IMPORT_ERROR
                rdi.error_message = error_message
                rdi.save(update_fields=["status", "error_message"])

                logger.warning(f"Import {rdi.id} completed with {len(errors)} validation errors: {error_details}")
            else:
                # Update stats
                from hope.apps.household.models import Household, Individual

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
                    f"Import {rdi.id} completed successfully: "
                    f"{households_count} households, {individuals_count} individuals"
                )

    except AlreadyRunningError as e:
        logger.error(str(e))
        raise  # Raise without retry - task will fail

    except Exception as e:
        logger.exception(f"Error processing generic import {registration_data_import_id}: {e}")

        # Update error status
        try:
            from sentry_sdk import capture_exception

            sentry_id = capture_exception(e)
        except Exception as exc:
            logger.exception(exc)
            sentry_id = "N/A"

        # Update ImportData status
        try:
            import_data = ImportData.objects.get(id=import_data_id)
            import_data.status = ImportData.STATUS_ERROR
            import_data.error = str(e)
            import_data.save(update_fields=["status", "error"])
        except Exception as exc:
            logger.exception(f"Failed to update ImportData status: {exc}")

        # Update RegistrationDataImport status
        try:
            rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)
            rdi.status = RegistrationDataImport.IMPORT_ERROR
            rdi.error_message = str(e)
            rdi.sentry_id = sentry_id
            rdi.save(update_fields=["status", "error_message", "sentry_id"])
        except Exception as exc:
            logger.exception(f"Failed to update RegistrationDataImport status: {exc}")

        raise self.retry(exc=e)
