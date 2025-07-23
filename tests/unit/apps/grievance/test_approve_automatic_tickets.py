from datetime import datetime
from typing import Any

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
)
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from parameterized import parameterized
import pytest
from rest_framework import status

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.sanction_list.models import SanctionListIndividual

pytestmark = pytest.mark.django_db()


class TestGrievanceApproveAutomaticTickets:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        call_command("loadcountries")
        self.business_area = create_afghanistan()
        self.business_area.biometric_deduplication_threshold = 33.33
        self.business_area.save()
        call_command("generatedocumenttypes")
        self.user = UserFactory.create()
        self.api_client = api_client(self.user)

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        self.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="sdfghjuytre2")
        self.admin_area_2 = AreaFactory(name="City Example", area_type=area_type, p_code="dfghgf3456")

        self.program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )
        partner = PartnerFactory()
        household_one = HouseholdFactory.build(
            registration_data_import__imported_by__partner=partner,
            program=self.program_one,
        )
        household_one.household_collection.save()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = household_one.program
        household_one.registration_data_import.save()

        self.individuals_to_create = [
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

        self.individuals = [
            IndividualFactory(household=household_one, program=self.program_one, **individual)
            for individual in self.individuals_to_create
        ]
        first_individual = self.individuals[0]
        second_individual = self.individuals[1]
        ind1, ind2 = sorted(self.individuals, key=lambda x: x.id)

        household_one.head_of_household = first_individual
        household_one.save()
        self.household_one = household_one

        # from test_utils.factories.sanction_list import SanctionListFactory

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
        self.sanction_list_individual = SanctionListIndividual.objects.create(**sanction_list_individual_data)

        self.system_flagging_grievance_ticket = GrievanceTicketFactory(
            description="system_flagging_grievance_ticket",
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            admin2=self.admin_area_1,
            business_area=self.business_area,
            created_by=self.user,
        )
        self.system_flagging_grievance_ticket.programs.set([self.program_one])

        TicketSystemFlaggingDetailsFactory(
            ticket=self.system_flagging_grievance_ticket,
            golden_records_individual=first_individual,
            sanction_list_individual=self.sanction_list_individual,
            approve_status=True,
        )

        self.needs_adjudication_grievance_ticket = GrievanceTicketFactory(
            description="needs_adjudication_grievance_ticket",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            admin2=self.admin_area_1,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            created_by=self.user,
        )
        self.needs_adjudication_grievance_ticket.programs.set([self.program_one])
        ticket_details = TicketNeedsAdjudicationDetailsFactory(
            ticket=self.needs_adjudication_grievance_ticket,
            golden_records_individual=first_individual,
            possible_duplicate=second_individual,
            selected_individual=None,
        )
        ticket_details.possible_duplicates.add(first_individual, second_individual)

    def test_approve_system_flagging(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR], self.business_area, self.program_one
        )

        response = self.api_client.post(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-approve-status-update",
                kwargs={
                    "business_area_slug": self.business_area.slug,
                    "pk": str(self.system_flagging_grievance_ticket.id),
                },
            ),
            {"approve_status": False, "version": self.system_flagging_grievance_ticket.version},
            format="json",
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "id" in resp_data
        assert resp_data["ticket_details"]["approve_status"] is False

    def test_approve_needs_adjudication(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE], self.business_area, self.program_one
        )

        response = self.api_client.post(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
                kwargs={
                    "business_area_slug": self.business_area.slug,
                    "pk": str(self.needs_adjudication_grievance_ticket.id),
                },
            ),
            {
                "selected_individual_id": str(self.individuals[1].id),
                "version": self.needs_adjudication_grievance_ticket.version,
            },
            format="json",
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "id" in resp_data
        assert resp_data["ticket_details"]["selected_individual"]["unicef_id"] == self.individuals[1].unicef_id

    def test_approve_needs_adjudication_should_allow_uncheck_selected_individual(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE], self.business_area, self.program_one
        )

        response = self.api_client.post(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
                kwargs={
                    "business_area_slug": self.business_area.slug,
                    "pk": str(self.needs_adjudication_grievance_ticket.id),
                },
            ),
            {"selected_individual_id": None, "version": self.needs_adjudication_grievance_ticket.version},
            format="json",
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "id" in resp_data
        assert resp_data["ticket_details"]["selected_individual"] is None

    def approve_multiple_needs_adjudication_ticket(self, grievance_ticket: GrievanceTicket) -> Any:
        return self.api_client.post(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
                kwargs={"business_area_slug": self.business_area.slug, "pk": str(grievance_ticket.id)},
            ),
            {
                "duplicate_individual_ids": [
                    str(self.individuals[0].id),
                    str(self.individuals[1].id),
                ],
                "version": grievance_ticket.version,
            },
            format="json",
        )

    def test_approve_needs_adjudication_allows_multiple_selected_individuals_without_permission(self) -> None:
        response = self.approve_multiple_needs_adjudication_ticket(self.needs_adjudication_grievance_ticket)
        resp_data = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "You do not have permission to perform this action." == resp_data["detail"]

    def test_approve_needs_adjudication_allows_multiple_selected_individuals_with_permission(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE], self.business_area, self.program_one
        )

        response = self.approve_multiple_needs_adjudication_ticket(self.needs_adjudication_grievance_ticket)
        resp_data = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert len(resp_data["ticket_details"]["possible_duplicates"]) == 2
        selected_individuals = resp_data["ticket_details"]["possible_duplicates"]
        selected_individuals_ids = list(map(lambda d: d["id"], selected_individuals))
        assert str(self.individuals[0].id) in selected_individuals_ids
        assert str(self.individuals[1].id) in selected_individuals_ids

    def test_approve_needs_adjudication_new_input_fields(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE], self.business_area, self.program_one
        )

        url = reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
            kwargs={
                "business_area_slug": self.business_area.slug,
                "pk": str(self.needs_adjudication_grievance_ticket.id),
            },
        )

        self.needs_adjudication_grievance_ticket.refresh_from_db()
        assert self.needs_adjudication_grievance_ticket.ticket_details.selected_distinct.count() == 0
        assert self.needs_adjudication_grievance_ticket.ticket_details.selected_individuals.count() == 0

        resp_1 = self.api_client.post(
            url,
            {
                "duplicate_individual_ids": [str(self.individuals[1].id)],
                "distinct_individual_ids": [str(self.individuals[0].id)],
                "version": self.needs_adjudication_grievance_ticket.version,
            },
            format="json",
        )
        assert resp_1.status_code == status.HTTP_400_BAD_REQUEST
        assert "Only one option for duplicate or distinct or clear individuals is available" in resp_1.json()

        # wrong grievance ticket status
        self.needs_adjudication_grievance_ticket.status = GrievanceTicket.STATUS_ASSIGNED
        self.needs_adjudication_grievance_ticket.save()
        resp_2 = self.api_client.post(
            url,
            {
                "duplicate_individual_ids": [str(self.individuals[1].id)],
                "version": self.needs_adjudication_grievance_ticket.version,
            },
            format="json",
        )
        assert resp_2.status_code == status.HTTP_400_BAD_REQUEST
        assert "A user can not flag individuals when a ticket is not in the 'For Approval' status" in resp_2.json()

        self.needs_adjudication_grievance_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
        self.needs_adjudication_grievance_ticket.save()
        resp_3 = self.api_client.post(
            url,
            {
                "duplicate_individual_ids": [str(self.individuals[1].id)],
                "version": self.needs_adjudication_grievance_ticket.version,
            },
            format="json",
        )
        assert resp_3.status_code == status.HTTP_202_ACCEPTED
        resp_data = resp_3.json()
        assert "id" in resp_data
        assert resp_data["ticket_details"]["selected_duplicates"][0]["unicef_id"] == self.individuals[1].unicef_id

        resp_4 = self.api_client.post(
            url,
            {
                "distinct_individual_ids": [str(self.individuals[0].id)],
                "version": self.needs_adjudication_grievance_ticket.version,
            },
            format="json",
        )
        assert resp_4.status_code == status.HTTP_202_ACCEPTED
        assert "id" in resp_4.json()
        assert self.needs_adjudication_grievance_ticket.ticket_details.selected_distinct.count() == 1
        assert self.needs_adjudication_grievance_ticket.ticket_details.selected_individuals.count() == 1

        resp_5 = self.api_client.post(
            url,
            {
                "clear_individual_ids": [str(self.individuals[0].id)],
                "version": self.needs_adjudication_grievance_ticket.version,
            },
            format="json",
        )
        assert resp_5.status_code == status.HTTP_202_ACCEPTED
        assert "id" in resp_5.json()
        assert self.needs_adjudication_grievance_ticket.ticket_details.selected_distinct.count() == 0
        assert self.needs_adjudication_grievance_ticket.ticket_details.selected_individuals.count() == 1
