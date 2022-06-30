import datetime
import logging
from contextlib import contextmanager

from django.core.cache import cache

from redis.exceptions import LockError

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.registration_datahub.models import Record
from hct_mis_api.apps.registration_datahub.services.extract_record import extract

logger = logging.getLogger(__name__)


@contextmanager
def locked_cache(key):
    try:
        if not hasattr(cache, "lock"):
            yield  # a little hack for the sake of tests that use LocMemCache that does not have `lock` attr
        else:
            with cache.lock(key, blocking_timeout=2, timeout=85400):
                yield
    finally:
        pass


@app.task
def registration_xlsx_import_task(registration_data_import_id, import_data_id, business_area):
    logger.info("registration_xlsx_import_task start")
    try:
        from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )

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

    logger.info("registration_xlsx_import_task end")


@app.task
def registration_kobo_import_task(registration_data_import_id, import_data_id, business_area):
    logger.info("registration_kobo_import_task start")

    try:
        from hct_mis_api.apps.registration_datahub.tasks.rdi_kobo_create import (
            RdiKoboCreateTask,
        )

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
        except:
            err = "N/A"

        RegistrationDataImportDatahub.objects.filter(
            id=registration_data_import_id,
        ).update(import_done=RegistrationDataImportDatahub.DONE)

        RegistrationDataImport.objects.filter(
            datahub_id=registration_data_import_id,
        ).update(status=RegistrationDataImport.IMPORT_ERROR, sentry_id=err, error_message=str(e))

        raise

    logger.info("registration_kobo_import_task end")


@app.task
def registration_kobo_import_hourly_task():
    logger.info("registration_kobo_import_hourly_task start")

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

        RdiKoboCreateTask().execute(
            registration_data_import_id=str(not_started_rdi.id),
            import_data_id=str(not_started_rdi.import_data.id),
            business_area_id=str(business_area.id),
        )
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("registration_kobo_import_hourly_task end")


@app.task
def registration_xlsx_import_hourly_task():
    logger.info("registration_xlsx_import_hourly_task start")

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

        RdiXlsxCreateTask().execute(
            registration_data_import_id=str(not_started_rdi.id),
            import_data_id=str(not_started_rdi.import_data.id),
            business_area_id=str(business_area.id),
        )
    except Exception as e:
        logger.exception(e)
        raise

    logger.info("registration_xlsx_import_hourly_task end")


@app.task
def merge_registration_data_import_task(registration_data_import_id):
    logger.info("merge_registration_data_import_task start")

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

    logger.info("merge_registration_data_import_task end")


@app.task(queue="priority")
def rdi_deduplication_task(registration_data_import_id):
    logger.info("rdi_deduplication_task start")

    try:
        from hct_mis_api.apps.registration_datahub.models import (
            RegistrationDataImportDatahub,
        )
        from hct_mis_api.apps.registration_datahub.tasks.deduplicate import (
            DeduplicateTask,
        )

        rdi_obj = RegistrationDataImportDatahub.objects.get(id=registration_data_import_id)

        DeduplicateTask.deduplicate_imported_individuals(registration_data_import_datahub=rdi_obj)
    except Exception as e:
        logger.exception(e)
        from hct_mis_api.apps.registration_data.models import RegistrationDataImport

        RegistrationDataImport.objects.filter(
            datahub_id=registration_data_import_id,
        ).update(status=RegistrationDataImport.IMPORT_ERROR)
        raise

    logger.info("rdi_deduplication_task end")


@app.task
def pull_kobo_submissions_task(import_data_id):
    logger.info("pull_kobo_submissions_task start")
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
    finally:
        logger.info("pull_kobo_submissions_task end")


@app.task
def validate_xlsx_import_task(import_data_id):
    logger.info("validate_xlsx_import_task start")
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
    finally:
        logger.info("validate_xlsx_import_task end")


