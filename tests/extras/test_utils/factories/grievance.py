"""Factories for grievance models."""

import factory
from factory.django import DjangoModelFactory

from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketIndividualDataUpdateDetails,
    TicketSensitiveDetails,
)

from .core import BusinessAreaFactory


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
    household = None
    individual = None
    payment = None


class TicketComplaintDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketComplaintDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
    )
    household = None
    individual = None


class TicketIndividualDataUpdateDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketIndividualDataUpdateDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )
    individual = None
