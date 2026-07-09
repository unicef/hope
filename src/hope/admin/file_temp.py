from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.utils.security import is_root
from hope.models import FileTemp


@admin.register(FileTemp)
class FileTempAdmin(HOPEModelAdminBase):
    list_display = ("file", "download_link", "content_type", "object_id", "was_downloaded", "created")
    list_filter = ("was_downloaded", "content_type")
    search_fields = ("file", "object_id")
    ordering = ("-created",)

    def get_readonly_fields(self, request: HttpRequest, obj: FileTemp | None = None) -> tuple[str, ...]:
        if is_root(request):
            return ("download_link", "password", "xlsx_password")
        return ("download_link",)

    def get_exclude(self, request: HttpRequest, obj: FileTemp | None = None) -> tuple[str, ...] | None:
        if is_root(request):
            return None
        return ("password", "xlsx_password")

    def download_link(self, obj: FileTemp) -> str:
        if not obj.file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.file.url)

    download_link.short_description = "Download"
