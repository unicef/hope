import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from hope.apps.core.celery import app
from hope.apps.core.models import BusinessArea
from hope.apps.household.models import Document, Household
from hope.apps.program.models import Program
from hope.apps.registration_data.models import RegistrationDataImport
from hope.apps.registration_datahub.exceptions import (
    AlreadyRunningException,
    WrongStatusException,
)
from hope.apps.registration_datahub.tasks.deduplicate import (
    HardDocumentDeduplication,
)
from hope.apps.registration_datahub.tasks.rdi_program_population_create import (
    RdiProgramPopulationCreateTask,
)
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


def handle_rdi_exception(rdi_id: str, e: BaseException) -> None:
    try:
        from sentry_sdk import capture_exception

        err = capture_exception(e)
    except Exception as exc:  # pragma: no cover
        err = "N/A"  # pragma: no cover
        logger.exception(exc)  # pragma: no cover
    RegistrationDataImport.objects.filter(
        id=rdi_id,
    ).update(status=RegistrationDataImport.IMPORT_ERROR, sentry_id=err, error_message=str(e))


@contextmanager
def locked_cache(key: int | str, timeout: int = 60 * 60 * 24) -> Any:
    now = timezone.now()
    try:
        if cache.get_or_set(key, now, timeout=timeout) == now:
            logger.info(f"Task with key {key} started")
            yield True
        else:
            logger.info(f"Task with key {key} is already running")
            yield False
    finally:
        cache.delete(key)
        logger.info(f"Task with key {key} finished")


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def registration_xlsx_import_task(
    self: Any,
    registration_data_import_id: str,
    import_data_id: str,
    business_area_id: str,
    program_id: "UUID",
) -> bool:
    try:
        from hope.apps.program.models import Program
        from hope.apps.registration_datahub.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )
        from hope.apps.registration_datahub.tasks.rdi_xlsx_people_create import (
            RdiXlsxPeopleCreateTask,
        )

        with locked_cache(key=f"registration_xlsx_import_task-{registration_data_import_id}") as locked:
            if not locked:
                raise AlreadyRunningException(
                    f"Task with key registration_xlsx_import_task {registration_data_import_id} is already running"
                )
            rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)
            set_sentry_business_area_tag(rdi.business_area.name)
            if rdi.status not in (RegistrationDataImport.IMPORT_SCHEDULED, RegistrationDataImport.IMPORT_ERROR):
                raise WrongStatusException("Rdi is not in status IMPORT_SCHEDULED while trying to import")
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
    except (WrongStatusException, AlreadyRunningException) as e:
        logger.info(str(e))
        return True
    except Exception as e:
        handle_rdi_exception(registration_data_import_id, e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def registration_program_population_import_task(
    self: Any,
    registration_data_import_id: str,
    business_area_id: str,
    import_from_program_id: "UUID",
    import_to_program_id: "UUID",
) -> bool:
    try:
        cache_key = f"registration_program_population_import_task-{registration_data_import_id}"
        with locked_cache(key=cache_key) as locked:
            if not locked:
                raise AlreadyRunningException(f"Task with key {cache_key} is already running")

            rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)
            set_sentry_business_area_tag(rdi.business_area.name)
            if rdi.status not in (RegistrationDataImport.IMPORT_SCHEDULED, RegistrationDataImport.IMPORT_ERROR):
                raise WrongStatusException("Rdi is not in status IMPORT_SCHEDULED while trying to import")
            rdi.status = RegistrationDataImport.IMPORTING
            rdi.save()

            RdiProgramPopulationCreateTask().execute(
                registration_data_import_id=registration_data_import_id,
                business_area_id=business_area_id,
                import_from_program_id=str(import_from_program_id),
                import_to_program_id=str(import_to_program_id),
            )
            return True
    except (WrongStatusException, AlreadyRunningException) as e:
        logger.info(str(e))
        return True
    except RegistrationDataImport.DoesNotExist:
        raise
    except Exception as e:  # pragma: no cover
        logger.warning(e)

        handle_rdi_exception(registration_data_import_id, e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def registration_kobo_import_task(
    self: Any, registration_data_import_id: str, import_data_id: str, business_area_id: str, program_id: "UUID"
) -> None:
    try:
        from hope.apps.core.models import BusinessArea
        from hope.apps.registration_datahub.tasks.rdi_kobo_create import (
            RdiKoboCreateTask,
        )

        set_sentry_business_area_tag(BusinessArea.objects.get(pk=business_area_id).name)

        RdiKoboCreateTask(
            registration_data_import_id=registration_data_import_id,
            business_area_id=business_area_id,
        ).execute(
            import_data_id=import_data_id,
            program_id=str(program_id),
        )
    except Exception as e:  # pragma: no cover
        logger.warning(e)  # pragma: no cover

        handle_rdi_exception(registration_data_import_id, e)  # pragma: no cover
        raise self.retry(exc=e)  # pragma: no cover


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def registration_kobo_import_hourly_task(self: Any) -> None:
    try:
        from hope.apps.core.models import BusinessArea
        from hope.apps.registration_datahub.tasks.rdi_kobo_create import (
            RdiKoboCreateTask,
        )

        not_started_rdi = RegistrationDataImport.objects.filter(status=RegistrationDataImport.LOADING).first()

        if not_started_rdi is None:
            return  # pragma: no cover
        business_area = BusinessArea.objects.get(slug=not_started_rdi.business_area.slug)
        program_id = RegistrationDataImport.objects.get(id=not_started_rdi.id).program.id
        set_sentry_business_area_tag(business_area.name)

        RdiKoboCreateTask(
            registration_data_import_id=str(not_started_rdi.id),
            business_area_id=str(business_area.id),
        ).execute(
            import_data_id=str(not_started_rdi.import_data.id),
            program_id=str(program_id),
        )
    except Exception as e:  # pragma: no cover
        raise self.retry(exc=e)  # pragma: no cover


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def registration_xlsx_import_hourly_task(self: Any) -> None:
    try:
        from hope.apps.core.models import BusinessArea
        from hope.apps.registration_datahub.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )

        not_started_rdi = RegistrationDataImport.objects.filter(status=RegistrationDataImport.LOADING).first()
        if not_started_rdi is None:
            return  # pragma: no cover

        business_area = BusinessArea.objects.get(slug=not_started_rdi.business_area.slug)
        program_id = not_started_rdi.program.id
        set_sentry_business_area_tag(business_area.name)

        RdiXlsxCreateTask().execute(
            registration_data_import_id=str(not_started_rdi.id),
            import_data_id=str(not_started_rdi.import_data.id),
            business_area_id=str(business_area.id),
            program_id=str(program_id),
        )
    except Exception as e:  # pragma: no cover
        raise self.retry(exc=e)  # pragma: no cover


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def merge_registration_data_import_task(self: Any, registration_data_import_id: str) -> bool:
    logger.info(
        f"merge_registration_data_import_task started for registration_data_import_id: {registration_data_import_id}"
    )
    with locked_cache(key=f"merge_registration_data_import_task-{registration_data_import_id}") as locked:
        if not locked:
            return True  # pragma: no cover
        try:
            from hope.apps.registration_data.models import RegistrationDataImport
            from hope.apps.registration_datahub.tasks.rdi_merge import (
                RdiMergeTask,
            )

            obj_hct = RegistrationDataImport.objects.get(id=registration_data_import_id)
            set_sentry_business_area_tag(obj_hct.business_area.name)

            RegistrationDataImport.objects.filter(id=registration_data_import_id).update(
                status=RegistrationDataImport.MERGING
            )

            RdiMergeTask().execute(registration_data_import_id)
        except Exception as e:
            logger.exception(e)
            from hope.apps.registration_data.models import RegistrationDataImport

            RegistrationDataImport.objects.filter(
                id=registration_data_import_id,
            ).update(status=RegistrationDataImport.MERGE_ERROR)
            raise self.retry(exc=e)

    logger.info(
        f"merge_registration_data_import_task finished for registration_data_import_id: {registration_data_import_id}"
    )
    return True


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def rdi_deduplication_task(self: Any, registration_data_import_id: str) -> None:
    try:
        from hope.apps.registration_datahub.tasks.deduplicate import (
            DeduplicateTask,
        )

        rdi_obj = RegistrationDataImport.objects.get(id=registration_data_import_id)
        program_id = rdi_obj.program.id
        set_sentry_business_area_tag(rdi_obj.business_area.slug)
        with transaction.atomic():
            DeduplicateTask(rdi_obj.business_area.slug, program_id).deduplicate_pending_individuals(
                registration_data_import=rdi_obj
            )
    except Exception as e:
        handle_rdi_exception(registration_data_import_id, e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def pull_kobo_submissions_task(self: Any, import_data_id: "UUID", program_id: "UUID") -> dict:
    from hope.apps.registration_data.models import KoboImportData

    kobo_import_data = KoboImportData.objects.get(id=import_data_id)
    program = Program.objects.get(id=program_id)
    set_sentry_business_area_tag(kobo_import_data.business_area_slug)
    from hope.apps.registration_datahub.tasks.pull_kobo_submissions import (
        PullKoboSubmissions,
    )

    try:
        return PullKoboSubmissions().execute(kobo_import_data, program)
    except Exception as e:  # pragma: no cover
        KoboImportData.objects.filter(
            id=kobo_import_data.id,
        ).update(status=KoboImportData.STATUS_ERROR, error=str(e))
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def validate_xlsx_import_task(self: Any, import_data_id: "UUID", program_id: "UUID") -> dict:
    from hope.apps.program.models import Program
    from hope.apps.registration_data.models import ImportData
    from hope.apps.registration_datahub.tasks.validate_xlsx_import import (
        ValidateXlsxImport,
    )

    import_data = ImportData.objects.get(id=import_data_id)
    program = Program.objects.get(id=program_id)
    set_sentry_business_area_tag(import_data.business_area_slug)
    try:
        return ValidateXlsxImport().execute(import_data, program)
    except Exception as e:  # pragma: no cover
        ImportData.objects.filter(
            id=import_data.id,
        ).update(status=ImportData.STATUS_ERROR, error=str(e))
        raise self.retry(exc=e)


def check_and_set_taxid(queryset: "QuerySet") -> dict:
    qs = queryset.filter(unique_field__isnull=True)
    results = {"updated": [], "processed": [], "errors": []}
    for record in qs.all():
        try:
            for individual in record.fields["individuals"]:
                if individual["role_i_c"] == "y":
                    record.unique_field = individual["tax_id_no_i_c"]
                    record.save()
                    results["updated"].append(record.pk)
                    break
            results["processed"].append(record.pk)

        except Exception as e:
            results["errors"].append(f"Record: {record.pk} - {e.__class__.__name__}: {str(e)}")
    return results


@app.task
@log_start_and_end
@sentry_tags
def deduplicate_documents(rdi_id: str) -> bool:
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


@app.task(bind=True, default_retry_delay=60 * 5, max_retries=3)
@log_start_and_end
@sentry_tags
def check_rdi_import_periodic_task(self: Any, business_area_slug: str | None = None) -> bool | None:
    with cache.lock(
        f"check_rdi_import_periodic_task_{business_area_slug}",
        blocking_timeout=60 * 5,
        timeout=60 * 60 * 1,
    ) as locked:
        if not locked:
            raise Exception("cannot set lock on check_rdi_import_periodic_task")
        from hope.apps.utils.celery_manager import (
            RegistrationDataXlsxImportCeleryManager,
        )

        business_area = BusinessArea.objects.filter(slug=business_area_slug).first()
        if business_area:
            set_sentry_business_area_tag(business_area.name)

        try:
            manager = RegistrationDataXlsxImportCeleryManager(business_area=business_area)
            manager.execute()
            return True
        except Exception as e:
            logger.warning(e)
            raise self.retry(exc=e)


@app.task
@sentry_tags
@log_start_and_end
def remove_old_rdi_links_task(page_count: int = 100) -> None:
    """Remove linked RDI objects for households and related objects (individuals, documents etc.)."""
    from datetime import timedelta

    from constance import config

    days = config.REMOVE_RDI_LINKS_TIMEDELTA
    try:
        # Get datahub_ids older than 3 months which have status other than MERGED
        unmerged_rdi_ids = list(
            RegistrationDataImport.objects.filter(
                created_at__lte=timezone.now() - timedelta(days=days),
                status__in=[
                    RegistrationDataImport.IN_REVIEW,
                    RegistrationDataImport.DEDUPLICATION_FAILED,
                    RegistrationDataImport.IMPORT_ERROR,
                    RegistrationDataImport.MERGE_ERROR,
                ],
            ).values_list("id", flat=True)
        )

        i, count = 0, len(unmerged_rdi_ids) // page_count
        while i <= count:
            logger.info(f"Page {i}/{count} processing...")
            rdi_ids_page = unmerged_rdi_ids[i * page_count : (i + 1) * page_count]

            Household.all_objects.filter(registration_data_import_id__in=rdi_ids_page).delete()

            RegistrationDataImport.objects.filter(id__in=rdi_ids_page).update(erased=True)
            i += 1

        logger.info(f"Data links for RDI(s): {''.join([str(_id) for _id in unmerged_rdi_ids])} removed successfully")
    except Exception:  # pragma: no cover
        logger.warning("Removing old RDI objects failed")
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@sentry_tags
@log_start_and_end
def deduplication_engine_process(self: Any, program_id: str) -> None:
    from hope.apps.registration_datahub.services.biometric_deduplication import (
        BiometricDeduplicationService,
    )

    program = Program.objects.get(id=program_id)
    set_sentry_business_area_tag(program.business_area.name)

    try:
        program = Program.objects.get(id=program_id)
        BiometricDeduplicationService().upload_and_process_deduplication_set(program)
    except Exception as e:
        logger.warning(e)
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def fetch_biometric_deduplication_results_and_process(self: Any, deduplication_set_id: str | None) -> None:
    from hope.apps.registration_datahub.services.biometric_deduplication import (
        BiometricDeduplicationService,
    )

    if not deduplication_set_id:
        logger.warning("Program.deduplication_set_id is None")
        return

    program = Program.objects.get(deduplication_set_id=deduplication_set_id)
    set_sentry_business_area_tag(program.business_area.name)

    try:
        service = BiometricDeduplicationService()
        service.fetch_biometric_deduplication_results_and_process(deduplication_set_id)
    except Exception as e:
        logger.warning(e)
        raise
