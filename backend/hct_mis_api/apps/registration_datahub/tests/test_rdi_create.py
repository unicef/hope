from django.core.management import call_command
from django.test import TestCase

from core.models import BusinessArea
from registration_datahub.fixtures import RegistrationDataImportDatahubFactory
from registration_datahub.models import ImportData


class TestRdiCreateTask(TestCase):
    multi_db = True

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")

        cls.import_data = ImportData.objects.create(
            xlsx_file="hct_mis_api/apps/registration_datahub/tests"
            "/test_file/new_reg_data_import.xlsx",
            number_of_households=3,
            number_of_individuals=6,
        )
        cls.registration_data_import = RegistrationDataImportDatahubFactory(
            import_data=cls.import_data
        )
        cls.business_area = BusinessArea.objects.first()

    def test_execute(self):
        pass

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
