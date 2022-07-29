from constance.test import override_config
from django.db import DEFAULT_DB_ALIAS, connections
from django.test.utils import CaptureQueriesContext

from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    FEMALE,
    HEAD,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    MALE,
    NEEDS_ADJUDICATION,
    SON_DAUGHTER,
    UNIQUE,
    WIFE_HUSBAND,
    Document,
    DocumentType,
    Individual,
    IDENTIFICATION_TYPE_TAX_ID,
)
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_datahub.fixtures import (
    RegistrationDataImportDatahubFactory,
    create_imported_household_and_individuals,
)
from hct_mis_api.apps.registration_datahub.models import (
    DUPLICATE_IN_BATCH,
    UNIQUE_IN_BATCH,
    ImportData,
    ImportedIndividual,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask


class TestGoldenRecordDeduplication(BaseElasticSearchTestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            has_data_sharing_agreement=True,
        )
        cls.registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
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
            ],
        )
        dt = DocumentType(country="PL", label=IDENTIFICATION_TYPE_NATIONAL_ID, type=IDENTIFICATION_TYPE_NATIONAL_ID)
        dt_tax_id = DocumentType.objects.create(
            country="PL", label=IDENTIFICATION_TYPE_TAX_ID, type=IDENTIFICATION_TYPE_TAX_ID
        )
        dt.save()
        cls.document1 = Document(
            type=dt, document_number="ASD123", individual=cls.individuals[0], status=Document.STATUS_VALID
        )
        cls.document2 = Document(type=dt, document_number="ASD123", individual=cls.individuals[1])
        cls.document3 = Document(type=dt, document_number="BBC999", individual=cls.individuals[2])
        cls.document4 = Document(type=dt, document_number="ASD123", individual=cls.individuals[3])
        cls.document5 = Document(
            type=dt, document_number="TOTALY UNIQ", individual=cls.individuals[4], status=Document.STATUS_VALID
        )
        cls.document6 = Document.objects.create(
            type=dt_tax_id, document_number="ASD123", individual=cls.individuals[2], status=Document.STATUS_VALID
        )
        cls.document7 = Document.objects.create(
            type=dt,
            document_number="ASD123",
            individual=cls.individuals[1],
        )

        cls.document1.save()
        cls.document2.save()
        cls.document3.save()
        cls.document4.save()
        cls.document5.save()
        cls.all_documents = [
            cls.document1,
            cls.document2,
            cls.document3,
            cls.document4,
            cls.document5,
            cls.document6,
            cls.document7,
        ]

    def refresh_all_documents(self):
        for document in self.all_documents:
            document.refresh_from_db()

    def test_hard_documents_deduplication(self):
        DeduplicateTask.hard_deduplicate_documents((self.document2, self.document3, self.document4))
        self.refresh_all_documents()
        self.assertEqual(self.document1.status, Document.STATUS_VALID)
        self.assertEqual(self.document2.status, Document.STATUS_NEED_INVESTIGATION)
        self.assertEqual(self.document3.status, Document.STATUS_VALID)
        self.assertEqual(self.document4.status, Document.STATUS_NEED_INVESTIGATION)
        self.assertEqual(GrievanceTicket.objects.count(), 1)
        ticket_details = GrievanceTicket.objects.first().needs_adjudication_ticket_details
        self.assertEqual(ticket_details.possible_duplicates.count(), 2)
        self.assertEqual(ticket_details.is_multiple_duplicates_version, True)

    def test_hard_documents_deduplication_for_initially_valid(self):
        DeduplicateTask.hard_deduplicate_documents((self.document5,))
        self.refresh_all_documents()
        self.assertEqual(self.document5.status, Document.STATUS_VALID)
        self.assertEqual(GrievanceTicket.objects.count(), 0)

    def test_hard_documents_deduplication_number_of_queries(self):
        context = CaptureQueriesContext(connection=connections[DEFAULT_DB_ALIAS])
        with context:
            DeduplicateTask.hard_deduplicate_documents((self.document2, self.document3, self.document4, self.document5))
            first_dedup_query_count = len(context.captured_queries)
            DeduplicateTask.hard_deduplicate_documents(
                (self.document2, self.document3, self.document4, self.document5, self.document7),
                self.registration_data_import,
            )
            second_dedup_query_count = len(context.captured_queries) - first_dedup_query_count
            self.assertEqual(
                first_dedup_query_count, second_dedup_query_count, "Both queries should use same amount of queries"
            )
            self.assertEqual(first_dedup_query_count, 6, "Should only use 6 queries")

    def test_ticket_created_correctly(self):
        DeduplicateTask.hard_deduplicate_documents((self.document2, self.document3, self.document4, self.document5))
        self.refresh_all_documents()

        self.assertEqual(GrievanceTicket.objects.count(), 1)
        DeduplicateTask.hard_deduplicate_documents(
            (self.document7,),
            self.registration_data_import,
        )
        self.assertEqual(GrievanceTicket.objects.count(), 1)
