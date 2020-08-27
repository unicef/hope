from constance.test import override_config
from django.core.management import call_command

from core.base_test_case import BaseElasticSearchTestCase
from core.models import BusinessArea
from household.fixtures import create_household_and_individuals
from household.models import (
    HEAD,
    WIFE_HUSBAND,
    SON_DAUGHTER,
    MALE,
    FEMALE,
    Individual,
    NEEDS_ADJUDICATION,
    DUPLICATE,
    UNIQUE,
)
from registration_data.fixtures import RegistrationDataImportFactory
from registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
    create_imported_household_and_individuals,
)
from registration_datahub.models import (
    ImportData,
    ImportedIndividual,
    DUPLICATE_IN_BATCH,
    UNIQUE_IN_BATCH,
)
from registration_datahub.tasks.deduplicate import DeduplicateTask


@override_config(
    DEDUPLICATION_BATCH_DUPLICATE_SCORE=4.0,
    DEDUPLICATION_BATCH_MIN_SCORE=3.7,
    DEDUPLICATION_GOLDEN_RECORD_MIN_SCORE=4.0,
    DEDUPLICATION_GOLDEN_RECORD_DUPLICATE_SCORE=7.0,
    DEDUPLICATION_BATCH_DUPLICATES_PERCENTAGE=100,
    DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_PERCENTAGE=100,
)
class TestBatchDeduplication(BaseElasticSearchTestCase):
    multi_db = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        import_data = ImportData.objects.create(
            file="test_file/new_reg_data_import.xlsx",
            number_of_households=10,
            number_of_individuals=100,
        )
        business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            has_data_sharing_agreement=True,
        )
        cls.registration_data_import_datahub = RegistrationDataImportDatahubFactory(
            import_data=import_data
        )
        rdi = RegistrationDataImportFactory(
            datahub_id=cls.registration_data_import_datahub.id
        )
        cls.registration_data_import_datahub.hct_id = rdi.id
        cls.registration_data_import_datahub.save()

        registration_data_import_second = RegistrationDataImportFactory()
        (
            cls.household,
            cls.individuals,
        ) = create_imported_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import_datahub,
            },
            individuals_data=[
                {
                    # DUPLICATE
                    "registration_data_import": cls.registration_data_import_datahub,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": "1955-09-04",
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
                    "birth_date": "1957-10-10",
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
                    "birth_date": "1996-12-12",
                },
                {
                    # DUPLICATE
                    "registration_data_import": cls.registration_data_import_datahub,
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": FEMALE,
                    "birth_date": "1997-07-07",
                },
                {
                    # DUPLICATE
                    "registration_data_import": cls.registration_data_import_datahub,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": "1955-09-04",
                },
                {
                    "registration_data_import": cls.registration_data_import_datahub,
                    "given_name": "Test",
                    "full_name": "Test Example",
                    "middle_name": "",
                    "family_name": "Example",
                    "phone_no": "432-125-765",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": MALE,
                    "birth_date": "1997-08-08",
                },
                {
                    # DUPLICATE
                    "registration_data_import": cls.registration_data_import_datahub,
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": FEMALE,
                    "birth_date": "1997-07-07",
                },
            ],
        )

        create_household_and_individuals(
            household_data={
                "registration_data_import": registration_data_import_second,
                "business_area": business_area,
            },
            individuals_data=[
                {
                    "registration_data_import": registration_data_import_second,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": "1955-09-04",
                },
                {
                    "registration_data_import": registration_data_import_second,
                    "given_name": "Test",
                    "full_name": "Test Example",
                    "middle_name": "",
                    "family_name": "Example",
                    "phone_no": "432-125-765",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": MALE,
                    "birth_date": "1997-08-08",
                },
                {
                    "registration_data_import": registration_data_import_second,
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": FEMALE,
                    "birth_date": "1997-07-07",
                },
                {
                    "registration_data_import": registration_data_import_second,
                    "given_name": "Tescik",
                    "full_name": "Tescik Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "666-777-888",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": MALE,
                    "birth_date": "1996-12-12",
                },
            ],
        )

        cls.rebuild_search_index()

    def test_batch_deduplication(self):
        task = DeduplicateTask()
        task.deduplicate_imported_individuals(
            self.registration_data_import_datahub
        )
        duplicate_in_batch = ImportedIndividual.objects.order_by(
            "full_name"
        ).filter(deduplication_batch_status=DUPLICATE_IN_BATCH)
        unique_in_batch = ImportedIndividual.objects.order_by(
            "full_name"
        ).filter(deduplication_batch_status=UNIQUE_IN_BATCH)

        self.assertEqual(duplicate_in_batch.count(), 4)
        self.assertEqual(unique_in_batch.count(), 3)

        expected_duplicates = (
            "Tessta Testowski",
            "Tessta Testowski",
            "Test Testowski",
            "Test Testowski",
        )
        expected_uniques = (
            "Tesa Testowski",
            "Tescik Testowski",
            "Test Example",
        )
        self.assertEqual(
            tuple(duplicate_in_batch.values_list("full_name", flat=True)),
            expected_duplicates,
        )
        self.assertEqual(
            tuple(unique_in_batch.values_list("full_name", flat=True)),
            expected_uniques,
        )

        duplicate_in_golden_record = ImportedIndividual.objects.order_by(
            "full_name"
        ).filter(deduplication_golden_record_status=DUPLICATE)
        needs_adjudication_in_golden_record = ImportedIndividual.objects.order_by(
            "full_name"
        ).filter(
            deduplication_golden_record_status=NEEDS_ADJUDICATION
        )
        unique_in_golden_record = ImportedIndividual.objects.order_by(
            "full_name"
        ).filter(deduplication_golden_record_status=UNIQUE)

        self.assertEqual(duplicate_in_golden_record.count(), 5)
        self.assertEqual(unique_in_golden_record.count(), 1)
        self.assertEqual(needs_adjudication_in_golden_record.count(), 1)

        expected_duplicates_gr = (
            "Tessta Testowski",
            "Tessta Testowski",
            "Test Example",
            "Test Testowski",
            "Test Testowski",
        )
        expected_needs_adjudication_gr = ("Tescik Testowski",)
        expected_uniques_gr = ("Tesa Testowski",)

        self.assertEqual(
            tuple(
                duplicate_in_golden_record.values_list("full_name", flat=True)
            ),
            expected_duplicates_gr,
        )
        self.assertEqual(
            tuple(
                needs_adjudication_in_golden_record.values_list(
                    "full_name", flat=True
                )
            ),
            expected_needs_adjudication_gr,
        )
        self.assertEqual(
            tuple(unique_in_golden_record.values_list("full_name", flat=True)),
            expected_uniques_gr,
        )


