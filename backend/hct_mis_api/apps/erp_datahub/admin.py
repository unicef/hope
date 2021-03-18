from adminfilters.filters import TextFieldFilter
from django.contrib import admin

from hct_mis_api.apps.erp_datahub.models import FundsCommitment, DownPayment
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(FundsCommitment)
class FundsCommitmentAdmin(HOPEModelAdminBase):
    list_filter = (
        "mis_sync_date",
        "ca_sync_date",
        TextFieldFilter.factory("business_area"),
    )
    date_hierarchy = "create_date"


@admin.register(DownPayment)
class DownPaymentAdmin(HOPEModelAdminBase):
    list_filter = (
        "mis_sync_date",
        "ca_sync_date",
        TextFieldFilter.factory("business_area"),
    )
    date_hierarchy = "create_date"
