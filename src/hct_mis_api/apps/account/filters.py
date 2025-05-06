from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.functions import Lower

from django_filters import BooleanFilter, CharFilter, FilterSet, MultipleChoiceFilter

from hct_mis_api.apps.account.models import USER_STATUS_CHOICES, Partner, Role
from hct_mis_api.apps.core.utils import CustomOrderingFilter, decode_id_string

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models.query import QuerySet

    from hct_mis_api.apps.account.models import User


class UsersFilter(FilterSet):
    business_area = CharFilter(required=True, method="business_area_filter")
    program = CharFilter(required=False, method="program_filter")
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=USER_STATUS_CHOICES)
    partner = MultipleChoiceFilter(choices=Partner.get_partners_as_choices(), method="partners_filter")
    roles = MultipleChoiceFilter(choices=Role.get_roles_as_choices(), method="roles_filter")
    is_ticket_creator = BooleanFilter(method="is_ticket_creator_filter")
    is_survey_creator = BooleanFilter(method="is_survey_creator_filter")
    is_message_creator = BooleanFilter(method="is_message_creator_filter")
    is_feedback_creator = BooleanFilter(method="is_feedback_creator_filter")

    class Meta:
        model = get_user_model()
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
        for value in values:
            q_obj |= Q(first_name__startswith=value)
            q_obj |= Q(last_name__startswith=value)
            q_obj |= Q(email__startswith=value)
        return qs.filter(q_obj)

    def business_area_filter(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[User]":
        return qs.filter(Q(user_roles__business_area__slug=value) | Q(partner__business_areas__slug=value))

    def program_filter(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[User]":
        program_id = decode_id_string(value)
        return qs.filter(partner__programs__id=program_id)

    def partners_filter(self, qs: "QuerySet", name: str, values: list["UUID"]) -> "QuerySet[User]":
        q_obj = Q()
        for value in values:
            q_obj |= Q(partner__id=value)
        return qs.filter(q_obj)

    def roles_filter(self, qs: "QuerySet", name: str, values: list) -> "QuerySet[User]":
        business_area_slug = self.data.get("business_area")
        q_obj = Q()
        for value in values:
            q_obj |= Q(
                user_roles__role__id=value,
                user_roles__business_area__slug=business_area_slug,
            ) | Q(
                partner__business_area_partner_through__roles__id=value,
                partner__business_areas__slug=business_area_slug,
            )
        return qs.filter(q_obj)
