import re
from datetime import datetime
from pathlib import Path
from zipfile import BadZipfile

import openpyxl
import phonenumbers
from dateutil import parser
from openpyxl import load_workbook

from core.core_fields_attributes import CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY
from core.utils import (
    serialize_flex_attributes,
    get_combined_attributes, get_admin_areas_as_choices,
)
from core.validators import BaseValidator


class UploadXLSXValidator(BaseValidator):
    WB = None
    CORE_FIELDS = CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY
    FLEX_FIELDS = serialize_flex_attributes()
    ALL_FIELDS = get_combined_attributes()

    @classmethod
    def validate(cls, *args, **kwargs):
        validate_methods = [
            getattr(cls, m) for m in dir(cls) if m.startswith("validate_")
        ]

        errors_list = []
        for method in validate_methods:
            errors = method(cls, *args, **kwargs)
            errors_list.extend(errors)

        return errors_list

    @classmethod
    def string_validator(cls, value, header, *args, **kwargs):
        if not cls.required_validator(value, header):
            return False
        if value is None:
            return True

    @classmethod
    def integer_validator(cls, value, header, *args, **kwargs):
        if not cls.required_validator(value, header):
            return False

        if value is None:
            return True

        try:
            int(value)
            return True
        # need to use Exception because of how Graphene catches errors
        except Exception as e:
            return False

    @classmethod
    def float_validator(cls, value, header, *args, **kwargs):
        if not cls.required_validator(value, header):
            return False
        if value is None:
            return True

        return isinstance(value, float)

    @classmethod
    def geolocation_validator(cls, value, header, *args, **kwargs):
        if not cls.required_validator(value, header):
            return False
        if value is None:
            return True

        pattern = re.compile(r"^(\-?\d+\.\d+?,\s*\-?\d+\.\d+?)$")
        return bool(re.match(pattern, value))

    @classmethod
    def date_validator(cls, value, header, *args, **kwargs):
        if cls.integer_validator(value, header):
            return False

        if isinstance(value, datetime):
            return True

        try:
            parser.parse(value)
        # need to use Exception because of how Graphene catches errors
        except Exception as e:
            return False
        return True

    @classmethod
    def phone_validator(cls, value, header, *args, **kwargs):
        if not cls.required_validator(value, header):
            return False
        if value is None:
            return True

        try:
            phonenumbers.parse(value)
            return True
        except (phonenumbers.NumberParseException, TypeError):
            return False

    @classmethod
    def choice_validator(cls, value, header, *args, **kwargs):
        field = cls.ALL_FIELDS.get(header)
        if field is None:
            return False

        if header in ("admin1", "admin2"):
            choices_list = get_admin_areas_as_choices(header[-1])
            choices = [x.get("value") for x in choices_list]
        else:
            choices = [x.get("value") for x in field["choices"]]

        choice_type = cls.ALL_FIELDS[header]["type"]

        if not cls.required_validator(value, header):
            return False
        if value is None:
            return True

        if choice_type == "SELECT_ONE":
            if isinstance(value, str):
                return value.strip() in choices
            else:
                if isinstance(value, float):
                    if value.is_integer():
                        return int(value) in choices
                    return value in choices
                else:
                    if value not in choices:
                        return str(value) in choices

        elif choice_type == "SELECT_MANY":
            if isinstance(value, str):
                selected_choices = value.split(",")
            else:
                selected_choices = value
            for choice in selected_choices:
                if isinstance(choice, str):
                    choice = choice.strip()
                if choice not in choices:
                    return False
            return True

        return False

    @classmethod
    def not_empty_validator(cls, value, *args, **kwargs):
        return not (value is None or value == "")

    @classmethod
    def bool_validator(cls, value, header, *args, **kwargs):
        if isinstance(value, bool):
            return True

        if cls.string_validator(value, header):
            value = value.capitalize()

            if value in ("True", "False"):
                return True

    @classmethod
    def required_validator(cls, value, header, *args, **kwargs):
        is_required = cls.ALL_FIELDS[header]["required"]
        is_not_empty = cls.not_empty_validator(value)

        if is_required:
            return is_not_empty

        return True

    @classmethod
    def image_validator(cls, value, header, *args, **kwargs):
        return True

    @classmethod
    def rows_validator(cls, sheet):
        first_row = sheet[1]
        combined_fields = {
            **cls.CORE_FIELDS[sheet.title.lower()],
            **cls.FLEX_FIELDS[sheet.title.lower()],
        }

        switch_dict = {
            "ID": cls.not_empty_validator,
            "STRING": cls.string_validator,
            "INTEGER": cls.integer_validator,
            "DECIMAL": cls.float_validator,
            "BOOL": cls.bool_validator,
            "DATE": cls.date_validator,
            "DATETIME": cls.date_validator,
            "SELECT_ONE": cls.choice_validator,
            "SELECT_MANY": cls.choice_validator,
            "PHONE_NUMBER": cls.phone_validator,
            "GEOPOINT": cls.geolocation_validator,
            "IMAGE": cls.image_validator,
        }

        # create set of household ids to validate
        # individual is matched with any household
        household_ids = (
            {cell.value for cell in sheet["A"]}
            if sheet.title == "Individuals"
            else None
        )

        invalid_rows = []
        current_household_id = None
        head_of_household_count = 0
        error_appended_flag = False
        for row in sheet.iter_rows(min_row=3):
            # openpyxl keeps iterating on empty rows so need to omit empty rows
            if not any([cell.value for cell in row]):
                continue

            for cell, header in zip(row, first_row):
                current_field = combined_fields.get(header.value)
                if not current_field:
                    continue

                # Validate there is only one head of household per household
                if (
                    header.value == "household_id"
                    and current_household_id != cell.value
                ):
                    current_household_id = cell.value
                    head_of_household_count = 0
                    error_appended_flag = False

                if header.value == "relationship_i_c" and cell.value == "HEAD":
                    head_of_household_count += 1

                if head_of_household_count > 1 and not error_appended_flag:
                    message = (
                        "Sheet: Individuals, There are multiple head of "
                        "households for household with "
                        f"id: {current_household_id}"
                    )
                    invalid_rows.append(
                        {
                            "row_number": cell.row,
                            "header": "relationship_i_c",
                            "message": message,
                        }
                    )
                    error_appended_flag = True

                field_type = current_field["type"]
                fn = switch_dict.get(field_type)

                value = cell.value
                if isinstance(cell.value, float):
                    if cell.value.is_integer():
                        value = int(cell.value)

                if fn(value, header.value) is False:
                    message = (
                        f"Sheet: {sheet.title}, Unexpected value: "
                        f"{value} for type "
                        f"{field_type.replace('_', ' ').lower()} "
                        f"of field {header.value}"
                    )
                    invalid_rows.append(
                        {
                            "row_number": cell.row,
                            "header": header.value,
                            "message": message,
                        }
                    )

                is_not_matched_with_household = (
                    household_ids and header.value == "household_id"
                ) and value not in household_ids

                if is_not_matched_with_household:
                    message = "Individual is not matched with any household"
                    invalid_rows.append(
                        {
                            "row_number": cell.row,
                            "header": header.value,
                            "message": message,
                        }
                    )

        return invalid_rows

    @classmethod
    def validate_file_extension(cls, *args, **kwargs):
        xlsx_file = kwargs.get("file")
        file_suffix = Path(xlsx_file.name).suffix
        if file_suffix != ".xlsx":
            return [
                {
                    "row_number": 1,
                    "header": f"{xlsx_file.name}",
                    "message": "Only .xlsx files are accepted for import.",
                }
            ]

        # Checking only extensions is not enough,
        # loading workbook to check if it is in fact true .xlsx file
        try:
            load_workbook(xlsx_file, data_only=True)
        except BadZipfile:
            return [
                {
                    "row_number": 1,
                    "header": f"{xlsx_file.name}",
                    "message": "Invalid .xlsx file",
                }
            ]

        return []

    @classmethod
    def validate_file_with_template(cls, *args, **kwargs):
        if cls.WB is None:
            xlsx_file = kwargs.get("file")
            wb = openpyxl.load_workbook(xlsx_file, data_only=True)
        else:
            wb = cls.WB

        errors = []
        for name, fields in cls.CORE_FIELDS.items():
            sheet = wb[name.capitalize()]
            first_row = sheet[1]

            all_fields = list(fields.values()) + list(
                cls.FLEX_FIELDS[name].values()
            )

            required_fields = set(
                field["xlsx_field"] for field in all_fields if field["required"]
            )

            column_names = {cell.value for cell in first_row}

            columns_difference = required_fields.difference(column_names)

            if columns_difference:
                errors.extend(
                    [
                        {
                            "row_number": 1,
                            "header": col,
                            "message": f"Missing column name {col}",
                        }
                        for col in columns_difference
                    ]
                )

        return errors

    @classmethod
    def validate_household_rows(cls, *args, **kwargs):
        if cls.WB is None:
            xlsx_file = kwargs.get("file")
            wb = openpyxl.load_workbook(xlsx_file, data_only=True)
        else:
            wb = cls.WB
        household_sheet = wb["Households"]
        return cls.rows_validator(household_sheet)

    @classmethod
    def validate_individuals_rows(cls, *args, **kwargs):
        if cls.WB is None:
            xlsx_file = kwargs.get("file")
            wb = openpyxl.load_workbook(xlsx_file, data_only=True)
        else:
            wb = cls.WB
        household_sheet = wb["Individuals"]
        return cls.rows_validator(household_sheet)
