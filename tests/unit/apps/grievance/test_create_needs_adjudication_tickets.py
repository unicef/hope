from django.core.files.base import ContentFile

import pytest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets,
    create_needs_adjudication_tickets_for_biometrics,
)
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.models import DeduplicationEngineSimilarityPair
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestCreateNeedsAdjudicationTickets(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        program = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )
        cls.household = HouseholdFactory.build(
            size=2,
            program=program,
        )
        cls.household.household_collection.save()
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.program = program
        cls.household.registration_data_import.save()
        cls.individuals_to_create = [
            {
                "full_name": "test name",
                "given_name": "test",
                "family_name": "name",
                "birth_date": "1999-01-22",
                "deduplication_golden_record_results": {
                    "duplicates": [],
                    "possible_duplicates": [],
                },
            },
            {
                "full_name": "Test2 Name2",
                "given_name": "Test2",
                "family_name": "Name2",
                "birth_date": "1999-01-22",
                "deduplication_golden_record_results": {
                    "duplicates": [],
                    "possible_duplicates": [],
                },
            },
        ]
        individuals = [
            IndividualFactory(household=cls.household, program=program, **individual)
            for individual in cls.individuals_to_create
        ]
        cls.household.head_of_household = individuals[0]
        cls.household.save()

        rebuild_search_index()

    def test_create_needs_adjudication_ticket_with_the_same_ind(self) -> None:
        self.assertEqual(Individual.objects.count(), 2)
        ind = Individual.objects.first()
        ind_2 = Individual.objects.last()
        ind.deduplication_golden_record_results = {
            "duplicates": [{"hit_id": str(ind.pk)}],
            "possible_duplicates": [{"hit_id": str(ind.pk)}],
        }
        ind.save()
        individuals_queryset = Individual.objects.all()
        rdi = self.household.registration_data_import

        create_needs_adjudication_tickets(
            individuals_queryset,
            "duplicates",
            self.business_area,
            GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
            rdi,
        )
        self.assertEqual(GrievanceTicket.objects.all().count(), 0)

        create_needs_adjudication_tickets(
            individuals_queryset,
            "possible_duplicates",
            self.business_area,
            GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
            rdi,
        )
        self.assertEqual(GrievanceTicket.objects.all().count(), 0)

        # ticket_have to be created
        deduplication_golden_record_results_data = {
            "duplicates": [{"hit_id": str(ind_2.pk)}],
            "possible_duplicates": [{"hit_id": str(ind_2.pk)}],
        }
        ind.deduplication_golden_record_results = deduplication_golden_record_results_data
        ind_2.deduplication_golden_record_results = {
            "duplicates": [],
            "possible_duplicates": [],
        }
        ind.save()
        ind_2.save()
        create_needs_adjudication_tickets(
            Individual.objects.all(),
            "duplicates",
            self.business_area,
            GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
            rdi,
        )
        self.assertEqual(GrievanceTicket.objects.all().count(), 1)


