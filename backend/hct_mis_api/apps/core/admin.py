import csv
import logging
import time

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.messages import ERROR
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import RegexValidator
from django.db import transaction
from django.db.models import Count, F, Func
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

import xlrd
from admin_extra_urls.api import ExtraUrlMixin, button
from adminfilters.filters import (
    AllValuesComboFilter,
    ChoicesFieldComboFilter,
    TextFieldFilter,
)
from xlrd import XLRDError

from hct_mis_api.apps.core.celery_tasks import (
    upload_new_kobo_template_and_update_flex_fields_task,
)
from hct_mis_api.apps.core.datamart.api import DatamartAPI
from hct_mis_api.apps.core.models import (
    AdminArea,
    AdminAreaLevel,
    BusinessArea,
    CountryCodeMap,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
    XLSXKoboTemplate,
)
from hct_mis_api.apps.core.tasks.admin_areas import load_admin_area
from hct_mis_api.apps.core.validators import KoboTemplateValidator
from hct_mis_api.apps.payment.rapid_pro.api import RapidProAPI
from mptt.admin import MPTTModelAdmin

logger = logging.getLogger(__name__)


class XLSImportForm(forms.Form):
    xls_file = forms.FileField()


class TestRapidproForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone number",
        required=True,
    )
    flow_name = forms.CharField(label="Name of the test flow", initial="Test", required=True)


class BusinessOfficeCodeValidator(RegexValidator):
    message = "Business office code must start with 'BO' and contains only chars"
    regex = "BO[A-Z]{2}"


class BusinessOfficeForm(forms.ModelForm):
    name = forms.CharField()
    code = forms.CharField(max_length=4, validators=[BusinessOfficeCodeValidator()])

    class Meta:
        model = BusinessArea
        fields = ("code", "name")


class BusinessofficeFilter(SimpleListFilter):
    template = "adminfilters/combobox.html"
    title = "Business Ofiice"
    parameter_name = "bo"

    def lookups(self, request, model_admin):
        return [(1, "Is a Business Office"), (2, "Is a Business Area")]

    def value(self):
        return self.used_parameters.get(self.parameter_name)

    def queryset(self, request, queryset):
        if self.value() == "2":
            return queryset.filter(parent_id__isnull=True)
        elif self.value() == "1":
            return queryset.exclude(parent_id__isnull=True)
        return queryset


from django.db.models import Aggregate, CharField


class GroupConcat(Aggregate):
    function = "GROUP_CONCAT"
    template = "%(function)s(%(distinct)s%(expressions)s)"

    def __init__(self, expression, distinct=False, **extra):
        super(GroupConcat, self).__init__(
            expression, distinct="DISTINCT " if distinct else "", output_field=CharField(), **extra
        )


@admin.register(BusinessArea)
class BusinessAreaAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "code",
        "region_name",
        "region_code",
    )
    search_fields = ("name", "slug")
    list_filter = ("has_data_sharing_agreement", "region_name", BusinessofficeFilter, "is_split")
    readonly_fields = ("parent", "is_split")
    filter_horizontal = ("countries",)

    @button(label="Create Business Office", permission=["core.can_split_business_area"])
    def split_business_area(self, request, pk):
        context = self.get_common_context(request, pk)
        opts = self.object._meta
        if request.POST:
            form = context["form"] = BusinessOfficeForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    self.object.is_split = True
                    name = form.cleaned_data["name"]
                    office = BusinessArea.objects.create(
                        code=form.cleaned_data["code"],
                        name=form.cleaned_data["name"],
                        parent=self.object,
                        region_code=self.object.region_code,
                        region_name=self.object.region_name,
                        long_name=f"Business Office: {name}",
                        slug=slugify(name),
                    )
                preserved_filters = self.get_preserved_filters(request)

                redirect_url = reverse(
                    "admin:%s_%s_change" % (opts.app_label, opts.model_name),
                    args=(office.pk,),
                    current_app=self.admin_site.name,
                )
                redirect_url = add_preserved_filters(
                    {"preserved_filters": preserved_filters, "opts": opts}, redirect_url
                )
                return HttpResponseRedirect(redirect_url)

        else:
            context["form"] = BusinessOfficeForm()

        return TemplateResponse(request, "core/admin/split_ba.html", context)

    @button()
    def members(self, request, pk):
        context = self.get_common_context(request, pk, title="Members")
        context["members"] = (
            context["original"]
            .user_roles.values("user__id", "user__email", "user__username")
            .annotate(roles=ArrayAgg("role__name"))
            .order_by("user__username")
        )
        return TemplateResponse(request, "core/admin/ba_members.html", context)

    @button(label="Test RapidPro Connection")
    def _test_rapidpro_connection(self, request, pk):
        context = self.get_common_context(request, pk)
        context["business_area"] = self.object
        context["title"] = f"Test `{self.object.name}` RapidPRO connection"

        api = RapidProAPI(self.object.slug)

        if request.method == "GET":
            phone_number = request.GET.get("phone_number", None)
            flow_uuid = request.GET.get("flow_uuid", None)
            flow_name = request.GET.get("flow_name", None)
            timestamp = request.GET.get("timestamp", None)

            if all([phone_number, flow_uuid, flow_name, timestamp]):
                error, result = api.test_connection_flow_run(flow_uuid, phone_number, timestamp)
                context["run_result"] = result
                context["phone_number"] = phone_number
                context["flow_uuid"] = flow_uuid
                context["flow_name"] = flow_name
                context["timestamp"] = timestamp

                if error:
                    messages.error(request, error)
                else:
                    messages.success(request, "Connection successful")
            else:
                context["form"] = TestRapidproForm()
        else:
            form = TestRapidproForm(request.POST)
            if form.is_valid():
                phone_number = form.cleaned_data["phone_number"]
                flow_name = form.cleaned_data["flow_name"]
                context["phone_number"] = phone_number
                context["flow_name"] = flow_name

                error, response = api.test_connection_start_flow(flow_name, phone_number)
                if response:
                    context["flow_uuid"] = response["flow"]["uuid"]
                    context["flow_status"] = response["status"]
                    context["timestamp"] = response["created_on"]

                if error:
                    messages.error(request, error)
                else:
                    messages.success(request, "Connection successful")

            context["form"] = form

        return TemplateResponse(request, "core/test_rapidpro.html", context)


