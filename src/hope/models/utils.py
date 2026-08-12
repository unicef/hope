import hashlib
import logging
import re
from typing import TYPE_CHECKING, Any, Iterable, Sequence, T, TypeVar
from uuid import uuid4

from concurrency.fields import IntegerVersionField
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.fields import ArrayField
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from model_utils.managers import SoftDeletableManagerMixin
from model_utils.models import UUIDModel
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from hope.apps.core.utils import nested_getattr

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.db.models.fields.files import FieldFile


logger = logging.getLogger(__name__)


@deconstructible
class UniqueUploadPath:
    """Give every uploaded file its own folder.

    File names come straight from user uploads, so two unrelated records easily carry the same
    name, and the media storage is configured to overwrite on name collision. The uuid folder
    makes the full path unique, so an upload can no longer replace another record's file.
    """

    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def __call__(self, instance: models.Model | None, filename: str) -> str:
        return f"{self.prefix}/{timezone.now():%Y/%m}/{uuid4().hex}/{filename}"

    def matches(self, name: str) -> bool:
        """Whether name/path has the shape this instance generates."""
        return re.fullmatch(rf"{re.escape(self.prefix)}/\d{{4}}/\d{{2}}/[0-9a-f]{{32}}/.+", name) is not None


def upload_basename(name: str | None) -> str:
    """Drop the generated upload path, leaving the name only."""
    return name.rsplit("/", 1)[-1] if name else ""


def replace_upload(field_file: "FieldFile", filename: str, content: File) -> None:
    """Store a file over the one a field already holds, dropping the file it replaces.

    Use in places where new file should delete old one.
    With transactional operation deletion is done on commit.
    Files that have different path strcuture than generated with this class are not deleted.
    """
    previous_name = field_file.name
    field_file.save(filename, content)
    upload_to = field_file.field.upload_to
    if not isinstance(upload_to, UniqueUploadPath):
        return
    if not previous_name or previous_name == field_file.name:
        return
    if not upload_to.matches(previous_name):
        return
    storage = field_file.storage
    transaction.on_commit(lambda: storage.delete(previous_name), robust=True)


def save_unique_upload(content: File, prefix: str, filename: str) -> str:
    """Store a file that has no model field, under the same unique path scheme.

    Flex field images are kept as a name inside a JSONField, so there is no FileField to
    carry an upload_to. This applies the same path and the same name validation the field
    would: Storage.generate_filename rejects a `..` directory and strips the base name down
    to word characters, dashes and dots, which plain Storage.save does not do.
    """
    name = default_storage.generate_filename(UniqueUploadPath(prefix)(None, filename))
    return default_storage.save(name, content)


def save_flex_field_image(content: File, filename: str) -> str:
    """Store a flex field image under the shared flex field prefix."""
    return save_unique_upload(content, "flex_field_image", filename)


class BulkSignalsManagerMixin:
    def bulk_create(self, objs: Iterable[Any], *args: Any, **kwargs: Any) -> list[Any]:
        val = super().bulk_create(objs, *args, **kwargs)
        from hope.apps.core.signals import post_bulk_create

        post_bulk_create.send(sender=self.model, instances=objs, **kwargs)
        return val

    def bulk_update(self, objs: Iterable[Any], *args: Any, **kwargs: Any) -> int:
        val = super().bulk_update(objs, *args, **kwargs)
        from hope.apps.core.signals import post_bulk_update

        post_bulk_update.send(sender=self.model, instances=objs, **kwargs)
        return val


_M = TypeVar("_M", bound=models.Model)


class BaseManager(BulkSignalsManagerMixin, models.Manager[_M]):
    pass


class SoftDeletableManager(BulkSignalsManagerMixin, SoftDeletableManagerMixin[_M], models.Manager[_M]):
    pass


class SoftDeletableIsVisibleManager(SoftDeletableManager[_M]):
    def get_queryset(self) -> "QuerySet[_M, _M]":
        return super().get_queryset().filter(is_visible=True)


class MergedManager(BulkSignalsManagerMixin, models.Manager[_M]):
    def get_queryset(self) -> "QuerySet[_M, _M]":
        return super().get_queryset().filter(rdi_merge_status="MERGED")


class PendingManager(BulkSignalsManagerMixin, models.Manager[_M]):
    def get_queryset(self) -> "QuerySet[_M, _M]":
        return super().get_queryset().filter(rdi_merge_status="PENDING")


class SoftDeletableMergedManager(SoftDeletableManager[_M]):
    def get_queryset(self) -> "QuerySet[_M, _M]":
        return super().get_queryset().filter(rdi_merge_status="MERGED")


class SoftDeletablePendingManager(SoftDeletableManager[_M]):
    def get_queryset(self) -> "QuerySet[_M, _M]":
        return super().get_queryset().filter(rdi_merge_status="PENDING")


def get_merge_status_choices() -> tuple:
    return MergeStatusModel.STATUS_CHOICE


class MergeStatusModel(models.Model):
    PENDING = "PENDING"
    MERGED = "MERGED"
    STATUS_CHOICE = (
        (PENDING, _("Pending")),
        (MERGED, _("Merged")),
    )

    rdi_merge_status = models.CharField(max_length=10, choices=get_merge_status_choices, default=PENDING, blank=True)

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

    def delete(  # type: ignore[override]
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
            # blake2b with digest_size=20 produces a 40-char hex digest matching the
            # signature_hash CharField(max_length=40); replaces legacy SHA-1 usage.
            hasher = hashlib.blake2b(digest_size=20)
            salt = settings.SECRET_KEY
            hasher.update(salt.encode("utf-8"))

            for field_name in self.signature_fields:
                value = nested_getattr(self, field_name, None)
                value = self._normalize(field_name, value)
                hasher.update(str(value).encode("utf-8"))
            self.signature_hash = hasher.hexdigest()
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
        return super(ArrayField, self).formfield(**defaults)  # type: ignore[arg-type]
