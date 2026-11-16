from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.core.forms import PayeeTypeForm
from hope.models import PayeeType


@admin.register(PayeeType)
class PayeeTypeAdmin(HOPEModelAdminBase):
    form = PayeeTypeForm
    list_display = ("name", "gl_code", "active", "default_data_collecting_type", "weight")
    list_filter = ("active",)
    search_fields = ("name", "gl_code")
    ordering = ("-weight", "name")
