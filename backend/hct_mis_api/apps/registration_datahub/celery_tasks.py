from hct_mis_api.apps.core.celery import app


@app.task
def registration_xlsx_import_task(registration_data_import_id, import_data_id, business_area):
    from hct_mis_api.apps.registration_datahub.tasks.rdi_create import RdiXlsxCreateTask

    RdiXlsxCreateTask().execute(
        registration_data_import_id=registration_data_import_id,
        import_data_id=import_data_id,
        business_area_id=business_area,
    )
