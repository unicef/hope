from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models import SurprisePageConfig


@admin.register(SurprisePageConfig)
class SurprisePageConfigAdmin(HOPEModelAdminBase):
    fields = ("image", "heading", "subheading")
