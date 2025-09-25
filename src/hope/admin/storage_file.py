import logging
from typing import Any

from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib import admin
from django.http import HttpRequest

from hope.models.storage_file import StorageFile

logger = logging.getLogger(__name__)


@admin.register(StorageFile)
class StorageFileAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = (
        "file_name",
        "file",
        "business_area",
        "file_size",
        "created_by",
        "created_at",
    )

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_download_storage_files()

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_download_storage_files()

    def has_view_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.can_download_storage_files()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.can_download_storage_files()
