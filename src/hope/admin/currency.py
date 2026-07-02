from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models import Currency


@admin.register(Currency)
class CurrencyAdmin(HOPEModelAdminBase):
    list_display = ("code", "name", "is_crypto", "vision_code", "active", "number_of_decimals")
    list_filter = ("is_crypto", "active")
    search_fields = ("code", "name")
    ordering = ("code", "vision_code")
