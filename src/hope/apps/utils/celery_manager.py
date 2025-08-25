import logging
from functools import cached_property
from typing import Any

from celery import Task
from django.db.models import QuerySet

from models.core import BusinessArea
from models.registration_data import RegistrationDataImport
from hope.apps.utils.celery_utils import (
    get_all_celery_tasks,
    get_task_in_queue_or_running,
)

logger = logging.getLogger(__name__)


class BaseCeleryTaskManager:
    pending_status: str | None = None
    queue = "default"

    def __init__(self, business_area: BusinessArea | None = None) -> None:
        self.all_celery_tasks = get_all_celery_tasks(self.queue)
        self.business_area = business_area

    @property
    def pending_queryset(self) -> QuerySet:
        raise NotImplementedError("pending_queryset not implemented")

    @property
    def pending_queryset_for_business_area(self) -> QuerySet:
        if not self.business_area:
            return self.pending_queryset
        return self.pending_queryset.filter(business_area=self.business_area)

    @property
    def in_progress_queryset(self) -> QuerySet:
        raise NotImplementedError("in_progress_queryset not implemented")

    @property
    def in_progress_queryset_for_business_area(self) -> QuerySet:
        if not self.business_area:
            return self.in_progress_queryset
        return self.in_progress_queryset.filter(business_area=self.business_area)

    def execute(self) -> None:
        for model_object in self.in_progress_queryset_for_business_area.all():
            task_kwargs = self.get_task_kwargs(model_object)
            task = self.get_celery_task_by_kwargs(task_kwargs)
            if not (task and task.get("status") == "queued" or not task):
                continue
            logger.info(
                f"{self.in_progress_queryset.model.__name__}: id {model_object.id}"
                f" was in status IN PROGRESS importing should be PENDING because task was"
                f" {'not_in_queue' if not task else 'queued'}"
            )
            model_object.status = self.pending_status
            model_object.save()

        for model_object in self.pending_queryset_for_business_area.all():
            task_kwargs = self.get_task_kwargs(model_object)
            task = self.get_celery_task_by_kwargs(task_kwargs)
            if task:
                continue
            logger.info(
                f"{self.pending_queryset.model.__name__}: id {model_object.id}"
                f" was in status PENDING but not in celery queue"
            )
            logger.info(f"registration_xlsx_import_task scheduled with kwargs {task_kwargs}")
            self.celery_task.delay(**task_kwargs)

    def get_celery_task_by_kwargs(self, task_kwargs: dict) -> dict | None:
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

    @property
    def pending_queryset(self) -> QuerySet:
        return RegistrationDataImport.objects.filter(
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            data_source=RegistrationDataImport.XLS,
        )

    @property
    def in_progress_queryset(self) -> QuerySet:
        return RegistrationDataImport.objects.filter(
            status=RegistrationDataImport.IMPORTING,
            data_source=RegistrationDataImport.XLS,
        )

    @cached_property
    def celery_task(self) -> Task:
        from hope.apps.registration_datahub.celery_tasks import (
            registration_xlsx_import_task,
        )

        return registration_xlsx_import_task

    def get_task_kwargs(self, rdi: RegistrationDataImport) -> dict:
        return {
            "registration_data_import_id": str(rdi.id),
            "import_data_id": str(rdi.import_data_id),
            "business_area_id": str(rdi.business_area_id),
            "program_id": str(rdi.program_id),
        }
