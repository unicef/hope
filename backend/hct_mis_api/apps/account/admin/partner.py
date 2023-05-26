import logging

from django.contrib import admin

from hct_mis_api.apps.utils.admin import HopeModelAdminMixin

from hct_mis_api.apps.account import models as account_models

logger = logging.getLogger(__name__)


@admin.register(account_models.Partner)
class PartnerAdmin(HopeModelAdminMixin, admin.ModelAdmin):
    list_filter = ("is_un",)
    search_fields = ("name",)
