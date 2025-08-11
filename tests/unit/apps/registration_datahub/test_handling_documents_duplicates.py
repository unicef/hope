from typing import List

from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.models import QuerySet
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

import pytest
from extras.test_utils.factories.household import (
    DocumentTypeFactory,
    create_household_and_individuals,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

from hope.apps.core.models import BusinessArea
from hope.apps.geo import models as geo_models
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hope.apps.household.models import (
    FEMALE,
    HEAD,
    MALE,
    SON_DAUGHTER,
    WIFE_HUSBAND,
    Document,
    DocumentType,
)
from hope.apps.registration_datahub.tasks.deduplicate import (
    HardDocumentDeduplication,
)
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestGoldenRecordDeduplication(TestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init-geo-fixtures")
        cls.business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            has_data_sharing_agreement=True,
        )
        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.business_area, program=cls.program
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
                "program": cls.program,
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
                {
                    "registration_data_import": cls.registration_data_import,
                    "given_name": "Example",
                    "full_name": "Example Example",
                    "middle_name": "",
                    "family_name": "Example",
                    "phone_no": "123-45-67-899",
                    "phone_no_alternative": "",
                    "relationship": SON_DAUGHTER,
                    "sex": MALE,
                    "birth_date": "1985-08-12",
                },
            ],
        )
        cls.country = geo_models.Country.objects.get(iso_code2="PL")
        cls.dt = DocumentTypeFactory(label="national_id", key="national_id", valid_for_deduplication=False)
        cls.dt_tax_id = DocumentTypeFactory(label="tax_id", key="tax_id", valid_for_deduplication=False)

        cls.document1 = Document.objects.create(
            country=cls.country,
            type=cls.dt,
            document_number="ASD123",
            individual=cls.individuals[0],
            status=Document.STATUS_VALID,
            program=cls.individuals[0].program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.document2 = Document.objects.create(
            type=cls.dt,
            document_number="ASD123",
            individual=cls.individuals[1],
            country=cls.country,
            program=cls.individuals[1].program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.document3 = Document.objects.create(
            type=cls.dt,
            document_number="BBC999",
            individual=cls.individuals[2],
            country=cls.country,
            program=cls.individuals[2].program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.document4 = Document.objects.create(
            type=cls.dt,
            document_number="ASD123",
            individual=cls.individuals[3],
            country=cls.country,
            program=cls.individuals[3].program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.document5 = Document.objects.create(
            country=cls.country,
            type=cls.dt,
            document_number="TOTALY UNIQ",
            individual=cls.individuals[4],
            status=Document.STATUS_VALID,
            program=cls.individuals[4].program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.document6 = Document.objects.create(
            country=cls.country,
            type=cls.dt_tax_id,
            document_number="ASD123",
            individual=cls.individuals[2],
            status=Document.STATUS_VALID,
            program=cls.individuals[2].program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.document7 = Document.objects.create(
            country=cls.country,
            type=cls.dt,
            document_number="ASD123",
            individual=cls.individuals[1],
            program=cls.individuals[1].program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.document8 = Document.objects.create(
            country=cls.country,
            type=cls.dt,
            document_number="ASD123",
            individual=cls.individuals[4],
            program=cls.individuals[4].program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.document9 = Document.objects.create(
            country=cls.country,
            type=cls.dt,
            document_number="UNIQ",
            individual=cls.individuals[5],
            program=cls.individuals[5].program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.all_documents = [
            cls.document1,
            cls.document2,
            cls.document3,
            cls.document4,
            cls.document5,
            cls.document6,
            cls.document7,
            cls.document8,
            cls.document9,
        ]
        rebuild_search_index()

    def get_documents_query(self, documents: List[Document]) -> QuerySet[Document]:
        return Document.objects.filter(id__in=[document.id for document in documents])

    def refresh_all_documents(self) -> None:
        for document in self.all_documents:
            document.refresh_from_db()

    def test_hard_documents_deduplication(self) -> None:
        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([self.document2, self.document3, self.document4]), self.registration_data_import
        )
        self.refresh_all_documents()
        self.assertEqual(self.document1.status, Document.STATUS_VALID)
        self.assertEqual(self.document2.status, Document.STATUS_NEED_INVESTIGATION)
        self.assertEqual(self.document3.status, Document.STATUS_VALID)
        self.assertEqual(self.document4.status, Document.STATUS_NEED_INVESTIGATION)
        self.assertEqual(GrievanceTicket.objects.count(), 1)
        grievance_ticket = GrievanceTicket.objects.first()
        self.assertEqual(grievance_ticket.programs.count(), 1)
        self.assertEqual(grievance_ticket.programs.first().id, self.program.id)
        ticket_details = GrievanceTicket.objects.first().needs_adjudication_ticket_details
        self.assertEqual(ticket_details.possible_duplicates.count(), 2)
        self.assertEqual(ticket_details.is_multiple_duplicates_version, True)

        self.household.refresh_from_db()
        self.assertEqual(GrievanceTicket.objects.first().household_unicef_id, self.household.unicef_id)

    def test_hard_documents_deduplication_for_initially_valid(self) -> None:
        HardDocumentDeduplication().deduplicate(
            self.get_documents_query(
                [
                    self.document5,
                ]
            ),
            self.registration_data_import,
        )
        self.refresh_all_documents()
        self.assertEqual(self.document5.status, Document.STATUS_VALID)
        self.assertEqual(GrievanceTicket.objects.count(), 0)

    def test_should_create_one_ticket(self) -> None:
        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([self.document2, self.document3, self.document4]), self.registration_data_import
        )
        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([self.document2, self.document3, self.document4]), self.registration_data_import
        )
        self.assertEqual(GrievanceTicket.objects.count(), 1)

    def test_hard_documents_deduplication_number_of_queries(self) -> None:
        documents1 = self.get_documents_query([self.document2, self.document3, self.document4, self.document5])
        documents2 = self.get_documents_query(
            [self.document2, self.document3, self.document4, self.document5, self.document7, self.document8]
        )
        context = CaptureQueriesContext(connection=connections[DEFAULT_DB_ALIAS])
        with context:
            HardDocumentDeduplication().deduplicate(documents1, self.registration_data_import)
            first_dedup_query_count = len(context.captured_queries)
            HardDocumentDeduplication().deduplicate(documents2, self.registration_data_import)
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
            # 7. Bulk Create GrievanceTicketProgramThrough
            # 8. Bulk Create TicketNeedsAdjudicationDetails
            # 9. Bulk Create PossibleDuplicateThrough
            # 10. Transaction savepoint release
            # 11 - 13. Queries for `is_cross_area` update
            self.assertEqual(first_dedup_query_count, 13, "Should only use 14 queries")

    def test_ticket_created_correctly(self) -> None:
        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([self.document2, self.document3, self.document4, self.document5]),
            self.registration_data_import,
        )
        self.refresh_all_documents()

        self.assertEqual(GrievanceTicket.objects.all().count(), 1)

        HardDocumentDeduplication().deduplicate(
            self.get_documents_query(
                [
                    self.document7,
                ]
            ),
            self.registration_data_import,
        )
        # failed probably because of all_matching_number_documents qs ordering
        self.assertEqual(GrievanceTicket.objects.all().count(), 1)
        grievance_ticket = GrievanceTicket.objects.first()
        self.assertEqual(grievance_ticket.programs.count(), 1)
        self.assertEqual(grievance_ticket.programs.first().id, self.program.id)

    def test_valid_for_deduplication_doc_type(self) -> None:
        dt_tax_id = DocumentType.objects.get(key="tax_id")
        dt_national_id = DocumentType.objects.get(key="national_id")
        Document.objects.create(
            country=self.country,
            type=dt_tax_id,
            document_number="TAX_ID_DOC_123",
            individual=self.individuals[2],
            status=Document.STATUS_VALID,
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        doc_national_id_1 = Document.objects.create(
            country=self.country,
            type=dt_national_id,
            document_number="TAX_ID_DOC_123",  # the same doc number
            individual=self.individuals[2],
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        doc_national_id_2 = Document.objects.create(
            country=self.country,
            type=dt_national_id,
            document_number="TAX_ID_DOC_123",  # the same doc number
            individual=self.individuals[2],
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([doc_national_id_1]), self.registration_data_import
        )
        doc_national_id_1.refresh_from_db()
        self.assertEqual(doc_national_id_1.status, Document.STATUS_NEED_INVESTIGATION)

        dt_national_id.valid_for_deduplication = True
        dt_national_id.save()

        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([doc_national_id_2]), self.registration_data_import
        )
        doc_national_id_2.refresh_from_db()
        self.assertEqual(doc_national_id_2.status, Document.STATUS_VALID)

    def test_hard_documents_deduplication_for_invalid_document(self) -> None:
        self.individuals[5].withdraw()
        self.document9.refresh_from_db()
        self.assertEqual(self.document9.status, Document.STATUS_INVALID)
        HardDocumentDeduplication().deduplicate(
            self.get_documents_query(
                [
                    self.document9,
                ]
            ),
            self.registration_data_import,
        )
        self.document9.refresh_from_db()
        self.assertEqual(self.document9.status, Document.STATUS_INVALID)

    def test_hard_documents_deduplication_for_the_diff_program(self) -> None:
        program_2 = ProgramFactory(business_area=self.business_area)

        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": self.registration_data_import,
                "business_area": self.business_area,
                "program": program_2,
            },
            individuals_data=[
                {
                    "registration_data_import": self.registration_data_import,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": "1955-09-07",
                }
            ],
        )
        individual = individuals[0]
        new_document_from_other_program = Document.objects.create(
            country=geo_models.Country.objects.get(iso_code2="PL"),
            type=DocumentType.objects.get(key="national_id"),
            document_number="ASD123",
            individual=individual,
            status=Document.STATUS_PENDING,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        individual.refresh_from_db()
        self.assertEqual(str(individual.program_id), str(program_2.pk))
        new_document_from_other_program.refresh_from_db()
        self.assertEqual(new_document_from_other_program.status, Document.STATUS_PENDING)

        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([new_document_from_other_program]), self.registration_data_import
        )
        new_document_from_other_program.refresh_from_db()
        self.assertEqual(new_document_from_other_program.status, Document.STATUS_VALID)

    def test_ticket_creation_for_the_same_ind_doc_numbers(self) -> None:
        passport = Document.objects.create(
            country=self.country,  # the same country
            type=self.dt,
            document_number="111",  # the same doc number
            individual=self.individuals[2],  # the same Individual
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        tax_id = Document.objects.create(
            country=self.country,  # the same country
            type=self.dt_tax_id,
            document_number="111",  # the same doc number
            individual=self.individuals[2],  # the same Individual
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        d1 = Document.objects.create(
            country=self.country,
            type=self.dt,
            document_number="222",
            individual=self.individuals[2],
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        # add more docs just to have coverage 95% XD
        Document.objects.create(
            country=self.country,
            type=self.dt,
            document_number="222",
            individual=self.individuals[1],
            program=self.program,
            status=Document.STATUS_VALID,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        d2 = Document.objects.create(
            country=self.country,
            type=self.dt,
            document_number="333",
            individual=self.individuals[3],
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        d3 = Document.objects.create(
            country=self.country,
            type=self.dt_tax_id,
            document_number="333",
            individual=self.individuals[4],
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        d4 = Document.objects.create(
            country=self.country,
            type=self.dt,
            document_number="444",
            individual=self.individuals[0],
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        d5 = Document.objects.create(
            country=self.country,
            type=self.dt_tax_id,
            document_number="444",
            individual=self.individuals[1],
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        d6 = Document.objects.create(
            country=self.country,
            type=DocumentTypeFactory(label="other_type", key="other_type"),
            document_number="444",
            individual=self.individuals[2],
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        self.assertEqual(GrievanceTicket.objects.all().count(), 0)
        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([passport, tax_id, d1, d2, d3, d4, d5, d6]),
            self.registration_data_import,
        )

        self.assertEqual(GrievanceTicket.objects.all().count(), 3)

        passport.refresh_from_db()
        self.assertEqual(passport.status, Document.STATUS_VALID)

        tax_id.refresh_from_db()
        self.assertEqual(tax_id.status, Document.STATUS_VALID)

    def test_ticket_creation_for_the_same_ind_and_across_other_inds_doc_numbers(self) -> None:
        passport = Document.objects.create(
            country=self.country,  # the same country
            type=self.dt,
            document_number="111",  # the same doc number
            individual=self.individuals[2],  # the same Individual
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        tax_id = Document.objects.create(
            country=self.country,  # the same country
            type=self.dt_tax_id,
            document_number="111",  # the same doc number
            individual=self.individuals[2],  # the same Individual
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        d1 = Document.objects.create(
            country=self.country,
            type=self.dt,
            document_number="222",  # different doc number
            individual=self.individuals[2],  # different Individual
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        d2 = Document.objects.create(
            country=self.country,
            type=self.dt,
            document_number="111",  # the same doc number
            individual=self.individuals[3],  # different Individual
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        self.assertEqual(GrievanceTicket.objects.all().count(), 0)
        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([passport, tax_id, d1, d2]),
            self.registration_data_import,
        )

        self.assertEqual(GrievanceTicket.objects.all().count(), 1)
        ticket_details = TicketNeedsAdjudicationDetails.objects.first()
        self.assertIsNotNone(ticket_details.golden_records_individual)
        self.assertEqual(ticket_details.possible_duplicates.all().count(), 1)
        self.assertNotEqual(ticket_details.golden_records_individual, ticket_details.possible_duplicates.first())

        passport.refresh_from_db()
        self.assertEqual(passport.status, Document.STATUS_VALID)
        tax_id.refresh_from_db()
        self.assertEqual(tax_id.status, Document.STATUS_VALID)
        d2.refresh_from_db()
        self.assertEqual(d2.status, Document.STATUS_NEED_INVESTIGATION)

    def test_ticket_creation_for_the_same_ind_doc_numbers_same_doc_type(self) -> None:
        Document.objects.all().delete()
        passport = Document.objects.create(
            country=self.country,  # the same country
            type=self.dt,
            document_number="111",  # the same doc number
            individual=self.individuals[2],  # the same Individual
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        passport2 = Document.objects.create(
            country=self.country,  # the same country
            type=self.dt,
            document_number="111",  # the same doc number
            individual=self.individuals[2],  # the same Individual
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        d1 = Document.objects.create(
            country=self.country,
            type=self.dt,
            document_number="222",
            individual=self.individuals[1],
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        self.assertEqual(GrievanceTicket.objects.all().count(), 0)
        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([passport, passport2, d1]),
            self.registration_data_import,
        )

        self.assertEqual(GrievanceTicket.objects.all().count(), 0)

        passport.refresh_from_db()
        self.assertEqual(passport.status, Document.STATUS_INVALID)

        passport2.refresh_from_db()
        self.assertEqual(passport2.status, Document.STATUS_VALID)
        self.assertEqual(GrievanceTicket.objects.all().count(), 0)

    def test_ticket_creation_for_the_same_ind_doc_numbers_different_doc_type(self) -> None:
        Document.objects.all().delete()
        passport = Document.objects.create(
            country=self.country,  # the same country
            type=self.dt,
            document_number="111",  # the same doc number
            individual=self.individuals[2],  # the same Individual
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        passport2 = Document.objects.create(
            country=self.country,  # the same country
            type=self.dt_tax_id,
            document_number="111",  # the same doc number
            individual=self.individuals[2],  # the same Individual
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        d1 = Document.objects.create(
            country=self.country,
            type=self.dt,
            document_number="222",
            individual=self.individuals[1],
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        self.assertEqual(GrievanceTicket.objects.all().count(), 0)
        HardDocumentDeduplication().deduplicate(
            self.get_documents_query([passport, passport2, d1]),
            self.registration_data_import,
        )

        self.assertEqual(GrievanceTicket.objects.all().count(), 0)

        passport.refresh_from_db()
        self.assertEqual(passport.status, Document.STATUS_VALID)

        passport2.refresh_from_db()
        self.assertEqual(passport2.status, Document.STATUS_VALID)
        self.assertEqual(GrievanceTicket.objects.all().count(), 0)
