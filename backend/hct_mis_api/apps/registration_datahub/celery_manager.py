import logging

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub
from hct_mis_api.apps.registration_datahub.celery_tasks import registration_xlsx_import_task

logger = logging.getLogger(__name__)


def check_rdi_imports() -> None:
    i = app.control.inspect()
    scheduled = i.scheduled()
    active = i.active()
    reserved = i.reserved()

    importing_rdi_list = list(
        RegistrationDataImport.objects.filter(status=RegistrationDataImport.IMPORTING).values_list("id", flat=True)
    )

    celery_rdi_ids_list = []
    for group in (scheduled, active, reserved):
        for _, task_list in group.items():
            for task in task_list:
                task_name = task["name"].split(".")[-1]
                if task_name == "registration_xlsx_import_task":
                    celery_rdi_ids_list.append(task["kwargs"].get("registration_data_import_id"))

    rdi_to_run = []
    for rdi_id in importing_rdi_list:
        if rdi_id not in celery_rdi_ids_list:
            rdi_to_run.append(rdi_id)

    if not rdi_to_run:
        logger.info("No RDI in status IMPORTING found")

    registration_xlsx_import_task_kwargs = []
    for rdi_id in rdi_to_run:
        rdi = RegistrationDataImport.objects.get(id=rdi_id)
        rdi_datahub = RegistrationDataImportDatahub.objects.get(id=str(rdi.datahub_id))
        kwargs = {
            'registration_data_import_id': str(rdi_datahub.id),
            'import_data_id': str(rdi_datahub.import_data_id),
            'business_area_id': str(rdi.business_area.id)
        }
        registration_xlsx_import_task_kwargs.append(kwargs)

    for kwargs in registration_xlsx_import_task_kwargs:
        registration_xlsx_import_task.delay(**kwargs)
        logger.info(f"RDI import task run for id {kwargs['registration_data_import_id']} from periodic task scheduler")