import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Iterable

import xlrd
from django.core.exceptions import ValidationError

from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.apps.core.field_attributes.fields_types import (
    TYPE_BOOL,
    TYPE_DATE,
    TYPE_DECIMAL,
    TYPE_GEOPOINT,
    TYPE_IMAGE,
    TYPE_INTEGER,
    TYPE_SELECT_MANY,
    TYPE_SELECT_ONE,
    TYPE_STRING,
    Scope,
)
from hope.apps.core.utils import xlrd_rows_iterator
from hope.apps.household.models import (
    BLANK,
    NOT_PROVIDED,
    RELATIONSHIP_UNKNOWN,
)

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet


logger = logging.getLogger(__name__)


class BaseValidator:
    """Base validation class, inherit from this class to create custom validators.

    Your custom validators have to implement validation methods that starts
    with name "validate_" so validate can call all the validators from your
    custom validator.

    Custom validate method have to takes *args, **kwargs parameters.

    validate method with parameters have to be called in mutate method.
    If there are validation errors they will be all
    returned as one error message.
    """

    @classmethod
    def validate(cls, excluded_validators: Any | None = None, *args: Any, **kwargs: Any) -> None:
        if not excluded_validators:
            excluded_validators = []

        validate_methods = [
            getattr(cls, m) for m in dir(cls) if m.startswith("validate_") and m not in excluded_validators
        ]

        errors_list = []
        for method in validate_methods:
            try:
                method(*args, **kwargs)
            except ValidationError as e:
                errors_list.append(e.message)

        if errors_list:
            logger.warning(", ".join(errors_list))
            raise Exception(", ".join(errors_list))


def prepare_choices_for_validation(choices_sheet: "Worksheet") -> dict[str, list[str]]:
    choices_mapping = defaultdict(list)
    first_row = choices_sheet.row(0)
    choices_headers_map = [col.value for col in first_row]
    required_columns = {"list_name", "name"}
    if required_columns.issubset(set(choices_headers_map)) is False:
        missing_columns = required_columns - set(choices_headers_map)
        str_missing_columns = ", ".join(missing_columns)
        msg = f"Choices sheet does not contain all required columns, missing columns: {str_missing_columns}"
        logger.warning(msg)
        raise ValidationError(msg)

    for row_number in range(1, choices_sheet.nrows):
        row = choices_sheet.row(row_number)

        if all(cell.ctype == xlrd.XL_CELL_EMPTY for cell in row):
            continue

        last_list_name = None
        choice_value = None
        for cell, header_name in zip(row, choices_headers_map, strict=True):
            cell_value = cell.value
            if header_name == "list_name" and cell_value != last_list_name:
                last_list_name = str(cell_value).strip()
            elif header_name == "name":
                if isinstance(cell_value, float) and cell_value.is_integer():
                    cell_value = str(int(cell_value))

                if isinstance(cell_value, str):
                    cell_value = cell_value.strip().upper()

                choice_value = cell_value

        if last_list_name is not None and choice_value is not None:
            choices_mapping[last_list_name].append(choice_value)

    return choices_mapping


