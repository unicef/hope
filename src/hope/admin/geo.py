import csv
import logging
from typing import TYPE_CHECKING, Any, Callable, Generator, Union

from admin_extra_buttons.decorators import button
from admin_sync.mixin import SyncMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import NumberFilter
from django.contrib import admin, messages
from django.contrib.admin import ListFilter, ModelAdmin, RelatedFieldListFilter
from django.contrib.admin.utils import prepare_lookup_value
from django.db.models import Model, QuerySet
from django.forms import FileField, FileInput, Form, TextInput
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from smart_admin.mixins import FieldsetMixin

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.geo.celery_tasks import import_areas_from_csv_task
from hope.apps.geo.models import Area, AreaType, Country

if TYPE_CHECKING:
    from django.http import (
        HttpRequest,
        HttpResponsePermanentRedirect,
        HttpResponseRedirect,
    )

logger = logging.getLogger(__name__)


class ImportCSVForm(Form):
    file = FileField(widget=FileInput(attrs={"accept": "text/csv"}))


class ActiveRecordFilter(ListFilter):
    title = "Active"
    parameter_name = "active"

    def __init__(
        self,
        request: "HttpRequest",
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
    ) -> None:
        super().__init__(request, params, model, model_admin)
        for p in self.expected_parameters():
            if p in params:
                value = params.pop(p)
                self.used_parameters[p] = prepare_lookup_value(p, value)

    def has_output(self) -> bool:
        return True

    def value(self) -> str:
        return self.used_parameters.get(self.parameter_name, "")

    def expected_parameters(self) -> list:
        return [self.parameter_name]

    def choices(self, changelist: list) -> Generator:
        for lookup, title in ((None, "All"), ("1", "Yes"), ("0", "No")):
            yield {
                "selected": self.value() == lookup,
                "query_string": changelist.get_query_string({self.parameter_name: lookup}),
                "display": title,
            }

    def queryset(self, request: "HttpRequest", queryset: QuerySet) -> QuerySet:
        if self.value() == "1":
            queryset = queryset.filter(valid_until__isnull=True)
        elif self.value() == "0":
            queryset = queryset.exclude(valid_until__isnull=True)
        return queryset


class ValidityManagerMixin:
    def get_list_filter(self, request: "HttpRequest") -> list:
        return list(self.list_filter) + [ActiveRecordFilter]


@admin.register(Country)
class CountryAdmin(ValidityManagerMixin, SyncMixin, FieldsetMixin, HOPEModelAdminBase):
    list_display = ("name", "short_name", "iso_code2", "iso_code3", "iso_num")
    search_fields = ("name", "short_name", "iso_code2", "iso_code3", "iso_num")
    raw_id_fields = ("parent",)
    fieldsets = (
        (
            "",
            {
                "fields": (
                    (
                        "name",
                        "short_name",
                    ),
                    ("iso_code2", "iso_code3", "iso_num"),
                )
            },
        ),
        ("Others", {"classes": ["collapse"], "fields": ("__others__",)}),
    )

    def formfield_for_dbfield(self, db_field: Any, request: "HttpRequest", **kwargs: Any) -> None:
        if db_field.name in ("iso_code2", "iso_code3", "iso_num"):
            kwargs = {"widget": TextInput(attrs={"size": "10"})}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_list_display(
        self, request: "HttpRequest"
    ) -> list[str | Callable[[Any], str]] | tuple[str | Callable[[Any], str], ...]:
        return super().get_list_display(request)


@admin.register(AreaType)
class AreaTypeAdmin(ValidityManagerMixin, FieldsetMixin, SyncMixin, HOPEModelAdminBase):
    list_display = ("name", "country", "area_level", "parent")
    list_filter = (("country", AutoCompleteFilter), ("area_level", NumberFilter))

    search_fields = ("name",)
    raw_id_fields = ("country", "parent")
    fieldsets = (
        (
            "",
            {
                "fields": (
                    (
                        "name",
                        "country",
                    ),
                    (
                        "area_level",
                        "parent",
                    ),
                )
            },
        ),
        ("Others", {"classes": ["collapse"], "fields": ("__others__",)}),
    )

    def get_queryset(self, request: "HttpRequest") -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .select_related(
                "country",
                "parent",
            )
        )


