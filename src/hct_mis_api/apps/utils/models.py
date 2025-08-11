import base64
import hashlib
import json
import logging
import sys
import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Sequence,
    T,
)

from django.conf import settings
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import classproperty
from django.utils.translation import gettext_lazy as _

import celery
from celery import states
from celery.contrib.abortable import AbortableAsyncResult
from concurrency.fields import IntegerVersionField
from model_utils.managers import SoftDeletableManager, SoftDeletableQuerySet
from model_utils.models import UUIDModel

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.utils import nested_getattr
from mptt.managers import TreeManager
from mptt.models import MPTTModel

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


class SoftDeletableIsVisibleManager(SoftDeletableManager):
    def get_queryset(self) -> "QuerySet":
        return super().get_queryset().filter(is_visible=True)


class MergedManager(models.Manager):
    def get_queryset(self) -> "QuerySet":
        return super().get_queryset().filter(rdi_merge_status="MERGED")


class PendingManager(models.Manager):
    def get_queryset(self) -> "QuerySet":
        return super().get_queryset().filter(rdi_merge_status="PENDING")


class SoftDeletableMergedManager(SoftDeletableManager):
    def get_queryset(self) -> "QuerySet":
        return super().get_queryset().filter(rdi_merge_status="MERGED")


class SoftDeletablePendingManager(SoftDeletableManager):
    def get_queryset(self) -> "QuerySet":
        return super().get_queryset().filter(rdi_merge_status="PENDING")


class SoftDeletableManagerMixin:
    """Manager that limits the queryset by default to show only not removed instances of model."""

    _queryset_class = SoftDeletableQuerySet

    def __init__(self, *args: Any, _emit_deprecation_warnings: bool = False, **kwargs: Any) -> None:
        self.emit_deprecation_warnings = _emit_deprecation_warnings
        super().__init__(*args, **kwargs)

    def get_queryset(self) -> "QuerySet":
        """Return queryset limited to not removed entries."""
        if self.emit_deprecation_warnings:
            warning_message = (
                f"{self.model.__class__.__name__}.objects model manager will include soft-deleted objects in an "
                f"upcoming release; please use {self.model.__class__.__name__}.available_objects to continue "
                "excluding soft-deleted objects. See "
                "https://django-model-utils.readthedocs.io/en/stable/models.html"
                "#softdeletablemodel for more information."
            )
            warnings.warn(warning_message, stacklevel=DeprecationWarning)

        kwargs = {"model": self.model, "using": self._db}
        if hasattr(self, "_hints"):
            kwargs["hints"] = self._hints

        return self._queryset_class(**kwargs).filter(is_removed=False)


class MergeStatusModel(models.Model):
    PENDING = "PENDING"
    MERGED = "MERGED"
    STATUS_CHOICE = (
        (PENDING, _("Pending")),
        (MERGED, _("Merged")),
    )

    rdi_merge_status = models.CharField(max_length=10, choices=STATUS_CHOICE, default=PENDING)

    class Meta:
        abstract = True


class SoftDeletableMergeStatusModel(MergeStatusModel):
    """Default manager returns only not-removed entries.

    An abstract base class model with a ``is_removed`` field that marks entries that are not going to be used
    anymore, but are kept in db for any reason.
    """

    is_removed = models.BooleanField(default=False, db_index=True)
    removed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    objects: models.Manager = SoftDeletableMergedManager(_emit_deprecation_warnings=True)  # MERGED - is_removed
    pending_objects: models.Manager = SoftDeletablePendingManager()  # PENDING - is_removed
    available_objects: models.Manager = SoftDeletableMergedManager()  # MERGED - is_removed
    all_merge_status_objects: models.Manager = SoftDeletableManager()  # MERGED + PENDING - is_removed
    all_objects: models.Manager = models.Manager()  # MERGED + PENDING + is_removed

    def delete(
        self, using: Any = None, keep_parents: bool = False, soft: bool = True, *args: Any, **kwargs: Any
    ) -> tuple[int, dict[str, int]]:
        """Soft delete object (set its ``is_removed`` field to True).

        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.removed_date = timezone.now()
            self.save(using=using)
            return 1, {self._meta.label: 1}

        return models.Model.delete(self, *args, **kwargs, using=using)


class AdminUrlMixin:
    @property
    def admin_url(self) -> str:
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name), args=[self.id])


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class TimeStampedUUIDModel(UUIDModel):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class SoftDeletionTreeManager(TreeManager):
    def get_queryset(self, *args: Any, **kwargs: Any) -> "QuerySet":
        """Return queryset limited to not removed entries."""
        return (
            super(TreeManager, self)
            .get_queryset(*args, **kwargs)
            .filter(is_removed=False)
            .order_by(self.tree_id_attr, self.left_attr)
        )


class SoftDeletionTreeModel(TimeStampedUUIDModel, MPTTModel):
    is_removed = models.BooleanField(default=False)

    class Meta:
        abstract = True

    objects = SoftDeletionTreeManager()
    all_objects = models.Manager()

    def delete(
        self, using: Any | None = None, soft: bool = True, *args: Any, **kwargs: Any
    ) -> tuple[int, dict[str, int]] | None:
        """Soft delete object (set its ``is_removed`` field to True).

        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.removed_date = timezone.now()
            self.save(using=using)
        else:
            return super().delete(*args, **kwargs, using=using)
        return None


