import itertools
from typing import Any, Dict, Tuple

from django.db.models import Avg, Case, CharField, Count, F, Q, QuerySet, Value, When
from django.db.models.functions import Extract
from django.utils.encoding import force_str

import graphene

from hct_mis_api.apps.core.utils import decode_id_string_required
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.schema import ChartDatasetNode, ChartDetailedDatasetsNode

TICKET_ORDERING_KEYS = [
    "Data Change",
    "Grievance Complaint",
    "Needs Adjudication",
    "Negative Feedback",
    "Payment Verification",
    "Positive Feedback",
    "Referral",
    "Sensitive Grievance",
    "System Flagging",
]

TICKET_ORDERING = {
    "Data Change": 0,
    "Grievance Complaint": 1,
    "Needs Adjudication": 2,
    "Negative Feedback": 3,
    "Payment Verification": 4,
    "Positive Feedback": 5,
    "Referral": 6,
    "Sensitive Grievance": 7,
    "System Flagging": 8,
}


def transform_to_chart_dataset(qs: QuerySet) -> Dict[str, Any]:
    labels, data = [], []
    for q in qs:
        label, value = q
        labels.append(label)
        data.append(value)

    return {"labels": labels, "datasets": [{"data": data}]}


def display_value(choices: Tuple, field: str, default_field: Any = None) -> Case:
    options = [When(**{field: k, "then": Value(force_str(v))}) for k, v in choices]
    return Case(*options, default=default_field, output_field=CharField())


def create_type_generated_queries() -> Tuple[Q, Q]:
    user_generated, system_generated = Q(), Q()
    for category in GrievanceTicket.CATEGORY_CHOICES:
        category_num, category_str = category
        if category_num in dict(GrievanceTicket.MANUAL_CATEGORIES):
            user_generated |= Q(category_name=force_str(category_str))
        else:
            system_generated |= Q(category_name=force_str(category_str))
    return user_generated, system_generated


def pre_filter_query_with_headers(info: Any) -> QuerySet:
    business_area_slug = info.context.headers.get("Business-Area")
    encoded_program_id = info.context.headers.get("Program")

    query = GrievanceTicket.objects.filter(ignored=False)

    if business_area_slug:
        query = query.filter(business_area__slug=business_area_slug)

    if encoded_program_id and encoded_program_id != "all":
        decoded_id = decode_id_string_required(encoded_program_id)
        program = Program.objects.get(id=decoded_id)
        query = query.filter(programs__in=[program])

    return query


class BusinessAreaInput(graphene.InputObjectType):
    business_area = graphene.String()


class TicketByType(graphene.ObjectType):
    user_generated_count = graphene.Int()
    system_generated_count = graphene.Int()
    closed_user_generated_count = graphene.Int()
    closed_system_generated_count = graphene.Int()
    user_generated_avg_resolution = graphene.Float()
    system_generated_avg_resolution = graphene.Float()


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

    def resolve_count(self, info: Any) -> int:
        return sum([category["count"] for category in self.get("categories")])


class Query(graphene.ObjectType):
    tickets_by_type = graphene.Field(TicketByType, business_area_slug=graphene.String(required=True))
    tickets_by_category = graphene.Field(ChartDatasetNode, business_area_slug=graphene.String(required=True))
    tickets_by_status = graphene.Field(ChartDatasetNode, business_area_slug=graphene.String(required=True))
    tickets_by_location_and_category = graphene.Field(
        ChartDetailedDatasetsNode, business_area_slug=graphene.String(required=True)
    )

    def resolve_tickets_by_type(self, info: Any, **kwargs: Any) -> Dict:
        user_generated, system_generated = create_type_generated_queries()

        qs = (
            pre_filter_query_with_headers(info)
            .annotate(
                category_name=display_value(GrievanceTicket.CATEGORY_CHOICES, "category"),
                days_diff=Extract(F("updated_at") - F("created_at"), "days"),
            )
            .values_list("category_name", "days_diff")
            .aggregate(
                user_generated_count=Count("category_name", filter=user_generated),
                system_generated_count=Count("category_name", filter=system_generated),
                closed_user_generated_count=Count("category_name", filter=user_generated & Q(status=6)),
                closed_system_generated_count=Count("category_name", filter=system_generated & Q(status=6)),
                user_generated_avg_resolution=Avg("days_diff", filter=user_generated & Q(status=6)),
                system_generated_avg_resolution=Avg("days_diff", filter=system_generated & Q(status=6)),
            )
        )

        qs = {k: (0.00 if v is None else v) for k, v in qs.items()}
        qs["user_generated_avg_resolution"] = round(qs["user_generated_avg_resolution"], 2)
        qs["system_generated_avg_resolution"] = round(qs["system_generated_avg_resolution"], 2)
        return qs

    def resolve_tickets_by_category(self, info: Any, **kwargs: Any) -> Dict:
        qs = (
            pre_filter_query_with_headers(info)
            .annotate(category_name=display_value(GrievanceTicket.CATEGORY_CHOICES, "category"))
            .values("category_name")
            .annotate(count=Count("category"))
            .values_list("category_name", "count")
            .order_by("-count")
        )

        return transform_to_chart_dataset(qs)

    def resolve_tickets_by_status(self, info: Any, **kwargs: Any) -> Dict:
        qs = (
            pre_filter_query_with_headers(info)
            .annotate(status_name=display_value(GrievanceTicket.STATUS_CHOICES, "status"))
            .values("status_name")
            .annotate(count=Count("status"))
            .values_list("status_name", "count")
            .order_by("-count", "status_name")
        )

        return transform_to_chart_dataset(qs)

    def resolve_tickets_by_location_and_category(self, info: Any, **kwargs: Any) -> Dict:
        qs = (
            pre_filter_query_with_headers(info)
            .select_related("admin2")
            .values_list("admin2__name", "category")
            .annotate(
                category_name=display_value(GrievanceTicket.CATEGORY_CHOICES, "category"), count=Count("category")
            )
            .order_by("admin2__name", "-count")
        )

        results, labels, totals = [], [], []
        for key, group in itertools.groupby(qs, lambda x: x[0]):
            if key is None:
                continue

            labels.append(key)
            ticket_horizontal_counts = [0 for _ in range(9)]

            for item in group:
                _, _, ticket_name, ticket_count = item
                idx = TICKET_ORDERING[ticket_name]
                ticket_horizontal_counts[idx] = ticket_count
            results.append(ticket_horizontal_counts)
        ticket_vertical_counts = list(zip(*results))

        for key, value in enumerate(ticket_vertical_counts):
            totals.append({"label": TICKET_ORDERING_KEYS[key], "data": list(value)})

        return {"labels": labels, "datasets": totals}
