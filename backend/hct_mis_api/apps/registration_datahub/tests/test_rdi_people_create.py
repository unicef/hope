from datetime import date
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.forms import model_to_dict

from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import (
    ImportData,
    ImportedHousehold,
    ImportedIndividual,
)
from hct_mis_api.apps.registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
)
from hct_mis_api.conftest import disabled_locally_test


@disabled_locally_test
class TestRdiXlsxPeople(BaseElasticSearchTestCase):
    databases = {
        "default",
        "registration_datahub",
    }
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/rdi_people_test.xlsx"
        ).read_bytes()
        file = File(BytesIO(content), name="rdi_people_test.xlsx")
        cls.business_area = create_afghanistan()

        from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_people_create import (
            RdiXlsxPeopleCreateTask,
        )

        cls.RdiXlsxPeopleCreateTask = RdiXlsxPeopleCreateTask
        cls.import_data = ImportData.objects.create(
            file=file,
            number_of_households=0,
            number_of_individuals=4,
        )
        cls.program = ProgramFactory(status=Program.ACTIVE, data_collecting_type__type=DataCollectingType.Type.SOCIAL)
        cls.registration_data_import = RegistrationDataImportDatahubFactory(
            import_data=cls.import_data, business_area_slug=cls.business_area.slug, hct_id=None
        )
        hct_rdi = RegistrationDataImportFactory(
            datahub_id=cls.registration_data_import.id,
            name=cls.registration_data_import.name,
            business_area=cls.business_area,
            program=cls.program,
        )
        cls.registration_data_import.hct_id = hct_rdi.id
        cls.registration_data_import.save()

        super().setUpTestData()

    def test_execute(self) -> None:
        self.RdiXlsxPeopleCreateTask().execute(
            self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id
        )
        households_count = ImportedHousehold.objects.count()
        individuals_count = ImportedIndividual.objects.count()

        self.assertEqual(4, households_count)
        self.assertEqual(4, individuals_count)

        individual_data = {
            "full_name": "Derek Index4",
            "given_name": "Derek",
            "middle_name": "",
            "family_name": "Index4",
            "sex": "MALE",
            "relationship": "HEAD",
            "birth_date": date(2000, 8, 22),
            "marital_status": "MARRIED",
        }
        matching_individuals = ImportedIndividual.objects.filter(**individual_data)

        self.assertEqual(matching_individuals.count(), 1)

        household_data = {
            "residence_status": "REFUGEE",
            "country": "IM",
            "zip_code": "002",
            "flex_fields": {},
        }
        household = matching_individuals.first().household
        household_obj_data = model_to_dict(household, ("residence_status", "country", "zip_code", "flex_fields"))

        roles = household.individuals_and_roles.all()
        self.assertEqual(roles.count(), 1)
        role = roles.first()
        self.assertEqual(role.role, "ALTERNATE")
        self.assertEqual(role.individual.full_name, "WorkerCollector ForDerekIndex_4")
        self.assertEqual(household_obj_data, household_data)

        role_primary = (
            ImportedIndividual.objects.filter(given_name="Jan", family_name="Index3")
            .first()
            .household.individuals_and_roles.all()
            .first()
        )
        self.assertEqual(role_primary.role, "PRIMARY")
        self.assertEqual(role_primary.individual.full_name, "Collector ForJanIndex_3")

        worker_individuals = ImportedIndividual.objects.filter(relationship="NON_BENEFICIARY")
        self.assertEqual(worker_individuals.count(), 2)
