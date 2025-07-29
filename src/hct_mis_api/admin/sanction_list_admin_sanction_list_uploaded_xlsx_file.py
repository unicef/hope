from django.contrib import admin
from django.http import HttpRequest


from hct_mis_api.admin.utils_admin import HOPEModelAdminBase
from hct_mis_api.apps.sanction_list.models import (
    UploadedXLSXFile,
)


@admin.register(UploadedXLSXFile)
class UploadedXLSXFileAdmin(HOPEModelAdminBase):
    list_display = ("id", "file", "associated_email")
    filter_horizontal = ("selected_lists",)

    def get_actions(self, request: HttpRequest) -> dict:
        return super().get_actions(request)