class CountryFilter(SimpleListFilter):
    template = "adminfilters/combobox.html"
    title = "Country"
    parameter_name = "country"

    def lookups(self, request, model_admin):
        return AdminArea.objects.filter(admin_area_level__admin_level=0).values_list("id", "title")

    def value(self):
        return self.used_parameters.get(self.parameter_name)

    def queryset(self, request, queryset):
        try:
            if self.value():
                country = AdminArea.objects.get(id=self.value())
                return queryset.filter(tree_id=country.tree_id)
        except AdminArea.DoesNotExist:
            pass
        return queryset


class AdminLevelFilter(SimpleListFilter):
    template = "adminfilters/combobox.html"

    title = "Admin Level"
    parameter_name = "alevel"

    def lookups(self, request, model_admin):
        return [(l, f"Level {l}") for l in range(3)]

    def value(self):
        return self.used_parameters.get(self.parameter_name)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(admin_area_level__admin_level=self.value())
        return queryset


@admin.register(AdminAreaLevel)
class AdminAreaLevelAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("name", "country_name", "admin_level", "area_code")
    list_filter = (
        ("admin_level", AllValuesComboFilter),
        ("country_name", AllValuesComboFilter),
    )
    search_fields = ("name",)
    ordering = ("country_name", "admin_level")

    @button(permission=["load_from_datamart"])
    def load_from_datamart(self, request):
        api = DatamartAPI()
        for level in api.get_admin_levels():
            try:
                AdminAreaLevel.objects.update_or_create(
                    datamart_id=level["id"],
                    defaults={
                        "name": level["name"],
                        "country_name": level["country_name"],
                        "area_code": level["area_code"],
                        "admin_level": level["admin_level"],
                    },
                )
            except Exception as e:
                logger.exception(e)


class LoadAdminAreaForm(forms.Form):
    # country = forms.ChoiceField(choices=AdminAreaLevel.objects.get_countries())
    country = forms.ModelChoiceField(queryset=AdminAreaLevel.objects.filter(admin_level=0).order_by("country_name"))
    geometries = forms.BooleanField(required=False)
    run_in_background = forms.BooleanField(required=False)

    page_size = forms.IntegerField(required=True, validators=[lambda x: x >= 1])
    max_records = forms.IntegerField(required=False, help_text="Leave blank for all records")


class ImportAreaForm(forms.Form):
    # country = forms.ChoiceField(choices=AdminAreaLevel.objects.get_countries())
    country = forms.ModelChoiceField(queryset=AdminArea.objects.filter(admin_area_level__admin_level=0))
    file = forms.FileField()


