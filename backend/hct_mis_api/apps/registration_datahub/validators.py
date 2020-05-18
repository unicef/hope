import re
from datetime import datetime
from pathlib import Path
from zipfile import BadZipfile

import openpyxl
import phonenumbers
from dateutil import parser
from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader

from core.core_fields_attributes import CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY
from core.utils import (
    serialize_flex_attributes,
    get_combined_attributes,
    get_admin_areas_as_choices,
)
from core.validators import BaseValidator
from household.models import Document, DocumentType, IndividualIdentity
from registration_datahub.models import (
    ImportedDocument,
    ImportedDocumentType,
    ImportedIndividualIdentity,
)


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

        if not cls.required_validator(value, header):
            return False
        if value is None:
            return True

        if header in ("admin1", "admin2"):
            choices_list = get_admin_areas_as_choices(header[-1])
            choices = [x.get("value") for x in choices_list]
        else:
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
    def documents_validator(cls, documents_numbers_dict, *args, **kwargs):
        invalid_rows = []
        message = f"Duplicated document"
        for key, values in documents_numbers_dict.items():

            if key == "other_id_no_i_c":
                continue

            document_name = values["type"].replace("_", " ").lower()

            seen = {}
            dupes = []
            for data_dict in values["validation_data"]:
                value = data_dict["value"]
                row_number = data_dict["row_number"]

                if not value:
                    continue

                if value not in seen:
                    seen[value] = 1
                else:
                    if seen[value] == 1:
                        dupes.append(row_number)
                    seen[value] += 1

                for number in dupes:
                    invalid_rows.append(
                        {
                            "row_number": number,
                            "header": key,
                            "message": f"{message}: "
                            f"{document_name} no: {value} in file",
                        }
                    )

            if key == "other_id_type_i_c":
                imp_doc_type_obj = ImportedDocumentType.objects.filter(
                    label=values["name"],
                    country=kwargs.get("business_area_slug"),
                    type=values["type"],
                )
                doc_type_obj = DocumentType.objects.filter(
                    label=values["name"],
                    country=kwargs.get("business_area_slug"),
                    type=values["type"],
                )
            else:
                imp_doc_type_obj = ImportedDocumentType.objects.filter(
                    country=kwargs.get("business_area_slug"),
                    type=values["type"],
                )
                doc_type_obj = DocumentType.objects.filter(
                    country=kwargs.get("business_area_slug"),
                    type=values["type"],
                )

            imp_doc_obj = []
            doc_obj = []
            if imp_doc_type_obj:
                imp_doc_obj = ImportedDocument.objects.filter(
                    type=imp_doc_type_obj, document_number__in=values["numbers"]
                )

            if doc_type_obj:
                doc_obj = Document.objects.filter(
                    type=doc_type_obj, document_number__in=values["numbers"]
                )

            for obj in imp_doc_obj:
                invalid_rows.append(
                    {
                        "row_number": 0,
                        "header": key,
                        "message": f"{message}: "
                        f"{document_name} no: {obj.document_number}"
                        f" in RDH Database",
                    }
                )

            for obj in doc_obj:
                invalid_rows.append(
                    {
                        "row_number": 0,
                        "header": key,
                        "message": f"{message}: {document_name} "
                        f"no: {obj.document_number} in HCT Database",
                    }
                )

        return invalid_rows

    @classmethod
    def identity_validator(cls, identities_numbers_dict, *args, **kwargs):
        invalid_rows = []
        message = "Duplicated identity document"
        for key, values in identities_numbers_dict.items():
            seen = {}
            dupes = []
            for data_dict in values["validation_data"]:
                value = data_dict["value"]
                row_number = data_dict["row_number"]

                if not value:
                    continue

                if value not in seen:
                    seen[value] = 1
                else:
                    if seen[value] == 1:
                        dupes.append(row_number)
                    seen[value] += 1

                for number in dupes:
                    invalid_rows.append(
                        {
                            "row_number": number,
                            "header": key,
                            "message": f"{message}: "
                            f"{values['agency']} no: {value} in file",
                        }
                    )

            imp_ident_obj = []
            ident_obj = []
            if imp_ident_obj:
                imp_ident_obj = ImportedIndividualIdentity.objects.filter(
                    agency=values["agency"],
                    document_number__in=values["numbers"],
                )

            if ident_obj:
                ident_obj = IndividualIdentity.objects.filter(
                    agency=values["agency"],
                    document_number__in=values["numbers"],
                )

            for obj in imp_ident_obj:
                invalid_rows.append(
                    {
                        "row_number": 0,
                        "header": key,
                        "message": f"{message}: "
                        f"{values['agency']} no: {obj.document_number}"
                        f" in RDH Database",
                    }
                )

            for obj in ident_obj:
                invalid_rows.append(
                    {
                        "row_number": 0,
                        "header": key,
                        "message": f"{message}: "
                        f"{values['agency']} no: {obj.document_number}"
                        f" in HCT Database",
                    }
                )

        return invalid_rows

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

        identities_numbers = {
            "unhcr_id_no": {
                "agency": "UNHCR",
                "validation_data": [],
                "numbers": [],
            },
            "scope_id_no": {
                "agency": "WFP",
                "validation_data": [],
                "numbers": [],
            },
        }
        documents_numbers = {
            "birth_certificate_no_i_c": {
                "type": "BIRTH_CERTIFICATE",
                "validation_data": [],
                "numbers": [],
            },
            "drivers_license_no_i_c": {
                "type": "DRIVERS_LICENSE",
                "validation_data": [],
                "numbers": [],
            },
            "electoral_card_no_i_c": {
                "type": "ELECTORAL_CARD",
                "validation_data": [],
                "numbers": [],
            },
            "national_id_no_ic": {
                "type": "NATIONAL_ID",
                "validation_data": [],
                "numbers": [],
            },
            "national_passport_i_c": {
                "type": "NATIONAL_PASSPORT",
                "validation_data": [],
                "numbers": [],
            },
            "other_id_type_i_c": {
                "type": "OTHER",
                "name": None,
                "validation_data": [],
                "numbers": [],
            },
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
                        {
                            "row_number": cell.row,
                            "header": header.value,
                            "message": message,
                        }
                    )

                if header.value in documents_numbers:
                    if header.value == "other_id_type_i_c":
                        documents_numbers["other_id_type_i_c"]["name"] = value
                    elif header.value == "other_id_no_i_c":
                        documents_numbers["other_id_type_i_c"][
                            "validation_data"
                        ].append({"row_number": cell.row, "value": value})
                        documents_numbers["other_id_type_i_c"][
                            "numbers"
                        ].append(value)
                    else:
                        documents_numbers[header.value][
                            "validation_data"
                        ].append({"row_number": cell.row, "value": value})
                        documents_numbers["other_id_type_i_c"][
                            "numbers"
                        ].append(header.value)

                if header.value in identities_numbers:
                    identities_numbers[header.value]["numbers"].append(value)
                    identities_numbers[header.value]["validation_data"].append(
                        {"row_number": cell.row, "value": value}
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

        invalid_doc_rows = cls.documents_validator(documents_numbers)

        invalid_ident_rows = cls.identity_validator(identities_numbers)

        return [*invalid_rows, *invalid_doc_rows, *invalid_ident_rows]

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
            wb = load_workbook(xlsx_file, data_only=True)
            cls.WB = wb
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
        cls.image_loader = SheetImageLoader(household_sheet)
        return cls.rows_validator(household_sheet)

    @classmethod
    def validate_individuals_rows(cls, *args, **kwargs):
        if cls.WB is None:
            xlsx_file = kwargs.get("file")
            wb = openpyxl.load_workbook(xlsx_file, data_only=True)
        else:
            wb = cls.WB
        individuals_sheet = wb["Individuals"]
        cls.image_loader = SheetImageLoader(individuals_sheet)
        return cls.rows_validator(individuals_sheet)
