from django.core.files import File
from django.core.management import call_command
from django.test import TestCase

from core.models import BusinessArea
from registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
    ImportedIndividualFactory,
)
from registration_datahub.models import (
    ImportData,
    ImportedHousehold,
    ImportedIndividual,
)
from registration_datahub.tasks.rdi_create import RdiCreateTask


class TestRdiCreateTask(TestCase):
    multi_db = True

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")

        with open(
            "hct_mis_api/apps/registration_datahub/tests"
            "/test_file/new_reg_data_import.xlsx",
            "rb",
        ) as excel_file:
            file = File(excel_file)
            cls.import_data = ImportData.objects.create(
                xlsx_file=file, number_of_households=3, number_of_individuals=6,
            )
        cls.registration_data_import = RegistrationDataImportDatahubFactory(
            import_data=cls.import_data
        )
        cls.business_area = BusinessArea.objects.first()

    def test_execute(self):
        task = RdiCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
        )

        households_count = ImportedHousehold.objects.count()
        individuals_count = ImportedIndividual.objects.count()

        self.assertEqual(3, households_count)
        self.assertEqual(6, individuals_count)

    def _handle_document_fields(
        self, value, header, individual, *args, **kwargs
    ):
        if value is None:
            return

        if header == "other_id_type_i_c":
            doc_type = value
        else:
            readable_name = (
                header.replace("_no", "").replace("_i_c", "").replace("_", " ")
            )
            readable_name_split = readable_name.split(" ")
            doc_type = ""
            for word in readable_name_split:
                if word == "id":
                    doc_type += word.upper() + " "
                else:
                    doc_type += word.capitalize() + " "
            doc_type = doc_type.strip()
        row_num = kwargs.get("row_number")
        document_data = self.documents.get(f"individual_{row_num}")
        if document_data:
            document_data["value"] = value
        else:
            self.documents[f"individual_{row_num}"] = {
                "individual": individual,
                "header": header,
                "type": None,
                "value": value,
            }

    def test_handle_document_fields(self):
        individual = ImportedIndividualFactory()

        # Case 1: If value is None
        task = RdiCreateTask()
        task._handle_document_fields(
            value=None, header="test", individual=individual, row_num=11,
        )
        self.assertIsNone(task.documents)

        # Case 2: If header == other_id_type_i_c
        task = RdiCreateTask()
        task._handle_document_fields(
            value="Some Document",
            header="other_id_type_i_c",
            individual=individual,
            row_num=11,
        )
        expected = {
            "individual_11": {
                "individual": individual,
                "header": "other_id_type_i_c",
                "type": "Some Document",
            }
        }
        self.assertEqual(expected, task.documents)

        # Case 3: If header == other_id_no_i_c
        task = RdiCreateTask()
        task._handle_document_fields(
            value="123-12-34-567",
            header="other_id_no_i_c",
            individual=individual,
            row_num=11,
        )
        expected = {
            "individual_11": {
                "individual": individual,
                "header": "other_id_no_i_c",
                "value": "123-12-34-567",
            }
        }
        self.assertEqual(expected, task.documents)

        # Case 3: First add other_id_no_i_c then other_id_type_i_c
        task = RdiCreateTask()
        task._handle_document_fields(
            value="123-12-34-567",
            header="other_id_no_i_c",
            individual=individual,
            row_num=11,
        )
        task._handle_document_fields(
            value="Some Document",
            header="other_id_no_i_c",
            individual=individual,
            row_num=11,
        )
        expected = {
            "individual_11": {
                "individual": individual,
                "header": "other_id_no_i_c",
                "type": "Some Document",
                "value": "123-12-34-567",
            }
        }
        self.assertEqual(expected, task.documents)

        # Case 4: First add other_id_type_i_c then other_id_no_i_c
        task = RdiCreateTask()
        task._handle_document_fields(
            value="123-12-34-567",
            header="other_id_no_i_c",
            individual=individual,
            row_num=11,
        )
        task._handle_document_fields(
            value="Some Document",
            header="other_id_no_i_c",
            individual=individual,
            row_num=11,
        )
        expected = {
            "individual_11": {
                "individual": individual,
                "header": "other_id_no_i_c",
                "type": "Some Document",
                "value": "123-12-34-567",
            }
        }
        self.assertEqual(expected, task.documents)

        # Case 4: Normal document
        task = RdiCreateTask()
        task._handle_document_fields(
            value="123-12-34-567",
            header="",
            individual=individual,
            row_num=11,
        )
        expected = {
            "individual_11": {
                "individual": individual,
                "header": "drivers_license_no_i_c",
                "type": "Drivers license_no_i_c",
                "value": "123-12-34-567",
            }
        }
        self.assertEqual(expected, task.documents)

    def test_handle_document_photo_fields(self):
        pass

    def test_handle_image_field(self):
        pass

    def test_handle_geopoint_field(self):
        pass

    def test_create_documents(self):
        pass

    def test_create_objects(self):
        pass
