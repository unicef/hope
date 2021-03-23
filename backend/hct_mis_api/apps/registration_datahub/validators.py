import logging
import re
from collections import Counter, defaultdict
from datetime import datetime
from itertools import zip_longest
from operator import itemgetter
from pathlib import Path
from typing import List, Union
from zipfile import BadZipfile

import openpyxl
import phonenumbers
import pycountry
from dateutil import parser
from django.core import validators as django_core_validators
from openpyxl import load_workbook

from hct_mis_api.apps.core.core_fields_attributes import (
    COLLECTORS_FIELDS,
    CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY,
    TYPE_SELECT_MANY,
    TYPE_SELECT_ONE,
    core_fields_to_separated_dict,
    KOBO_ONLY_INDIVIDUAL_FIELDS,
    KOBO_ONLY_HOUSEHOLD_FIELDS,
)
from hct_mis_api.apps.core.kobo.common import KOBO_FORM_INDIVIDUALS_COLUMN_NAME, get_field_name
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import (
    get_combined_attributes,
    rename_dict_keys,
    serialize_flex_attributes,
    SheetImageLoader,
)
from hct_mis_api.apps.core.validators import BaseValidator
from hct_mis_api.apps.household.models import ROLE_ALTERNATE, ROLE_PRIMARY
from hct_mis_api.apps.registration_datahub.models import KoboImportedSubmission
from hct_mis_api.apps.registration_datahub.tasks.utils import collectors_str_ids_to_list, get_submission_metadata

logger = logging.getLogger(__name__)


class XLSXValidator(BaseValidator):
    @classmethod
    def validate(cls, *args, **kwargs):
        try:
            validate_methods = [getattr(cls, m) for m in dir(cls) if m.startswith("validate_")]

            errors_list = []
            for method in validate_methods:
                errors = method(*args, **kwargs)
                errors_list.extend(errors)

            errors_list.sort(key=itemgetter("header"))

            return errors_list
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def validate_file_extension(cls, *args, **kwargs):
        try:
            xlsx_file = kwargs.get("file")
            file_suffix = Path(xlsx_file.name).suffix
            if file_suffix != ".xlsx":
                return [
                    {
                        "row_number": 1,
                        "header": f"{xlsx_file.name}",
                        "message": "Only .xlsx files are accepted for import",
                    }
                ]

            # Checking only extensions is not enough,
            # loading workbook to check if it is in fact true .xlsx file
            try:
                load_workbook(xlsx_file, data_only=True)
            except BadZipfile:
                return [{"row_number": 1, "header": f"{xlsx_file.name}", "message": "Invalid .xlsx file"}]

            return []
        except Exception as e:
            logger.exception(e)
            raise


