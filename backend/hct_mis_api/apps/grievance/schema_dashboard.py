import logging

import graphene
from django.db.models import Case, CharField, Count, When, Value
from django.utils.encoding import force_str

from hct_mis_api.apps.grievance.models import GrievanceTicket

logger = logging.getLogger(__name__)


def display_value(choices, field):
    options = [When(**{field: k, "then": Value(v)}) for k, v in choices]
    return Case(*options, output_field=CharField())


class BusinessAreaInput(graphene.InputObjectType):
    business_area = graphene.String()


class TicketByCategory(graphene.ObjectType):
    category_name = graphene.String()
    count = graphene.Int()


class TicketByStatus(graphene.ObjectType):
    status_name = graphene.String()
    count = graphene.Int()


class TicketByLocationAndCategory(graphene.ObjectType):
    location = graphene.String()
    count = graphene.Int()
    categories = graphene.List(TicketByCategory)

    def resolve_count(self, info):
        return sum([category["count"] for category in self.get("categories")])


class Query(graphene.ObjectType):
    tickets_by_category = graphene.List(TicketByCategory, business_area=graphene.String(required=True))
    tickets_by_status = graphene.List(TicketByStatus, business_area=graphene.String(required=True))
    tickets_by_location_and_category = graphene.List(
        TicketByLocationAndCategory, business_area=graphene.String(required=True)
    )

    def resolve_tickets_by_category(self, info, **kwargs):
        logger.info(kwargs)
        return (
            GrievanceTicket.objects.filter(business_area=kwargs["business_area"])
            .annotate(
                category_name=Case(
                    *[When(category=i, then=Value(force_str(j))) for (i, j) in GrievanceTicket.CATEGORY_CHOICES],
                    default=Value("XXX"),
                    output_field=CharField()
                )
            )
            .values("category_name")
            .annotate(count=Count("category"))
            .order_by("-count")
        )

    def resolve_tickets_by_status(self, info, **kwargs):
        return (
            GrievanceTicket.objects.filter(business_area=kwargs["business_area"])
            .annotate(
                status_name=Case(
                    *[When(status=i, then=Value(force_str(j))) for (i, j) in GrievanceTicket.STATUS_CHOICES],
                    default=Value("XXX"),
                    output_field=CharField()
                )
            )
            .values("status_name")
            .annotate(count=Count("status"))
            .order_by("-count")
        )

    def resolve_tickets_by_location_and_category(self, info, **kwargs):
        qs = (
            GrievanceTicket.objects.select_related("admin2")
            .filter(business_area=kwargs["business_area"])
            .values_list("admin2__title", "category")
            .annotate(
                category_name=Case(
                    *[When(category=i, then=Value(force_str(j))) for (i, j) in GrievanceTicket.CATEGORY_CHOICES],
                    default=Value("XXX"),
                    output_field=CharField()
                )
            )
            .annotate(count=Count("category"))
            .order_by("admin2__title", "-count")
        )

        results = []
        for item in qs:
            location, _, category_name, count = item
            category_item = {"category_name": category_name, "count": count}
            if results and results[-1]["location"] == location:
                results[-1]["categories"].append(category_item)
            else:
                results.append({"location": location, "categories": [category_item]})
        return results
