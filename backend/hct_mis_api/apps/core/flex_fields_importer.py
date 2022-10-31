import logging
from collections import defaultdict
from os.path import isfile
from typing import List, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.html import strip_tags

import xlrd

from hct_mis_api.apps.core.core_fields_attributes import (
    TYPE_DATE,
    TYPE_DECIMAL,
    TYPE_IMAGE,
    TYPE_INTEGER,
    TYPE_SELECT_MANY,
    TYPE_SELECT_ONE,
    TYPE_STRING,
)
from hct_mis_api.apps.core.models import (
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
)

logger = logging.getLogger(__name__)


class FlexibleAttributeImporter:
    TYPE_CHOICE_MAP = {
        "note": TYPE_STRING,
        "image": TYPE_IMAGE,
        "select_one": TYPE_SELECT_ONE,
        "text": TYPE_STRING,
        "integer": TYPE_INTEGER,
        "decimal": TYPE_DECIMAL,
        "date": TYPE_DATE,
        "select_multiple": TYPE_SELECT_MANY,
    }
    CALCULATE_TYPE_CHOICE_MAP = {
        "text": TYPE_STRING,
        "integer": TYPE_INTEGER,
        "decimal": TYPE_DECIMAL,
        "date": TYPE_DATE,
    }

    # Constants for xls import
    ATTRIBUTE_MODEL_FIELDS = [field.name for field in FlexibleAttribute._meta.get_fields()]

    GROUP_MODEL_FIELDS = [field.name for field in FlexibleAttributeGroup._meta.get_fields()]

    CHOICE_MODEL_FIELDS = [field.name for field in FlexibleAttributeChoice._meta.get_fields()]

    CORE_FIELD_SUFFIXES = (
        "_h_c",
        "_i_c",
    )

    FLEX_FIELD_SUFFIXES = (
        "_h_f",
        "_i_f",
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

    def _get_model_fields(self, object_type_to_add) -> Optional[List[str]]:
        return {
            "attribute": self.ATTRIBUTE_MODEL_FIELDS,
            "group": self.GROUP_MODEL_FIELDS,
            "choice": self.CHOICE_MODEL_FIELDS,
        }.get(object_type_to_add)

    def _assign_field_values(self, value, header_name, object_type_to_add, row, row_number) -> None:
        if not (model_fields := self._get_model_fields(object_type_to_add)):
            return

        if any(header_name.startswith(i) for i in self.JSON_MODEL_FIELDS):
            if "::" in header_name:
                label, language = header_name.split("::")
            else:
                label, language = header_name.split(":")

            if label in model_fields:
                cleared_value = strip_tags(value).replace("#", "").strip()

                if label == "label" and language == "English(EN)":
                    if isinstance(row[1].value, str):
                        is_index_field = row[1].value.endswith("_index")
                    else:
                        is_index_field = False

                    if object_type_to_add == "attribute":
                        field_suffix = row[1].value[-4:]
                        is_empty_and_not_index_field = not value and not is_index_field
                        is_core_or_flex_field = (
                            field_suffix in self.CORE_FIELD_SUFFIXES or field_suffix in self.FLEX_FIELD_SUFFIXES
                        )
                        if is_empty_and_not_index_field and is_core_or_flex_field:
                            logger.error(f"Survey Sheet: Row {row_number + 1}: English label cannot be empty")
                            raise ValidationError(f"Survey Sheet: Row {row_number + 1}: English label cannot be empty")
                    if object_type_to_add == "choice" and not value:
                        logger.error(f"Choices Sheet: Row {row_number + 1}: English label cannot be empty")
                        raise ValidationError(f"Choices Sheet: Row {row_number + 1}: English label cannot be empty")

                self.json_fields_to_create[label].update({language: cleared_value if value else ""})
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
                    logger.error(f"Survey Sheet: Row {row_number + 1}: Type is required")
                    raise ValidationError(f"Survey Sheet: Row {row_number + 1}: Type is required")
                choice_key = value.split(" ")[0]
                if choice_key == "calculate":
                    self.object_fields_to_create["type"] = "calculate"
                elif choice_key in self.TYPE_CHOICE_MAP.keys():
                    self.object_fields_to_create["type"] = self.TYPE_CHOICE_MAP.get(choice_key)
            else:
                is_attribute_name_empty = header_name == "name" and value in (None, "")
                is_choice_list_name_empty = (
                    header_name == "list_name" and object_type_to_add == "choice"
                ) and not value

                if is_attribute_name_empty:
                    logger.error(f"Survey Sheet: Row {row_number + 1}: Name is required")
                    raise ValidationError(f"Survey Sheet: Row {row_number + 1}: Name is required")
                if is_choice_list_name_empty:
                    logger.error(f"Survey Sheet: Row {row_number + 1}: List Name is required")
                    raise ValidationError(f"Survey Sheet: Row {row_number + 1}: List Name is required")
                self.object_fields_to_create[header_name] = value if value else ""

        is_valid_calculate_field_and_header_is_calculate_field_type = (
            object_type_to_add == "attribute"
            and header_name == "calculated_result_field_type"
            and row[0].value == "calculate"
            and any(self.object_fields_to_create["name"].endswith(i) for i in self.FLEX_FIELD_SUFFIXES)
        )
        if is_valid_calculate_field_and_header_is_calculate_field_type:
            choice_key = value.strip() if value and isinstance(value, str) else None
            if choice_key is None:
                validation_error_message = (
                    f"Survey Sheet: Row {row_number + 1}: "
                    f"Calculated result field type must be provided for calculate type fields"
                )
                logger.error(validation_error_message)
                raise ValidationError(validation_error_message)
            elif choice_key not in self.CALCULATE_TYPE_CHOICE_MAP.keys():
                validation_error_message = (
                    f"Survey Sheet: Row {row_number + 1}: "
                    f"Invalid type: {choice_key} for calculate field, valid choices are "
                    f"{', '.join(self.CALCULATE_TYPE_CHOICE_MAP.keys())}"
                )
                logger.error(validation_error_message)
                raise ValidationError(validation_error_message)
            else:
                self.object_fields_to_create["type"] = self.CALCULATE_TYPE_CHOICE_MAP[choice_key]

    def _can_add_row(self, row):
        is_core_field = any(row[1].value.endswith(i) for i in self.CORE_FIELD_SUFFIXES) and not row[0].value.endswith(
            "_group"
        )

        is_in_excluded = row[0].value in self.EXCLUDED_MODEL_FIELDS

        is_version_field = row[1].value == "__version__"

        is_end_info = any(row[0].value == i for i in ("end_repeat", "end_group"))

        if is_end_info:
            if self.current_group_tree:
                self.current_group_tree.pop()
            else:
                self.current_group_tree = []
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

        return {row[0].value.split(" ")[1] for row in fields_with_choices}

    def _get_field_choice_name(self, row):
        has_choice = row[0].value.startswith("select_")
        if has_choice:
            return row[0].value.split(" ")[1]
        return

    def _reset_model_fields_variables(self) -> None:
        self.json_fields_to_create = defaultdict(dict)
        self.object_fields_to_create = {}

    def _handle_choices(self, sheets) -> None:
        choices_assigned_to_fields = self._get_list_of_field_choices(sheets["survey"])
        choices_from_db = FlexibleAttributeChoice.objects.all()
        choices_first_row = sheets["choices"].row(0)
        choices_headers_map = [col.value for col in choices_first_row]
        to_create_choices = []
        updated_choices = []
        for row_number in range(1, sheets["choices"].nrows):
            row = sheets["choices"].row(row_number)
            self._reset_model_fields_variables()

            if all([cell.ctype == xlrd.XL_CELL_EMPTY for cell in row]):
                continue

            if row[0].value not in choices_assigned_to_fields:
                continue

            for cell, header_name in zip(row, choices_headers_map):
                cell_value = cell.value
                if isinstance(cell_value, float) and cell_value.is_integer():
                    cell_value = str(int(cell_value))
                self._assign_field_values(
                    cell_value,
                    header_name,
                    "choice",
                    row,
                    row_number,
                )

            obj = FlexibleAttributeChoice.all_objects.filter(
                list_name=self.object_fields_to_create["list_name"],
                name=self.object_fields_to_create["name"],
            ).first()

            if obj:
                obj.label = self.json_fields_to_create["label"]
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

        choices_to_delete = set(choices_from_db).difference(set(created_choices + updated_choices))

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

            if all([cell.ctype == xlrd.XL_CELL_EMPTY for cell in row]):
                continue

            object_type_to_add = "group" if row[0].value in ("begin_group", "begin_repeat") else "attribute"
            repeatable = True if row[0].value == "begin_repeat" else False
            self._reset_model_fields_variables()

            if not self._can_add_row(row):
                continue

            for cell, header_name in zip(row, headers_map):
                value = cell.value

                self._assign_field_values(
                    value,
                    header_name,
                    object_type_to_add,
                    row,
                    row_number,
                )

            is_flex_field = any(self.object_fields_to_create["name"].endswith(i) for i in self.FLEX_FIELD_SUFFIXES)

            if object_type_to_add == "group":
                obj = FlexibleAttributeGroup.all_objects.filter(
                    name=self.object_fields_to_create["name"],
                ).first()

                if self.current_group_tree:
                    parent = self.current_group_tree[-1]
                else:
                    parent = None

                if obj:
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
                        parent=parent,
                    )
                    self.current_group_tree.append(group)

                FlexibleAttributeGroup.objects.rebuild()

                all_groups.append(group)

            elif object_type_to_add == "attribute" and is_flex_field:
                choice_name = self._get_field_choice_name(row)
                obj = FlexibleAttribute.all_objects.filter(
                    name=self.object_fields_to_create["name"],
                ).first()

                if self.current_group_tree:
                    parent = self.current_group_tree[-1]
                else:
                    parent = None

                if obj:
                    if obj.type != self.object_fields_to_create["type"] and not obj.is_removed:
                        logger.error(
                            f"Survey Sheet: Row {row_number + 1}: Type of the " f"attribute cannot be changed!"
                        )
                        raise ValidationError(
                            f"Survey Sheet: Row {row_number + 1}: Type of the attribute cannot be changed!"
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
                    attribute_suffix = self.object_fields_to_create["name"][-4:]
                    field = FlexibleAttribute.objects.create(
                        group=parent,
                        associated_with=(0 if attribute_suffix == "_h_f" else 1),
                        **self.object_fields_to_create,
                        **self.json_fields_to_create,
                    )

                if choice_name:
                    choices = FlexibleAttributeChoice.objects.filter(
                        list_name=choice_name,
                    )
                    field.choices.set(choices)

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
    def import_xls(self, xls_file) -> None:
        self.current_group_tree = [None]
        if isinstance(xls_file, str) and isfile(xls_file):
            wb = xlrd.open_workbook(filename=xls_file)
        else:
            xls_file.seek(0)
            wb = xlrd.open_workbook(file_contents=xls_file.read())
        sheets = {
            "survey": wb.sheet_by_name("survey"),
            "choices": wb.sheet_by_name("choices"),
        }
        self._handle_choices(sheets)
        self._handle_groups_and_fields(sheets["survey"])