@app.task
def process_flex_records_task(rdi_id, records_ids):
    logger.info("process_flex_records start")
    from hct_mis_api.apps.registration_datahub.services.flex_registration_service import (
        FlexRegistrationService,
    )

    FlexRegistrationService().process_records(rdi_id, records_ids)
    logger.info("process_flex_records end")


@app.task
def extract_records_task(max_records=500):
    logger.info("extract_records_task start")

    records_ids = Record.objects.filter(data__isnull=True).only("pk").values_list("pk", flat=True)[:max_records]
    extract(records_ids)
    logger.info("extract_records_task end")


@app.task
def fresh_extract_records_task(records_ids=None):
    logger.info("fresh_extract_records_task start")

    if not records_ids:
        records_ids = Record.objects.all().only("pk").values_list("pk", flat=True)[:5000]
    extract(records_ids)

    logger.info("fresh_extract_records_task end")


@app.task
def automate_rdi_creation_task(registration_id: int, page_size: int, template="ukraine rdi {date}", **filters):
    from hct_mis_api.apps.registration_datahub.services.flex_registration_service import (
        FlexRegistrationService,
    )

    try:
        with locked_cache(key=f"automate_rdi_creation_task-{registration_id}"):
            try:
                service = FlexRegistrationService()

                all_records_ids = (
                    Record.objects.filter(registration=registration_id, **filters)
                    .exclude(status__in=[Record.STATUS_IMPORTED, Record.STATUS_ERROR])
                    .values_list("id", flat=True)
                )
                if len(all_records_ids) == 0:
                    return None

                splitted_record_ids = [
                    all_records_ids[i : i + page_size] for i in range(0, len(all_records_ids), page_size)
                ]
                output = []
                for records_ids in splitted_record_ids:
                    rdi_name = template.format(
                        date=datetime.datetime.now(),
                        registration_id=registration_id,
                        page_size=page_size,
                        records=len(records_ids),
                    )
                    rdi = service.create_rdi(imported_by=None, rdi_name=rdi_name)
                    service.process_records(rdi_id=rdi.id, records_ids=records_ids)
                    output.append([rdi_name, len(records_ids)])
                return output
            except Exception as e:
                logger.exception(e)
    except LockError as e:
        logger.exception(e)
    return None


@app.task
def automate_registration_diia_import_task(page_size: int, template="Diia ukraine rdi {date} {page_size}", **filters):
    logger.info("automate_registration_diia_import_task start")

    from hct_mis_api.apps.registration_datahub.tasks.rdi_diia_create import (
        RdiDiiaCreateTask,
    )

    try:
        with locked_cache(key="automate_rdi_diia_creation_task"):
            try:
                service = RdiDiiaCreateTask()
                rdi_name = template.format(
                    date=datetime.datetime.now(),
                    page_size=page_size,
                )
                rdi = service.create_rdi(None, rdi_name)
                service.execute(rdi.id, diia_hh_count=page_size)
                return [rdi_name, page_size]
            except Exception as e:
                logger.exception(e)
    except LockError as e:
        logger.exception(e)
        return []

    logger.info("automate_registration_diia_import_task end")


@app.task
def registration_diia_import_task(diia_hh_ids, template="Diia ukraine rdi {date} {page_size}", **filters):
    logger.info("registration_diia_import_task start")

    from hct_mis_api.apps.registration_datahub.tasks.rdi_diia_create import (
        RdiDiiaCreateTask,
    )

    try:
        with locked_cache(key="registration_diia_import_task"):
            try:
                service = RdiDiiaCreateTask()
                rdi_name = template.format(
                    date=datetime.datetime.now(),
                    page_size=len(diia_hh_ids),
                )
                rdi = service.create_rdi(None, rdi_name)
                service.execute(rdi.id, diia_hh_ids=diia_hh_ids)
                return [rdi_name, len(diia_hh_ids)]
            except Exception as e:
                logger.exception(e)
    except LockError as e:
        logger.exception(e)
        return []

    logger.info("registration_diia_import_task end")
