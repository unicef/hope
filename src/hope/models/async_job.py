from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_celery_boost.models import AsyncJobModel


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
    def create_for_instance(cls, instance: models.Model, *, job_name: str | None = None, **kwargs) -> "AsyncJob":
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
            **payload,
        }

        job = (
            cls.create_for_instance(instance, **job_payload)
            if instance is not None
            else cls.objects.create(**job_payload)
        )
        job.queue()
        return job

    def save(self, *args, **kwargs):
        if not self.job_name:
            self.job_name = self.default_job_name(self.action)
        super().save(*args, **kwargs)


class AsyncRetryJob(AsyncJob):
    celery_task_name = "hope.apps.core.celery_tasks.async_retry_job_task"

    class Meta:
        proxy = True
        app_label = "core"
        verbose_name = "Retry Asynchronous Job"
        verbose_name_plural = "Retry Asynchronous Jobs"
