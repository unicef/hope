from apps.household.models import Individual, Household, HEAD, COUSIN, BROTHER_SISTER
from apps.registration_data.fixtures import RegistrationDataImportFactory
from apps.registration_datahub.fixtures import RegistrationDataImportDatahubFactory, ImportedHouseholdFactory, \
    ImportedIndividualFactory
from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase

from freezegun import freeze_time


class TestRdiDiiaCreateTask(BaseElasticSearchTestCase):
    databases = "__all__"
    fixtures = [
        "hct_mis_api/apps/core/fixtures/data.json",
    ]

    @classmethod
    def setUpTestData(cls):
        from hct_mis_api.apps.registration_datahub.tasks.rdi_merge import RdiMergeTask

        cls.RdiMergeTask = RdiMergeTask

        cls.rdi = RegistrationDataImportFactory()
        rdi_hub = RegistrationDataImportDatahubFactory(
                name=cls.rdi.name, hct_id=cls.rdi.id, business_area_slug=cls.rdi.business_area.slug
            )
        cls.rdi.datahub_id = rdi_hub.id
        cls.rdi.save()

        imported_household = ImportedHouseholdFactory(
            registration_data_import=rdi_hub,
        )

        individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "relationship": HEAD,
                "birth_date": "1962-02-02",
                "sex": "MALE",
                "id": "47dd625a-e64e-48a9-bfcd-e970ca356bf7",
                "registration_data_import": rdi_hub,
                "household": imported_household,
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "relationship": COUSIN,
                "birth_date": "2012-02-15",  # age 9
                "sex": "MALE",
                "id": "f91eb18b-175a-495c-a49d-92af4ad554ba",
                "registration_data_import": rdi_hub,
                "household": imported_household,
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "relationship": COUSIN,
                "birth_date": "1983-12-21",
                "sex": "MALE",
                "id": "4174aa63-4d3d-416a-bf39-09bc0e14e7c6",
                "registration_data_import": rdi_hub,
                "household": imported_household,
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "relationship": BROTHER_SISTER,
                "birth_date": "1973-03-23",
                "sex": "MALE",
                "id": "6aada701-4639-4142-92ca-7cbf82411534",
                "registration_data_import": rdi_hub,
                "household": imported_household,
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "relationship": BROTHER_SISTER,
                "birth_date": "1969-11-29",
                "sex": "FEMALE",
                "id": "c38fa2a5-e518-495c-988f-c308c94dcc53",
                "registration_data_import": rdi_hub,
                "household": imported_household,
            },
        ]

        cls.individuals = [ImportedIndividualFactory(**individual) for individual in individuals_to_create]

    @freeze_time("2022-01-01")
    def test_merge_rdi_and_recalculation(self):
        self.RdiMergeTask().execute(self.rdi.pk)

        households = Household.objects.all()
        individuals = Individual.objects.all()


        self.assertEqual(3, households.count())
        self.assertEqual(5, individuals.count())