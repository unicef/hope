import logging
from functools import cached_property
from typing import Any, Optional

from django.db.models import QuerySet

from celery import Task

from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub
from hct_mis_api.apps.utils.celery_utils import (
    get_all_celery_tasks,
    get_task_in_queue_or_running,
)

logger = logging.getLogger(__name__)


class BaseCeleryTaskManager:
    pending_status: Optional[str] = None
    pending_queryset: Optional[QuerySet] = None
    in_progress_queryset: Optional[QuerySet] = None
    queue = "default"

    def __init__(self) -> None:
        self.all_celery_tasks = get_all_celery_tasks(self.queue)

    def execute(self) -> None:
        for model_object in self.in_progress_queryset:
            task_kwargs = self.get_task_kwargs(model_object)
            task = self.get_celery_task_by_kwargs(task_kwargs)
            if not (task and task.get("status") == "queued" or not task):
                continue
            logger.info(
                f"{self.in_progress_queryset.model.__name__}: id {model_object.id} was in status IN PROGRESS importing should be PENDING because task was {'not_in_queue' if not task else 'queued'}"
            )
            model_object.status = self.pending_status
            model_object.save()

        for model_object in self.pending_queryset:
            task_kwargs = self.get_task_kwargs(model_object)
            task = self.get_celery_task_by_kwargs(task_kwargs)
            if task:
                continue
            logger.info(
                f"{self.pending_queryset.model.__name__}: id {model_object.id} was in status PENDING but not in celery queue"
            )
            logger.info(f"registration_xlsx_import_task scheduled with kwargs {task_kwargs}")
            self.celery_task.delay(**task_kwargs)

    def get_celery_task_by_kwargs(self, task_kwargs: dict) -> Optional[dict]:
        return get_task_in_queue_or_running(
            name=self.celery_task.name,
            all_celery_tasks=self.all_celery_tasks,
            kwargs=task_kwargs,
        )

    @cached_property
    def celery_task(self) -> Task:
        raise NotImplementedError

    def get_task_kwargs(self, model_object: Any) -> dict:
        raise NotImplementedError


class RegistrationDataXlsxImportCeleryManager(BaseCeleryTaskManager):
    pending_status = RegistrationDataImport.IMPORT_SCHEDULED
    pending_queryset = RegistrationDataImport.objects.filter(
        status=RegistrationDataImport.IMPORT_SCHEDULED, data_source=RegistrationDataImport.XLS
    )
    in_progress_queryset = RegistrationDataImport.objects.filter(
        status=RegistrationDataImport.IMPORTING, data_source=RegistrationDataImport.XLS
    )

    @cached_property
    def celery_task(self) -> Task:
        from hct_mis_api.apps.registration_datahub.celery_tasks import (
            registration_xlsx_import_task,
        )

        return registration_xlsx_import_task

    def get_task_kwargs(self, rdi: RegistrationDataImport) -> dict:
        rdi_datahub = RegistrationDataImportDatahub.objects.get(hct_id=rdi.id)
        return {
            "registration_data_import_id": str(rdi_datahub.id),
            "import_data_id": str(rdi_datahub.import_data_id),
            "business_area_id": str(rdi.business_area_id),
        }
