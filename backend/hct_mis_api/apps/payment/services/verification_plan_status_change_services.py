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
        if self.cash_plan_verification.verification_channel == CashPlanPaymentVerification.VERIFICATION_CHANNEL_XLSX:
            if (
                not self.cash_plan_verification.xlsx_cash_plan_payment_verification_file_was_downloaded
                or self.cash_plan_verification.xlsx_file_imported
            ):
                raise GraphQLError("You can't discard if xlsx file was downloaded or imported")
            # remove xlsx file
            if self.cash_plan_verification.has_xlsx_cash_plan_payment_verification_file:
                self.cash_plan_verification.xlsx_cashplan_payment_verification_file.delete()

        self.cash_plan_verification.set_pending()
        self.cash_plan_verification.save()

        self._reset_payment_verifications()

        return self.cash_plan_verification

    def mark_invalid(self) -> CashPlanPaymentVerification:
        if self.cash_plan_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            raise GraphQLError("You can mark invalid only ACTIVE verification")
        if self.cash_plan_verification.verification_channel != CashPlanPaymentVerification.VERIFICATION_CHANNEL_XLSX:
            raise GraphQLError("You can mark invalid only verification when XLSX channel is selected")

        if (
            self.cash_plan_verification.xlsx_cash_plan_payment_verification_file_was_downloaded
            or self.cash_plan_verification.xlsx_file_imported
        ):
            self.cash_plan_verification.status = CashPlanPaymentVerification.STATUS_INVALID
            self.cash_plan_verification.save()
            self._reset_payment_verifications()
            # remove xlsx file
            if self.cash_plan_verification.has_xlsx_cash_plan_payment_verification_file:
                self.cash_plan_verification.xlsx_cashplan_payment_verification_file.delete()

            return self.cash_plan_verification
        else:
            raise GraphQLError("You can mark invalid if xlsx file was downloaded or imported")

    def _reset_payment_verifications(self):
        # payment verifications to reset using for discard and mark_invalid
        payment_record_verifications = self.cash_plan_verification.payment_record_verifications.all()
        for payment_record_verification in payment_record_verifications:
            payment_record_verification.set_pending()

        PaymentVerification.objects.bulk_update(
            payment_record_verifications, ["status_date", "status", "received_amount"]
        )

    def activate(self) -> CashPlanPaymentVerification:
        if self.cash_plan_verification.can_activate():
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
        individuals = Individual.objects.filter(
            heading_household__payment_records__verification__cash_plan_payment_verification=pv_id,
            heading_household__payment_records__verification__sent_to_rapid_pro=False,
        )
        phone_numbers = list(individuals.values_list("phone_no", flat=True))
        flow_start_info_list, error = api.start_flows(self.cash_plan_verification.rapid_pro_flow_id, phone_numbers)
        for (flow_start_info, _) in flow_start_info_list:
            self.cash_plan_verification.rapid_pro_flow_start_uuids.append(flow_start_info.get("uuid"))

        all_urns = []
        for (_, urns) in flow_start_info_list:
            all_urns.extend(urn.split(":")[-1] for urn in urns)
        processed_individuals = individuals.filter(phone_no__in=all_urns)
        CashPlanPaymentVerification.objects.get(id=pv_id).payment_record_verifications.filter(
            payment_record__head_of_household__in=processed_individuals
        ).update(sent_to_rapid_pro=True)
        self.cash_plan_verification.save()

        if error is not None:
            self.cash_plan_verification.status = CashPlanPaymentVerification.STATUS_RAPID_PRO_ERROR
            self.cash_plan_verification.error = str(error)
            self.cash_plan_verification.save()
            raise error

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

        grievance_ticket_list = [
            GrievanceTicket(
                category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
                business_area=cashplan_payment_verification.cash_plan.business_area,
            )
            for _ in list(range(verifications.count()))
        ]
        grievance_ticket_objs = GrievanceTicket.objects.bulk_create(grievance_ticket_list)

        ticket_payment_verification_details_list = []
        for verification, grievance_ticket in zip(verifications, grievance_ticket_objs):

            GrievanceNotification.send_all_notifications(
                GrievanceNotification.prepare_notification_for_ticket_creation(grievance_ticket)
            )

            ticket_payment_verification_details = TicketPaymentVerificationDetails(
                ticket=grievance_ticket, payment_verification_status=status, payment_verification=verification
            )
            ticket_payment_verification_details_list.append(ticket_payment_verification_details)

        TicketPaymentVerificationDetails.objects.bulk_create(ticket_payment_verification_details_list)

    def _create_grievance_tickets(self, cashplan_payment_verification):
        self._create_grievance_ticket_for_status(cashplan_payment_verification, PaymentVerification.STATUS_NOT_RECEIVED)
        self._create_grievance_ticket_for_status(
            cashplan_payment_verification, PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
        )
