import logging

from django.contrib import admin

from hct_mis_api.apps.household.models import BankAccountInfo

logger = logging.getLogger(__name__)


@admin.register(BankAccountInfo)
class BankAccountAdmin(admin.ModelAdmin):
    model = BankAccountInfo
    raw_id_fields = ("individual", "copied_from")
