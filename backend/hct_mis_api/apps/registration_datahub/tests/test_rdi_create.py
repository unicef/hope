import unittest

from django.core.files import File
from django.core.management import call_command
from django.test import TestCase

from core.models import BusinessArea, AdminArea, AdminAreaType
from registration_datahub.fixtures import RegistrationDataImportDatahubFactory
from registration_datahub.models import (
    ImportData,
    ImportedHousehold,
    ImportedIndividual,
)
from registration_datahub.tasks.rdi_create import (
    RdiXlsxCreateTask,
    RdiKoboCreateTask,
)


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
                file=file, number_of_households=3, number_of_individuals=6,
            )
        cls.registration_data_import = RegistrationDataImportDatahubFactory(
            import_data=cls.import_data
        )
        cls.business_area = BusinessArea.objects.first()

    def test_execute(self):
        task = RdiXlsxCreateTask()
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

@unittest.skip("skip for now until I will mock response")
class TestRdiKoboCreateTask(TestCase):
    multi_db = True

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")

        with open(
            "hct_mis_api/apps/registration_datahub/tests"
            "/test_file/kobo_submissions.json",
            "rb",
        ) as json_file:
            file = File(json_file.raw)
            cls.import_data = ImportData.objects.create(
                file=file, number_of_households=1, number_of_individuals=2,
            )

        cls.business_area = BusinessArea.objects.first()
        cls.business_area.save()

        admin1_type = AdminAreaType.objects.create(
            name="Bakool", admin_level=1, business_area=cls.business_area
        )
        admin1 = AdminArea.objects.create(
            title="SO25", admin_area_type=admin1_type
        )

        admin2_type = AdminAreaType.objects.create(
            name="Ceel Barde", admin_level=2, business_area=cls.business_area
        )
        AdminArea.objects.create(
            title="SO2502", parent=admin1, admin_area_type=admin2_type
        )

        cls.registration_data_import = RegistrationDataImportDatahubFactory(
            import_data=cls.import_data
        )

    def test_execute(self):
        task = RdiKoboCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
        )

        households_count = ImportedHousehold.objects.count()
        individuals_count = ImportedIndividual.objects.count()

        self.assertEqual(1, households_count)
        self.assertEqual(2, individuals_count)
