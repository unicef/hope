import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from django.core.cache import cache
from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from sentry_sdk import configure_scope

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.household.models import Document
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import Record
from hct_mis_api.apps.registration_datahub.services.extract_record import extract
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import (
    HardDocumentDeduplication,
)
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags
from hct_mis_api.aurora.models import Registration

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import QuerySet, _QuerySet

logger = logging.getLogger(__name__)


def handle_rdi_exception(datahub_rdi_id: str, e: BaseException) -> None:
    try:
        from sentry_sdk import capture_exception

        err = capture_exception(e)
    except Exception:
        err = "N/A"

    RegistrationDataImport.objects.filter(
        datahub_id=datahub_rdi_id,
    ).update(status=RegistrationDataImport.IMPORT_ERROR, sentry_id=err, error_message=str(e))


@contextmanager
def locked_cache(key: Union[int, str], timeout: int = 60 * 60 * 24) -> Any:
    if cache.get(key):
        logger.info(f"Task with key {key} is already running")
        yield False
    else:
        try:
            logger.info(f"Task with key {key} running")
            cache.set(key, True, timeout=timeout)
            yield True
        finally:
            cache.delete(key)
            logger.info(f"Task with key {key} finished")


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def registration_xlsx_import_task(
    self: Any, registration_data_import_id: str, import_data_id: str, business_area_id: str
) -> None:
    try:
        from hct_mis_api.apps.core.models import BusinessArea
        from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )

        with configure_scope() as scope:
            scope.set_tag("business_area", BusinessArea.objects.get(pk=business_area_id))

            RegistrationDataImport.objects.filter(datahub_id=registration_data_import_id).update(
                status=RegistrationDataImport.IMPORTING
            )

            RdiXlsxCreateTask().execute(
                registration_data_import_id=registration_data_import_id,
                import_data_id=import_data_id,
                business_area_id=business_area_id,
            )
    except Exception as e:
        logger.warning(e)
        from hct_mis_api.apps.registration_datahub.models import (
            RegistrationDataImportDatahub,
        )

        RegistrationDataImportDatahub.objects.filter(
            id=registration_data_import_id,
        ).update(import_done=RegistrationDataImportDatahub.DONE)

        handle_rdi_exception(registration_data_import_id, e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def registration_kobo_import_task(
    self: Any, registration_data_import_id: str, import_data_id: str, business_area_id: str
) -> None:
    try:
        from hct_mis_api.apps.core.models import BusinessArea
        from hct_mis_api.apps.registration_datahub.tasks.rdi_kobo_create import (
            RdiKoboCreateTask,
        )

        with configure_scope() as scope:
            scope.set_tag("business_area", BusinessArea.objects.get(pk=business_area_id))

            RdiKoboCreateTask().execute(
                registration_data_import_id=registration_data_import_id,
                import_data_id=import_data_id,
                business_area_id=business_area_id,
            )
    except Exception as e:
        logger.warning(e)
        from hct_mis_api.apps.registration_datahub.models import (
            RegistrationDataImportDatahub,
        )

        RegistrationDataImportDatahub.objects.filter(
            id=registration_data_import_id,
        ).update(import_done=RegistrationDataImportDatahub.DONE)

        handle_rdi_exception(registration_data_import_id, e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def registration_kobo_import_hourly_task(self: Any) -> None:
    try:
        from hct_mis_api.apps.core.models import BusinessArea
        from hct_mis_api.apps.registration_datahub.models import (
            RegistrationDataImportDatahub,
        )
        from hct_mis_api.apps.registration_datahub.tasks.rdi_kobo_create import (
            RdiKoboCreateTask,
        )

        not_started_rdi = RegistrationDataImportDatahub.objects.filter(
            import_done=RegistrationDataImportDatahub.NOT_STARTED
        ).first()

        if not_started_rdi is None:
            return
        business_area = BusinessArea.objects.get(slug=not_started_rdi.business_area_slug)
        with configure_scope() as scope:
            scope.set_tag("business_area", business_area)

            RdiKoboCreateTask().execute(
                registration_data_import_id=str(not_started_rdi.id),
                import_data_id=str(not_started_rdi.import_data.id),
                business_area_id=str(business_area.id),
            )
    except Exception as e:
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def registration_xlsx_import_hourly_task(self: Any) -> None:
    try:
        from hct_mis_api.apps.core.models import BusinessArea
        from hct_mis_api.apps.registration_datahub.models import (
            RegistrationDataImportDatahub,
        )
        from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )

        not_started_rdi = RegistrationDataImportDatahub.objects.filter(
            import_done=RegistrationDataImportDatahub.NOT_STARTED
        ).first()
        if not_started_rdi is None:
            return

        business_area = BusinessArea.objects.get(slug=not_started_rdi.business_area_slug)
        with configure_scope() as scope:
            scope.set_tag("business_area", business_area)

            RdiXlsxCreateTask().execute(
                registration_data_import_id=str(not_started_rdi.id),
                import_data_id=str(not_started_rdi.import_data.id),
                business_area_id=str(business_area.id),
            )
    except Exception as e:
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def merge_registration_data_import_task(self: Any, registration_data_import_id: str) -> bool:
    logger.info(
        f"merge_registration_data_import_task started for registration_data_import_id: {registration_data_import_id}"
    )
    with locked_cache(key=f"merge_registration_data_import_task-{registration_data_import_id}") as locked:
        if not locked:
            return True
        try:
            from hct_mis_api.apps.registration_data.models import RegistrationDataImport
            from hct_mis_api.apps.registration_datahub.tasks.rdi_merge import (
                RdiMergeTask,
            )

            RegistrationDataImport.objects.filter(id=registration_data_import_id).update(
                status=RegistrationDataImport.MERGING
            )

            RdiMergeTask().execute(registration_data_import_id)
        except Exception as e:
            logger.exception(e)
            from hct_mis_api.apps.registration_data.models import RegistrationDataImport

            RegistrationDataImport.objects.filter(
                id=registration_data_import_id,
            ).update(status=RegistrationDataImport.MERGE_ERROR)
            raise self.retry(exc=e)

    logger.info(
        f"merge_registration_data_import_task finished for registration_data_import_id: {registration_data_import_id}"
    )
    return True


@app.task(bind=True, queue="priority", default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def rdi_deduplication_task(self: Any, registration_data_import_id: str) -> None:
    try:
        from hct_mis_api.apps.registration_datahub.models import (
            RegistrationDataImportDatahub,
        )
        from hct_mis_api.apps.registration_datahub.tasks.deduplicate import (
            DeduplicateTask,
        )

        rdi_obj = RegistrationDataImportDatahub.objects.get(id=registration_data_import_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", rdi_obj.business_area_slug)

            with transaction.atomic(using="default"), transaction.atomic(using="registration_datahub"):
                DeduplicateTask(rdi_obj.business_area_slug).deduplicate_imported_individuals(
                    registration_data_import_datahub=rdi_obj
                )
    except Exception as e:
        handle_rdi_exception(registration_data_import_id, e)
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def pull_kobo_submissions_task(self: Any, import_data_id: "UUID") -> Dict:
    from hct_mis_api.apps.registration_datahub.models import KoboImportData

    kobo_import_data = KoboImportData.objects.get(id=import_data_id)
    from hct_mis_api.apps.registration_datahub.tasks.pull_kobo_submissions import (
        PullKoboSubmissions,
    )

    try:
        return PullKoboSubmissions().execute(kobo_import_data)
    except Exception as e:
        from hct_mis_api.apps.registration_data.models import RegistrationDataImport

        RegistrationDataImport.objects.filter(
            id=kobo_import_data.id,
        ).update(status=KoboImportData.STATUS_ERROR, error=str(e))
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def validate_xlsx_import_task(self: Any, import_data_id: "UUID") -> Dict:
    from hct_mis_api.apps.registration_datahub.models import ImportData

    import_data = ImportData.objects.get(id=import_data_id)
    from hct_mis_api.apps.registration_datahub.tasks.validatate_xlsx_import import (
        ValidateXlsxImport,
    )

    try:
        return ValidateXlsxImport().execute(import_data)
    except Exception as e:
        ImportData.objects.filter(
            id=import_data.id,
        ).update(status=ImportData.STATUS_ERROR, error=str(e))
        raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def process_flex_records_task(self: Any, reg_id: "UUID", rdi_id: "UUID", records_ids: List) -> None:
    registration = Registration.objects.get(id=reg_id)
    try:
        if service := registration.rdi_parser:
            service.process_records(rdi_id, records_ids)
        else:
            logger.exception("Not Implemented Service for Registration")
            raise NotImplementedError
    except Exception as e:
        logger.exception("Process Flex Records Task error")
        raise self.retry(exc=e)


@app.task
@log_start_and_end
@sentry_tags
def extract_records_task(max_records: int = 500) -> None:
    records_ids = Record.objects.filter(data__isnull=True).only("pk").values_list("pk", flat=True)[:max_records]
    extract(records_ids)


@app.task
@log_start_and_end
@sentry_tags
def fresh_extract_records_task(records_ids: Optional["_QuerySet[Any, Any]"] = None) -> None:
    if not records_ids:
        records_ids = Record.objects.all().only("pk").values_list("pk", flat=True)[:5000]
    extract(records_ids)


@app.task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 30})
@log_start_and_end
@sentry_tags
def automate_rdi_creation_task(
    registration_id: int,
    page_size: int,
    template: str = "{business_area_name} rdi {date}",
    auto_merge: bool = False,
    fix_tax_id: bool = False,
    **filters: Any,
) -> List:
    try:
        with locked_cache(key=f"automate_rdi_creation_task-{registration_id}") as locked:
            if not locked:
                return []
            output = []
            try:
                registration = Registration.objects.get(id=registration_id)
            except Registration.DoesNotExist:
                raise NotImplementedError
            project = registration.project
            # programme = project.programme TODO programme refactoring
            organization = project.organization
            service: Optional[Any] = registration.rdi_parser
            if service is None:
                raise NotImplementedError

            qs = Record.objects.filter(registration=registration_id, **filters).exclude(
                status__in=[Record.STATUS_IMPORTED, Record.STATUS_ERROR]
            )
            if fix_tax_id:
                check_and_set_taxid(qs)
            all_records_ids = qs.values_list("id", flat=True)
            if len(all_records_ids) == 0:
                return ["No Records found", 0]

            splitted_record_ids = [
                all_records_ids[i : i + page_size] for i in range(0, len(all_records_ids), page_size)
            ]
            for page, records_ids in enumerate(splitted_record_ids, 1):
                rdi_name = template.format(
                    page=page,
                    date=timezone.now(),
                    registration_id=registration_id,
                    page_size=page_size,
                    records=len(records_ids),
                    business_area_name=organization.name,
                )
                rdi = service.create_rdi(imported_by=None, rdi_name=rdi_name)
                service.process_records(rdi_id=rdi.id, records_ids=records_ids)
                output.append([rdi_name, len(records_ids)])
                if auto_merge:
                    merge_registration_data_import_task.delay(rdi.id)

            return output

    except Exception:
        raise


def check_and_set_taxid(queryset: "QuerySet") -> Dict:
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


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def automate_registration_diia_import_task(
    self: Any, page_size: int, template: str = "Diia ukraine rdi {date} {page_size}", **filters: Any
) -> List:
    from hct_mis_api.apps.core.models import BusinessArea
    from hct_mis_api.apps.registration_datahub.tasks.rdi_diia_create import (
        RdiDiiaCreateTask,
    )

    with locked_cache(key="automate_rdi_diia_creation_task") as locked:
        if not locked:
            return []
        try:
            with configure_scope() as scope:
                scope.set_tag("business_area", BusinessArea.objects.get(slug="ukraine"))
                service = RdiDiiaCreateTask()
                rdi_name = template.format(
                    date=timezone.now(),
                    page_size=page_size,
                )
                rdi = service.create_rdi(None, rdi_name)
                service.execute(rdi.id, diia_hh_count=page_size)
                return [rdi_name, page_size]
        except Exception as e:
            raise self.retry(exc=e)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def registration_diia_import_task(
    self: Any, diia_hh_ids: List, template: str = "Diia ukraine rdi {date} {page_size}", **filters: Any
) -> List:
    from hct_mis_api.apps.core.models import BusinessArea
    from hct_mis_api.apps.registration_datahub.tasks.rdi_diia_create import (
        RdiDiiaCreateTask,
    )

    with locked_cache(key="registration_diia_import_task") as locked:
        if not locked:
            return []
        try:
            with configure_scope() as scope:
                scope.set_tag("business_area", BusinessArea.objects.get(slug="ukraine"))
                service = RdiDiiaCreateTask()
                rdi_name = template.format(
                    date=timezone.now(),
                    page_size=len(diia_hh_ids),
                )
                rdi = service.create_rdi(None, rdi_name)
                service.execute(rdi.id, diia_hh_ids=diia_hh_ids)
                return [rdi_name, len(diia_hh_ids)]
        except Exception as e:
            raise self.retry(exc=e)


@app.task
@log_start_and_end
@sentry_tags
def deduplicate_documents() -> bool:
    with locked_cache(key="deduplicate_documents") as locked:
        if not locked:
            return True
        grouped_rdi = (
            Document.objects.filter(status=Document.STATUS_PENDING)
            .values("individual__registration_data_import")
            .annotate(count=Count("individual__registration_data_import"))
        )
        rdi_ids = [x["individual__registration_data_import"] for x in grouped_rdi if x is not None]
        for rdi in RegistrationDataImport.objects.filter(id__in=rdi_ids).order_by("created_at"):
            with transaction.atomic():
                documents_query = Document.objects.filter(
                    status=Document.STATUS_PENDING, individual__registration_data_import=rdi
                )
                HardDocumentDeduplication().deduplicate(
                    documents_query,
                    registration_data_import=rdi,
                )

        with transaction.atomic():
            documents_query = Document.objects.filter(
                status=Document.STATUS_PENDING, individual__registration_data_import__isnull=True
            )
            HardDocumentDeduplication().deduplicate(
                documents_query,
            )
    return True


@app.task
@sentry_tags
def check_rdi_import_periodic_task() -> bool:
    from hct_mis_api.apps.utils.celery_manager import rdi_import_celery_manager

    with locked_cache(key="celery_manager_periodic_task") as locked:
        if not locked:
            return True
        rdi_import_celery_manager.execute()
    return True


@app.task
@sentry_tags
def check_rdi_merge_periodic_task() -> bool:
    from hct_mis_api.apps.utils.celery_manager import rdi_merge_celery_manager

    with locked_cache(key="celery_manager_periodic_task") as locked:
        if not locked:
            return True
        rdi_merge_celery_manager.execute()
    return True