class AreaTypeFilter(RelatedFieldListFilter):
    def field_choices(self, field: Any, request: "HttpRequest", model_admin: ModelAdmin) -> list[tuple[str, str]]:
        if "area_type__country__exact" not in request.GET:
            return []
        return AreaType.objects.filter(country=request.GET["area_type__country__exact"]).values_list("id", "name")


@admin.register(Area)
class AreaAdmin(ValidityManagerMixin, FieldsetMixin, SyncMixin, HOPEModelAdminBase):
    list_display = (
        "name",
        "area_type",
        "p_code",
    )
    list_filter = (
        ("area_type__country", AutoCompleteFilter),
        ("area_type", AreaTypeFilter),
    )
    search_fields = ("name", "p_code")
    raw_id_fields = ("area_type", "parent")
    fieldsets = (
        (
            "",
            {
                "fields": (
                    (
                        "name",
                        "p_code",
                    ),
                    (
                        "area_type",
                        "parent",
                    ),
                )
            },
        ),
        ("Others", {"classes": ["collapse"], "fields": ("__others__",)}),
    )

    def get_queryset(self, request: "HttpRequest") -> "QuerySet":
        return (
            super()
            .get_queryset(request)
            .select_related(
                "area_type",
                "parent",
            )
        )

    @button(permission="geo.import_areas")
    def import_areas(
        self, request: "HttpRequest"
    ) -> Union["HttpResponsePermanentRedirect", "HttpResponseRedirect", TemplateResponse]:
        context = self.get_common_context(request, processed=False)
        if request.method == "POST":
            form = ImportCSVForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data["file"]
                data_set = csv_file.read().decode("utf-8-sig")
                reader = csv.DictReader(data_set.splitlines())
                rows = list(reader)

                if not rows:
                    self.message_user(request, "CSV file is empty.", messages.WARNING)
                    return redirect("admin:geo_area_changelist")

                try:
                    Country.objects.get(short_name=rows[0]["Country"])
                except Country.DoesNotExist:
                    self.message_user(request, f"Country '{rows[0]['Country']}' not found", messages.ERROR)
                    return redirect("admin:geo_area_changelist")
                except KeyError:
                    self.message_user(request, "CSV must have a 'Country' column", messages.ERROR)
                    return redirect("admin:geo_area_changelist")

                keys = list(rows[0].keys())
                num_cols = len(keys)
                if num_cols % 2 != 0:
                    self.message_user(
                        request, "CSV must have an even number of columns (names and p-codes)", messages.ERROR
                    )
                    return redirect("admin:geo_area_changelist")

                d = num_cols // 2
                name_headers = keys[:d]
                p_code_headers = keys[d:]

                if name_headers[0] != "Country":
                    self.message_user(request, "First column must be 'Country'", messages.ERROR)
                    return redirect("admin:geo_area_changelist")

                all_p_codes = {row[h] for row in rows for h in p_code_headers if row.get(h)}
                existing_p_codes = set(Area.objects.filter(p_code__in=all_p_codes).values_list("p_code", flat=True))
                new_areas_count = len(all_p_codes - existing_p_codes)

                import_areas_from_csv_task.delay(data_set)

                self.message_user(
                    request,
                    (f"Found {new_areas_count} new areas to create. The import is running in the background."),
                    messages.SUCCESS,
                )
                return redirect("admin:geo_area_changelist")
        else:
            form = ImportCSVForm()
        context["form"] = form
        return TemplateResponse(request, "admin/geo/import_area_csv.html", context)
