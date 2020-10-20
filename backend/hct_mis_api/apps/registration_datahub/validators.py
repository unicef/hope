import re
from collections import defaultdict, Counter
from datetime import datetime
from operator import itemgetter
from pathlib import Path
from typing import List, Union
from zipfile import BadZipfile

import openpyxl
import phonenumbers
import pycountry
from dateutil import parser
from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader

from core.core_fields_attributes import (
    CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY,
    COLLECTORS_FIELDS,
    KOBO_COLLECTOR_FIELD,
)
from core.kobo.common import KOBO_FORM_INDIVIDUALS_COLUMN_NAME, get_field_name
from core.models import BusinessArea
from core.utils import (
    serialize_flex_attributes,
    get_combined_attributes,
    rename_dict_keys,
)
from core.validators import BaseValidator
from household.models import IndividualIdentity, ROLE_PRIMARY, ROLE_ALTERNATE
from registration_datahub.models import ImportedIndividualIdentity
from registration_datahub.tasks.utils import collectors_str_ids_to_list


class XLSXValidator(BaseValidator):
    @classmethod
    def validate(cls, *args, **kwargs):
        validate_methods = [getattr(cls, m) for m in dir(cls) if m.startswith("validate_")]

        errors_list = []
        for method in validate_methods:
            errors = method(*args, **kwargs)
            errors_list.extend(errors)

        errors_list.sort(key=itemgetter("header"))

        return errors_list

    @classmethod
    def validate_file_extension(cls, *args, **kwargs):
        xlsx_file = kwargs.get("file")
        file_suffix = Path(xlsx_file.name).suffix
        if file_suffix != ".xlsx":
            return [
                {"row_number": 1, "header": f"{xlsx_file.name}", "message": "Only .xlsx files are accepted for import"}
            ]

        # Checking only extensions is not enough,
        # loading workbook to check if it is in fact true .xlsx file
        try:
            wb = load_workbook(xlsx_file, data_only=True)
        except BadZipfile:
            return [{"row_number": 1, "header": f"{xlsx_file.name}", "message": "Invalid .xlsx file"}]

        return []


class ImportDataValidator(BaseValidator):
    BUSINESS_AREA_SLUG = None
    BUSINESS_AREA_CODE = None

    @classmethod
    def validate(cls, *args, **kwargs):
        validate_methods = [getattr(cls, m) for m in dir(cls) if m.startswith("validate_")]

        errors_list = []
        for method in validate_methods:
            errors = method(*args, **kwargs)
            errors_list.extend(errors)

        errors_list.sort(key=itemgetter("header"))

        return errors_list

    @classmethod
    def documents_validator(cls, documents_numbers_dict, is_xlsx=True, *args, **kwargs):
        invalid_rows = []
        for key, values in documents_numbers_dict.items():
            if key == "other_id_type_i_c":
                for name, validation_data in zip(values["names"], values["validation_data"]):
                    value = validation_data["value"]
                    row_number = validation_data.get("row_number")
                    if not name and value:
                        error = {
                            "header": key,
                            "message": f"Name for other_id_type is "
                            f"required, when number is "
                            f"provided: no: {value}",
                        }
                        if is_xlsx is True:
                            error["row_number"] = row_number
                        invalid_rows.append(error)
                    if name and not value:
                        error = {
                            "header": key,
                            "message": "Number for other_id_no_i_c is " "required, when name is provided",
                        }
                        if is_xlsx is True:
                            error["row_number"] = row_number
                        invalid_rows.append(error)

        return invalid_rows

    @classmethod
    def identity_validator(cls, identities_numbers_dict, is_xlsx=True, *args, **kwargs):
        invalid_rows = []
        message = "Duplicated identity document"
        for key, values in identities_numbers_dict.items():
            seen = {}
            dupes = []
            for data_dict in values["validation_data"]:
                value = data_dict["value"]
                row_number = data_dict.get("row_number")

                if not value:
                    continue

                if value not in seen:
                    seen[value] = 1
                else:
                    if seen[value] == 1:
                        dupes.append(row_number)
                    seen[value] += 1

                for number in dupes:
                    error = {
                        "header": key,
                        "message": f"{message}: " f"{values['agency']} no: {value}",
                    }
                    if is_xlsx is True:
                        error["row_number"] = number
                    invalid_rows.append(error)

            imp_ident_obj = []
            ident_obj = []
            if imp_ident_obj:
                imp_ident_obj = ImportedIndividualIdentity.objects.filter(
                    agency=values["agency"], document_number__in=values["numbers"],
                )

            if ident_obj:
                ident_obj = IndividualIdentity.objects.filter(
                    agency=values["agency"], document_number__in=values["numbers"],
                )

            for obj in imp_ident_obj:
                error = {
                    "header": key,
                    "message": f"{message}: " f"{values['agency']} no: {obj.document_number}" f" in RDH Database",
                }
                if is_xlsx is True:
                    error["row_number"] = 0
                invalid_rows.append(error)

            for obj in ident_obj:
                error = {
                    "header": key,
                    "message": f"{message}: " f"{values['agency']} no: {obj.document_number}" f" in HCT Database",
                }
                if is_xlsx is True:
                    error["row_number"] = 0
                invalid_rows.append(error)

        return invalid_rows


