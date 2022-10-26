from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import JSONField

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin, confirm_action
from adminactions.helpers import AdminActionPermMixin
from adminfilters.mixin import AdminFiltersMixin
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import DisplayAllMixin as SmartDisplayAllMixin

from hct_mis_api.apps.administration.widgets import JsonWidget
from hct_mis_api.apps.utils.security import is_root


class SoftDeletableAdminMixin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_list_filter(self, request):
        return tuple(list(super().get_list_filter(request)) + ["is_removed"])


class JSONWidgetMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, JSONField):
            if is_root(request) or settings.DEBUG:
                kwargs = {"widget": JSONEditor}
            else:
                kwargs = {"widget": JsonWidget}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class LastSyncDateResetMixin:
    @button()
    def reset_sync_date(self, request):
        if request.method == "POST":
            self.get_queryset(request).update(last_sync_at=None)
        else:
            return confirm_action(
                self,
                request,
                self.reset_sync_date,
                "Continuing will reset all records last_sync_date field.",
                "Successfully executed",
                title="aaaaa",
            )

    @button(label="reset sync date")
    def reset_sync_date_single(self, request, pk):
        if request.method == "POST":
            self.get_queryset(request).filter(id=pk).update(last_sync_at=None)
        else:
            return confirm_action(
                self,
                request,
                self.reset_sync_date,
                "Continuing will reset last_sync_date field.",
                "Successfully executed",
            )


class HopeModelAdminMixin(ExtraButtonsMixin, SmartDisplayAllMixin, AdminActionPermMixin, AdminFiltersMixin):
    pass


class HOPEModelAdminBase(HopeModelAdminMixin, JSONWidgetMixin, admin.ModelAdmin):
    list_per_page = 50

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions and not is_root(request):
            del actions["delete_selected"]
        return actions

    def count_queryset(self, request, queryset):
        count = queryset.count()
        self.message_user(request, f"Selection contains {count} records")


class HUBBusinessAreaFilter(SimpleListFilter):
    parameter_name = "ba"
    title = "Business Area"
    template = "adminfilters/combobox.html"

    def lookups(self, request, model_admin):
        from hct_mis_api.apps.core.models import BusinessArea

        return BusinessArea.objects.values_list("code", "name").distinct()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(business_area=self.value()).distinct()
        return queryset
