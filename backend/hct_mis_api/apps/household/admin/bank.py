import logging

from django.contrib import admin

from hct_mis_api.apps.household.models import BankAccountInfo, Individual
from hct_mis_api.apps.utils.admin import RdiMergeStatusAdminMixin

logger = logging.getLogger(__name__)


@admin.register(BankAccountInfo)
class BankAccountAdmin(RdiMergeStatusAdminMixin):
    model = BankAccountInfo
    raw_id_fields = ("individual", "copied_from")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "individual":
            kwargs["queryset"] = Individual.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
