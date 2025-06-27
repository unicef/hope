import logging
from typing import Any

from django.contrib import admin
from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin

from hct_mis_api.apps.household.models import BankAccountInfo, Individual
from hct_mis_api.apps.utils.admin import RdiMergeStatusAdminMixin

logger = logging.getLogger(__name__)


@admin.register(BankAccountInfo)
class BankAccountAdmin(AdminFiltersMixin, RdiMergeStatusAdminMixin):
    model = BankAccountInfo
    raw_id_fields = ("individual", "copied_from")
    list_display = (
        "bank_name",
        "bank_account_number",
        "bank_branch_name",
        "debit_card_number",
        "account_holder_name",
        "rdi_merge_status",
    )
    search_fields = ("bank_name", "bank_account_number", "bank_branch_name", "debit_card_number", "account_holder_name")
    list_filter = (
        ("individual__program__business_area", AutoCompleteFilter),
        ("individual__program", AutoCompleteFilter),
        ("individual", AutoCompleteFilter),
    )

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "individual":
            kwargs["queryset"] = Individual.all_objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
