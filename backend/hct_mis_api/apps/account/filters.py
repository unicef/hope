from django.contrib.auth import get_user_model
from django_filters import CharFilter, FilterSet, MultipleChoiceFilter

from django.db.models import Q
from django.db.models.functions import Lower

from hct_mis_api.apps.account.models import USER_STATUS_CHOICES, Partner, Role
from hct_mis_api.apps.core.utils import CustomOrderingFilter


class UsersFilter(FilterSet):
    business_area = CharFilter(required=True, method="business_area_filter")
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=USER_STATUS_CHOICES)
    partner = MultipleChoiceFilter(choices=Partner.get_partners_as_choices(), method="partners_filter")
    roles = MultipleChoiceFilter(choices=Role.get_roles_as_choices(), method="roles_filter")

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

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(first_name__startswith=value)
            q_obj |= Q(last_name__startswith=value)
            q_obj |= Q(email__startswith=value)
        return qs.filter(q_obj)

    def business_area_filter(self, qs, name, value):
        return qs.filter(user_roles__business_area__slug=value)

    def partners_filter(self, qs, name, values):
        q_obj = Q()
        for value in values:
            q_obj |= Q(partner__id=value)
        return qs.filter(q_obj)

    def roles_filter(self, qs, name, values):
        business_area_slug = self.data.get("business_area")
        q_obj = Q()
        for value in values:
            q_obj |= Q(
                user_roles__role__id=value,
                user_roles__business_area__slug=business_area_slug,
            )
        return qs.filter(q_obj)
