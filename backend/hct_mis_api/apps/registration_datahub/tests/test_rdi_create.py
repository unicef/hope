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

    def test_handle_document_fields(self):
        pass

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
