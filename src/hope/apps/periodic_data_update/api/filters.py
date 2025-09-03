from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters

from hope.apps.account.models import User
from hope.apps.core.api.filters import UpdatedAtFilter
from hope.apps.periodic_data_update.models import PDUOnlineEdit


class PDUOnlineEditFilter(UpdatedAtFilter):
    status = filters.MultipleChoiceFilter(choices=PDUOnlineEdit.Status.choices)

    class Meta:
        model = PDUOnlineEdit
        fields = ("status",)


class UserAvailableFilter(filters.FilterSet):
    search = filters.CharFilter(
        method="search_filter", help_text="Search users by first name, last name or email."
    )

    def search_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet[User]:
        values = value.split()
        q_obj = Q()
        for v in values:
            q_obj |= Q(first_name__icontains=v)
            q_obj |= Q(last_name__icontains=v)
            q_obj |= Q(email__icontains=v)
        return qs.filter(q_obj)
