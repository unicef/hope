"""Factories for grievance models."""

import factory
from factory.django import DjangoModelFactory

from hope.apps.grievance.models import (
    GrievanceDocument,
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNote,
    TicketPaymentVerificationDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hope.models import PaymentVerification

from .core import BusinessAreaFactory
from .household import HouseholdFactory, IndividualFactory
from .sanction_list import SanctionListIndividualFactory


class GrievanceTicketFactory(DjangoModelFactory):
    class Meta:
        model = GrievanceTicket

    business_area = factory.SubFactory(BusinessAreaFactory)
    category = GrievanceTicket.CATEGORY_DATA_CHANGE
    issue_type = GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL
    status = GrievanceTicket.STATUS_NEW
    description = factory.Sequence(lambda n: f"Test grievance ticket {n}")


class TicketSensitiveDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketSensitiveDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
    )


class TicketComplaintDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketComplaintDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
    )


class TicketReferralDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketReferralDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
    )


class GrievanceComplaintTicketWithoutExtrasFactory(DjangoModelFactory):
    class Meta:
        model = TicketComplaintDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
    )


class TicketDeleteIndividualDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketDeleteIndividualDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
    )
    individual = factory.SubFactory(IndividualFactory)


class TicketDeleteHouseholdDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketDeleteHouseholdDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
    )


class TicketSystemFlaggingDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketSystemFlaggingDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
    )
    golden_records_individual = factory.SubFactory(IndividualFactory)
    sanction_list_individual = factory.SubFactory(SanctionListIndividualFactory)


class TicketNeedsAdjudicationDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketNeedsAdjudicationDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
    )
    golden_records_individual = factory.SubFactory(IndividualFactory)


class TicketPaymentVerificationDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketPaymentVerificationDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION, issue_type=None
    )
    payment_verification_status = PaymentVerification.STATUS_RECEIVED_WITH_ISSUES


class TicketIndividualDataUpdateDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketIndividualDataUpdateDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )
    individual = factory.SubFactory(IndividualFactory)


class TicketAddIndividualDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketAddIndividualDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )
    household = factory.SubFactory(HouseholdFactory)
    approve_status = True
    individual_data = {}


class TicketHouseholdDataUpdateDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketHouseholdDataUpdateDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
    )
    household = factory.SubFactory(HouseholdFactory)
    household_data = {}


class GrievanceDocumentFactory(DjangoModelFactory):
    class Meta:
        model = GrievanceDocument

    name = factory.Sequence(lambda n: f"Document {n}")
    grievance_ticket = factory.SubFactory(GrievanceTicketFactory)
    content_type = "image/jpeg"
    file_size = 1024


class TicketNoteFactory(DjangoModelFactory):
    class Meta:
        model = TicketNote

    ticket = factory.SubFactory(GrievanceTicketFactory)
    description = factory.Sequence(lambda n: f"Note {n}")