class KoboTemplateValidator:
    CHOICE_MAP = {
        "note": TYPE_STRING,
        "image": TYPE_IMAGE,
        "calculate": TYPE_STRING,
        "select_one": TYPE_SELECT_ONE,
        "text": TYPE_STRING,
        "integer": TYPE_INTEGER,
        "decimal": TYPE_DECIMAL,
        "date": TYPE_DATE,
        "select_multiple": TYPE_SELECT_MANY,
        "geopoint": TYPE_GEOPOINT,
        "start": TYPE_STRING,
        "end": TYPE_STRING,
        "deviceid": TYPE_STRING,
    }
    EXPECTED_REQUIRED_FIELDS = (
        "country_h_c",
        "size_h_c",
        "relationship_i_c",
        "full_name_i_c",
        "gender_i_c",
        "birth_date_i_c",
        "estimated_birth_date_i_c",
    )
    FIELDS_EXCLUDED_FROM_CHOICE_CHECK = (
        # temporarily disabled from checking
        "admin1_h_c",
        "admin2_h_c",
        "disability_i_c",
        "preferred_language_i_c",
    )
    CHOICES_EXCLUDED_FROM_CHECKING = (
        BLANK,
        NOT_PROVIDED,
        RELATIONSHIP_UNKNOWN,
    )

    @classmethod
    def _map_columns_numbers(cls, first_row: Iterable) -> dict[str, int]:
        columns_names_and_numbers_mapping: dict[str, Any] = {
            "type": None,
            "name": None,
            "required": None,
        }

        for index, cell in enumerate(first_row):
            column_name = cell.value
            if column_name in columns_names_and_numbers_mapping:
                columns_names_and_numbers_mapping[column_name] = index

        if None in columns_names_and_numbers_mapping.values():
            logger.warning("Survey sheet does not contain all required columns")
            raise ValidationError("Survey sheet does not contain all required columns")

        return columns_names_and_numbers_mapping

    @classmethod
    def _get_core_fields_from_file(
        cls,
        survey_sheet: "Worksheet",
        choices_mapping: dict,
        columns_names_and_numbers_mapping: dict,
    ) -> dict:
        core_fields_in_file = {}
        for row in xlrd_rows_iterator(survey_sheet):
            field_name = row[columns_names_and_numbers_mapping["name"]].value
            if field_name.endswith("_c") is False:
                continue

            field_type = row[columns_names_and_numbers_mapping["type"]].value

            choices_list_name = None
            if field_type.startswith("select_"):
                field_type, choices_list_name, *_ = field_type.split(" ")

            if field_type not in cls.CHOICE_MAP:
                continue

            required_value = str(row[columns_names_and_numbers_mapping["required"]].value)
            if required_value.lower() not in ("true", "false"):
                is_field_required = False
            else:
                is_field_required = bool(required_value == "true")

            field_type = cls.CHOICE_MAP[field_type] if field_type != "calculate" else "CALCULATE"

            core_fields_in_file[field_name] = {
                "type": field_type,
                "required": is_field_required,
                "choices": choices_mapping[choices_list_name] if choices_list_name is not None else [],
            }

        return core_fields_in_file

    @classmethod
    def _get_core_fields_from_db(cls) -> dict:
        all_core_fields = FieldFactory.from_scope(Scope.KOBO_IMPORT).apply_business_area()
        return {
            core_field_data["xlsx_field"]: {
                "type": core_field_data["type"],
                "required": core_field_data["required"],
                "choices": core_field_data["choices"],
            }
            for core_field_data in all_core_fields
            if core_field_data["xlsx_field"].endswith("_c")
        }

    @classmethod
    def _check_field_type(cls, core_field: Any, core_field_from_file: dict, field_type: str) -> dict | None:
        if field_type != core_field_from_file["type"] and core_field_from_file["type"] != "CALCULATE":
            return {
                "field": core_field,
                "message": f"Expected type: {field_type}, actual type: {core_field_from_file['type']}",
            }
        return None

    @classmethod
    def _check_is_field_required(cls, core_field: Any, core_field_from_file: dict) -> dict | None:
        field_from_file_required = str(core_field_from_file["required"])

        if core_field in cls.EXPECTED_REQUIRED_FIELDS and field_from_file_required.lower() != "true":
            return {
                "field": core_field,
                "message": "Field must be required",
            }
        return None

    @classmethod
    def _check_field_choices(cls, core_field: Any, core_field_from_file: Any, field_choices: list) -> list | None:
        if core_field in cls.FIELDS_EXCLUDED_FROM_CHOICE_CHECK:
            return None

        from_file_choices = core_field_from_file["choices"]
        errors = []

        for internal_choice in field_choices:
            if internal_choice in cls.CHOICES_EXCLUDED_FROM_CHECKING:
                continue

            if internal_choice not in from_file_choices:
                errors.append(
                    {
                        "field": core_field,
                        "message": f"Choice: {internal_choice} is not present in the file",
                    }
                )

        errors += [
            {
                "field": core_field,
                "message": f"Choice: {file_choice} is not present in HOPE",
            }
            for file_choice in from_file_choices
            if file_choice not in field_choices
        ]
        return errors

    @classmethod
    def validate_kobo_template(cls, survey_sheet: "Worksheet", choices_sheet: "Worksheet") -> list[dict[str, str]]:
        choices_mapping = prepare_choices_for_validation(choices_sheet)

        first_row = survey_sheet.row(0)
        columns_names_and_numbers_mapping = cls._map_columns_numbers(first_row)

        core_fields_in_file = cls._get_core_fields_from_file(
            survey_sheet, choices_mapping, columns_names_and_numbers_mapping
        )
        core_fields_in_db = cls._get_core_fields_from_db()

        validation_errors = []
        for core_field, field_data in core_fields_in_db.items():
            field_type = field_data["type"]
            field_choices = [choice["value"] for choice in field_data["choices"]]

            if not (core_field_from_file := core_fields_in_file.get(core_field)):
                validation_errors.append({"field": core_field, "message": "Field is missing"})
                continue

            field_required_error = cls._check_is_field_required(core_field, core_field_from_file)
            if field_required_error:
                validation_errors.append(field_required_error)

            if field_type == TYPE_BOOL and core_field_from_file["type"] == TYPE_SELECT_ONE:
                continue

            field_type_error = cls._check_field_type(core_field, core_field_from_file, field_type)
            if field_type_error:
                validation_errors.append(field_type_error)

            field_choices_errors = cls._check_field_choices(core_field, core_field_from_file, field_choices)
            if field_choices_errors:
                validation_errors.extend(field_choices_errors)

        return validation_errors
