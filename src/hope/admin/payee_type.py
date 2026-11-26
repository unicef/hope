from django.contrib import admin
from django.utils.text import Truncator

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.core.forms import PayeeTypeForm
from hope.models import PayeeType


@admin.register(PayeeType)
class PayeeTypeAdmin(HOPEModelAdminBase):
    form = PayeeTypeForm
    list_display = ("name", "gl_code", "description_preview", "active", "default_data_collecting_type", "weight")
    list_filter = ("active",)
    search_fields = ("name", "gl_code", "description")
    ordering = ("-weight", "name")

    @admin.display(description="Description", ordering="description")
    def description_preview(self, obj: PayeeType) -> str:
        return Truncator(obj.description).chars(80)
