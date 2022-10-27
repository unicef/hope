# Create your models here.
import logging
import sys

from django.db import models
from django.utils import timezone

from concurrency.fields import IntegerVersionField
from model_utils.managers import SoftDeletableManager
from model_utils.models import UUIDModel

from mptt.managers import TreeManager
from mptt.models import MPTTModel

logger = logging.getLogger(__name__)


class TimeStampedUUIDModel(UUIDModel):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class SoftDeletableModelWithDate(models.Model):
    """
    An abstract base class model with a ``is_removed`` field that
    marks entries that are not going to be used anymore, but are
    kept in db for any reason.
    Default manager returns only not-removed entries.
    """

    is_removed = models.BooleanField(default=False, db_index=True)
    removed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    objects = SoftDeletableManager()
    all_objects = models.Manager()

    def delete(self, using=None, soft=True, *args, **kwargs):
        """
        Soft delete object (set its ``is_removed`` field to True).
        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.removed_date = timezone.now()
            self.save(using=using)
        else:
            return super().delete(using=using, *args, **kwargs)


class SoftDeletionTreeManager(TreeManager):
    def get_queryset(self, *args, **kwargs):
        """
        Return queryset limited to not removed entries.
        """
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

    def delete(self, using=None, soft=True, *args, **kwargs):
        """
        Soft delete object (set its ``is_removed`` field to True).
        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.removed_date = timezone.now()
            self.save(using=using)
        else:
            return super().delete(using=using, *args, **kwargs)


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

    def process_exception(self, exc, request=None):
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

    def __str__(self):
        return f"#{self.id} on {self.timestamp}"


class AbstractSyncable(models.Model):
    last_sync_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class SoftDeletableDefaultManagerModel(models.Model):
    """
    An abstract base class model with a ``is_removed`` field that
    marks entries that are not going to be used anymore, but are
    kept in db for any reason.
    Default manager returns only not-removed entries.
    """

    is_removed = models.BooleanField(default=False)

    class Meta:
        abstract = True

    active_objects = SoftDeletableManager()
    objects = models.Manager()

    def delete(self, using=None, soft=True, *args, **kwargs):
        """
        Soft delete object (set its ``is_removed`` field to True).
        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.save(using=using)
        else:
            return super().delete(using=using, *args, **kwargs)


class ConcurrencyModel(models.Model):
    version = IntegerVersionField()

    class Meta:
        abstract = True


class UnicefIdentifiedModel(models.Model):
    unicef_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self._state.adding:
            # due to existence of "CREATE TRIGGER" in migrations
            self.refresh_from_db(fields=["unicef_id"])
