"""Factories for grievance models."""

import factory
from factory.django import DjangoModelFactory

from hope.apps.grievance.models import GrievanceTicket


class GrievanceTicketFactory(DjangoModelFactory):
    class Meta:
        model = GrievanceTicket

    # business_area must be passed explicitly (no SubFactory)
    category = GrievanceTicket.CATEGORY_DATA_CHANGE
    issue_type = GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL
    status = GrievanceTicket.STATUS_NEW
    description = factory.Sequence(lambda n: f"Test grievance ticket {n}")
