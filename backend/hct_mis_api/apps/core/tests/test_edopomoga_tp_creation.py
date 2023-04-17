from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.celery_tasks import create_target_population_task
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, StorageFile
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.models import STATUS_INACTIVE, Household, Individual
from hct_mis_api.apps.mis_datahub import models as dh_mis_models
from hct_mis_api.apps.mis_datahub.tasks.send_tp_to_datahub import SendTPToDatahubTask
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


class TestEdopomogaCreation(APITestCase):
    databases = ("default", "registration_datahub", "cash_assist_datahub_mis")

    @classmethod
    def setUpTestData(cls) -> None:
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

    def test_edopomoga_tp_creation(self) -> None:
        create_target_population_inner = create_target_population_task.__wrapped__
        create_target_population_inner(self.storage_file.id, self.program.id, "test_edopomoga")

        self.assertEqual(Household.objects.count(), 3)
        self.assertEqual(Individual.objects.count(), 5)
        self.assertEqual(TargetPopulation.objects.count(), 1)
        self.assertEqual(Household.objects.filter(withdrawn=True).count(), 3)
        self.assertEqual(Individual.objects.filter(withdrawn=True).count(), 5)

        self.storage_file.refresh_from_db()
        self.assertEqual(self.storage_file.status, StorageFile.STATUS_FINISHED)

    def test_calculate_household_size(self) -> None:
        create_target_population_inner = create_target_population_task.__wrapped__
        create_target_population_inner(self.storage_file.id, self.program.id, "test_edopomoga")

        household1 = Household.objects.get(family_id="1281191")
        household2 = Household.objects.get(family_id="1281375")
        household3 = Household.objects.get(family_id="1281383")

        self.assertEqual(household1.size, 4)
        self.assertEqual(household2.size, 4)
        self.assertEqual(household3.size, 4)

    def test_edopomoga_tp_send_to_ca_clear_withdrawn(self) -> None:
        # set clear_withdrawn flag
        self.business_area.custom_fields = {"clear_withdrawn": True}
        self.business_area.save()
        tp_name = "New eDopomoga test clear_withdrawn data"
        create_target_population_inner = create_target_population_task.__wrapped__
        create_target_population_inner(self.storage_file.id, self.program.id, tp_name)

        target_population = TargetPopulation.objects.get(name=tp_name)

        SendTPToDatahubTask().execute(target_population)

        self.assertEqual(Household.objects.filter(withdrawn=True).count(), 3)
        self.assertEqual(Individual.objects.filter(withdrawn=True).count(), 5)

        self.assertEqual(dh_mis_models.Household.objects.filter(status=STATUS_INACTIVE).count(), 0)
        self.assertEqual(dh_mis_models.Individual.objects.filter(status=STATUS_INACTIVE).count(), 0)
