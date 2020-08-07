from django.core.management import call_command

from core.base_test_case import BaseElasticSearchTestCase
from household.models import HEAD, WIFE_HUSBAND, SON_DAUGHTER, MALE, FEMALE
from registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
    ImportedHouseholdFactory,
    ImportedIndividualFactory,
)
from registration_datahub.models import ImportData
from registration_datahub.tasks.batch_deduplicate import BatchDeduplicate


class TestBatchDeduplicate(BaseElasticSearchTestCase):
    multi_db = True

    @staticmethod
    def _create_household_and_individuals(
        household_data=None, individuals_data=None
    ):
        if household_data is None:
            household_data = {}
        if individuals_data is None:
            individuals_data = {}
        household = ImportedHouseholdFactory.build(
            **household_data, size=len(individuals_data)
        )
        individuals = [
            ImportedIndividualFactory(household=household, **individual_data)
            for individual_data in individuals_data
        ]
        household.head_of_household = individuals[0]
        household.save()
        return household, individuals

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        import_data = ImportData.objects.create(
            file="test_file/new_reg_data_import.xlsx",
            number_of_households=10,
            number_of_individuals=100,
        )
        cls.registration_data_import_datahub = RegistrationDataImportDatahubFactory(
            import_data=import_data
        )
        import_data_second = ImportData.objects.create(
            file="test_file/new_reg_data_import.xlsx",
            number_of_households=1,
            number_of_individuals=3,
        )
        registration_data_import_datahub_second = RegistrationDataImportDatahubFactory(
            import_data=import_data_second
        )
        cls.household, cls.individuals = cls._create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import_datahub,
            },
            individuals_data=[
                {
                    "registration_data_import": cls.registration_data_import_datahub,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                },
                {
                    "registration_data_import": cls.registration_data_import_datahub,
                    "given_name": "Tesa",
                    "full_name": "Tesa Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": WIFE_HUSBAND,
                    "sex": FEMALE,
                },
                {
                    "registration_data_import": cls.registration_data_import_datahub,
                    "given_name": "Tescik",
                    "full_name": "Tescik Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": MALE,
                },
                {
                    "registration_data_import": cls.registration_data_import_datahub,
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": FEMALE,
                },
            ],
        )
        cls._create_household_and_individuals(
            household_data={
                "registration_data_import": registration_data_import_datahub_second,
            },
            individuals_data=[
                {
                    "registration_data_import": registration_data_import_datahub_second,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                },
                {
                    "registration_data_import": registration_data_import_datahub_second,
                    "given_name": "Test",
                    "full_name": "Test Example",
                    "middle_name": "",
                    "family_name": "Test Example",
                    "phone_no": "432-125-765",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": MALE,
                },
                {
                    "registration_data_import": registration_data_import_datahub_second,
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": FEMALE,
                },
            ],
        )
        call_command("search_index", "--rebuild", "-f")

    def test_deduplicate(self):
        task = BatchDeduplicate(
            registration_data_import_datahub=self.registration_data_import_datahub
        )
        task.deduplicate()
