from datetime import datetime
from typing import Any, Dict, List

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.utils import timezone

from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from tests.extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from tests.extras.test_utils.factories.fixtures import ProgramFactory
from hct_mis_api.apps.sanction_list.models import SanctionListIndividual


class TestGrievanceApproveAutomaticMutation(APITestCase):
    APPROVE_SYSTEM_FLAGGING_MUTATION = """
    mutation ApproveSystemFlagging($grievanceTicketId: ID!, $approveStatus: Boolean!) {
      approveSystemFlagging(grievanceTicketId: $grievanceTicketId, approveStatus: $approveStatus) {
        grievanceTicket {
          description
          systemFlaggingTicketDetails {
            approveStatus
          }
        }
      }
    }
    """
    APPROVE_NEEDS_ADJUDICATION_MUTATION = """
    mutation ApproveNeedsAdjudicationTicket(
    $grievanceTicketId: ID!, $selectedIndividualId: ID, $duplicateIndividualIds: [ID], $distinctIndividualIds: [ID], $clearIndividualIds: [ID]
    ) {
      approveNeedsAdjudication(
      grievanceTicketId: $grievanceTicketId,
      selectedIndividualId: $selectedIndividualId,
      duplicateIndividualIds: $duplicateIndividualIds,
      distinctIndividualIds: $distinctIndividualIds,
      clearIndividualIds: $clearIndividualIds,
      ) {
        grievanceTicket {
          description
          needsAdjudicationTicketDetails {
            selectedIndividual {
              unicefId
            }
          }
        }
      }
    }
    """
    APPROVE_MULTIPLE_NEEDS_ADJUDICATION_MUTATION = """
    mutation ApproveNeedsAdjudicationTicket(
    $grievanceTicketId: ID!, $selectedIndividualId: ID, $duplicateIndividualIds: [ID]
    ) {
      approveNeedsAdjudication(
      grievanceTicketId: $grievanceTicketId,
      selectedIndividualId: $selectedIndividualId,
      duplicateIndividualIds: $duplicateIndividualIds
      ) {
        grievanceTicket {
          description
          needsAdjudicationTicketDetails {
            possibleDuplicates {
              unicefId
            }
          }
        }
      }
    }
    """
    APPROVE_MULTIPLE_NEEDS_ADJUDICATION_MUTATION_WITH_ID = """
        mutation ApproveNeedsAdjudicationTicket(
        $grievanceTicketId: ID!, $selectedIndividualId: ID, $duplicateIndividualIds: [ID]
        ) {
          approveNeedsAdjudication(
          grievanceTicketId: $grievanceTicketId,
          selectedIndividualId: $selectedIndividualId,
          duplicateIndividualIds: $duplicateIndividualIds
          ) {
            grievanceTicket {
              id
              needsAdjudicationTicketDetails {
                possibleDuplicates {
                  id
                }
              }
            }
          }
        }
        """
    APPROVE_NEEDS_ADJUDICATION_MUTATION_NEW_FIELDS = """
        mutation ApproveNeedsAdjudicationTicket(
        $grievanceTicketId: ID!, $selectedIndividualId: ID, $duplicateIndividualIds: [ID], $distinctIndividualIds: [ID], $clearIndividualIds: [ID]
        ) {
          approveNeedsAdjudication(
          grievanceTicketId: $grievanceTicketId,
          selectedIndividualId: $selectedIndividualId,
          duplicateIndividualIds: $duplicateIndividualIds,
          distinctIndividualIds: $distinctIndividualIds,
          clearIndividualIds: $clearIndividualIds,
          ) {
            grievanceTicket {
              description
              needsAdjudicationTicketDetails {
                selectedIndividual {
                  unicefId
                }
                selectedDistinct {
                  unicefId
                }
                selectedDuplicates {
                  unicefId
                }
                extraData{
                    dedupEngineSimilarityPair {
                      individual1 {
                        fullName
                      }
                      individual2 {
                        fullName
                      }
                      similarityScore
                    }
                }
              }
            }
          }
        }
        """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("loadcountries")
        cls.generate_document_types_for_all_countries()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.business_area.biometric_deduplication_threshold = 33.33
        cls.business_area.save()

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="sdfghjuytre2")
        cls.admin_area_2 = AreaFactory(name="City Example", area_type=area_type, p_code="dfghgf3456")

        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )
        partner = PartnerFactory()
        household_one = HouseholdFactory.build(
            registration_data_import__imported_by__partner=partner,
            program=program_one,
        )
        household_one.household_collection.save()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = household_one.program
        household_one.registration_data_import.save()

        cls.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "unicef_id": "IND-123-123",
                "photo": ContentFile(b"111", name="foo1.png"),
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "unicef_id": "IND-222-222",
                "photo": ContentFile(b"222", name="foo2.png"),
            },
        ]

        cls.individuals = [
            IndividualFactory(household=household_one, program=program_one, **individual)
            for individual in cls.individuals_to_create
        ]
        first_individual = cls.individuals[0]
        second_individual = cls.individuals[1]
        ind1, ind2 = sorted(cls.individuals, key=lambda x: x.id)

        household_one.head_of_household = first_individual
        household_one.save()
        cls.household_one = household_one

        from test_utils.factories.sanction_list import SanctionListFactory

        sanction_list_individual_data = {
            "sanction_list": SanctionListFactory(),
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
            "country_of_birth": geo_models.Country.objects.get(iso_code2="IN"),
        }
        cls.sanction_list_individual = SanctionListIndividual.objects.create(**sanction_list_individual_data)

        cls.system_flagging_grievance_ticket = GrievanceTicketFactory(
            description="system_flagging_grievance_ticket",
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            admin2=cls.admin_area_1,
            business_area=cls.business_area,
        )

        TicketSystemFlaggingDetailsFactory(
            ticket=cls.system_flagging_grievance_ticket,
            golden_records_individual=first_individual,
            sanction_list_individual=cls.sanction_list_individual,
            approve_status=True,
        )

        cls.needs_adjudication_grievance_ticket = GrievanceTicketFactory(
            description="needs_adjudication_grievance_ticket",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            admin2=cls.admin_area_1,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        ticket_details = TicketNeedsAdjudicationDetailsFactory(
            ticket=cls.needs_adjudication_grievance_ticket,
            golden_records_individual=first_individual,
            possible_duplicate=second_individual,
            selected_individual=None,
        )
        ticket_details.possible_duplicates.add(first_individual, second_individual)

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
            ),
            ("without_permission", []),
        ]
    )
    def test_approve_system_flagging(self, _: Any, permissions: List[Permissions]) -> None:
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
    def test_approve_needs_adjudication(self, _: Any, permissions: List[Permissions]) -> None:
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
    def test_approve_needs_adjudication_should_allow_uncheck_selected_individual(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
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

    def test_approve_needs_adjudication_allows_multiple_selected_individuals_without_permission(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        grievance_ticket_id = self.id_to_base64(self.needs_adjudication_grievance_ticket.id, "GrievanceTicketNode")
        response = self.approve_multiple_needs_adjudication_ticket(grievance_ticket_id)

        self.assertIn("Permission Denied", response["errors"][0]["message"])

    def test_approve_needs_adjudication_allows_multiple_selected_individuals_with_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE], self.business_area
        )

        grievance_ticket_id = self.id_to_base64(self.needs_adjudication_grievance_ticket.id, "GrievanceTicketNode")
        response = self.approve_multiple_needs_adjudication_ticket(grievance_ticket_id)

        response_data = response["data"]["approveNeedsAdjudication"]["grievanceTicket"]
        selected_individuals = response_data["needsAdjudicationTicketDetails"]["possibleDuplicates"]
        selected_individuals_ids = list(map(lambda d: d["id"], selected_individuals))

        self.assertEqual(grievance_ticket_id, response_data["id"])
        self.assertIn(self.id_to_base64(self.individuals[0].id, "IndividualNode"), selected_individuals_ids)
        self.assertIn(self.id_to_base64(self.individuals[1].id, "IndividualNode"), selected_individuals_ids)

    def approve_multiple_needs_adjudication_ticket(self, grievance_ticket_id: str) -> Dict:
        return self.graphql_request(
            request_string=self.APPROVE_MULTIPLE_NEEDS_ADJUDICATION_MUTATION_WITH_ID,
            context={"user": self.user},
            variables={
                "grievanceTicketId": grievance_ticket_id,
                "duplicateIndividualIds": [
                    self.id_to_base64(self.individuals[0].id, "IndividualNode"),
                    self.id_to_base64(self.individuals[1].id, "IndividualNode"),
                ],
            },
        )

    def test_approve_needs_adjudication_new_input_fields(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE], self.business_area
        )

        self.needs_adjudication_grievance_ticket.refresh_from_db()
        self.assertEqual(self.needs_adjudication_grievance_ticket.ticket_details.selected_distinct.count(), 0)
        self.assertEqual(self.needs_adjudication_grievance_ticket.ticket_details.selected_individuals.count(), 0)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_NEEDS_ADJUDICATION_MUTATION_NEW_FIELDS,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.needs_adjudication_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "duplicateIndividualIds": self.id_to_base64(self.individuals[1].id, "IndividualNode"),
                "distinctIndividualIds": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
            },
        )

        # wrong grievance ticket status
        self.needs_adjudication_grievance_ticket.status = GrievanceTicket.STATUS_ASSIGNED
        self.needs_adjudication_grievance_ticket.save()
        self.snapshot_graphql_request(
            request_string=self.APPROVE_NEEDS_ADJUDICATION_MUTATION_NEW_FIELDS,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.needs_adjudication_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "duplicateIndividualIds": self.id_to_base64(self.individuals[1].id, "IndividualNode"),
            },
        )
        self.needs_adjudication_grievance_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
        self.needs_adjudication_grievance_ticket.save()

        self.snapshot_graphql_request(
            request_string=self.APPROVE_NEEDS_ADJUDICATION_MUTATION_NEW_FIELDS,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.needs_adjudication_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "duplicateIndividualIds": self.id_to_base64(self.individuals[1].id, "IndividualNode"),
            },
        )
        self.snapshot_graphql_request(
            request_string=self.APPROVE_NEEDS_ADJUDICATION_MUTATION_NEW_FIELDS,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.needs_adjudication_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "distinctIndividualIds": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
            },
        )

        self.assertEqual(self.needs_adjudication_grievance_ticket.ticket_details.selected_distinct.count(), 1)
        self.assertEqual(self.needs_adjudication_grievance_ticket.ticket_details.selected_individuals.count(), 1)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_NEEDS_ADJUDICATION_MUTATION_NEW_FIELDS,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.needs_adjudication_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "clearIndividualIds": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
            },
        )

        self.assertEqual(self.needs_adjudication_grievance_ticket.ticket_details.selected_distinct.count(), 0)
        self.assertEqual(self.needs_adjudication_grievance_ticket.ticket_details.selected_individuals.count(), 1)
