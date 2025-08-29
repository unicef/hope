from typing import Any

from django.core.management import call_command
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.grievance import (
    TicketPaymentVerificationDetailsFactory,
)
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.models import country as geo_models
from hope.apps.grievance.models import GrievanceTicket
from hope.models.payment_verification import PaymentVerification
from hope.models.payment_verification_plan import PaymentVerificationPlan
from hope.models.program import Program

pytestmark = pytest.mark.django_db()


class TestGrievanceUpdatePaymentVerificationTicket:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        call_command("loadcountries")
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner, first_name="TestUser")
        self.user2 = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        self.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")
        PaymentPlanFactory(
            id="0272dd2d-c41e-435d-9587-6ba280678c54",
            unicef_id="B4M-21-CSH-00004",
            business_area=self.afghanistan,
            program_cycle=self.program.cycles.first(),
        )

        household, _ = create_household_and_individuals(
            {
                "id": "01780fad-9fa9-4e27-b3cd-7187c13452e5",
                "unicef_id": "HH-21-0000.8129",
                "business_area": self.afghanistan,
            },
            [
                {
                    "full_name": "Jenna Franklin",
                    "given_name": "Jenna",
                    "family_name": "Franklin",
                    "phone_no": "001-296-358-5428-607",
                    "birth_date": "1969-11-29",
                    "id": "001A2C2D-22CA-4538-A36F-D454AF5EDD3E",
                    "unicef_id": "IND-21-0002.2658",
                },
            ],
        )

        payment_plan = PaymentPlanFactory(
            name="TEST",
            program_cycle=self.program.cycles.first(),
            business_area=self.afghanistan,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        payment_verification_plan = PaymentVerificationPlanFactory(
            payment_plan=payment_plan, status=PaymentVerificationPlan.STATUS_ACTIVE
        )
        payment = PaymentFactory(
            parent=payment_plan,
            household=household,
            unicef_id="P8F-21-CSH-00031-123123",
            currency="PLN",
        )
        payment_verification = PaymentVerificationFactory(
            id="a76bfe6f-c767-4b7f-9671-6df10b8095cc",
            payment_verification_plan=payment_verification_plan,
            payment=payment,
            status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        )
        self.ticket = TicketPaymentVerificationDetailsFactory(
            payment_verification=payment_verification,
            ticket__status=GrievanceTicket.STATUS_IN_PROGRESS,
            ticket__business_area=self.afghanistan,
        )
        self.ticket.ticket.programs.set([self.program])
        self.list_details = reverse(
            "api:grievance-tickets:grievance-tickets-global-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "pk": str(self.ticket.ticket.pk),
            },
        )

    def test_update_payment_verification_ticket_with_new_received_amount_extras(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.afghanistan, self.program)
        data = {
            "extras": {
                "ticket_payment_verification_details_extras": {
                    "new_received_amount": 1234.99,
                    "new_status": PaymentVerification.STATUS_RECEIVED,
                }
            }
        }
        response = self.api_client.patch(self.list_details, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["ticket_details"]["new_status"] == PaymentVerification.STATUS_RECEIVED
        assert response.json()["ticket_details"]["new_received_amount"] == "1234.99"

    def test_payment_verification_ticket_approve_payment_details(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION],
            self.afghanistan,
            self.program,
        )
        # update status for approval
        self.ticket.ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
        self.ticket.ticket.save()

        input_data = {
            "version": self.ticket.ticket.version,
            "approve_status": True,
        }

        response = self.api_client.post(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-approve-payment-details",
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(self.ticket.ticket.pk),
                },
            ),
            input_data,
            format="json",
        )

        resp_data = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "id" in resp_data
        self.ticket.refresh_from_db()
        assert self.ticket.approve_status is True
