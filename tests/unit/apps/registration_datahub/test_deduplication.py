from django.conf import settings
from django.test import TestCase

import pytest

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.documents import get_individual_doc
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    FEMALE,
    HEAD,
    MALE,
    NEEDS_ADJUDICATION,
    SON_DAUGHTER,
    UNIQUE,
    WIFE_HUSBAND,
    Individual,
    PendingIndividual,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import (
    DUPLICATE_IN_BATCH,
    UNIQUE_IN_BATCH,
    ImportData,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.utils.elasticsearch_utils import (
    populate_index,
    rebuild_search_index,
)
from hct_mis_api.apps.utils.querysets import evaluate_qs
from tests.unit.conftest import disabled_locally_test

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@disabled_locally_test
class TestBatchDeduplication(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        import_data = ImportData.objects.create(
            file="test_file/x.xlsx",
            number_of_households=10,
            number_of_individuals=100,
        )
        cls.business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            has_data_sharing_agreement=True,
            deduplication_duplicate_score=14.0,
            deduplication_possible_duplicate_score=11.0,
            deduplication_batch_duplicates_percentage=100,
            deduplication_batch_duplicates_allowed=10,
            deduplication_golden_record_duplicates_percentage=100,
            deduplication_golden_record_duplicates_allowed=10,
        )
        cls.program = ProgramFactory(status="ACTIVE")
        cls.registration_data_import = RegistrationDataImportFactory(
            import_data=import_data,
            business_area=cls.business_area,
            program=cls.program,
        )

        registration_data_import_second = RegistrationDataImportFactory(
            business_area=cls.business_area, program=cls.program
        )
        (
            cls.household,
            cls.individuals,
        ) = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "program_id": cls.program.id,
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
                    "birth_date": "1955-09-04",
                    "program_id": cls.program.id,
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
                    "birth_date": "1957-10-10",
                    "program_id": cls.program.id,
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
                    "birth_date": "1996-12-12",
                    "program_id": cls.program.id,
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
                    "birth_date": "1997-07-07",
                    "program_id": cls.program.id,
                },
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
                    "birth_date": "1955-09-04",
                    "program_id": cls.program.id,
                },
                {
                    "registration_data_import": cls.registration_data_import,
                    "given_name": "Test",
                    "full_name": "Test Example",
                    "middle_name": "",
                    "family_name": "Example",
                    "phone_no": "432-125-765",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": MALE,
                    "birth_date": "1997-08-08",
                    "program_id": cls.program.id,
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
                    "birth_date": "1997-07-07",
                    "program_id": cls.program.id,
                },
            ],
        )

        create_household_and_individuals(
            household_data={
                "registration_data_import": registration_data_import_second,
                "business_area": cls.business_area,
                "program": registration_data_import_second.program,
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

        rebuild_search_index()

    def test_batch_deduplication(self) -> None:
        task = DeduplicateTask(self.business_area.slug, self.program.id)

        with self.assertNumQueries(11):
            task.deduplicate_pending_individuals(self.registration_data_import)
        duplicate_in_batch = PendingIndividual.objects.order_by("full_name").filter(
            deduplication_batch_status=DUPLICATE_IN_BATCH
        )
        unique_in_batch = PendingIndividual.objects.order_by("full_name").filter(
            deduplication_batch_status=UNIQUE_IN_BATCH
        )

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

        duplicate_in_golden_record = PendingIndividual.objects.order_by("full_name").filter(
            deduplication_golden_record_status=DUPLICATE
        )
        needs_adjudication_in_golden_record = PendingIndividual.objects.order_by("full_name").filter(
            deduplication_golden_record_status=NEEDS_ADJUDICATION
        )
        unique_in_golden_record = PendingIndividual.objects.order_by("full_name").filter(
            deduplication_golden_record_status=UNIQUE
        )

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

        expected_uniques_gr = ("Tesa Testowski",)

        self.assertEqual(
            tuple(duplicate_in_golden_record.values_list("full_name", flat=True)),
            expected_duplicates_gr,
        )
        self.assertEqual(
            tuple(unique_in_golden_record.values_list("full_name", flat=True)),
            expected_uniques_gr,
        )


@disabled_locally_test
class TestGoldenRecordDeduplication(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            deduplication_possible_duplicate_score=11.0,
            has_data_sharing_agreement=True,
        )
        cls.program = ProgramFactory(status="ACTIVE")
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.business_area, program=cls.program
        )
        registration_data_import_second = RegistrationDataImportFactory(
            business_area=cls.business_area, program=cls.program
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
                "program": cls.registration_data_import.program,
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
                    "phone_no": "453-85-423",
                    "phone_no_alternative": "",
                    "relationship": WIFE_HUSBAND,
                    "sex": FEMALE,
                    "birth_date": "1955-09-05",
                },
                {
                    "registration_data_import": cls.registration_data_import,
                    "given_name": "Example",
                    "full_name": "Example Example",
                    "middle_name": "",
                    "family_name": "Example",
                    "phone_no": "934-25-25-121",
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
                    "phone_no": "363-224-112",
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
                "business_area": cls.business_area,
                "program": registration_data_import_second.program,
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
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "363-224-112",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": FEMALE,
                    "birth_date": "1989-09-10",
                },
            ],
        )
        rebuild_search_index()

    def test_golden_record_deduplication(self) -> None:
        task = DeduplicateTask(self.business_area.slug, self.program.id)
        individuals = evaluate_qs(
            Individual.objects.filter(registration_data_import=self.registration_data_import)
            .select_for_update()
            .order_by("pk")
        )
        populate_index(individuals, get_individual_doc(self.business_area.slug))

        with self.assertNumQueries(4):
            task.deduplicate_individuals_against_population(individuals)
        needs_adjudication = Individual.objects.filter(deduplication_golden_record_status=NEEDS_ADJUDICATION)
        duplicate = Individual.objects.filter(deduplication_golden_record_status=DUPLICATE)

        self.assertEqual(needs_adjudication.count(), 0)
        self.assertEqual(duplicate.count(), 4)

    def test_deduplicate_individuals_from_other_source(self) -> None:
        task = DeduplicateTask(self.business_area.slug, self.program.id)
        individuals = evaluate_qs(
            Individual.objects.filter(registration_data_import=self.registration_data_import)
            .select_for_update()
            .order_by("pk")
        )
        populate_index(individuals, get_individual_doc(self.business_area.slug))

        with self.assertNumQueries(4):
            task.deduplicate_individuals_from_other_source(individuals)
        needs_adjudication = Individual.objects.filter(deduplication_golden_record_status=NEEDS_ADJUDICATION)
        duplicate = Individual.objects.filter(deduplication_golden_record_status=DUPLICATE)

        self.assertEqual(needs_adjudication.count(), 0)
        self.assertEqual(duplicate.count(), 2)
