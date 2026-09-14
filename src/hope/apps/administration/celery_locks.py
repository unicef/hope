from collections import defaultdict
import logging
from typing import Any

from django.contrib import messages
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from hope.apps.administration.forms import CeleryLockDeleteForm
from hope.apps.core.celery_lock import LOCK_PREFIX
from hope.apps.utils.security import is_root

logger = logging.getLogger(__name__)


def celery_locks_for(object_id: object) -> list[str]:
    return [key for key in cache.celery_lock_keys() if str(object_id) in key.split(":")[1:]]


def grouped_celery_locks() -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for key in cache.celery_lock_keys():
        groups[key.removeprefix(LOCK_PREFIX).split(":", 1)[0]].append(key)
    return dict(groups)


def remove_celery_lock(request: HttpRequest, key: str, obj: Model | None = None) -> None:
    cache.delete_celery_lock(key)
    logger.warning("%s removed celery lock %s", request.user, key)
    LogEntry.objects.create(
        user_id=request.user.pk,
        content_type=ContentType.objects.get_for_model(obj) if obj else None,
        object_id=str(obj.pk) if obj else None,
        object_repr=key,
        action_flag=DELETION,
        change_message="Celery lock removed",
    )


def celery_locks_view(request: HttpRequest) -> HttpResponse:
    if not is_root(request):
        raise PermissionDenied
    form = CeleryLockDeleteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        remove_celery_lock(request, form.cleaned_data["key"])
        messages.success(request, f"Removed lock {form.cleaned_data['key']}")
        return HttpResponseRedirect(request.path)
    ctx: dict[str, Any] = {"title": "Celery locks", "groups": grouped_celery_locks(), "form": form}
    return render(request, "admin/celery_locks.html", ctx)
