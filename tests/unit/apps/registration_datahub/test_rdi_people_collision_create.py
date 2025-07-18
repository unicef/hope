from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.test import TestCase

import pytest

from hct_mis_api.apps.account.fixtures import PartnerFactory
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    create_pdu_flexible_attribute,
)
from hct_mis_api.apps.core.models import DataCollectingType, PeriodicFieldData
from hct_mis_api.apps.household.models import PendingHousehold, PendingIndividual
from hct_mis_api.apps.payment.fixtures import generate_delivery_mechanisms
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import ImportData
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestRdiXlsxPeopleCollisions(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        PartnerFactory(name="UNHCR")
        content = Path(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/rdi_people_test_collision.xlsx"
        ).read_bytes()
        cls.file = File(BytesIO(content), name="rdi_people_test_collision.xlsx")
        cls.business_area = create_afghanistan()

        from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_people_create import (
            RdiXlsxPeopleCreateTask,
        )

        cls.RdiXlsxPeopleCreateTask = RdiXlsxPeopleCreateTask
        cls.program = ProgramFactory(
            status=Program.ACTIVE,
            data_collecting_type__type=DataCollectingType.Type.SOCIAL,
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
            number_of_households=0,
            number_of_individuals=4,
        )
        registration_data_import1 = RegistrationDataImportFactory(
            business_area=self.business_area, program=self.program, import_data=import_data1
        )
        self.RdiXlsxPeopleCreateTask().execute(
            registration_data_import1.id, import_data1.id, self.business_area.id, self.program.id
        )
        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        self.assertEqual(4, households_count)
        self.assertEqual(4, individuals_count)

        import_data2 = ImportData.objects.create(
            file=self.file,
            number_of_households=0,
            number_of_individuals=4,
        )
        registration_data_import2 = RegistrationDataImportFactory(
            business_area=self.business_area, program=self.program, import_data=import_data2
        )
        self.RdiXlsxPeopleCreateTask().execute(
            registration_data_import2.id, import_data2.id, self.business_area.id, self.program.id
        )
        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        self.assertEqual(7, households_count)
        self.assertEqual(7, individuals_count)
        self.assertEqual(
            PendingHousehold.objects.get(identification_key="ab1234").extra_rdis.first().id,
            registration_data_import2.id,
        )
