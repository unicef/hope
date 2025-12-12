from django.db import models
from django_celery_boost.models import AsyncJobModel

from hope.models.file_temp import FileTemp
from hope.models.program import Program


class AsyncJob(AsyncJobModel):
    """Define the base async job used by all job types.

    - `program`, `file_temp`, and `errors` are generic fields reusable by multiple job types.
    - Different job types are implemented as proxy models on top of this one.
    """

    celery_task_name = "hope.apps.core.celery_tasks.async_job_task"

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="async_jobs",
    )
    file = models.ForeignKey(
        FileTemp,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="async_jobs",
    )
    errors = models.JSONField(default=dict, blank=True)

    class Meta(AsyncJobModel.Meta):
        app_label = "core"
        verbose_name = "Background Job"
        verbose_name_plural = "Background Jobs"