@admin.register(AdminArea)
class AdminAreaAdmin(ExtraUrlMixin, MPTTModelAdmin):
    search_fields = ("p_code", "title")
    list_display = ("title", "country", "parent", "tree_id", "external_id", "admin_area_level", "p_code")
    list_filter = (
        AdminLevelFilter,
        CountryFilter,
        TextFieldFilter.factory("tree_id"),
        TextFieldFilter.factory("external_id"),
    )

    @button(permission="core.import_from_csv_adminarea")
    def import_file(self, request):
        context = self.get_common_context(request)
        if request.method == "GET":
            form = ImportAreaForm(initial={})
            context["form"] = form
        else:
            form = ImportAreaForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                try:
                    csv_file = form.cleaned_data["file"]
                    # If file is too large
                    if csv_file.multiple_chunks():
                        raise Exception("Uploaded file is too big (%.2f MB)" % (csv_file.size(1000 * 1000)))

                    data_set = csv_file.read().decode("utf-8-sig").splitlines()
                    reader = csv.DictReader(data_set, quoting=csv.QUOTE_NONE, delimiter=";")
                    provided = set(reader.fieldnames)
                    minimum_set = {"area_code", "area_level", "parent_area_code", "area_name"}
                    if not minimum_set.issubset(provided):
                        raise Exception(f"Invalid columns {reader.fieldnames}. {provided.difference(minimum_set)}")
                    lines = []
                    infos = {"skipped": 0}
                    # country = form.cleaned_data['country']
                    # country = AdminArea.objects.get(admin_area_level=form.cleaned_data["country"])
                    country = form.cleaned_data["country"]
                    with transaction.atomic():
                        external_id = f"import-{int(time.time())}"
                        for row in reader:
                            if all(row.values()):
                                level_number = int(row["area_level"])
                                level, __ = AdminAreaLevel.objects.get_or_create(
                                    country=country.admin_area_level,
                                    admin_level=level_number,
                                    defaults={"name": row.get("level_name", f"{country.title} {level_number}")},
                                )
                                parent = AdminArea.objects.filter(
                                    tree_id=country.tree_id, p_code=row["parent_area_code"]
                                ).first()
                                if parent is None:
                                    assert level_number == 0, f"Cannot find parent area for {row}"
                                AdminArea.objects.create(
                                    external_id=external_id,
                                    title=row["area_name"],
                                    admin_area_level=level,
                                    p_code=row["area_code"],
                                    parent=parent,
                                )
                                lines.append(row)
                            else:
                                infos["skipped"] += 1
                    AdminArea.objects.rebuild()
                    context["country"] = form.cleaned_data["country"]
                    context["columns"] = minimum_set
                    context["lines"] = lines
                    context["infos"] = infos
                except Exception as e:
                    logger.exception(e)
                    context["form"] = form
                    self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)
            else:
                context["form"] = form

        return TemplateResponse(request, "core/admin/import_locations.html", context)

    @button(permission="core.load_from_datamart_adminarea")
    def load_from_datamart(self, request):
        context = self.get_common_context(request)
        if request.method == "GET":
            form = LoadAdminAreaForm(initial={"page_size": DatamartAPI.PAGE_SIZE})
            context["form"] = form
        else:
            form = LoadAdminAreaForm(data=request.POST)
            if form.is_valid():
                try:
                    country = form.cleaned_data["country"]
                    geom = form.cleaned_data["geometries"]
                    page_size = form.cleaned_data["page_size"]
                    max_records = form.cleaned_data["max_records"]
                    if form.cleaned_data["run_in_background"]:
                        load_admin_area.delay(
                            country, geom, page_size=page_size, max_records=max_records, notify_to=[request.user.email]
                        )
                        context["run_in_background"] = True
                    else:
                        results = load_admin_area(country, geom, page_size, max_records)
                        context["admin_areas"] = results
                except Exception as e:
                    context["form"] = form
                    self.message_user(request, str(e), messages.ERROR)
            else:
                context["form"] = form

        return TemplateResponse(request, "core/admin/load_admin_areas.html", context)


class FlexibleAttributeInline(admin.TabularInline):
    model = FlexibleAttribute
    fields = readonly_fields = ("name", "associated_with", "required")
    extra = 0


@admin.register(FlexibleAttribute)
class FlexibleAttributeAdmin(admin.ModelAdmin):
    list_display = ("type", "name", "required")
    list_filter = (
        ("type", ChoicesFieldComboFilter),
        ("associated_with", ChoicesFieldComboFilter),
        "required",
        "is_removed",
    )
    search_fields = ("name",)


@admin.register(FlexibleAttributeGroup)
class FlexibleAttributeGroupAdmin(MPTTModelAdmin):
    inlines = (FlexibleAttributeInline,)
    list_display = ("name", "parent", "required", "repeatable", "is_removed")
    autocomplete_fields = ("parent",)
    list_filter = ("repeatable", "required", "is_removed")
    search_fields = ("name",)


