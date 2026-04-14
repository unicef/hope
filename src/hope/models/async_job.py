from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_celery_boost.models import AsyncJobModel

from hope.apps.core.celery import CELERY_QUEUE_DEFAULT, CELERY_QUEUE_PERIODIC


class AsyncJob(AsyncJobModel):
    """Define the base async job used by all job types.

    - `program', `errors`, 'content_object' are generic fields reusable by multiple job types.
    - Different job types are implemented as proxy models on top of this one.
    """

    celery_task_name = "hope.apps.core.celery_tasks.async_job_task"

    program = models.ForeignKey(
        "program.Program",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="async_jobs",
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
    queue_name = models.CharField(
        max_length=255,
        default=CELERY_QUEUE_DEFAULT,
        db_index=True,
    )
    errors = models.JSONField(default=dict, blank=True)

    class Meta(AsyncJobModel.Meta):
        app_label = "core"
        verbose_name = "Asynchronous Job"
        verbose_name_plural = "Asynchronous Jobs"
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
    def create_for_instance(cls, instance: models.Model, *, job_name: str | None = None, **kwargs: Any) -> "AsyncJob":
        if instance.pk is None:
            raise ValueError("Cannot create an async job for an unsaved instance.")

        if "program" not in kwargs and hasattr(instance, "program"):
            kwargs["program"] = instance.program

        if not job_name:
            job_name = cls.default_job_name(kwargs.get("action"))

        kwargs.setdefault("queue_name", cls.celery_task_queue)

        return cls.objects.create(
            content_object=instance,
            job_name=job_name,
            **kwargs,
        )

    @classmethod
    def queue_task(
        cls,
        *,
        action: str,
        instance: models.Model | None = None,
        **payload: Any,
    ) -> "AsyncJob":
        job_name = payload.pop("job_name", None)
        config = payload.pop("config", None) or {}
        repeatable = payload.pop("repeatable", True)

        job_payload = {
            "job_name": job_name or cls.default_job_name(action),
            "type": AsyncJobModel.JobType.JOB_TASK,
            "repeatable": repeatable,
            "action": action,
            "config": config,
            "queue_name": payload.pop("queue_name", cls.celery_task_queue),
            **payload,
        }

        job = (
            cls.create_for_instance(instance, **job_payload)
            if instance is not None
            else cls.objects.create(**job_payload)
        )
        job.queue()
        return job

    def queue(self, use_version: bool = True) -> str | None:
        if self.task_status in self.ACTIVE_STATUSES:
            return None

        res = self.task_handler.apply_async(
            args=(self.pk, self.version if use_version else None),
            queue=self.queue_name,
        )
        self.set_queued(res)
        return self.curr_async_result_id

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.job_name:
            self.job_name = self.default_job_name(self.action)
        if not self.queue_name:
            self.queue_name = self.celery_task_queue
        super().save(*args, **kwargs)


class AsyncRetryJob(AsyncJob):
    celery_task_name = "hope.apps.core.celery_tasks.async_retry_job_task"

    class Meta:
        proxy = True
        app_label = "core"
        verbose_name = "Retry Asynchronous Job"
        verbose_name_plural = "Retry Asynchronous Jobs"


class PeriodicAsyncJob(AsyncJob):
    celery_task_queue = CELERY_QUEUE_PERIODIC

    class Meta:
        proxy = True
        app_label = "core"
        verbose_name = "Periodic Asynchronous Job"
        verbose_name_plural = "Periodic Asynchronous Jobs"


class PeriodicAsyncRetryJob(AsyncRetryJob):
    celery_task_queue = CELERY_QUEUE_PERIODIC

    class Meta:
        proxy = True
        app_label = "core"
        verbose_name = "Periodic Retry Asynchronous Job"
        verbose_name_plural = "Periodic Retry Asynchronous Jobs"
