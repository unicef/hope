from typing import Any, Optional

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, PartnerFactory
from hct_mis_api.apps.accountability.fixtures import (
    CommunicationMessageFactory,
    FeedbackFactory,
    FeedbackMessageFactory,
)
from hct_mis_api.apps.accountability.models import Feedback, Message
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo.fixtures import CountryFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceComplaintTicketWithoutExtrasFactory,
    GrievanceDocumentFactory,
    GrievanceTicketFactory,
    ReferralTicketWithoutExtrasFactory,
    SensitiveGrievanceTicketWithoutExtrasFactory,
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
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_PRIMARY,
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.fixtures import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.sanction_list.fixtures import SanctionListIndividualFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.one_time_scripts.migrate_grievance_to_representations import (
    migrate_grievance_to_representations,
)


class TestMigrateGrievanceTicketsAndFeedbacks(TestCase):
    def setUp(self) -> None:
        self.PAYMENT_RECORD_CT_ID = ContentType.objects.get(app_label="payment", model="paymentrecord").id
        self.PAYMENT_CT_ID = ContentType.objects.get(app_label="payment", model="payment").id

        self.business_area = BusinessAreaFactory()
        self.program1 = ProgramFactory(name="program1", business_area=self.business_area, status=Program.ACTIVE)
        self.program2 = ProgramFactory(name="program2", business_area=self.business_area, status=Program.ACTIVE)
        self.program3 = ProgramFactory(name="program3", business_area=self.business_area, status=Program.ACTIVE)
        self.program4 = ProgramFactory(name="program4", business_area=self.business_area, status=Program.ACTIVE)

        self.create_complaint_tickets()

        self.create_sensitive_tickets()

        self.create_payment_verification_tickets()

        self.tickets_add_ind = self.create_hh_only_tickets(TicketAddIndividualDetailsFactory)

        self.tickets_delete_hh = self.create_hh_only_tickets(TicketDeleteHouseholdDetailsFactory)

        self.tickets_update_hh = self.create_hh_only_tickets(TicketHouseholdDataUpdateDetailsFactory)

        self.tickets_upd_ind_data = self.create_ind_only_tickets(
            TicketIndividualDataUpdateDetailsFactory, is_individual_data_update=True
        )

        self.tickets_delete_ind = self.create_ind_only_tickets(TicketDeleteIndividualDetailsFactory)

        self.tickets_sys_flagging = self.create_ind_only_tickets(
            TicketSystemFlaggingDetailsFactory,
            "golden_records_individual",
        )

        self.messages, self.messages_hh = self.create_messages()

        self.create_referral_tickets()

        self.create_needs_adjudication_tickets()

        self.create_feedback_closed()

        self.create_feedback_with_program()

        self.create_feedback_without_program_and_not_closed()

    def check_grievance_household_unicef_id(
        self, grievance_ticket: GrievanceTicket, household_unicef_id_expected: Optional[str]
    ) -> None:
        self.assertEqual(grievance_ticket.household_unicef_id, household_unicef_id_expected)

    def check_tickets_unicef_id_uniqueness(self, grievance_tickets: list, ticket_field: str = "ticket") -> None:
        ticket_unicef_ids = [getattr(t, ticket_field).unicef_id for t in grievance_tickets]
        self.assertEqual(
            len(ticket_unicef_ids),
            len(set(ticket_unicef_ids)),
        )

    def check_feedback_unicef_id_uniqueness(self, grievance_tickets: list) -> None:
        ticket_unicef_ids = [t.unicef_id for t in grievance_tickets]
        self.assertEqual(
            len(ticket_unicef_ids),
            len(set(ticket_unicef_ids)),
        )

    def check_created_at_equality(self, tickets: list, ticket_field: str = "ticket") -> None:
        self.assertTrue(all(t.created_at == tickets[0].created_at for t in tickets))
        if getattr(tickets[0], ticket_field) and ticket_field == "linked_grievance" or ticket_field == "ticket":
            self.assertTrue(
                all(
                    getattr(t, ticket_field).created_at == getattr(tickets[0], ticket_field).created_at for t in tickets
                )
            )
            notes_len = getattr(tickets[0], ticket_field).ticket_notes.count()
            documents_len = getattr(tickets[0], ticket_field).support_documents.count()
            for x in range(notes_len):
                self.assertTrue(
                    all(
                        getattr(t, ticket_field).ticket_notes.order_by("created_at")[x].created_at
                        == getattr(tickets[0], ticket_field).ticket_notes.order_by("created_at")[x].created_at
                        for t in tickets
                    )
                )
            for x in range(documents_len):
                self.assertTrue(
                    all(
                        getattr(t, ticket_field).support_documents.order_by("created_at")[x].created_at
                        == getattr(tickets[0], ticket_field).support_documents.order_by("created_at")[x].created_at
                        for t in tickets
                    )
                )

    def create_household_with_representations(
        self,
        original_program: Program,
        representations_programs: Optional[list[Program]] = None,
    ) -> Household:
        if not representations_programs:
            representations_programs = []
        individual = IndividualFactory(household=None, business_area=self.business_area)
        original_household = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=individual,
            program=original_program,
        )
        original_household.copied_from = original_household
        original_household.origin_unicef_id = original_household.unicef_id
        original_household.save()

        for program in representations_programs:
            individual = IndividualFactory(household=None, business_area=self.business_area)
            HouseholdFactory(
                business_area=self.business_area,
                head_of_household=individual,
                copied_from=original_household,
                origin_unicef_id=original_household.unicef_id,
                program=program,
            )

        original_household.refresh_from_db()
        return original_household

    def create_individual_with_representations(
        self,
        original_program: Program,
        representations_programs: Optional[list[Program]] = None,
    ) -> Individual:
        if not representations_programs:
            representations_programs = []
        original_individual = IndividualFactory(
            business_area=self.business_area,
            household=None,
            program=original_program,
        )
        original_individual.copied_from = original_individual
        original_individual.origin_unicef_id = original_individual.unicef_id
        original_individual.save()

        for program in representations_programs:
            IndividualFactory(
                household=None,
                business_area=self.business_area,
                copied_from=original_individual,
                origin_unicef_id=original_individual.unicef_id,
                program=program,
            )

        original_individual.refresh_from_db()
        return original_individual

    def create_role_individual_with_representations(
        self,
        individual: Individual,
        original_program: Program,
        representations_programs: Optional[list[Program]] = None,
        role: str = ROLE_PRIMARY,
    ) -> tuple[IndividualRoleInHousehold, dict[str, IndividualRoleInHousehold]]:
        original_household = self.create_household_with_representations(original_program, representations_programs)
        if not representations_programs:
            representations_programs = []

        original_role = IndividualRoleInHouseholdFactory(
            individual=individual.copied_to.get(program=original_program),
            household=original_household.copied_to.get(program=original_program),
            role=role,
        )

        roles_in_programs = {}
        for program in representations_programs:
            roles_in_programs[program.id] = IndividualRoleInHouseholdFactory(
                individual=individual.copied_to.get(program=program),
                household=original_household.copied_to.get(program=program),
                role=role,
            )
        return original_role, roles_in_programs

    def create_complaint_tickets(self) -> None:
        # ComplaintTicketDetails with payment in pr1, with HH in pr1 and IND in pr3 with representation in pr1
        household_pr1 = self.create_household_with_representations(self.program1)
        self.individual_complaint_ticket_with_payment = self.create_individual_with_representations(
            self.program3,
            [self.program1],
        )

        target_population1 = TargetPopulationFactory(program=self.program1)
        payment_plan = PaymentPlanFactory(target_population=target_population1)
        payment = PaymentFactory(parent=payment_plan)

        self.complaint_ticket_with_payment = GrievanceComplaintTicketWithoutExtrasFactory(
            household=household_pr1,
            individual=self.individual_complaint_ticket_with_payment,
            payment_object_id=payment.id,
            payment_content_type_id=self.PAYMENT_CT_ID,
        )

        # ComplaintTicketDetails with payment_record in pr2, with HH in pr3 with representation in pr2
        household_pr3 = self.create_household_with_representations(self.program3, [self.program2])
        target_population2 = TargetPopulationFactory(program=self.program2)
        payment_record = PaymentRecordFactory(target_population=target_population2, household=household_pr3)

        self.complaint_ticket_with_payment_record = GrievanceComplaintTicketWithoutExtrasFactory(
            household=household_pr3,
            individual=None,
            payment_object_id=payment_record.id,
            payment_content_type_id=self.PAYMENT_RECORD_CT_ID,
        )

        # ComplaintTicketDetails without payment_obj
        # GT is Closed, no HH and no IND
        self.complaint_ticket_no_payment_no_hh_no_ind_closed_gt = GrievanceComplaintTicketWithoutExtrasFactory(
            household=None,
            individual=None,
            payment_object_id=None,
            payment_content_type_id=None,
        )
        self.complaint_ticket_no_payment_no_hh_no_ind_closed_gt.ticket.status = GrievanceTicket.STATUS_CLOSED
        self.complaint_ticket_no_payment_no_hh_no_ind_closed_gt.ticket.save()

        # GT is Closed, HH in pr1, and IND in pr3 with representation in pr1, pr2
        household_pr1 = self.create_household_with_representations(self.program1)
        self.individual_complaint_ticket_no_payment_closed_gt = self.create_individual_with_representations(
            self.program3,
            [self.program1, self.program2],
        )
        self.complaint_ticket_no_payment_closed_gt = GrievanceComplaintTicketWithoutExtrasFactory(
            household=household_pr1,
            individual=self.individual_complaint_ticket_no_payment_closed_gt,
            payment_object_id=None,
            payment_content_type_id=None,
        )
        self.complaint_ticket_no_payment_closed_gt.ticket.status = GrievanceTicket.STATUS_CLOSED
        self.complaint_ticket_no_payment_closed_gt.ticket.save()

        # GT is Closed, HH in p1 and repr in pr2
        self.household_complaint_ticket_no_payment_closed_gt_only_hh = self.create_household_with_representations(
            self.program1,
            [self.program2],
        )
        self.complaint_ticket_no_payment_closed_gt_only_hh = GrievanceComplaintTicketWithoutExtrasFactory(
            household=self.household_complaint_ticket_no_payment_closed_gt_only_hh,
            individual=None,
            payment_object_id=None,
            payment_content_type_id=None,
        )
        self.complaint_ticket_no_payment_closed_gt_only_hh.ticket.status = GrievanceTicket.STATUS_CLOSED
        self.complaint_ticket_no_payment_closed_gt_only_hh.ticket.save()

        # GT is not Closed, HH in p1 and repr in pr2
        self.household_complaint_ticket_no_payment_only_hh = self.create_household_with_representations(
            self.program1,
            [self.program2],
        )
        self.complaint_ticket_no_payment_only_hh = GrievanceComplaintTicketWithoutExtrasFactory(
            household=self.household_complaint_ticket_no_payment_only_hh,
            individual=None,
            payment_object_id=None,
            payment_content_type_id=None,
        )
        self.complaint_ticket_no_payment_only_hh.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        self.complaint_ticket_no_payment_only_hh.ticket.save()

        # GT is not Closed and has 2 documents and 1 note, hh in p1 with repr in pr2, ind in pr3 with repr in pr1, pr2
        self.household_complaint_ticket_no_payment_not_closed_gt = self.create_household_with_representations(
            self.program1,
            [self.program2],
        )
        self.individual_complaint_ticket_no_payment_not_closed_gt = self.create_individual_with_representations(
            self.program3,
            [self.program1, self.program2],
        )

        self.complaint_ticket_no_payment_not_closed_gt = GrievanceComplaintTicketWithoutExtrasFactory(
            household=self.household_complaint_ticket_no_payment_not_closed_gt,
            individual=self.individual_complaint_ticket_no_payment_not_closed_gt,
            payment_object_id=None,
            payment_content_type_id=None,
        )
        grievance_ticket = self.complaint_ticket_no_payment_not_closed_gt.ticket
        grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        grievance_ticket.save()

        TicketNoteFactory(ticket=grievance_ticket)
        GrievanceDocumentFactory(grievance_ticket=grievance_ticket)
        GrievanceDocumentFactory(grievance_ticket=grievance_ticket)

        # GT is not Closed with note and document, no HH no IND
        self.complaint_ticket_no_payment_not_closed_gt_no_hh_no_ind = GrievanceComplaintTicketWithoutExtrasFactory(
            household=None,
            individual=None,
            payment_object_id=None,
            payment_content_type_id=None,
        )
        grievance_ticket = self.complaint_ticket_no_payment_not_closed_gt_no_hh_no_ind.ticket
        grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        grievance_ticket.save()

        TicketNoteFactory(ticket=grievance_ticket)
        GrievanceDocumentFactory(grievance_ticket=grievance_ticket)

    def create_sensitive_tickets(self) -> None:
        # TicketSensitiveDetails with payment in pr1, IND in pr1
        individual_pr1 = self.create_individual_with_representations(self.program1)

        target_population1 = TargetPopulationFactory(program=self.program1)
        payment_plan = PaymentPlanFactory(target_population=target_population1)
        payment = PaymentFactory(parent=payment_plan)

        self.sensitive_ticket_with_payment = SensitiveGrievanceTicketWithoutExtrasFactory(
            household=None,
            individual=individual_pr1,
            payment_obj=payment,
        )

        # TicketSensitiveDetails without payment_obj
        # GT is Closed, IND in pr1
        individual_pr1 = self.create_individual_with_representations(self.program1)
        self.sensitive_ticket_no_payment_closed_gt = SensitiveGrievanceTicketWithoutExtrasFactory(
            household=None,
            individual=individual_pr1,
            payment_obj=None,
        )
        self.sensitive_ticket_no_payment_closed_gt.ticket.status = GrievanceTicket.STATUS_CLOSED
        self.sensitive_ticket_no_payment_closed_gt.ticket.save()

        # GT is not Closed and has 2 notes and 1 document and is linked to
        # self.complaint_ticket_no_payment_not_closed_gt.ticket, IND in pr1 with repr in pr2
        self.individual_sensitive_ticket_no_payment_not_closed_gt = self.create_individual_with_representations(
            self.program1, [self.program2]
        )
        self.sensitive_ticket_no_payment_not_closed_gt = SensitiveGrievanceTicketWithoutExtrasFactory(
            household=None,
            individual=self.individual_sensitive_ticket_no_payment_not_closed_gt,
            payment_obj=None,
        )
        grievance_ticket = self.sensitive_ticket_no_payment_not_closed_gt.ticket
        grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        grievance_ticket.save()
        grievance_ticket.linked_tickets.add(self.complaint_ticket_no_payment_not_closed_gt.ticket)

        TicketNoteFactory(ticket=grievance_ticket)
        TicketNoteFactory(ticket=grievance_ticket)
        GrievanceDocumentFactory(grievance_ticket=grievance_ticket)

        # TicketSensitiveDetails with payment_record in pr2, HH in pr1 with repr in pr2, IND in pr3 with repr in pr2
        self.household_sensitive_ticket_with_payment_record = self.create_household_with_representations(
            self.program1,
            [self.program2],
        )
        self.individual_sensitive_ticket_with_payment_record = self.create_individual_with_representations(
            self.program3,
            [self.program2],
        )
        target_population2 = TargetPopulationFactory(program=self.program2)
        payment_record = PaymentRecordFactory(
            target_population=target_population2,
            household=self.household_sensitive_ticket_with_payment_record,
        )
        self.sensitive_ticket_with_payment_record = SensitiveGrievanceTicketWithoutExtrasFactory(
            household=self.household_sensitive_ticket_with_payment_record,
            individual=self.individual_sensitive_ticket_with_payment_record,
            payment_obj=payment_record,
        )
        # TicketSensitiveDetails with no payment, GT not Closed, HH in pr1 with repr pr2, pr3, IND in pr2 with repr pr3
        self.household_sensitive_ticket_no_payment_not_closed_3hh_2ind = self.create_household_with_representations(
            self.program1,
            [self.program2, self.program3],
        )
        self.individual_sensitive_ticket_no_payment_not_closed_3hh_2ind = self.create_individual_with_representations(
            self.program2,
            [self.program3],
        )
        self.sensitive_ticket_no_payment_not_closed_3hh_2ind = SensitiveGrievanceTicketWithoutExtrasFactory(
            household=self.household_sensitive_ticket_no_payment_not_closed_3hh_2ind,
            individual=self.individual_sensitive_ticket_no_payment_not_closed_3hh_2ind,
            payment_obj=None,
        )
        grievance_ticket = self.sensitive_ticket_no_payment_not_closed_3hh_2ind.ticket
        grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        grievance_ticket.save()

        TicketNoteFactory(ticket=grievance_ticket)
        TicketNoteFactory(ticket=grievance_ticket)
        GrievanceDocumentFactory(grievance_ticket=grievance_ticket)
        GrievanceDocumentFactory(grievance_ticket=grievance_ticket)

    def create_payment_verification_tickets(self) -> None:
        PaymentVerificationPlanFactory()
        # TicketPaymentVerificationDetails with payment_verification with payment_record
        household_pr1 = self.create_household_with_representations(self.program1)
        target_population1 = TargetPopulationFactory(program=self.program1)
        payment_record = PaymentRecordFactory(target_population=target_population1, household=household_pr1)
        payment_verification1 = PaymentVerificationFactory(
            generic_fk_obj=payment_record,
            payment_object_id=payment_record.id,
            payment_content_type=ContentType.objects.get_for_model(payment_record),
        )
        self.payment_verification_ticket_with_payment_record = TicketPaymentVerificationDetailsFactory(
            payment_verification=payment_verification1,
        )
        self.payment_verification_ticket_with_payment_record.ticket.linked_tickets.add(
            self.sensitive_ticket_no_payment_not_closed_gt.ticket
        )

        # TicketPaymentVerificationDetails with payment with payment_record
        target_population2 = TargetPopulationFactory(program=self.program2)
        payment_plan = PaymentPlanFactory(target_population=target_population2)
        payment = PaymentFactory(parent=payment_plan)
        payment_verification2 = PaymentVerificationFactory(
            generic_fk_obj=payment,
            payment_object_id=payment.id,
            payment_content_type=ContentType.objects.get_for_model(payment),
        )
        self.payment_verification_ticket_with_payment = TicketPaymentVerificationDetailsFactory(
            payment_verification=payment_verification2,
        )

        # TicketPaymentVerificationDetails without payment_verification
        self.payment_verification_ticket_no_payment_verification = TicketPaymentVerificationDetailsFactory(
            payment_verification=None,
        )

    def create_hh_only_tickets(self, factory_model: Any) -> tuple:
        # GT closed, no hh
        ticket_closed_no_hh = factory_model()
        ticket_closed_no_hh.ticket.status = GrievanceTicket.STATUS_CLOSED
        ticket_closed_no_hh.ticket.save()

        # GT closed, 2 hhs
        household = self.create_household_with_representations(self.program1, [self.program2])

        ticket_closed_2hh = factory_model(
            household=household,
        )
        ticket_closed_2hh.ticket.status = GrievanceTicket.STATUS_CLOSED
        ticket_closed_2hh.ticket.save()

        # GT not closed, no hh
        ticket_active_no_hh = factory_model()
        ticket_active_no_hh.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        ticket_active_no_hh.ticket.save()

        # GT not closed, 1 hh
        household = self.create_household_with_representations(self.program2)
        ticket_active_1hh = factory_model(
            household=household,
        )
        ticket_active_1hh.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        ticket_active_1hh.ticket.save()

        # GT not closed, 3 hhs, 2 notes and 2 docs
        household = self.create_household_with_representations(self.program1, [self.program2, self.program3])
        ticket_active_3hh_2notes_2docs = factory_model(
            household=household,
        )
        grievance_ticket = ticket_active_3hh_2notes_2docs.ticket
        grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        grievance_ticket.save()
        [TicketNoteFactory(ticket=grievance_ticket) for _ in range(2)]
        [GrievanceDocumentFactory(grievance_ticket=grievance_ticket) for _ in range(2)]

        return (
            ticket_closed_no_hh,
            ticket_closed_2hh,
            ticket_active_no_hh,
            ticket_active_1hh,
            ticket_active_3hh_2notes_2docs,
        )

    def create_ind_only_tickets(
        self, factory_model: Any, individual_field: str = "individual", is_individual_data_update: bool = False
    ) -> tuple:
        kwargs = {}
        if factory_model == TicketSystemFlaggingDetailsFactory:
            kwargs = {"sanction_list_individual": SanctionListIndividualFactory()}
        # GT closed, 2 ind
        individual = self.create_individual_with_representations(self.program1, [self.program2])
        individual_for_role = self.create_individual_with_representations(self.program1, [self.program2])
        original_role, other_roles = self.create_role_individual_with_representations(
            individual, self.program1, [self.program2]
        )

        ticket_closed_2ind_reassign_data = {
            str(original_role.id): {
                "household": encode_id_base64(original_role.household.id, "Household"),
                "individual": encode_id_base64(individual_for_role.id, "Individual"),
                "role": ROLE_PRIMARY,
            }
        }
        if is_individual_data_update:
            self.create_individual_related_data(individual, [self.program2])
            self.individual_data_ticket_closed_2ind = {"individual_data": self.create_individual_data_dict(individual)}
            individual_data = self.individual_data_ticket_closed_2ind
        else:
            individual_data = {}

        ticket_closed_2ind = factory_model(
            **{individual_field: individual},
            **kwargs,
            role_reassign_data=ticket_closed_2ind_reassign_data,
            **individual_data,
        )
        ticket_closed_2ind.ticket.status = GrievanceTicket.STATUS_CLOSED
        ticket_closed_2ind.ticket.save()

        # GT not closed, 1 ind
        individual = self.create_individual_with_representations(self.program2)

        (
            ticket_active_1ind_original_role,
            ticket_active_1ind_other_roles,
        ) = self.create_role_individual_with_representations(individual, self.program2)
        ticket_active_1ind_individual_for_role = self.create_individual_with_representations(self.program2)

        ticket_active_1ind_reassign_data = {
            str(ticket_active_1ind_original_role.id): {
                "household": encode_id_base64(ticket_active_1ind_original_role.household.id, "Household"),
                "individual": encode_id_base64(ticket_active_1ind_individual_for_role.id, "Individual"),
                "role": ROLE_PRIMARY,
            }
        }
        if is_individual_data_update:
            self.create_individual_related_data(individual, [])
            self.individual_data_ticket_active_1ind = {"individual_data": self.create_individual_data_dict(individual)}
            individual_data = self.individual_data_ticket_active_1ind
        else:
            individual_data = {}

        ticket_active_1ind = factory_model(
            **{individual_field: individual},
            **kwargs,
            role_reassign_data=ticket_active_1ind_reassign_data,
            **individual_data,
        )
        ticket_active_1ind.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        ticket_active_1ind.ticket.save()

        # GT not closed, 3 ind, 2 notes and 2 docs
        individual = self.create_individual_with_representations(self.program1, [self.program2, self.program3])
        (
            ticket_active_3ind_2notes_2docs_original_role,
            ticket_active_3ind_2notes_2docs_other_roles,
        ) = self.create_role_individual_with_representations(individual, self.program3, [self.program2, self.program1])
        ticket_active_3ind_2notes_2docs_individual_for_role = self.create_individual_with_representations(
            self.program1, [self.program2, self.program3]
        )
        ticket_active_3ind_2notes_2docs_reassign_data = {
            str(ticket_active_3ind_2notes_2docs_original_role.id): {
                "household": encode_id_base64(ticket_active_3ind_2notes_2docs_original_role.household.id, "Household"),
                "individual": encode_id_base64(ticket_active_3ind_2notes_2docs_individual_for_role.id, "Individual"),
                "role": ROLE_PRIMARY,
            },
            "HEAD": {
                "household": encode_id_base64(ticket_active_3ind_2notes_2docs_original_role.household.id, "Household"),
                "individual": encode_id_base64(ticket_active_3ind_2notes_2docs_individual_for_role.id, "Individual"),
                "role": HEAD,
            },
        }
        if is_individual_data_update:
            self.create_individual_related_data(individual, [self.program2, self.program3])
            self.individual_data_ticket_active_3ind_2notes_2docs = {
                "individual_data": self.create_individual_data_dict(individual)
            }
            individual_data = self.individual_data_ticket_active_3ind_2notes_2docs
        else:
            individual_data = {}
        ticket_active_3ind_2notes_2docs = factory_model(
            **{individual_field: individual},
            **kwargs,
            role_reassign_data=ticket_active_3ind_2notes_2docs_reassign_data,
            **individual_data,
        )
        grievance_ticket = ticket_active_3ind_2notes_2docs.ticket
        grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        grievance_ticket.save()
        [TicketNoteFactory(ticket=grievance_ticket) for _ in range(2)]
        [GrievanceDocumentFactory(grievance_ticket=grievance_ticket) for _ in range(2)]

        return (
            ticket_closed_2ind,
            ticket_closed_2ind_reassign_data,
            ticket_active_1ind,
            ticket_active_1ind_reassign_data,
            ticket_active_3ind_2notes_2docs,
            ticket_active_3ind_2notes_2docs_original_role,
            ticket_active_3ind_2notes_2docs_other_roles,
            ticket_active_3ind_2notes_2docs_individual_for_role,
        )

    def create_individual_data_dict(self, individual: Individual) -> dict:
        first_document = individual.documents.order_by("document_number").first()
        last_document = individual.documents.order_by("document_number").last()
        first_identity = individual.identities.order_by("number").first()
        last_identity = individual.identities.order_by("number").last()
        first_bank_account_info = individual.bank_account_info.order_by("bank_account_number").first()
        last_bank_account_info = individual.bank_account_info.order_by("bank_account_number").last()
        return {
            "documents_to_remove": [
                {
                    "value": encode_id_base64(first_document.id, "Document"),
                },
            ],
            "previous_documents": {
                encode_id_base64(first_document.id, "Document"): {
                    "id": encode_id_base64(first_document.id, "Document"),
                    "individual": encode_id_base64(individual.id, "Individual"),
                    "document_number": first_document.document_number,
                    "key": first_document.type.key,
                    "country": first_document.country.iso_code3,
                }
            },
            "documents_to_edit": [
                {
                    "previous_value": {
                        "country": last_document.country.iso_code3,
                        "id": encode_id_base64(last_document.id, "Document"),
                        "number": last_document.document_number,
                    },
                    "value": {
                        "country": "POL",
                        "id": encode_id_base64(last_document.id, "Document"),
                        "number": "789-789-646",
                    },
                },
            ],
            "identities_to_remove": [
                {
                    "value": encode_id_base64(first_identity.id, "IndividualIdentity"),
                },
            ],
            "previous_identities": {
                encode_id_base64(first_identity.id, "IndividualIdentity"): {
                    "id": encode_id_base64(first_identity.id, "IndividualIdentity"),
                    "individual": encode_id_base64(individual.id, "Individual"),
                    "number": first_identity.number,
                    "partner": first_identity.partner.name,
                    "country": first_identity.country.iso_code3,
                }
            },
            "identities_to_edit": [
                {
                    "previous_value": {
                        "country": last_identity.country.iso_code3,
                        "id": encode_id_base64(last_identity.id, "IndividualIdentity"),
                        "individual": encode_id_base64(individual.id, "Individual"),
                        "number": last_identity.number,
                        "partner": last_identity.partner.name,
                    },
                    "value": {
                        "country": "POL",
                        "id": encode_id_base64(last_identity.id, "IndividualIdentity"),
                        "individual": encode_id_base64(individual.id, "Individual"),
                        "number": "789-789-646",
                        "partner": "Partner",
                    },
                },
            ],
            "payment_channels_to_remove": [
                {
                    "value": encode_id_base64(first_bank_account_info.id, "BankAccountInfo"),
                }
            ],
            "previous_payment_channels": {
                encode_id_base64(first_bank_account_info.id, "BankAccountInfo"): {
                    "id": encode_id_base64(first_bank_account_info.id, "BankAccountInfo"),
                    "individual": encode_id_base64(individual.id, "Individual"),
                    "bank_name": first_bank_account_info.bank_name,
                    "bank_account_number": first_bank_account_info.bank_account_number,
                }
            },
            "payment_channels_to_edit": [
                {
                    "previous_value": {
                        "id": encode_id_base64(last_bank_account_info.id, "BankAccountInfo"),
                        "individual": encode_id_base64(individual.id, "Individual"),
                        "bank_name": last_bank_account_info.bank_name,
                        "bank_account_number": last_bank_account_info.bank_account_number,
                    },
                    "value": {
                        "id": encode_id_base64(last_bank_account_info.id, "BankAccountInfo"),
                        "individual": encode_id_base64(individual.id, "Individual"),
                        "bank_name": "Some name",
                        "bank_account_number": "111 111",
                    },
                },
            ],
        }

    def create_individual_related_data(
        self,
        individual: Individual,
        other_programs: list[Program],
    ) -> None:
        country = CountryFactory()
        partner = PartnerFactory()
        documents = [DocumentFactory(individual=individual, program=individual.program) for _ in range(2)]
        identities = [
            IndividualIdentityFactory(individual=individual, partner=partner, country=country) for _ in range(2)
        ]

        bank_accounts = [BankAccountInfoFactory(individual=individual) for _ in range(2)]
        for program in other_programs:
            individual_representation = individual.copied_to.get(program=program)
            [
                DocumentFactory(
                    individual=individual_representation,
                    document_number=d.document_number,
                    type=d.type,
                    country=d.country,
                    program=program,
                )
                for d in documents
            ]
            [
                IndividualIdentityFactory(
                    individual=individual_representation,
                    number=i.number,
                    partner=i.partner,
                    country=i.country,
                )
                for i in identities
            ]
            [
                BankAccountInfoFactory(
                    individual=individual_representation,
                    bank_name=b.bank_name,
                    bank_account_number=b.bank_account_number,
                )
                for b in bank_accounts
            ]

    def create_messages(self) -> tuple[list[Message], list[Household]]:
        # Message with target population
        hh1_1 = self.create_household_with_representations(self.program2, [self.program1])
        hh2_1 = self.create_household_with_representations(self.program1)
        hh3_1 = self.create_household_with_representations(self.program1, [self.program2, self.program3])
        hh4_1 = self.create_household_with_representations(self.program2)
        target_population = TargetPopulationFactory(program=self.program1)
        message_tp = CommunicationMessageFactory(
            target_population=target_population,
        )
        message_tp.households.set([hh1_1, hh2_1, hh3_1, hh4_1])

        # Message without target population
        hh1 = self.create_household_with_representations(self.program2, [self.program1])
        hh2 = self.create_household_with_representations(self.program1)
        hh3 = self.create_household_with_representations(self.program1, [self.program2, self.program3])
        hh4 = self.create_household_with_representations(self.program2)
        message_no_tp = CommunicationMessageFactory()
        message_no_tp.households.set([hh1, hh2, hh3, hh4])

        # Message without target population and without households
        message_no_tp_no_hh = CommunicationMessageFactory()
        return [message_tp, message_no_tp, message_no_tp_no_hh], [hh1, hh2, hh3, hh4]

    def create_referral_tickets(self) -> None:
        # GT closed, no hh no ind
        self.referral_closed_gt_no_hh_no_ind = ReferralTicketWithoutExtrasFactory()
        self.referral_closed_gt_no_hh_no_ind.ticket.status = GrievanceTicket.STATUS_CLOSED
        self.referral_closed_gt_no_hh_no_ind.ticket.save()

        # GT closed, hh in pr1 repr in pr2, ind in pr2 repr pr1
        self.household_referral_closed_gt_1hh_1ind = self.create_household_with_representations(
            self.program1, [self.program2]
        )
        self.individual_referral_closed_gt_1hh_1ind = self.create_individual_with_representations(
            self.program2, [self.program1]
        )
        self.referral_closed_gt_1hh_1ind = ReferralTicketWithoutExtrasFactory(
            household=self.household_referral_closed_gt_1hh_1ind,
            individual=self.individual_referral_closed_gt_1hh_1ind,
        )
        self.referral_closed_gt_1hh_1ind.ticket.status = GrievanceTicket.STATUS_CLOSED
        self.referral_closed_gt_1hh_1ind.ticket.save()

        # GT closed, no hh, ind in pr2
        individual = self.create_individual_with_representations(self.program2)
        self.referral_closed_gt_no_hh_1ind = ReferralTicketWithoutExtrasFactory(
            individual=individual,
        )
        self.referral_closed_gt_no_hh_1ind.ticket.status = GrievanceTicket.STATUS_CLOSED
        self.referral_closed_gt_no_hh_1ind.ticket.save()

        # GT closed, hh in pr3, no ind
        household = self.create_household_with_representations(self.program3)
        self.referral_closed_gt_1hh_no_ind = ReferralTicketWithoutExtrasFactory(
            household=household,
        )
        self.referral_closed_gt_1hh_no_ind.ticket.status = GrievanceTicket.STATUS_CLOSED
        self.referral_closed_gt_1hh_no_ind.ticket.save()

        # GT not closed, no hh no ind
        self.referral_active_gt_no_hh_no_ind = ReferralTicketWithoutExtrasFactory()
        self.referral_active_gt_no_hh_no_ind.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        self.referral_active_gt_no_hh_no_ind.ticket.save()

        # GT not closed 2 notes 2 docs, hh in pr1 repr in pr2, no ind
        self.household_referral_active_gt_1hh_2notes_2docs = self.create_household_with_representations(
            self.program1,
            [self.program2],
        )
        self.referral_active_gt_1hh_2notes_2docs = ReferralTicketWithoutExtrasFactory(
            household=self.household_referral_active_gt_1hh_2notes_2docs,
        )
        grievance_ticket = self.referral_active_gt_1hh_2notes_2docs.ticket
        grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        grievance_ticket.save()
        [TicketNoteFactory(ticket=grievance_ticket) for _ in range(2)]
        [GrievanceDocumentFactory(grievance_ticket=grievance_ticket) for _ in range(2)]

        # GT not closed, no hh, ind in pr3 repr in p2
        individual = self.create_individual_with_representations(self.program3, [self.program2])
        self.referral_active_gt_no_hh_1ind_2repr = ReferralTicketWithoutExtrasFactory(
            individual=individual,
        )
        self.referral_active_gt_no_hh_1ind_2repr.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        self.referral_active_gt_no_hh_1ind_2repr.ticket.save()

        # GT not closed, hh in pr1 repr pr2 pr3, ind in pr2 repr pr3
        self.household_referral_active_gt_1hh_1ind = self.create_household_with_representations(
            self.program1, [self.program2, self.program3]
        )
        self.individual_referral_active_gt_1hh_1ind = self.create_individual_with_representations(
            self.program2, [self.program3]
        )
        self.referral_active_gt_1hh_1ind = ReferralTicketWithoutExtrasFactory(
            household=self.household_referral_active_gt_1hh_1ind,
            individual=self.individual_referral_active_gt_1hh_1ind,
        )
        self.referral_active_gt_1hh_1ind.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        self.referral_active_gt_1hh_1ind.ticket.save()

        # GT not closed 2 docs 2 notes, hh in pr3 repr pr2, ind in pr1 repr in pr2 pr3
        self.household_referral_active_gt_1hh_1ind_2notes_2docs = self.create_household_with_representations(
            self.program3, [self.program2]
        )
        self.individual_referral_active_gt_1hh_1ind_2notes_2docs = self.create_individual_with_representations(
            self.program1, [self.program2, self.program3]
        )
        self.referral_active_gt_1hh_1ind_2notes_2docs = ReferralTicketWithoutExtrasFactory(
            household=self.household_referral_active_gt_1hh_1ind_2notes_2docs,
            individual=self.individual_referral_active_gt_1hh_1ind_2notes_2docs,
        )
        grievance_ticket = self.referral_active_gt_1hh_1ind_2notes_2docs.ticket
        grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        grievance_ticket.save()
        [TicketNoteFactory(ticket=grievance_ticket) for _ in range(2)]
        [GrievanceDocumentFactory(grievance_ticket=grievance_ticket) for _ in range(2)]

        # GT not closed, no hh, ind in pr1
        individual = self.create_individual_with_representations(self.program1)
        self.referral_active_gt_no_hh_1ind = ReferralTicketWithoutExtrasFactory(
            individual=individual,
        )
        self.referral_active_gt_no_hh_1ind.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        self.referral_active_gt_no_hh_1ind.ticket.save()

    def create_extra_data_for_needs_adjudication(self, golden_records_ids: list, possible_duplicates_ids: list) -> dict:
        data = {"golden_records": [], "possible_duplicate": []}

        for golden_record_id in golden_records_ids:
            data["golden_records"].append(
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(golden_record_id),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": "score",
                }
            )
        for possible_duplicate_id in possible_duplicates_ids:
            data["possible_duplicate"].append(
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(possible_duplicate_id),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": "score",
                },
            )
        return data

    def create_needs_adjudication_tickets(self) -> None:
        # GT not closed, golden ind pr1 repr pr3, selected ind 2 and 3
        self.golden_rec_needs_adjudication_not_closed = self.create_individual_with_representations(
            self.program1, [self.program3]
        )
        self.possible_dup1_needs_adjudication_not_closed = self.create_individual_with_representations(
            self.program2, [self.program1, self.program3]
        )
        self.possible_dup2_needs_adjudication_not_closed = self.create_individual_with_representations(
            self.program1, [self.program4]
        )
        self.possible_dup3_needs_adjudication_not_closed = self.create_individual_with_representations(self.program2)
        self.possible_dup4_needs_adjudication_not_closed = self.create_individual_with_representations(
            self.program3, [self.program2]
        )
        extra_data = self.create_extra_data_for_needs_adjudication(
            [self.golden_rec_needs_adjudication_not_closed.id],
            [self.possible_dup1_needs_adjudication_not_closed.id, self.possible_dup4_needs_adjudication_not_closed.id],
        )

        self.needs_adjudication_not_closed = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=self.golden_rec_needs_adjudication_not_closed,
            extra_data=extra_data,
        )
        self.needs_adjudication_not_closed.ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        self.needs_adjudication_not_closed.ticket.save()
        self.needs_adjudication_not_closed.possible_duplicates.set(
            [
                self.possible_dup1_needs_adjudication_not_closed,
                self.possible_dup2_needs_adjudication_not_closed,
                self.possible_dup3_needs_adjudication_not_closed,
                self.possible_dup4_needs_adjudication_not_closed,
            ]
        )
        self.needs_adjudication_not_closed.selected_individuals.set(
            [
                self.possible_dup2_needs_adjudication_not_closed,
                self.possible_dup3_needs_adjudication_not_closed,
            ]
        )
        # link the ticket with others
        self.needs_adjudication_not_closed.ticket.linked_tickets.add(
            self.sensitive_ticket_no_payment_not_closed_gt.ticket
        )
        self.needs_adjudication_not_closed.ticket.linked_tickets.add(
            self.payment_verification_ticket_with_payment_record.ticket
        )
        # GT closed, golden in pr4, selected ind 1 3 and 4
        self.golden_rec_needs_adjudication_closed = self.create_individual_with_representations(self.program4)
        self.possible_dup1_needs_adjudication_closed = self.create_individual_with_representations(
            self.program1, [self.program3]
        )
        self.possible_dup2_needs_adjudication_closed = self.create_individual_with_representations(self.program3)
        self.possible_dup3_needs_adjudication_closed = self.create_individual_with_representations(
            self.program2, [self.program1, self.program3]
        )
        self.possible_dup4_needs_adjudication_closed = self.create_individual_with_representations(
            self.program3, [self.program4]
        )
        self.needs_adjudication_closed = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=self.golden_rec_needs_adjudication_closed
        )
        self.needs_adjudication_closed.ticket.status = GrievanceTicket.STATUS_CLOSED
        self.needs_adjudication_closed.ticket.save()
        self.needs_adjudication_closed.possible_duplicates.set(
            [
                self.possible_dup1_needs_adjudication_closed,
                self.possible_dup2_needs_adjudication_closed,
                self.possible_dup3_needs_adjudication_closed,
                self.possible_dup4_needs_adjudication_closed,
            ]
        )
        self.needs_adjudication_closed.selected_individuals.set(
            [
                self.possible_dup1_needs_adjudication_closed,
                self.possible_dup3_needs_adjudication_closed,
                self.possible_dup4_needs_adjudication_closed,
            ]
        )

        # GT closed 2docs 2 notes, golden from pr1, selected ind 3 and 4
        self.golden_rec_needs_adjudication_closed_2docs_2notes = self.create_individual_with_representations(
            self.program1
        )
        self.possible_dup1_needs_adjudication_closed_2docs_2notes = self.create_individual_with_representations(
            self.program2
        )
        self.possible_dup2_needs_adjudication_closed_2docs_2notes = self.create_individual_with_representations(
            self.program3, [self.program2]
        )
        self.possible_dup3_needs_adjudication_closed_2docs_2notes = self.create_individual_with_representations(
            self.program2, [self.program3]
        )
        self.possible_dup4_needs_adjudication_closed_2docs_2notes = self.create_individual_with_representations(
            self.program4
        )
        self.needs_adjudication_closed_2docs_2notes = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=self.golden_rec_needs_adjudication_closed_2docs_2notes
        )
        grievance_ticket = self.needs_adjudication_closed_2docs_2notes.ticket
        grievance_ticket.status = GrievanceTicket.STATUS_CLOSED
        grievance_ticket.save()
        [TicketNoteFactory(ticket=grievance_ticket) for _ in range(2)]
        [GrievanceDocumentFactory(grievance_ticket=grievance_ticket) for _ in range(2)]

        self.needs_adjudication_closed_2docs_2notes.possible_duplicates.set(
            [
                self.possible_dup1_needs_adjudication_closed_2docs_2notes,
                self.possible_dup2_needs_adjudication_closed_2docs_2notes,
                self.possible_dup3_needs_adjudication_closed_2docs_2notes,
                self.possible_dup4_needs_adjudication_closed_2docs_2notes,
            ]
        )
        self.needs_adjudication_closed_2docs_2notes.selected_individuals.set(
            [
                self.possible_dup3_needs_adjudication_closed_2docs_2notes,
                self.possible_dup4_needs_adjudication_closed_2docs_2notes,
            ]
        )

        # golden in pr1, possible dup in pr2
        self.golden_rec_no_common_program = self.create_individual_with_representations(self.program1)
        self.possible_dup1_no_common_program = self.create_individual_with_representations(self.program2)
        self.needs_adjudication_no_common_program = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=self.golden_rec_no_common_program
        )

        self.needs_adjudication_no_common_program.possible_duplicates.set([self.possible_dup1_no_common_program])

    def create_feedback_closed(self) -> None:
        # gt closed, hh in pr1 repr pr2, ind in pr2 repr pr1 pr3
        self.household_feedback_closed_2hh_3ind = self.create_household_with_representations(
            self.program1, [self.program2]
        )
        self.individual_feedback_closed_2hh_3ind = self.create_individual_with_representations(
            self.program2, [self.program1, self.program3]
        )

        self.feedback_closed_2hh_3ind = FeedbackFactory(
            household_lookup=self.household_feedback_closed_2hh_3ind,
            individual_lookup=self.individual_feedback_closed_2hh_3ind,
        )
        self.feedback_closed_2hh_3ind.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_CLOSED,
        )
        self.feedback_closed_2hh_3ind.save()
        [FeedbackMessageFactory(feedback=self.feedback_closed_2hh_3ind) for _ in range(2)]

        # gt closed, no hh no ind
        self.feedback_closed_no_hh_no_ind = FeedbackFactory()
        self.feedback_closed_no_hh_no_ind.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_CLOSED,
        )
        self.feedback_closed_no_hh_no_ind.save()

        # gt closed, hh in pr1, ind in pr1
        self.household_feedback_closed_1hh_1ind_same_program = self.create_household_with_representations(self.program1)
        self.individual_feedback_closed_1hh_1ind_same_program = self.create_individual_with_representations(
            self.program1
        )
        self.feedback_closed_1hh_1ind_same_program = FeedbackFactory(
            household_lookup=self.household_feedback_closed_1hh_1ind_same_program,
            individual_lookup=self.individual_feedback_closed_1hh_1ind_same_program,
        )
        self.feedback_closed_1hh_1ind_same_program.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_CLOSED,
        )
        self.feedback_closed_1hh_1ind_same_program.save()
        # gt closed, hh in pr1, ind in pr2, repr pr1
        self.household_feedback_closed_1hh_1ind_diff_program_with_repr = self.create_household_with_representations(
            self.program1
        )
        self.individual_feedback_closed_1hh_1ind_diff_program_with_repr = self.create_individual_with_representations(
            self.program2, [self.program1]
        )
        self.feedback_closed_1hh_1ind_diff_program_with_repr = FeedbackFactory(
            household_lookup=self.household_feedback_closed_1hh_1ind_diff_program_with_repr,
            individual_lookup=self.individual_feedback_closed_1hh_1ind_diff_program_with_repr,
        )
        self.feedback_closed_1hh_1ind_diff_program_with_repr.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_CLOSED,
        )
        self.feedback_closed_1hh_1ind_diff_program_with_repr.save()

        # gt closed, hh in pr1
        self.household_feedback_closed_only_hh = self.create_household_with_representations(self.program1)
        self.feedback_closed_only_hh = FeedbackFactory(
            household_lookup=self.household_feedback_closed_only_hh,
        )
        self.feedback_closed_only_hh.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_CLOSED,
        )
        self.feedback_closed_only_hh.save()

        # gt closed, ind in pr1
        self.individual_feedback_closed_only_ind = self.create_individual_with_representations(self.program1)
        self.feedback_closed_only_ind = FeedbackFactory(
            individual_lookup=self.individual_feedback_closed_only_ind,
        )
        self.feedback_closed_only_ind.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_CLOSED,
        )
        self.feedback_closed_only_ind.save()

        # gt closed, hh in pr1, ind in pr2
        self.household_feedback_closed_1hh_1ind_diff_program = self.create_household_with_representations(self.program1)
        self.individual_feedback_closed_1hh_1ind_diff_program = self.create_individual_with_representations(
            self.program2
        )
        self.feedback_closed_1hh_1ind_diff_program = FeedbackFactory(
            household_lookup=self.household_feedback_closed_1hh_1ind_diff_program,
            individual_lookup=self.individual_feedback_closed_1hh_1ind_diff_program,
        )
        self.feedback_closed_1hh_1ind_diff_program.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_CLOSED,
        )
        self.feedback_closed_1hh_1ind_diff_program.save()

    def create_feedback_with_program(self) -> None:
        # gt closed, hh in pr1 repr pr3, ind in pr2 repr pr1 pr3, feedback in pr3
        self.household_feedback_closed_2hh_3ind_in_pr3 = self.create_household_with_representations(
            self.program1,
            [self.program3],
        )
        self.individual_feedback_closed_2hh_3ind_in_pr3 = self.create_individual_with_representations(
            self.program2,
            [self.program1, self.program3],
        )

        self.feedback_closed_2hh_3ind_in_pr3 = FeedbackFactory(
            household_lookup=self.household_feedback_closed_2hh_3ind_in_pr3,
            individual_lookup=self.individual_feedback_closed_2hh_3ind_in_pr3,
            program=self.program3,
        )

        self.feedback_closed_2hh_3ind_in_pr3.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_CLOSED,
        )
        self.feedback_closed_2hh_3ind_in_pr3.save()
        [FeedbackMessageFactory(feedback=self.feedback_closed_2hh_3ind_in_pr3) for _ in range(2)]

        # no gt, hh in pr1 repr pr3, ind in pr2 repr pr1 pr3, feedback in pr3
        self.household_feedback_no_gt_2hh_3ind_in_pr3 = self.create_household_with_representations(
            self.program1,
            [self.program3],
        )
        self.individual_feedback_no_gt_2hh_3ind_in_pr3 = self.create_individual_with_representations(
            self.program2,
            [self.program1, self.program3],
        )

        self.feedback_no_gt_2hh_3ind_in_pr3 = FeedbackFactory(
            household_lookup=self.household_feedback_no_gt_2hh_3ind_in_pr3,
            individual_lookup=self.individual_feedback_no_gt_2hh_3ind_in_pr3,
            program=self.program3,
        )

        # gt active , no hh no ind, feedback in pr1
        self.feedback_active_gt_no_hh_no_ind_in_pr1 = FeedbackFactory(
            program=self.program1,
        )
        self.feedback_active_gt_no_hh_no_ind_in_pr1.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
        self.feedback_active_gt_no_hh_no_ind_in_pr1.save()

        # gt active, ind in pr1 repr pr2, feedback in pr2
        self.individual_feedback_active_only_ind_in_pr2 = self.create_individual_with_representations(
            self.program1, [self.program2]
        )
        self.feedback_active_only_ind_in_pr2 = FeedbackFactory(
            individual_lookup=self.individual_feedback_active_only_ind_in_pr2,
            program=self.program2,
        )
        self.feedback_active_only_ind_in_pr2.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
        self.feedback_active_only_ind_in_pr2.save()

        # no gt, hh in pr2, ind in pr2 feedback in pr1
        self.household_feedback_no_gt_1hh_1ind_in_pr2 = self.create_household_with_representations(self.program2)
        self.individual_feedback_no_gt_1hh_1ind_in_pr2 = self.create_individual_with_representations(self.program2)
        self.feedback_no_gt_1hh_1ind_in_pr2 = FeedbackFactory(
            household_lookup=self.household_feedback_no_gt_1hh_1ind_in_pr2,
            individual_lookup=self.individual_feedback_no_gt_1hh_1ind_in_pr2,
            program=self.program1,
        )

    def create_feedback_without_program_and_not_closed(self) -> None:
        # without GT
        # no hh no ind
        self.feedback_no_program_no_gt_no_hh_no_ind = FeedbackFactory()

        # ind in pr1 repr pr2, no hh, 2 feedback messages
        self.individual_feedback_no_program_no_gt_no_hh_1ind = self.create_individual_with_representations(
            self.program1, [self.program2]
        )
        self.feedback_no_program_no_gt_no_hh_1ind = FeedbackFactory(
            individual_lookup=self.individual_feedback_no_program_no_gt_no_hh_1ind,
        )
        [FeedbackMessageFactory(feedback=self.feedback_no_program_no_gt_no_hh_1ind) for _ in range(2)]

        # hh in pr2 repr pr1, ind in pr1 repr pr2 pr3
        self.household_feedback_no_program_no_gt_2hh_3ind = self.create_household_with_representations(
            self.program2, [self.program1]
        )
        self.individual_feedback_no_program_no_gt_2hh_3ind = self.create_individual_with_representations(
            self.program1, [self.program2, self.program3]
        )
        self.feedback_no_program_no_gt_2hh_3ind = FeedbackFactory(
            household_lookup=self.household_feedback_no_program_no_gt_2hh_3ind,
            individual_lookup=self.individual_feedback_no_program_no_gt_2hh_3ind,
        )

        # hh in pr1, ind pr2
        self.household_feedback_no_program_no_gt_1hh_1ind = self.create_household_with_representations(self.program1)
        self.individual_feedback_no_program_no_gt_1hh_1ind = self.create_individual_with_representations(self.program2)
        self.feedback_no_program_no_gt_1hh_1ind = FeedbackFactory(
            household_lookup=self.household_feedback_no_program_no_gt_1hh_1ind,
            individual_lookup=self.individual_feedback_no_program_no_gt_1hh_1ind,
        )

        # GT active, hh in pr1 repr pr2, no ind
        self.household_feedback_active_gt_no_program_2hh_no_ind = self.create_household_with_representations(
            self.program1, [self.program2]
        )

        self.feedback_active_gt_no_program_2hh_no_ind = FeedbackFactory(
            household_lookup=self.household_feedback_active_gt_no_program_2hh_no_ind,
        )
        self.feedback_active_gt_no_program_2hh_no_ind.linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
        self.feedback_active_gt_no_program_2hh_no_ind.save()

        # GT active, hh in pr1 repr pr2 pr3, ind in pr2 repr in pr3, 2 docs, 2 notes, 2 messages, linked
        self.household_feedback_active_gt_no_program_3hh_2ind = self.create_household_with_representations(
            self.program1, [self.program2, self.program3]
        )
        self.individual_feedback_active_gt_no_program_3hh_2ind = self.create_individual_with_representations(
            self.program2, [self.program3]
        )
        self.feedback_active_gt_no_program_3hh_2ind = FeedbackFactory(
            household_lookup=self.household_feedback_active_gt_no_program_3hh_2ind,
            individual_lookup=self.individual_feedback_active_gt_no_program_3hh_2ind,
        )
        linked_grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
        self.feedback_active_gt_no_program_3hh_2ind.linked_grievance = linked_grievance
        self.feedback_active_gt_no_program_3hh_2ind.save()
        [FeedbackMessageFactory(feedback=self.feedback_active_gt_no_program_3hh_2ind) for _ in range(2)]
        [TicketNoteFactory(ticket=linked_grievance) for _ in range(2)]
        [GrievanceDocumentFactory(grievance_ticket=linked_grievance) for _ in range(2)]
        linked_grievance.linked_tickets.add(self.sensitive_ticket_no_payment_not_closed_gt.ticket)

    def perform_test_on_hh_only_tickets(self, model: Any, objects: tuple) -> None:
        for obj in objects:
            obj.refresh_from_db()
        (
            ticket_closed_no_hh,
            ticket_closed_2hh,
            ticket_active_no_hh,
            ticket_active_1hh,
            ticket_active_3hh_2notes_2docs,
        ) = objects

        # ticket_closed_no_hh
        self.assertIsNone(ticket_closed_no_hh.household)
        self.assertEqual(
            ticket_closed_no_hh.ticket.programs.first().name,
            "Void Program",
        )

        # ticket_closed_2hh
        self.assertEqual(
            ticket_closed_2hh.household.program,
            self.program1,
        )
        self.assertEqual(
            ticket_closed_2hh.ticket.programs.first(),
            self.program1,
        )
        not_existing_ticket = model.objects.filter(
            household=ticket_closed_2hh.household.copied_to.get(program=self.program2),
        ).first()
        self.assertIsNone(not_existing_ticket)

        # ticket_active_no_hh
        self.assertEqual(
            ticket_active_no_hh.ticket.programs.first().name,
            "Void Program",
        )

        # ticket_active_1hh
        self.assertEqual(
            ticket_active_1hh.household.program,
            self.program2,
        )
        self.assertEqual(
            ticket_active_1hh.ticket.programs.first(),
            self.program2,
        )

        # ticket_active_3hh_2notes_2docs
        original_hh = ticket_active_3hh_2notes_2docs.household
        self.assertEqual(
            original_hh.program,
            self.program1,
        )
        self.assertEqual(
            ticket_active_3hh_2notes_2docs.ticket.programs.first(),
            self.program1,
        )
        self.assertEqual(
            ticket_active_3hh_2notes_2docs.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_active_3hh_2notes_2docs.ticket.support_documents.count(),
            2,
        )
        self.check_grievance_household_unicef_id(ticket_active_3hh_2notes_2docs.ticket, original_hh.unicef_id)

        copied_hh_pr2 = original_hh.copied_to.get(program=self.program2)
        copied_hh_pr3 = original_hh.copied_to.get(program=self.program3)
        ticket_active_3hh_2notes_2docs_pr2 = model.objects.filter(
            household=copied_hh_pr2,
        ).first()
        ticket_active_3hh_2notes_2docs_pr3 = model.objects.filter(
            household=copied_hh_pr3,
        ).first()

        self.assertEqual(
            ticket_active_3hh_2notes_2docs_pr2.ticket.programs.first(),
            self.program2,
        )
        self.assertEqual(
            ticket_active_3hh_2notes_2docs_pr2.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_active_3hh_2notes_2docs_pr2.ticket.support_documents.count(),
            2,
        )
        self.check_grievance_household_unicef_id(ticket_active_3hh_2notes_2docs_pr2.ticket, copied_hh_pr2.unicef_id)

        self.assertEqual(
            ticket_active_3hh_2notes_2docs_pr3.ticket.programs.first(),
            self.program3,
        )
        self.assertEqual(
            ticket_active_3hh_2notes_2docs_pr3.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_active_3hh_2notes_2docs_pr3.ticket.support_documents.count(),
            2,
        )
        self.check_grievance_household_unicef_id(ticket_active_3hh_2notes_2docs_pr3.ticket, copied_hh_pr3.unicef_id)
        self.check_tickets_unicef_id_uniqueness(
            [
                ticket_active_3hh_2notes_2docs,
                ticket_active_3hh_2notes_2docs_pr2,
                ticket_active_3hh_2notes_2docs_pr3,
            ]
        )
        self.check_created_at_equality(
            [
                ticket_active_3hh_2notes_2docs,
                ticket_active_3hh_2notes_2docs_pr2,
                ticket_active_3hh_2notes_2docs_pr3,
            ]
        )

    def perform_test_on_ind_only_tickets(
        self, model: Any, objects: tuple, individual_field: str = "individual", is_individual_data_update: bool = False
    ) -> None:
        (
            ticket_closed_2ind,
            ticket_closed_2ind_reassign_data,
            ticket_active_1ind,
            ticket_active_1ind_reassign_data,
            ticket_active_3ind_2notes_2docs,
            ticket_active_3ind_2notes_2docs_original_role,
            ticket_active_3ind_2notes_2docs_other_roles,
            ticket_active_3ind_2notes_2docs_individual_for_role,
        ) = objects
        ticket_closed_2ind.refresh_from_db()
        ticket_active_1ind.refresh_from_db()
        ticket_active_3ind_2notes_2docs.refresh_from_db()
        # ticket_closed_2ind
        self.assertEqual(
            getattr(ticket_closed_2ind, individual_field).program,
            self.program1,
        )
        self.assertEqual(
            ticket_closed_2ind.ticket.programs.first(),
            self.program1,
        )
        self.assertEqual(
            ticket_closed_2ind_reassign_data,
            ticket_closed_2ind.role_reassign_data,
        )
        not_existing_ticket = model.objects.filter(
            **{individual_field: getattr(ticket_closed_2ind, individual_field).copied_to.get(program=self.program2)},
        ).first()
        if is_individual_data_update:
            self.assertEqual(
                ticket_closed_2ind.individual_data, self.individual_data_ticket_closed_2ind["individual_data"]
            )
        self.assertIsNone(not_existing_ticket)

        # ticket_active_1ind
        self.assertEqual(
            getattr(ticket_active_1ind, individual_field).program,
            self.program2,
        )
        self.assertEqual(
            ticket_active_1ind.ticket.programs.first(),
            self.program2,
        )
        self.assertEqual(
            ticket_active_1ind.role_reassign_data,
            ticket_active_1ind_reassign_data,
        )
        if is_individual_data_update:
            self.assertEqual(
                ticket_active_1ind.individual_data, self.individual_data_ticket_active_1ind["individual_data"]
            )

        # ticket_active_3ind_2notes_2docs
        original_ind = getattr(ticket_active_3ind_2notes_2docs, individual_field)
        self.assertEqual(
            original_ind.program,
            self.program1,
        )
        self.assertEqual(
            ticket_active_3ind_2notes_2docs.ticket.programs.first(),
            self.program1,
        )
        self.assertEqual(
            ticket_active_3ind_2notes_2docs.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_active_3ind_2notes_2docs.ticket.support_documents.count(),
            2,
        )
        self.assertEqual(
            ticket_active_3ind_2notes_2docs.role_reassign_data,
            {
                str(ticket_active_3ind_2notes_2docs_other_roles[self.program1.id].id): {
                    "household": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_other_roles[self.program1.id].household.id,
                        "Household",
                    ),
                    "individual": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_individual_for_role.id,
                        "Individual",
                    ),
                    "role": ROLE_PRIMARY,
                },
                "HEAD": {
                    "household": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_other_roles[self.program1.id].household.id,
                        "Household",
                    ),
                    "individual": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_individual_for_role.id,
                        "Individual",
                    ),
                    "role": HEAD,
                },
            },
        )
        if is_individual_data_update:
            self.assertEqual(
                ticket_active_3ind_2notes_2docs.individual_data,
                self.individual_data_ticket_active_3ind_2notes_2docs["individual_data"],
            )
        self.check_grievance_household_unicef_id(ticket_active_3ind_2notes_2docs.ticket, None)

        copied_ind_pr2 = original_ind.copied_to.get(program=self.program2)
        copied_ind_pr3 = original_ind.copied_to.get(program=self.program3)
        ticket_active_3ind_2notes_2docs_pr2 = model.objects.filter(
            **{individual_field: copied_ind_pr2},
        ).first()
        ticket_active_3ind_2notes_2docs_pr3 = model.objects.filter(
            **{individual_field: copied_ind_pr3},
        ).first()

        self.assertEqual(
            ticket_active_3ind_2notes_2docs_pr2.ticket.programs.first(),
            self.program2,
        )
        self.assertEqual(
            ticket_active_3ind_2notes_2docs_pr2.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_active_3ind_2notes_2docs_pr2.ticket.support_documents.count(),
            2,
        )
        self.assertEqual(
            ticket_active_3ind_2notes_2docs_pr2.role_reassign_data,
            {
                str(ticket_active_3ind_2notes_2docs_other_roles[self.program2.id].pk): {
                    "household": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_other_roles[self.program2.id].household.id,
                        "Household",
                    ),
                    "individual": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_individual_for_role.copied_to.get(program=self.program2).id,
                        "Individual",
                    ),
                    "role": ROLE_PRIMARY,
                },
                "HEAD": {
                    "household": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_other_roles[self.program2.id].household.id,
                        "Household",
                    ),
                    "individual": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_individual_for_role.copied_to.get(program=self.program2).id,
                        "Individual",
                    ),
                    "role": HEAD,
                },
            },
        )
        if is_individual_data_update:
            self.assertEqual(
                ticket_active_3ind_2notes_2docs_pr2.individual_data, self.create_individual_data_dict(copied_ind_pr2)
            )
        self.check_grievance_household_unicef_id(ticket_active_3ind_2notes_2docs_pr2.ticket, None)

        self.assertEqual(
            ticket_active_3ind_2notes_2docs_pr3.ticket.programs.first(),
            self.program3,
        )
        self.assertEqual(
            ticket_active_3ind_2notes_2docs_pr3.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_active_3ind_2notes_2docs_pr3.ticket.support_documents.count(),
            2,
        )
        self.assertEqual(
            ticket_active_3ind_2notes_2docs_pr3.role_reassign_data,
            {
                str(ticket_active_3ind_2notes_2docs_original_role.id): {
                    "household": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_original_role.household.id,
                        "Household",
                    ),
                    "individual": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_individual_for_role.copied_to.get(program=self.program3).id,
                        "Individual",
                    ),
                    "role": ROLE_PRIMARY,
                },
                "HEAD": {
                    "household": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_original_role.household.id,
                        "Household",
                    ),
                    "individual": encode_id_base64(
                        ticket_active_3ind_2notes_2docs_individual_for_role.copied_to.get(program=self.program3).id,
                        "Individual",
                    ),
                    "role": HEAD,
                },
            },
        )
        if is_individual_data_update:
            self.assertEqual(
                ticket_active_3ind_2notes_2docs_pr3.individual_data,
                self.create_individual_data_dict(copied_ind_pr3),
            )
        self.check_grievance_household_unicef_id(ticket_active_3ind_2notes_2docs_pr3.ticket, None)
        self.check_tickets_unicef_id_uniqueness(
            [
                ticket_active_3ind_2notes_2docs,
                ticket_active_3ind_2notes_2docs_pr2,
                ticket_active_3ind_2notes_2docs_pr3,
            ]
        )
        self.check_created_at_equality(
            [
                ticket_active_3ind_2notes_2docs,
                ticket_active_3ind_2notes_2docs_pr2,
                ticket_active_3ind_2notes_2docs_pr3,
            ]
        )

    def refresh_objects(self) -> None:
        self.complaint_ticket_with_payment.refresh_from_db()
        self.complaint_ticket_with_payment_record.refresh_from_db()
        self.complaint_ticket_no_payment_no_hh_no_ind_closed_gt.refresh_from_db()
        self.complaint_ticket_no_payment_closed_gt.refresh_from_db()
        self.complaint_ticket_no_payment_not_closed_gt.refresh_from_db()
        self.complaint_ticket_no_payment_closed_gt_only_hh.refresh_from_db()
        self.sensitive_ticket_with_payment.refresh_from_db()
        self.sensitive_ticket_with_payment_record.refresh_from_db()
        self.payment_verification_ticket_with_payment_record.refresh_from_db()

        self.referral_closed_gt_no_hh_no_ind.refresh_from_db()
        self.referral_closed_gt_1hh_1ind.refresh_from_db()
        self.referral_closed_gt_no_hh_1ind.refresh_from_db()
        self.referral_closed_gt_1hh_no_ind.refresh_from_db()
        self.referral_active_gt_no_hh_no_ind.refresh_from_db()
        self.referral_active_gt_1hh_2notes_2docs.refresh_from_db()
        self.referral_active_gt_no_hh_1ind_2repr.refresh_from_db()
        self.referral_active_gt_1hh_1ind.refresh_from_db()
        self.referral_active_gt_1hh_1ind_2notes_2docs.refresh_from_db()
        self.referral_active_gt_no_hh_1ind.refresh_from_db()

        self.needs_adjudication_not_closed.refresh_from_db()
        self.needs_adjudication_closed.refresh_from_db()
        self.needs_adjudication_closed_2docs_2notes.refresh_from_db()

        self.feedback_closed_2hh_3ind.refresh_from_db()
        self.feedback_closed_no_hh_no_ind.refresh_from_db()
        self.feedback_closed_1hh_1ind_same_program.refresh_from_db()
        self.feedback_closed_1hh_1ind_diff_program_with_repr.refresh_from_db()
        self.feedback_closed_only_hh.refresh_from_db()
        self.feedback_closed_only_ind.refresh_from_db()
        self.feedback_closed_1hh_1ind_diff_program.refresh_from_db()
        self.feedback_closed_2hh_3ind_in_pr3.refresh_from_db()
        self.feedback_no_gt_2hh_3ind_in_pr3.refresh_from_db()
        self.feedback_active_gt_no_hh_no_ind_in_pr1.refresh_from_db()
        self.feedback_active_only_ind_in_pr2.refresh_from_db()
        self.feedback_no_gt_1hh_1ind_in_pr2.refresh_from_db()
        self.feedback_no_program_no_gt_no_hh_no_ind.refresh_from_db()
        self.feedback_no_program_no_gt_no_hh_1ind.refresh_from_db()
        self.feedback_no_program_no_gt_2hh_3ind.refresh_from_db()
        self.feedback_no_program_no_gt_1hh_1ind.refresh_from_db()
        self.feedback_active_gt_no_program_3hh_2ind.refresh_from_db()

    def _test_ticket_complaint_details(self) -> None:
        # Test complaint_ticket_with_payment
        self.assertEqual(
            self.complaint_ticket_with_payment.household.program,
            self.program1,
        )
        self.assertEqual(
            self.complaint_ticket_with_payment.individual.program,
            self.program1,
        )
        self.assertEqual(
            self.complaint_ticket_with_payment.individual.copied_from,
            self.individual_complaint_ticket_with_payment,
        )
        self.assertEqual(
            self.complaint_ticket_with_payment.ticket.programs.count(),
            1,
        )
        self.assertEqual(
            self.complaint_ticket_with_payment.ticket.programs.first(),
            self.program1,
        )
        self.check_grievance_household_unicef_id(
            self.complaint_ticket_with_payment.ticket,
            self.complaint_ticket_with_payment.household.unicef_id,
        )

        # Test complaint_ticket_with_payment_record
        self.assertEqual(
            self.complaint_ticket_with_payment_record.household.program,
            self.program2,
        )
        self.assertEqual(
            self.complaint_ticket_with_payment_record.individual,
            None,
        )
        self.assertEqual(
            self.complaint_ticket_with_payment_record.ticket.programs.first(),
            self.program2,
        )
        self.check_grievance_household_unicef_id(
            self.complaint_ticket_with_payment_record.ticket,
            self.complaint_ticket_with_payment_record.household.unicef_id,
        )

        # Test complaint_ticket_no_payment_no_hh_no_ind_closed_gt
        self.assertEqual(
            self.complaint_ticket_no_payment_no_hh_no_ind_closed_gt.household,
            None,
        )
        self.assertEqual(
            self.complaint_ticket_no_payment_no_hh_no_ind_closed_gt.individual,
            None,
        )
        self.assertEqual(
            self.complaint_ticket_no_payment_no_hh_no_ind_closed_gt.ticket.programs.first().name,
            "Void Program",
        )
        self.check_grievance_household_unicef_id(
            self.complaint_ticket_no_payment_no_hh_no_ind_closed_gt.ticket,
            None,
        )

        # Test complaint_ticket_no_payment_closed_gt
        self.assertEqual(
            self.complaint_ticket_no_payment_closed_gt.household.program,
            self.program1,
        )
        self.assertEqual(
            self.complaint_ticket_no_payment_closed_gt.individual.program,
            self.program1,
        )
        self.assertEqual(
            self.complaint_ticket_no_payment_closed_gt.individual.copied_from,
            self.individual_complaint_ticket_no_payment_closed_gt,
        )
        self.assertEqual(
            self.complaint_ticket_no_payment_closed_gt.ticket.programs.first(),
            self.program1,
        )
        self.check_grievance_household_unicef_id(
            self.complaint_ticket_no_payment_closed_gt.ticket,
            self.complaint_ticket_no_payment_closed_gt.household.unicef_id,
        )

        # Test complaint_ticket_no_payment_closed_gt_only_hh
        self.assertEqual(
            self.complaint_ticket_no_payment_closed_gt_only_hh.household,
            self.household_complaint_ticket_no_payment_closed_gt_only_hh,
        )
        self.assertEqual(
            self.complaint_ticket_no_payment_closed_gt_only_hh.ticket.programs.first(),
            self.program1,
        )
        not_existing_ticket = TicketComplaintDetails.objects.filter(
            household=self.household_complaint_ticket_no_payment_closed_gt_only_hh.copied_to.get(program=self.program2),
            individual=None,
        ).first()
        self.assertIsNone(not_existing_ticket)
        self.check_grievance_household_unicef_id(
            self.complaint_ticket_no_payment_closed_gt.ticket,
            self.complaint_ticket_no_payment_closed_gt.household.unicef_id,
        )

        # Test complaint_ticket_no_payment_only_hh
        ticker_pr1 = TicketComplaintDetails.objects.filter(
            household=self.household_complaint_ticket_no_payment_only_hh,
            individual=None,
        ).first()
        self.assertIsNotNone(ticker_pr1)
        self.assertEqual(
            ticker_pr1.ticket.programs.first(),
            self.program1,
        )
        self.assertEqual(
            ticker_pr1.ticket.programs.first(),
            self.household_complaint_ticket_no_payment_only_hh.program,
        )
        self.check_grievance_household_unicef_id(
            ticker_pr1.ticket,
            ticker_pr1.household.unicef_id,
        )

        ticker_pr2 = TicketComplaintDetails.objects.filter(
            household=self.household_complaint_ticket_no_payment_only_hh.copied_to.get(program=self.program2),
            individual=None,
        ).first()
        self.assertIsNotNone(ticker_pr2)
        self.assertEqual(
            ticker_pr2.ticket.programs.first(),
            self.program2,
        )
        self.check_grievance_household_unicef_id(
            ticker_pr2.ticket,
            ticker_pr2.household.unicef_id,
        )
        self.check_created_at_equality([ticker_pr1, ticker_pr2, self.complaint_ticket_no_payment_only_hh])

        self.check_tickets_unicef_id_uniqueness([ticker_pr1, ticker_pr2])

        # Test complaint_ticket_no_payment_not_closed_gt
        ticket_complaint_pr1 = TicketComplaintDetails.objects.filter(
            household=self.household_complaint_ticket_no_payment_not_closed_gt,
            individual=self.individual_complaint_ticket_no_payment_not_closed_gt.copied_to.get(program=self.program1),
        ).first()

        self.assertIsNotNone(ticket_complaint_pr1)
        self.assertEqual(
            ticket_complaint_pr1.ticket.programs.first(),
            self.program1,
        )
        self.assertEqual(
            ticket_complaint_pr1.ticket.ticket_notes.count(),
            1,
        )
        self.assertEqual(
            ticket_complaint_pr1.ticket.support_documents.count(),
            2,
        )
        self.check_grievance_household_unicef_id(
            ticket_complaint_pr1.ticket,
            ticket_complaint_pr1.household.unicef_id,
        )

        ticket_complaint_pr2 = TicketComplaintDetails.objects.filter(
            household=self.household_complaint_ticket_no_payment_not_closed_gt.copied_to.get(program=self.program2),
            individual=self.individual_complaint_ticket_no_payment_not_closed_gt.copied_to.get(program=self.program2),
        ).first()
        self.assertIsNotNone(ticket_complaint_pr2)
        self.assertEqual(
            ticket_complaint_pr2.ticket.programs.first(),
            self.program2,
        )
        self.assertEqual(
            ticket_complaint_pr2.ticket.ticket_notes.count(),
            1,
        )
        self.assertEqual(
            ticket_complaint_pr2.ticket.support_documents.count(),
            2,
        )
        self.check_grievance_household_unicef_id(
            ticket_complaint_pr2.ticket,
            ticket_complaint_pr2.household.unicef_id,
        )

        ticket_complaint_pr3 = TicketComplaintDetails.objects.filter(
            household=None,
            individual=self.individual_complaint_ticket_no_payment_not_closed_gt,
        ).first()
        self.assertIsNotNone(ticket_complaint_pr3)
        self.assertEqual(
            ticket_complaint_pr3.ticket.programs.first(),
            self.program3,
        )
        self.assertEqual(
            ticket_complaint_pr3.ticket.ticket_notes.count(),
            1,
        )
        self.assertEqual(
            ticket_complaint_pr3.ticket.support_documents.count(),
            2,
        )
        self.check_grievance_household_unicef_id(
            ticket_complaint_pr3.ticket,
            None,
        )
        self.check_created_at_equality(
            [
                ticket_complaint_pr1,
                ticket_complaint_pr2,
                ticket_complaint_pr3,
                self.complaint_ticket_no_payment_not_closed_gt,
            ]
        )

        self.assertIn(
            ticket_complaint_pr1.ticket,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )
        self.assertIn(
            ticket_complaint_pr2.ticket,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )
        self.assertIn(
            ticket_complaint_pr3.ticket,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )
        self.assertIn(
            self.payment_verification_ticket_with_payment_record.ticket,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )
        self.check_tickets_unicef_id_uniqueness([ticket_complaint_pr1, ticket_complaint_pr2, ticket_complaint_pr3])

        # Test TicketComplaintDetails complaint_ticket_no_payment_not_closed_gt_no_hh_no_ind
        self.assertIsNone(self.complaint_ticket_no_payment_not_closed_gt_no_hh_no_ind.household)
        self.assertIsNone(self.complaint_ticket_no_payment_not_closed_gt_no_hh_no_ind.individual)
        self.assertEqual(
            self.complaint_ticket_no_payment_not_closed_gt_no_hh_no_ind.ticket.programs.first().name,
            "Void Program",
        )
        self.assertEqual(
            self.complaint_ticket_no_payment_not_closed_gt_no_hh_no_ind.ticket.ticket_notes.count(),
            1,
        )
        self.assertEqual(
            self.complaint_ticket_no_payment_not_closed_gt_no_hh_no_ind.ticket.support_documents.count(),
            1,
        )
        self.check_grievance_household_unicef_id(
            self.complaint_ticket_no_payment_not_closed_gt_no_hh_no_ind.ticket,
            None,
        )

    def _test_ticket_sensitive_details(self) -> None:
        # Test TicketSensitiveDetails sensitive_ticket_with_payment
        self.assertIsNone(
            self.sensitive_ticket_with_payment.household,
        )
        self.assertEqual(
            self.sensitive_ticket_with_payment.individual.program,
            self.program1,
        )
        self.assertEqual(
            self.sensitive_ticket_with_payment.ticket.programs.first(),
            self.program1,
        )
        self.check_grievance_household_unicef_id(
            self.sensitive_ticket_with_payment.ticket,
            None,
        )

        # Test TicketSensitiveDetails sensitive_ticket_no_payment_closed_gt
        self.assertIsNone(self.sensitive_ticket_no_payment_closed_gt.household)
        self.assertEqual(
            self.sensitive_ticket_no_payment_closed_gt.individual.program,
            self.program1,
        )
        self.assertEqual(
            self.sensitive_ticket_no_payment_closed_gt.ticket.programs.first(),
            self.program1,
        )

        # Test TicketSensitiveDetails sensitive_ticket_no_payment_not_closed_gt
        ticket_sensitive_pr1 = TicketSensitiveDetails.objects.filter(
            household=None,
            individual=self.individual_sensitive_ticket_no_payment_not_closed_gt,
        ).first()

        self.assertIsNotNone(ticket_sensitive_pr1)
        self.assertEqual(
            ticket_sensitive_pr1.ticket.programs.first(),
            self.program1,
        )
        self.assertEqual(
            ticket_sensitive_pr1.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_sensitive_pr1.ticket.support_documents.count(),
            1,
        )

        ticket_sensitive_pr2 = TicketSensitiveDetails.objects.filter(
            household=None,
            individual=self.individual_sensitive_ticket_no_payment_not_closed_gt.copied_to.get(program=self.program2),
        ).first()
        self.assertIsNotNone(ticket_sensitive_pr2)
        self.assertEqual(
            ticket_sensitive_pr2.ticket.programs.first(),
            self.program2,
        )
        self.assertEqual(
            ticket_sensitive_pr1.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_sensitive_pr1.ticket.support_documents.count(),
            1,
        )

        self.assertNotEqual(
            ticket_sensitive_pr1.individual,
            ticket_sensitive_pr2.individual,
        )
        self.assertEqual(
            ticket_sensitive_pr2.individual.copied_from,
            ticket_sensitive_pr1.individual,
        )
        self.check_created_at_equality(
            [ticket_sensitive_pr1, ticket_sensitive_pr2, self.sensitive_ticket_no_payment_not_closed_gt]
        )

        # Test linked tickets
        self.assertEqual(
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.count(),
            11,
        )
        self.assertIn(
            ticket_sensitive_pr2.ticket,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )
        self.assertIn(
            self.feedback_active_gt_no_program_3hh_2ind.linked_grievance,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )
        self.assertIn(
            self.complaint_ticket_no_payment_not_closed_gt.ticket,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )
        self.assertIn(
            self.payment_verification_ticket_with_payment_record.ticket,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )
        self.assertIn(
            self.needs_adjudication_not_closed.ticket,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )

        self.assertEqual(
            ticket_sensitive_pr2.ticket.linked_tickets.count(),
            11,
        )
        self.assertIn(
            self.sensitive_ticket_no_payment_not_closed_gt.ticket,
            ticket_sensitive_pr2.ticket.linked_tickets.all(),
        )
        self.assertIn(
            self.complaint_ticket_no_payment_not_closed_gt.ticket,
            ticket_sensitive_pr2.ticket.linked_tickets.all(),
        )
        self.assertIn(
            self.payment_verification_ticket_with_payment_record.ticket,
            ticket_sensitive_pr2.ticket.linked_tickets.all(),
        )
        self.check_tickets_unicef_id_uniqueness([ticket_sensitive_pr1, ticket_sensitive_pr2])

        # Test TicketSensitiveDetails sensitive_ticket_with_payment_record
        self.assertEqual(
            self.sensitive_ticket_with_payment_record.household,
            self.household_sensitive_ticket_with_payment_record.copied_to.get(program=self.program2),
        )
        self.assertEqual(
            self.sensitive_ticket_with_payment_record.individual,
            self.individual_sensitive_ticket_with_payment_record.copied_to.get(program=self.program2),
        )
        self.assertEqual(
            self.sensitive_ticket_with_payment_record.ticket.programs.first(),
            self.program2,
        )
        self.check_grievance_household_unicef_id(
            self.sensitive_ticket_with_payment_record.ticket,
            self.household_sensitive_ticket_with_payment_record.copied_to.get(program=self.program2).unicef_id,
        )

        ticket_sensitive_pr1 = TicketSensitiveDetails.objects.filter(
            household=self.household_sensitive_ticket_with_payment_record, individual=None
        ).first()
        self.assertIsNone(ticket_sensitive_pr1)
        ticket_sensitive_p3 = TicketSensitiveDetails.objects.filter(
            household=None,
            individual=self.individual_sensitive_ticket_with_payment_record,
        ).first()
        self.assertIsNone(ticket_sensitive_p3)

        # Test sensitive_ticket_no_payment_not_closed_3hh_2ind
        ticket_sensitive_pr1 = TicketSensitiveDetails.objects.filter(
            household=self.household_sensitive_ticket_no_payment_not_closed_3hh_2ind, individual=None
        ).first()
        self.assertIsNotNone(ticket_sensitive_pr1)
        self.assertEqual(
            ticket_sensitive_pr1.ticket.programs.first(),
            self.program1,
        )
        self.assertEqual(
            ticket_sensitive_pr1.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_sensitive_pr1.ticket.support_documents.count(),
            2,
        )
        self.check_grievance_household_unicef_id(
            ticket_sensitive_pr1.ticket,
            self.household_sensitive_ticket_no_payment_not_closed_3hh_2ind.unicef_id,
        )
        ticket_sensitive_pr2 = TicketSensitiveDetails.objects.filter(
            household=self.household_sensitive_ticket_no_payment_not_closed_3hh_2ind.copied_to.get(
                program=self.program2
            ),
            individual=self.individual_sensitive_ticket_no_payment_not_closed_3hh_2ind,
        ).first()
        self.assertIsNotNone(ticket_sensitive_pr2)
        self.assertEqual(
            ticket_sensitive_pr2.ticket.programs.first(),
            self.program2,
        )
        self.assertEqual(
            ticket_sensitive_pr2.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_sensitive_pr2.ticket.support_documents.count(),
            2,
        )
        self.check_grievance_household_unicef_id(
            ticket_sensitive_pr2.ticket,
            ticket_sensitive_pr2.household.unicef_id,
        )

        ticket_sensitive_pr3 = TicketSensitiveDetails.objects.filter(
            household=self.household_sensitive_ticket_no_payment_not_closed_3hh_2ind.copied_to.get(
                program=self.program3
            ),
            individual=self.individual_sensitive_ticket_no_payment_not_closed_3hh_2ind.copied_to.get(
                program=self.program3
            ),
        ).first()
        self.assertIsNotNone(ticket_sensitive_pr3)
        self.assertEqual(
            ticket_sensitive_pr3.ticket.programs.first(),
            self.program3,
        )
        self.assertEqual(
            ticket_sensitive_pr3.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_sensitive_pr3.ticket.support_documents.count(),
            2,
        )
        self.check_grievance_household_unicef_id(
            ticket_sensitive_pr3.ticket,
            ticket_sensitive_pr3.household.unicef_id,
        )

        self.check_tickets_unicef_id_uniqueness([ticket_sensitive_pr1, ticket_sensitive_pr2, ticket_sensitive_pr3])
        self.check_created_at_equality(
            [
                ticket_sensitive_pr1,
                ticket_sensitive_pr2,
                ticket_sensitive_pr3,
                self.sensitive_ticket_no_payment_not_closed_3hh_2ind,
            ]
        )

    def _test_ticket_payment_verification_details(self) -> None:
        # Test payment_verification_ticket_with_payment_record
        self.assertEqual(
            self.payment_verification_ticket_with_payment_record.ticket.programs.first(),
            self.program1,
        )
        self.check_grievance_household_unicef_id(
            self.payment_verification_ticket_with_payment_record.ticket,
            self.payment_verification_ticket_with_payment_record.payment_verification.payment_obj.household.unicef_id,
        )

        self.assertIn(
            self.needs_adjudication_not_closed.ticket,
            self.payment_verification_ticket_with_payment_record.ticket.linked_tickets.all(),
        )
        self.assertIn(
            self.sensitive_ticket_no_payment_not_closed_gt.ticket,
            self.payment_verification_ticket_with_payment_record.ticket.linked_tickets.all(),
        )

        # Test payment_verification_ticket_with_payment
        self.assertEqual(
            self.payment_verification_ticket_with_payment.ticket.programs.first(),
            self.program2,
        )
        self.check_grievance_household_unicef_id(
            self.payment_verification_ticket_with_payment.ticket,
            self.payment_verification_ticket_with_payment.payment_verification.payment_obj.household.unicef_id,
        )

        # Test payment_verification_ticket_no_payment_verification
        self.assertEqual(
            self.payment_verification_ticket_no_payment_verification.ticket.programs.first().name,
            "Void Program",
        )
        self.check_grievance_household_unicef_id(
            self.payment_verification_ticket_no_payment_verification.ticket,
            None,
        )

    def _test_ticket_add_individual_details(self) -> None:
        self.perform_test_on_hh_only_tickets(TicketAddIndividualDetails, self.tickets_add_ind)

    def _test_ticket_delete_household_details(self) -> None:
        self.perform_test_on_hh_only_tickets(TicketDeleteHouseholdDetails, self.tickets_delete_hh)

    def _test_ticket_update_household_details(self) -> None:
        self.perform_test_on_hh_only_tickets(TicketHouseholdDataUpdateDetails, self.tickets_update_hh)

    def _test_ticket_upd_individual_details(self) -> None:
        self.perform_test_on_ind_only_tickets(
            TicketIndividualDataUpdateDetails, self.tickets_upd_ind_data, is_individual_data_update=True
        )

    def _test_ticket_delete_individual_details(self) -> None:
        self.perform_test_on_ind_only_tickets(TicketDeleteIndividualDetails, self.tickets_delete_ind)

    def _test_ticket_system_flagging_details(self) -> None:
        self.perform_test_on_ind_only_tickets(
            TicketSystemFlaggingDetails,
            self.tickets_sys_flagging,
            individual_field="golden_records_individual",
        )

    def _test_message(self) -> None:
        message_tp, message_no_tp, message_no_tp_no_hh = self.messages
        message_tp.refresh_from_db()
        message_no_tp.refresh_from_db()
        message_no_tp_no_hh.refresh_from_db()
        hh1, hh2, hh3, hh4 = self.messages_hh

        # message_tp
        self.assertEqual(message_tp.households.count(), 3)
        for hh in message_tp.households.all():
            self.assertEqual(hh.program, self.program1)
        self.assertEqual(message_tp.program, self.program1)

        # message_no_tp
        message_pr1 = Message.objects.filter(
            households__in=[hh1.copied_to.get(program=self.program1), hh2, hh3]
        ).first()
        self.assertIsNotNone(message_pr1)
        self.assertEqual(message_pr1.households.count(), 3)
        self.assertEqual(message_pr1.program, self.program1)

        message_pr2 = Message.objects.filter(
            households__in=[hh1.copied_to.get(program=self.program2), hh4, hh3.copied_to.get(program=self.program2)]
        ).first()
        self.assertIsNotNone(message_pr2)
        self.assertEqual(message_pr2.households.count(), 3)
        self.assertEqual(message_pr2.program, self.program2)

        message_pr3 = Message.objects.filter(households__in=[hh3.copied_to.get(program=self.program3)]).first()
        self.assertIsNotNone(message_pr3)
        self.assertEqual(message_pr3.households.count(), 1)
        self.assertEqual(message_pr3.program, self.program3)

        assert message_pr1.created_at == message_pr2.created_at == message_pr3.created_at
        self.assertNotEqual(message_pr1.unicef_id, message_pr2.unicef_id)
        self.assertNotEqual(message_pr2.unicef_id, message_pr3.unicef_id)
        self.assertNotEqual(message_pr1.unicef_id, message_pr3.unicef_id)

        # message_no_tp_no_hh
        self.assertEqual(message_no_tp_no_hh.households.count(), 0)
        self.assertEqual(message_no_tp_no_hh.program.name, "Void Program")

    def _test_ticket_referral_details(self) -> None:
        # Test referral_closed_gt_no_hh_no_ind
        self.assertEqual(
            self.referral_closed_gt_no_hh_no_ind.ticket.programs.first().name,
            "Void Program",
        )
        self.check_grievance_household_unicef_id(self.referral_closed_gt_no_hh_no_ind.ticket, None)

        # Test referral_closed_gt_1hh_1ind
        self.assertEqual(
            self.referral_closed_gt_1hh_1ind.ticket.programs.first(),
            self.program1,
        )
        self.check_grievance_household_unicef_id(
            self.referral_closed_gt_1hh_1ind.ticket,
            self.referral_closed_gt_1hh_1ind.household.unicef_id,
        )
        self.assertEqual(
            self.referral_closed_gt_1hh_1ind.household.program,
            self.program1,
        )
        self.assertEqual(self.referral_closed_gt_1hh_1ind.household, self.household_referral_closed_gt_1hh_1ind)
        self.assertEqual(
            self.referral_closed_gt_1hh_1ind.individual.program,
            self.program1,
        )
        self.assertEqual(
            self.referral_closed_gt_1hh_1ind.individual.copied_from, self.individual_referral_closed_gt_1hh_1ind
        )
        self.assertNotEqual(self.referral_closed_gt_1hh_1ind.individual, self.individual_referral_closed_gt_1hh_1ind)

        # Test referral_closed_gt_no_hh_1ind
        self.assertEqual(
            self.referral_closed_gt_no_hh_1ind.ticket.programs.first(),
            self.program2,
        )
        self.check_grievance_household_unicef_id(
            self.referral_closed_gt_no_hh_1ind.ticket,
            None,
        )
        self.assertIsNotNone(self.referral_closed_gt_no_hh_1ind.individual)
        self.assertIsNone(self.referral_closed_gt_no_hh_1ind.household)

        # Test referral_closed_gt_1hh_no_ind
        self.assertEqual(
            self.referral_closed_gt_1hh_no_ind.ticket.programs.first(),
            self.program3,
        )
        self.check_grievance_household_unicef_id(
            self.referral_closed_gt_1hh_no_ind.ticket,
            self.referral_closed_gt_1hh_no_ind.household.unicef_id,
        )
        self.assertIsNotNone(self.referral_closed_gt_1hh_no_ind.household)
        self.assertIsNone(self.referral_closed_gt_1hh_no_ind.individual)

        # Test referral_active_gt_no_hh_no_ind
        self.assertEqual(
            self.referral_active_gt_no_hh_no_ind.ticket.programs.first().name,
            "Void Program",
        )
        self.check_grievance_household_unicef_id(self.referral_active_gt_no_hh_no_ind.ticket, None)

        # Test referral_active_gt_1hh_2notes_2docs
        ticket_referral1 = TicketReferralDetails.objects.filter(
            household=self.household_referral_active_gt_1hh_2notes_2docs,
            individual=None,
        ).first()
        self.assertEqual(
            ticket_referral1.ticket.programs.first(),
            self.program1,
        )
        self.check_grievance_household_unicef_id(
            ticket_referral1.ticket,
            self.household_referral_active_gt_1hh_2notes_2docs.unicef_id,
        )
        self.assertEqual(
            ticket_referral1.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_referral1.ticket.support_documents.count(),
            2,
        )

        hh_repr_pr2 = self.household_referral_active_gt_1hh_2notes_2docs.copied_to.get(program=self.program2)
        ticket_referral2 = TicketReferralDetails.objects.filter(
            household=hh_repr_pr2,
            individual=None,
        ).first()
        self.assertEqual(
            ticket_referral2.ticket.programs.first(),
            self.program2,
        )
        self.check_grievance_household_unicef_id(
            ticket_referral2.ticket,
            hh_repr_pr2.unicef_id,
        )
        self.assertEqual(
            ticket_referral2.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_referral2.ticket.support_documents.count(),
            2,
        )
        self.check_tickets_unicef_id_uniqueness([ticket_referral1, ticket_referral2])
        self.check_created_at_equality(
            [ticket_referral1, ticket_referral2, self.referral_active_gt_1hh_2notes_2docs],
        )

        # Test referral_active_gt_no_hh_1ind_2repr
        self.assertEqual(
            self.referral_active_gt_no_hh_1ind_2repr.ticket.programs.first(),
            self.program3,
        )
        self.check_grievance_household_unicef_id(
            self.referral_active_gt_no_hh_1ind_2repr.ticket,
            None,
        )

        # Test referral_active_gt_1hh_1ind
        ticket_referral1 = TicketReferralDetails.objects.filter(
            household=self.household_referral_active_gt_1hh_1ind,
            individual=None,
        ).first()
        self.assertEqual(
            ticket_referral1.ticket.programs.first(),
            self.program1,
        )
        self.check_grievance_household_unicef_id(
            ticket_referral1.ticket,
            self.household_referral_active_gt_1hh_1ind.unicef_id,
        )
        ticket_referral2 = TicketReferralDetails.objects.filter(
            household=self.household_referral_active_gt_1hh_1ind.copied_to.get(program=self.program2),
            individual=self.individual_referral_active_gt_1hh_1ind,
        ).first()
        self.assertEqual(
            ticket_referral2.ticket.programs.first(),
            self.program2,
        )
        self.check_grievance_household_unicef_id(
            ticket_referral2.ticket,
            self.household_referral_active_gt_1hh_1ind.copied_to.get(program=self.program2).unicef_id,
        )
        ticket_referral3 = TicketReferralDetails.objects.filter(
            household=self.household_referral_active_gt_1hh_1ind.copied_to.get(program=self.program3),
            individual=self.individual_referral_active_gt_1hh_1ind.copied_to.get(program=self.program3),
        ).first()
        self.assertEqual(
            ticket_referral3.ticket.programs.first(),
            self.program3,
        )
        self.check_grievance_household_unicef_id(
            ticket_referral3.ticket,
            self.household_referral_active_gt_1hh_1ind.copied_to.get(program=self.program3).unicef_id,
        )

        self.check_tickets_unicef_id_uniqueness([ticket_referral1, ticket_referral2, ticket_referral3])
        self.check_created_at_equality(
            [ticket_referral1, ticket_referral2, ticket_referral3, self.referral_active_gt_1hh_1ind],
        )

        # Test referral_active_gt_1hh_1ind_2notes_2docs
        ticket_referral1 = TicketReferralDetails.objects.filter(
            household=None,
            individual=self.individual_referral_active_gt_1hh_1ind_2notes_2docs,
        ).first()
        self.assertEqual(
            ticket_referral1.ticket.programs.first(),
            self.program1,
        )
        self.check_grievance_household_unicef_id(
            ticket_referral1.ticket,
            None,
        )
        self.assertEqual(
            ticket_referral1.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_referral1.ticket.support_documents.count(),
            2,
        )

        ticket_referral2 = TicketReferralDetails.objects.filter(
            household=self.household_referral_active_gt_1hh_1ind_2notes_2docs.copied_to.get(program=self.program2),
            individual=self.individual_referral_active_gt_1hh_1ind_2notes_2docs.copied_to.get(program=self.program2),
        ).first()
        self.assertEqual(
            ticket_referral2.ticket.programs.first(),
            self.program2,
        )
        self.check_grievance_household_unicef_id(
            ticket_referral2.ticket,
            self.household_referral_active_gt_1hh_1ind_2notes_2docs.copied_to.get(program=self.program2).unicef_id,
        )
        self.assertEqual(
            ticket_referral2.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_referral2.ticket.support_documents.count(),
            2,
        )

        ticket_referral3 = TicketReferralDetails.objects.filter(
            household=self.household_referral_active_gt_1hh_1ind_2notes_2docs,
            individual=self.individual_referral_active_gt_1hh_1ind_2notes_2docs.copied_to.get(program=self.program3),
        ).first()
        self.assertEqual(
            ticket_referral3.ticket.programs.first(),
            self.program3,
        )
        self.check_grievance_household_unicef_id(
            ticket_referral3.ticket,
            self.household_referral_active_gt_1hh_1ind_2notes_2docs.unicef_id,
        )
        self.assertEqual(
            ticket_referral3.ticket.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            ticket_referral3.ticket.support_documents.count(),
            2,
        )

        self.check_tickets_unicef_id_uniqueness([ticket_referral1, ticket_referral2, ticket_referral3])
        self.check_created_at_equality(
            [ticket_referral1, ticket_referral2, ticket_referral3, self.referral_active_gt_1hh_1ind_2notes_2docs],
        )

        # Test referral_active_gt_no_hh_1ind
        self.assertEqual(
            self.referral_active_gt_no_hh_1ind.ticket.programs.first(),
            self.program1,
        )
        self.check_grievance_household_unicef_id(
            self.referral_active_gt_no_hh_1ind.ticket,
            None,
        )

    def assert_needs_adjudication_ticket(
        self,
        possible_duplicates: list,
        program: Program,
        selected_individuals: list,
        notes_count: int = 0,
        documents_count: int = 0,
    ) -> TicketNeedsAdjudicationDetails:
        ticket_pr = TicketNeedsAdjudicationDetails.objects.filter(golden_records_individual__in=possible_duplicates)
        self.assertEqual(
            ticket_pr.count(),
            1,
        )
        ticket_pr = ticket_pr.first()

        self.assertEqual(
            ticket_pr.golden_records_individual.program,
            program,
        )
        self.assertEqual(
            ticket_pr.ticket.programs.first(),
            program,
        )

        possible_duplicates = [pd for pd in possible_duplicates if pd != ticket_pr.golden_records_individual]
        for poss_dup in possible_duplicates:
            self.assertIn(poss_dup.pk, ticket_pr.possible_duplicates.values_list("pk", flat=True))
        self.assertEqual(
            ticket_pr.possible_duplicates.count(),
            len(possible_duplicates),
        )

        for selected_individual in selected_individuals:
            self.assertIn(
                selected_individual,
                ticket_pr.selected_individuals.all(),
            )
        if not selected_individuals:
            self.assertEqual(
                ticket_pr.selected_individuals.count(),
                0,
            )
        self.assertEqual(
            ticket_pr.ticket.ticket_notes.count(),
            notes_count,
        )
        self.assertEqual(
            ticket_pr.ticket.support_documents.count(),
            documents_count,
        )
        return ticket_pr

    def _test_needs_adjudication_tickets(self) -> None:
        # Test needs_adjudication_not_closed
        ticket_pr1 = self.assert_needs_adjudication_ticket(
            [
                self.golden_rec_needs_adjudication_not_closed,
                self.possible_dup1_needs_adjudication_not_closed.copied_to.get(program=self.program1),
                self.possible_dup2_needs_adjudication_not_closed.copied_to.get(program=self.program1),
            ],
            self.program1,
            [
                self.possible_dup2_needs_adjudication_not_closed,
            ],
        )
        self.assertEqual(
            ticket_pr1.extra_data,
            self.create_extra_data_for_needs_adjudication(
                [self.golden_rec_needs_adjudication_not_closed.id],
                [self.possible_dup1_needs_adjudication_not_closed.copied_to.get(program=self.program1).id],
            ),
        )

        ticket_pr2 = self.assert_needs_adjudication_ticket(
            [
                self.possible_dup1_needs_adjudication_not_closed,
                self.possible_dup3_needs_adjudication_not_closed,
                self.possible_dup4_needs_adjudication_not_closed.copied_to.get(program=self.program2),
            ],
            self.program2,
            [
                self.possible_dup3_needs_adjudication_not_closed,
            ],
        )
        self.assertEqual(
            ticket_pr2.extra_data,
            self.create_extra_data_for_needs_adjudication(
                [],
                [
                    self.possible_dup1_needs_adjudication_not_closed.copied_to.get(program=self.program2).id,
                    self.possible_dup4_needs_adjudication_not_closed.copied_to.get(program=self.program2).id,
                ],
            ),
        )
        ticket_pr3 = self.assert_needs_adjudication_ticket(
            [
                self.possible_dup1_needs_adjudication_not_closed.copied_to.get(program=self.program3),
                self.possible_dup4_needs_adjudication_not_closed.copied_to.get(program=self.program3),
                self.golden_rec_needs_adjudication_not_closed.copied_to.get(program=self.program3),
            ],
            self.program3,
            [],
        )
        self.assertEqual(
            ticket_pr3.extra_data,
            self.create_extra_data_for_needs_adjudication(
                [self.golden_rec_needs_adjudication_not_closed.copied_to.get(program=self.program3).id],
                [
                    self.possible_dup1_needs_adjudication_not_closed.copied_to.get(program=self.program3).id,
                    self.possible_dup4_needs_adjudication_not_closed.id,
                ],
            ),
        )
        self.check_tickets_unicef_id_uniqueness([ticket_pr1, ticket_pr2, ticket_pr3])
        self.check_created_at_equality(
            [ticket_pr1, ticket_pr2, ticket_pr3],
        )

        # Test needs_adjudication_closed
        ticket_pr1 = self.assert_needs_adjudication_ticket(
            [
                self.possible_dup1_needs_adjudication_closed,
                self.possible_dup3_needs_adjudication_closed.copied_to.get(program=self.program1),
            ],
            self.program1,
            [
                self.possible_dup1_needs_adjudication_closed,
                self.possible_dup3_needs_adjudication_closed.copied_to.get(program=self.program1),
            ],
        )

        ticket_pr2 = self.assert_needs_adjudication_ticket(
            [
                self.possible_dup1_needs_adjudication_closed.copied_to.get(program=self.program3),
                self.possible_dup2_needs_adjudication_closed,
                self.possible_dup3_needs_adjudication_closed.copied_to.get(program=self.program3),
                self.possible_dup4_needs_adjudication_closed,
            ],
            self.program3,
            [
                self.possible_dup1_needs_adjudication_closed.copied_to.get(program=self.program3),
                self.possible_dup3_needs_adjudication_closed.copied_to.get(program=self.program3),
                self.possible_dup4_needs_adjudication_closed,
            ],
        )

        ticket_pr3 = self.assert_needs_adjudication_ticket(
            [
                self.golden_rec_needs_adjudication_closed,
                self.possible_dup4_needs_adjudication_closed.copied_to.get(program=self.program4),
            ],
            self.program4,
            [
                self.possible_dup4_needs_adjudication_closed.copied_to.get(program=self.program4),
            ],
        )

        self.check_tickets_unicef_id_uniqueness([ticket_pr1, ticket_pr2, ticket_pr3])
        self.check_created_at_equality(
            [ticket_pr1, ticket_pr2, ticket_pr3],
        )

        # Test needs_adjudication_closed_2docs_2notes
        ticket_pr1 = self.assert_needs_adjudication_ticket(
            [
                self.possible_dup1_needs_adjudication_closed_2docs_2notes,
                self.possible_dup2_needs_adjudication_closed_2docs_2notes.copied_to.get(program=self.program2),
                self.possible_dup3_needs_adjudication_closed_2docs_2notes.copied_to.get(program=self.program2),
            ],
            self.program2,
            [
                self.possible_dup3_needs_adjudication_closed_2docs_2notes.copied_to.get(program=self.program2),
            ],
            2,
            2,
        )

        ticket_pr2 = self.assert_needs_adjudication_ticket(
            [
                self.possible_dup2_needs_adjudication_closed_2docs_2notes,
                self.possible_dup3_needs_adjudication_closed_2docs_2notes.copied_to.get(program=self.program3),
            ],
            self.program3,
            [
                self.possible_dup3_needs_adjudication_closed_2docs_2notes.copied_to.get(program=self.program3),
            ],
            2,
            2,
        )

        self.check_tickets_unicef_id_uniqueness([ticket_pr1, ticket_pr2])
        self.check_created_at_equality(
            [ticket_pr1, ticket_pr2],
        )

        # Test needs_adjudication_no_common_program
        self.assertFalse(
            TicketNeedsAdjudicationDetails.objects.filter(id=self.needs_adjudication_no_common_program.id).exists()
        )

    def _test_feedback(self) -> None:
        # Test feedback_closed_2hh_3ind
        self.assertEqual(
            self.feedback_closed_2hh_3ind.household_lookup,
            self.household_feedback_closed_2hh_3ind,
        )
        self.assertEqual(
            self.feedback_closed_2hh_3ind.individual_lookup,
            self.individual_feedback_closed_2hh_3ind.copied_to.get(program=self.program1),
        )
        self.assertEqual(
            self.feedback_closed_2hh_3ind.feedback_messages.count(),
            2,
        )
        self.assertEqual(
            self.feedback_closed_2hh_3ind.program,
            self.program1,
        )
        self.assertEqual(
            self.feedback_closed_2hh_3ind.linked_grievance.programs.first(),
            self.program1,
        )
        self.assertIsNone(
            Feedback.objects.filter(
                household_lookup=self.household_feedback_closed_2hh_3ind.copied_to.get(program=self.program2),
                individual_lookup=self.individual_feedback_closed_2hh_3ind,
            ).first()
        )

        # Test feedback_closed_no_hh_no_ind
        self.assertIsNone(self.feedback_closed_no_hh_no_ind.household_lookup)
        self.assertIsNone(self.feedback_closed_no_hh_no_ind.individual_lookup)
        self.assertEqual(
            self.feedback_closed_no_hh_no_ind.linked_grievance.programs.first().name,
            "Void Program",
        )
        self.assertEqual(
            self.feedback_closed_no_hh_no_ind.program.name,
            "Void Program",
        )

        # Test feedback_closed_1hh_1ind_same_program
        self.assertEqual(
            self.feedback_closed_1hh_1ind_same_program.program,
            self.program1,
        )
        self.assertEqual(
            self.feedback_closed_1hh_1ind_same_program.linked_grievance.programs.first(),
            self.program1,
        )
        self.assertEqual(
            self.feedback_closed_1hh_1ind_same_program.household_lookup,
            self.household_feedback_closed_1hh_1ind_same_program,
        )
        self.assertEqual(
            self.feedback_closed_1hh_1ind_same_program.individual_lookup,
            self.individual_feedback_closed_1hh_1ind_same_program,
        )

        # Test feedback_closed_1hh_1ind_diff_program_with_repr
        self.assertEqual(
            self.feedback_closed_1hh_1ind_diff_program_with_repr.program,
            self.program1,
        )
        self.assertEqual(
            self.feedback_closed_1hh_1ind_diff_program_with_repr.linked_grievance.programs.first(),
            self.program1,
        )
        self.assertEqual(
            self.feedback_closed_1hh_1ind_diff_program_with_repr.household_lookup,
            self.household_feedback_closed_1hh_1ind_diff_program_with_repr,
        )
        self.assertEqual(
            self.feedback_closed_1hh_1ind_diff_program_with_repr.individual_lookup,
            self.individual_feedback_closed_1hh_1ind_diff_program_with_repr.copied_to.get(program=self.program1),
        )
        self.assertIsNone(
            Feedback.objects.filter(
                household_lookup=None,
                individual_lookup=self.individual_feedback_closed_1hh_1ind_diff_program_with_repr,
            ).first()
        )

        # Test feedback_closed_only_hh
        self.assertEqual(
            self.feedback_closed_only_hh.household_lookup,
            self.household_feedback_closed_only_hh,
        )
        self.assertIsNone(
            self.feedback_closed_only_hh.individual_lookup,
        )
        self.assertEqual(
            self.feedback_closed_only_hh.linked_grievance.programs.first(),
            self.program1,
        )
        self.assertEqual(
            self.feedback_closed_only_hh.program,
            self.program1,
        )

        # Test feedback_closed_only_ind
        self.assertIsNone(
            self.feedback_closed_only_ind.household_lookup,
        )
        self.assertEqual(
            self.feedback_closed_only_ind.individual_lookup,
            self.individual_feedback_closed_only_ind,
        )
        self.assertEqual(
            self.feedback_closed_only_ind.linked_grievance.programs.first(),
            self.program1,
        )
        self.assertEqual(
            self.feedback_closed_only_ind.program,
            self.program1,
        )

        # Test feedback_closed_1hh_1ind_diff_program
        self.assertEqual(
            self.feedback_closed_1hh_1ind_diff_program.program,
            self.program1,
        )
        self.assertEqual(
            self.feedback_closed_1hh_1ind_diff_program.linked_grievance.programs.first(),
            self.program1,
        )
        self.assertEqual(
            self.feedback_closed_1hh_1ind_diff_program.household_lookup,
            self.household_feedback_closed_1hh_1ind_diff_program,
        )
        self.assertIsNone(
            self.feedback_closed_1hh_1ind_diff_program.individual_lookup,
        )
        self.assertIsNone(
            Feedback.objects.filter(individual_lookup=self.individual_feedback_closed_1hh_1ind_diff_program).first()
        )

        # Test feedback_closed_2hh_3ind_in_pr3
        self.assertEqual(
            self.feedback_closed_2hh_3ind_in_pr3.program,
            self.program3,
        )
        self.assertEqual(
            self.feedback_closed_2hh_3ind_in_pr3.household_lookup,
            self.household_feedback_closed_2hh_3ind_in_pr3.copied_to.get(program=self.program3),
        )
        self.assertEqual(
            self.feedback_closed_2hh_3ind_in_pr3.individual_lookup,
            self.individual_feedback_closed_2hh_3ind_in_pr3.copied_to.get(program=self.program3),
        )
        self.assertEqual(
            self.feedback_closed_2hh_3ind_in_pr3.feedback_messages.count(),
            2,
        )
        self.assertEqual(
            self.feedback_closed_2hh_3ind_in_pr3.linked_grievance.programs.first(),
            self.program3,
        )

        self.assertIsNone(
            Feedback.objects.filter(
                household_lookup=self.household_feedback_closed_2hh_3ind_in_pr3,
                individual_lookup=self.individual_feedback_closed_2hh_3ind_in_pr3.copied_to.get(program=self.program1),
            ).first()
        )

        # Test feedback_no_gt_2hh_3ind_in_pr3
        self.assertEqual(
            self.feedback_no_gt_2hh_3ind_in_pr3.household_lookup,
            self.household_feedback_no_gt_2hh_3ind_in_pr3.copied_to.get(program=self.program3),
        )
        self.assertEqual(
            self.feedback_no_gt_2hh_3ind_in_pr3.individual_lookup,
            self.individual_feedback_no_gt_2hh_3ind_in_pr3.copied_to.get(program=self.program3),
        )
        self.assertEqual(
            self.feedback_no_gt_2hh_3ind_in_pr3.program,
            self.program3,
        )

        self.assertIsNone(
            Feedback.objects.filter(
                household_lookup=self.household_feedback_no_gt_2hh_3ind_in_pr3,
                individual_lookup=self.individual_feedback_no_gt_2hh_3ind_in_pr3.copied_to.get(program=self.program1),
            ).first()
        )

        # Test feedback_active_gt_no_hh_no_ind_in_pr1
        self.assertEqual(
            self.feedback_active_gt_no_hh_no_ind_in_pr1.program,
            self.program1,
        )
        self.assertEqual(
            self.feedback_active_gt_no_hh_no_ind_in_pr1.linked_grievance.programs.first(),
            self.program1,
        )
        self.assertIsNone(
            self.feedback_active_gt_no_hh_no_ind_in_pr1.household_lookup,
        )
        self.assertIsNone(
            self.feedback_active_gt_no_hh_no_ind_in_pr1.individual_lookup,
        )

        # Test feedback_active_only_ind_in_pr2.linked_grievance
        self.assertEqual(
            self.feedback_active_only_ind_in_pr2.program,
            self.program2,
        )
        self.assertEqual(
            self.feedback_active_only_ind_in_pr2.linked_grievance.programs.first(),
            self.program2,
        )
        self.assertIsNone(
            self.feedback_active_only_ind_in_pr2.household_lookup,
        )
        self.assertEqual(
            self.feedback_active_only_ind_in_pr2.individual_lookup,
            self.individual_feedback_active_only_ind_in_pr2.copied_to.get(program=self.program2),
        )
        self.assertIsNone(
            Feedback.objects.filter(
                individual_lookup=self.individual_feedback_active_only_ind_in_pr2,
                household_lookup=None,
            ).first()
        )

        # Test feedback_no_gt_1hh_1ind_in_pr2
        self.assertEqual(
            self.feedback_no_gt_1hh_1ind_in_pr2.program,
            self.program1,
        )
        self.assertIsNone(self.feedback_no_gt_1hh_1ind_in_pr2.household_lookup)
        self.assertIsNone(self.feedback_no_gt_1hh_1ind_in_pr2.individual_lookup)
        self.assertIsNone(
            Feedback.objects.filter(
                household_lookup=self.household_feedback_no_gt_1hh_1ind_in_pr2,
                individual_lookup=self.individual_feedback_no_gt_1hh_1ind_in_pr2,
            ).first()
        )

        # Test feedback_no_program_no_gt_no_hh_no_ind
        self.assertEqual(
            self.feedback_no_program_no_gt_no_hh_no_ind.program.name,
            "Void Program",
        )

        # Test feedback_no_program_no_gt_no_hh_1ind
        feedback1 = Feedback.objects.filter(
            household_lookup=None,
            individual_lookup=self.individual_feedback_no_program_no_gt_no_hh_1ind,
        ).first()
        self.assertIsNotNone(feedback1)
        self.assertEqual(
            feedback1.program,
            self.program1,
        )
        self.assertEqual(
            feedback1.feedback_messages.count(),
            2,
        )

        feedback2 = Feedback.objects.filter(
            household_lookup=None,
            individual_lookup=self.individual_feedback_no_program_no_gt_no_hh_1ind.copied_to.get(program=self.program2),
        ).first()
        self.assertIsNotNone(feedback2)
        self.assertEqual(
            feedback2.program,
            self.program2,
        )
        self.assertEqual(
            feedback2.feedback_messages.count(),
            2,
        )
        self.assertEqual(
            feedback2.feedback_messages.order_by("created_at").first().created_at,
            feedback1.feedback_messages.order_by("created_at").first().created_at,
        )
        self.assertEqual(
            feedback2.feedback_messages.order_by("created_at").last().created_at,
            feedback1.feedback_messages.order_by("created_at").last().created_at,
        )
        self.check_created_at_equality([feedback1, feedback2], ticket_field="linked_grievance")
        self.check_feedback_unicef_id_uniqueness([feedback1, feedback2])

        # Test feedback_no_program_no_gt_2hh_3ind
        feedback1 = Feedback.objects.filter(
            household_lookup=self.household_feedback_no_program_no_gt_2hh_3ind.copied_to.get(program=self.program1),
            individual_lookup=self.individual_feedback_no_program_no_gt_2hh_3ind,
        ).first()
        self.assertIsNotNone(feedback1)
        self.assertEqual(
            feedback1.program,
            self.program1,
        )
        feedback2 = Feedback.objects.filter(
            household_lookup=self.household_feedback_no_program_no_gt_2hh_3ind,
            individual_lookup=self.individual_feedback_no_program_no_gt_2hh_3ind.copied_to.get(program=self.program2),
        ).first()
        self.assertIsNotNone(feedback2)
        self.assertEqual(
            feedback2.program,
            self.program2,
        )
        feedback3 = Feedback.objects.filter(
            household_lookup=None,
            individual_lookup=self.individual_feedback_no_program_no_gt_2hh_3ind.copied_to.get(program=self.program3),
        ).first()
        self.assertIsNotNone(feedback3)
        self.assertEqual(
            feedback3.program,
            self.program3,
        )
        self.check_created_at_equality([feedback1, feedback2, feedback3], ticket_field="linked_grievance")
        self.check_feedback_unicef_id_uniqueness([feedback1, feedback2, feedback3])

        # Test feedback_no_program_no_gt_1hh_1ind
        feedback1 = Feedback.objects.filter(
            household_lookup=self.household_feedback_no_program_no_gt_1hh_1ind,
            individual_lookup=None,
        ).first()
        self.assertIsNotNone(feedback1)
        self.assertEqual(
            feedback1.program,
            self.program1,
        )
        feedback2 = Feedback.objects.filter(
            household_lookup=None,
            individual_lookup=self.individual_feedback_no_program_no_gt_1hh_1ind,
        ).first()
        self.assertIsNotNone(feedback2)
        self.assertEqual(
            feedback2.program,
            self.program2,
        )
        self.check_created_at_equality([feedback1, feedback2], ticket_field="linked_grievance")
        self.check_feedback_unicef_id_uniqueness([feedback1, feedback2])

        # Test feedback_active_gt_no_program_2hh_no_ind
        feedback1 = Feedback.objects.filter(
            household_lookup=self.household_feedback_active_gt_no_program_2hh_no_ind,
            individual_lookup=None,
        ).first()
        self.assertIsNotNone(feedback1)
        self.assertEqual(
            feedback1.program,
            self.program1,
        )
        self.assertEqual(
            feedback1.linked_grievance.programs.first(),
            self.program1,
        )

        feedback2 = Feedback.objects.filter(
            household_lookup=self.household_feedback_active_gt_no_program_2hh_no_ind.copied_to.get(
                program=self.program2
            ),
            individual_lookup=None,
        ).first()
        self.assertIsNotNone(feedback2)
        self.assertEqual(
            feedback2.program,
            self.program2,
        )
        self.assertEqual(
            feedback2.linked_grievance.programs.first(),
            self.program2,
        )
        self.check_created_at_equality([feedback1, feedback2], ticket_field="linked_grievance")
        self.check_tickets_unicef_id_uniqueness([feedback1, feedback2], ticket_field="linked_grievance")
        self.check_feedback_unicef_id_uniqueness([feedback1, feedback2])

        # Test feedback_active_gt_no_program_3hh_2ind
        feedback1 = Feedback.objects.filter(
            household_lookup=self.household_feedback_active_gt_no_program_3hh_2ind,
            individual_lookup=None,
        ).first()
        self.assertIsNotNone(feedback1)
        self.assertEqual(
            feedback1.program,
            self.program1,
        )
        self.assertEqual(
            feedback1.linked_grievance.programs.first(),
            self.program1,
        )
        self.assertEqual(
            feedback1.feedback_messages.count(),
            2,
        )
        self.assertEqual(
            feedback1.linked_grievance.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            feedback1.linked_grievance.support_documents.count(),
            2,
        )
        self.assertIn(
            feedback1.linked_grievance,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )

        feedback2 = Feedback.objects.filter(
            household_lookup=self.household_feedback_active_gt_no_program_3hh_2ind.copied_to.get(program=self.program2),
            individual_lookup=self.individual_feedback_active_gt_no_program_3hh_2ind.copied_to.get(
                program=self.program2
            ),
        ).first()
        self.assertIsNotNone(feedback1)
        self.assertEqual(
            feedback2.program,
            self.program2,
        )
        self.assertEqual(
            feedback2.linked_grievance.programs.first(),
            self.program2,
        )
        self.assertEqual(
            feedback2.feedback_messages.count(),
            2,
        )
        self.assertEqual(
            feedback2.linked_grievance.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            feedback2.linked_grievance.support_documents.count(),
            2,
        )
        self.assertIn(
            feedback2.linked_grievance,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )

        feedback3 = Feedback.objects.filter(
            household_lookup=self.household_feedback_active_gt_no_program_3hh_2ind.copied_to.get(program=self.program3),
            individual_lookup=self.individual_feedback_active_gt_no_program_3hh_2ind.copied_to.get(
                program=self.program3
            ),
        ).first()
        self.assertIsNotNone(feedback1)
        self.assertEqual(
            feedback3.program,
            self.program3,
        )
        self.assertEqual(
            feedback3.linked_grievance.programs.first(),
            self.program3,
        )
        self.assertEqual(
            feedback3.feedback_messages.count(),
            2,
        )
        self.assertEqual(
            feedback3.linked_grievance.ticket_notes.count(),
            2,
        )
        self.assertEqual(
            feedback3.linked_grievance.support_documents.count(),
            2,
        )
        self.assertIn(
            feedback3.linked_grievance,
            self.sensitive_ticket_no_payment_not_closed_gt.ticket.linked_tickets.all(),
        )

        self.check_created_at_equality([feedback1, feedback2, feedback3], ticket_field="linked_grievance")
        self.check_tickets_unicef_id_uniqueness([feedback1, feedback2, feedback3], ticket_field="linked_grievance")
        self.check_feedback_unicef_id_uniqueness([feedback1, feedback2, feedback3])

        assert (
            feedback1.feedback_messages.order_by("created_at").first().created_at
            == feedback2.feedback_messages.order_by("created_at").first().created_at
            == feedback3.feedback_messages.order_by("created_at").first().created_at
        )
        assert (
            feedback1.feedback_messages.order_by("created_at").last().created_at
            == feedback2.feedback_messages.order_by("created_at").last().created_at
            == feedback3.feedback_messages.order_by("created_at").last().created_at
        )

    # def test(self) -> None:
    #     needs_adjudication_count = TicketNeedsAdjudicationDetails.objects.count()
    #     migrate_grievance_to_representations()
    #
    #     self.refresh_objects()
    #     self.assertEqual(needs_adjudication_count + 4, TicketNeedsAdjudicationDetails.objects.count())
    #
    #     self._test_ticket_complaint_details()
    #     self._test_ticket_sensitive_details()
    #     self._test_ticket_payment_verification_details()
    #     self._test_ticket_delete_household_details()
    #     self._test_ticket_update_household_details()
    #     self._test_ticket_add_individual_details()
    #     self._test_ticket_upd_individual_details()
    #     self._test_ticket_delete_individual_details()
    #     self._test_ticket_system_flagging_details()
    #
    #     self._test_ticket_referral_details()
    #     self._test_needs_adjudication_tickets()
    #     self._test_feedback()
    #
    #     self._test_message()
