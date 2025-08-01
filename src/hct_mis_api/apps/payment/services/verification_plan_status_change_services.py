import io

from django.utils import timezone

from rest_framework.exceptions import ValidationError

from hct_mis_api.apps.core.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketPaymentVerificationDetails,
)
from hct_mis_api.apps.grievance.notifications import GrievanceNotification
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.payment.celery_tasks import create_payment_verification_plan_xlsx
from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hct_mis_api.apps.payment.utils import calculate_counts
from hct_mis_api.apps.payment.xlsx.xlsx_verification_import_service import (
    XlsxVerificationImportService,
)


class VerificationPlanStatusChangeServices:
    def __init__(self, payment_verification_plan: PaymentVerificationPlan):
        self.payment_verification_plan = payment_verification_plan

    def discard(self) -> PaymentVerificationPlan:
        if self.payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            raise ValidationError("You can discard only ACTIVE verification")
        if self.payment_verification_plan.verification_channel == PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX:
            if (
                self.payment_verification_plan.xlsx_payment_verification_plan_file_was_downloaded
                or self.payment_verification_plan.xlsx_file_imported
            ):
                raise ValidationError("You can't discard if xlsx file was downloaded or imported")
            # remove xlsx file
            if self.payment_verification_plan.has_xlsx_payment_verification_plan_file:
                self.payment_verification_plan.get_xlsx_verification_file.file.delete()
                self.payment_verification_plan.get_xlsx_verification_file.delete()

        self.payment_verification_plan.set_pending()
        self.payment_verification_plan.save()

        self._reset_payment_verifications()

        return self.payment_verification_plan

    def mark_invalid(self) -> PaymentVerificationPlan:
        if self.payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            raise ValidationError("You can mark invalid only ACTIVE verification")
        if self.payment_verification_plan.verification_channel != PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX:
            raise ValidationError("You can mark invalid only verification when XLSX channel is selected")

        if (
            self.payment_verification_plan.xlsx_payment_verification_plan_file_was_downloaded
            or self.payment_verification_plan.xlsx_file_imported
        ):
            self.payment_verification_plan.status = PaymentVerificationPlan.STATUS_INVALID
            self.payment_verification_plan.save()
            self._reset_payment_verifications()
            # remove xlsx file
            if self.payment_verification_plan.has_xlsx_payment_verification_plan_file:
                self.payment_verification_plan.get_xlsx_verification_file.file.delete()
                self.payment_verification_plan.get_xlsx_verification_file.delete()

            return self.payment_verification_plan
        raise ValidationError("You can mark invalid if xlsx file was downloaded or imported")

    def _reset_payment_verifications(self) -> None:
        # payment verifications to reset using for discard and mark_invalid
        payment_record_verifications = self.payment_verification_plan.payment_record_verifications.all()
        for payment_record_verification in payment_record_verifications:
            payment_record_verification.set_pending()

        PaymentVerification.objects.bulk_update(
            payment_record_verifications, ["status_date", "status", "received_amount"]
        )

    def activate(self) -> PaymentVerificationPlan:
        if self.payment_verification_plan.can_activate():
            raise ValidationError("You can activate only PENDING verification")

        if self._can_activate_via_rapidpro():
            self._activate_rapidpro()

        self.payment_verification_plan.set_active()
        self.payment_verification_plan.save()

        return self.payment_verification_plan

    def _can_activate_via_rapidpro(self) -> bool:
        return (
            self.payment_verification_plan.verification_channel == PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO
        )

    def _activate_rapidpro(self) -> None:
        business_area_slug = self.payment_verification_plan.business_area.slug
        api = RapidProAPI(business_area_slug, RapidProAPI.MODE_VERIFICATION)

        hoh_ids = [
            pv.payment.household.head_of_household.pk
            for pv in self.payment_verification_plan.payment_record_verifications.filter(sent_to_rapid_pro=False)
        ]
        individuals = Individual.objects.filter(pk__in=hoh_ids)
        phone_numbers = list(individuals.values_list("phone_no", flat=True))
        successful_flows, error = api.start_flow(self.payment_verification_plan.rapid_pro_flow_id, phone_numbers)
        for successful_flow in successful_flows:
            self.payment_verification_plan.rapid_pro_flow_start_uuids.append(successful_flow.response["uuid"])

        all_urns = []
        for successful_flow in successful_flows:
            all_urns.extend(urn.split(":")[-1] for urn in successful_flow.urns)
        processed_individuals = individuals.filter(phone_no__in=all_urns)

        payment_verifications_to_upd = []
        for pv in self.payment_verification_plan.payment_record_verifications.all():
            if pv.payment.head_of_household in processed_individuals:
                pv.sent_to_rapid_pro = True
                payment_verifications_to_upd.append(pv)
        PaymentVerification.objects.bulk_update(payment_verifications_to_upd, ("sent_to_rapid_pro",), 1000)

        self.payment_verification_plan.save()

        if error is not None:
            self.payment_verification_plan.status = PaymentVerificationPlan.STATUS_RAPID_PRO_ERROR
            self.payment_verification_plan.error = str(error)
            self.payment_verification_plan.save()
            raise error

    def finish(self) -> PaymentVerificationPlan:
        self.payment_verification_plan.status = PaymentVerificationPlan.STATUS_FINISHED
        self.payment_verification_plan.completion_date = timezone.now()
        self.payment_verification_plan.save()
        self._create_grievance_tickets(self.payment_verification_plan)
        self.payment_verification_plan.payment_record_verifications.filter(
            status=PaymentVerification.STATUS_PENDING
        ).delete()
        return self.payment_verification_plan

    def _create_grievance_ticket_for_status(
        self, payment_verification_plan: PaymentVerificationPlan, status: str
    ) -> None:
        verifications = payment_verification_plan.payment_record_verifications.filter(status=status)
        if verifications.count() == 0:
            return

        business_area = payment_verification_plan.payment_plan.business_area
        grievance_ticket_list = []
        tickets_programs = []
        GrievanceTicketProgramThrough = GrievanceTicket.programs.through
        for verification in verifications:
            grievance_ticket = GrievanceTicket(
                category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
                business_area=business_area,
                household_unicef_id=verification.payment.household.unicef_id,
                admin2_id=verification.payment.household.admin2_id,
            )
            grievance_ticket_list.append(grievance_ticket)
            # get program from parent GenericPaymentPlan.program
            program = verification.payment.parent.program

            tickets_programs.append(
                GrievanceTicketProgramThrough(grievanceticket=grievance_ticket, program_id=program.id)
            )
        grievance_ticket_objs = GrievanceTicket.objects.bulk_create(grievance_ticket_list)
        GrievanceTicketProgramThrough.objects.bulk_create(tickets_programs)

        ticket_payment_verification_details_list = []
        for verification, grievance_ticket in zip(verifications, grievance_ticket_objs, strict=True):
            GrievanceNotification.send_all_notifications(
                GrievanceNotification.prepare_notification_for_ticket_creation(grievance_ticket)
            )

            ticket_payment_verification_details = TicketPaymentVerificationDetails(
                ticket=grievance_ticket,
                payment_verification_status=status,
                payment_verification=verification,
            )
            ticket_payment_verification_details_list.append(ticket_payment_verification_details)

        TicketPaymentVerificationDetails.objects.bulk_create(ticket_payment_verification_details_list)

    def _create_grievance_tickets(self, payment_verification_plan: PaymentVerificationPlan) -> None:
        self._create_grievance_ticket_for_status(payment_verification_plan, PaymentVerification.STATUS_NOT_RECEIVED)
        self._create_grievance_ticket_for_status(
            payment_verification_plan, PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
        )

    def export_xlsx(self, user_id: str) -> PaymentVerificationPlan:
        if self.payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            raise ValidationError("You can only export verification for active CashPlan verification")
        if self.payment_verification_plan.verification_channel != PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX:
            raise ValidationError("You can only export verification when XLSX channel is selected")
        if self.payment_verification_plan.xlsx_file_exporting:
            raise ValidationError("Exporting xlsx file is already started. Please wait")
        if self.payment_verification_plan.has_xlsx_payment_verification_plan_file:
            raise ValidationError("Xlsx file is already created")

        self.payment_verification_plan.xlsx_file_exporting = True
        self.payment_verification_plan.save()
        create_payment_verification_plan_xlsx.delay(str(self.payment_verification_plan.pk), user_id)
        return self.payment_verification_plan

    def import_xlsx(self, file: io.BytesIO) -> PaymentVerificationPlan:
        if self.payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            raise ValidationError("You can only import verification for active CashPlan verification")
        if self.payment_verification_plan.verification_channel != PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX:
            raise ValidationError("You can only import verification when XLSX channel is selected")
        import_service = XlsxVerificationImportService(self.payment_verification_plan, file)
        import_service.open_workbook()
        import_service.validate()

        import_service.import_verifications()
        calculate_counts(self.payment_verification_plan)
        self.payment_verification_plan.xlsx_file_imported = True
        self.payment_verification_plan.save()
        return self.payment_verification_plan
