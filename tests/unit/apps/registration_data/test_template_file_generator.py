from django.test import TestCase
from extras.test_utils.factories.core import (
    create_afghanistan,
    create_pdu_flexible_attribute,
)
from extras.test_utils.factories.program import get_program_with_dct_type_and_name

from hope.models.flexible_attribute import PeriodicFieldData
from hope.apps.registration_data.services.template_generator_service import (
    TemplateFileGeneratorService,
)


class TestTemplateFileGenerator(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.program = get_program_with_dct_type_and_name()
        create_pdu_flexible_attribute(
            label="PDU Flex Attribute",
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=1,
            rounds_names=["May"],
            program=cls.program,
        )

    def test_create_workbook(self) -> None:
        wb = TemplateFileGeneratorService(self.program).create_workbook()

        expected_sheet_names = [
            "Households",
            "Individuals",
            "Import helper",
            "People",
        ].sort()
        result_sheet_names = wb.sheetnames.sort()

        assert expected_sheet_names == result_sheet_names

    def test_handle_name_and_label_row(self) -> None:
        fields = {
            "test": {
                "label": {"English(EN)": "My Test Label"},
                "required": True,
                "type": "STRING",
                "choices": [],
            },
            "test_h_f": {
                "label": {"English(EN)": "Flex Test Label"},
                "required": False,
                "type": "STRING",
                "choices": [],
            },
        }

        result = TemplateFileGeneratorService(self.program)._handle_name_and_label_row(fields)
        expected = (
            ["test", "test_h_f"],
            ["My Test Label - STRING - required", "Flex Test Label - STRING"],
        )
        assert expected == result

    def test_add_template_columns(self) -> None:
        result_wb = TemplateFileGeneratorService(self.program).create_workbook()

        households_rows = tuple(result_wb["Households"].iter_rows(values_only=True))

        assert households_rows[0][0] == "residence_status_h_c"
        assert households_rows[1][0] == "Residence status - SELECT_ONE"

        individuals_rows = tuple(result_wb["Individuals"].iter_rows(values_only=True))

        assert "pdu_flex_attribute_round_1_value" in individuals_rows[0]
        assert "pdu_flex_attribute_round_1_collection_date" in individuals_rows[0]

        assert individuals_rows[0][0] == "age"
        assert individuals_rows[1][0] == "Age (calculated) - INTEGER"

        people_rows = tuple(result_wb["People"].iter_rows(values_only=True))

        assert people_rows[0][0] == "pp_age"
        assert people_rows[1][0] == "Age (calculated) - INTEGER"

        assert people_rows[0][10] == "pp_admin3_i_c"
        assert people_rows[1][10] == "Social Worker resides in which admin3? - SELECT_ONE"

        assert people_rows[0][19] == "pp_middle_name_i_c"
        assert people_rows[1][19] == "Middle name(s) - STRING"

        assert people_rows[0][39] == "pp_drivers_license_issuer_i_c"
        assert people_rows[1][39] == "Issuing country of driver's license - SELECT_ONE"

        assert people_rows[0][69] == "pp_village_i_c"
        assert people_rows[1][69] == "Village - STRING"

        assert people_rows[0][87] == "pdu_flex_attribute_round_1_collection_date"

        assert people_rows[0][83] == "pp_index_id"
        assert people_rows[1][83] == "Index ID - INTEGER - required"
