from collections import defaultdict

import xlrd
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import forms
from django.shortcuts import redirect, render, render_to_response
from django.urls import path
from django.utils.html import strip_tags
from xlrd import XLRDError

from core.models import (
    BusinessArea,
    FlexibleAttribute,
    FlexibleAttributeGroup,
    FlexibleAttributeChoice,
)


class XLSImportForm(forms.Form):
    xls_file = forms.FileField()


@admin.register(BusinessArea)
class BusinessAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


@admin.register(FlexibleAttribute)
class FlexibleAttributeAdmin(admin.ModelAdmin):
    change_list_template = "core/flexible_fields_changelist.html"

    TYPE_CHOICE_MAP = {
        "note": "STRING",
        "image": "IMAGE",
        "calculate": "DECIMAL",
        "select_one": "SELECT_ONE",
        "text": "STRING",
        "integer": "INTEGER",
        "date": "DATETIME",
        "select_multiple": "SELECT_MANY",
    }

    # Constants for xls import
    ATTRIBUTE_MODEL_FIELDS = [
        field.name for field in FlexibleAttribute._meta.get_fields()
    ]

    GROUP_MODEL_FIELDS = [
        field.name for field in FlexibleAttributeGroup._meta.get_fields()
    ]

    CHOICE_MODEL_FIELDS = [
        field.name for field in FlexibleAttributeChoice._meta.get_fields()
    ]

    CORE_FIELD_SUFFIXES = (
        "_h_c",
        "_i_c",
    )

    JSON_MODEL_FIELDS = (
        "label",
        "hint",
    )

    EXCLUDED_MODEL_FIELDS = (
        "start",
        "end",
        "deviceid",
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-xls/", self.import_xls),
        ]
        return my_urls + urls

    def _validate_file_has_required_core_fields(self, sheet):
        required_fields = [
            "consent_h_c",
            "residence_status_h_c",
            "nationality_h_c",
            "f_0_5_age_group_h_c",
            "f_6_11_age_group_h_c",
            "f_12_17_age_group_h_c",
            "f_adults_h_c",
            "m_0_5_age_group_h_c",
            "m_6_11_age_group_h_c",
            "m_12_17_age_group_h_c",
            "m_adults_h_c",
            "hh_size_h_c",
            "head_of_hh_i_c",
            "marital_status_i_c",
            "status_head_of_hh_i_c",
            "contact_details_i_c",
            "address_i_c",
            "admin1_i_c",
            "admin2_i_c",
            "phone_no_i_c",
            "phone_no_alternative_i_c",
            "given_name_i_c",
            "middle_name_i_c",
            "family_name_i_c",
            "full_name_i_c",
            "sex_i_c",
            "birth_date_i_c",
            "estimated_birth_date_i_c",
            "work_status_i_c",
            "disability_i_c",
        ]

        core_fields_from_xls = []
        for row_number in range(1, sheet.nrows):
            field_name = sheet.row(row_number)[1].value
            if any(field_name.endswith(i) for i in self.CORE_FIELD_SUFFIXES):
                core_fields_from_xls.append(field_name)

        missing = set(required_fields).difference(set(core_fields_from_xls))
        if missing:
            raise ValidationError(f"XLS File is missing core fields: {missing}")

    def _get_model_fields(self, object_type_to_add):
        return {
            "attribute": self.ATTRIBUTE_MODEL_FIELDS,
            "group": self.GROUP_MODEL_FIELDS,
            "choice": self.CHOICE_MODEL_FIELDS,
        }.get(object_type_to_add)

    def _assign_field_values(
        self, value, header_name, object_type_to_add, row, row_number
    ):
        model_fields = self._get_model_fields(object_type_to_add)

        if any(header_name.startswith(i) for i in self.JSON_MODEL_FIELDS):
            field_name, language = header_name.split("::")
            if field_name in model_fields:
                cleared_value = strip_tags(value).replace("#", "").strip()

                if field_name == "label" and language == "English(EN)":
                    is_index_field = row[1].value.endswith("_index")
                    # only index fields and group labels can be empty
                    if (
                        not value
                        and not is_index_field
                        and not object_type_to_add == "group"
                    ):
                        raise ValidationError(
                            f"Row {row_number + 1}: "
                            f"English label cannot be empty"
                        )

                self.json_fields_to_create[field_name].update(
                    {language: cleared_value if value else ""}
                )
            return

        if header_name == "required":
            if value == "true":
                self.object_fields_to_create[header_name] = True
            else:
                self.object_fields_to_create[header_name] = False
            return

        if header_name in model_fields:
            if header_name == "type":
                if not value:
                    raise ValidationError(
                        f"Row {row_number + 1}: Type is required"
                    )
                choice_key = value.split(" ")[0]

                if choice_key in self.TYPE_CHOICE_MAP.keys():
                    self.object_fields_to_create[
                        "type"
                    ] = self.TYPE_CHOICE_MAP.get(choice_key)
            else:
                is_attribute_name_empty = header_name == "name" and not value
                is_choice_list_name_empty = (
                    header_name == "list_name"
                    and object_type_to_add == "choice"
                ) and not value

                if is_attribute_name_empty:
                    raise ValidationError(
                        f"Row {row_number + 1}: Name is required"
                    )
                if is_choice_list_name_empty:
                    raise ValidationError(
                        f"Row {row_number + 1}: List Name is required"
                    )
                self.object_fields_to_create[header_name] = (
                    value if value else ""
                )
        elif header_name.startswith("admin"):
            self.object_fields_to_create["admin"] = value if value else ""

    def _can_add_row(self, row):
        is_core_field = any(
            row[1].value.endswith(i) for i in self.CORE_FIELD_SUFFIXES
        ) and not row[0].value.endswith("_group")

        is_in_excluded = row[0].value in self.EXCLUDED_MODEL_FIELDS

        is_version_field = row[1].value == "__version__"

        is_end_info = any(
            row[0].value == i for i in ("end_repeat", "end_group")
        )

        if is_end_info:
            self.current_group_tree.pop()
            return False

        if is_core_field or is_in_excluded or is_version_field:
            return False

        return True

    def _get_list_of_field_choices(self, sheet):
        fields_with_choices = []
        for row_number in range(1, sheet.nrows):
            row = sheet.row(row_number)
            if row[0].value.startswith("select_"):
                fields_with_choices.append(row)

        return set(row[0].value.split(" ")[1] for row in fields_with_choices)

    def _get_field_choice_name(self, row):
        has_choice = row[0].value.startswith("select_")
        if has_choice:
            return row[0].value.split(" ")[1]
        return

    def _reset_model_fields_variables(self):
        self.json_fields_to_create = defaultdict(dict)
        self.object_fields_to_create = {}

    def _handle_choices(self, sheets):
        choices_assigned_to_fields = self._get_list_of_field_choices(
            sheets["survey"]
        )
        choices_from_db = FlexibleAttributeChoice.objects.all()
        choices_first_row = sheets["choices"].row(0)
        choices_headers_map = [col.value for col in choices_first_row]
        to_create_choices = []
        updated_choices = []
        for row_number in range(1, sheets["choices"].nrows):
            row = sheets["choices"].row(row_number)
            self._reset_model_fields_variables()

            if row[0].value not in choices_assigned_to_fields:
                raise ValidationError(
                    f"Row {row_number + 1}: "
                    f"Choice is not assigned to any field"
                )

            for cell, header_name in zip(row, choices_headers_map):
                self._assign_field_values(
                    cell.value, header_name, "choice", row, row_number,
                )

            obj = FlexibleAttributeChoice.all_objects.filter(
                list_name=self.object_fields_to_create["list_name"],
                name=self.object_fields_to_create["name"],
            ).first()

            if obj:
                obj.label = self.json_fields_to_create["label"]
                obj.admin = self.object_fields_to_create["admin"]
                obj.is_removed = False
                obj.save()
                updated_choices.append(obj)
            else:
                choice = FlexibleAttributeChoice(
                    **self.object_fields_to_create,
                    **self.json_fields_to_create,
                )
                to_create_choices.append(choice)

        created_choices = FlexibleAttributeChoice.objects.bulk_create(
            to_create_choices,
        )

        choices_to_delete = set(choices_from_db).difference(
            set(created_choices + updated_choices)
        )

        for choice in choices_to_delete:
            choice.delete()

    def _handle_groups_and_fields(self, sheet):
        groups_from_db, attrs_from_db = (
            FlexibleAttributeGroup.objects.all(),
            FlexibleAttribute.objects.all(),
        )

        first_row = sheet.row(0)

        headers_map = [col.value for col in first_row]

        all_attrs = []
        all_groups = []
        for row_number in range(1, sheet.nrows):
            row = sheet.row(row_number)
            object_type_to_add = (
                "group"
                if row[0].value in ("begin_group", "begin_repeat")
                else "attribute"
            )
            repeatable = True if row[0].value == "begin_repeat" else False
            self._reset_model_fields_variables()

            if not self._can_add_row(row):
                continue

            for cell, header_name in zip(row, headers_map):
                value = cell.value

                self._assign_field_values(
                    value, header_name, object_type_to_add, row, row_number,
                )

            if object_type_to_add == "group":
                obj = FlexibleAttributeGroup.all_objects.filter(
                    name=self.object_fields_to_create["name"],
                ).first()

                if obj:
                    parent = self.current_group_tree[-1]
                    obj.label = self.json_fields_to_create["label"]
                    obj.hint = self.json_fields_to_create["hint"]
                    obj.repeatable = repeatable
                    obj.parent = parent
                    obj.is_removed = False
                    obj.save()
                    group = obj
                    self.current_group_tree.append(group)
                else:
                    group = FlexibleAttributeGroup.objects.create(
                        **self.object_fields_to_create,
                        **self.json_fields_to_create,
                        repeatable=repeatable,
                        parent=self.current_group_tree[-1],
                    )
                    self.current_group_tree.append(group)

                FlexibleAttributeGroup.objects.rebuild()

                all_groups.append(group)
            elif object_type_to_add == "attribute":
                choice_name = self._get_field_choice_name(row)
                obj = FlexibleAttribute.all_objects.filter(
                    name=self.object_fields_to_create["name"],
                ).first()

                if obj:
                    if obj.type != self.object_fields_to_create["type"]:
                        raise ValidationError(
                            f"Row {row_number + 1}: Type of the "
                            f"attribute cannot be changed!"
                        )
                    obj.type = self.object_fields_to_create["type"]
                    obj.name = self.object_fields_to_create["name"]
                    obj.required = self.object_fields_to_create["required"]
                    obj.label = self.json_fields_to_create["label"]
                    obj.hint = self.json_fields_to_create["hint"]
                    obj.is_removed = False
                    obj.save()
                    field = obj

                else:
                    field = FlexibleAttribute.objects.create(
                        group=self.current_group_tree[-1],
                        **self.object_fields_to_create,
                        **self.json_fields_to_create,
                    )
                if choice_name:
                    choices = FlexibleAttributeChoice.objects.filter(
                        list_name=choice_name,
                    )
                    field.flexibleattributechoice_set.set(choices)

                all_attrs.append(field)

        groups_to_delete = set(groups_from_db).difference(set(all_groups))

        for group in groups_to_delete:
            group.delete()

        attrs_to_delete = set(attrs_from_db).difference(set(all_attrs))

        for attr in attrs_to_delete:
            attr.delete()

    current_group_tree = None
    # variables re-initialized for each model creation
    json_fields_to_create = defaultdict(dict)
    object_fields_to_create = {}
    can_add_flag = True

    @transaction.atomic
    def import_xls(self, request):
        if request.method == "POST":
            form = XLSImportForm(request.POST, request.FILES)

            xls_file = request.FILES["xls_file"]

            # Disabled till we now what core fields we should have
            # self._validate_file_has_required_core_fields(sheets["survey"])
            self.current_group_tree = [None]

            try:
                wb = xlrd.open_workbook(file_contents=xls_file.read())
                sheets = {
                    "survey": wb.sheet_by_name("survey"),
                    "choices": wb.sheet_by_name("choices"),
                }
                self._handle_choices(sheets)
                self._handle_groups_and_fields(sheets["survey"])
            except ValidationError as validation_error:
                form.add_error("xls_file", validation_error)
                transaction.set_rollback(True)
            except XLRDError as file_error:
                form.add_error("xls_file", file_error)
                transaction.set_rollback(True)

            if form.is_valid():
                self.message_user(request, "Your xls file has been imported, ")
                return redirect("..")
            else:
                payload = {"form": form}
                return render(request, "core/xls_form.html", payload)

        form = XLSImportForm()
        payload = {"form": form}

        return render(request, "core/xls_form.html", payload)


@admin.register(FlexibleAttributeGroup)
class FlexibleAttributeGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(FlexibleAttributeChoice)
class FlexibleAttributeChoiceAdmin(admin.ModelAdmin):
    pass