@override_config(
    DEDUPLICATION_GOLDEN_RECORD_MIN_SCORE=4.0,
    DEDUPLICATION_GOLDEN_RECORD_DUPLICATE_SCORE=7.0,
)
class TestGoldenRecordDeduplication(BaseElasticSearchTestCase):
    multi_db = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.registration_data_import = RegistrationDataImportFactory()
        registration_data_import_second = RegistrationDataImportFactory()
        business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            has_data_sharing_agreement=True,
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": business_area,
            },
            individuals_data=[
                {
                    "registration_data_import": cls.registration_data_import,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": "1955-09-07",
                },
                {
                    "registration_data_import": cls.registration_data_import,
                    "given_name": "Tesa",
                    "full_name": "Tesa Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": WIFE_HUSBAND,
                    "sex": FEMALE,
                    "birth_date": "1955-09-05",
                },
                {
                    "registration_data_import": cls.registration_data_import,
                    "given_name": "Tescik",
                    "full_name": "Tescik Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": MALE,
                    "birth_date": "1985-08-12",
                },
                {
                    "registration_data_import": cls.registration_data_import,
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": FEMALE,
                    "birth_date": "1989-09-10",
                },
            ],
        )
        create_household_and_individuals(
            household_data={
                "registration_data_import": registration_data_import_second,
                "business_area": business_area,
            },
            individuals_data=[
                {
                    "registration_data_import": registration_data_import_second,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": "1955-09-07",
                },
                {
                    "registration_data_import": registration_data_import_second,
                    "given_name": "Test",
                    "full_name": "Test Example",
                    "middle_name": "",
                    "family_name": "Test Example",
                    "phone_no": "432-125-765",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": MALE,
                    "birth_date": "1999-10-10",
                },
                {
                    "registration_data_import": registration_data_import_second,
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": FEMALE,
                    "birth_date": "1989-09-10",
                },
            ],
        )
        cls.rebuild_search_index()

    def test_golden_record_deduplication(self):
        task = DeduplicateTask()
        task.deduplicate_individuals(self.registration_data_import)
        needs_adjudication = Individual.objects.filter(
            deduplication_status=NEEDS_ADJUDICATION
        )
        duplicate = Individual.objects.filter(deduplication_status=DUPLICATE)

        self.assertEqual(needs_adjudication.count(), 0)
        self.assertEqual(duplicate.count(), 2)
