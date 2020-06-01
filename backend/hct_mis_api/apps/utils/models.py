# Create your models here.
from django.db import models
from model_utils.models import UUIDModel
from mptt.managers import TreeManager
from mptt.models import MPTTModel


class TimeStampedUUIDModel(UUIDModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
            self.save(using=using)
        else:
            return super().delete(using=using, *args, **kwargs)


class AbstractSession(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    SOURCE_MIS = "MIS"
    SOURCE_CA = "CA"
    STATUS_NEW = "NEW"
    STATUS_READY = "READY"
    STATUS_PROCESSING = "PROCESSING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"

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
        ),
    )
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
