from typing import Any

import pytest
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.urls import reverse
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status

from hope.apps.account.permissions import Permissions
from hope.apps.core.base_test_case import BaseTestCase
from hope.models.core import BusinessArea
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets,
    create_needs_adjudication_tickets_for_biometrics,
)
from hope.models.household import Individual
from hope.models.registration_data import DeduplicationEngineSimilarityPair
from hope.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")
pytestmark = pytest.mark.django_db()


@pytest.mark.elasticsearch
class TestCreateNeedsAdjudicationTickets(BaseTestCase):
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
        assert Individual.objects.count() == 2
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
        assert GrievanceTicket.objects.all().count() == 0

        create_needs_adjudication_tickets(
            individuals_queryset,
            "possible_duplicates",
            self.business_area,
            GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
            rdi,
        )
        assert GrievanceTicket.objects.all().count() == 0

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
        assert GrievanceTicket.objects.all().count() == 1


@pytest.mark.elasticsearch
class TestCreateNeedsAdjudicationTicketsBiometrics:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        call_command("loadcountries")
        self.business_area = create_afghanistan()
        self.business_area.biometric_deduplication_threshold = 44.44
        self.business_area.save()
        self.user = UserFactory.create()
        self.api_client = api_client(self.user)
        self.program = ProgramFactory(
            name="Test HOPE",
            business_area=BusinessArea.objects.first(),
        )
        program2 = ProgramFactory(
            name="Test HOPE2",
            business_area=BusinessArea.objects.first(),
        )
        self.household = HouseholdFactory.build(
            size=2,
            program=self.program,
        )
        self.household2 = HouseholdFactory.build(
            size=1,
            program=self.program,
        )
        self.household3 = HouseholdFactory.build(
            size=1,
            program=program2,
        )
        self.household.household_collection.save()
        self.household.registration_data_import.imported_by.save()
        self.household.registration_data_import.program = self.program
        self.household.registration_data_import.save()
        self.household2.household_collection.save()
        self.household2.registration_data_import.imported_by.save()
        self.household2.registration_data_import.program = self.program
        self.household2.registration_data_import.save()
        self.household3.household_collection.save()
        self.household3.registration_data_import.imported_by.save()
        self.household3.registration_data_import.program = program2
        self.household3.registration_data_import.save()
        self.rdi = self.household.registration_data_import
        self.rd2 = self.household3.registration_data_import
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
            IndividualFactory(household=self.household, program=self.program, **individual)
            for individual in individuals_to_create
        ]
        other_individual = [
            IndividualFactory(household=self.household2, program=self.program, **individual)
            for individual in individuals_to_create_2
        ][0]
        other_individual2 = [
            IndividualFactory(household=self.household3, program=program2, **individual)
            for individual in individuals_to_create_3
        ][0]
        self.household.head_of_household = individuals[0]
        self.household.save()
        self.household2.head_of_household = other_individual
        self.household2.save()
        self.household3.head_of_household = other_individual2
        self.household3.save()

        self.ind1, self.ind2 = sorted(individuals, key=lambda x: x.id)
        self.ind1.registration_data_import = self.rdi
        self.ind2.registration_data_import = self.rdi
        self.ind1.save()
        self.ind2.save()
        self.ind3, self.ind4 = sorted([self.ind1, other_individual], key=lambda x: x.id)
        self.ind5 = other_individual2

        self.dedup_engine_similarity_pair = DeduplicationEngineSimilarityPair.objects.create(
            program=self.program,
            individual1=self.ind1,
            individual2=self.ind2,
            similarity_score=55.55,
            status_code="200",
        )
        self.dedup_engine_similarity_pair_2 = DeduplicationEngineSimilarityPair.objects.create(
            program=self.program,
            individual1=self.ind3,
            individual2=self.ind4,
            similarity_score=75.25,
            status_code="200",
        )
        self.dedup_engine_similarity_pair_3 = DeduplicationEngineSimilarityPair.objects.create(
            program=program2,
            individual1=self.ind5,
            individual2=None,
            similarity_score=0.0,
            status_code="429",
        )

    def test_create_na_tickets_biometrics(self) -> None:
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketNeedsAdjudicationDetails.objects.all().count() == 0
        assert self.rdi.deduplication_engine_status is None

        create_needs_adjudication_tickets_for_biometrics(DeduplicationEngineSimilarityPair.objects.none(), self.rdi)
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketNeedsAdjudicationDetails.objects.all().count() == 0

        assert DeduplicationEngineSimilarityPair.objects.all().count() == 3
        create_needs_adjudication_tickets_for_biometrics(
            DeduplicationEngineSimilarityPair.objects.filter(pk=self.dedup_engine_similarity_pair.pk),
            self.rdi,
        )

        assert GrievanceTicket.objects.all().count() == 1
        assert TicketNeedsAdjudicationDetails.objects.all().count() == 1
        grievance_ticket = GrievanceTicket.objects.first()
        na_ticket = TicketNeedsAdjudicationDetails.objects.first()

        assert grievance_ticket.category == GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION
        assert grievance_ticket.issue_type == GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY

        assert na_ticket.is_multiple_duplicates_version is True
        assert (
            na_ticket.extra_data["dedup_engine_similarity_pair"]
            == self.dedup_engine_similarity_pair.serialize_for_ticket()
        )

        # different RDI
        create_needs_adjudication_tickets_for_biometrics(
            DeduplicationEngineSimilarityPair.objects.filter(pk=self.dedup_engine_similarity_pair_2.pk),
            self.rdi,
        )
        assert GrievanceTicket.objects.all().count() == 2
        assert TicketNeedsAdjudicationDetails.objects.all().count() == 2
        # run one time
        create_needs_adjudication_tickets_for_biometrics(
            DeduplicationEngineSimilarityPair.objects.filter(pk=self.dedup_engine_similarity_pair_2.pk),
            self.rdi,
        )
        assert GrievanceTicket.objects.all().count() == 2
        assert TicketNeedsAdjudicationDetails.objects.all().count() == 2

    def test_create_na_tickets_biometrics_for_1_ind(self) -> None:
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketNeedsAdjudicationDetails.objects.all().count() == 0

        create_needs_adjudication_tickets_for_biometrics(
            DeduplicationEngineSimilarityPair.objects.filter(pk=self.dedup_engine_similarity_pair_3.pk),
            self.rdi,
        )

        assert GrievanceTicket.objects.all().count() == 1
        assert TicketNeedsAdjudicationDetails.objects.all().count() == 1
        grievance_ticket = GrievanceTicket.objects.first()
        na_ticket = TicketNeedsAdjudicationDetails.objects.first()

        assert grievance_ticket.category == GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION
        assert grievance_ticket.issue_type == GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY

        assert str(na_ticket.golden_records_individual.id) == str(self.ind5.id)
        assert na_ticket.possible_duplicate is None
        assert (
            na_ticket.extra_data["dedup_engine_similarity_pair"]
            == self.dedup_engine_similarity_pair_3.serialize_for_ticket()
        )

    def test_ticket_biometric_query_response(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_BIOMETRIC_RESULTS,
            ],
            self.business_area,
            self.program,
        )

        assert GrievanceTicket.objects.all().count() == 0
        assert TicketNeedsAdjudicationDetails.objects.all().count() == 0

        create_needs_adjudication_tickets_for_biometrics(
            DeduplicationEngineSimilarityPair.objects.filter(pk=self.dedup_engine_similarity_pair.pk),
            self.rdi,
        )
        assert GrievanceTicket.objects.all().count() == 1
        assert TicketNeedsAdjudicationDetails.objects.all().count() == 1

        response = self.api_client.get(
            reverse(
                "api:grievance:grievance-tickets-list",
                kwargs={
                    "business_area_slug": self.business_area.slug,
                    "program_slug": self.program.slug,
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 1
        data_extra = TicketNeedsAdjudicationDetails.objects.first().extra_data
        assert "individual1" in data_extra["dedup_engine_similarity_pair"]
        assert "individual2" in data_extra["dedup_engine_similarity_pair"]
        assert "status_code" in data_extra["dedup_engine_similarity_pair"]
        assert "similarity_score" in data_extra["dedup_engine_similarity_pair"]