class AbstractSession(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    SOURCE_MIS = "MIS"
    SOURCE_CA = "CA"
    # HOPE statueses
    STATUS_PROCESSING = "PROCESSING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"
    # CA statuses
    STATUS_NEW = "NEW"
    STATUS_READY = "READY"
    STATUS_EMPTY = "EMPTY"
    STATUS_LOADING = "LOADING"
    STATUS_ERRORED = "ERRORED"
    STATUS_IGNORED = "IGNORED"

    source = models.CharField(
        max_length=3,
        choices=((SOURCE_MIS, "HCT-MIS"), (SOURCE_CA, "Cash Assist")),
    )
    status = models.CharField(
        max_length=11,
        choices=(
            (STATUS_NEW, "New"),
            (STATUS_READY, "Ready"),
            (STATUS_PROCESSING, "Processing"),
            (STATUS_COMPLETED, "Completed"),
            (STATUS_FAILED, "Failed"),
            (STATUS_EMPTY, "Empty"),
            (STATUS_IGNORED, "Ignored"),
            (STATUS_LOADING, "Loading"),
            (STATUS_ERRORED, "Errored"),
        ),
    )
    last_modified_date = models.DateTimeField(auto_now=True)

    business_area = models.CharField(
        max_length=20,
        help_text="""Same as the business area set on program, but
            this is set as the same value, and all other
            models this way can get easy access to the business area
            via the session.""",
    )

    sentry_id = models.CharField(max_length=100, default="", blank=True, null=True)
    traceback = models.TextField(default="", blank=True, null=True)

    class Meta:
        abstract = True

    def process_exception(self, exc: BaseException, request: HttpRequest | None = None) -> int | None:
        try:
            from sentry_sdk import capture_exception

            err = capture_exception(exc)
            self.sentry_id = err
        except Exception:
            pass

        try:
            from django.views.debug import ExceptionReporter

            reporter = ExceptionReporter(request, *sys.exc_info())
            self.traceback = reporter.get_traceback_html()
        except Exception as e:
            logger.exception(e)
            self.traceback = "N/A"
        finally:
            self.status = self.STATUS_FAILED

        return self.sentry_id

    def __str__(self) -> str:
        return f"#{self.id} on {self.timestamp}"


class AbstractSyncable(models.Model):
    last_sync_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class SoftDeletableDefaultManagerModel(models.Model):
    """Default manager returns only not-removed entries.

    An abstract base class model with a ``is_removed`` field that
    marks entries that are not going to be used anymore, but are
    kept in db for any reason.
    """

    is_removed = models.BooleanField(default=False)

    class Meta:
        abstract = True

    active_objects = SoftDeletableManager()
    objects = models.Manager()

    def delete(
        self, using: Any = None, keep_parents: bool = False, soft: bool = True, *args: Any, **kwargs: Any
    ) -> tuple[int, dict[str, int]]:
        """Soft delete object (set its ``is_removed`` field to True).

        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.save(using=using)
            return 1, {self._meta.label: 1}

        return super().delete(*args, **kwargs, using=using)


class ConcurrencyModel(models.Model):
    version = IntegerVersionField()

    class Meta:
        abstract = True


class UnicefIdentifiedModel(models.Model):
    unicef_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        if self._state.adding or self.unicef_id is None:
            # due to existence of "CREATE TRIGGER" in migrations
            self.refresh_from_db(fields=["unicef_id"])


class SignatureManager(models.Manager):
    def bulk_create_with_signature(self, objs: Iterable[T], *args: Any, **kwargs: Any) -> list[T]:
        from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
            bulk_create_payment_snapshot_data,
        )

        created_objects = super().bulk_create(objs, *args, **kwargs)
        bulk_create_payment_snapshot_data([x.id for x in created_objects])
        for obj in created_objects:
            obj.update_signature_hash()
        super().bulk_update(created_objects, ["signature_hash"])
        return created_objects

    def bulk_update_with_signature(self, objs: Iterable[T], fields: Sequence[str], *args: Any, **kwargs: Any) -> int:
        for obj in objs:
            if any(field in fields for field in obj.signature_fields):
                obj.update_signature_hash()
        new_fields = set(fields)
        if "signature_hash" not in fields:
            new_fields.add("signature_hash")
        return super().bulk_update(objs, list(new_fields), *args, **kwargs)


class SignatureMixin(models.Model):
    signature_hash = models.CharField(max_length=40, blank=True, editable=False)
    signature_manager = SignatureManager()

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.update_signature_hash()
        super().save(*args, **kwargs)

    def _normalize(self, name: str, value: Any) -> Any:
        if "." in name:
            return value
        field = self.__class__._meta.get_field(name)
        if isinstance(field, models.DecimalField) and value is not None:
            return f"{{:.{field.decimal_places}f}}".format(value)
        return value

    def update_signature_hash(self) -> None:
        if hasattr(self, "signature_fields") and isinstance(self.signature_fields, list | tuple):
            sha1 = hashlib.sha1()
            salt = settings.SECRET_KEY
            sha1.update(salt.encode("utf-8"))

            for field_name in self.signature_fields:
                value = nested_getattr(self, field_name, None)
                value = self._normalize(field_name, value)
                sha1.update(str(value).encode("utf-8"))
            self.signature_hash = sha1.hexdigest()
        else:
            raise ValueError("Define 'signature_fields' in class for SignatureMixin")


class CeleryEnabledModel(models.Model):  # pragma: no cover
    # QUEUED (task exists in Redis but unkonw to Celery)
    # CANCELED (task is canceled BEFORE worker fetch it)
    # PENDING (waiting for execution or unknown task id)
    # STARTED (task has been started)
    # SUCCESS (task executed successfully)
    # FAILURE (task execution resulted in exception)
    # RETRY (task is being retried)
    # REVOKED (task has been revoked)
    CELERY_STATUS_SCHEDULED = frozenset({states.PENDING, states.RECEIVED, states.STARTED, states.RETRY, "QUEUED"})
    CELERY_STATUS_QUEUED = "QUEUED"
    CELERY_STATUS_CANCELED = "CANCELED"
    CELERY_STATUS_RECEIVED = states.RECEIVED
    CELERY_STATUS_NOT_SCHEDULED = "NOT_SCHEDULED"
    CELERY_STATUS_STARTED = states.STARTED
    CELERY_STATUS_SUCCESS = states.SUCCESS
    CELERY_STATUS_FAILURE = states.FAILURE
    CELERY_STATUS_RETRY = states.RETRY
    CELERY_STATUS_REVOKED = states.REVOKED

    celery_tasks_results_ids = models.JSONField(
        default=dict, blank=True, help_text="Current (active) AsyncResult ids for celery tasks."
    )

    celery_task_names: dict[str, str] = {}

    class Meta:
        abstract = True

    def _get_task_name(self, task_name: str | None = None) -> str:
        if task_name:
            if task_name not in self.celery_task_names:
                raise ValueError(f"Task '{task_name}' is not defined in celery_task_names.")
            return task_name

        if len(self.celery_task_names) == 1:
            return next(iter(self.celery_task_names))

        raise ValueError("Multiple tasks defined in celery_task_names. Please specify which task to use.")

    def get_celery_queue_position(self, task_name: str | None = None) -> int:
        from hct_mis_api.apps.core.celery import app

        task_name = self._get_task_name(task_name)
        task_id = self.celery_tasks_results_ids.get(task_name)
        if not task_id:
            return 0

        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, -1)
        for i, task in enumerate(tasks, 1):
            j = json.loads(task)
            if j["headers"]["id"] == task_id:
                return i
        return 0

    def celery_queue_status(self) -> "dict[str, int]":
        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, 1)
            revoked = list(conn.default_channel.client.smembers(settings.CELERY_TASK_REVOKED_QUEUE))
            pending = len(tasks)
            canceled = 0
            pending_tasks = [json.loads(task)["headers"]["id"].encode() for task in tasks]
            for task_id in pending_tasks:
                if task_id in revoked:
                    pending -= 1
                    canceled += 1

            for rem in revoked:
                if rem not in pending_tasks:
                    conn.default_channel.client.srem(settings.CELERY_TASK_REVOKED_QUEUE, rem)
            return {"size": len(tasks), "pending": pending, "canceled": canceled, "revoked": len(revoked)}

    def get_async_result(self, task_name: str | None = None) -> "AbortableAsyncResult|None":
        task_name = self._get_task_name(task_name)
        task_id = self.celery_tasks_results_ids.get(task_name)
        if task_id:
            return AbortableAsyncResult(task_id, app=celery.current_app)
        return None

    def get_queue_info(self, task_name: str | None = None) -> "dict[str, Any]":
        task_name = self._get_task_name(task_name)
        async_result = self.get_async_result(task_name)
        if not async_result:
            return {"id": "NotFound"}

        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, -1)

        for task in tasks:
            j = json.loads(task)
            if j["headers"]["id"] == async_result.id:
                j["body"] = json.loads(base64.b64decode(j["body"]))
                return j
        return {"id": "NotFound"}

    def get_task_info(self, task_name: str | None = None) -> dict[str, Any] | None:
        task_name = self._get_task_name(task_name)
        async_result = self.get_async_result(task_name)
        if async_result:
            info = async_result._get_task_meta()
            result, task_status = info["result"], info["status"]
            if task_status == self.CELERY_STATUS_SUCCESS:
                started_at = result.get("start_time", 0)
            else:
                started_at = 0
            last_update = info["date_done"]
            if isinstance(result, Exception):
                error = str(result)
            elif task_status == self.CELERY_STATUS_CANCELED:
                error = _("Query execution cancelled.")
            else:
                error = ""

            if task_status == self.CELERY_STATUS_SUCCESS and not error:
                query_result_id = result
            else:
                query_result_id = None
            return {
                **info,
                "last_update": last_update,
                "started_at": started_at,
                "status": task_status,
                "error": error,
                "query_result_id": query_result_id,
            }
        return None

    @classproperty
    def task_handlers(cls) -> dict[str, Callable[[Any], Any]]:
        import importlib

        handlers = {}
        for name, path in cls.celery_task_names.items():
            module_path, func_name = path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            handlers[name] = getattr(module, func_name)
        return handlers

    def is_queued(self, task_name: str | None = None) -> bool:
        from hct_mis_api.apps.core.celery import app

        task_name = self._get_task_name(task_name)
        task_id = self.celery_tasks_results_ids.get(task_name)
        if not task_id:
            return False

        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, -1)
        for task in tasks:
            j = json.loads(task)
            if j["headers"]["id"] == task_id:
                return True
        return False

    def is_canceled(self, task_name: str | None = None) -> bool:
        task_name = self._get_task_name(task_name)
        task_id = self.celery_tasks_results_ids.get(task_name)
        if not task_id:
            return False
        with app.pool.acquire(block=True) as conn:
            return conn.default_channel.client.sismember(settings.CELERY_TASK_REVOKED_QUEUE, task_id)

    def get_celery_status(self, task_name: str | None = None) -> str:
        try:
            task_name = self._get_task_name(task_name)
            task_id = self.celery_tasks_results_ids.get(task_name)
            if task_id:
                if self.is_canceled(task_name):
                    return self.CELERY_STATUS_CANCELED

                async_result = self.get_async_result(task_name)
                result = async_result.state
                if result == states.PENDING:
                    if self.is_queued(task_name):
                        result = self.CELERY_STATUS_QUEUED
                    else:
                        result = self.CELERY_STATUS_NOT_SCHEDULED
            else:
                result = self.CELERY_STATUS_NOT_SCHEDULED
            return result
        except Exception as e:
            return str(e)

    def queue(self, task_name: str | None = None) -> str | None:
        task_name = self._get_task_name(task_name)
        if self.get_celery_status(task_name) not in self.CELERY_STATUS_SCHEDULED:
            res = self.task_handlers[task_name].delay(self.pk)
            self.celery_tasks_results_ids[task_name] = res.id
            self.save(update_fields=["celery_tasks_results_ids"])
            return res
        return None

    def terminate(self, task_name: str | None = None) -> None:
        task_name = self._get_task_name(task_name)
        task_id = self.celery_tasks_results_ids.get(task_name)
        if not task_id:
            return

        if self.get_celery_status(task_name) in ["QUEUED", "PENDING"]:
            with app.pool.acquire(block=True) as conn:
                conn.default_channel.client.sadd(settings.CELERY_TASK_REVOKED_QUEUE, task_id, task_id)
        else:
            app.control.revoke(task_id, terminate=True)

    @classmethod
    def discard_all(cls) -> None:
        app.control.discard_all()
        cls.objects.update(celery_tasks_results_ids={})
        with app.pool.acquire(block=True) as conn:
            conn.default_channel.client.delete(settings.CELERY_TASK_REVOKED_QUEUE)

    @classmethod
    def purge(cls) -> None:
        app.control.purge()

    @property
    def celery_statuses(self) -> dict[str, str]:
        return {name: self.get_celery_status(name) for name in self.celery_task_names}


class InternalDataFieldModel(models.Model):
    internal_data = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