class ImportDataValidator(BaseValidator):
    BUSINESS_AREA_SLUG = None
    BUSINESS_AREA_CODE = None
    DOCUMENTS_ISSUING_COUNTRIES_MAPPING = {
        "birth_certificate_issuer_i_c": "birth_certificate_no_i_c",
        "drivers_license_issuer_i_c": "drivers_license_no_i_c",
        "electoral_card_issuer_i_c": "electoral_card_no_i_c",
        "national_id_issuer_i_c": "national_id_no_i_c",
        "national_passport_issuer_i_c": "national_passport_i_c",
        "other_id_issuer_i_c": "other_id_type_i_c",
        # identities
        "scope_id_issuer_i_c": "scope_id_no_i_c",
        "unhcr_id_issuer_i_c": "unhcr_id_no_i_c",
    }

    @classmethod
    def validate(cls, *args, **kwargs):
        try:
            validate_methods = [getattr(cls, m) for m in dir(cls) if m.startswith("validate_")]

            errors_list = []
            for method in validate_methods:
                errors = method(*args, **kwargs)
                errors_list.extend(errors)

            errors_list.sort(key=itemgetter("header"))

            return errors_list
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def documents_validator(cls, documents_numbers_dict, is_xlsx=True, *args, **kwargs):
        try:
            invalid_rows = []
            for key, values in documents_numbers_dict.items():
                if key == "other_id_no_i_c":
                    continue
                issuing_countries = values.get("issuing_countries")
                if not issuing_countries:
                    issuing_countries = [None] * len(values["validation_data"])
                if key == "other_id_type_i_c":
                    for name, value, validation_data, issuing_country in zip(
                        values["names"], values["numbers"], values["validation_data"], issuing_countries
                    ):
                        row_number = validation_data.get("row_number")
                        if not name and value:
                            error = {
                                "header": key,
                                "message": f"Name for other_id_type is required, when number is provided: no: {value}",
                            }
                            if is_xlsx is True:
                                error["row_number"] = row_number
                            invalid_rows.append(error)
                        if name and not value:
                            error = {
                                "header": key,
                                "message": "Number for other_id_no_i_c is required, when name is provided",
                            }
                            if is_xlsx is True:
                                error["row_number"] = row_number
                            invalid_rows.append(error)
                        if (name or value) and not issuing_country:
                            error = {
                                "header": key,
                                "message": "Issuing country for other_id_no_i_c is required, "
                                "when any document data are provided",
                            }
                            if is_xlsx is True:
                                error["row_number"] = row_number
                            invalid_rows.append(error)
                else:
                    for validation_data, value, issuing_country in zip_longest(
                        values["validation_data"], values["numbers"], issuing_countries
                    ):
                        row_number = (
                            validation_data.get("row_number") if isinstance(validation_data, dict) else validation_data
                        )
                        if value and not issuing_country:
                            error = {
                                "header": key,
                                "message": f"Issuing country for {key} is required, when any document data are provided",
                            }
                            if is_xlsx is True:
                                error["row_number"] = row_number
                            invalid_rows.append(error)
                        elif issuing_country and not value:
                            error = {
                                "header": key,
                                "message": f"Number for {key} is required, when issuing country is provided",
                            }
                            if is_xlsx is True:
                                error["row_number"] = row_number
                            invalid_rows.append(error)

            return invalid_rows
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def identity_validator(cls, identities_numbers_dict, is_xlsx=True, *args, **kwargs):
        try:
            invalid_rows = []
            for key, values in identities_numbers_dict.items():
                issuing_countries = values.get("issuing_countries")
                if not issuing_countries:
                    issuing_countries = [None] * len(values["validation_data"])
                for data_dict, value, issuing_country in zip_longest(
                    values["validation_data"], values["numbers"], issuing_countries
                ):
                    row_number = data_dict.get("row_number") if isinstance(data_dict, dict) else data_dict
                    if not value and not issuing_country:
                        continue
                    elif value and not issuing_country:
                        error = {
                            "header": key,
                            "message": f"Issuing country is required: agency: {values['agency']} no: {value}",
                        }
                        if is_xlsx is True:
                            error["row_number"] = row_number
                        invalid_rows.append(error)
                    elif issuing_country and not value:
                        error = {
                            "header": key,
                            "message": f"Number for {key} is required, when issuing country is provided",
                        }
                        if is_xlsx is True:
                            error["row_number"] = row_number
                        invalid_rows.append(error)

            return invalid_rows
        except Exception as e:
            logger.exception(e)
            raise


def lazy_default_get(dict_object, key, lazy_default):
    if key not in dict_object:
        raise
        return lazy_default()
    return dict_object.get(key)


