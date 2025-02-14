from typing import Union

from admin_extra_buttons.decorators import button
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.forms import SimpleArrayField
from django.forms import CheckboxSelectMultiple
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse

from .models import UniversalUpdate, DocumentType, DeliveryMechanism, Program
from .universal_individual_update_script.all_updatable_fields import (
    individual_fields,
    get_individual_flex_fields,
    household_fields,
)
from .universal_individual_update_script.universal_individual_update_script import UniversalIndividualUpdateEngine
from ..utils.admin import HOPEModelAdminBase
from .celery_tasks import run_universal_update


class ArrayFieldFilteredSelectMultiple(FilteredSelectMultiple):

    def format_value(self, value):
        """Return selected values as a list."""
        if value is None and self.allow_multiple_selected:
            return []
        elif self.allow_multiple_selected:
            value = [v for v in value.split(",")]

        if not isinstance(value, (tuple, list)):
            value = [value]

        results = [str(v) if v is not None else '' for v in value]
        return results

class UniversalUpdateAdminForm(forms.ModelForm):
    individual_fields = SimpleArrayField(
        base_field=forms.CharField(max_length=255),
        widget=ArrayFieldFilteredSelectMultiple("Individual Fields", is_stacked=False),
        required=False,
    )
    individual_flex_fields_fields = SimpleArrayField(
        base_field=forms.CharField(max_length=255),
        widget=ArrayFieldFilteredSelectMultiple("Individual Flex Fields", is_stacked=False),
        required=False,
    )
    household_fields = SimpleArrayField(
        base_field=forms.CharField(max_length=255),
        widget=ArrayFieldFilteredSelectMultiple("Household Fields", is_stacked=False),
        required=False,
    )

    class Meta:
        model = UniversalUpdate
        fields = '__all__'
        widgets = {
            'document_types': FilteredSelectMultiple("Document Types", is_stacked=False),
            'delivery_mechanisms': FilteredSelectMultiple("Delivery Mechanisms", is_stacked=False),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use list() to ensure choices are set as a list of tuples
        self.fields['individual_fields'].widget.choices = list(self.get_dynamic_individual_fields_choices())
        self.fields['individual_flex_fields_fields'].widget.choices = list(self.get_dynamic_individual_flex_fields_choices())
        self.fields['household_fields'].widget.choices = list(self.get_dynamic_household_fields_choices())
        self.fields['document_types'].queryset = self.get_dynamic_document_types_queryset()
        self.fields['delivery_mechanisms'].queryset = self.get_dynamic_delivery_mechanisms_queryset()



    def get_dynamic_individual_fields_choices(self):
        for _column_name, field_data in individual_fields.items():
            yield (field_data[0], field_data[0])

    def get_dynamic_individual_flex_fields_choices(self):
        for key, field_data in get_individual_flex_fields().items():
            yield (field_data[0], field_data[0])

    def get_dynamic_household_fields_choices(self):
        for key, field_data in household_fields.items():
            yield (field_data[0], field_data[0])

    def get_dynamic_document_types_queryset(self):
        return DocumentType.objects.all()

    def get_dynamic_delivery_mechanisms_queryset(self):
        return DeliveryMechanism.objects.all()


@admin.register(UniversalUpdate)
class UniversalUpdateAdmin(HOPEModelAdminBase):
    form = UniversalUpdateAdminForm
    filter_horizontal = ('document_types', 'delivery_mechanisms',)
    autocomplete_fields = ('program',)
    list_display = ('id', 'program', 'update_file', 'created_at', 'updated_at')
    readonly_fields = ('saved_logs', 'logs_property', 'backup_snapshot',)
    fieldsets = (
        (None, {
            'fields': ('program', 'update_file',"unicef_ids"),
        }),
        ('Field Configuration', {
            'fields': ('individual_fields', 'individual_flex_fields_fields', 'household_fields','document_types', 'delivery_mechanisms'),
        }),
        ('Logs', {
            'fields': ('logs_property', 'saved_logs'),
        }),
        ('Backup', {
            'fields': ('backup_snapshot',),
        }),
    )

    def logs_property(self, obj):
        return obj.logs or "-"
    logs_property.short_description = "Live Logs"

    @button(label="Generate Excel Template")
    def generate_xlsx_template(self, request, pk):
        universal_update = self.get_object(request, pk)
        engine = UniversalIndividualUpdateEngine(
            universal_update,
            ignore_empty_values=True,
            deduplicate_es=False,
            deduplicate_documents=False,
        )
        xlsx_file = engine.create_xlsx_template()
        xlsx_file.seek(0)
        content = xlsx_file.read()
        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="update_template.xlsx"'
        return response


    @button(label="Start Universal Update Task")
    def start_universal_update_task(self, request, pk):
        universal_update = self.get_object(request, pk)
        result = run_universal_update.delay(str(universal_update.id))
        self.message_user(request, f"Celery task scheduled with task id: {result.id}")
        return None
