import operator
from unittest import mock

from django.conf import settings
from django.core.management import call_command

import openpyxl

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.utils import SheetImageLoader
from hct_mis_api.apps.registration_datahub.validators import UploadXLSXInstanceValidator


class TestXLSXValidatorsMethods(APITestCase):
    FILES_DIR_PATH = f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file"

    @classmethod
    def setUpTestData(cls):
        call_command("loadflexfieldsattributes")

    def test_geolocation_validator(self):
        # test correct values:
        correct_values = (
            "1.1, 1.1",
            "0.0, 0.0",
            "54.1234252, 67.535232",
        )
        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        for value in correct_values:
            self.assertTrue(upload_xlsx_instance_validator.geolocation_validator(value, "hh_geopoint_h_c"))

        # test incorrect values:
        incorrect_values = (
            "1, 1, 1, 1",
            "0, 0",
            "52.124.124, 1241.242",
            "24.121a, bcd421.222",
        )
        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        for value in incorrect_values:
            self.assertFalse(upload_xlsx_instance_validator.geolocation_validator(value, "hh_geopoint_h_c"))

    def test_date_validator(self):
        # test correct values:
        correct_values = (
            "01-03-1994",
            "1-3-1994",
            "27-12-2020",
            "27/12/2020",
            "27.12.2020",
            "27.12.2020",
        )
        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        for value in correct_values:
            self.assertTrue(upload_xlsx_instance_validator.date_validator(value, "birth_date_i_c"))

        # test incorrect values:
        incorrect_values = (
            "13-13-1994",
            "213.22.2020",
            "qwerty",
            "24",
            "-24",
        )
        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        for value in incorrect_values:
            self.assertFalse(upload_xlsx_instance_validator.date_validator(value, "birth_date_i_c"))

    def test_integer_validator(self):
        # test correct values:
        correct_values = (
            "12",
            "0",
            0,
            12,
            12345,
            -12,
        )
        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        for value in correct_values:
            self.assertTrue(upload_xlsx_instance_validator.integer_validator(value, "size_h_c"))

        # test incorrect values:
        incorrect_values = (
            "13-13-1994",
            "213.22.2020",
            "qwerty",
            # 12.2345,
            "12,242",
        )

        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        for value in incorrect_values:
            self.assertFalse(upload_xlsx_instance_validator.integer_validator(value, "size_h_c"))

    def test_phone_validator(self):
        # test correct values:
        correct_values = (
            "+1-202-555-0172",
            "+44 1632 960852",
            "+1-613-555-0182",
            "+61 1900 654 321",
            "+36 55 979 922",
            "+353 20 915 8245",
            "+48 69 563 7300",
        )
        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        for value in correct_values:
            self.assertTrue(upload_xlsx_instance_validator.phone_validator(value, "phone_no_i_c"))

        # test incorrect values:
        incorrect_values = (
            "123 123 123",  # no region code
            "13-13-1994",
            "213.22.2020",
            "qwerty",
            12.2345,
            "12,242",
            "12",
            12,
        )

        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        for value in incorrect_values:
            self.assertFalse(upload_xlsx_instance_validator.phone_validator(value, "phone_no_i_c"))

    def test_choice_validator(self):
        test_correct_values = (("REFUGEE", "residence_status_h_c"),)
        test_incorrect_values = (
            ("YES", "work_status"),
            ("OTHER", "work_status"),
            ("Hearing Problems", "disability"),
            ("Option 37", "assistance_type_h_f"),
        )
        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        for value, header in test_correct_values:
            self.assertTrue(upload_xlsx_instance_validator.choice_validator(value, header))

        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        for value, header in test_incorrect_values:
            self.assertFalse(upload_xlsx_instance_validator.choice_validator(value, header))

    def test_rows_validator_too_many_head_of_households(self):
        wb = openpyxl.load_workbook(
            f"{self.FILES_DIR_PATH}/error-xlsx.xlsx",
            data_only=True,
        )
        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
        upload_xlsx_instance_validator.rows_validator(wb["Households"])
        result = upload_xlsx_instance_validator.rows_validator(wb["Individuals"])
        expected = [
            {
                "row_number": 0,
                "header": "relationship_i_c",
                "message": "Sheet: Individuals, There are multiple head of " "households for household with id: 3",
            }
        ]
        self.assertEqual(expected, result)

    def test_rows_validator(self):

        wb = openpyxl.load_workbook(
            f"{self.FILES_DIR_PATH}/invalid_rows.xlsx",
            data_only=True,
        )

        wb_valid = openpyxl.load_workbook(
            f"{self.FILES_DIR_PATH}/new_reg_data_import.xlsx",
            data_only=True,
        )

        invalid_file = (
            (
                wb["Households"],
                [
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 1 for type select "
                        "many of field assistance_type_h_f",
                        "row_number": 3,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 1, Option 2, Option "
                        "3 for type select many of field assistance_type_h_f",
                        "row_number": 4,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 13 for type select "
                        "many of field assistance_type_h_f",
                        "row_number": 5,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 3 for type select "
                        "many of field assistance_type_h_f",
                        "row_number": 6,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 1, Option 3 for type "
                        "select many of field assistance_type_h_f",
                        "row_number": 7,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 2, Option 3 for type "
                        "select many of field assistance_type_h_f",
                        "row_number": 8,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 2 for type select "
                        "many of field assistance_type_h_f",
                        "row_number": 9,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 1, Option 2, Option "
                        "4 for type select many of field assistance_type_h_f",
                        "row_number": 10,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 4 for type select "
                        "many of field assistance_type_h_f",
                        "row_number": 11,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 5 for type select "
                        "many of field assistance_type_h_f",
                        "row_number": 12,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 1, Option 4 for type "
                        "select many of field assistance_type_h_f",
                        "row_number": 13,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 2, Option 4 for type "
                        "select many of field assistance_type_h_f",
                        "row_number": 14,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 3 for type select "
                        "many of field assistance_type_h_f",
                        "row_number": 15,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 1, Option 2, Option "
                        "5 for type select many of field assistance_type_h_f",
                        "row_number": 16,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 6 for type select "
                        "many of field assistance_type_h_f",
                        "row_number": 17,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 7 for type select "
                        "many of field assistance_type_h_f",
                        "row_number": 18,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 1, Option 5 for type "
                        "select many of field assistance_type_h_f",
                        "row_number": 19,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 2, Option 5 for type "
                        "select many of field assistance_type_h_f",
                        "row_number": 20,
                    },
                    {
                        "header": "assistance_type_h_f",
                        "message": "Sheet: Households, Unexpected value: Option 4 for type select "
                        "many of field assistance_type_h_f",
                        "row_number": 21,
                    },
                ],
            ),
            (
                wb["Individuals"],
                [
                    {
                        "row_number": 8,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, There is no household with provided id: TEXT",
                    },
                    {
                        "row_number": 29,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, There is no household with provided id: 52",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 34, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 35, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 36, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 37, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 38, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 39, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 40, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 41, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 42, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 43, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 44, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 45, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 46, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 47, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 48, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 49, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 50, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: 51, has to have a head of household",
                    },
                    {
                        "row_number": 0,
                        "header": "relationship_i_c",
                        "message": "Sheet: Individuals, Household with id: Some Text, has to have a head of household",
                    },
                ],
            ),
        )
        valid_file = (
            (
                wb_valid["Households"],
                [],
            ),
            (
                wb_valid["Individuals"],
                [],
            ),
        )
        files = (invalid_file, valid_file)
        for file in files:
            upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
            for sheet, expected_values in file:
                upload_xlsx_instance_validator.image_loader = SheetImageLoader(sheet)
                result = upload_xlsx_instance_validator.rows_validator(sheet)
                self.assertEqual(result, expected_values)

    def test_validate_file_extension(self):
        file_path, expected_values = (
            f"{self.FILES_DIR_PATH}/" f"image.png",
            [{"row_number": 1, "message": "Only .xlsx files are accepted for import"}],
        )
        with open(file_path, "rb") as file:
            upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
            result = upload_xlsx_instance_validator.validate_file_extension(file)
            self.assertEqual(result[0]["row_number"], expected_values[0]["row_number"])
            self.assertEqual(result[0]["message"], expected_values[0]["message"])

    def test_validate_file_content_as_xlsx(self):
        file_path, expected_values = (
            f"{self.FILES_DIR_PATH}/" f"not_excel_file.xlsx",
            [{"row_number": 1, "message": "Invalid .xlsx file"}],
        )
        with open(file_path, "rb") as file:
            upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
            result = upload_xlsx_instance_validator.validate_everything(file, "afghanistan")
            self.assertEqual(result[0]["row_number"], expected_values[0]["row_number"])
            self.assertEqual(result[0]["message"], expected_values[0]["message"])

    def test_validate_file_with_template(self):
        invalid_cols_file_path = f"{self.FILES_DIR_PATH}/new_reg_data_import.xlsx"
        with open(invalid_cols_file_path, "rb") as file:
            upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
            wb = openpyxl.load_workbook(file, data_only=True)
            errors = upload_xlsx_instance_validator.validate_file_with_template(wb)
            errors.sort(key=operator.itemgetter("row_number", "header"))
            self.assertEqual(errors, [])

    def test_required_validator(self):
        with mock.patch(
            "hct_mis_api.apps.registration_datahub.validators.UploadXLSXInstanceValidator.get_all_fields",
            lambda *args: {"test": {"required": True}},
        ):
            upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
            result = upload_xlsx_instance_validator.required_validator(value="tak", header="test")
            self.assertTrue(result)

        with mock.patch(
            "hct_mis_api.apps.registration_datahub.validators.UploadXLSXInstanceValidator.get_all_fields",
            lambda *args: {"test": {"required": True}},
        ):
            upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
            result = upload_xlsx_instance_validator.required_validator(value="", header="test")
            self.assertFalse(result)

        with mock.patch(
            "hct_mis_api.apps.registration_datahub.validators.UploadXLSXInstanceValidator.get_all_fields",
            lambda *args: {"test": {"required": False}},
        ):
            upload_xlsx_instance_validator = UploadXLSXInstanceValidator()
            result = upload_xlsx_instance_validator.required_validator(value="", header="test")
            self.assertTrue(result)

    def test_validate_empty_file(self):
        empty_file_path = f"{self.FILES_DIR_PATH}/empty_rdi.xlsx"
        wb = openpyxl.load_workbook(
            empty_file_path,
            data_only=True,
        )
        upload_xlsx_instance_validator = UploadXLSXInstanceValidator()

        expected_result = [
            {
                "header": "Households",
                "message": "There aren't households in the file.",
                "row_number": 1,
            },
            {
                "header": "Individuals",
                "message": "There aren't individuals in the file.",
                "row_number": 1,
            },
        ]

        result = upload_xlsx_instance_validator.validate_collectors_size(wb)
        self.assertEqual(result, expected_result)
