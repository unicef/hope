from hct_mis_api.apps.core.celery import app


@app.task
def registration_xlsx_import_task(registration_data_import_id, import_data_id, business_area):
    from hct_mis_api.apps.registration_datahub.tasks.rdi_create import RdiXlsxCreateTask

    RdiXlsxCreateTask().execute(
        registration_data_import_id=registration_data_import_id,
        import_data_id=import_data_id,
        business_area_id=business_area,
    )


@app.task
def registration_kobo_import_task(registration_data_import_id, import_data_id, business_area):
    from hct_mis_api.apps.registration_datahub.tasks.rdi_create import RdiKoboCreateTask

    RdiKoboCreateTask().execute(
        registration_data_import_id=registration_data_import_id,
        import_data_id=import_data_id,
        business_area_id=business_area,
    )


@app.task
def registration_kobo_import_hourly_task():
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


@app.task
def registration_xlsx_import_hourly_task():
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


@app.task
def merge_registration_data_import_task(registration_data_import_id):
    from hct_mis_api.apps.registration_datahub.tasks.rdi_merge import RdiMergeTask

    RdiMergeTask().execute(registration_data_import_id)


@app.task
def rdi_deduplication_task(registration_data_import_id):
    from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
    from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub

    rdi_obj = RegistrationDataImportDatahub.objects.get(id=registration_data_import_id)

    DeduplicateTask.deduplicate_imported_individuals(registration_data_import_datahub=rdi_obj)
