from enum import Enum, auto, unique
import hashlib
import logging
from typing import TYPE_CHECKING, Any, Iterable, Sequence, T

from concurrency.fields import IntegerVersionField
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.managers import SoftDeletableManagerMixin
from model_utils.models import UUIDModel
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from hope.apps.core.utils import nested_getattr

if TYPE_CHECKING:
    from django.db.models import QuerySet


logger = logging.getLogger(__name__)


class BulkSignalsManagerMixin:
    def bulk_create(self, objs, *args, **kwargs):
        val = super().bulk_create(objs, *args, **kwargs)
        from hope.apps.core.signals import post_bulk_create

        post_bulk_create.send(sender=self.model, instances=objs, **kwargs)
        return val

    def bulk_update(self, objs, *args, **kwargs):
        val = super().bulk_update(objs, *args, **kwargs)
        from hope.apps.core.signals import post_bulk_update

        post_bulk_update.send(sender=self.model, instances=objs, **kwargs)
        return val


class BaseManager(BulkSignalsManagerMixin, models.Manager):
    pass


class SoftDeletableManager(BulkSignalsManagerMixin, SoftDeletableManagerMixin, models.Manager):
    pass


class SoftDeletableIsVisibleManager(SoftDeletableManager):
    def get_queryset(self) -> "QuerySet":
        return super().get_queryset().filter(is_visible=True)


class MergedManager(BulkSignalsManagerMixin, models.Manager):
    def get_queryset(self) -> "QuerySet":
        return super().get_queryset().filter(rdi_merge_status="MERGED")


class PendingManager(BulkSignalsManagerMixin, models.Manager):
    def get_queryset(self) -> "QuerySet":
        return super().get_queryset().filter(rdi_merge_status="PENDING")


class SoftDeletableMergedManager(SoftDeletableManager):
    def get_queryset(self) -> "QuerySet":
        return super().get_queryset().filter(rdi_merge_status="MERGED")


class SoftDeletablePendingManager(SoftDeletableManager):
    def get_queryset(self) -> "QuerySet":
        return super().get_queryset().filter(rdi_merge_status="PENDING")


class MergeStatusModel(models.Model):
    PENDING = "PENDING"
    MERGED = "MERGED"
    STATUS_CHOICE = (
        (PENDING, _("Pending")),
        (MERGED, _("Merged")),
    )

    rdi_merge_status = models.CharField(max_length=10, choices=STATUS_CHOICE, default=PENDING, blank=True)

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
    all_objects: models.Manager = BaseManager()  # MERGED + PENDING + is_removed

    def delete(
        self,
        using: Any = None,
        keep_parents: bool = False,
        soft: bool = True,
        *args: Any,
        **kwargs: Any,
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
        return reverse(
            "admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name),
            args=[self.id],
        )


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
    all_objects = BaseManager()

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

    active_objects = SoftDeletableManager()
    objects = BaseManager()

    class Meta:
        abstract = True

    def delete(
        self,
        using: Any = None,
        keep_parents: bool = False,
        soft: bool = True,
        *args: Any,
        **kwargs: Any,
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
        from hope.apps.payment.services.payment_household_snapshot_service import (
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
            sha1 = hashlib.sha1()  # noqa
            salt = settings.SECRET_KEY
            sha1.update(salt.encode("utf-8"))

            for field_name in self.signature_fields:
                value = nested_getattr(self, field_name, None)
                value = self._normalize(field_name, value)
                sha1.update(str(value).encode("utf-8"))
            self.signature_hash = sha1.hexdigest()
        else:
            raise ValueError("Define 'signature_fields' in class for SignatureMixin")


class InternalDataFieldModel(models.Model):
    internal_data = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True


class HorizontalChoiceArrayField(ArrayField):
    def formfield(
        self,
        form_class: Any | None = ...,
        choices_form_class: Any | None = ...,
        **kwargs: Any,
    ) -> Any:
        widget = FilteredSelectMultiple(self.verbose_name, False)
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "widget": widget,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


@unique
class Grant(Enum):
    def _generate_next_value_(self: str, start: int, count: int, last_values: list[Any]) -> Any:  # type: ignore # FIXME: signature differs from superclass
        return self

    API_READ_ONLY = auto()
    API_RDI_UPLOAD = auto()
    API_RDI_CREATE = auto()

    API_PROGRAM_CREATE = auto()
    API_GENERIC_IMPORT = auto()

    @classmethod
    def choices(cls) -> tuple[tuple[Any, Any], ...]:
        return tuple((i.value, i.value) for i in cls)
