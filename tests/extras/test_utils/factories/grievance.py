"""Factories for grievance models."""

import factory
from factory.django import DjangoModelFactory

from hope.apps.grievance.models import GrievanceTicket, TicketSensitiveDetails

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
