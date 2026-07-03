from django.contrib import admin
from django.utils.html import format_html

from hope.admin.utils import HOPEModelAdminBase
from hope.models import FileTemp


@admin.register(FileTemp)
class FileTempAdmin(HOPEModelAdminBase):
    list_display = ("file", "download_link", "content_type", "object_id", "was_downloaded", "created")
    list_filter = ("was_downloaded", "content_type")
    search_fields = ("file", "object_id")
    readonly_fields = ("download_link", "password", "xlsx_password")
    ordering = ("-created",)

    def download_link(self, obj: FileTemp) -> str:
        if not obj.file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.file.url)

    download_link.short_description = "Download"
