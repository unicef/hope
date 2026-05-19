from typing import Any, TypeVar, cast

from concurrency.api import concurrency_disable_increment
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils import timezone
from django_celery_boost.models import AsyncJobModel
from django_celery_boost.signals import task_queued

from hope.apps.core.celery import CELERY_QUEUE_DEFAULT, CELERY_QUEUE_PERIODIC

AsyncJobT = TypeVar("AsyncJobT", bound="BaseAsyncJob")


class BaseAsyncJob(AsyncJobModel):
    """Shared async job fields and behavior for both user and periodic queues."""

    celery_task_name = "hope.apps.core.celery_tasks.async_job_task"
    program = models.ForeignKey(
        "program.Program",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="+",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="+",
    )
    object_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")
    job_name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    errors = models.JSONField(default=dict, blank=True)

    class Meta(AsyncJobModel.Meta):
        abstract = True
        app_label = "core"
        indexes = [
            models.Index(fields=["content_type", "object_id", "job_name"]),
        ]

    @staticmethod
    def default_job_name(action: str | None) -> str:
        if not action:
            return ""

        job_name = action.rsplit(".", 1)[-1]
        if job_name.endswith("_action"):
            return job_name.removesuffix("_action")
        return job_name

    @classmethod
    def create_for_instance(
        cls: type[AsyncJobT],
        instance: models.Model,
        *,
        job_name: str | None = None,
        **kwargs: Any,
    ) -> AsyncJobT:
        if instance.pk is None:
            raise ValueError("Cannot create an async job for an unsaved instance.")

        if "program" not in kwargs and hasattr(instance, "program"):
            kwargs["program"] = instance.program

        if not job_name:
            job_name = cls.default_job_name(kwargs.get("action"))

        return cls.objects.create(
            content_object=instance,
            job_name=job_name,
            **kwargs,
        )

    @classmethod
    def queue_task(
        cls: type[AsyncJobT],
        *,
        action: str,
        instance: models.Model | None = None,
        **payload: Any,
    ) -> AsyncJobT:
        job_name = payload.pop("job_name", None)
        config = payload.pop("config", None) or {}
        repeatable = payload.pop("repeatable", True)

        job_payload = {
            "job_name": job_name or cls.default_job_name(action),
            "type": AsyncJobModel.JobType.JOB_TASK,
            "repeatable": repeatable,
            "action": action,
            "config": config,
            **payload,
        }

        with transaction.atomic():
            job = (
                cls.create_for_instance(instance, **job_payload)
                if instance is not None
                else cls.objects.create(**job_payload)
            )
            transaction.on_commit(job.queue)

        return job

    def queue(self, use_version: bool = True) -> str | None:
        if self.task_status in self.ACTIVE_STATUSES:
            return None

        job_name = self.job_name or self.default_job_name(self.action)
        res = self.task_handler.apply_async(
            args=(self._meta.label_lower, self.pk, self.version if use_version else None),
            queue=self.celery_task_queue,
            shadow=job_name,
            headers={
                "async_job_id": str(self.pk),
                "async_job_model": self._meta.label_lower,
                "job_name": job_name,
                "action": self.action or "",
                "program_id": str(self.program_id) if self.program_id else "",
                "object_id": self.object_id or "",
                "queue_name": self.celery_task_queue,
            },
            argsrepr=f"(async_job_model={self._meta.label_lower!r}, async_job_id={self.pk}, job_name={job_name!r})",
        )
        self.set_queued(res)
        return cast("str | None", res.id)

    def set_queued(self, result: Any) -> None:
        previous_async_result_id = cast("str | None", getattr(self, "curr_async_result_id", None))
        with concurrency_disable_increment(self):
            self.last_async_result_id = previous_async_result_id
            self.curr_async_result_id = cast("str", result.id)
            self.datetime_queued = timezone.now()
            self.save(update_fields=["last_async_result_id", "curr_async_result_id", "datetime_queued"])
            task_queued.send(sender=self.__class__, task=self)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.job_name:
            self.job_name = self.default_job_name(self.action)
        super().save(*args, **kwargs)


class AsyncJob(BaseAsyncJob):
    celery_task_queue = CELERY_QUEUE_DEFAULT

    class Meta:
        app_label = "core"
        verbose_name = "Asynchronous Job"
        verbose_name_plural = "Asynchronous Jobs"
        permissions = (("recover_missing_async_job", "Can recover missing async jobs"),)
        indexes = [
            models.Index(fields=["content_type", "object_id", "job_name"]),
        ]


class PeriodicAsyncJob(BaseAsyncJob):
    celery_task_queue = CELERY_QUEUE_PERIODIC

    class Meta:
        app_label = "core"
        verbose_name = "Periodic Asynchronous Job"
        verbose_name_plural = "Periodic Asynchronous Jobs"
        indexes = [
            models.Index(fields=["content_type", "object_id", "job_name"]),
        ]


class AsyncRetryJob(AsyncJob):
    celery_task_name = "hope.apps.core.celery_tasks.async_retry_job_task"

    class Meta:
        proxy = True
        app_label = "core"
        verbose_name = "Retry Asynchronous Job"
        verbose_name_plural = "Retry Asynchronous Jobs"


class PeriodicAsyncRetryJob(PeriodicAsyncJob):
    celery_task_name = "hope.apps.core.celery_tasks.async_retry_job_task"

    class Meta:
        proxy = True
        app_label = "core"
        verbose_name = "Periodic Retry Asynchronous Job"
        verbose_name_plural = "Periodic Retry Asynchronous Jobs"
