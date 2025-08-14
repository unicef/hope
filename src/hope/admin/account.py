from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter

from hope.admin.utils import (
    HOPEModelAdminBase,
)
from hope.apps.core.models import BusinessArea
from hope.apps.payment.models import (
    Account,
    AccountType,
    DeliveryMechanism,
    DeliveryMechanismConfig,
)

from hope.apps.program.models import Program


@admin.register(Account)
class AccountAdmin(HOPEModelAdminBase):
    list_display = ("individual", "number", "get_business_area", "get_program", "account_type", "is_unique")

    raw_id_fields = ("account_type", "individual")
    readonly_fields = ("unique_key", "signature_hash")
    search_fields = (
        "number",
        "individual__unicef_id",
    )
    list_filter = (
        ("individual__program__business_area", AutoCompleteFilter),
        ("individual__program", AutoCompleteFilter),
        ("individual", AutoCompleteFilter),
        ("financial_institution", AutoCompleteFilter),
        ("account_type", AutoCompleteFilter),
        "is_unique",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related("individual__program__business_area", "financial_institution", "account_type")
        )

    def get_business_area(self, obj: Account) -> BusinessArea:
        return obj.individual.program.business_area

    def get_program(self, obj: Account) -> Program:
        return obj.individual.program


@admin.register(DeliveryMechanism)
class DeliveryMechanismAdmin(HOPEModelAdminBase):
    list_display = ("code", "name", "is_active", "transfer_type", "account_type")
    search_fields = ("code", "name")
    list_filter = ("is_active", "transfer_type")


@admin.register(AccountType)
class AccountTypeAdmin(HOPEModelAdminBase):
    list_display = ("key", "unique_fields", "payment_gateway_id")
    search_fields = ("key", "payment_gateway_id")


@admin.register(DeliveryMechanismConfig)
class DeliveryMechanismConfigAdmin(HOPEModelAdminBase):
    list_display = (
        "id",
        "delivery_mechanism",
        "fsp",
        "country",
    )
    search_fields = ("code",)
    list_filter = (
        ("delivery_mechanism", AutoCompleteFilter),
        ("fsp", AutoCompleteFilter),
        ("country", AutoCompleteFilter),
    )
    raw_id_fields = ("delivery_mechanism", "fsp", "country")
    readonly_fields = ("required_fields", "fsp", "delivery_mechanism", "country")
