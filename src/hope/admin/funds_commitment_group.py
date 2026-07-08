from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.contrib.vision.models import FundsCommitmentGroup


@admin.register(FundsCommitmentGroup)
class FundsCommitmentGroupAdmin(HOPEModelAdminBase):
    list_display = ("funds_commitment_number",)
    search_fields = ("funds_commitment_number",)
