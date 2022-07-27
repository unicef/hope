from django.db import transaction
from django.db.models import Count
from django.utils import timezone
import logging
from contextlib import contextmanager
from sentry_sdk import configure_scope

from django.core.cache import cache
from redis.exceptions import LockError

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.household.models import Document
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import Record
from hct_mis_api.apps.registration_datahub.services.extract_record import extract
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask

logger = logging.getLogger(__name__)


@contextmanager
def locked_cache(key):
    try:
        # ``blocking_timeout`` indicates the maximum amount of time in seconds to
        # spend trying to acquire the lock.
        # ``timeout`` indicates a maximum life for the lock.
        # some procedures here can take a few seconds
        # 30s to try acquiring the lock should be enough
        with cache.lock(key, blocking_timeout=30, timeout=60 * 60 * 24) as lock:
            yield
    except LockError as e:
        logger.exception(f"Couldn't lock cache for key '{key}'. Failed with: {e}")
    else:
        if lock.locked():
            lock.release()


@app.task
@log_start_and_end
@sentry_tags
def registration_xlsx_import_task(registration_data_import_id, import_data_id, business_area):
    try:
        from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )
        from hct_mis_api.apps.core.models import BusinessArea

        with configure_scope() as scope:
            scope.set_tag("business_area", BusinessArea.objects.get(pk=business_area))
            RdiXlsxCreateTask().execute(
                registration_data_import_id=registration_data_import_id,
                import_data_id=import_data_id,
                business_area_id=business_area,
            )
    except Exception as e:
        logger.exception(e)
        from hct_mis_api.apps.registration_data.models import RegistrationDataImport
        from hct_mis_api.apps.registration_datahub.models import (
            RegistrationDataImportDatahub,
        )

        RegistrationDataImportDatahub.objects.filter(
            id=registration_data_import_id,
        ).update(import_done=RegistrationDataImportDatahub.DONE)

        RegistrationDataImport.objects.filter(
            datahub_id=registration_data_import_id,
        ).update(status=RegistrationDataImport.IMPORT_ERROR)
        raise


@app.task
@log_start_and_end
@sentry_tags
def registration_kobo_import_task(registration_data_import_id, import_data_id, business_area):
    try:
        from hct_mis_api.apps.registration_datahub.tasks.rdi_kobo_create import (
            RdiKoboCreateTask,
        )
        from hct_mis_api.apps.core.models import BusinessArea

        with configure_scope() as scope:
            scope.set_tag("business_area", BusinessArea.objects.get(pk=business_area))

            RdiKoboCreateTask().execute(
                registration_data_import_id=registration_data_import_id,
                import_data_id=import_data_id,
                business_area_id=business_area,
            )
    except Exception as e:
        logger.exception(e)
        from hct_mis_api.apps.registration_data.models import RegistrationDataImport
        from hct_mis_api.apps.registration_datahub.models import (
            RegistrationDataImportDatahub,
        )

        try:
            from sentry_sdk import capture_exception

            err = capture_exception(e)
        except Exception:
            err = "N/A"

        RegistrationDataImportDatahub.objects.filter(
            id=registration_data_import_id,
        ).update(import_done=RegistrationDataImportDatahub.DONE)

        RegistrationDataImport.objects.filter(
            datahub_id=registration_data_import_id,
        ).update(status=RegistrationDataImport.IMPORT_ERROR, sentry_id=err, error_message=str(e))

        raise


@app.task
@log_start_and_end
@sentry_tags
def registration_kobo_import_hourly_task():
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
            scope.set_tag("business_area", BusinessArea.objects.get(pk=business_area))

            RdiKoboCreateTask().execute(
                registration_data_import_id=str(not_started_rdi.id),
                import_data_id=str(not_started_rdi.import_data.id),
                business_area_id=str(business_area.id),
            )
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def registration_xlsx_import_hourly_task():
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
            scope.set_tag("business_area", BusinessArea.objects.get(pk=business_area))

            RdiXlsxCreateTask().execute(
                registration_data_import_id=str(not_started_rdi.id),
                import_data_id=str(not_started_rdi.import_data.id),
                business_area_id=str(business_area.id),
            )
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def merge_registration_data_import_task(registration_data_import_id):
    logger.info(
        f"merge_registration_data_import_task started for registration_data_import_id: {registration_data_import_id}"
    )
    try:
        from hct_mis_api.apps.registration_datahub.tasks.rdi_merge import RdiMergeTask

        RdiMergeTask().execute(registration_data_import_id)
    except Exception as e:
        logger.exception(e)
        from hct_mis_api.apps.registration_data.models import RegistrationDataImport

        RegistrationDataImport.objects.filter(
            id=registration_data_import_id,
        ).update(status=RegistrationDataImport.MERGE_ERROR)
        raise

    logger.info(
        f"merge_registration_data_import_task finished for registration_data_import_id: {registration_data_import_id}"
    )


@app.task(queue="priority")
@log_start_and_end
@sentry_tags
def rdi_deduplication_task(registration_data_import_id):

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

            DeduplicateTask.deduplicate_imported_individuals(registration_data_import_datahub=rdi_obj)
    except Exception as e:
        logger.exception(e)
        from hct_mis_api.apps.registration_data.models import RegistrationDataImport

        RegistrationDataImport.objects.filter(
            datahub_id=registration_data_import_id,
        ).update(status=RegistrationDataImport.IMPORT_ERROR)
        raise


