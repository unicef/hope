from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.test import TestCase

import pytest
from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import (
    create_afghanistan,
    create_pdu_flexible_attribute,
)
from extras.test_utils.factories.payment import generate_delivery_mechanisms
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

from hct_mis_api.apps.core.models import DataCollectingType, PeriodicFieldData
from hct_mis_api.apps.geo.fixtures import generate_small_areas_for_afghanistan_only
from hct_mis_api.apps.household.models import (
    Household,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import ImportData
from hct_mis_api.apps.registration_datahub.tasks.rdi_merge import RdiMergeTask
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestRdiXlsxCollisions(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        call_command("loadcountrycodes")
        PartnerFactory(name="WFP")
        PartnerFactory(name="UNHCR")
        content = Path(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/new_reg_data_import_collision.xlsx"
        ).read_bytes()
        cls.file = File(BytesIO(content), name="new_reg_data_import_collision.xlsx")
        cls.business_area = create_afghanistan()
        generate_small_areas_for_afghanistan_only()

        from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )

        cls.RdiXlsxCreateTask = RdiXlsxCreateTask
        cls.program = ProgramFactory(
            status=Program.ACTIVE,
            data_collecting_type__type=DataCollectingType.Type.STANDARD,
            collision_detection_enabled=True,
            collision_detector="hct_mis_api.apps.program.collision_detectors.IdentificationKeyCollisionDetector",
        )
        cls.string_attribute = create_pdu_flexible_attribute(
            label="PDU String Attribute",
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=1,
            rounds_names=["May"],
            program=cls.program,
        )
        generate_delivery_mechanisms()

        rebuild_search_index()

    def test_execute(self) -> None:
        import_data1 = ImportData.objects.create(
            file=self.file,
            number_of_households=3,
            number_of_individuals=6,
        )
        registration_data_import1 = RegistrationDataImportFactory(
            business_area=self.business_area, program=self.program, import_data=import_data1
        )
        self.RdiXlsxCreateTask().execute(
            registration_data_import1.id, import_data1.id, self.business_area.id, self.program.id
        )
        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        self.assertEqual(3, households_count)
        self.assertEqual(6, individuals_count)

        import_data2 = ImportData.objects.create(
            file=self.file,
            number_of_households=3,
            number_of_individuals=6,
        )
        registration_data_import2 = RegistrationDataImportFactory(
            business_area=self.business_area, program=self.program, import_data=import_data2
        )
        self.RdiXlsxCreateTask().execute(
            registration_data_import2.id, import_data2.id, self.business_area.id, self.program.id
        )
        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        self.assertEqual(5, households_count)
        self.assertEqual(11, individuals_count)
        self.assertEqual(
            PendingHousehold.objects.get(identification_key="ab1234").extra_rdis.first().id,
            registration_data_import2.id,
        )

    def test_merge(self) -> None:
        import_data1 = ImportData.objects.create(
            file=self.file,
            number_of_households=3,
            number_of_individuals=6,
        )
        registration_data_import1 = RegistrationDataImportFactory(
            business_area=self.business_area, program=self.program, import_data=import_data1
        )
        self.RdiXlsxCreateTask().execute(
            registration_data_import1.id, import_data1.id, self.business_area.id, self.program.id
        )
        import_data2 = ImportData.objects.create(
            file=self.file,
            number_of_households=3,
            number_of_individuals=6,
        )
        registration_data_import2 = RegistrationDataImportFactory(
            business_area=self.business_area, program=self.program, import_data=import_data2
        )
        self.RdiXlsxCreateTask().execute(
            registration_data_import2.id, import_data2.id, self.business_area.id, self.program.id
        )
        self.assertEqual(
            PendingHousehold.objects.get(identification_key="ab1234").extra_rdis.first().id,
            registration_data_import2.id,
        )
        RdiMergeTask().execute(registration_data_import2.pk)
        self.assertEqual(
            Household.objects.get(identification_key="ab1234").registration_data_import.pk, registration_data_import2.pk
        )
        self.assertEqual(
            Household.objects.get(identification_key="ab1234").extra_rdis.first().id,
            registration_data_import1.id,
        )
        self.assertEqual(Household.objects.get(identification_key="ab1234").rdi_merge_status, Household.MERGED)
