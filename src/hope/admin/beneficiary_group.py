from django.contrib import admin

from hope.admin.utils import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
)
from hope.apps.program.models import BeneficiaryGroup


@admin.register(BeneficiaryGroup)
class BeneficiaryGroupAdmin(LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("name", "group_label", "group_label_plural", "member_label", "member_label_plural", "master_detail")
    search_fields = (
        "name",
        "group_label",
        "group_label_plural",
        "member_label",
        "member_label_plural",
    )
    ordering = ("name",)
