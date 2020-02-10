from collections import defaultdict

import xlrd
from django.contrib import admin
from django.db import transaction
from django.forms import forms, ModelChoiceField
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import strip_tags

from core.models import (
    BusinessArea,
    FlexibleAttribute,
    FlexibleAttributeGroup,
    FlexibleAttributeChoice,
)


class XLSImportForm(forms.Form):
    business_area = ModelChoiceField(queryset=BusinessArea.objects.all())
    xls_file = forms.FileField()


@admin.register(BusinessArea)
class BusinessAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


@admin.register(FlexibleAttribute)
class FlexibleAttributeAdmin(admin.ModelAdmin):
    change_list_template = "core/flexible_fields_changelist.html"
    attribute_model_fields = [
        field.name for field in FlexibleAttribute._meta.get_fields()
    ]

    group_model_fields = [
        field.name for field in FlexibleAttributeGroup._meta.get_fields()
    ]

    choice_model_fields = [
        field.name for field in FlexibleAttributeChoice._meta.get_fields()
    ]

    core_field_suffixes = (
        "_h_c",
        "_i_c",
    )

    language_fields = (
        "label",
        "hint",
    )

    fields_to_exclude = (
        "start",
        "end",
        "deviceid",
    )

    json_fields = defaultdict(dict)

    object_fields = {}

    group_tree = [None]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-xls/", self.import_xls),
        ]
        return my_urls + urls

    def assign_field_value(
        self, value, header_name, object_type_to_add="choice",
    ):
        if object_type_to_add == "attribute":
            model_fields = self.attribute_model_fields
        elif object_type_to_add == "group":
            model_fields = self.group_model_fields
        else:
            model_fields = self.choice_model_fields

        if any(header_name.startswith(i) for i in self.language_fields):
            field_name, language = header_name.split("::")
            if field_name in model_fields:
                cleared_value = strip_tags(value).replace("#", "").strip()
                self.json_fields[field_name].update(
                    {language: cleared_value if value else ""}
                )
            return

        if header_name == "required":
            if value == "true":
                self.object_fields[header_name] = True
            else:
                self.object_fields[header_name] = False
            return

        if header_name in model_fields:
            self.object_fields[header_name] = value if value else ""
        elif header_name.startswith("admin"):
            self.object_fields["admin"] = value if value else ""

    def check_if_can_add(self, value, row):
        is_core_field = isinstance(value, str) and any(
            value.endswith(i) for i in self.core_field_suffixes
        ) and not row[0].value.endswith('_group')

        is_in_excluded = value in self.fields_to_exclude

        is_end_info = any(value == i for i in ("end_repeat", "end_group"))

        if is_end_info:
            self.group_tree.pop()
            return False

        if is_core_field or is_in_excluded:
            return False

        return True

    @transaction.atomic
    def import_xls(self, request):
        # TODO: Break this code into smaller pieces (functions)
        if request.method == "POST":
            xls_file = request.FILES["xls_file"]
            business_area_id = request.POST.get("business_area")
            business_area = BusinessArea.objects.get(id=business_area_id)

            groups_from_db = FlexibleAttributeGroup.objects.filter(
                business_area=business_area
            )
            attrs_from_db = FlexibleAttribute.objects.filter(
                business_area=business_area
            )

            wb = xlrd.open_workbook(file_contents=xls_file.read())

            sheets = {
                "survey": wb.sheet_by_name("survey"),
                "choices": wb.sheet_by_name("choices"),
            }

            first_row = sheets["survey"].row(0)

            headers_map = [col.value for col in first_row]

            all_attrs = []
            all_groups = []
            updated_attrs = []
            for row_number in range(1, sheets["survey"].nrows):
                row = sheets["survey"].row(row_number)
                object_type_to_add = (
                    "group"
                    if row[0].value in ("begin_group", "begin_repeat")
                    else "attribute"
                )
                repeatable = True if row[0].value == "begin_repeat" else False
                can_add_flag = True
                self.json_fields = defaultdict(dict)
                self.object_fields = {}

                for cell, header_name in zip(row, headers_map):
                    value = cell.value

                    if not self.check_if_can_add(value, row):
                        can_add_flag = False
                        break

                    self.assign_field_value(
                        value, header_name, object_type_to_add
                    )

                if can_add_flag:
                    if object_type_to_add == "group":
                        from_db = FlexibleAttributeGroup.objects.filter(
                            name=self.object_fields["name"],
                            business_area=business_area,
                        )
                        if from_db:
                            from_db.update(
                                name=self.object_fields["name"],
                                **self.json_fields,
                                repeatable=repeatable,
                                parent=self.group_tree[-1],
                            )
                            group = FlexibleAttributeGroup.objects.get(
                                name=self.object_fields["name"],
                                business_area=business_area,
                            )
                            self.group_tree.append(group)
                        else:
                            group = FlexibleAttributeGroup.objects.create(
                                **self.object_fields,
                                **self.json_fields,
                                repeatable=repeatable,
                                parent=self.group_tree[-1],
                                business_area=business_area,
                                lft=1,
                                rght=1,
                                tree_id=1,
                                level=1,
                            )
                            self.group_tree.append(group)
                        all_groups.append(group)
                    elif object_type_to_add == "attribute":
                        obj = FlexibleAttribute.objects.filter(
                            name=self.object_fields["name"],
                            type=self.object_fields["type"],
                            business_area=business_area,
                        )
                        if obj:
                            obj.update(
                                group=self.group_tree[-1],
                                **self.object_fields,
                                **self.json_fields,
                            )
                            updated_attrs.append(
                                FlexibleAttribute.objects.get(
                                    name=self.object_fields["name"],
                                    type=self.object_fields["type"],
                                    business_area=business_area,
                                )
                            )
                        else:
                            all_attrs.append(
                                FlexibleAttribute(
                                    business_area=business_area,
                                    group=self.group_tree[-1],
                                    **self.object_fields,
                                    **self.json_fields,
                                )
                            )

            groups_to_delete = set(groups_from_db).difference(set(all_groups))

            for group in groups_to_delete:
                group.delete()

            created_attribs = FlexibleAttribute.objects.bulk_create(all_attrs)
            attrs_to_delete = set(attrs_from_db).difference(
                set(created_attribs + updated_attrs)
            )

            for attr in attrs_to_delete:
                attr.delete()

            choices_first_row = sheets["choices"].row(0)
            choices_headers_map = [col.value for col in choices_first_row]
            choices_from_db = FlexibleAttributeChoice.objects.all()
            created_choices = []
            updated_choices = []
            for row_number in range(1, sheets["choices"].nrows):
                row = sheets["choices"].row(row_number)
                self.json_fields = defaultdict(dict)
                self.object_fields = {}

                for cell, header_name in zip(row, choices_headers_map):
                    self.assign_field_value(
                        cell.value, header_name,
                    )

                flex_attrs = FlexibleAttribute.objects.filter(
                    type__contains=self.object_fields["list_name"],
                    business_area=business_area,
                )

                obj = FlexibleAttributeChoice.objects.filter(
                    list_name=self.object_fields["list_name"],
                    name=self.object_fields["name"],
                    business_area=business_area,
                )

                if obj:
                    obj.update(
                        business_area=business_area,
                        **self.object_fields,
                        **self.json_fields,
                    )
                    updated_choices.append(
                        FlexibleAttributeChoice.objects.filter(
                            list_name=self.object_fields["list_name"],
                            name=self.object_fields["name"],
                        )
                    )
                    obj.first().flex_attributes.set(flex_attrs)

                created = FlexibleAttributeChoice.objects.create(
                    business_area=business_area,
                    **self.object_fields,
                    **self.json_fields,
                )
                created.flex_attributes.set(flex_attrs)
                created_choices.append(created)

            choices_to_delete = set(choices_from_db).difference(
                set(created_choices + updated_choices)
            )

            for choice in choices_to_delete:
                choice.delete()

            self.message_user(request, "Your xls file has been imported, ")
            return redirect("..")

        form = XLSImportForm()
        payload = {"form": form}

        return render(request, "core/xls_form.html", payload)


@admin.register(FlexibleAttributeGroup)
class FlexibleAttributeGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(FlexibleAttributeChoice)
class FlexibleAttributeChoiceAdmin(admin.ModelAdmin):
    pass
