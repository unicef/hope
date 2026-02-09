"""Factories for grievance models."""

import factory
from factory.django import DjangoModelFactory

from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketPaymentVerificationDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hope.models import PaymentVerification

from .core import BusinessAreaFactory
from .household import IndividualFactory


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
    )


class TicketNeedsAdjudicationDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketNeedsAdjudicationDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
    )


class TicketPaymentVerificationDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketPaymentVerificationDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION)
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
