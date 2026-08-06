from django.contrib import admin, messages
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models import Currency


@admin.register(Currency)
class CurrencyAdmin(HOPEModelAdminBase):
    list_display = ("code", "name", "is_crypto", "vision_code", "active", "number_of_decimals")
    list_filter = ("is_crypto", "active")
    search_fields = ("code", "vision_code", "name")
    ordering = ("code", "vision_code")
    actions = ("deprecate_currency",)

    @admin.action(description="Deprecate: swap the active currency for this code", permissions=["change"])
    def deprecate_currency(self, request: HttpRequest, queryset: QuerySet[Currency]) -> None:
        active = [c for c in queryset if c.active]
        inactive = [c for c in queryset if not c.active]

        if len(active) != 1 or len(inactive) != 1:
            self.message_user(
                request,
                "Select exactly two currencies: one selected currency must be active and the other inactive.",
                level=messages.ERROR,
            )
            return

        old, new = active[0], inactive[0]
        if old.code != new.code:
            self.message_user(request, "Selected currencies must share the same code.", level=messages.ERROR)
            return

        # Deactivate first, then activate
        with transaction.atomic():
            Currency.objects.filter(pk=old.pk).update(active=False)
            Currency.objects.filter(pk=new.pk).update(active=True)
            old.active, new.active = False, True
            self.log_change(request, old, f"Deprecated in favour of '{new.vision_code}'.")
            self.log_change(request, new, f"Activated in place of '{old.vision_code}'.")

        self.message_user(
            request,
            f"Deprecated '{old.vision_code}' in favour of '{new.vision_code}' for code '{new.code}'.",
            level=messages.SUCCESS,
        )