class UploadXLSXValidator(XLSXValidator, ImportDataValidator):
    WB = None
    CORE_FIELDS = CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY
    FLEX_FIELDS = serialize_flex_attributes()
    ALL_FIELDS = get_combined_attributes()

    @classmethod
    def string_validator(cls, value, header, *args, **kwargs):
        if not cls.required_validator(value, header):
            return True
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

        pattern = re.compile(r"^(-?\d+\.\d+?,\s*-?\d+\.\d+?)$")
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
            phonenumbers.parse(value, region=cls.BUSINESS_AREA_CODE)
            return True
        except (phonenumbers.NumberParseException, TypeError):
            return False

    @classmethod
    def choice_validator(cls, value, header, *args, **kwargs):
        field = cls.ALL_FIELDS.get(header)
        if field is None:
            return False

        if not cls.required_validator(value, header):
            return False
        if value is None:
            return True

        choices = [x.get("value") for x in field["choices"]]

        choice_type = cls.ALL_FIELDS[header]["type"]

        if choice_type == "SELECT_ONE":
            if isinstance(value, str):
                return value.strip() in choices
            else:
                if value not in choices:
                    str_value = str(value)
                    return str_value in choices
            return False

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
    def image_validator(cls, value, header, cell, *args, **kwargs):
        if cls.required_validator(value, header):
            return True
        return cls.image_loader.image_in(cell.coordinate)

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

        invalid_rows = []
        current_household_id = None
        head_of_household_count = defaultdict(int)

        identities_numbers = {
            "unhcr_id_no": {"agency": "UNHCR", "validation_data": [], "numbers": []},
            "scope_id_no": {"agency": "WFP", "validation_data": [], "numbers": []},
        }
        documents_numbers = {
            "birth_certificate_no_i_c": {"type": "BIRTH_CERTIFICATE", "validation_data": [], "numbers": []},
            "drivers_license_no_i_c": {"type": "DRIVERS_LICENSE", "validation_data": [], "numbers": []},
            "electoral_card_no_i_c": {"type": "ELECTORAL_CARD", "validation_data": [], "numbers": []},
            "national_id_no_ic": {"type": "NATIONAL_ID", "validation_data": [], "numbers": []},
            "national_passport_i_c": {"type": "NATIONAL_PASSPORT", "validation_data": [], "numbers": []},
            "other_id_type_i_c": {"type": "OTHER", "names": [], "validation_data": [], "numbers": []},
            "other_id_no_i_c": None,
        }
        for row in sheet.iter_rows(min_row=3):
            # openpyxl keeps iterating on empty rows so need to omit empty rows
            if not any([cell.value for cell in row]):
                continue

            for cell, header in zip(row, first_row):
                current_field = combined_fields.get(header.value)
                if not current_field:
                    continue

                if header.value == "household_id":
                    current_household_id = cell.value

                if header.value == "relationship_i_c" and cell.value == "HEAD":
                    head_of_household_count[current_household_id] += 1

                field_type = current_field["type"]
                fn = switch_dict.get(field_type)

                value = cell.value
                if isinstance(value, float) and value.is_integer():
                    value = int(value)

                if fn(value, header.value, cell) is False:
                    message = (
                        f"Sheet: {sheet.title}, Unexpected value: "
                        f"{value} for type "
                        f"{field_type.replace('_', ' ').lower()} "
                        f"of field {header.value}"
                    )
                    invalid_rows.append(
                        {"row_number": cell.row, "header": header.value, "message": message}
                    )

                if header.value in documents_numbers:
                    if header.value == "other_id_type_i_c":
                        documents_numbers["other_id_type_i_c"]["names"].append(value)
                    elif header.value == "other_id_no_i_c":
                        documents_numbers["other_id_type_i_c"]["validation_data"].append(
                            {"row_number": cell.row, "value": value}
                        )
                        documents_numbers["other_id_type_i_c"]["numbers"].append(str(value))
                    else:
                        documents_numbers[header.value]["validation_data"].append(
                            {"row_number": cell.row, "value": value}
                        )
                        documents_numbers[header.value]["numbers"].append(str(value))

                if header.value in identities_numbers:
                    identities_numbers[header.value]["numbers"].append(value)
                    identities_numbers[header.value]["validation_data"].append({"row_number": cell.row, "value": value})

        # validate head of household count
        for household_id, count in head_of_household_count.items():
            if count == 0:
                message = f"Sheet: Individuals, Household with id: {household_id}, " "has to have a head of household"
                invalid_rows.append(
                    {"row_number": 0, "header": "relationship_i_c", "message": message}
                )
            elif count > 1:
                message = (
                    "Sheet: Individuals, There are multiple head of "
                    f"households for household with id: {household_id}"
                )
                invalid_rows.append(
                    {"row_number": 0, "header": "relationship_i_c", "message": message}
                )

        invalid_doc_rows = []
        invalid_ident_rows = []
        if sheet.title == "Individuals":
            invalid_doc_rows = cls.documents_validator(documents_numbers)
            invalid_ident_rows = cls.identity_validator(identities_numbers)

        return [*invalid_rows, *invalid_doc_rows, *invalid_ident_rows]

    @classmethod
    def validate_file_extension(cls, *args, **kwargs):
        xlsx_file = kwargs.get("file")
        file_suffix = Path(xlsx_file.name).suffix
        if file_suffix != ".xlsx":
            return [
                {"row_number": 1, "header": f"{xlsx_file.name}", "message": "Only .xlsx files are accepted for import"}
            ]

        # Checking only extensions is not enough,
        # loading workbook to check if it is in fact true .xlsx file
        try:
            wb = load_workbook(xlsx_file, data_only=True)
        except BadZipfile:
            return [{"row_number": 1, "header": f"{xlsx_file.name}", "message": "Invalid .xlsx file"}]

        return []

    @classmethod
    def validate_file_with_template(cls, *args, **kwargs):
        xlsx_file = kwargs.get("file")
        wb = openpyxl.load_workbook(xlsx_file, data_only=True)

        errors = []
        core_fields = {**cls.CORE_FIELDS}
        core_fields["individuals"] = {
            **core_fields["individuals"],
            **COLLECTORS_FIELDS,
        }

        for name, fields in core_fields.items():
            sheet = wb[name.capitalize()]
            first_row = sheet[1]

            all_fields = list(fields.values()) + list(cls.FLEX_FIELDS[name].values())

            required_fields = set(field["xlsx_field"] for field in all_fields if field["required"])

            column_names = {cell.value for cell in first_row}

            columns_difference = required_fields.difference(column_names)

            if columns_difference:
                errors.extend(
                    [
                        {"row_number": 1, "header": col, "message": f"Missing column name {col}"}
                        for col in columns_difference
                    ]
                )

        return errors

    @classmethod
    def validate_household_rows(cls, *args, **kwargs):
        xlsx_file = kwargs.get("file")
        wb = openpyxl.load_workbook(xlsx_file, data_only=True)
        household_sheet = wb["Households"]
        cls.image_loader = SheetImageLoader(household_sheet)
        cls.BUSINESS_AREA_SLUG = kwargs.get("business_area_slug")
        business_area_name = BusinessArea.objects.get(slug=cls.BUSINESS_AREA_SLUG).name
        cls.BUSINESS_AREA_CODE = pycountry.countries.get(name=business_area_name).alpha_2

        return cls.rows_validator(household_sheet)

    @classmethod
    def validate_individuals_rows(cls, *args, **kwargs):
        xlsx_file = kwargs.get("file")
        wb = openpyxl.load_workbook(xlsx_file, data_only=True)
        individuals_sheet = wb["Individuals"]
        cls.image_loader = SheetImageLoader(individuals_sheet)

        cls.BUSINESS_AREA_SLUG = kwargs.get("business_area_slug")
        business_area_name = BusinessArea.objects.get(slug=cls.BUSINESS_AREA_SLUG).name
        cls.BUSINESS_AREA_CODE = pycountry.countries.get(name=business_area_name).alpha_2

        return cls.rows_validator(individuals_sheet)

    @staticmethod
    def collector_column_validator(header, data_dict, household_ids):
        is_primary_collector = header == "primary_collector_id"
        errors = []
        collectors_ids = []
        for row, cell in data_dict.items():
            if not cell.value:
                continue
            list_of_ids = set(collectors_str_ids_to_list(cell.value))
            contains_correct_ids = list_of_ids.issubset(household_ids)
            if not contains_correct_ids:
                errors.append(
                    {
                        "row_number": row,
                        "header": header,
                        "message": "One or more ids are not attached " "to any household in the file.",
                    }
                )
            collectors_ids.extend(list_of_ids)

        collectors_ids_set = set(collectors_ids)

        if is_primary_collector:
            household_ids_without_collectors = household_ids.difference(collectors_ids_set)
            errors.extend(
                {
                    "row_number": 1,
                    "header": header,
                    "message": f"Household with id: {hh_id} " f"does not have primary collector",
                }
                for hh_id in household_ids_without_collectors
            )

        ids_counter = Counter(collectors_ids)
        erroneous_collectors_ids = [item for item, count in ids_counter.items() if count > 1]
        message = "Household can contain only one " "primary and one alternate collector"
        errors.extend(
            {"row_number": 1, "header": header, "message": f"{message}, erroneous id: {hh_id}"}
            for hh_id in erroneous_collectors_ids
        )
        return errors

    @classmethod
    def validate_collectors(cls, *args, **kwargs):
        xlsx_file = kwargs.get("file")
        wb = openpyxl.load_workbook(xlsx_file, data_only=True)

        errors = []

        individuals_sheet = wb["Individuals"]
        households_sheet = wb["Households"]
        first_row = individuals_sheet[1]
        household_ids = {str(cell.value) for cell in households_sheet["A"][2:] if cell.value}

        primary_collectors_data = {}
        alternate_collectors_data = {}
        for cell in first_row:
            if cell.value == "primary_collector_id":
                primary_collectors_data = {c.row: c for c in individuals_sheet[cell.column_letter][2:] if c.value}
            elif cell.value == "alternate_collector_id":
                alternate_collectors_data = {c.row: c for c in individuals_sheet[cell.column_letter][2:] if c.value}

        errors.extend(cls.collector_column_validator("primary_collector_id", primary_collectors_data, household_ids))
        errors.extend(
            cls.collector_column_validator("alternate_collector_id", alternate_collectors_data, household_ids,)
        )

        return errors


