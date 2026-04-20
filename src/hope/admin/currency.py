from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models import Currency


@admin.register(Currency)
class CurrencyAdmin(HOPEModelAdminBase):
    list_display = ("code", "name", "is_crypto")
    list_filter = ("is_crypto",)
    search_fields = ("code", "name")
    ordering = ("code",)
