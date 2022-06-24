from datetime import datetime

from django.utils import timezone

from django.core.management import call_command

from django_countries.fields import Country
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    AdminAreaFactory,
    AdminAreaLevelFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.sanction_list.models import SanctionListIndividual


class TestGrievanceApproveAutomaticMutation(APITestCase):
    APPROVE_SYSTEM_FLAGGING_MUTATION = """
    mutation ApproveSystemFlagging($grievanceTicketId: ID!, $approveStatus: Boolean!) {
      approveSystemFlagging(grievanceTicketId: $grievanceTicketId, approveStatus: $approveStatus) {
        grievanceTicket {
          id
          systemFlaggingTicketDetails {
            approveStatus
          }
        }
      }
    }
    """
    APPROVE_NEEDS_ADJUDICATION_MUTATION = """
    mutation ApproveNeedsAdjudicationTicket(
    $grievanceTicketId: ID!, $selectedIndividualId: ID, $selectedIndividualIds: [ID]
    ) {
      approveNeedsAdjudication(
      grievanceTicketId: $grievanceTicketId, 
      selectedIndividualId: $selectedIndividualId, 
      selectedIndividualIds: $selectedIndividualIds
      ) {
        grievanceTicket {
          id
          needsAdjudicationTicketDetails {
            selectedIndividual {
              id
            }
          }
        }
      }
    }
    """
    APPROVE_MULTIPLE_NEEDS_ADJUDICATION_MUTATION = """
    mutation ApproveNeedsAdjudicationTicket(
    $grievanceTicketId: ID!, $selectedIndividualId: ID, $selectedIndividualIds: [ID]
    ) {
      approveNeedsAdjudication(
      grievanceTicketId: $grievanceTicketId, 
      selectedIndividualId: $selectedIndividualId, 
      selectedIndividualIds: $selectedIndividualIds
      ) {
        grievanceTicket {
          id
          needsAdjudicationTicketDetails {
            selectedIndividuals {
              id
            }
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.generate_document_types_for_all_countries()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=cls.business_area,
        )
        cls.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="sdfghjuytre2")
        cls.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_level=area_type, p_code="dfghgf3456")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_1_new = AreaFactory(name="City Test", area_type=area_type, p_code="sdfghjuytre2")
        cls.admin_area_2_new = AreaFactory(name="City Example", area_type=area_type, p_code="dfghgf3456")

        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )
        partner = PartnerFactory()
        household_one = HouseholdFactory.build(
            id="07a901ed-d2a5-422a-b962-3570da1d5d07", registration_data_import__imported_by__partner=partner
        )
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        cls.individuals_to_create = [
            {
                "id": "f9e27ca8-11f7-4386-bafb-e077b0bb47f3",
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
            },
            {
                "id": "94b09ff2-9e6d-4f34-a72c-c319e1db7115",
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
            },
        ]

        cls.individuals = [
            IndividualFactory(household=household_one, **individual) for individual in cls.individuals_to_create
        ]
        first_individual = cls.individuals[0]
        second_individual = cls.individuals[1]

        household_one.head_of_household = first_individual
        household_one.save()
        cls.household_one = household_one

        sanction_list_individual_data = {
            "data_id": 112138,
            "version_num": 1,
            "first_name": "DAWOOD",
            "second_name": "IBRAHIM",
            "third_name": "KASKAR",
            "fourth_name": "",
            "full_name": "Dawood Ibrahim Kaskar",
            "name_original_script": "",
            "un_list_type": "Al-Qaida",
            "reference_number": "QDi.135",
            "listed_on": timezone.make_aware(datetime(2003, 11, 3, 0, 0)),
            "comments": "Father’s name is Sheikh Ibrahim Ali Kaskar, mother’s name is Amina Bi, wife’s "
            "name is Mehjabeen Shaikh. International arrest warrant issued by the Government of India. "
            "Review pursuant to Security Council resolution 1822 (2008) was concluded on 20 May"
            "2010. INTERPOL-UN Security Council Special Notice web link: "
            "https://www.interpol.int/en/How-we-work/Notices/View-UN-Notices-Individuals",
            "designation": "",
            "list_type": "UN List",
            "street": "House Nu 37 - 30th Street - defence, Housing Authority, Karachi",
            "city": "Karachi",
            "state_province": "",
            "address_note": "White House, Near Saudi Mosque, Clifton",
            "country_of_birth": Country(code="IN"),
        }
        cls.sanction_list_individual = SanctionListIndividual.objects.create(**sanction_list_individual_data)

        cls.system_flagging_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            issue_type=None,
            admin2=cls.admin_area_1,
            admin2_new=cls.admin_area_1_new,
            business_area=cls.business_area,
        )

        TicketSystemFlaggingDetailsFactory(
            ticket=cls.system_flagging_grievance_ticket,
            golden_records_individual=first_individual,
            sanction_list_individual=cls.sanction_list_individual,
            approve_status=True,
        )

        cls.needs_adjudication_grievance_ticket = GrievanceTicketFactory(
            id="2b419ce3-3297-47ee-a47f-43442abac73e",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            issue_type=None,
            admin2=cls.admin_area_1,
            admin2_new=cls.admin_area_1_new,
            business_area=cls.business_area,
        )

        TicketNeedsAdjudicationDetailsFactory(
            ticket=cls.needs_adjudication_grievance_ticket,
            golden_records_individual=first_individual,
            possible_duplicate=second_individual,
            selected_individual=None,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
            ),
            ("without_permission", []),
        ]
    )
    def test_approve_system_flagging(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_SYSTEM_FLAGGING_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(self.system_flagging_grievance_ticket.id, "GrievanceTicketNode"),
                "approveStatus": False,
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
            ),
            ("without_permission", []),
        ]
    )
    def test_approve_needs_adjudication(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_NEEDS_ADJUDICATION_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.needs_adjudication_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "selectedIndividualId": self.id_to_base64(self.individuals[1].id, "IndividualNode"),
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
            ),
            ("without_permission", []),
        ]
    )
    def test_approve_needs_adjudication_should_allow_uncheck_selected_individual(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_NEEDS_ADJUDICATION_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.needs_adjudication_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "selectedIndividualId": None,
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
            ),
            ("without_permission", []),
        ]
    )
    def test_approve_needs_adjudication_allows_multiple_selected_individuals(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_MULTIPLE_NEEDS_ADJUDICATION_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.needs_adjudication_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "selectedIndividualIds": [
                    self.id_to_base64(self.individuals[0].id, "IndividualNode"),
                    self.id_to_base64(self.individuals[1].id, "IndividualNode"),
                ],
            },
        )
