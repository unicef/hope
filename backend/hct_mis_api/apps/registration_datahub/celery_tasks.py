import json
import logging

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.registration_datahub.models import Record

logger = logging.getLogger(__name__)


@app.task
def registration_xlsx_import_task(registration_data_import_id, import_data_id, business_area):
    logger.info("registration_xlsx_import_task start")
    try:
        from hct_mis_api.apps.registration_datahub.tasks.rdi_create import (
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
        from hct_mis_api.apps.registration_datahub.tasks.rdi_create import (
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
        from hct_mis_api.apps.registration_datahub.tasks.rdi_create import (
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
        from hct_mis_api.apps.registration_datahub.tasks.rdi_create import (
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


@app.task
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
def extract_records_task():
    logger.info("extract_records_task start")

    records_ids = Record.objects.filter(data={}).values_list("pk", flat=True)[:5000]
    Record.extract(records_ids)

    logger.info("extract_records_task end")
