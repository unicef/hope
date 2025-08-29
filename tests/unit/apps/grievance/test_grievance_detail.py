from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.core.files.base import ContentFile
from django.utils import timezone
from freezegun import freeze_time
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan, create_ukraine
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.grievance import (
    GrievanceDocumentFactory,
    GrievanceTicketFactory,
    TicketAddIndividualDetailsFactory,
    TicketDeleteHouseholdDetailsFactory,
    TicketDeleteIndividualDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketNoteFactory,
    TicketPaymentVerificationDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
)
from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    create_household_and_individuals,
)
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.sanction_list import SanctionListIndividualFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models.household import (
    DUPLICATE,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SINGLE,
)
from hope.models.individual_role_in_household import IndividualRoleInHousehold
from hope.models.payment_verification import PaymentVerification
from hope.models.payment_verification_plan import PaymentVerificationPlan
from hope.models.program import Program
from hope.models.deduplication_engine_similarity_pair import DeduplicationEngineSimilarityPair
from hope.models.sanction_list_individual_date_of_birth import SanctionListIndividualDateOfBirth
from hope.models.sanction_list_individual_document import SanctionListIndividualDocument

pytestmark = pytest.mark.django_db()


@freeze_time("2024-08-25 12:00:00")
class TestGrievanceTicketDetail:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.detail_url_name = "api:grievance:grievance-tickets-global-detail"

        self.afghanistan = create_afghanistan()
        self.ukraine = create_ukraine()
        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.user2 = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.country = CountryFactory()
        self.admin_type = AreaTypeFactory(country=self.country, area_level=1)
        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=self.admin_type)
        self.area2 = AreaFactory(parent=None, p_code="AF0101", area_type=self.admin_type)

        self.grievance_ticket_base_data = {
            "business_area": self.afghanistan,
            "admin2": self.area1,
            "language": "Polish",
            "consent": True,
            "description": "Test Description",
            "status": GrievanceTicket.STATUS_NEW,
            "created_by": self.user,
            "assigned_to": self.user2,
            "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
        }

        self.ticket_note = TicketNoteFactory(
            description="Test Note",
            created_by=self.user,
            created_at=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            updated_at=timezone.make_aware(datetime(year=2021, month=8, day=24)),
        )

        self.grievance_document = GrievanceDocumentFactory(
            name="Test Document",
            created_by=self.user,
            created_at=timezone.make_aware(datetime(year=2022, month=8, day=22)),
            updated_at=timezone.make_aware(datetime(year=2022, month=8, day=24)),
        )

        self.household1, self.individuals1 = create_household_and_individuals(
            household_data={
                "admin1": self.area1,
                "admin2": self.area2,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        self.household2, self.individuals2 = create_household_and_individuals(
            household_data={
                "admin1": self.area1,
                "admin2": self.area2,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.linked_ticket = GrievanceTicketFactory(
            business_area=self.ukraine,
            admin2=self.area1,
            language="Polish",
            consent=True,
            description="Linked Ticket",
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            status=GrievanceTicket.STATUS_NEW,
            created_by=self.user2,
            assigned_to=self.user2,
        )
        self.linked_ticket.created_at = timezone.make_aware(datetime(year=2021, month=8, day=22))
        self.linked_ticket.save()

        self.existing_ticket = GrievanceTicketFactory(
            business_area=self.ukraine,
            admin2=self.area1,
            language="Polish",
            consent=True,
            description="Linked Ticket",
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            status=GrievanceTicket.STATUS_NEW,
            created_by=self.user2,
            assigned_to=self.user2,
            household_unicef_id=self.household1.unicef_id,  # will match if household_unicef_id is the same
        )
        self.existing_ticket.created_at = timezone.make_aware(datetime(year=2021, month=8, day=23))
        self.existing_ticket.save()

    def test_grievance_detail_with_all_permissions(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        )
        grievance_ticket.programs.add(self.program)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "permissions",
        [
            [],
            (Permissions.PROGRAMME_ACTIVATE,),
        ],
    )
    def test_grievance_detail_without_permissions(
        self, permissions: list, create_user_role_with_permissions: Any
    ) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        )
        grievance_ticket.programs.add(self.program)

        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_grievance_detail_area_limits(
        self,
        create_user_role_with_permissions: Any,
        set_admin_area_limits_in_program: Any,
    ) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        )
        grievance_ticket.programs.add(self.program)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        set_admin_area_limits_in_program(self.partner, self.program, [self.area2])

        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_grievance_detail_with_permissions_in_program(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        )
        grievance_ticket.programs.add(self.program)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        ("permissions", "area_limit", "expected_status_1", "expected_status_2"),
        [
            (
                [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
                False,
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND,
            ),
            (
                [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR],
                False,
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND,
            ),
            (
                [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER],
                False,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_404_NOT_FOUND,
            ),
            (
                [Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE],
                False,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_200_OK,
            ),
            (
                [Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR],
                False,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_404_NOT_FOUND,
            ),
            (
                [Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER],
                False,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_200_OK,
            ),
            (
                [
                    Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                ],
                False,
                status.HTTP_200_OK,
                status.HTTP_200_OK,
            ),
            (
                [
                    Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                ],
                True,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_200_OK,
            ),
        ],
    )
    def test_grievance_ticket_detail_access_based_on_permissions(
        self,
        permissions: list,
        area_limit: bool,
        expected_status_1: int,
        expected_status_2: int,
        create_user_role_with_permissions: Callable,
        set_admin_area_limits_in_program: Callable,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        grievance_ticket_non_sensitive_with_creator = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        )
        grievance_ticket_non_sensitive_with_creator.programs.add(self.program)
        grievance_ticket_sensitive_with_owner = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            issue_type=GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE,
        )
        grievance_ticket_sensitive_with_owner.created_by = self.user2
        grievance_ticket_sensitive_with_owner.assigned_to = self.user
        grievance_ticket_sensitive_with_owner.admin2 = None
        grievance_ticket_sensitive_with_owner.save()
        grievance_ticket_sensitive_with_owner.programs.add(self.program)
        if area_limit:
            set_admin_area_limits_in_program(self.partner, self.program, [self.area2])

        response_1 = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket_non_sensitive_with_creator.id),
                },
            )
        )
        assert response_1.status_code == expected_status_1

        response_2 = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket_sensitive_with_owner.id),
                },
            )
        )
        assert response_2.status_code == expected_status_2

    def test_grievance_detail_household_data_update(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            household_unicef_id=self.household1.unicef_id,
        )
        ticket_details = TicketHouseholdDataUpdateDetailsFactory(
            ticket=grievance_ticket,
            household=self.household1,
            household_data={"village": {"value": "Test Village", "approve_status": True}},
        )
        self._assign_ticket_data(grievance_ticket)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        self._assert_base_grievance_data(data, grievance_ticket)
        assert data["payment_record"] is None

        assert data["ticket_details"] == {
            "id": str(ticket_details.id),
            "household_data": ticket_details.household_data,
        }

    def test_grievance_detail_individual_data_update(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            household_unicef_id=self.household1.unicef_id,
        )
        ticket_details = TicketIndividualDataUpdateDetailsFactory(
            ticket=grievance_ticket,
            individual=self.individuals1[0],
            individual_data={"role": {"value": ROLE_ALTERNATE, "approve_status": True}},
        )
        self._assign_ticket_data(grievance_ticket)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        self._assert_base_grievance_data(data, grievance_ticket)
        assert data["payment_record"] is None

        assert data["ticket_details"] == {
            "id": str(ticket_details.id),
            "individual_data": ticket_details.individual_data,
            "role_reassign_data": ticket_details.role_reassign_data,
        }

    def test_grievance_detail_add_individual(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            household_unicef_id=self.household1.unicef_id,
        )
        ticket_details = TicketAddIndividualDetailsFactory(
            ticket=grievance_ticket,
            household=self.household1,
            approve_status=True,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
                "documents": [],
            },
        )
        self._assign_ticket_data(grievance_ticket)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        self._assert_base_grievance_data(data, grievance_ticket)
        assert data["payment_record"] is None

        assert data["ticket_details"] == {
            "id": str(ticket_details.id),
            "individual_data": ticket_details.individual_data,
            "approve_status": ticket_details.approve_status,
        }

    def test_grievance_detail_delete_individual(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            household_unicef_id=self.household1.unicef_id,
        )
        role_primary = IndividualRoleInHousehold.objects.create(
            role=ROLE_PRIMARY,
            individual=self.individuals1[0],
            household=self.household1,
        )
        ticket_details = TicketDeleteIndividualDetailsFactory(
            ticket=grievance_ticket,
            individual=self.individuals1[0],
            approve_status=True,
            role_reassign_data={
                str(role_primary.id): {
                    "role": ROLE_PRIMARY,
                    "household": str(self.household1.id),
                    "individual": str(self.individuals1[1].id),
                }
            },
        )
        self._assign_ticket_data(grievance_ticket)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        self._assert_base_grievance_data(data, grievance_ticket)
        assert data["payment_record"] is None

        assert data["ticket_details"] == {
            "id": str(ticket_details.id),
            "role_reassign_data": ticket_details.role_reassign_data,
            "approve_status": ticket_details.approve_status,
        }

    def test_grievance_detail_delete_household(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
            household_unicef_id=self.household1.unicef_id,
        )
        role_primary = IndividualRoleInHousehold.objects.create(
            role=ROLE_PRIMARY,
            individual=self.individuals1[0],
            household=self.household2,
        )
        ticket_details = TicketDeleteHouseholdDetailsFactory(
            ticket=grievance_ticket,
            household=self.household1,
            approve_status=True,
            reason_household=self.household2,
            role_reassign_data={
                str(role_primary.id): {
                    "role": ROLE_PRIMARY,
                    "household": str(self.household2.id),
                    "individual": str(self.individuals2[0].id),
                }
            },
        )
        self._assign_ticket_data(grievance_ticket)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        self._assert_base_grievance_data(data, grievance_ticket)
        assert data["payment_record"] is None

        assert data["ticket_details"] == {
            "id": str(ticket_details.id),
            "approve_status": ticket_details.approve_status,
            "role_reassign_data": ticket_details.role_reassign_data,
            "reason_household": {
                "id": str(ticket_details.reason_household.id),
                "unicef_id": ticket_details.reason_household.unicef_id,
                "admin1": {
                    "id": str(ticket_details.reason_household.admin1.id),
                    "name": ticket_details.reason_household.admin1.name,
                },
                "admin2": {
                    "id": str(ticket_details.reason_household.admin2.id),
                    "name": ticket_details.reason_household.admin2.name,
                },
                "admin3": None,
                "admin4": None,
                "first_registration_date": ticket_details.reason_household.first_registration_date.strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "last_registration_date": ticket_details.reason_household.last_registration_date.strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                "total_cash_received": None,
                "total_cash_received_usd": None,
                "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                "start": ticket_details.reason_household.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "zip_code": None,
                "residence_status": ticket_details.reason_household.get_residence_status_display(),
                "country_origin": ticket_details.reason_household.country_origin.name,
                "country": ticket_details.reason_household.country.name,
                "address": ticket_details.reason_household.address,
                "village": ticket_details.reason_household.village,
                "geopoint": None,
                "import_id": ticket_details.reason_household.unicef_id,
                "program_slug": self.program.slug,
            },
        }

    def test_grievance_detail_system_flagging(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            household_unicef_id=self.household1.unicef_id,
        )
        sanction_list_individual = SanctionListIndividualFactory(full_name="Sanction Individual")
        sanction_list_individual_document = SanctionListIndividualDocument.objects.create(
            individual=sanction_list_individual,
            document_number="123-456-789",
            type_of_document="DOC",
        )
        sanction_list_date_of_birth = SanctionListIndividualDateOfBirth.objects.create(
            individual=sanction_list_individual,
            date=date(year=1980, month=2, day=1),
        )
        golden_records_individual = self.individuals1[0]
        golden_records_individual.deduplication_golden_record_status = DUPLICATE
        golden_records_individual.deduplication_golden_record_results = {
            "duplicates": [
                {
                    "hit_id": str(golden_records_individual.pk),
                    "score": 9.0,
                    "proximity_to_score": 3.0,
                }
            ],
            "possible_duplicates": [{"hit_id": str(golden_records_individual.pk)}],
        }
        golden_records_individual.save()
        document_type = DocumentTypeFactory()
        document = DocumentFactory(
            document_number="123-456-789",
            type=document_type,
            individual=golden_records_individual,
            program=self.program,
            country=self.country,
        )
        ticket_details = TicketSystemFlaggingDetailsFactory(
            ticket=grievance_ticket,
            golden_records_individual=golden_records_individual,
            sanction_list_individual=sanction_list_individual,
            approve_status=True,
        )
        self._assign_ticket_data(grievance_ticket)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        self._assert_base_grievance_data(data, grievance_ticket)
        assert data["payment_record"] is None

        ticket_details_data = data["ticket_details"]
        assert ticket_details_data["id"] == str(ticket_details.id)
        assert ticket_details_data["approve_status"] == ticket_details.approve_status
        assert ticket_details_data["role_reassign_data"] == ticket_details.role_reassign_data
        assert ticket_details_data["golden_records_individual"] == {
            "id": str(golden_records_individual.id),
            "unicef_id": golden_records_individual.unicef_id,
            "full_name": golden_records_individual.full_name,
            "birth_date": f"{golden_records_individual.birth_date:%Y-%m-%d}",
            "last_registration_date": f"{golden_records_individual.last_registration_date:%Y-%m-%d}",
            "sex": golden_records_individual.sex,
            "duplicate": golden_records_individual.duplicate,
            "program_slug": golden_records_individual.program.slug,
            "household": {
                "id": str(golden_records_individual.household.id),
                "unicef_id": golden_records_individual.household.unicef_id,
                "admin1": {
                    "id": str(golden_records_individual.household.admin1.id),
                    "name": golden_records_individual.household.admin1.name,
                },
                "admin2": {
                    "id": str(golden_records_individual.household.admin2.id),
                    "name": golden_records_individual.household.admin2.name,
                },
                "admin3": None,
                "admin4": None,
                "country": golden_records_individual.household.country.name,
                "country_origin": golden_records_individual.household.country_origin.name,
                "address": golden_records_individual.household.address,
                "village": golden_records_individual.household.village,
                "geopoint": golden_records_individual.household.geopoint,
                "first_registration_date": (
                    f"{golden_records_individual.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}"
                ),
                "last_registration_date": (
                    f"{golden_records_individual.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
                ),
                "total_cash_received": golden_records_individual.household.total_cash_received,
                "total_cash_received_usd": golden_records_individual.household.total_cash_received_usd,
                "delivered_quantities": [
                    {
                        "currency": "USD",
                        "total_delivered_quantity": "0.00",
                    }
                ],
                "start": f"{golden_records_individual.household.start:%Y-%m-%dT%H:%M:%SZ}",
                "zip_code": golden_records_individual.household.zip_code,
                "residence_status": golden_records_individual.household.get_residence_status_display(),
                "import_id": golden_records_individual.household.unicef_id,
                "program_slug": golden_records_individual.household.program.slug,
            },
            "deduplication_golden_record_results": [
                {
                    "hit_id": str(golden_records_individual.pk),
                    "unicef_id": golden_records_individual.unicef_id,
                    "score": golden_records_individual.deduplication_golden_record_results["duplicates"][0]["score"],
                    "proximity_to_score": golden_records_individual.deduplication_golden_record_results["duplicates"][
                        0
                    ]["proximity_to_score"],
                    "location": "Not provided",
                    "age": None,
                    "duplicate": False,
                    "distinct": False,
                }
            ],
            "documents": [
                {
                    "id": str(document.id),
                    "type": {
                        "id": str(document.type.id),
                        "label": document.type.label,
                        "key": document.type.key,
                    },
                    "country": {
                        "id": str(document.country.id),
                        "name": document.country.name,
                        "iso_code3": document.country.iso_code3,
                    },
                    "document_number": document.document_number,
                    "photo": document.photo.url if document.photo else None,
                },
            ],
        }

        assert ticket_details_data["sanction_list_individual"] == {
            "id": str(sanction_list_individual.id),
            "full_name": sanction_list_individual.full_name,
            "reference_number": sanction_list_individual.reference_number,
            "documents": [
                {
                    "id": str(sanction_list_individual_document.id),
                    "document_number": sanction_list_individual_document.document_number,
                    "type_of_document": sanction_list_individual_document.type_of_document,
                }
            ],
            "dates_of_birth": [
                {
                    "id": str(sanction_list_date_of_birth.id),
                    "date": f"{sanction_list_date_of_birth.date:%Y-%m-%d}",
                }
            ],
        }

    def test_grievance_detail_payment_verification(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
            household_unicef_id=self.household1.unicef_id,
        )
        payment_plan = PaymentPlanFactory(
            name="TEST",
            business_area=self.afghanistan,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        payment_verification_plan = PaymentVerificationPlanFactory(
            payment_plan=payment_plan, status=PaymentVerificationPlan.STATUS_ACTIVE
        )
        payment = PaymentFactory(
            parent=payment_plan,
            household=self.household1,
            delivered_quantity_usd=50,
            delivered_quantity=100,
            currency="PLN",
        )
        payment_verification = PaymentVerificationFactory(
            payment_verification_plan=payment_verification_plan,
            payment=payment,
            status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            received_amount=10,
        )
        ticket_details = TicketPaymentVerificationDetailsFactory(
            ticket=grievance_ticket,
            approve_status=True,
            new_status=PaymentVerification.STATUS_RECEIVED,
            old_received_amount=0,
            new_received_amount=20,
            payment_verification_status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            payment_verification=payment_verification,
        )
        self._assign_ticket_data(grievance_ticket)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        self._assert_base_grievance_data(
            data,
            grievance_ticket,
            delivered_quantities=[
                {"currency": "USD", "total_delivered_quantity": "50.00"},
                {"currency": "PLN", "total_delivered_quantity": "100.00"},
            ],
        )

        assert data["payment_record"] == {
            "id": str(payment.id),
            "unicef_id": payment.unicef_id,
            "parent_id": payment_plan.id,
            "delivered_quantity": f"{payment.delivered_quantity:.2f}",
            "entitlement_quantity": f"{payment.entitlement_quantity:.2f}",
            "verification": payment_verification.id,
        }

        assert data["ticket_details"] == {
            "id": str(ticket_details.id),
            "approve_status": ticket_details.approve_status,
            "new_status": ticket_details.new_status,
            "old_received_amount": f"{ticket_details.old_received_amount:.2f}",
            "new_received_amount": f"{ticket_details.new_received_amount:.2f}",
            "payment_verification_status": ticket_details.payment_verification_status,
            "has_multiple_payment_verifications": False,
            "payment_verification": {
                "id": str(payment_verification.id),
                "status": payment_verification.status,
                "status_date": f"{payment_verification.status_date:%Y-%m-%dT%H:%M:%SZ}",
                "received_amount": f"{payment_verification.received_amount:.2f}",
            },
        }

    def test_grievance_detail_needs_adjudication(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            household_unicef_id=self.household1.unicef_id,
            issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        )
        golden_records_individual, duplicate = sorted(self.individuals1, key=lambda x: x.id)

        golden_records_individual.deduplication_golden_record_status = DUPLICATE
        golden_records_individual.deduplication_golden_record_results = {
            "duplicates": [
                {
                    "hit_id": str(golden_records_individual.pk),
                    "score": 9.0,
                    "proximity_to_score": 3.0,
                }
            ],
            "possible_duplicates": [{"hit_id": str(golden_records_individual.pk)}],
        }
        golden_records_individual.save()
        document_type = DocumentTypeFactory()
        document = DocumentFactory(
            document_number="123-456-789",
            type=document_type,
            individual=golden_records_individual,
            program=self.program,
            country=self.country,
            photo=ContentFile(b"abc", name="doc_aaa.png"),
        )

        dedup_engine_similarity_pair = DeduplicationEngineSimilarityPair.objects.create(
            program=self.program,
            individual1=golden_records_individual,
            individual2=duplicate,
            similarity_score=0.0,
            status_code="429",
        )
        ticket_details = TicketNeedsAdjudicationDetailsFactory(
            ticket=grievance_ticket,
            golden_records_individual=golden_records_individual,
            is_multiple_duplicates_version=True,
            possible_duplicate=self.individuals2[0],
            selected_individual=None,
            role_reassign_data={},
            extra_data={
                "golden_records": [
                    {
                        "dob": "1923-01-01",
                        "score": 9.0,
                        "hit_id": str(golden_records_individual.pk),
                        "location": "Abband",
                        "full_name": "Jan Romaniak",
                        "proximity_to_score": 3.0,
                        "duplicate": False,
                        "distinct": False,
                    }
                ],
                "possible_duplicate": [
                    {
                        "dob": "1923-01-01",
                        "score": 9.0,
                        "hit_id": str(self.individuals2[0].pk),
                        "location": "Abband",
                        "full_name": "Jan Romaniak1",
                        "proximity_to_score": 3.0,
                        "duplicate": True,
                        "distinct": False,
                    },
                ],
                "dedup_engine_similarity_pair": {
                    "similarity_score": dedup_engine_similarity_pair.similarity_score,
                    "status_code": dedup_engine_similarity_pair.status_code,
                    "individual1": {
                        "id": str(dedup_engine_similarity_pair.individual1.id),
                        "unicef_id": dedup_engine_similarity_pair.individual1.unicef_id,
                        "full_name": dedup_engine_similarity_pair.individual1.full_name,
                        "photo_name": None,
                    },
                    "individual2": {
                        "id": str(dedup_engine_similarity_pair.individual2.id),
                        "unicef_id": dedup_engine_similarity_pair.individual2.unicef_id,
                        "full_name": dedup_engine_similarity_pair.individual2.full_name,
                        "photo_name": None,
                    },
                },
            },
        )
        ticket_details.possible_duplicates.set([self.individuals2[0]])
        ticket_details.selected_individuals.set([duplicate])
        self._assign_ticket_data(grievance_ticket)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        self._assert_base_grievance_data(data, grievance_ticket)
        assert data["payment_record"] is None

        ticket_details_data = data["ticket_details"]
        assert ticket_details_data["id"] == str(ticket_details.id)
        assert ticket_details_data["is_multiple_duplicates_version"] == ticket_details.is_multiple_duplicates_version
        assert ticket_details_data["golden_records_individual"] == {
            "id": str(golden_records_individual.id),
            "unicef_id": golden_records_individual.unicef_id,
            "full_name": golden_records_individual.full_name,
            "birth_date": f"{golden_records_individual.birth_date:%Y-%m-%d}",
            "last_registration_date": f"{golden_records_individual.last_registration_date:%Y-%m-%d}",
            "sex": golden_records_individual.sex,
            "duplicate": golden_records_individual.duplicate,
            "program_slug": golden_records_individual.program.slug,
            "household": {
                "id": str(golden_records_individual.household.id),
                "unicef_id": golden_records_individual.household.unicef_id,
                "admin1": {
                    "id": str(golden_records_individual.household.admin1.id),
                    "name": golden_records_individual.household.admin1.name,
                },
                "admin2": {
                    "id": str(golden_records_individual.household.admin2.id),
                    "name": golden_records_individual.household.admin2.name,
                },
                "admin3": None,
                "admin4": None,
                "country": golden_records_individual.household.country.name,
                "country_origin": golden_records_individual.household.country_origin.name,
                "address": golden_records_individual.household.address,
                "village": golden_records_individual.household.village,
                "geopoint": golden_records_individual.household.geopoint,
                "first_registration_date": (
                    f"{golden_records_individual.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}"
                ),
                "last_registration_date": (
                    f"{golden_records_individual.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
                ),
                "total_cash_received": golden_records_individual.household.total_cash_received,
                "total_cash_received_usd": golden_records_individual.household.total_cash_received_usd,
                "delivered_quantities": [
                    {
                        "currency": "USD",
                        "total_delivered_quantity": "0.00",
                    }
                ],
                "start": f"{golden_records_individual.household.start:%Y-%m-%dT%H:%M:%SZ}",
                "zip_code": golden_records_individual.household.zip_code,
                "residence_status": golden_records_individual.household.get_residence_status_display(),
                "import_id": golden_records_individual.household.unicef_id,
                "program_slug": self.program.slug,
            },
            "deduplication_golden_record_results": [
                {
                    "hit_id": str(golden_records_individual.pk),
                    "unicef_id": golden_records_individual.unicef_id,
                    "score": golden_records_individual.deduplication_golden_record_results["duplicates"][0]["score"],
                    "proximity_to_score": golden_records_individual.deduplication_golden_record_results["duplicates"][
                        0
                    ]["proximity_to_score"],
                    "location": "Not provided",
                    "age": None,
                    "duplicate": False,
                    "distinct": False,
                }
            ],
            "documents": [
                {
                    "id": str(document.id),
                    "type": {
                        "id": str(document.type.id),
                        "label": document.type.label,
                        "key": document.type.key,
                    },
                    "country": {
                        "id": str(document.country.id),
                        "name": document.country.name,
                        "iso_code3": document.country.iso_code3,
                    },
                    "document_number": document.document_number,
                    "photo": document.photo.url if document.photo else None,
                },
            ],
        }
        assert ticket_details_data["possible_duplicate"] == {
            "id": str(self.individuals2[0].id),
            "unicef_id": self.individuals2[0].unicef_id,
            "full_name": self.individuals2[0].full_name,
            "birth_date": f"{self.individuals2[0].birth_date:%Y-%m-%d}",
            "last_registration_date": f"{self.individuals2[0].last_registration_date:%Y-%m-%d}",
            "sex": self.individuals2[0].sex,
            "duplicate": self.individuals2[0].duplicate,
            "program_slug": self.individuals2[0].program.slug,
            "household": {
                "id": str(self.individuals2[0].household.id),
                "unicef_id": self.individuals2[0].household.unicef_id,
                "admin1": {
                    "id": str(self.individuals2[0].household.admin1.id),
                    "name": self.individuals2[0].household.admin1.name,
                },
                "admin2": {
                    "id": str(self.individuals2[0].household.admin2.id),
                    "name": self.individuals2[0].household.admin2.name,
                },
                "admin3": None,
                "admin4": None,
                "country": self.individuals2[0].household.country.name,
                "country_origin": self.individuals2[0].household.country_origin.name,
                "address": self.individuals2[0].household.address,
                "village": self.individuals2[0].household.village,
                "geopoint": self.individuals2[0].household.geopoint,
                "first_registration_date": (
                    f"{self.individuals2[0].household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}"
                ),
                "last_registration_date": (
                    f"{self.individuals2[0].household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
                ),
                "total_cash_received": self.individuals2[0].household.total_cash_received,
                "total_cash_received_usd": self.individuals2[0].household.total_cash_received_usd,
                "delivered_quantities": [
                    {
                        "currency": "USD",
                        "total_delivered_quantity": "0.00",
                    }
                ],
                "start": f"{self.individuals2[0].household.start:%Y-%m-%dT%H:%M:%SZ}",
                "zip_code": self.individuals2[0].household.zip_code,
                "residence_status": self.individuals2[0].household.get_residence_status_display(),
                "import_id": self.individuals2[0].household.unicef_id,
                "program_slug": self.program.slug,
            },
            "deduplication_golden_record_results": [],
            "documents": [],
        }
        assert ticket_details_data["possible_duplicates"] == [
            {
                "id": str(self.individuals2[0].id),
                "unicef_id": self.individuals2[0].unicef_id,
                "full_name": self.individuals2[0].full_name,
                "birth_date": f"{self.individuals2[0].birth_date:%Y-%m-%d}",
                "last_registration_date": f"{self.individuals2[0].last_registration_date:%Y-%m-%d}",
                "sex": self.individuals2[0].sex,
                "duplicate": self.individuals2[0].duplicate,
                "program_slug": self.individuals2[0].program.slug,
                "household": {
                    "id": str(self.individuals2[0].household.id),
                    "unicef_id": self.individuals2[0].household.unicef_id,
                    "admin1": {
                        "id": str(self.individuals2[0].household.admin1.id),
                        "name": self.individuals2[0].household.admin1.name,
                    },
                    "admin2": {
                        "id": str(self.individuals2[0].household.admin2.id),
                        "name": self.individuals2[0].household.admin2.name,
                    },
                    "admin3": None,
                    "admin4": None,
                    "country": self.individuals2[0].household.country.name,
                    "country_origin": self.individuals2[0].household.country_origin.name,
                    "address": self.individuals2[0].household.address,
                    "village": self.individuals2[0].household.village,
                    "geopoint": self.individuals2[0].household.geopoint,
                    "first_registration_date": (
                        f"{self.individuals2[0].household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}"
                    ),
                    "last_registration_date": (
                        f"{self.individuals2[0].household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
                    ),
                    "total_cash_received": self.individuals2[0].household.total_cash_received,
                    "total_cash_received_usd": self.individuals2[0].household.total_cash_received_usd,
                    "delivered_quantities": [
                        {
                            "currency": "USD",
                            "total_delivered_quantity": "0.00",
                        }
                    ],
                    "start": f"{self.individuals2[0].household.start:%Y-%m-%dT%H:%M:%SZ}",
                    "zip_code": self.individuals2[0].household.zip_code,
                    "residence_status": self.individuals2[0].household.get_residence_status_display(),
                    "import_id": self.individuals2[0].household.unicef_id,
                    "program_slug": self.program.slug,
                },
                "deduplication_golden_record_results": [],
                "documents": [],
            },
        ]
        assert ticket_details_data["selected_duplicates"] == [
            {
                "id": str(duplicate.id),
                "unicef_id": duplicate.unicef_id,
                "full_name": duplicate.full_name,
                "birth_date": f"{duplicate.birth_date:%Y-%m-%d}",
                "last_registration_date": f"{duplicate.last_registration_date:%Y-%m-%d}",
                "sex": duplicate.sex,
                "duplicate": duplicate.duplicate,
                "program_slug": duplicate.program.slug,
                "household": {
                    "id": str(duplicate.household.id),
                    "unicef_id": duplicate.household.unicef_id,
                    "admin1": {
                        "id": str(duplicate.household.admin1.id),
                        "name": duplicate.household.admin1.name,
                    },
                    "admin2": {
                        "id": str(duplicate.household.admin2.id),
                        "name": duplicate.household.admin2.name,
                    },
                    "admin3": None,
                    "admin4": None,
                    "country": duplicate.household.country.name,
                    "country_origin": duplicate.household.country_origin.name,
                    "address": duplicate.household.address,
                    "village": duplicate.household.village,
                    "geopoint": duplicate.household.geopoint,
                    "first_registration_date": f"{duplicate.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                    "last_registration_date": f"{duplicate.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                    "total_cash_received": duplicate.household.total_cash_received,
                    "total_cash_received_usd": duplicate.household.total_cash_received_usd,
                    "delivered_quantities": [
                        {
                            "currency": "USD",
                            "total_delivered_quantity": "0.00",
                        }
                    ],
                    "start": f"{duplicate.household.start:%Y-%m-%dT%H:%M:%SZ}",
                    "zip_code": duplicate.household.zip_code,
                    "residence_status": duplicate.household.get_residence_status_display(),
                    "import_id": duplicate.household.unicef_id,
                    "program_slug": self.program.slug,
                },
                "deduplication_golden_record_results": [],
                "documents": [],
            },
        ]
        assert ticket_details_data["selected_individual"] is None
        assert ticket_details_data["selected_distinct"] == []
        assert ticket_details_data["role_reassign_data"] == ticket_details.role_reassign_data

        assert ticket_details_data["extra_data"] == {
            "golden_records": [
                {
                    "unicef_id": golden_records_individual.unicef_id,
                    "full_name": ticket_details.extra_data["golden_records"][0]["full_name"],
                    "hit_id": ticket_details.extra_data["golden_records"][0]["hit_id"],
                    "score": ticket_details.extra_data["golden_records"][0]["score"],
                    "proximity_to_score": ticket_details.extra_data["golden_records"][0]["proximity_to_score"],
                    "location": ticket_details.extra_data["golden_records"][0]["location"],
                    "age": relativedelta(
                        date.today(),
                        parse(ticket_details.extra_data["golden_records"][0]["dob"]),
                    ).years,
                    "duplicate": ticket_details.extra_data["golden_records"][0]["duplicate"],
                    "distinct": ticket_details.extra_data["golden_records"][0]["distinct"],
                }
            ],
            "possible_duplicate": [
                {
                    "unicef_id": self.individuals2[0].unicef_id,
                    "full_name": ticket_details.extra_data["possible_duplicate"][0]["full_name"],
                    "hit_id": ticket_details.extra_data["possible_duplicate"][0]["hit_id"],
                    "score": ticket_details.extra_data["possible_duplicate"][0]["score"],
                    "proximity_to_score": ticket_details.extra_data["possible_duplicate"][0]["proximity_to_score"],
                    "location": ticket_details.extra_data["possible_duplicate"][0]["location"],
                    "age": relativedelta(
                        date.today(),
                        parse(ticket_details.extra_data["possible_duplicate"][0]["dob"]),
                    ).years,
                    "duplicate": ticket_details.extra_data["possible_duplicate"][0]["duplicate"],
                    "distinct": ticket_details.extra_data["possible_duplicate"][0]["distinct"],
                },
            ],
            "dedup_engine_similarity_pair": {},  # No permissions
        }

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_BIOMETRIC_RESULTS],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK

        assert response.data["ticket_details"]["extra_data"]["dedup_engine_similarity_pair"] == {
            "similarity_score": f"{ticket_details.extra_data['dedup_engine_similarity_pair']['similarity_score']:.1f}",
            "status_code": ticket_details.extra_data["dedup_engine_similarity_pair"]["status_code"],
            "individual1": {
                "id": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual1"]["id"],
                "unicef_id": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual1"]["unicef_id"],
                "full_name": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual1"]["full_name"],
                "photo": None,
            },
            "individual2": {
                "id": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual2"]["id"],
                "unicef_id": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual2"]["unicef_id"],
                "full_name": ticket_details.extra_data["dedup_engine_similarity_pair"]["individual2"]["full_name"],
                "photo": None,
            },
        }

    def _assign_ticket_data(self, grievance_ticket: GrievanceTicket) -> None:
        self.ticket_note.ticket = grievance_ticket
        self.ticket_note.save()
        self.grievance_document.grievance_ticket = grievance_ticket
        self.grievance_document.save()

        grievance_ticket.programs.add(self.program)

        grievance_ticket.linked_tickets.add(self.linked_ticket)

    def _assert_base_grievance_data(
        self,
        data: Dict,
        grievance_ticket: GrievanceTicket,
        delivered_quantities: Optional[List] = None,
    ) -> None:
        assert data["id"] == str(grievance_ticket.id)
        assert data["unicef_id"] == grievance_ticket.unicef_id
        assert data["status"] == grievance_ticket.status
        assert data["programs"] == [
            {
                "id": str(grievance_ticket.programs.first().id),
                "programme_code": grievance_ticket.programs.first().programme_code,
                "slug": grievance_ticket.programs.first().slug,
                "name": grievance_ticket.programs.first().name,
                "status": grievance_ticket.programs.first().status,
                "screen_beneficiary": grievance_ticket.programs.first().screen_beneficiary,
            }
        ]
        household = getattr(getattr(grievance_ticket, "ticket_details", None), "household", None)
        expected_household = (
            {
                "id": str(household.id),
                "unicef_id": household.unicef_id,
                "unhcr_id": household.unhcr_id,
                "village": household.village,
                "address": household.address,
                "admin1": {
                    "id": str(household.admin1.id),
                    "name": household.admin1.name,
                },
                "admin2": {
                    "id": str(household.admin2.id),
                    "name": household.admin2.name,
                },
                "country": household.country.name,
                "country_origin": household.country_origin.name,
                "geopoint": household.geopoint,
                "size": household.size,
                "residence_status": household.get_residence_status_display(),
                "program_slug": household.program.slug,
                "head_of_household": {
                    "id": str(household.head_of_household.id),
                    "full_name": household.head_of_household.full_name,
                },
                "active_individuals_count": household.active_individuals.count(),
            }
            if household
            else None
        )
        assert data["household"] == expected_household
        assert data["admin"] == (grievance_ticket.admin2.name if grievance_ticket.admin2 else "")
        expected_admin2 = (
            {
                "id": str(grievance_ticket.admin2.id),
                "name": grievance_ticket.admin2.name,
                "p_code": grievance_ticket.admin2.p_code,
                "area_type": grievance_ticket.admin2.area_type.id,
                "updated_at": f"{grievance_ticket.admin2.updated_at:%Y-%m-%dT%H:%M:%SZ}",
            }
            if grievance_ticket.admin2
            else None
        )
        assert data["admin2"] == expected_admin2
        assert data["assigned_to"] == {
            "id": str(grievance_ticket.assigned_to.id),
            "first_name": grievance_ticket.assigned_to.first_name,
            "last_name": grievance_ticket.assigned_to.last_name,
            "email": grievance_ticket.assigned_to.email,
            "username": grievance_ticket.assigned_to.username,
        }
        assert data["created_by"] == {
            "id": str(grievance_ticket.created_by.id),
            "first_name": grievance_ticket.created_by.first_name,
            "last_name": grievance_ticket.created_by.last_name,
            "email": grievance_ticket.created_by.email,
            "username": grievance_ticket.created_by.username,
        }
        assert data["user_modified"] == f"{grievance_ticket.user_modified:%Y-%m-%dT%H:%M:%SZ}"
        assert data["category"] == grievance_ticket.category
        assert data["issue_type"] == grievance_ticket.issue_type
        assert data["priority"] == grievance_ticket.priority
        assert data["urgency"] == grievance_ticket.urgency
        assert data["created_at"] == f"{grievance_ticket.created_at:%Y-%m-%dT%H:%M:%SZ}"
        assert data["updated_at"] == f"{grievance_ticket.updated_at:%Y-%m-%dT%H:%M:%SZ}"

        # total_days
        if grievance_ticket.status == GrievanceTicket.STATUS_CLOSED:
            delta = grievance_ticket.updated_at - grievance_ticket.created_at
        else:
            delta = timezone.now() - grievance_ticket.created_at
        expected_total_days = delta.days
        assert data["total_days"] == expected_total_days
        assert data["target_id"] == grievance_ticket.target_id
        assert data["partner"] == (
            {
                "id": str(grievance_ticket.partner.id),
                "name": grievance_ticket.partner.name,
            }
            if grievance_ticket.partner
            else None
        )
        assert data["postpone_deduplication"] == self.afghanistan.postpone_deduplication
        individual = getattr(getattr(grievance_ticket, "ticket_details", None), "individual", None)
        expected_role = (
            (individual.households_and_roles(manager="all_objects").filter(household=individual.household).first())
            if individual
            else None
        )
        expected_individual = (
            {
                "id": str(individual.id),
                "unicef_id": individual.unicef_id,
                "full_name": individual.full_name,
                "program_slug": individual.program.slug,
                "household": {
                    "id": str(individual.household.id),
                    "unicef_id": individual.household.unicef_id,
                    "admin1": {
                        "id": str(individual.household.admin1.id),
                        "name": individual.household.admin1.name,
                    },
                    "admin2": {
                        "id": str(individual.household.admin2.id),
                        "name": individual.household.admin2.name,
                    },
                    "program_slug": individual.program.slug,
                    "admin3": None,
                    "admin4": None,
                    "first_registration_date": f"{individual.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                    "last_registration_date": f"{individual.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                    "total_cash_received": None,
                    "total_cash_received_usd": None,
                    "delivered_quantities": delivered_quantities
                    or [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                    "start": individual.household.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "zip_code": None,
                    "residence_status": individual.household.get_residence_status_display(),
                    "country_origin": individual.household.country_origin.name,
                    "country": individual.household.country.name,
                    "address": individual.household.address,
                    "village": individual.household.village,
                    "geopoint": None,
                    "import_id": individual.household.unicef_id,
                },
                "roles_in_households": [
                    {
                        "id": str(role.id),
                        "role": role.role,
                        "household": {
                            "id": str(role.household.id),
                            "unicef_id": role.household.unicef_id,
                            "admin1": {
                                "id": str(role.household.admin1.id),
                                "name": role.household.admin1.name,
                            },
                            "admin2": {
                                "id": str(role.household.admin2.id),
                                "name": role.household.admin2.name,
                            },
                            "admin3": None,
                            "admin4": None,
                            "country": role.household.country.name,
                            "country_origin": role.household.country_origin.name,
                            "address": role.household.address,
                            "village": role.household.village,
                            "geopoint": role.household.geopoint,
                            "first_registration_date": f"{role.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                            "last_registration_date": f"{role.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                            "total_cash_received": role.household.total_cash_received,
                            "total_cash_received_usd": role.household.total_cash_received_usd,
                            "delivered_quantities": delivered_quantities
                            or [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                            "start": f"{role.household.start:%Y-%m-%dT%H:%M:%SZ}",
                            "zip_code": role.household.zip_code,
                            "residence_status": role.household.get_residence_status_display(),
                            "import_id": role.household.unicef_id,
                            "program_slug": self.program.slug,
                        },
                    }
                    for role in individual.households_and_roles(manager="all_merge_status_objects").all()
                ],
                "relationship": individual.relationship,
                "role": (expected_role.get_role_display() if expected_role else "-"),
                "documents": [
                    {
                        "id": str(document.id),
                        "type": {
                            "id": str(document.type.id),
                            "label": document.type.label,
                            "key": document.type.key,
                        },
                        "country": {
                            "id": str(document.country.id),
                            "name": document.country.name,
                            "iso_code3": document.country.iso_code3,
                        },
                        "document_number": document.document_number,
                        "photo": document.photo.url if document.photo else None,
                    }
                    for document in individual.documents.all()
                ],
            }
            if individual
            else None
        )
        assert data["individual"] == expected_individual

        related_tickets = data["related_tickets"]
        assert {
            "id": str(self.existing_ticket.id),
            "unicef_id": self.existing_ticket.unicef_id,
        } in related_tickets
        assert {
            "id": str(self.linked_ticket.id),
            "unicef_id": self.linked_ticket.unicef_id,
        } in related_tickets
        assert data["linked_tickets"] == [
            {
                "id": str(self.linked_ticket.id),
                "unicef_id": self.linked_ticket.unicef_id,
            },
        ]
        assert data["existing_tickets"] == [
            {
                "id": str(self.existing_ticket.id),
                "unicef_id": self.existing_ticket.unicef_id,
            },
        ]

        assert data["ticket_notes"] == [
            {
                "id": str(self.ticket_note.id),
                "description": self.ticket_note.description,
                "created_by": {
                    "id": str(self.user.id),
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "email": self.user.email,
                    "username": self.user.username,
                },
                "created_at": f"{self.ticket_note.created_at:%Y-%m-%dT%H:%M:%SZ}",
                "updated_at": f"{self.ticket_note.updated_at:%Y-%m-%dT%H:%M:%SZ}",
            }
        ]

        assert data["documentation"] == [
            {
                "id": str(self.grievance_document.id),
                "name": self.grievance_document.name,
                "file_path": self.grievance_document.file_path,
                "file_name": self.grievance_document.file_name,
                "content_type": self.grievance_document.content_type,
                "file_size": self.grievance_document.file_size,
                "created_by": {
                    "id": str(self.user.id),
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "email": self.user.email,
                    "username": self.user.username,
                },
                "created_at": f"{self.grievance_document.created_at:%Y-%m-%dT%H:%M:%SZ}",
                "updated_at": f"{self.grievance_document.updated_at:%Y-%m-%dT%H:%M:%SZ}",
            }
        ]
