"""Factories for grievance models."""

import factory
from factory.django import DjangoModelFactory

from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketPaymentVerificationDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hope.models import PaymentVerification

from .core import BusinessAreaFactory
from .household import IndividualFactory
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


class TicketAddIndividualDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketAddIndividualDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )
    household = factory.SubFactory("extras.test_utils.factories.household.HouseholdFactory")
    individual_data = factory.LazyFunction(dict)
    approve_status = True


class TicketDeleteHouseholdDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketDeleteHouseholdDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
    )


class TicketHouseholdDataUpdateDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketHouseholdDataUpdateDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
    )
    household = factory.SubFactory("extras.test_utils.factories.household.HouseholdFactory")
    household_data = factory.LazyFunction(dict)


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
