from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.admin.options import ActionLocation
    from django.http import HttpRequest

from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models import UploadedXLSXFile


@admin.register(UploadedXLSXFile)
class UploadedXLSXFileAdmin(HOPEModelAdminBase):
    list_display = ("id", "file", "associated_email")
    readonly_fields = ("file",)
    filter_horizontal = ("selected_lists",)

    def get_actions(self, request: HttpRequest, action_location: ActionLocation | None = None) -> dict:
        return super().get_actions(
            request, **({"action_location": action_location} if action_location is not None else {})
        )
