from django.contrib import admin
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.sanction_list.models import UploadedXLSXFile


@admin.register(UploadedXLSXFile)
class UploadedXLSXFileAdmin(HOPEModelAdminBase):
    list_display = ("id", "file", "associated_email")
    filter_horizontal = ("selected_lists",)

    def get_actions(self, request: HttpRequest) -> dict:
        return super().get_actions(request)