class KoboProjectImportDataValidator(ImportDataValidator):
    CORE_FIELDS: dict = CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY
    FLEX_FIELDS: dict = serialize_flex_attributes()
    ALL_FIELDS = get_combined_attributes()

    EXPECTED_HOUSEHOLDS_CORE_FIELDS = {
        field["xlsx_field"] for field in CORE_FIELDS["households"].values() if field["required"]
    }
    EXPECTED_HOUSEHOLDS_FLEX_FIELDS = {
        field["xlsx_field"] for field in FLEX_FIELDS["households"].values() if field["required"]
    }

    EXPECTED_INDIVIDUALS_CORE_FIELDS = {
        field["xlsx_field"] for field in CORE_FIELDS["individuals"].values() if field["required"]
    }
    EXPECTED_INDIVIDUALS_FLEX_FIELDS = {
        field["xlsx_field"] for field in FLEX_FIELDS["individuals"].values() if field["required"]
    }

    EXPECTED_HOUSEHOLD_FIELDS = EXPECTED_HOUSEHOLDS_CORE_FIELDS.union(EXPECTED_HOUSEHOLDS_FLEX_FIELDS)
    EXPECTED_INDIVIDUALS_FIELDS = EXPECTED_INDIVIDUALS_CORE_FIELDS.union(EXPECTED_INDIVIDUALS_FLEX_FIELDS)

    @classmethod
    def standard_type_validator(cls, value: str, field: str, field_type: str):
        value_type_name = type(value).__name__

        if field_type == "INTEGER":
            try:
                int(value)
                return
            except Exception as e:
                return f"Invalid value {value} of type {value_type_name} for " f"field {field} of type int"
        elif field_type == "STRING":
            # everything from Kobo is string so cannot really validate it
            # only check phone number
            if field.startswith("phone_no"):
                try:
                    phonenumbers.parse(value, region=cls.BUSINESS_AREA_CODE)
                except (phonenumbers.NumberParseException, TypeError):
                    return f"Invalid phone number {value} for field {field}"
            return

        elif field_type == "BOOL":
            # Important! if value == 0 or 1 it's also evaluated to True
            # checking for int values even tho Kobo returns everything as str
            # to no not break import if they start returning integers
            if value in ("True", "False", True, False, "0", "1"):
                return None
            return f"Invalid value {value} of type {value_type_name} for " f"field {field} of type bool"

    @classmethod
    def image_validator(cls, value: str, field: str, attachments: List[dict], *args, **kwargs) -> Union[str, None]:
        allowed_extensions = (
            "bmp",
            "dib",
            "gif",
            "tif",
            "tiff",
            "jfif",
            "jpe",
            "jpg",
            "jpeg",
            "pbm",
            "pgm",
            "ppm",
            "pnm",
            "png",
            "apng",
            "blp",
            "bufr",
            "cur",
            "pcx",
            "dcx",
            "dds",
            "ps",
            "eps",
            "fit",
            "fits",
            "fli",
            "flc",
            "fpx",
            "ftc",
            "ftu",
            "gbr",
            "grib",
            "h5",
            "hdf",
            "icns",
            "ico",
            "im",
            "iim",
            "jp2",
            "j2k",
            "jpc",
            "jpf",
            "jpx",
            "j2c",
            "mic",
            "mpg",
            "mpeg",
            "mpo",
            "msp",
            "palm",
            "pcd",
            "pdf",
            "pxr",
            "psd",
            "bw",
            "rgb",
            "rgba",
            "sgi",
            "ras",
            "tga",
            "icb",
            "vda",
            "vst",
            "webp",
            "wmf",
            "emf",
            "xbm",
            "xpm",
        )
        file_extension = value.split(".")[-1]

        if file_extension not in allowed_extensions:
            message = f"Specified image {value} for " f"field {field} is not a valid image file"
            return message

        message = f"Specified image {value} for field {field} is not in attachments"

        is_correct_attachment = False

        for attachment in attachments:
            if get_field_name(attachment["filename"]) == value:
                is_correct_attachment = True
                break

        is_valid_image = isinstance(value, str) and is_correct_attachment

        return None if is_valid_image else message

    @classmethod
    def geopoint_validator(cls, value: str, field: str, *args, **kwargs) -> Union[str, None]:
        message = f"Invalid geopoint {value} for field {field}"

        if not value or not isinstance(value, str):
            return message

        geopoint_to_list = value.split(" ")
        geopoint = " ".join(geopoint_to_list[:2])

        pattern = re.compile(r"^(-?\d+\.\d+? \s*-?\d+\.\d+?)$")
        is_valid_geopoint = bool(re.match(pattern, geopoint))

        return None if is_valid_geopoint else message

    @classmethod
    def date_validator(cls, value: str, field: str, *args, **kwargs) -> Union[str, None]:
        message = (
            f"Invalid datetime/date {value} for field {field}, " "accepted formats: datetime ISO 8601, date YYYY-MM-DD"
        )

        if not value:
            return message

        pattern_iso = re.compile(
            r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-"
            r"(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):"
            r"([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):"
            r"[0-5][0-9])?$"
        )

        matched = re.match(pattern_iso, value)

        if matched is None:
            pattern_date = re.compile(r"([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))")

            matched = re.match(pattern_date, value)

        return None if matched else message

    @classmethod
    def choice_validator(cls, value: str, field: str, *args, **kwargs) -> Union[str, None]:
        message = f"Invalid choice {value} for field {field}"

        field = cls.ALL_FIELDS.get(field)
        if not value:
            return message

        custom_validate_choices_method = field.get("custom_validate_choices")
        choices = [x.get("value") for x in field["choices"]]

        choice_type = field["type"]

        if choice_type == "SELECT_ONE":
            if custom_validate_choices_method is not None:
                return None if custom_validate_choices_method(value) is True else message

            is_in_choices = value in choices
            if is_in_choices is False:
                # try uppercase version
                uppercase_value = value.upper()
                is_in_choices = uppercase_value in choices
            return None if is_in_choices else message

        elif choice_type == "SELECT_MANY":
            selected_choices = value.split(",")

            if custom_validate_choices_method is not None:
                return None if custom_validate_choices_method(value) is True else message

            for choice in selected_choices:
                choice = choice.strip()
                if choice not in choices:
                    # try uppercase version
                    uppercase_value = value.upper()
                    return None if uppercase_value in choices else message
            return None

    @classmethod
    def _get_field_type_error(cls, field: str, value: Union[str, list], attachments: list) -> Union[dict, None]:
        field_dict = cls.ALL_FIELDS.get(field)
        if field_dict is None:
            return

        complex_types = {
            "GEOPOINT": cls.geopoint_validator,
            "IMAGE": cls.image_validator,
            "DATE": cls.date_validator,
            "SELECT_ONE": cls.choice_validator,
            "SELECT_MANY": cls.choice_validator,
        }
        field_type = field_dict["type"]
        complex_type_fn = complex_types.get(field_type)

        if complex_type_fn:
            message = complex_type_fn(field=field, value=value, attachments=attachments)
            if message is not None:
                return {
                    "header": field,
                    "message": message,
                }
        else:
            message = cls.standard_type_validator(value, field, field_type)
            if message:
                return {
                    "header": field,
                    "message": message,
                }

    @classmethod
    def _docs_and_identities_validator(cls, data_to_validate):
        pass

    @classmethod
    def validate_fields(cls, submissions: list, business_area_name: str):
        cls.BUSINESS_AREA_CODE = pycountry.countries.get(name=business_area_name).alpha_2
        reduced_submissions = rename_dict_keys(submissions, get_field_name)
        docs_and_identities_to_validate = []
        errors = []
        # have fun debugging this ;_;

        identities_numbers = {
            "unhcr_id_no": {"agency": "UNHCR", "validation_data": [], "numbers": []},
            "scope_id_no": {"agency": "WFP", "validation_data": [], "numbers": []},
        }
        documents_numbers = {
            "birth_certificate_no_i_c": {"type": "BIRTH_CERTIFICATE", "validation_data": [], "numbers": []},
            "drivers_license_no_i_c": {"type": "DRIVERS_LICENSE", "validation_data": [], "numbers": []},
            "electoral_card_no_i_c": {"type": "ELECTORAL_CARD", "validation_data": [], "numbers": []},
            "national_id_no_ic": {"type": "NATIONAL_ID", "validation_data": [], "numbers": []},
            "national_passport_i_c": {"type": "NATIONAL_PASSPORT", "validation_data": [], "numbers": []},
            "other_id_type_i_c": {"type": "OTHER", "names": [], "validation_data": [], "numbers": []},
            "other_id_no_i_c": None,
        }

        for household in reduced_submissions:
            head_of_hh_counter = 0
            primary_collector_counter = 0
            alternate_collector_counter = 0
            expected_hh_fields = cls.EXPECTED_HOUSEHOLD_FIELDS.copy()
            attachments = household.get("_attachments", [])
            for hh_field, hh_value in household.items():
                expected_hh_fields.discard(hh_field)
                if hh_field == KOBO_FORM_INDIVIDUALS_COLUMN_NAME:
                    for individual in hh_value:
                        expected_i_fields = {
                            *cls.EXPECTED_INDIVIDUALS_FIELDS,
                            *KOBO_COLLECTOR_FIELD.keys(),
                        }
                        current_individual_docs_and_identities = defaultdict(dict)
                        for i_field, i_value in individual.items():
                            if i_field in documents_numbers:
                                if i_field == "other_id_type_i_c":
                                    documents_numbers["other_id_type_i_c"]["names"].append(i_value)
                                elif i_field == "other_id_no_i_c":
                                    documents_numbers["other_id_type_i_c"]["validation_data"].append({"value": i_value})
                                    documents_numbers["other_id_type_i_c"]["numbers"].append(i_value)
                                else:
                                    documents_numbers[i_field]["validation_data"].append({"value": i_value})
                                    documents_numbers[i_field]["numbers"].append(i_value)

                            if i_field in identities_numbers:
                                identities_numbers[i_field]["numbers"].append(i_value)
                                identities_numbers[i_field]["validation_data"].append({"value": i_value})

                            if i_field == "relationship_i_c" and i_value.upper() == "HEAD":
                                head_of_hh_counter += 1
                            if i_field == "role_i_c":
                                role = i_value.upper()
                                if role == ROLE_PRIMARY:
                                    primary_collector_counter += 1
                                elif role == ROLE_ALTERNATE:
                                    alternate_collector_counter += 1

                            expected_i_fields.discard(i_field)
                            error = cls._get_field_type_error(i_field, i_value, attachments)
                            if error:
                                errors.append(error)

                        docs_and_identities_to_validate.append(current_individual_docs_and_identities)

                        i_expected_field_errors = [
                            {"header": field, "message": "Missing individual " f"required field {field}"}
                            for field in expected_i_fields
                        ]
                        errors.extend(i_expected_field_errors)

                    if head_of_hh_counter == 0:
                        errors.append(
                            {"header": "relationship_i_c", "message": "Household has to have a " "head of household"}
                        )
                    if head_of_hh_counter > 1:
                        errors.append(
                            {"header": "relationship_i_c", "message": "Only one person can " "be a head of household"}
                        )
                    if primary_collector_counter == 0:
                        errors.append(
                            {"header": "role_i_c", "message": "Household must have a " "primary collector"}
                        )
                    if primary_collector_counter > 1:
                        errors.append(
                            {"header": "role_i_c", "message": "Only one person can " "be a primary collector"}
                        )
                    if alternate_collector_counter > 1:
                        errors.append(
                            {"header": "role_i_c", "message": "Only one person can " "be a alternate collector"}
                        )
                else:
                    error = cls._get_field_type_error(hh_field, hh_value, attachments)
                    if error:
                        errors.append(error)
            hh_expected_field_errors = [
                {"header": field, "message": f"Missing household required field {field}"}
                for field in expected_hh_fields
            ]
            errors.extend(hh_expected_field_errors)

        document_errors = cls.documents_validator(documents_numbers, is_xlsx=False)
        identities_errors = cls.identity_validator(identities_numbers, is_xlsx=False)

        return [*errors, *document_errors, *identities_errors]
