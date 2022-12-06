from typing import List

from django.db import DEFAULT_DB_ALIAS, connections
from django.db.models import QuerySet
from django.test.utils import CaptureQueriesContext

from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import (
    DocumentTypeFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    FEMALE,
    HEAD,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_TAX_ID,
    MALE,
    SON_DAUGHTER,
    WIFE_HUSBAND,
    Document,
)
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask


class TestGoldenRecordDeduplication(BaseElasticSearchTestCase):
    databases = "__all__"
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls):
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
        country = geo_models.Country.objects.get(iso_code2="PL")
        dt = DocumentTypeFactory(label=IDENTIFICATION_TYPE_NATIONAL_ID, type=IDENTIFICATION_TYPE_NATIONAL_ID)
        dt_tax_id = DocumentTypeFactory(label=IDENTIFICATION_TYPE_TAX_ID, type=IDENTIFICATION_TYPE_TAX_ID)
        dt.save()
        cls.document1 = Document(
            country=country,
            type=dt,
            document_number="ASD123",
            individual=cls.individuals[0],
            status=Document.STATUS_VALID,
        )
        cls.document2 = Document(type=dt, document_number="ASD123", individual=cls.individuals[1], country=country)
        cls.document3 = Document(type=dt, document_number="BBC999", individual=cls.individuals[2], country=country)
        cls.document4 = Document(type=dt, document_number="ASD123", individual=cls.individuals[3], country=country)
        cls.document5 = Document(
            country=country,
            type=dt,
            document_number="TOTALY UNIQ",
            individual=cls.individuals[4],
            status=Document.STATUS_VALID,
        )
        cls.document6 = Document.objects.create(
            country=country,
            type=dt_tax_id,
            document_number="ASD123",
            individual=cls.individuals[2],
            status=Document.STATUS_VALID,
        )
        cls.document7 = Document.objects.create(
            country=country,
            type=dt,
            document_number="ASD123",
            individual=cls.individuals[1],
        )
        cls.document8 = Document.objects.create(
            country=country,
            type=dt,
            document_number="ASD123",
            individual=cls.individuals[4],
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
        super().setUpTestData()

    def get_documents_query(self, documents: List[Document]) -> QuerySet[Document]:
        return Document.objects.filter(id__in=[document.id for document in documents])

    def refresh_all_documents(self):
        for document in self.all_documents:
            document.refresh_from_db()

    def test_hard_documents_deduplication(self):
        DeduplicateTask.hard_deduplicate_documents(
            self.get_documents_query([self.document2, self.document3, self.document4])
        )
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
        DeduplicateTask.hard_deduplicate_documents(
            self.get_documents_query(
                [
                    self.document5,
                ]
            )
        )
        self.refresh_all_documents()
        self.assertEqual(self.document5.status, Document.STATUS_VALID)
        self.assertEqual(GrievanceTicket.objects.count(), 0)

    def test_should_create_one_ticket(self):
        DeduplicateTask.hard_deduplicate_documents(
            self.get_documents_query([self.document2, self.document3, self.document4])
        )
        DeduplicateTask.hard_deduplicate_documents(
            self.get_documents_query([self.document2, self.document3, self.document4])
        )
        self.assertEqual(GrievanceTicket.objects.count(), 1)

    def test_hard_documents_deduplication_number_of_queries(self):
        documents1 = self.get_documents_query([self.document2, self.document3, self.document4, self.document5])
        documents2 = self.get_documents_query(
            [self.document2, self.document3, self.document4, self.document5, self.document7, self.document8]
        )
        context = CaptureQueriesContext(connection=connections[DEFAULT_DB_ALIAS])
        with context:
            DeduplicateTask.hard_deduplicate_documents(documents1)
            first_dedup_query_count = len(context.captured_queries)
            DeduplicateTask.hard_deduplicate_documents(documents2, self.registration_data_import)
            second_dedup_query_count = len(context.captured_queries) - first_dedup_query_count
            self.assertEqual(
                first_dedup_query_count, second_dedup_query_count, "Both queries should use same amount of queries"
            )

            # Queries:
            # 1. Transaction savepoint
            # 2. Select for update: Documents, Individuals
            # 3. Filter all_matching_number_documents
            # 4. Update Documents.status
            # 5. Filter PossibleDuplicateThrough
            # 6. Bulk Create GrievanceTicket
            # 7. Bulk Create TicketNeedsAdjudicationDetails
            # 8. Bulk Create PossibleDuplicateThrough
            # 9. Transaction savepoint release
            self.assertEqual(first_dedup_query_count, 9, "Should only use 9 queries")

    def test_ticket_created_correctly(self):
        DeduplicateTask.hard_deduplicate_documents(
            self.get_documents_query([self.document2, self.document3, self.document4, self.document5])
        )
        self.refresh_all_documents()

        self.assertEqual(GrievanceTicket.objects.count(), 1)
        DeduplicateTask.hard_deduplicate_documents(
            self.get_documents_query(
                [
                    self.document7,
                ]
            ),
            self.registration_data_import,
        )
        self.assertEqual(GrievanceTicket.objects.count(), 1)
