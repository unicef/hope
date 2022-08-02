from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.activity_log.utils import create_diff
from hct_mis_api.apps.core.utils import nested_getattr


def log_create(mapping, business_area_field, user=None, old_object=None, new_object=None):
    if new_object:
        instance = new_object
    else:
        instance = old_object
    action = LogEntry.UPDATE
    if old_object is None:
        action = LogEntry.CREATE
    elif new_object is None:
        action = LogEntry.DELETE
    else:
        is_removed = getattr(new_object, "is_removed", None)
        is_removed_old = getattr(old_object, "is_removed", None)
        if is_removed and is_removed_old != is_removed:
            action = LogEntry.SOFT_DELETE
    business_area = nested_getattr(instance, business_area_field)
    log = LogEntry.objects.create(
        action=action,
        content_object=instance,
        user=user,
        business_area=business_area,
        object_repr=str(instance),
        changes=create_diff(old_object, new_object, mapping)
        if action not in (LogEntry.DELETE, LogEntry.SOFT_DELETE)
        else None,
    )
    return log


class LogEntry(models.Model):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SOFT_DELETE = "SOFT_DELETE"

    LOG_ENTRY_ACTION_CHOICES = (
        (CREATE, _("Create")),
        (UPDATE, _("Update")),
        (DELETE, _("Delete")),
        (SOFT_DELETE, _("Soft Delete")),
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="log_entries",
        db_index=True,
    )
    object_id = models.UUIDField(null=True, db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")
    action = models.CharField(
        choices=LOG_ENTRY_ACTION_CHOICES,
        max_length=100,
        verbose_name=_("action"),
        db_index=True,
    )
    object_repr = models.TextField(blank=True)
    changes = JSONField(null=True, verbose_name=_("change message"))
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="logs",
        verbose_name=_("actor"),
    )
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.SET_NULL, null=True)

    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("timestamp"), db_index=True)

    class Meta:
        get_latest_by = "timestamp"
        ordering = ["-timestamp"]
        verbose_name = _("log entry")
        verbose_name_plural = _("log entries")