@app.task
@log_start_and_end
@sentry_tags
def pull_kobo_submissions_task(import_data_id):
    from hct_mis_api.apps.registration_datahub.models import KoboImportData

    kobo_import_data = KoboImportData.objects.get(id=import_data_id)
    from hct_mis_api.apps.registration_datahub.tasks.pull_kobo_submissions import (
        PullKoboSubmissions,
    )

    try:
        return PullKoboSubmissions().execute(kobo_import_data)
    except Exception as e:
        logger.exception(e)
        from hct_mis_api.apps.registration_data.models import RegistrationDataImport

        RegistrationDataImport.objects.filter(
            id=kobo_import_data.id,
        ).update(status=KoboImportData.STATUS_ERROR, error=str(e))
        raise


@app.task
@log_start_and_end
@sentry_tags
def validate_xlsx_import_task(import_data_id):
    from hct_mis_api.apps.registration_datahub.models import ImportData

    import_data = ImportData.objects.get(id=import_data_id)
    from hct_mis_api.apps.registration_datahub.tasks.validatate_xlsx_import import (
        ValidateXlsxImport,
    )

    try:
        return ValidateXlsxImport().execute(import_data)
    except Exception as e:
        logger.exception(e)
        from hct_mis_api.apps.registration_data.models import RegistrationDataImport

        RegistrationDataImport.objects.filter(
            id=import_data.id,
        ).update(status=ImportData.STATUS_ERROR, error=str(e))
        raise


@app.task
@log_start_and_end
@sentry_tags
def process_flex_records_task(rdi_id, records_ids):
    from hct_mis_api.apps.registration_datahub.services.flex_registration_service import (
        FlexRegistrationService,
    )

    FlexRegistrationService().process_records(rdi_id, records_ids)


@app.task
@log_start_and_end
@sentry_tags
def extract_records_task(max_records=500):
    records_ids = Record.objects.filter(data__isnull=True).only("pk").values_list("pk", flat=True)[:max_records]
    extract(records_ids)


@app.task
@log_start_and_end
@sentry_tags
def fresh_extract_records_task(records_ids=None):
    if not records_ids:
        records_ids = Record.objects.all().only("pk").values_list("pk", flat=True)[:5000]
    extract(records_ids)


@app.task
@log_start_and_end
@sentry_tags
def automate_rdi_creation_task(
    registration_id: int,
    page_size: int,
    template: str = "ukraine rdi {date}",
    auto_merge=False,
    fix_tax_id=False,
    **filters,
):
    from hct_mis_api.apps.registration_datahub.services.flex_registration_service import (
        FlexRegistrationService,
    )

    try:
        with locked_cache(key=f"automate_rdi_creation_task-{registration_id}"):
            try:
                service = FlexRegistrationService()

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
                output = []
                for page, records_ids in enumerate(splitted_record_ids, 1):
                    rdi_name = template.format(
                        page=page,
                        date=timezone.now(),
                        registration_id=registration_id,
                        page_size=page_size,
                        records=len(records_ids),
                    )
                    rdi = service.create_rdi(imported_by=None, rdi_name=rdi_name)
                    service.process_records(rdi_id=rdi.id, records_ids=records_ids)
                    output.append([rdi_name, len(records_ids)])
                    if auto_merge:
                        merge_registration_data_import_task.delay(rdi.id)

                return output
            except Exception as e:
                logger.exception(e)
                raise
    except LockError as e:
        logger.exception(e)
    return None


def check_and_set_taxid(queryset):
    qs = queryset.filter(unique_field__isnull=True)
    results = {"updated": [], "processed": []}
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
            results[record.pk] = f"{e.__class__.__name__}: {str(e)}"
    return results


@app.task
@sentry_tags
def automate_registration_diia_import_task(page_size: int, template="Diia ukraine rdi {date} {page_size}", **filters):
    from hct_mis_api.apps.registration_datahub.tasks.rdi_diia_create import (
        RdiDiiaCreateTask,
    )

    with locked_cache(key="automate_rdi_diia_creation_task"):
        try:
            service = RdiDiiaCreateTask()
            rdi_name = template.format(
                date=timezone.now(),
                page_size=page_size,
            )
            rdi = service.create_rdi(None, rdi_name)
            service.execute(rdi.id, diia_hh_count=page_size)
            return [rdi_name, page_size]
        except Exception:
            raise


@app.task
@sentry_tags
def registration_diia_import_task(diia_hh_ids, template="Diia ukraine rdi {date} {page_size}", **filters):
    from hct_mis_api.apps.registration_datahub.tasks.rdi_diia_create import (
        RdiDiiaCreateTask,
    )

    with locked_cache(key="registration_diia_import_task"):
        try:
            service = RdiDiiaCreateTask()
            rdi_name = template.format(
                date=timezone.now(),
                page_size=len(diia_hh_ids),
            )
            rdi = service.create_rdi(None, rdi_name)
            service.execute(rdi.id, diia_hh_ids=diia_hh_ids)
            return [rdi_name, len(diia_hh_ids)]
        except Exception:
            raise


@app.task
def deduplicate_documents():
    with locked_cache(key="deduplicate_documents"):
        with transaction.atomic():
            grouped_rdi = (
                Document.objects.filter(status=Document.STATUS_PENDING)
                .values("individual__registration_data_import")
                .annotate(count=Count("individual__registration_data_import"))
                .order_by("-individual__registration_data_import__created_at")
            )
            rdi_ids = [x["individual__registration_data_import"] for x in grouped_rdi if x is not None]
            for rdi in RegistrationDataImport.objects.filter(id__in=rdi_ids):
                print(rdi)
                DeduplicateTask.hard_deduplicate_documents(
                    Document.objects.filter(status=Document.STATUS_PENDING, individual__registration_data_import=rdi),
                    registration_data_import=rdi,
                )
            DeduplicateTask.hard_deduplicate_documents(
                Document.objects.filter(status=Document.STATUS_PENDING, individual__registration_data_import__isnull=True),
                registration_data_import=rdi,
            )
            import ipdb;ipdb.set_trace()
            raise