@pytest.mark.elasticsearch
class TestCreateNeedsAdjudicationTicketsBiometrics(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.business_area.biometric_deduplication_threshold = 44.44
        cls.business_area.save()
        program = ProgramFactory(
            name="Test HOPE",
            business_area=BusinessArea.objects.first(),
        )
        program2 = ProgramFactory(
            name="Test HOPE2",
            business_area=BusinessArea.objects.first(),
        )
        cls.household = HouseholdFactory.build(
            size=2,
            program=program,
        )
        cls.household2 = HouseholdFactory.build(
            size=1,
            program=program,
        )
        cls.household3 = HouseholdFactory.build(
            size=1,
            program=program2,
        )
        cls.household.household_collection.save()
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.program = program
        cls.household.registration_data_import.save()
        cls.household2.household_collection.save()
        cls.household2.registration_data_import.imported_by.save()
        cls.household2.registration_data_import.program = program
        cls.household2.registration_data_import.save()
        cls.household3.household_collection.save()
        cls.household3.registration_data_import.imported_by.save()
        cls.household3.registration_data_import.program = program2
        cls.household3.registration_data_import.save()
        cls.rdi = cls.household.registration_data_import
        cls.rd2 = cls.household3.registration_data_import
        individuals_to_create = [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "full_name": "test name",
                "given_name": "test",
                "family_name": "name",
                "birth_date": "1999-01-22",
                "deduplication_golden_record_results": {
                    "duplicates": [],
                    "possible_duplicates": [],
                },
                "photo": ContentFile(b"aaa", name="fooa.png"),
            },
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "full_name": "Test2 Name2",
                "given_name": "Test2",
                "family_name": "Name2",
                "birth_date": "1999-01-22",
                "deduplication_golden_record_results": {
                    "duplicates": [],
                    "possible_duplicates": [],
                },
                "photo": ContentFile(b"bbb", name="foob.png"),
            },
        ]
        individuals_to_create_2 = [
            {
                "id": "33333333-3333-3333-3333-333333333333",
                "full_name": "test name",
                "given_name": "test",
                "family_name": "name",
                "birth_date": "1999-01-22",
                "deduplication_golden_record_results": {
                    "duplicates": [],
                    "possible_duplicates": [],
                },
                "photo": ContentFile(b"aaa", name="fooa.png"),
            },
        ]
        individuals_to_create_3 = [
            {
                "id": "33333333-3333-3333-4444-333333333333",
                "full_name": "test name 2",
                "given_name": "test 2",
                "family_name": "name 2",
                "birth_date": "1999-01-22",
                "deduplication_golden_record_results": {
                    "duplicates": [],
                    "possible_duplicates": [],
                },
                "photo": ContentFile(b"aaa", name="fooa2.png"),
            },
        ]

        individuals = [
            IndividualFactory(household=cls.household, program=program, **individual)
            for individual in individuals_to_create
        ]
        other_individual = [
            IndividualFactory(household=cls.household2, program=program, **individual)
            for individual in individuals_to_create_2
        ][0]
        other_individual2 = [
            IndividualFactory(household=cls.household3, program=program2, **individual)
            for individual in individuals_to_create_3
        ][0]
        cls.household.head_of_household = individuals[0]
        cls.household.save()
        cls.household2.head_of_household = other_individual
        cls.household2.save()
        cls.household3.head_of_household = other_individual2
        cls.household3.save()

        cls.ind1, cls.ind2 = sorted(individuals, key=lambda x: x.id)
        cls.ind1.registration_data_import = cls.rdi
        cls.ind2.registration_data_import = cls.rdi
        cls.ind1.save()
        cls.ind2.save()
        cls.ind3, cls.ind4 = sorted([cls.ind1, other_individual], key=lambda x: x.id)
        cls.ind5 = other_individual2

        cls.dedup_engine_similarity_pair = DeduplicationEngineSimilarityPair.objects.create(
            program=program, individual1=cls.ind1, individual2=cls.ind2, similarity_score=55.55, status_code="200"
        )
        cls.dedup_engine_similarity_pair_2 = DeduplicationEngineSimilarityPair.objects.create(
            program=program, individual1=cls.ind3, individual2=cls.ind4, similarity_score=75.25, status_code="200"
        )
        cls.dedup_engine_similarity_pair_3 = DeduplicationEngineSimilarityPair.objects.create(
            program=program2, individual1=cls.ind5, individual2=None, similarity_score=0.0, status_code="429"
        )

    def test_create_na_tickets_biometrics(self) -> None:
        self.assertEqual(GrievanceTicket.objects.all().count(), 0)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.all().count(), 0)
        self.assertIsNone(self.rdi.deduplication_engine_status)

        create_needs_adjudication_tickets_for_biometrics(DeduplicationEngineSimilarityPair.objects.none(), self.rdi)
        self.assertEqual(GrievanceTicket.objects.all().count(), 0)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.all().count(), 0)

        self.assertEqual(DeduplicationEngineSimilarityPair.objects.all().count(), 3)
        create_needs_adjudication_tickets_for_biometrics(
            DeduplicationEngineSimilarityPair.objects.filter(pk=self.dedup_engine_similarity_pair.pk),
            self.rdi,
        )

        self.assertEqual(GrievanceTicket.objects.all().count(), 1)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.all().count(), 1)
        grievance_ticket = GrievanceTicket.objects.first()
        na_ticket = TicketNeedsAdjudicationDetails.objects.first()

        self.assertEqual(grievance_ticket.category, GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION)
        self.assertEqual(
            grievance_ticket.issue_type,
            GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY,
        )

        self.assertTrue(na_ticket.is_multiple_duplicates_version)
        self.assertEqual(
            na_ticket.extra_data["dedup_engine_similarity_pair"],
            self.dedup_engine_similarity_pair.serialize_for_ticket(),
        )

        # different RDI
        create_needs_adjudication_tickets_for_biometrics(
            DeduplicationEngineSimilarityPair.objects.filter(pk=self.dedup_engine_similarity_pair_2.pk),
            self.rdi,
        )
        self.assertEqual(GrievanceTicket.objects.all().count(), 2)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.all().count(), 2)
        # run one time
        create_needs_adjudication_tickets_for_biometrics(
            DeduplicationEngineSimilarityPair.objects.filter(pk=self.dedup_engine_similarity_pair_2.pk),
            self.rdi,
        )
        self.assertEqual(GrievanceTicket.objects.all().count(), 2)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.all().count(), 2)

    def test_create_na_tickets_biometrics_for_1_ind(self) -> None:
        self.assertEqual(GrievanceTicket.objects.all().count(), 0)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.all().count(), 0)

        create_needs_adjudication_tickets_for_biometrics(
            DeduplicationEngineSimilarityPair.objects.filter(pk=self.dedup_engine_similarity_pair_3.pk),
            self.rdi,
        )

        self.assertEqual(GrievanceTicket.objects.all().count(), 1)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.all().count(), 1)
        grievance_ticket = GrievanceTicket.objects.first()
        na_ticket = TicketNeedsAdjudicationDetails.objects.first()

        self.assertEqual(grievance_ticket.category, GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION)
        self.assertEqual(
            grievance_ticket.issue_type,
            GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY,
        )

        self.assertEqual(str(na_ticket.golden_records_individual.id), str(self.ind5.id))
        self.assertIsNone(na_ticket.possible_duplicate)
        self.assertEqual(
            na_ticket.extra_data["dedup_engine_similarity_pair"],
            self.dedup_engine_similarity_pair_3.serialize_for_ticket(),
        )