@admin.register(FlexibleAttributeChoice)
class FlexibleAttributeChoiceAdmin(admin.ModelAdmin):
    list_display = (
        "list_name",
        "name",
    )
    search_fields = ("name", "list_name")
    list_filter = ("is_removed",)
    filter_horizontal = ("flex_attributes",)


@admin.register(XLSXKoboTemplate)
class XLSXKoboTemplateAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("original_file_name", "uploaded_by", "created_at", "file", "import_status")

    exclude = ("is_removed", "file_name", "status", "template_id")

    readonly_fields = ("original_file_name", "uploaded_by", "file", "import_status", "error_description")

    def import_status(self, obj):
        if obj.status == self.model.SUCCESSFUL:
            color = "89eb34"
        elif obj.status == self.model.UNSUCCESSFUL:
            color = "e30b0b"
        else:
            color = "7a807b"

        return format_html(
            '<span style="color: #{};">{}</span>',
            color,
            obj.status,
        )

    def original_file_name(self, obj):
        return obj.file_name

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj is None:
            return XLSImportForm
        return super().get_form(request, obj, change, **kwargs)

    @button()
    def download_last_valid_file(self, request):
        latest_valid_import = self.model.objects.latest_valid()
        if latest_valid_import:
            return redirect(latest_valid_import.file.url)
        self.message_user(
            request,
            "There is no valid file to download",
            level=ERROR,
        )

    @button(label="Rerun KOBO Import", visible=lambda o: o is not None and o.status != XLSXKoboTemplate.SUCCESSFUL)
    def rerun_kobo_import(self, request, pk):
        xlsx_kobo_template_object = get_object_or_404(XLSXKoboTemplate, pk=pk)
        upload_new_kobo_template_and_update_flex_fields_task.run(
            xlsx_kobo_template_id=str(xlsx_kobo_template_object.id)
        )
        return redirect(".")

    def add_view(self, request, form_url="", extra_context=None):
        if not self.has_add_permission(request):
            logger.error("The user did not have permission to do that")
            raise PermissionDenied

        opts = self.model._meta
        app_label = opts.app_label

        context = {
            **self.admin_site.each_context(request),
            "opts": opts,
            "app_label": app_label,
            "has_file_field": True,
        }
        form_class = self.get_form(request)
        payload = {**context}

        if request.method == "POST":
            form = form_class(request.POST, request.FILES)
            payload["form"] = form
            xls_file = request.FILES["xls_file"]

            try:
                wb = xlrd.open_workbook(file_contents=xls_file.read())
                sheets = {
                    "survey_sheet": wb.sheet_by_name("survey"),
                    "choices_sheet": wb.sheet_by_name("choices"),
                }
                validation_errors = KoboTemplateValidator.validate_kobo_template(**sheets)
                if validation_errors:
                    errors = [f"Field: {error['field']} - {error['message']}" for error in validation_errors]
                    form.add_error(field=None, error=errors)
            except ValidationError as validation_error:
                logger.exception(validation_error)
                form.add_error("xls_file", validation_error)
            except XLRDError as file_error:
                logger.exception(file_error)
                form.add_error("xls_file", file_error)

            if form.is_valid():
                xlsx_kobo_template_object = XLSXKoboTemplate.objects.create(
                    file_name=xls_file.name,
                    uploaded_by=request.user,
                    file=xls_file,
                    status=XLSXKoboTemplate.UPLOADED,
                )
                self.message_user(
                    request,
                    "Core field validation successful, running KoBo Template upload task..., "
                    "Import status will change after task completion",
                )
                upload_new_kobo_template_and_update_flex_fields_task.run(
                    xlsx_kobo_template_id=str(xlsx_kobo_template_object.id)
                )
                return redirect("..")
        else:
            payload["form"] = form_class()

        return TemplateResponse(request, "core/xls_form.html", payload)

    def change_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = dict(show_save=False, show_save_and_continue=False, show_delete=True)
        has_add_permission = self.has_add_permission
        self.has_add_permission = lambda __: False
        template_response = super().change_view(request, object_id, form_url, extra_context)
        self.has_add_permission = has_add_permission

        return template_response


@admin.register(CountryCodeMap)
class CountryCodeMapAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("country", "alpha2", "alpha3", "ca_code")
    search_fields = ("country",)

    def alpha2(self, obj):
        return obj.country.countries.alpha2(obj.country.code)

    def alpha3(self, obj):
        return obj.country.countries.alpha3(obj.country.code)
