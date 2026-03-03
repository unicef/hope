from typing import TYPE_CHECKING

from django.db.models import Q
from django.db.models.functions import Lower
from django_filters import BooleanFilter, CharFilter, FilterSet, MultipleChoiceFilter

from hope.apps.core.utils import CustomOrderingFilter
from hope.models import USER_STATUS_CHOICES, Partner, User

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class UsersFilter(FilterSet):
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=USER_STATUS_CHOICES)
    partner = MultipleChoiceFilter(choices=Partner.get_partners_as_choices, method="partners_filter")
    is_ticket_creator = BooleanFilter(method="is_ticket_creator_filter")
    is_survey_creator = BooleanFilter(method="is_survey_creator_filter")
    is_message_creator = BooleanFilter(method="is_message_creator_filter")
    is_feedback_creator = BooleanFilter(method="is_feedback_creator_filter")

    class Meta:
        model = User
        fields = {"status": ["exact"], "partner": ["exact"]}

    order_by = CustomOrderingFilter(
        fields=(
            Lower("first_name"),
            Lower("last_name"),
            "last_login",
            "status",
            "partner",
            "email",
        )
    )

    def is_ticket_creator_filter(self, qs: "QuerySet[User]", name: str, value: bool) -> "QuerySet[User]":
        return qs.exclude(created_tickets__isnull=value)

    def is_survey_creator_filter(self, qs: "QuerySet[User]", name: str, value: bool) -> "QuerySet[User]":
        return qs.exclude(surveys__isnull=value)

    def is_message_creator_filter(self, qs: "QuerySet[User]", name: str, value: bool) -> "QuerySet[User]":
        return qs.exclude(messages__isnull=value)

    def is_feedback_creator_filter(self, qs: "QuerySet[User]", name: str, value: bool) -> "QuerySet[User]":
        return qs.exclude(feedbacks__isnull=value)

    def search_filter(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[User]":
        values = value.split(" ")
        q_obj = Q()
        for v in values:
            q_obj |= Q(first_name__startswith=v)
            q_obj |= Q(last_name__startswith=v)
            q_obj |= Q(email__startswith=v)
        return qs.filter(q_obj)

    def business_area_filter(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[User]":
        return qs.filter(
            Q(role_assignments__business_area__slug=value) | Q(partner__role_assignments__business_area__slug=value)
        )

    def partners_filter(self, qs: "QuerySet", name: str, values: list[int]) -> "QuerySet[User]":
        return qs.filter(partner_id__in=values)
