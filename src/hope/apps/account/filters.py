from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.functions import Lower
from django_filters import BooleanFilter, CharFilter, FilterSet, MultipleChoiceFilter

from hope.models.user import USER_STATUS_CHOICES
from hope.models.role import Role
from hope.models.partner import Partner
from hope.apps.core.utils import CustomOrderingFilter
from hope.models.program import Program


class UsersFilter(FilterSet):
    program = CharFilter(required=False, method="program_filter")
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=USER_STATUS_CHOICES)
    partner = MultipleChoiceFilter(choices=lambda: Partner.get_partners_as_choices(), method="partners_filter")
    roles = MultipleChoiceFilter(choices=lambda: Role.get_roles_as_choices(), method="roles_filter")
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
        for v in values:
            q_obj |= Q(first_name__startswith=v)
            q_obj |= Q(last_name__startswith=v)
            q_obj |= Q(email__startswith=v)
        return qs.filter(q_obj)

    def business_area_filter(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[User]":
        return qs.filter(
            Q(role_assignments__business_area__slug=value) | Q(partner__role_assignments__business_area__slug=value)
        )

    def program_filter(self, qs: "QuerySet", name: str, value: str) -> "QuerySet[User]":
        business_area = Program.objects.get(slug=value).business_area
        return qs.filter(
            Q(partner__role_assignments__program__slug=value)
            | Q(
                partner__role_assignments__program=None,
                partner__role_assignments__business_area=business_area,
            )
            | Q(role_assignments__program__slug=value)
            | Q(
                role_assignments__program=None,
                role_assignments__business_area=business_area,
            )
        )

    def partners_filter(self, qs: "QuerySet", name: str, values: list["UUID"]) -> "QuerySet[User]":
        q_obj = Q()
        for value in values:
            q_obj |= Q(partner__id=value)
        return qs.filter(q_obj)

    def roles_filter(self, qs: "QuerySet", name: str, values: list) -> "QuerySet[User]":
        business_area_slug = self.request.parser_context["kwargs"]["business_area_slug"]
        q_obj = Q()
        for value in values:
            q_obj |= Q(
                role_assignments__role__id=value,
                role_assignments__business_area__slug=business_area_slug,
            ) | Q(
                partner__role_assignments__role__id=value,
                partner__role_assignments__business_area__slug=business_area_slug,
            )
        return qs.filter(q_obj)