class UploadXLSXValidator(XLSXValidator, ImportDataValidator):
    household_ids = []

    @classmethod
    def get_core_fields(cls):
        print("get_core_fields")
        try:
            return CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def get_flex_fields(cls):
        print("get_flex_fields")
        try:
            return serialize_flex_attributes()
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def get_all_fields(cls):
        print("get_all_fields")
        try:
            return get_combined_attributes()
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def string_validator(cls, value, header, *args, **kwargs):
        try:
            if not cls.required_validator(value, header, *args, **kwargs):
                return True
            if value is None:
                return True
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def integer_validator(cls, value, header, *args, **kwargs):
        try:
            if not cls.required_validator(value, header, *args, **kwargs):
                return False

            if value is None:
                return True

            try:
                int(value)
                return True
            # need to use Exception because of how Graphene catches errors
            except Exception as e:
                return False
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def float_validator(cls, value, header, *args, **kwargs):
        try:
            if not cls.required_validator(value, header, *args, **kwargs):
                return False
            if value is None:
                return True

            return isinstance(value, float)
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def geolocation_validator(cls, value, header, *args, **kwargs):
        try:
            if not cls.required_validator(value, header, *args, **kwargs):
                return False
            if value is None:
                return True

            pattern = re.compile(r"^(-?\d+\.\d+?,\s*-?\d+\.\d+?)$")
            return bool(re.match(pattern, value))
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def date_validator(cls, value, header, *args, **kwargs):
        try:
            if cls.integer_validator(value, header, *args, **kwargs):
                return False

            if isinstance(value, datetime):
                return True

            try:
                parser.parse(value)
            # need to use Exception because of how Graphene catches errors
            except Exception as e:
                return False
            return True
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def phone_validator(cls, value, header, *args, **kwargs):
        try:
            if not cls.required_validator(value, header, *args, **kwargs):
                return False
            if value is None:
                return True

            try:
                phonenumbers.parse(value, region=cls.BUSINESS_AREA_CODE)
                return True
            except (phonenumbers.NumberParseException, TypeError):
                return False
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def choice_validator(cls, value, header, *args, **kwargs):
        try:
            all_fields = lazy_default_get(kwargs, "all_fields", cls.get_all_fields)
            field = all_fields.get(header)
            if field is None:
                return False

            if not cls.required_validator(value, header, *args, **kwargs):
                return False
            if value is None:
                return True

            choices = [x.get("value") for x in field["choices"]]

            choice_type = all_fields[header]["type"]

            if choice_type == TYPE_SELECT_ONE:
                if isinstance(value, str):
                    return value.strip() in choices
                else:
                    if value not in choices:
                        str_value = str(value)
                        return str_value in choices
                return False

            elif choice_type == TYPE_SELECT_MANY:
                if isinstance(value, str):
                    if "," in value:
                        selected_choices = value.split(",")
                    elif ";" in value:
                        selected_choices = value.split(";")
                    else:
                        selected_choices = value.split(" ")
                else:
                    selected_choices = [value]
                for choice in selected_choices:
                    if isinstance(choice, str):
                        choice = choice.strip()
                        if choice not in choices or choice.upper() not in choices:
                            return False
                    if choice not in choices:
                        return False
                return True

            return False
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def not_empty_validator(cls, value, *args, **kwargs):
        try:
            return not (value is None or value == "")
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def bool_validator(cls, value, header, *args, **kwargs):
        try:
            all_fields = lazy_default_get(kwargs, "all_fields", cls.get_all_fields)
            if isinstance(value, bool):
                return True

            if all_fields[header]["required"] is False and (value is None or value == ""):
                return True
            if type(value) is str:
                value = value.capitalize()
                if value in ("True", "False"):
                    return True
            return False
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def required_validator(cls, value, header, *args, **kwargs):
        try:
            all_fields = lazy_default_get(kwargs, "all_fields", cls.get_all_fields)
            is_required = all_fields[header]["required"]
            is_not_empty = cls.not_empty_validator(value)

            if is_required:
                return is_not_empty

            return True
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def image_validator(cls, value, header, cell, *args, **kwargs):
        try:
            if cls.required_validator(value, header, *args, **kwargs):
                return True
            return cls.image_loader.image_in(cell.coordinate)
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def rows_validator(cls, sheet, all_fields):
        try:
            first_row = sheet[1]
            combined_fields = {
                **cls.get_core_fields()[sheet.title.lower()],
                **cls.get_flex_fields()[sheet.title.lower()],
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
                "unhcr_id_no_i_c": {
                    "agency": "UNHCR",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "scope_id_no_i_c": {
                    "agency": "WFP",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
            }
            documents_numbers = {
                "birth_certificate_no_i_c": {
                    "type": "BIRTH_CERTIFICATE",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "drivers_license_no_i_c": {
                    "type": "DRIVERS_LICENSE",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "electoral_card_no_i_c": {
                    "type": "ELECTORAL_CARD",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "national_id_no_i_c": {
                    "type": "NATIONAL_ID",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "national_passport_i_c": {
                    "type": "NATIONAL_PASSPORT",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "other_id_type_i_c": {
                    "type": "OTHER",
                    "names": [],
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "other_id_no_i_c": None,
            }
            for row in sheet.iter_rows(min_row=3):
                # openpyxl keeps iterating on empty rows so need to omit empty rows
                if not any([cell.value for cell in row]):
                    continue
                row_number = 0
                for cell, header in zip(row, first_row):
                    current_field = combined_fields.get(header.value)
                    if not current_field:
                        continue

                    row_number = cell.row

                    value = cell.value
                    if isinstance(value, float) and value.is_integer():
                        value = int(value)

                    if header.value == "household_id":
                        current_household_id = value
                        if sheet.title == "Households":
                            cls.household_ids.append(value)

                    if header.value == "relationship_i_c" and cell.value == "HEAD":
                        head_of_household_count[current_household_id] += 1

                    field_type = current_field["type"]
                    fn = switch_dict.get(field_type)

                    if fn(value, header.value, cell, all_fields=all_fields) is False:
                        message = (
                            f"Sheet: {sheet.title}, Unexpected value: "
                            f"{value} for type "
                            f"{field_type.replace('_', ' ').lower()} "
                            f"of field {header.value}"
                        )
                        invalid_rows.append({"row_number": cell.row, "header": header.value, "message": message})

                    if header.value in documents_numbers:
                        if header.value == "other_id_type_i_c":
                            documents_numbers["other_id_type_i_c"]["names"].append(value)
                        elif header.value == "other_id_no_i_c":
                            documents_numbers["other_id_type_i_c"]["numbers"].append(str(value) if value else None)
                        else:
                            documents_numbers[header.value]["numbers"].append(str(value) if value else None)

                    if header.value in cls.DOCUMENTS_ISSUING_COUNTRIES_MAPPING.keys():
                        document_key = cls.DOCUMENTS_ISSUING_COUNTRIES_MAPPING.get(header.value)
                        documents_dict = documents_numbers
                        if document_key in identities_numbers.keys():
                            documents_dict = identities_numbers
                        documents_dict[document_key]["issuing_countries"].append(value)

                    if header.value in identities_numbers:
                        identities_numbers[header.value]["numbers"].append(str(value) if value else None)

                if current_household_id and current_household_id not in cls.household_ids:
                    message = f"Sheet: Individuals, There is no household with provided id: {current_household_id}"
                    invalid_rows.append({"row_number": row_number, "header": "relationship_i_c", "message": message})

                for header in cls.DOCUMENTS_ISSUING_COUNTRIES_MAPPING.values():
                    documents_or_identity_dict = (
                        identities_numbers if header in identities_numbers.keys() else documents_numbers
                    )
                    documents_or_identity_dict[header]["validation_data"].append({"row_number": row[0].row})

            # validate head of household count
            for household_id, count in head_of_household_count.items():
                if count == 0:
                    message = f"Sheet: Individuals, Household with id: {household_id}, has to have a head of household"
                    invalid_rows.append({"row_number": 0, "header": "relationship_i_c", "message": message})
                elif count > 1:
                    message = f"Sheet: Individuals, There are multiple head of households for household with id: {household_id}"
                    invalid_rows.append({"row_number": 0, "header": "relationship_i_c", "message": message})

            invalid_doc_rows = []
            invalid_ident_rows = []
            if sheet.title == "Individuals":
                invalid_doc_rows = cls.documents_validator(documents_numbers)
                invalid_ident_rows = cls.identity_validator(identities_numbers)

            return [*invalid_rows, *invalid_doc_rows, *invalid_ident_rows]
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def validate_file_extension(cls, *args, **kwargs):
        try:
            xlsx_file = kwargs.get("file")
            file_suffix = Path(xlsx_file.name).suffix
            if file_suffix != ".xlsx":
                return [
                    {
                        "row_number": 1,
                        "header": f"{xlsx_file.name}",
                        "message": "Only .xlsx files are accepted for import",
                    }
                ]

            # Checking only extensions is not enough,
            # loading workbook to check if it is in fact true .xlsx file
            try:
                load_workbook(xlsx_file, data_only=True)
            except BadZipfile:
                return [{"row_number": 1, "header": f"{xlsx_file.name}", "message": "Invalid .xlsx file"}]

            return []
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def validate_file_with_template(cls, *args, **kwargs):
        try:
            xlsx_file = kwargs.get("file")
            wb = openpyxl.load_workbook(xlsx_file, data_only=True)

            errors = []
            core_fields = {**cls.get_core_fields()}
            core_fields["individuals"] = {
                **core_fields["individuals"],
                **COLLECTORS_FIELDS,
            }

            for name, fields in core_fields.items():
                sheet = wb[name.capitalize()]
                first_row = sheet[1]

                all_fields = list(fields.values()) + list(cls.get_flex_fields()[name].values())

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
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def validate_household_rows(cls, *args, **kwargs):
        try:
            xlsx_file = kwargs.get("file")
            wb = openpyxl.load_workbook(xlsx_file, data_only=True)
            household_sheet = wb["Households"]
            cls.image_loader = SheetImageLoader(household_sheet)
            cls.BUSINESS_AREA_SLUG = kwargs.get("business_area_slug")
            business_area_name = BusinessArea.objects.get(slug=cls.BUSINESS_AREA_SLUG).name
            cls.BUSINESS_AREA_CODE = pycountry.countries.get(name=business_area_name).alpha_2
            all_fields = cls.get_all_fields()
            return cls.rows_validator(household_sheet, all_fields)
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def validate_individuals_rows(cls, *args, **kwargs):
        try:
            xlsx_file = kwargs.get("file")
            wb = openpyxl.load_workbook(xlsx_file, data_only=True)
            individuals_sheet = wb["Individuals"]
            cls.image_loader = SheetImageLoader(individuals_sheet)

            cls.BUSINESS_AREA_SLUG = kwargs.get("business_area_slug")
            business_area_name = BusinessArea.objects.get(slug=cls.BUSINESS_AREA_SLUG).name
            cls.BUSINESS_AREA_CODE = pycountry.countries.get(name=business_area_name).alpha_2
            all_fields = cls.get_all_fields()
            return cls.rows_validator(individuals_sheet, all_fields)
        except Exception as e:
            logger.exception(e)
            raise

    @staticmethod
    def collector_column_validator(header, data_dict, household_ids):
        try:
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
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def validate_collectors(cls, *args, **kwargs):
        try:
            xlsx_file = kwargs.get("file")
            wb = openpyxl.load_workbook(xlsx_file, data_only=True)

            errors = []

            individuals_sheet = wb["Individuals"]
            households_sheet = wb["Households"]
            first_row = individuals_sheet[1]

            household_ids = {
                str(int(cell.value)) if isinstance(cell.value, float) and cell.value.is_integer() else str(cell.value)
                for cell in households_sheet["A"][2:]
                if cell.value
            }

            primary_collectors_data = {}
            alternate_collectors_data = {}
            for cell in first_row:
                if cell.value == "primary_collector_id":
                    primary_collectors_data = {c.row: c for c in individuals_sheet[cell.column_letter][2:] if c.value}
                elif cell.value == "alternate_collector_id":
                    alternate_collectors_data = {c.row: c for c in individuals_sheet[cell.column_letter][2:] if c.value}

            errors.extend(
                cls.collector_column_validator("primary_collector_id", primary_collectors_data, household_ids)
            )
            errors.extend(
                cls.collector_column_validator(
                    "alternate_collector_id",
                    alternate_collectors_data,
                    household_ids,
                )
            )

            return errors
        except Exception as e:
            logger.exception(e)
            raise


class KoboProjectImportDataValidator(ImportDataValidator):
    @classmethod
    def get_core_fields(cls):
        try:
            return core_fields_to_separated_dict(append_household_id=False, append_xlsx=False)
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def get_flex_fields(cls):
        try:
            return serialize_flex_attributes()
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def get_all_fields(cls):
        try:
            return get_combined_attributes()
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def get_expected_household_core_fields(cls):
        try:
            return {field["xlsx_field"] for field in cls.get_core_fields()["households"].values() if field["required"]}
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def get_expected_households_flex_fields(cls):
        try:
            return {field["xlsx_field"] for field in cls.get_flex_fields()["households"].values() if field["required"]}
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def get_expected_individuals_core_fields(cls):
        try:
            return {field["xlsx_field"] for field in cls.get_core_fields()["individuals"].values() if field["required"]}
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def get_expected_individuals_flex_fields(cls):
        try:
            return {field["xlsx_field"] for field in cls.get_flex_fields()["individuals"].values() if field["required"]}
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def get_expected_household_fields(cls):
        try:
            return cls.get_expected_household_core_fields().union(cls.get_expected_households_flex_fields())
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def get_expected_individuals_fields(cls):
        try:
            return cls.get_expected_individuals_core_fields().union(cls.get_expected_individuals_flex_fields())
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def standard_type_validator(cls, value: str, field: str, field_type: str):
        try:
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
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def image_validator(cls, value: str, field: str, attachments: List[dict], *args, **kwargs) -> Union[str, None]:
        try:
            allowed_extensions = django_core_validators.get_available_image_extensions()
            file_extension = value.split(".")[-1]

            if file_extension.lower() not in allowed_extensions:
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
        except Exception as e:
            logger.exception(e)
            raise

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
        try:
            message = (
                f"Invalid datetime/date {value} for field {field}, "
                "accepted formats: datetime ISO 8601, date YYYY-MM-DD"
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
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def choice_validator(cls, value: str, field: str, *args, **kwargs) -> Union[str, None]:
        try:
            message = f"Invalid choice {value} for field {field}"

            field = cls.get_all_fields().get(field)
            if not value:
                return message

            custom_validate_choices_method = field.get("custom_validate_choices")
            choices = [x.get("value") for x in field["choices"]]

            choice_type = field["type"]

            if choice_type == TYPE_SELECT_ONE:
                if custom_validate_choices_method is not None:
                    return None if custom_validate_choices_method(value) is True else message

                is_in_choices = value in choices
                if is_in_choices is False:
                    # try uppercase version
                    uppercase_value = value.upper()
                    is_in_choices = uppercase_value in choices
                return None if is_in_choices else message

            elif choice_type == TYPE_SELECT_MANY:
                str_value = str(value)
                if "," in str_value:
                    selected_choices = str_value.split(",")
                elif ";" in str_value:
                    selected_choices = str_value.split(";")
                else:
                    selected_choices = str_value.split(" ")

                if custom_validate_choices_method is not None:
                    return None if custom_validate_choices_method(str_value) is True else message

                for choice in selected_choices:
                    choice = choice.strip()
                    if choice not in choices:
                        # try uppercase version
                        uppercase_value = choice.upper()
                        return None if uppercase_value in choices else message
                return None
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def _get_field_type_error(cls, field: str, value: Union[str, list], attachments: list) -> Union[dict, None]:
        try:
            field_dict = cls.get_all_fields().get(field)
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
        except Exception as e:
            logger.exception(e)
            raise

    @classmethod
    def validate_fields(cls, submissions: list, business_area_name: str):
        try:
            cls.BUSINESS_AREA_CODE = pycountry.countries.get(name=business_area_name).alpha_2
            reduced_submissions = rename_dict_keys(submissions, get_field_name)
            docs_and_identities_to_validate = []
            errors = []
            # have fun debugging this ;_;

            identities_numbers = {
                "unhcr_id_no_i_c": {"agency": "UNHCR", "validation_data": [], "numbers": []},
                "scope_id_no_i_c": {"agency": "WFP", "validation_data": [], "numbers": []},
            }
            documents_numbers = {
                "birth_certificate_no_i_c": {
                    "type": "BIRTH_CERTIFICATE",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "drivers_license_no_i_c": {
                    "type": "DRIVERS_LICENSE",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "electoral_card_no_i_c": {
                    "type": "ELECTORAL_CARD",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "national_id_no_i_c": {
                    "type": "NATIONAL_ID",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "national_passport_i_c": {
                    "type": "NATIONAL_PASSPORT",
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "other_id_type_i_c": {
                    "type": "OTHER",
                    "names": [],
                    "validation_data": [],
                    "numbers": [],
                    "issuing_countries": [],
                },
                "other_id_no_i_c": None,
            }

            for household in reduced_submissions:
                submission_meta_data = get_submission_metadata(household)
                submission_exists = KoboImportedSubmission.objects.filter(**submission_meta_data).exists()
                if submission_exists is True:
                    continue
                head_of_hh_counter = 0
                primary_collector_counter = 0
                alternate_collector_counter = 0
                expected_hh_fields = {*cls.get_expected_household_fields(), *KOBO_ONLY_HOUSEHOLD_FIELDS.keys()}
                attachments = household.get("_attachments", [])
                for hh_field, hh_value in household.items():
                    expected_hh_fields.discard(hh_field)
                    if hh_field == KOBO_FORM_INDIVIDUALS_COLUMN_NAME:
                        for individual in hh_value:
                            expected_i_fields = {
                                *cls.get_expected_individuals_fields(),
                                *KOBO_ONLY_INDIVIDUAL_FIELDS,
                            }
                            current_individual_docs_and_identities = defaultdict(dict)
                            for i_field, i_value in individual.items():
                                if i_field in documents_numbers:
                                    if i_field == "other_id_type_i_c":
                                        documents_numbers["other_id_type_i_c"]["names"].append(i_value)
                                    elif i_field == "other_id_no_i_c":
                                        documents_numbers["other_id_type_i_c"]["validation_data"].append(
                                            {"value": i_value}
                                        )
                                        documents_numbers["other_id_type_i_c"]["numbers"].append(i_value)
                                    else:
                                        documents_numbers[i_field]["validation_data"].append({"value": i_value})
                                        documents_numbers[i_field]["numbers"].append(i_value)
                                if i_field in cls.DOCUMENTS_ISSUING_COUNTRIES_MAPPING.keys():
                                    document_key = cls.DOCUMENTS_ISSUING_COUNTRIES_MAPPING.get(i_field)
                                    documents_dict = documents_numbers
                                    if document_key in identities_numbers.keys():
                                        documents_dict = identities_numbers
                                    documents_dict[document_key]["issuing_countries"].append(i_value)

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
                                {
                                    "header": "relationship_i_c",
                                    "message": "Household has to have a " "head of household",
                                }
                            )
                        if head_of_hh_counter > 1:
                            errors.append(
                                {
                                    "header": "relationship_i_c",
                                    "message": "Only one person can " "be a head of household",
                                }
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
        except Exception as e:
            logger.exception(e)
            raise
