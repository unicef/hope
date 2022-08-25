import csv
import logging
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.contrib.admin import FieldListFilter, ListFilter, RelatedFieldListFilter
from django.contrib.admin.utils import prepare_lookup_value
from django.forms import TextInput, Form, FileField, FileInput
from admin_extra_buttons.decorators import button

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import NumberFilter
from smart_admin.mixins import FieldsetMixin
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.geo.models import Area, AreaType, Country
from django.template.response import TemplateResponse

logger = logging.getLogger(__name__)


class ImportCSVForm(Form):
    file = FileField(widget=FileInput(attrs={"accept": "text/csv"}))


class ActiveRecordFilter(ListFilter):
    title = "Active"
    parameter_name = "active"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        for p in self.expected_parameters():
            if p in params:
                value = params.pop(p)
                self.used_parameters[p] = prepare_lookup_value(p, value)

    def has_output(self):
        return True

    def value(self):
        return self.used_parameters.get(self.parameter_name, "")

    def expected_parameters(self):
        return [self.parameter_name]

    def choices(self, changelist):
        for lookup, title in ((None, "All"), ("1", "Yes"), ("0", "No")):
            yield {
                "selected": self.value() == lookup,
                "query_string": changelist.get_query_string({self.parameter_name: lookup}),
                "display": title,
            }

    def queryset(self, request, queryset):
        if self.value() == "1":
            queryset = queryset.filter(valid_until__isnull=True)
        elif self.value() == "0":
            queryset = queryset.exclude(valid_until__isnull=True)
        return queryset


class ValidityManagerMixin:
    def get_list_filter(self, request):
        return list(self.list_filter) + [ActiveRecordFilter]


@admin.register(Country)
class CountryAdmin(ExtraButtonsMixin, ValidityManagerMixin, FieldsetMixin, HOPEModelAdminBase):
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
        # ("GIS", {"classes": ["collapse"], "fields": ("geom", "point")}),
        ("Others", {"classes": ["collapse"], "fields": ("__others__",)}),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ("iso_code2", "iso_code3", "iso_num"):
            kwargs = {"widget": TextInput(attrs={"size": "10"})}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_list_display(self, request):
        ret = super().get_list_display(request)
        return ret


@admin.register(AreaType)
class AreaTypeAdmin(ExtraButtonsMixin, ValidityManagerMixin, FieldsetMixin, HOPEModelAdminBase):
    list_display = ("name", "country", "area_level", "parent")
    list_filter = (("country", AutoCompleteFilter), ("area_level", NumberFilter))

    search_fields = ("name",)
    autocomplete_fields = ("country", "parent")
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
        # ("GIS", {"classes": ["collapse"], "fields": ("geom", "point")}),
        ("Others", {"classes": ["collapse"], "fields": ("__others__",)}),
    )


class AreaTypeFilter(RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        if "area_type__country__exact" not in request.GET:
            return []
        return AreaType.objects.filter(country=request.GET["area_type__country__exact"]).values_list("id", "name")


@admin.register(Area)
class AreaAdmin(ExtraButtonsMixin, ValidityManagerMixin, FieldsetMixin, HOPEModelAdminBase):
    list_display = (
        "name",
        "area_type",
        "p_code",
    )
    list_filter = (
        ("area_type__country", AutoCompleteFilter),
        ("area_type", AreaTypeFilter),
    )
    search_fields = ("name",)
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
        ("GIS", {"classes": ["collapse"], "fields": ("geom", "point")}),
        ("Others", {"classes": ["collapse"], "fields": ("__others__",)}),
    )

    @button()
    def import_areas(self, request):
        context = self.get_common_context(request, processed=False)
        if request.method == "POST":
            form = ImportCSVForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data["file"]
                data_set = csv_file.read().decode("utf-8-sig").splitlines()
                reader = csv.DictReader(data_set)
                country = None
                for row in reader:
                    try:
                        d = len(row) // 2
                        area_types = [*row][:d]
                        admin_area = [*row][d:]
                        country = Country.objects.get(short_name=row["Country"])
                        for idx, x in enumerate(area_types):
                            if idx > 0:
                                art, created = AreaType.objects.get_or_create(name=x, country=country, area_level=idx)
                                area, created = Area.objects.get_or_create(
                                    name=row[x], p_code=row[admin_area[idx]], area_type=art
                                )
                                ids = idx - 1
                                if ids > 0:
                                    art.parent = AreaType.objects.get(
                                        country=country, area_level=ids, name=area_types[ids]
                                    )
                                    art.save()
                                    area.parent = Area.objects.get(
                                        p_code=row[admin_area[ids]], name=row[area_types[ids]]
                                    )
                                    area.save()
                    except Exception:
                        self.message_user(request, f"Unable to load areas, please check the format", messages.ERROR)
                        raise

                self.message_user(request, f"Updated all areas for {country}")
                return redirect("admin:geo_area_changelist")
        else:
            form = ImportCSVForm()
            context["form"] = form
        context["form"] = form
        return TemplateResponse(request, "admin/geo/import_area_csv.html", context)
