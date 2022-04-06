from django.utils import timezone

from graphql import GraphQLError

from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketPaymentVerificationDetails,
)
from hct_mis_api.apps.grievance.notifications import GrievanceNotification
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentVerification,
)
from hct_mis_api.apps.payment.services.rapid_pro.api import RapidProAPI


class VerificationPlanStatusChangeServices:
    def __init__(self, cash_plan_verification: CashPlanPaymentVerification):
        self.cash_plan_verification = cash_plan_verification

    def discard(self) -> CashPlanPaymentVerification:
        if self.cash_plan_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            raise GraphQLError("You can discard only ACTIVE verification")

        self.cash_plan_verification.set_pending()
        self.cash_plan_verification.save()

        # payment verifications to reset
        payment_record_verifications = self.cash_plan_verification.payment_record_verifications.all()
        for payment_record_verification in payment_record_verifications:
            payment_record_verification.set_pending()

        PaymentVerification.objects.bulk_update(
            payment_record_verifications, ["status_date", "status", "received_amount"]
        )

        return self.cash_plan_verification

    def activate(self) -> CashPlanPaymentVerification:
        if self.cash_plan_verification.status != CashPlanPaymentVerification.STATUS_PENDING:
            raise GraphQLError("You can activate only PENDING verification")

        if self._can_activate_via_rapidpro():
            self._activate_rapidpro()

        self.cash_plan_verification.set_active()
        self.cash_plan_verification.save()

        return self.cash_plan_verification

    def _can_activate_via_rapidpro(self):
        return (
            self.cash_plan_verification.verification_channel
            == CashPlanPaymentVerification.VERIFICATION_CHANNEL_RAPIDPRO
        )

    def _activate_rapidpro(self):
        business_area_slug = self.cash_plan_verification.business_area.slug
        api = RapidProAPI(business_area_slug)
        pv_id = self.cash_plan_verification.id
        phone_numbers = list(
            Individual.objects.filter(
                heading_household__payment_records__verifications__cash_plan_payment_verification=pv_id
            ).values_list("phone_no", flat=True)
        )
        flow_start_info = api.start_flow(self.cash_plan_verification.rapid_pro_flow_id, phone_numbers)
        self.cash_plan_verification.rapid_pro_flow_start_uuid = flow_start_info.get("uuid")

    def finish(self) -> CashPlanPaymentVerification:
        self.cash_plan_verification.status = CashPlanPaymentVerification.STATUS_FINISHED
        self.cash_plan_verification.completion_date = timezone.now()
        self.cash_plan_verification.save()
        self._create_grievance_tickets(self.cash_plan_verification)
        self.cash_plan_verification.payment_record_verifications.filter(
            status=PaymentVerification.STATUS_PENDING
        ).delete()
        return self.cash_plan_verification

    def _create_grievance_ticket_for_status(self, cashplan_payment_verification, status):
        verifications = cashplan_payment_verification.payment_record_verifications.filter(status=status)
        if verifications.count() == 0:
            return
        for verification in verifications:
            grievance_ticket = GrievanceTicket.objects.create(
                category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
                business_area=cashplan_payment_verification.cash_plan.business_area,
            )

            GrievanceNotification.send_all_notifications(
                GrievanceNotification.prepare_notification_for_ticket_creation(grievance_ticket)
            )
            TicketPaymentVerificationDetails.objects.create(
                ticket=grievance_ticket,
                payment_verification_status=status,
                payment_verification=verification
            )

    def _create_grievance_tickets(self, cashplan_payment_verification):
        self._create_grievance_ticket_for_status(cashplan_payment_verification, PaymentVerification.STATUS_NOT_RECEIVED)
        self._create_grievance_ticket_for_status(
            cashplan_payment_verification, PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
        )
