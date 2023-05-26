import logging

from django.contrib import admin

from adminfilters.value import ValueFilter

from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

from hct_mis_api.apps.household.models import EntitlementCard

logger = logging.getLogger(__name__)


@admin.register(EntitlementCard)
class EntitlementCardAdmin(HOPEModelAdminBase):
    list_display = ("id", "card_number", "status", "card_type", "service_provider")
    search_fields = ("card_number",)
    date_hierarchy = "created_at"
    raw_id_fields = ("household",)
    list_filter = (
        "status",
        ("card_type", ValueFilter),
        ("service_provider", ValueFilter),
    )
