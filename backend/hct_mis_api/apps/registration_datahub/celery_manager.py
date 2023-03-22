import abc
import logging

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub
from hct_mis_api.apps.registration_datahub.celery_tasks import registration_xlsx_import_task, \
    merge_registration_data_import_task

logger = logging.getLogger(__name__)


class BaseCeleryManager(abc.ABC):
    model = ""
    model_status = ""
    task = ""
    lookup = ""

    def create_obj_list(self):
        return list(self.model.objects.filter(status=self.model_status).values_list("id", flat=True))

    @staticmethod
    def get_celery_tasks():
        i = app.control.inspect()
        return i.scheduled(), i.active(), i.reserved()

    @abc.abstractmethod
    def create_kwargs(self, rdi_ids_to_run):
        pass

    def execute(self):
        list_to_check = self.create_obj_list()
        celery_ids_list = []

        for group in [*self.get_celery_tasks()]:
            for _, task_list in group.items():
                for task in task_list:
                    task_name = task["name"].split(".")[-1]
                    if task_name == self.task.__name__:
                        celery_ids_list.append(task["kwargs"].get(self.lookup))

        rdi_ids_to_run = []
        for rdi_id in list_to_check:
            if rdi_id not in celery_ids_list:
                rdi_ids_to_run.append(rdi_id)

        if not rdi_ids_to_run:
            logger.info(f"Found no {self.model.__name__} with status {self.model_status}")

        task_kwargs = self.create_kwargs(rdi_ids_to_run)
        for kwargs in task_kwargs:
            self.task.delay(**kwargs)
            logger.info(
                f"Celery task run for {self.model.__name__} id: {kwargs[self.lookup]} from periodic task scheduler")


class RdiImportCeleryManager(BaseCeleryManager):
    model = RegistrationDataImport
    model_status = RegistrationDataImport.IMPORTING
    task = registration_xlsx_import_task
    lookup = "registration_data_import_id"

    def create_kwargs(self, rdi_ids_to_run):
        registration_xlsx_import_task_kwargs = []
        for rdi_id in rdi_ids_to_run:
            rdi = RegistrationDataImport.objects.get(id=rdi_id)
            rdi_datahub = RegistrationDataImportDatahub.objects.get(id=str(rdi.datahub_id))
            kwargs = {
                'registration_data_import_id': str(rdi_datahub.id),
                'import_data_id': str(rdi_datahub.import_data_id),
                'business_area_id': str(rdi.business_area.id)
            }
            registration_xlsx_import_task_kwargs.append(kwargs)
        return registration_xlsx_import_task_kwargs


class RdiMergeCeleryManager(BaseCeleryManager):
    model = RegistrationDataImport
    model_status = RegistrationDataImport.MERGING
    task = merge_registration_data_import_task
    lookup = "registration_data_import_id"

    def create_kwargs(self, rdi_ids_to_run):
        merge_registration_data_import_task_kwargs = []
        for rdi_id in rdi_ids_to_run:
            merge_registration_data_import_task_kwargs.append({'registration_data_import_id': str(rdi_id)})
        return merge_registration_data_import_task_kwargs


class SendTPCeleryManager(BaseCeleryManager):

    def create_kwargs(self, rdi_ids_to_run):
        pass


rdi_import_celery_manager = RdiImportCeleryManager()
rdi_merge_celery_manager = RdiMergeCeleryManager()
send_tp_celery_manager = SendTPCeleryManager()
