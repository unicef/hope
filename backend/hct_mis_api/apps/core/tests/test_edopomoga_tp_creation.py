from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.celery_tasks import create_target_population_task
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, StorageFile
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.geo import models as geo_models


class TestEdopomogaCreation(APITestCase):
    databases = ("default", "registration_datahub")

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.generate_document_types_for_all_countries()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        cls.business_area.countries.add(country)

        cls.program = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )

        content = Path(f"{settings.PROJECT_ROOT}/apps/core/tests/test_files/edopomoga_sample.csv")

        cls.storage_file = StorageFile.objects.create(
            created_by=cls.user,
            business_area=cls.business_area,
            status=StorageFile.STATUS_NOT_PROCESSED,
            file=File(BytesIO(content.read_bytes()), name="edopomoga_sample.csv"),
        )

    def test_edopomoga_tp_creation(self):
        create_target_population_inner = create_target_population_task.__wrapped__
        create_target_population_inner(self.storage_file.id, "test_edopomoga")

        self.assertEqual(Household.objects.count(), 3)
        self.assertEqual(Individual.objects.count(), 5)


        self.storage_file.refresh_from_db()
        self.assertEqual(self.storage_file.status, StorageFile.STATUS_FINISHED)
