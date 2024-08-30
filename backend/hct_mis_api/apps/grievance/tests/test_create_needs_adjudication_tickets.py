from django.core.files.base import ContentFile

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


class TestCreateNeedsAdjudicationTickets(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        program = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )
        cls.household = HouseholdFactory.build(
            id="12a123ed-d2a5-123a-b123-1234da1d5d23",
            size=2,
            program=program,
        )
        cls.household.household_collection.save()
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.program = program
        cls.household.registration_data_import.save()
        cls.household.programs.add(program)
        cls.individuals_to_create = [
            {
                "full_name": "test name",
                "given_name": "test",
                "family_name": "name",
                "birth_date": "1999-01-22",
                "deduplication_golden_record_results": {"duplicates": [], "possible_duplicates": []},
            },
            {
                "full_name": "Test2 Name2",
                "given_name": "Test2",
                "family_name": "Name2",
                "birth_date": "1999-01-22",
                "deduplication_golden_record_results": {"duplicates": [], "possible_duplicates": []},
            },
        ]
        individuals = [
            IndividualFactory(household=cls.household, program=program, **individual)
            for individual in cls.individuals_to_create
        ]
        cls.household.head_of_household = individuals[0]
        cls.household.save()

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
        ind_2.deduplication_golden_record_results = {"duplicates": [], "possible_duplicates": []}
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


class TestCreateNeedsAdjudicationTicketsBiometrics(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.business_area.biometric_deduplication_threshold = 44.44
        cls.business_area.save()
        program = ProgramFactory(
            name="Test HOPE",
            business_area=BusinessArea.objects.first(),
        )
        cls.household = HouseholdFactory.build(
            id="12a123ed-d2a5-123a-b123-1234da1d5d23",
            size=2,
            program=program,
        )
        cls.household.household_collection.save()
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.program = program
        cls.household.registration_data_import.save()
        cls.rdi = cls.household.registration_data_import
        cls.household.programs.add(program)
        cls.individuals_to_create = [
            {
                "full_name": "test name",
                "given_name": "test",
                "family_name": "name",
                "birth_date": "1999-01-22",
                "deduplication_golden_record_results": {"duplicates": [], "possible_duplicates": []},
                "photo": ContentFile(b"aaa", name="fooa.png"),
            },
            {
                "full_name": "Test2 Name2",
                "given_name": "Test2",
                "family_name": "Name2",
                "birth_date": "1999-01-22",
                "deduplication_golden_record_results": {"duplicates": [], "possible_duplicates": []},
                "photo": ContentFile(b"bbb", name="foob.png"),
            },
        ]
        individuals = [
            IndividualFactory(household=cls.household, program=program, **individual)
            for individual in cls.individuals_to_create
        ]
        cls.household.head_of_household = individuals[0]
        cls.household.save()

        cls.ind1, cls.ind2 = sorted(individuals, key=lambda x: x.id)

        cls.dedup_engine_similarity_pair = DeduplicationEngineSimilarityPair.objects.create(
            program=program,
            individual1=cls.ind1,
            individual2=cls.ind2,
            similarity_score=55.55,
        )

    def test_create_na_tickets_biometrics(self) -> None:
        self.assertEqual(GrievanceTicket.objects.all().count(), 0)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.all().count(), 0)
        self.assertIsNone(self.rdi.deduplication_engine_status)

        create_needs_adjudication_tickets_for_biometrics(DeduplicationEngineSimilarityPair.objects.none(), self.rdi)
        self.assertEqual(GrievanceTicket.objects.all().count(), 0)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.all().count(), 0)

        self.assertEqual(DeduplicationEngineSimilarityPair.objects.all().count(), 1)
        create_needs_adjudication_tickets_for_biometrics(DeduplicationEngineSimilarityPair.objects.all(), self.rdi)

        self.assertEqual(GrievanceTicket.objects.all().count(), 1)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.all().count(), 1)
        grievance_ticket = GrievanceTicket.objects.first()
        na_ticket = TicketNeedsAdjudicationDetails.objects.first()

        self.assertEqual(grievance_ticket.category, GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION)
        self.assertEqual(grievance_ticket.issue_type, GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY)

        self.assertTrue(na_ticket.is_multiple_duplicates_version)
        self.assertEqual(na_ticket.dedup_engine_similarity_pair, self.dedup_engine_similarity_pair)
