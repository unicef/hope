from django.core.exceptions import ValidationError


class BaseValidator:
    """
    Base validation class, inherit from this class to create custom validators.
    Your custom validators have to implement validation methods that starts
    with name "validate_" so validate can call all the validators from your
    custom validator.

    Custom validate method have to takes *args, **kwargs parameters.

    validate method with parameters have to be called in mutate method.
    If there are validation errors they will be all
    returned as one error message.
    """

    @classmethod
    def validate(cls, excluded_validators=None, *args, **kwargs):
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
            raise Exception(", ".join(errors_list))


class CommonValidator(BaseValidator):
    @classmethod
    def validate_start_end_date(cls, *args, **kwargs):
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date cannot be greater than the end date.")


def prepare_choices_for_validation(choices_sheet):
    from collections import defaultdict
    import xlrd

    choices_mapping = defaultdict(list)
    first_row = choices_sheet.row(0)
    choices_headers_map = [col.value for col in first_row]

    if {"list_name", "name", "label:English(EN)"}.issubset(set(choices_headers_map)) is False:
        raise ValueError("Choices sheet does not contain all required columns")

    for row_number in range(1, choices_sheet.nrows):
        row = choices_sheet.row(row_number)

        if all([cell.ctype == xlrd.XL_CELL_EMPTY for cell in row]):
            continue

        last_list_name = None
        choice_value = None
        english_label = ""
        for cell, header_name in zip(row, choices_headers_map):
            cell_value = cell.value

            if header_name == "list_name" and cell_value != last_list_name:
                last_list_name = cell_value
            elif header_name == "name":
                if isinstance(cell_value, float) and cell_value.is_integer():
                    cell_value = str(int(cell_value))

                if isinstance(cell_value, str):
                    cell_value = cell_value.strip().upper()

                choice_value = cell_value
            elif header_name == "label:English(EN)":
                from unicodedata import normalize

                english_label = normalize("NFKD", str(cell_value))

        if last_list_name is not None and choice_value is not None:
            choices_mapping[last_list_name].append({"label": {"English(EN)": english_label}, "value": choice_value})

    return choices_mapping


def validate_kobo_template(survey_sheet, choices_sheet):
    from hct_mis_api.apps.core.core_fields_attributes import (
        CORE_FIELDS_ATTRIBUTES,
        KOBO_ONLY_HOUSEHOLD_FIELDS,
        KOBO_ONLY_INDIVIDUAL_FIELDS,
        TYPE_GEOPOINT,
        TYPE_SELECT_MANY,
        TYPE_DATE,
        TYPE_DECIMAL,
        TYPE_INTEGER,
        TYPE_STRING,
        TYPE_SELECT_ONE,
        TYPE_IMAGE,
        TYPE_BOOL,
    )
    from hct_mis_api.apps.core.utils import xlrd_rows_iterator

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
    }

    choices_mapping = prepare_choices_for_validation(choices_sheet)

    columns_names_and_numbers_mapping = {
        "type": None,
        "name": None,
        "required": None,
    }
    first_row = survey_sheet.row(0)
    for index, cell in enumerate(first_row):
        column_name = cell.value
        if column_name in columns_names_and_numbers_mapping.keys():
            columns_names_and_numbers_mapping[column_name] = index

    if None in columns_names_and_numbers_mapping.values():
        raise ValueError("Survey sheet does not contain all required columns")

    core_fields_in_file = {}
    for row in xlrd_rows_iterator(survey_sheet):
        field_name = row[columns_names_and_numbers_mapping["name"]].value
        if field_name.endswith("_c") is False:
            continue

        field_type = row[columns_names_and_numbers_mapping["type"]].value

        choices_list_name = None
        if field_type.startswith("select_"):
            field_type, choices_list_name, *_ = field_type.split(" ")

        if field_type not in CHOICE_MAP.keys():
            continue

        required_value = str(row[columns_names_and_numbers_mapping["required"]].value)
        if required_value.lower() not in ("true", "false"):
            is_field_required = False
        else:
            is_field_required = True if required_value == "true" else False

        field_type = CHOICE_MAP[field_type] if field_type != "calculate" else "CALCULATE"

        core_fields_in_file[field_name] = {
            "type": field_type,
            "required": is_field_required,
            "choices": choices_mapping[choices_list_name] if choices_list_name is not None else [],
        }

    all_core_fields = (
        CORE_FIELDS_ATTRIBUTES + list(KOBO_ONLY_HOUSEHOLD_FIELDS.values()) + list(KOBO_ONLY_INDIVIDUAL_FIELDS.values())
    )
    core_fields_in_db = {
        core_field_data["xlsx_field"]: {
            "type": core_field_data["type"],
            "required": core_field_data["required"],
            "choices": core_field_data["choices"],
        }
        for core_field_data in all_core_fields
        if core_field_data["xlsx_field"].endswith("_c")
    }

    validation_errors = []
    for core_field, field_data in core_fields_in_db.items():
        field_type = field_data["type"]
        field_required = field_data["required"]
        field_choices = field_data["choices"]
        core_field_from_file = core_fields_in_file.get(core_field)

        # check if field exists
        if core_field_from_file is None:
            validation_errors.append(
                {
                    "field": core_field,
                    "message": "Field is missing",
                }
            )
            continue

        # check types
        if field_type != core_field_from_file["type"] and core_field_from_file["type"] != "CALCULATE":
            if field_type == TYPE_BOOL and core_field_from_file["type"] == TYPE_SELECT_ONE:
                continue
            validation_errors.append(
                {
                    "field": core_field,
                    "message": f"Expected type: {field_type}, actual type: {core_field_from_file['type']}",
                }
            )

        # check required
        field_from_file_required = str(core_field_from_file["required"])
        expected_required_fields = (
            "country_h_c"
            "size_h_c"
            "relationship_i_c"
            "role_i_c"
            "full_name_i_c"
            "gender_i_c"
            "birth_date_i_c"
            "estimated_birth_date_i_c"
        )
        if core_field in expected_required_fields and field_from_file_required.lower() != "true":
            validation_errors.append(
                {
                    "field": core_field,
                    "message": "Field must be required",
                }
            )
        # if field_required != field_from_file_required:
        #     if field_required is True and field_from_file_required is False:
        #         validation_errors.append(
        #             {
        #                 "field": core_field,
        #                 "message": "Field must be required",
        #             }
        #         )
        #     else:
        #         validation_errors.append(
        #             {
        #                 "field": core_field,
        #                 "message": "Field must be not required",
        #             }
        #         )

        # check choices
        fields_excluded_from_choice_check = (
            "country_h_c",
            "country_origin_h_c",
            "birth_certificate_issuer_i_c",
            "drivers_license_issuer_i_c",
            "electoral_card_issuer_i_c",
            "unhcr_id_issuer_i_c",
            "national_passport_issuer_i_c",
            "national_id_issuer_i_c",
            "scope_id_issuer_i_c",
            "other_id_issuer_i_c",
            "currency_h_c",
            # temporarily disabled from checking
            "admin1_h_c",
            "admin2_h_c",
        )
        if core_field in fields_excluded_from_choice_check:
            continue

        from_file_choices = core_field_from_file["choices"]

        choices_excluded_from_checking = (
            {"label": {"English(EN)": "None"}, "value": ""},
            {"label": {"English(EN)": "Not provided"}, "value": "NOT_PROVIDED"},
            {"label": {"English(EN)": "Unknown"}, "value": "UNKNOWN"},
        )
        for internal_choice in field_choices:
            if internal_choice in choices_excluded_from_checking:
                continue

            if internal_choice not in from_file_choices:
                validation_errors.append(
                    {
                        "field": core_field,
                        "message": f"Choice: {internal_choice} is not present in the file",
                    }
                )

        for file_choice in from_file_choices:
            if file_choice not in from_file_choices:
                validation_errors.append(
                    {
                        "field": core_field,
                        "message": f"Choice: {file_choice} is not present in HOPE",
                    }
                )

    return validation_errors
